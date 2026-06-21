"""
Memory-aware patching for HopsSimulator — MINIMAL STUB.

The canonical src/core/hops_simulator._simulate_with_mesohops() already
contains built-in memory-aware parallelization (psutil-based n_jobs
calculation, batch execution, memory cleanup between batches).

This module is retained as a no-op for backward compatibility with
reproducibility/main.py which calls apply_memory_aware_patching().
"""

import logging

logger = logging.getLogger(__name__)


def apply_memory_aware_patching():
    """
    No-op stub — memory-aware features are already built into
    src/core/hops_simulator._simulate_with_mesohops().
    
    Previously this module replaced the entire _simulate_with_mesohops
    method with a batch-execution version. The canonical simulator now
    includes these features natively, so this patch is no longer needed.
    """
    logger.info(
        "Memory-aware patching skipped: features are built into "
        "HopsSimulator._simulate_with_mesohops natively."
    )
