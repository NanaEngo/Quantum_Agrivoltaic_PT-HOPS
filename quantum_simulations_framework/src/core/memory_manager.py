"""
Re-export from root-level core.memory_manager for src.core compatibility.

The canonical MemoryAwareJobScheduler lives in core/memory_manager.py.
This module re-exports all public symbols so that import statements
like 'from src.core.memory_manager import MemoryAwareJobScheduler'
resolve correctly from the src.core namespace.
"""

from core.memory_manager import (
    MemoryAwareJobScheduler,
    validate_memory_configuration,
    cleanup_memory,
)

__all__ = [
    "MemoryAwareJobScheduler",
    "validate_memory_configuration",
    "cleanup_memory",
]
