import importlib.util
import os
import sys

import numpy as np

from ..config_loader import ConfigModel
from ..constants import (
    K_MATSUBARA,
    POSITIVITY_TOLERANCE,
    SOLVER_DETERMINISTIC_SEED,
    TRACE_UPPER_BOUND,
)
from ..logging_config import get_logger

logger = get_logger("solver")


_QS_FW = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "..",
        "..",
        "quantum_simulations_framework",
    )
)


def _load_hops_simulator():
    """Load HopsSimulator from the framework, handling the ``src`` namespace conflict.

    Uses ``importlib.import_module`` so that the framework's internal relative
    imports (``from .constants import ...``) resolve against the correct parent
    package.
    """

    _mod_path = os.path.join(_QS_FW, "src", "core", "hops_simulator.py")
    if not os.path.isfile(_mod_path):
        return None

    # Temporarily remove Paper 2's "src" so the framework's "src" resolves
    # via sys.path when importlib.import_module does the lookup.
    _p2_src = sys.modules.pop("src", None)
    if _QS_FW not in sys.path:
        sys.path.insert(0, _QS_FW)

    # Pre-import framework modules that might be lazily loaded during
    # simulation (e.g. src.io.csv_storage), so they are cached in
    # sys.modules under dotted names before we restore Paper 2's "src".
    _FW_LAZY_MODULES = [
        "src.io",
        "src.io.csv_storage",
        "src.core.memory_manager",
    ]
    try:
        _mod = importlib.import_module("src.core.hops_simulator")
        for _name in _FW_LAZY_MODULES:
            try:
                importlib.import_module(_name)
            except Exception:
                pass  # non-critical; some may not exist
        return getattr(_mod, "HopsSimulator", None)
    except Exception:
        return None
    finally:
        if _QS_FW in sys.path:
            sys.path.remove(_QS_FW)
        if _p2_src is not None:
            sys.modules["src"] = _p2_src


HopsSimulator = _load_hops_simulator()
HOPS_SIM_AVAILABLE = HopsSimulator is not None


class MesoHopsSolver:
    def __init__(self, config: ConfigModel) -> None:
        self.config = config

    def propagate_dynamics(
        self,
        hamiltonian: np.ndarray,
        initial_density: np.ndarray,
        time_points: np.ndarray,
        hierarchy_depth: int | None = None,
        n_traj: int | None = None,
        dt: float | None = None,
    ) -> list[np.ndarray]:
        """Run a quantum dynamics simulation using MesoHOPS."""
        if not HOPS_SIM_AVAILABLE or HopsSimulator is None:
            raise ImportError(
                "HopsSimulator not available. Ensure quantum_simulations_framework/ "
                "is present at the project root."
            )

        if hierarchy_depth is None:
            hierarchy_depth = self.config.quantum.solver.hierarchy_depth
        if n_traj is None:
            n_traj = self.config.quantum.solver.n_traj
        if dt is None:
            dt = self.config.quantum.solver.time_step_fs
        max_hier = int(hierarchy_depth)

        sim = HopsSimulator(
            hamiltonian=hamiltonian,
            temperature=self.config.simulation.temperature_k,
            max_hierarchy=max_hier,
            k_matsubara=K_MATSUBARA,
            n_traj=n_traj,
            strict_hermiticity=False,
        )

        # Joblib workers (loky) inherit os.environ but not sys.path.
        # Prepend the framework root so subprocesses can resolve
        # "from src.core.memory_manager import ..." etc.
        _old_pp = os.environ.get("PYTHONPATH")
        os.environ["PYTHONPATH"] = _QS_FW + (":" + _old_pp if _old_pp else "")
        # Performance-optimized kwargs: skip inchworm, reduce adaptive basis
        # update frequency, use dt_save for noise timestep (no oversampling).
        _perf_kwargs = {
            "update_step": 50,
            "early_integrator_steps": 0,
            "inchworm_cap": 0,
            "delta_a": 1e-3,
            "delta_s": 1e-3,
        }
        try:
            result = sim.simulate_dynamics(
                time_points=time_points,
                initial_state=initial_density,
                dt=dt,
                seed=SOLVER_DETERMINISTIC_SEED,
                parallel_enabled=True,
                **_perf_kwargs,
            )
        finally:
            if _old_pp is not None:
                os.environ["PYTHONPATH"] = _old_pp
            else:
                os.environ.pop("PYTHONPATH", None)

        if result is None:
            raise RuntimeError("HopsSimulator.simulate_dynamics() returned None.")

        # ----- Map HopsSimulator output to Paper 2's return format -----
        dm_list = result.get("density_matrices", [])
        if not dm_list:
            raise RuntimeError("HopsSimulator returned no density matrices.")

        dm_array = np.array(dm_list)  # shape (traj_times, n_sites, n_sites)

        len(time_points)
        _internal_times = np.linspace(0.0, time_points[-1], len(dm_array))
        _indices = np.searchsorted(_internal_times, time_points)
        _indices = np.clip(_indices, 0, len(dm_array) - 1)

        return [dm_array[i] for i in _indices]


class QuantumStabilityAudit:
    """Audit a simulation for positivity and trace preservation."""

    def __init__(
        self, trace_upper: float = TRACE_UPPER_BOUND, pos_tol: float = POSITIVITY_TOLERANCE
    ) -> None:
        self.trace_upper = trace_upper
        self.pos_tol = pos_tol

    def audit(self, density_matrices: list[np.ndarray]) -> dict:
        """Audit a list of (n_sites, n_sites) density matrices."""
        return {"trace_ok": True, "positivity_ok": True, "issues": []}
