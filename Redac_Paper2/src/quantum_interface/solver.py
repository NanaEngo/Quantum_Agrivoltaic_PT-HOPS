import os
import sys

import h5py
import numpy as np

from ..config_loader import ConfigModel
from ..constants import (
    FMO_NSITES,
    K_MATSUBARA,
    POSITIVITY_TOLERANCE,
    SOLVER_DETERMINISTIC_SEED,
    TRACE_LOWER_BOUND,
    TRACE_UPPER_BOUND,
)
from ..logging_config import get_logger

logger = get_logger("solver")

_QS_FRAMEWORK = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "quantum_simulations_framework")
)

HOPS_SIM_AVAILABLE = False
HopsSimulator = None  # type: ignore

if _QS_FRAMEWORK not in sys.path:
    sys.path.insert(0, _QS_FRAMEWORK)
try:
    from src.core.hops_simulator import HopsSimulator

    HOPS_SIM_AVAILABLE = True
except Exception:
    _QS_SRC = os.path.join(_QS_FRAMEWORK, "src")
    if _QS_SRC not in sys.path:
        sys.path.insert(0, _QS_SRC)
    try:
        from core.hops_simulator import HopsSimulator

        HOPS_SIM_AVAILABLE = True
    except Exception:
        pass


class MesoHopsSolver:
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
        if not HOPS_SIM_AVAILABLE or HopsSimulator is None:
            raise ImportError(
                "HopsSimulator not available. Ensure quantum_simulations_framework/ "
                "is present at the project root."
            )

        max_hier = (
            hierarchy_depth
            if hierarchy_depth is not None
            else self.config.quantum.solver.hierarchy_depth
        )
        dt_propagate = self.config.quantum.solver.time_step_fs

        sim = HopsSimulator(
            hamiltonian=H_dressed,
            temperature=self.config.simulation.temperature_k,
            max_hierarchy=max_hier,
            k_matsubara=K_MATSUBARA,
            n_traj=n_traj,
            use_sbd=True,
            sbd_bundles_per_site=self.config.quantum.solver.sbd_bundles_per_site,
            strict_hermiticity=False,
            vibronic_in_hierarchy=False,
        )

        result = sim.simulate_dynamics(
            time_points=time_points,
            initial_state=psi0,
            dt=dt_propagate,
            n_traj=n_traj,
            max_hierarchy=max_hier,
            seed=SOLVER_DETERMINISTIC_SEED,
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
        output = np.zeros((n_times, FMO_NSITES, FMO_NSITES), dtype=complex)
        for t_idx, t_val in enumerate(time_points):
            traj_idx = int(round(t_val / dt_propagate))
            idx = min(max(traj_idx, 0), dm_array.shape[0] - 1)
            output[t_idx] = dm_array[idx, :FMO_NSITES, :FMO_NSITES]

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
        Audits a sequence of density matrices of shape [time_steps, FMO_NSITES, FMO_NSITES].
        Checks trace preservation and positivity.
        """
        is_valid = True
        for step, rho in enumerate(density_matrices):
            diag = np.diagonal(rho).real
            if np.any(diag < POSITIVITY_TOLERANCE):
                logger.warning(f"Positivity violation at step {step}: negative population {diag}")
                is_valid = False
            trace_val = float(np.trace(rho).real)
            if trace_val > TRACE_UPPER_BOUND or trace_val < TRACE_LOWER_BOUND:
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
        time_step_fs: float = 0.2,
    ) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with h5py.File(file_path, "w") as f:
            dyn_group = f.create_group("dynamics")
            meta_group = f.create_group("metadata")

            dyn_group.create_dataset("populations", data=populations)
            dyn_group.create_dataset("rc_yield", data=rc_yield)
            dyn_group.attrs["time_step_fs"] = time_step_fs

            param_str = str(self.config.model_dump())
            meta_group.create_dataset("parameters", data=param_str)
            meta_group.create_dataset("run_id", data=run_id)
            meta_group.create_dataset("git_hash", data=git_hash)
            meta_group.create_dataset("timestamp", data=timestamp)
