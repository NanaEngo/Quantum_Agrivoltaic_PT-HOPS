"""
Memory-aware job scheduling for quantum dynamics simulations.
"""

__title__ = "MemoryAwareJobScheduler"
__author__ = "JPCL Revision Team"
__version__ = "1.0.0"

import os
import gc
import logging
import resource
from typing import Dict, Any

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from .constants import (
    BASE_TRAJ_MEMORY_GB,
    MIN_TRAJ_MEMORY_GB,
    MEMORY_FRACTION_LIMIT,
    CPU_COUNT_FRACTION,
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
        n_jobs = min(n_jobs_raw, cpu_limit) if n_jobs_raw >= 1 else 0

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
            warnings.append(
                f"Mémoire/traj élevée: {mem_per_traj:.1f}GB (>80% de limite)"
            )
        if n_jobs < os.cpu_count() * CPU_COUNT_FRACTION:
            warnings.append(
                f"Parallélisme limité: {n_jobs}/{os.cpu_count()} cœurs utilisés"
            )

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
        Estimate memory per trajectory.

        Reference: 21 modes (3 DL × 7 sites, no vibronic) at L=8, K=2, 1000 fs → 6.0 GB.
        Full FMO: 189 modes (3 DL + 24 vibronic × 7 sites) at L=8, K=2, 1000 fs → ~54 GB/traj.
        For small L (≤4), uses exact C(modes+L, L) ratio to avoid overestimation.
        """
        n = float(n_hierarchy_modes)
        L = float(self.L_max)

        if L <= 4 and n > 21:
            import math

            def comb(x, k):
                return math.comb(int(x), int(k))

            hier_ref = comb(29, 8)  # C(21+8, 8) = 4,292,145
            hier_actual = comb(n + L, L)
            ratio = hier_actual / hier_ref
            estimate = BASE_TRAJ_MEMORY_GB * ratio
        else:
            L_ref, K_ref, n_modes_ref = 8.0, 2.0, 21.0
            l_factor = (L / L_ref) ** 2
            k_factor = max(0.5, self.K_max / K_ref)
            modes_factor = max(1.0, n / n_modes_ref)
            estimate = BASE_TRAJ_MEMORY_GB * l_factor * k_factor * modes_factor

        # Scale with simulation time
        time_factor = self.time_max_fs / 1000.0
        estimate *= time_factor

        if HAS_PSUTIL:
            total_ram_gb = psutil.virtual_memory().total / (1024**3)
            if total_ram_gb < 16.0:
                estimate *= 1.5

        return max(MIN_TRAJ_MEMORY_GB, estimate)

    def print_report(self) -> None:
        """Log a human-readable summary of the scheduling plan."""
        try:
            info = self.validate_and_adapt()
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

    def set_process_mem_limit(
        self, mem_per_traj_gb: float, margin: float = 1.2
    ) -> bool:
        """
        Set a per-process virtual memory limit via resource.setrlimit.

        This kills the worker process if it exceeds the limit, preventing
        the OS OOM-killer from taking down unrelated processes.

        Parameters
        ----------
        mem_per_traj_gb : float
            Estimated memory per trajectory in GB.
        margin : float
            Safety margin (default 1.2 = 20% headroom above estimate).

        Returns
        -------
        bool
            True if limit was set successfully.
        """
        try:
            limit_bytes = int(mem_per_traj_gb * margin * (1024**3))
            resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))
            logger.info(
                f"Per-process memory limit set to {mem_per_traj_gb * margin:.1f} GB"
            )
            return True
        except (ValueError, resource.error) as e:
            logger.warning(f"Could not set RLIMIT_AS: {e}")
            return False

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
            # Conservative fallback
            return 64.0


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
        logger.warning("  ⚠️ Avertissements:")
        for warning in info["warnings"]:
            logger.warning(f"    - {warning}")
    else:
        logger.info("  ✓ Configuration optimale (pas d'avertissement)")

    return info


def cleanup_memory() -> None:
    """
    Manually trigger garbage collection and log available system memory.

    Should be called between batches in large simulations to prevent
    fragmentation and accumulated memory usage from stalled processes.
    """
    gc.collect()
    if HAS_PSUTIL:
        mem = psutil.virtual_memory()
        logger.info(
            f"  🧹 Mémoire nettoyée: {mem.available / (1024**3):.1f} GB disponible"
        )
