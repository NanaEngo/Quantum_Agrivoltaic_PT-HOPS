"""
Parallel Execution Utilities — RE-EXPORT MODULE

Canonical source is src/utils/parallel_utils.py.
This module re-exports all public symbols for backward compatibility.
"""
from src.utils.parallel_utils import (  # noqa: F401
    get_safe_n_jobs,
    estimate_memory_per_traj,
    ParallelExecutor,
)

__all__ = [
    "get_safe_n_jobs",
    "estimate_memory_per_traj",
    "ParallelExecutor",
]
