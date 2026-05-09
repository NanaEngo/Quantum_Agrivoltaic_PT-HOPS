"""
GPU-accelerated quantum dynamics using CUDA (CuPy primary, JAX fallback).
Optimized for NVIDIA RTX A4000 (Ampere architecture, 16 GB VRAM).
"""

import logging
import numpy as np
from typing import Tuple, Optional, Dict, Any

try:
    from core.constants import DEFAULT_TEMPERATURE
except ImportError:
    from .constants import DEFAULT_TEMPERATURE

logger = logging.getLogger(__name__)

# Try to import CuPy (CUDA native, preferred)
try:
    import cupy as cp
    from cupyx.scipy.linalg import expm as cp_expm
    CUPY_AVAILABLE = True
    logger.info(f"CuPy available: {cp.__version__} (CUDA native)")
except ImportError:
    CUPY_AVAILABLE = False
    cp = None

# Try to import JAX (fallback)
try:
    import jax
    import jax.numpy as jnp
    from jax import jit, vmap, grad
    from jax.scipy.linalg import expm as jax_expm
    JAX_AVAILABLE = True
    
    # Configure JAX for GPU
    jax.config.update('jax_platform_name', 'gpu')
    jax.config.update('jax_enable_x64', False)  # float32 for speed
    logger.info(f"JAX available: {jax.__version__} (fallback)")
    
except ImportError:
    JAX_AVAILABLE = False
    jax = None
    logger.warning("Neither CuPy nor JAX available, GPU acceleration disabled")

# Determine GPU backend
GPU_AVAILABLE = CUPY_AVAILABLE or JAX_AVAILABLE
GPU_BACKEND = 'cupy' if CUPY_AVAILABLE else ('jax' if JAX_AVAILABLE else 'none')


class GPUQuantumDynamics:
    """GPU-accelerated quantum dynamics simulator using JAX."""
    
    def __init__(self, hamiltonian: np.ndarray, temperature: float = DEFAULT_TEMPERATURE,
                 use_gpu: bool = True):
        """
        Initialize GPU quantum dynamics simulator.
        
        Parameters
        ----------
        hamiltonian : np.ndarray
            System Hamiltonian (n x n)
        temperature : float
            Temperature in Kelvin
        use_gpu : bool
            Enable GPU acceleration
        """
        self.H = hamiltonian
        self.n_sites = hamiltonian.shape[0]
        self.temperature = temperature
        self.use_gpu = use_gpu and JAX_AVAILABLE
        
        if self.use_gpu:
            # Transfer Hamiltonian to GPU
            self.H_gpu = jnp.array(hamiltonian, dtype=jnp.float32)
            logger.info(f"GPU dynamics initialized: {self.n_sites} sites, T={temperature}K")
        else:
            logger.info(f"CPU dynamics initialized: {self.n_sites} sites, T={temperature}K")
    
    @staticmethod
    @jit
    def _liouvillian_step_gpu(rho, H, dt):
        """Single Liouvillian time step on GPU (JIT-compiled)."""
        # Commutator: -i[H, ρ]
        commutator = -1j * (jnp.matmul(H, rho) - jnp.matmul(rho, H))
        return rho + dt * commutator
    
    @staticmethod
    @jit
    def _rk4_step_gpu(rho, H, dt):
        """4th-order Runge-Kutta step on GPU (JIT-compiled)."""
        def drho_dt(rho_t):
            return -1j * (jnp.matmul(H, rho_t) - jnp.matmul(rho_t, H))
        
        k1 = drho_dt(rho)
        k2 = drho_dt(rho + 0.5 * dt * k1)
        k3 = drho_dt(rho + 0.5 * dt * k2)
        k4 = drho_dt(rho + dt * k3)
        
        return rho + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
    
    def simulate_batch_trajectories(self, initial_states: np.ndarray,
                                    time_points: np.ndarray,
                                    method: str = 'rk4') -> np.ndarray:
        """
        Simulate multiple trajectories in parallel on GPU.
        
        Parameters
        ----------
        initial_states : np.ndarray
            Array of initial density matrices (batch_size, n, n)
        time_points : np.ndarray
            Time points for evolution (n_times,)
        method : str
            Integration method ('euler' or 'rk4')
        
        Returns
        -------
        trajectories : np.ndarray
            Density matrices at each time point (batch_size, n_times, n, n)
        """
        if not self.use_gpu:
            return self._simulate_batch_cpu(initial_states, time_points, method)
        
        batch_size = initial_states.shape[0]
        n_times = len(time_points)
        dt = time_points[1] - time_points[0]
        
        logger.info(f"GPU batch simulation: {batch_size} trajectories, {n_times} time points")
        
        # Transfer to GPU
        rho_batch = jnp.array(initial_states, dtype=jnp.complex64)
        H_gpu = self.H_gpu.astype(jnp.complex64)
        
        # Vectorized time evolution
        if method == 'rk4':
            step_func = lambda rho: self._rk4_step_gpu(rho, H_gpu, dt)
        else:
            step_func = lambda rho: self._liouvillian_step_gpu(rho, H_gpu, dt)
        
        # Vectorize over batch dimension
        batched_step = vmap(step_func)
        
        # Time evolution loop
        trajectories = []
        rho_current = rho_batch
        
        for i in range(n_times):
            trajectories.append(rho_current)
            if i < n_times - 1:
                rho_current = batched_step(rho_current)
        
        # Stack and transfer back to CPU
        trajectories_gpu = jnp.stack(trajectories, axis=1)
        trajectories_cpu = np.array(trajectories_gpu)
        
        logger.info(f"GPU simulation complete: {trajectories_cpu.shape}")
        return trajectories_cpu
    
    def _simulate_batch_cpu(self, initial_states: np.ndarray,
                           time_points: np.ndarray,
                           method: str = 'rk4') -> np.ndarray:
        """Fallback CPU implementation."""
        batch_size = initial_states.shape[0]
        n_times = len(time_points)
        dt = time_points[1] - time_points[0]
        
        trajectories = np.zeros((batch_size, n_times, self.n_sites, self.n_sites),
                               dtype=np.complex128)
        
        for b in range(batch_size):
            rho = initial_states[b]
            for t in range(n_times):
                trajectories[b, t] = rho
                if t < n_times - 1:
                    # Simple Euler step
                    commutator = -1j * (self.H @ rho - rho @ self.H)
                    rho = rho + dt * commutator
        
        return trajectories
    
    def compute_populations_batch(self, density_matrices: np.ndarray) -> np.ndarray:
        """
        Extract populations from batch of density matrices on GPU.
        
        Parameters
        ----------
        density_matrices : np.ndarray
            Array of density matrices (batch_size, n_times, n, n)
        
        Returns
        -------
        populations : np.ndarray
            Populations (batch_size, n_times, n)
        """
        if not self.use_gpu:
            # CPU fallback
            return np.real(np.diagonal(density_matrices, axis1=2, axis2=3))
        
        # GPU computation
        rho_gpu = jnp.array(density_matrices)
        
        @jit
        def extract_diag(rho):
            return jnp.real(jnp.diagonal(rho, axis1=-2, axis2=-1))
        
        # Vectorize over batch and time dimensions
        batched_diag = vmap(vmap(extract_diag))
        populations_gpu = batched_diag(rho_gpu)
        
        return np.array(populations_gpu)


def gpu_ensemble_average(trajectories: np.ndarray, axis: int = 0, backend: str = 'auto') -> np.ndarray:
    """
    Compute ensemble average on GPU using CuPy or JAX.
    
    Parameters
    ----------
    trajectories : np.ndarray
        Array of trajectories (n_traj, n_times, ...)
    axis : int
        Axis to average over
    backend : str
        GPU backend ('auto', 'cupy', 'jax', or 'cpu')
    
    Returns
    -------
    average : np.ndarray
        Ensemble-averaged trajectory
    """
    if backend == 'auto':
        backend = GPU_BACKEND
    
    if backend == 'cupy' and CUPY_AVAILABLE:
        traj_gpu = cp.array(trajectories)
        avg_gpu = cp.mean(traj_gpu, axis=axis)
        return cp.asnumpy(avg_gpu)
    elif backend == 'jax' and JAX_AVAILABLE:
        traj_gpu = jnp.array(trajectories)
        avg_gpu = jnp.mean(traj_gpu, axis=axis)
        return np.array(avg_gpu)
    else:
        return np.mean(trajectories, axis=axis)


def gpu_batch_coherence(density_matrices: np.ndarray, backend: str = 'auto') -> np.ndarray:
    """
    Compute coherence for batch of density matrices on GPU.
    
    Parameters
    ----------
    density_matrices : np.ndarray
        Array of density matrices (batch_size, n_times, n, n)
    backend : str
        GPU backend ('auto', 'cupy', 'jax', or 'cpu')
    
    Returns
    -------
    coherences : np.ndarray
        Coherence values (batch_size, n_times)
    """
    if backend == 'auto':
        backend = GPU_BACKEND
    
    batch_size, n_times, n, _ = density_matrices.shape
    
    if backend == 'cupy' and CUPY_AVAILABLE:
        # CuPy computation
        rho_gpu = cp.array(density_matrices)
        coherences = cp.zeros((batch_size, n_times))
        mask = 1.0 - cp.eye(n)
        
        for b in range(batch_size):
            for t in range(n_times):
                coherences[b, t] = cp.sum(cp.abs(rho_gpu[b, t] * mask))
        
        return cp.asnumpy(coherences)
    
    elif backend == 'jax' and JAX_AVAILABLE:
        # JAX computation
        rho_gpu = jnp.array(density_matrices)
        
        @jit
        def coherence_l1(rho):
            n = rho.shape[0]
            mask = 1.0 - jnp.eye(n)
            return jnp.sum(jnp.abs(rho * mask))
        
        # Vectorize over batch and time dimensions
        batched_coherence = vmap(vmap(coherence_l1))
        coherences_gpu = batched_coherence(rho_gpu)
        
        return np.array(coherences_gpu)
    
    else:
        # CPU fallback
        coherences = np.zeros((batch_size, n_times))
        for b in range(batch_size):
            for t in range(n_times):
                rho = density_matrices[b, t]
                mask = 1.0 - np.eye(n)
                coherences[b, t] = np.sum(np.abs(rho * mask))
        return coherences
        return coherences
