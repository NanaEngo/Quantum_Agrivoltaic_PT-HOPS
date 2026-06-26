"""
Utilities for quantum agrivoltaic simulations.

This package provides logging, GPU detection, and parallel execution tools.
"""

from .gpu_detection import GpuInfo, detect_gpu, log_gpu_status
from .logging_config import SimulationLogMixin, get_logger, setup_logging
from .parallel_utils import estimate_memory_per_traj, get_safe_n_jobs

__all__ = [
    "setup_logging",
    "get_logger",
    "SimulationLogMixin",
    "GpuInfo",
    "detect_gpu",
    "log_gpu_status",
    "estimate_memory_per_traj",
    "get_safe_n_jobs",
]
