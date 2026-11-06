"""
Hardware-Aware Memory Scaling Utilities.

Provides memory estimation and safe job count calculation for quantum dynamics
simulations. Delegates to MemoryAwareJobScheduler for all heavy lifting.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Configure BLAS threading to avoid oversubscription
os.environ["OPENBLAS_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["NUMEXPR_NUM_THREADS"] = "2"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["MKL_DYNAMIC"] = "FALSE"


def estimate_memory_per_traj(
    L_max: int = 8,
    K_max: int = 2,
    n_hierarchy_modes: int = 189,
    time_max_fs: float = 1000.0,
) -> float:
    """Estimate peak RAM per trajectory. Delegates to MemoryAwareJobScheduler."""
    from src.core.memory_manager import MemoryAwareJobScheduler

    sched = MemoryAwareJobScheduler(L_max, K_max, 1, time_max_fs=time_max_fs)
    return sched._estimate_memory(n_hierarchy_modes)


def get_safe_n_jobs(
    memory_per_traj_gb: Optional[float] = None,
    L_max: int = 8,
    K_max: int = 2,
    n_hierarchy_modes: int = 189,
    time_max_fs: float = 1000.0,
) -> int:
    """Calculate safe n_jobs. Delegates to MemoryAwareJobScheduler."""
    from src.core.memory_manager import MemoryAwareJobScheduler

    if memory_per_traj_gb is None:
        sched = MemoryAwareJobScheduler(L_max, K_max, 1, time_max_fs=time_max_fs)
        info = sched.validate_and_adapt(n_hierarchy_modes)
    else:
        mem_fraction = 0.66
        import multiprocessing

        import psutil

        n_cpus = multiprocessing.cpu_count()
        cpu_limit = max(1, int(n_cpus * 0.66))
        available_gb = psutil.virtual_memory().available / (1024**3)
        ram_slots = max(1, int((available_gb * mem_fraction) / memory_per_traj_gb))
        info = {"n_jobs": min(cpu_limit, ram_slots)}

    logger.info(
        f"Hardware-Aware Scaling: n_jobs={info['n_jobs']} "
        f"(est. {info.get('memory_per_traj_gb', memory_per_traj_gb or 0):.1f}GB/traj)"
    )
    return info["n_jobs"]
