# ADR-0002: MemoryAwareJobScheduler with RLIMIT_AS for OOM prevention

**Date**: 2026-06-21
**Status**: accepted
**Deciders**: Nana Engo

## Context

The production simulation on the 125 GB server failed with SIGSEGV after 12 hours due to memory exhaustion. Each trajectory at L=8, K=2, SBD=3 consumes ~6 GB RAM, and parallel execution with 24 workers can quickly oversubscribe the available 125 GB. Python's garbage collector does not reclaim memory fast enough when numpy/scipy arrays are freed, and the OS OOM-killer kills random processes (including the simulation driver) rather than individual trajectory workers.

A hardcoded `MAX_N_JOBS=1` was used as a workaround, but this made the 200-trajectory production run take days instead of hours.

## Decision

Implement a layered OOM prevention strategy:

1. `MemoryAwareJobScheduler` — estimates per-trajectory RAM using exact combinatorial scaling of the hierarchy size, and calculates safe `n_jobs` and `batch_size` based on available RAM × `MEMORY_FRACTION_LIMIT` (0.66).
2. `resource.setrlimit(RLIMIT_AS)` — applied per-worker in subprocess context only (detected via `multiprocessing.parent_process() is not None`), preventing individual workers from exceeding their budget. Adds `BASE_PYTHON_OVERHEAD_GB` (2 GB) for numpy/scipy VmSize.
3. Batch execution — trajectories are split into batches of `n_jobs` each, with `gc.collect()` between batches.
4. OOM recovery — catches `MemoryError` with exponential `n_jobs //= 2` backoff, falling back to `n_jobs=1`.

## Alternatives Considered

### Alternative 1: Single trajectory per process (n_jobs=1)
- **Pros**: No OOM risk, simplest design
- **Cons**: 200 trajectories × 30 min each = 100 hours, impractical
- **Why not**: Makes production sweeps infeasible within submission deadlines

### Alternative 2: Use psutil + external memory monitoring
- **Pros**: Reactive, adapts to actual usage
- **Cons**: Race condition — by the time memory is detected as high, it's too late to prevent OOM
- **Why not**: Proactive estimation via combinatorial scaling prevents the race

### Alternative 3: Subprocess with timeout + memory limit per worker
- **Pros**: Strong isolation
- **Cons**: Pickling overhead for large Hamiltonian objects (3.2 GB serialized)
- **Why not**: joblib with `max_nbytes=None` avoids memmap overhead

## Consequences

### Positive
- Production 200-traj run completed in ~30 hours (n_jobs=10-12 dynamically)
- No OOM-killer intervention in any Phase 1-3 sweep
- RLIMIT_AS is safely skipped in main process (avoids breaking git/pandas I/O)
- Memory estimation correctly scales from L=3 (laptop, 0.5 GB/traj) to L=8 (server, 6 GB/traj)

### Negative
- SBD compression must be accounted for in the estimator (capping effective modes at 21) — incorrect mode count would underestimate memory by ~5×
- `BASE_PYTHON_OVERHEAD_GB` (2 GB) is empirical and may need recalibration for different numpy/scipy versions
