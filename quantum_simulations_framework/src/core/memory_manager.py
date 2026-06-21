"""
Memory-aware job scheduling for quantum dynamics simulations.
"""

__title__ = "MemoryAwareJobScheduler"
__author__ = "Nana Engo et al."
__version__ = "1.0.0"

import gc
import logging
import math
import os
from typing import Any, Dict

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from .constants import (
    BASE_TRAJ_MEMORY_GB,
    CPU_COUNT_FRACTION,
    MAX_N_JOBS,
    MEMORY_FRACTION_LIMIT,
    MIN_TRAJ_MEMORY_GB,
)

logger = logging.getLogger(__name__)


class MemoryAwareJobScheduler:
    """
    Intelligent job scheduler that validates memory feasibility and adapts
    batch size and parallelism to prevent OOM errors.

    This scheduler ensures that:
    1. Total memory usage never exceeds 2/3 of available RAM
    2. n_traj is validated against L_max and K_max constraints
    3. Batch processing prevents queue explosion in joblib
    4. Memory is properly cleaned between batches
    """

    def __init__(
        self,
        L_max: int,
        K_max: int,
        total_trajectories: int,
        time_max_fs: float = 1000.0,
    ):
        """
        Initialize the memory-aware scheduler.

        Parameters
        ----------
        L_max : int
            Maximum hierarchy depth (truncation level)
        K_max : int
            Number of Matsubara terms
        total_trajectories : int
            Total number of trajectories to simulate
        time_max_fs : float
            Maximum simulation time in fs (shorter → less memory per traj)
        """
        self.L_max = L_max
        self.K_max = K_max
        self.n_traj_total = total_trajectories
        self.time_max_fs = time_max_fs

    def validate_and_adapt(self, n_hierarchy_modes: int = 189) -> dict:
        """
        Validate simulation feasibility and return optimized scheduling parameters.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing:
            - n_jobs: int - Number of parallel workers
            - batch_size: int - Trajectories per batch
            - n_batches: int - Number of batches needed
            - memory_per_traj_gb: float - Memory per trajectory
            - available_ram_gb: float - Total available RAM
            - ram_limit_gb: float - RAM usage limit (2/3)
            - warnings: list - Any warnings about constraints

        Raises
        ------
        ValueError
            If simulation is impossible given memory constraints
        """
        # 1. Estimate memory per trajectory
        mem_per_traj = self._estimate_memory(n_hierarchy_modes)

        # 2. Get available RAM and limits
        available_gb = self._get_available_ram()
        limit_gb = available_gb * MEMORY_FRACTION_LIMIT

        # 3. Calculate maximum parallel jobs
        n_jobs_raw = int(limit_gb / mem_per_traj) if mem_per_traj > 0 else 0
        cpu_limit = int(os.cpu_count() * CPU_COUNT_FRACTION)
        n_jobs = min(n_jobs_raw, cpu_limit, MAX_N_JOBS) if n_jobs_raw >= 1 else 0

        # 4. Validate feasibility
        if n_jobs < 1:
            raise ValueError(
                f"Impossible: mémoire/traj ({mem_per_traj:.1f}GB) "
                f"> RAM limite ({limit_gb:.1f}GB). "
                f"Réduisez L_max ({self.L_max}) ou K_max ({self.K_max})."
            )

        # 5. Calculate batch strategy — batch_size must never exceed n_jobs
        # to prevent more concurrent objects than workers (memory explosion)
        batch_size = n_jobs
        n_batches = (self.n_traj_total + batch_size - 1) // batch_size

        # 6. Generate warnings
        warnings = []
        if n_batches > 1:
            warnings.append(f"{n_batches} batches nécessaires (dépassement mémoire)")
        if mem_per_traj > limit_gb * 0.8:
            warnings.append(f"Mémoire/traj élevée: {mem_per_traj:.1f}GB (>80% de limite)")
        if n_jobs < os.cpu_count() * CPU_COUNT_FRACTION:
            warnings.append(f"Parallélisme limité: {n_jobs}/{os.cpu_count()} cœurs utilisés")

        return {
            "n_jobs": n_jobs,
            "batch_size": batch_size,
            "n_batches": n_batches,
            "memory_per_traj_gb": mem_per_traj,
            "available_ram_gb": available_gb,
            "ram_limit_gb": limit_gb,
            "warnings": warnings,
        }

    def _estimate_memory(self, n_hierarchy_modes: int = 189) -> float:
        """
        Estimate memory per trajectory using exact combinatorial scaling.

        Reference: 21 effective modes (SBD=3 × 7 sites) at L=8, K=2, 1000 fs → 6.0 GB.
        Hierarchy size = C(n_modes + L, L). Ratio vs reference C(29, 8) gives memory.

        NOTE: SBD compression reduces effective modes to sbd_bundles_per_site × n_sites.
        For sbd_bundles=3, the max effective is 21. We cap at 21 to reflect this.
        """
        n = min(float(n_hierarchy_modes), 21.0)
        L = self.L_max

        hier_ref = math.comb(29, 8)  # C(21+8, 8) = 4,292,145 → 6.0 GB
        hier_actual = math.comb(int(n + L), L)
        ratio = hier_actual / hier_ref
        estimate = BASE_TRAJ_MEMORY_GB * ratio

        k_factor = max(0.5, self.K_max / 2.0)
        estimate *= k_factor

        time_factor = self.time_max_fs / 1000.0
        estimate *= time_factor

        if HAS_PSUTIL:
            total_ram_gb = psutil.virtual_memory().total / (1024**3)
            if total_ram_gb < 16.0:
                estimate *= 1.5

        return max(MIN_TRAJ_MEMORY_GB, estimate)

    def print_report(self, n_hierarchy_modes: int = 189) -> None:
        """Log a human-readable summary of the scheduling plan."""
        try:
            info = self.validate_and_adapt(n_hierarchy_modes)
        except ValueError as e:
            logger.error(f"Memory plan infeasible: {e}")
            return
        logger.info(
            f"Memory Plan: {info['n_batches']} batch(es) × {info['batch_size']} traj | "
            f"n_jobs={info['n_jobs']} | "
            f"{info['memory_per_traj_gb']:.1f} GB/traj | "
            f"RAM avail={info['available_ram_gb']:.1f} GB limit={info['ram_limit_gb']:.1f} GB"
        )
        for w in info.get("warnings", []):
            logger.warning(f"Memory Warning: {w}")

    def _get_available_ram(self) -> float:
        """
        Get available RAM in GB.

        Returns
        -------
        float
            Available RAM in GB
        """
        if HAS_PSUTIL:
            return psutil.virtual_memory().available / (1024**3)
        else:
            import os as _os

            pages = _os.sysconf("SC_PHYS_PAGES")
            page_size = _os.sysconf("SC_PAGE_SIZE")
            if pages > 0 and page_size > 0:
                return pages * page_size / (1024**3) * 0.5
            return 8.0


def validate_memory_configuration(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate the memory configuration and return optimized execution parameters.

    This function cross-references the simulation physics parameters (L, K)
    with the available system RAM and CPU cores to determine the safest and
    most efficient parallelization strategy.

    Parameters
    ----------
    cfg : Dict[str, Any]
        Configuration dictionary containing 'dynamics' and 'simulation'
        parameter blocks.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing optimized execution parameters:
        - n_jobs: Number of parallel processes to spawn.
        - batch_size: Number of trajectories to process per batch.
        - n_batches: Total number of sequential batches required.
        - memory_per_traj_gb: Estimated memory footprint per trajectory.

    Raises
    ------
    ValueError
        If the memory requirements for a single trajectory exceed the
        available system limits.
    """
    L = cfg["dynamics"]["L_max"]
    K = cfg["dynamics"]["matsubara_truncation"]
    n_traj = cfg["simulation"]["n_traj"]

    time_max = cfg.get("dynamics", {}).get("time_max", 1000.0)
    scheduler = MemoryAwareJobScheduler(L, K, n_traj, time_max_fs=time_max)
    info = scheduler.validate_and_adapt()

    logger.info("✓ Validation configuration mémoire:")
    logger.info(f"  L={L}, K={K}, n_traj={n_traj}")
    logger.info(f"  Mémoire/traj: {info['memory_per_traj_gb']:.2f} GB")
    logger.info(f"  RAM disponible: {info['available_ram_gb']:.1f} GB")
    logger.info(f"  RAM limite (2/3): {info['ram_limit_gb']:.1f} GB")
    logger.info(f"  n_jobs parallèle: {info['n_jobs']}")
    logger.info(f"  Batches: {info['n_batches']} × {info['batch_size']} traj")

    if info["warnings"]:
        logger.warning("  [!] Avertissements:")
        for warning in info["warnings"]:
            logger.warning(f"    - {warning}")
    else:
        logger.info("  [OK] Configuration optimale")

    return info


def log_memory_pressure(threshold_percent: float = 80.0) -> bool:
    """
    Log current memory pressure and return True if usage exceeds threshold.

    Parameters
    ----------
    threshold_percent : float
        Memory usage percentage that triggers a warning (default 80%%).

    Returns
    -------
    bool
        True if memory usage exceeds the threshold, False otherwise.
    """
    if not HAS_PSUTIL:
        return False
    mem = psutil.virtual_memory()
    used_pct = mem.percent
    logger.info(
        f"Memory pressure: {used_pct:.0f}%% used "
        f"({mem.used / (1024**3):.1f}/{mem.total / (1024**3):.1f} GB)"
    )
    if used_pct > threshold_percent:
        logger.warning(
            f"High memory pressure: {used_pct:.0f}%% > {threshold_percent:.0f}%% "
            f"threshold — consider reducing n_jobs or batch_size"
        )
        return True
    return False


def cleanup_memory() -> None:
    """
    Manually trigger garbage collection and log available system memory.

    Should be called between batches in large simulations to prevent
    fragmentation and accumulated memory usage from stalled processes.
    """
    gc.collect()
    if HAS_PSUTIL:
        mem = psutil.virtual_memory()
        logger.info(f"  Memoire nettoyee: {mem.available / (1024**3):.1f} GB disponible")


def cleanup_joblib() -> None:
    """
    Kill orphaned Loky worker processes to prevent memory leaks between sweeps.

    Long-running parameter sweeps can leave zombie LokyProcess workers alive,
    consuming RAM and swap. This function finds and terminates them via psutil.
    """
    if not HAS_PSUTIL:
        logger.warning("psutil not available; cannot clean orphan workers")
        return
    import signal

    killed = 0
    current_pid = os.getpid()
    for proc in psutil.process_iter(["pid", "name", "ppid"]):
        try:
            name = proc.info.get("name", "") or ""
            ppid = proc.info.get("ppid", 0)
            if "loky" in name.lower() or "LokyProcess" in name:
                if proc.pid != current_pid and ppid != current_pid:
                    os.kill(proc.pid, signal.SIGKILL)
                    killed += 1
                    logger.info(f"Killed orphan Loky worker PID {proc.pid}")
        except (psutil.NoSuchProcess, ProcessLookupError, OSError):
            pass
    if killed > 0:
        logger.info(f"cleanup_joblib: {killed} orphan worker(s) terminated")
    gc.collect()
