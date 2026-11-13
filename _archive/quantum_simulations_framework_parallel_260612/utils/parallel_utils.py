"""
Parallel Execution and Hardware-Aware Scaling Utilities.

This module provides high-level abstractions for parallelizing quantum dynamics
simulations across CPU and GPU backends. It is specifically optimized for
high-performance workstations (e.g., dual Xeon Gold 6136 with 48 cores) and
implements intelligent memory-safe job scheduling to prevent OOM errors
during large-scale adHOPS ensemble runs.
"""

import os
import logging
from multiprocessing import Pool, cpu_count
from functools import partial
from typing import Any, Callable, Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Configure BLAS threading to avoid oversubscription
os.environ["OPENBLAS_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["NUMEXPR_NUM_THREADS"] = "2"
os.environ["OMP_NUM_THREADS"] = "2"


def estimate_memory_per_traj(
    L_max: int = 8,
    K_max: int = 2,
    n_hierarchy_modes: int = 189,
    time_max_fs: float = 1000.0,
) -> float:
    """
    Estimate peak RAM per trajectory based on hierarchy and time parameters.

    Reference: 21 modes (3 DL × 7 sites, no vibronic) at L=8, K=2, 1000 fs → 6.0 GB.
    Full FMO: 189 modes (3 DL + 24 vibronic × 7 sites) at L=8, K=2, 1000 fs → ~54 GB/traj.

    For small L (≤4), uses the exact hierarchy size C(modes+L, L) ratio for accuracy;
    the (L/8)² × (modes/21) approximation overestimates by ~8× at L=3, 147 modes.
    """
    try:
        from core.constants import BASE_TRAJ_MEMORY_GB, MIN_TRAJ_MEMORY_GB
    except ImportError:
        BASE_TRAJ_MEMORY_GB = 6.0
        MIN_TRAJ_MEMORY_GB = 0.5

    n = float(n_hierarchy_modes)
    L = float(L_max)

    if L <= 4 and n > 21:
        # Exact hierarchy ratio for small L: C(n+L, L) / C(29, 8)
        # L_ref=8, n_ref=21 → C(29, 8) = 4,292,145
        import math

        def comb(x, k):
            return math.comb(int(x), int(k))

        hier_ref = comb(29, 8)
        hier_actual = comb(n + L, L)
        ratio = hier_actual / hier_ref
        est = BASE_TRAJ_MEMORY_GB * ratio
    else:
        L_ref, K_ref, n_modes_ref = 8.0, 2.0, 21.0
        l_factor = (L / L_ref) ** 2
        k_factor = max(0.5, K_max / K_ref)
        modes_factor = max(1.0, n / n_modes_ref)
        est = BASE_TRAJ_MEMORY_GB * l_factor * k_factor * modes_factor

    # Scale with simulation time (shorter trajectories use less memory)
    time_factor = time_max_fs / 1000.0
    est *= time_factor

    return max(MIN_TRAJ_MEMORY_GB, est)


def get_safe_n_jobs(
    memory_per_traj_gb: Optional[float] = None,
    L_max: int = 8,
    K_max: int = 2,
    n_hierarchy_modes: int = 189,
    time_max_fs: float = 1000.0,
) -> int:
    """
    Calculate the optimal number of parallel workers based on hardware limits.

    Prevents Out-of-Memory (OOM) errors by calculating 'RAM slots' from
    the estimated trajectory footprint and available system RAM.

    Parameters
    ----------
    memory_per_traj_gb : float, optional
        Explicit peak RAM per trajectory. If None, estimated from L/K/modes/time.
    L_max, K_max, n_hierarchy_modes : int
        Hierarchy parameters for estimation (ignored if memory_per_traj_gb given).
    time_max_fs : float
        Max simulation time in fs (shorter = less memory).

    Returns
    -------
    int
        The number of parallel workers (n_jobs) that can safely execute concurrently.
    """
    import multiprocessing

    cpu_fraction = 0.66
    mem_fraction = 0.66

    try:
        from core.constants import CPU_COUNT_FRACTION, MEMORY_FRACTION_LIMIT

        cpu_fraction = CPU_COUNT_FRACTION
        mem_fraction = MEMORY_FRACTION_LIMIT
    except ImportError:
        pass

    if memory_per_traj_gb is None:
        memory_per_traj_gb = estimate_memory_per_traj(
            L_max, K_max, n_hierarchy_modes, time_max_fs
        )

    n_cpus = multiprocessing.cpu_count()
    cpu_limit = max(1, int(n_cpus * cpu_fraction))

    try:
        import psutil

        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024**3)
    except ImportError:
        try:
            total_gb = (os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")) / (
                1024**3
            )
            available_gb = total_gb * 0.7
        except Exception:
            available_gb = 8.0

    ram_slots_raw = (
        int((available_gb * mem_fraction) / memory_per_traj_gb)
        if memory_per_traj_gb > 0
        else 0
    )
    ram_slots = max(ram_slots_raw, 1) if ram_slots_raw >= 1 else 0
    n_jobs = min(cpu_limit, ram_slots)

    logger.info(
        f"Hardware-Aware Scaling: Available RAM={available_gb:.1f}GB, "
        f"CPU Slots={cpu_limit}, RAM Slots={ram_slots} "
        f"(est. {memory_per_traj_gb:.1f}GB/traj). n_jobs={n_jobs}"
    )

    if n_jobs < 1:
        raise RuntimeError(
            f"Insufficient RAM: {memory_per_traj_gb:.1f} GB/traj × {cpu_limit} CPU slots "
            f"exceeds {available_gb:.1f} GB available (after {mem_fraction:.0%} budget). "
            f"Reduce L_max/K_max/modes or increase hardware."
        )

    return n_jobs


class ParallelExecutor:
    """Manages parallel execution across CPU cores and GPU."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize parallel executor.

        Parameters
        ----------
        config : dict
            Parallel configuration from parallel_config.yaml
        """
        self.config = config
        self.n_workers = config.get("parallel", {}).get("n_workers", cpu_count() - 8)
        self.use_gpu = config.get("parallel", {}).get("use_gpu", False)
        self.gpu_backend = config.get("parallel", {}).get("gpu_backend", "jax")

        # Initialize GPU backend if requested
        if self.use_gpu:
            self._init_gpu_backend()

        logger.info(
            f"ParallelExecutor initialized: {self.n_workers} CPU workers, GPU={'enabled' if self.use_gpu else 'disabled'}"
        )

    def _init_gpu_backend(self):
        """Initialize GPU backend (JAX, CuPy, or PyTorch)."""
        if self.gpu_backend == "jax":
            try:
                import jax
                import jax.numpy as jnp
                from jax import jit, vmap

                # Configure JAX for GPU
                jax.config.update("jax_platform_name", "gpu")
                jax.config.update("jax_enable_x64", False)  # Use float32 for speed

                self.jnp = jnp
                self.jit = jit
                self.vmap = vmap

                # Test GPU availability
                devices = jax.devices("gpu")
                logger.info(
                    f"JAX GPU backend initialized: {len(devices)} GPU(s) available"
                )
                logger.info(f"  Device: {devices[0]}")

            except Exception as e:
                logger.warning(f"Failed to initialize JAX GPU backend: {e}")
                self.use_gpu = False
        else:
            logger.warning(
                f"GPU backend '{self.gpu_backend}' not implemented, falling back to CPU"
            )
            self.use_gpu = False

    def map_parallel(
        self, func: Callable, items: List[Any], desc: str = "Processing"
    ) -> List[Any]:
        """
        Execute function in parallel across CPU workers.

        Parameters
        ----------
        func : callable
            Function to execute (must be picklable)
        items : list
            List of items to process
        desc : str
            Description for logging

        Returns
        -------
        results : list
            Results from parallel execution
        """
        n_items = len(items)
        logger.info(f"{desc}: {n_items} items across {self.n_workers} workers")

        if n_items == 1 or self.n_workers == 1:
            # Single-threaded execution
            return [func(item) for item in items]

        # Parallel execution
        with Pool(processes=self.n_workers) as pool:
            results = pool.map(func, items)

        return results

    def map_parallel_with_context(
        self,
        func: Callable,
        items: List[Any],
        context: Dict[str, Any],
        desc: str = "Processing",
    ) -> List[Any]:
        """
        Execute function in parallel with shared context.

        Parameters
        ----------
        func : callable
            Function to execute (signature: func(item, context))
        items : list
            List of items to process
        context : dict
            Shared context (e.g., Hamiltonian, bath parameters)
        desc : str
            Description for logging

        Returns
        -------
        results : list
            Results from parallel execution
        """
        # Create partial function with context
        func_with_context = partial(func, context=context)
        return self.map_parallel(func_with_context, items, desc)

    def batch_process(
        self,
        func: Callable,
        items: List[Any],
        batch_size: int,
        desc: str = "Batch processing",
    ) -> List[Any]:
        """
        Process items in batches (useful for GPU memory management).

        Parameters
        ----------
        func : callable
            Function to execute on each batch
        items : list
            List of items to process
        batch_size : int
            Number of items per batch
        desc : str
            Description for logging

        Returns
        -------
        results : list
            Concatenated results from all batches
        """
        n_items = len(items)
        n_batches = (n_items + batch_size - 1) // batch_size

        logger.info(f"{desc}: {n_items} items in {n_batches} batches of {batch_size}")

        results = []
        for i in range(0, n_items, batch_size):
            batch = items[i : i + batch_size]
            batch_results = func(batch)
            results.extend(batch_results)

        return results


def parallel_trajectory_simulation(
    trajectory_params: List[Dict[str, Any]],
    simulator_func: Callable,
    n_workers: int = 1,
) -> List[Dict[str, Any]]:
    """
    Simulate multiple trajectories in parallel.

    Parameters
    ----------
    trajectory_params : list of dict
        List of parameter dictionaries for each trajectory
    simulator_func : callable
        Simulation function (signature: func(params) -> results)
    n_workers : int
        Number of parallel workers

    Returns
    -------
    results : list of dict
        Simulation results for each trajectory
    """
    logger.info(
        f"Parallel trajectory simulation: {len(trajectory_params)} trajectories, {n_workers} workers"
    )

    with Pool(processes=n_workers) as pool:
        results = pool.map(simulator_func, trajectory_params)

    return results


def gpu_batch_matmul(
    matrices_a: np.ndarray, matrices_b: np.ndarray, use_jax: bool = True
) -> np.ndarray:
    """
    Batch matrix multiplication on GPU using JAX.

    Parameters
    ----------
    matrices_a : np.ndarray
        Array of shape (batch_size, n, m)
    matrices_b : np.ndarray
        Array of shape (batch_size, m, k)
    use_jax : bool
        Use JAX for GPU acceleration

    Returns
    -------
    result : np.ndarray
        Array of shape (batch_size, n, k)
    """
    if not use_jax:
        # Fallback to NumPy
        return np.einsum("bij,bjk->bik", matrices_a, matrices_b)

    try:
        import jax.numpy as jnp
        from jax import jit, vmap

        # Define batched matrix multiplication
        @jit
        def batched_matmul(a, b):
            return vmap(jnp.matmul)(a, b)

        # Transfer to GPU, compute, transfer back
        a_gpu = jnp.array(matrices_a)
        b_gpu = jnp.array(matrices_b)
        result_gpu = batched_matmul(a_gpu, b_gpu)

        return np.array(result_gpu)

    except Exception as e:
        logger.warning(f"GPU batch matmul failed: {e}, falling back to NumPy")
        return np.einsum("bij,bjk->bik", matrices_a, matrices_b)


def gpu_expm_batch(matrices: np.ndarray, use_jax: bool = True) -> np.ndarray:
    """
    Batch matrix exponential on GPU using JAX.

    Parameters
    ----------
    matrices : np.ndarray
        Array of shape (batch_size, n, n)
    use_jax : bool
        Use JAX for GPU acceleration

    Returns
    -------
    result : np.ndarray
        Array of shape (batch_size, n, n)
    """
    if not use_jax:
        from scipy.linalg import expm

        return np.array([expm(m) for m in matrices])

    try:
        import jax.numpy as jnp
        from jax import jit, vmap
        from jax.scipy.linalg import expm as jax_expm

        @jit
        def batched_expm(mats):
            return vmap(jax_expm)(mats)

        mats_gpu = jnp.array(matrices)
        result_gpu = batched_expm(mats_gpu)

        return np.array(result_gpu)

    except Exception as e:
        logger.warning(f"GPU batch expm failed: {e}, falling back to SciPy")
        from scipy.linalg import expm

        return np.array([expm(m) for m in matrices])
