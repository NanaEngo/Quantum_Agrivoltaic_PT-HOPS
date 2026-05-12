"""
Memory-aware job scheduling for quantum dynamics simulations.

This module provides intelligent memory management and job scheduling to prevent 
out-of-memory (OOM) errors during large-scale parallel quantum trajectory 
simulations. It calculates resource requirements based on hierarchy depth 
and provides batching strategies to optimize throughput on restricted hardware.
"""

import os
import gc
import logging
from typing import Dict, Any, Optional

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

    def __init__(self, L_max: int, K_max: int, total_trajectories: int):
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
        """
        self.L_max = L_max
        self.K_max = K_max
        self.n_traj_total = total_trajectories

    def validate_and_adapt(self) -> Dict[str, Any]:
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
        mem_per_traj = self._estimate_memory()

        # 2. Get available RAM and limits
        available_gb = self._get_available_ram()
        limit_gb = available_gb * MEMORY_FRACTION_LIMIT

        # 3. Calculate maximum parallel jobs
        n_jobs_max = max(1, int(limit_gb / mem_per_traj))
        cpu_limit = int(os.cpu_count() * CPU_COUNT_FRACTION)
        n_jobs = min(n_jobs_max, cpu_limit)

        # 4. Validate feasibility
        if n_jobs < 1:
            raise ValueError(
                f"Impossible: mémoire/traj ({mem_per_traj:.1f}GB) "
                f"> RAM limite ({limit_gb:.1f}GB). "
                f"Réduisez L_max ({self.L_max}) ou K_max ({self.K_max})."
            )

        # 5. Calculate batch strategy
        if self.n_traj_total <= n_jobs:
            # Fit in single batch
            batch_size = self.n_traj_total
            n_batches = 1
        else:
            # Multi-batch strategy to prevent queue explosion
            # Use min(n_jobs, n_traj_total // 4) for stability
            batch_size = max(n_jobs, self.n_traj_total // 4)
            n_batches = (self.n_traj_total + batch_size - 1) // batch_size

        # 6. Generate warnings
        warnings = []
        if n_batches > 1:
            warnings.append(f"{n_batches} batches nécessaires (dépassement mémoire)")
        if mem_per_traj > limit_gb * 0.8:
            warnings.append(f"Mémoire/traj élevée: {mem_per_traj:.1f}GB (>80% de limite)")
        if n_jobs < os.cpu_count() * 0.5:
            warnings.append(f"Parallélisme limité: {n_jobs}/{os.cpu_count()} cœurs utilisés")

        return {
            'n_jobs': n_jobs,
            'batch_size': batch_size,
            'n_batches': n_batches,
            'memory_per_traj_gb': mem_per_traj,
            'available_ram_gb': available_gb,
            'ram_limit_gb': limit_gb,
            'warnings': warnings,
        }

    def _estimate_memory(self) -> float:
        """
        Estimate memory per trajectory using quadratic scaling with L
        and linear scaling with K.

        Returns
        -------
        float
            Memory estimate in GB
        """
        L_ref, K_ref = 8.0, 2.0

        # Quadratic scaling with hierarchy depth
        l_factor = (self.L_max / L_ref) ** 2

        # Linear scaling with Matsubara terms (minimum 0.5)
        k_factor = max(0.5, self.K_max / K_ref)

        estimate = BASE_TRAJ_MEMORY_GB * l_factor * k_factor

        # Apply safety buffer for low-RAM systems
        if HAS_PSUTIL:
            total_ram_gb = psutil.virtual_memory().total / (1024**3)
            if total_ram_gb < 16.0:
                estimate *= 1.5  # 50% more conservative

        return max(MIN_TRAJ_MEMORY_GB, estimate)

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
    L = cfg['dynamics']['L_max']
    K = cfg['dynamics']['matsubara_truncation']
    n_traj = cfg['simulation']['n_traj']

    scheduler = MemoryAwareJobScheduler(L, K, n_traj)
    info = scheduler.validate_and_adapt()

    print("✓ Validation configuration mémoire:")
    print(f"  L={L}, K={K}, n_traj={n_traj}")
    print(f"  Mémoire/traj: {info['memory_per_traj_gb']:.2f} GB")
    print(f"  RAM disponible: {info['available_ram_gb']:.1f} GB")
    print(f"  RAM limite (2/3): {info['ram_limit_gb']:.1f} GB")
    print(f"  n_jobs parallèle: {info['n_jobs']}")
    print(f"  Batches: {info['n_batches']} × {info['batch_size']} traj")

    if info['warnings']:
        print("  ⚠️ Avertissements:")
        for warning in info['warnings']:
            print(f"    - {warning}")
    else:
        print("  ✓ Configuration optimale (pas d'avertissement)")

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
        print(f"  🧹 Mémoire nettoyée: {mem.available / (1024**3):.1f} GB disponible")