"""
Memory-Aware Job Scheduler — RE-EXPORT MODULE

Canonical source is src/core/memory_manager.py.
This module re-exports all public symbols for backward compatibility.
"""
from src.core.memory_manager import (  # noqa: F401
    MemoryAwareJobScheduler,
    validate_memory_configuration,
    cleanup_memory,
)

__all__ = [
    "MemoryAwareJobScheduler",
    "validate_memory_configuration",
    "cleanup_memory",
]
