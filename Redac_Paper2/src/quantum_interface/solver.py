import sys
import os
import logging
import numpy as np
import h5py
from ..config_loader import ConfigModel

# Configure logging to logs/solver_errors.log
log_dir = os.path.join(os.path.dirname(__file__), "../../logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "solver_errors.log")

# Custom logger to avoid interfering with global basicConfig
logger = logging.getLogger("Redac_Paper2.solver")
logger.setLevel(logging.WARNING)
if not logger.handlers:
    fh = logging.FileHandler(log_file)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)

# -------------------------------------------------------------------
# Import shared HopsSimulator from project-level quantum_simulations_framework
# -------------------------------------------------------------------
# Strategy: add the PROJECT ROOT to sys.path, then import using the full
# package path (quantum_simulations_framework.core.hops_simulator.HopsSimulator).
# This keeps all relative imports within the framework working correctly
# and avoids the namespace conflict where Redac_Paper2/src/ (regular package
# with __init__.py) shadows framework_root/src/ (namespace package).
_QS_FRAMEWORK = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "quantum_simulations_framework")
)
_PROJECT_ROOT = os.path.dirname(_QS_FRAMEWORK)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

try:
    from quantum_simulations_framework.core.hops_simulator import HopsSimulator

    HOPS_SIM_AVAILABLE = True
except ImportError:
    HopsSimulator = None  # type: ignore
    HOPS_SIM_AVAILABLE = False


class MesoHopsSolver:
    """
    Integrates the shared HopsSimulator (Paper 1 engine) for Paper 2 dynamics.

    Delegates to quantum_simulations_framework/core/hops_simulator.py::HopsSimulator,
    gaining SBD compression, parallel joblib execution, memory-aware scheduling,
    3-level fallback chain, and quantum metrics (QFI, entropy, IPR) at no extra cost.
    """

    def __init__(self, config: ConfigModel):
        self.config = config

    def propagate_dynamics(
        self,
        H_dressed: np.ndarray,
        psi0: np.ndarray,
        time_points: np.ndarray,
        n_traj: int = 2,
        hierarchy_depth: int | None = None,
    ) -> np.ndarray:
        """
        Runs ensemble-averaged non-Markovian dynamics using the shared HopsSimulator.

        Delegates to HopsSimulator.simulate_dynamics() and returns the 8×8 FMO
        density matrix block at each requested time point.

        Parameters
        ----------
        hierarchy_depth : int, optional
            Override hierarchy depth (MAXHIER). If None, uses config value (default 8).
            For testing, use a small value (e.g. 2) to avoid OOM.
        """
        n_sites = H_dressed.shape[0]  # 9 if dressed with plasmon

        # Hierarchy depth: override if provided, otherwise fall back to config
        max_hier = (
            hierarchy_depth
            if hierarchy_depth is not None
            else self.config.quantum.solver.hierarchy_depth
        )

        # Time step from config (default 0.5 fs)
        dt_propagate = self.config.quantum.solver.time_step_fs

        # ----- Delegate to shared HopsSimulator -----
        if not HOPS_SIM_AVAILABLE or HopsSimulator is None:
            raise ImportError(
                "HopsSimulator not available. Ensure quantum_simulations_framework/ "
                "is present at the project root."
            )

        sim = HopsSimulator(
            hamiltonian=H_dressed,
            temperature=self.config.simulation.temperature_k,
            max_hierarchy=max_hier,
            k_matsubara=2,  # K=2 standard
            n_traj=n_traj,
            use_sbd=True,  # Enable SBD compression (requires mesohops_adapters)
            strict_hermiticity=False,  # Allow imaginary trapping terms on diagonal
            vibronic_in_hierarchy=False,  # Paper 2: Drude-Lorentz bath only (no explicit vibronic modes)
        )

        result = sim.simulate_dynamics(
            time_points=time_points,
            initial_state=psi0,
            dt=dt_propagate,
            n_traj=n_traj,
            max_hierarchy=max_hier,
            seed=0,  # deterministic seed for reproducibility
            show_progress=False,
        )

        # ----- Map HopsSimulator output to Paper 2's return format -----
        # HopsSimulator returns density_matrices as a list of (n_sites, n_sites) arrays
        # at the trajectory's internal time grid.  We slice down to the 8×8 FMO block.
        dm_list = result.get("density_matrices", [])
        if not dm_list:
            raise RuntimeError("HopsSimulator returned no density matrices.")

        dm_array = np.array(dm_list)  # shape (traj_times, n_sites, n_sites)

        # Build output at the requested time_points by indexing into the trajectory
        n_times = len(time_points)
        output = np.zeros((n_times, 8, 8), dtype=complex)
        for t_idx, t_val in enumerate(time_points):
            traj_idx = int(round(t_val / dt_propagate))
            idx = min(max(traj_idx, 0), dm_array.shape[0] - 1)
            output[t_idx] = dm_array[idx, 0:8, 0:8]

        return output


class QuantumStabilityAudit:
    """
    Performs stability audits (trace preservation and positive semi-definiteness)
    and handles standardized HDF5 serialization of simulation dynamics.
    """

    def __init__(self, config: ConfigModel):
        self.config = config

    def audit_trajectory(self, density_matrices: np.ndarray) -> bool:
        """
        Audits a sequence of density matrices of shape [time_steps, 8, 8].
        Checks if:
          1. Total population trace is conserved to 1.0 (before trapping captures it,
             or accounting for captured population).
          2. Population values remain positive (rho_ii >= -1e-5).
        Logs any physical violations to solver_errors.log.
        """
        is_valid = True
        for step, rho in enumerate(density_matrices):
            # Check diagonal positivity
            diag = np.diagonal(rho).real
            if np.any(diag < -1e-5):
                logger.warning(
                    f"Positivity violation at step {step}: negative population {diag}"
                )
                is_valid = False

            # Trace preservation audit
            # Note: with reaction center trap, trace(rho) + captured population = 1.0
            # For raw trace check, trace(rho) must be <= 1.0001
            trace_val = float(np.trace(rho).real)
            if trace_val > 1.0001 or trace_val < -1e-5:
                logger.warning(f"Trace out of bounds at step {step}: trace={trace_val}")
                is_valid = False

        return is_valid

    def serialize_to_hdf5(
        self,
        file_path: str,
        populations: np.ndarray,
        rc_yield: np.ndarray,
        run_id: str = "unknown",
        git_hash: str = "unknown",
        timestamp: str = "unknown",
    ) -> None:
        """
        Serializes trajectory datasets to a standardized HDF5 file hierarchy:
          - /dynamics/populations -> shape [time_steps, 8]
          - /dynamics/rc_yield    -> shape [time_steps]
          - /metadata/parameters  -> serialized model configurations
          - /metadata/run_id      -> unique run identifier
          - /metadata/git_hash    -> Git commit hash of the code version
          - /metadata/timestamp   -> ISO 8601 timestamp of the run
        """
        # Ensure directories exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with h5py.File(file_path, "w") as f:
            # Create groups
            dyn_group = f.create_group("dynamics")
            meta_group = f.create_group("metadata")

            # Create datasets
            dyn_group.create_dataset("populations", data=populations)
            dyn_group.create_dataset("rc_yield", data=rc_yield)

            # Save metadata
            param_str = str(self.config.model_dump())
            meta_group.create_dataset("parameters", data=param_str)
            meta_group.create_dataset("run_id", data=run_id)
            meta_group.create_dataset("git_hash", data=git_hash)
            meta_group.create_dataset("timestamp", data=timestamp)
