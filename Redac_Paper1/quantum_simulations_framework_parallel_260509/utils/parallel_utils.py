"""
Parallel execution utilities for quantum dynamics simulations.
Optimized for dual Xeon Gold 6136 (48 cores) + NVIDIA RTX A4000.
"""

import os
import logging
from multiprocessing import Pool, cpu_count, shared_memory
from functools import partial
from typing import Callable, List, Any, Optional, Dict
import numpy as np

logger = logging.getLogger(__name__)

# Configure BLAS threading to avoid oversubscription
os.environ['OPENBLAS_NUM_THREADS'] = '2'
os.environ['MKL_NUM_THREADS'] = '2'
os.environ['NUMEXPR_NUM_THREADS'] = '2'
os.environ['OMP_NUM_THREADS'] = '2'


def get_safe_n_jobs(memory_per_traj_gb: float = 2.0) -> int:
    """
    Calculate the number of parallel workers that can safely run without OOM.
    
    Parameters
    ----------
    memory_per_traj_gb : float
        Estimated memory consumption per trajectory in GB.
        
    Returns
    -------
    n_jobs : int
        Number of parallel workers.
    """
    import multiprocessing
    
    # Default fractions if constants cannot be imported
    cpu_fraction = 0.66
    mem_fraction = 0.66
    
    try:
        from core.constants import CPU_COUNT_FRACTION, MEMORY_FRACTION_LIMIT
        cpu_fraction = CPU_COUNT_FRACTION
        mem_fraction = MEMORY_FRACTION_LIMIT
    except ImportError:
        pass

    # 1. Get CPU Count and apply fraction limit
    n_cpus = multiprocessing.cpu_count()
    cpu_limit = max(1, int(n_cpus * cpu_fraction))
    
    # 2. Get RAM Availability
    try:
        import psutil
        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024**3)
    except ImportError:
        # Fallback to os.sysconf
        try:
            total_gb = (os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')) / (1024**3)
            available_gb = total_gb * 0.7  # Conservative estimate
        except:
            available_gb = 8.0 # Safe fallback
            
    # 3. Calculate RAM-based slots
    ram_slots = max(1, int((available_gb * mem_fraction) / memory_per_traj_gb))
    
    # 4. Final n_jobs is the minimum of both
    n_jobs = min(cpu_limit, ram_slots)
    
    logger.info(f"Hardware-Aware Scaling: Available RAM={available_gb:.1f}GB, "
                f"CPU Slots={cpu_limit}, RAM Slots={ram_slots} (at {memory_per_traj_gb}GB/traj). "
                f"Setting n_jobs={n_jobs}")
    
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
        self.n_workers = config.get('parallel', {}).get('n_workers', cpu_count() - 8)
        self.use_gpu = config.get('parallel', {}).get('use_gpu', False)
        self.gpu_backend = config.get('parallel', {}).get('gpu_backend', 'jax')
        
        # Initialize GPU backend if requested
        if self.use_gpu:
            self._init_gpu_backend()
        
        logger.info(f"ParallelExecutor initialized: {self.n_workers} CPU workers, GPU={'enabled' if self.use_gpu else 'disabled'}")
    
    def _init_gpu_backend(self):
        """Initialize GPU backend (JAX, CuPy, or PyTorch)."""
        if self.gpu_backend == 'jax':
            try:
                import jax
                import jax.numpy as jnp
                from jax import jit, vmap
                
                # Configure JAX for GPU
                jax.config.update('jax_platform_name', 'gpu')
                jax.config.update('jax_enable_x64', False)  # Use float32 for speed
                
                self.jnp = jnp
                self.jit = jit
                self.vmap = vmap
                
                # Test GPU availability
                devices = jax.devices('gpu')
                logger.info(f"JAX GPU backend initialized: {len(devices)} GPU(s) available")
                logger.info(f"  Device: {devices[0]}")
                
            except Exception as e:
                logger.warning(f"Failed to initialize JAX GPU backend: {e}")
                self.use_gpu = False
        else:
            logger.warning(f"GPU backend '{self.gpu_backend}' not implemented, falling back to CPU")
            self.use_gpu = False
    
    def map_parallel(self, func: Callable, items: List[Any], 
                    desc: str = "Processing") -> List[Any]:
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
    
    def map_parallel_with_context(self, func: Callable, items: List[Any],
                                  context: Dict[str, Any],
                                  desc: str = "Processing") -> List[Any]:
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
    
    def batch_process(self, func: Callable, items: List[Any],
                     batch_size: int, desc: str = "Batch processing") -> List[Any]:
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
            batch = items[i:i+batch_size]
            batch_results = func(batch)
            results.extend(batch_results)
        
        return results


def parallel_trajectory_simulation(trajectory_params: List[Dict[str, Any]],
                                   simulator_func: Callable,
                                   n_workers: int = 40) -> List[Dict[str, Any]]:
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
    logger.info(f"Parallel trajectory simulation: {len(trajectory_params)} trajectories, {n_workers} workers")
    
    with Pool(processes=n_workers) as pool:
        results = pool.map(simulator_func, trajectory_params)
    
    return results


def gpu_batch_matmul(matrices_a: np.ndarray, matrices_b: np.ndarray,
                     use_jax: bool = True) -> np.ndarray:
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
        return np.einsum('bij,bjk->bik', matrices_a, matrices_b)
    
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
        return np.einsum('bij,bjk->bik', matrices_a, matrices_b)


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
