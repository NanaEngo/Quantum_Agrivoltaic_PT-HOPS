"""\nGPU-accelerated quantum dynamics — RE-EXPORT MODULE\n\nCanonical source is src/core/gpu_dynamics.py.\nThis module re-exports all public symbols for backward compatibility.\n"""
from src.core.gpu_dynamics import (  # noqa: F401
    GPUQuantumDynamics,
    gpu_ensemble_average,
    gpu_batch_coherence,
    GPU_AVAILABLE,
    GPU_BACKEND,
    CUPY_AVAILABLE,
    JAX_AVAILABLE,
)

__all__ = [
    "GPUQuantumDynamics",
    "gpu_ensemble_average",
    "gpu_batch_coherence",
    "GPU_AVAILABLE",
    "GPU_BACKEND",
    "CUPY_AVAILABLE",
    "JAX_AVAILABLE",
]
