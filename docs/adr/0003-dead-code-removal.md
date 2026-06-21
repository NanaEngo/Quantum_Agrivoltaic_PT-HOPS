# ADR-0003: Removal of dead GPU code and backward-compat shims

**Date**: 2026-06-21
**Status**: accepted
**Deciders**: Nana Engo

## Context

The codebase accumulated 24 dead files over 6 months of development:
- `gpu_dynamics.py` (319 lines) — GPU-accelerated kernels that were never called anywhere in the codebase; GPU acceleration is not supported by MesoHOPS itself
- `memory_aware_patch.py` — a no-op stub whose functionality had been folded into `HopsSimulator._simulate_with_mesohops()` months earlier, but the stub was kept "for backward compatibility" with no remaining importers
- 13 individual `models/*.py` shims, each re-exporting one class from `src/` — all imports already went through `models/__init__.py` which imports directly from `src.*`
- `extensions/` shims, `utils/` scripts (ParallelExecutor, theme, standalone scripts, import_standardizer)

Additionally, `src/utils/parallel_utils.py` contained `ParallelExecutor` (276 lines of GPU initialization + joblib wrappers) that was completely unused.

## Decision

Remove all 24 dead files and 276 lines of dead code in `parallel_utils.py`. The criteria for removal:
1. File has zero importers across the entire codebase
2. File is a shim that only re-exports from `src/` when the parent `__init__.py` already does so
3. Code has been superseded by a newer implementation and is no longer referenced

Files preserved: `core/constants.py` (imported by root `__init__.py`), `utils/figure_generator.py` and `utils/orca_wrapper.py` (imported by `utils/__init__.py`), `models/__init__.py` (aggregator), `extensions/__init__.py` (aggregator).

## Alternatives Considered

### Alternative 1: Keep all shims
- **Pros**: No risk of breaking external imports (though none existed)
- **Cons**: 24 files of dead code confusing to new developers; 319 lines of GPU code that doesn't work and never did
- **Why not**: Dead code imposes a real cognitive tax — every new developer wastes time figuring out which files are real

### Alternative 2: Mark as deprecated with warnings
- **Pros**: Gradual migration path
- **Cons**: The code has been unused for months with no migration needed; adding warnings adds runtime overhead
- **Why not**: None of these files had any importers to warn

## Consequences

### Positive
- 24 fewer files to maintain
- 595 lines of dead code removed (319 gpu_dynamics.py + 276 ParallelExecutor)
- `src/utils/parallel_utils.py` reduced from 345 to 62 lines, focused on its actual purpose

### Negative
- External tools that imported from the old shim paths (e.g., `from models.quantum_dynamics_simulator import QuantumDynamicsSimulator`) would break — but no such importers were found
- A Jupyter notebook in `archives/` references `from core.hamiltonian_factory import ...` which was a shim — the notebook would need updating before re-run (it's archived, not active)
