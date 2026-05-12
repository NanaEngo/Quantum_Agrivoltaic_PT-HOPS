# OOM Audit Report — Third Pass (Definitive)
**Codebase:** `quantum_simulations_framework_parallel_260512`  
**Date:** 2026-05-12  
**Server:** ThinkStation P720 — 2× Intel Xeon Gold 6136 (48 cores), 128 GB RAM, NVIDIA RTX A4000

---

## Methodology

All 96 Python files were enumerated with `find` and audited with exhaustive grep patterns covering every mechanism that can spawn parallel processes or estimate memory:

- `Parallel(`, `Pool(`, `ProcessPoolExecutor`, `ThreadPoolExecutor`
- `n_jobs =`, `n_workers =`
- `def _get_memory_estimate`, `def _estimate_memory`
- `estimate = BASE_TRAJ_MEMORY_GB *` (without `modes_factor`)
- `n_jobs = min(n_mem_jobs, cpu_count)` (without hard cap)
- `get_safe_n_jobs(BASE_TRAJ_MEMORY_GB)`
- `cpu_count * 0.5` (unsafe fallback)
- `MAX_N_JOBS`

---

## Memory budget

| Parameter | Value |
|---|---|
| Total RAM | 128 GB |
| Safety limit (66 %) | ~80 GB |
| Full FMO trajectory (189 modes, L=8, K=2) | **~54 GB** |
| Safe max concurrent trajectories | **1** |

---

## All issues found across three passes — 17 total

| Pass | # | File | Line | Issue | Peak RAM | Status |
|---|---|---|---|---|---|---|
| 1 | 1 | `core/constants.py` | 202 | `MAX_N_JOBS=10` | 540 GB | ✅ Fixed |
| 1 | 2 | `src/core/constants.py` | 202 | `MAX_N_JOBS=10` | 540 GB | ✅ Fixed |
| 1 | 3 | `core/hops_simulator.py` | ~824 | `len(gw_sysbath)` NameError → fallback `n_jobs=48` | 2592 GB | ✅ Fixed |
| 1 | 4 | `core/memory_manager.py` | 60 | `validate_and_adapt(default=21)` | 756 GB | ✅ Fixed |
| 1 | 5 | `core/memory_manager.py` | 125 | `_estimate_memory(default=21)` | 756 GB | ✅ Fixed |
| 1 | 6 | `core/memory_manager.py` | ~83 | `batch_size=max(n_jobs, n_traj//4)=25` | 1350 GB | ✅ Fixed |
| 1 | 7 | `src/core/memory_aware_patch.py` | 81 | `validate_and_adapt()` without n_hierarchy_modes | 756 GB | ✅ Fixed |
| 1 | 8 | `utils/parallel_utils.py` | 27 | `get_safe_n_jobs(default=2.0)` → n_jobs=42 | 2268 GB | ✅ Fixed |
| 2 | 9 | `utils/parallel_utils.py` | ~240 | `parallel_trajectory_simulation(n_workers=40)` | 2160 GB | ✅ Fixed |
| 2 | 10 | `pipelines/jpcl_resubmission/main.py` | 631 | `get_safe_n_jobs(BASE_TRAJ_MEMORY_GB)` temp sweep | 756 GB | ✅ Fixed |
| 2 | 11 | `pipelines/jpcl_resubmission/main.py` | 721 | `get_safe_n_jobs(BASE_TRAJ_MEMORY_GB)` disorder | 1512 GB | ✅ Fixed |
| 2 | 12 | `reproducibility/main.py` | 715 | `get_safe_n_jobs(BASE_TRAJ_MEMORY_GB)` temp sweep | 756 GB | ✅ Fixed |
| 2 | 13 | `reproducibility/main.py` | 805 | `get_safe_n_jobs(BASE_TRAJ_MEMORY_GB)` disorder | 1512 GB | ✅ Fixed |
| 2 | 14 | `models/quantum_dynamics_simulator.py` | ~498 | `_get_memory_estimate()` no `modes_factor` | 756 GB | ✅ Fixed |
| 2 | 15 | `models/quantum_dynamics_simulator.py` | ~580 | `n_jobs=min(n_mem_jobs,cpu_count)` no cap + fallback `cpu_count*0.5=24` | 1296 GB | ✅ Fixed |
| 3 | 16 | `core/hops_simulator.py` | 369 | `_get_memory_estimate()` no `modes_factor` (MemoryAwareJobScheduler fallback path) | 756 GB | ✅ Fixed |
| 3 | 17 | `src/core/hops_simulator.py` | 790 | psutil-unavailable fallback `cpu_count*0.5=24` | 1296 GB | ✅ Fixed |

---

## Final grep verification (all clean)

```
estimate = BASE_TRAJ without modes_factor    →  NONE ✅
n_jobs = min(n_mem_jobs, cpu_count) no cap  →  NONE ✅
get_safe_n_jobs(BASE_TRAJ_MEMORY_GB)         →  NONE ✅
cpu_count * 0.5 as n_jobs fallback           →  NONE ✅ (only in warning threshold check)
```

---

## State of every `_get_memory_estimate` / `_estimate_memory`

| File | Signature | modes_factor | Safe |
|---|---|---|---|
| `core/hops_simulator.py` | `(self, n_hierarchy_modes=189)` | ✅ | ✅ |
| `core/memory_manager.py` | `(self, n_hierarchy_modes=189)` | ✅ | ✅ |
| `src/core/hops_simulator.py` | `(self, n_hierarchy_modes=189)` | ✅ | ✅ |
| `models/quantum_dynamics_simulator.py` | `(self)` reads `self.gw_sysbath` | ✅ | ✅ |

---

## State of every `Parallel(` call

| File | n_jobs source | Safe |
|---|---|---|
| `core/hops_simulator.py` | `MemoryAwareJobScheduler.validate_and_adapt(n_hierarchy_modes)` → 1 | ✅ |
| `src/core/hops_simulator.py` | `min(n_mem_jobs, cpu_count, MAX_N_JOBS=1)` | ✅ |
| `src/core/memory_aware_patch.py` | `MemoryAwareJobScheduler.validate_and_adapt(n_hierarchy_modes)` → 1 | ✅ |
| `models/quantum_dynamics_simulator.py` | `min(n_mem_jobs, cpu_count, 1)` | ✅ |
| `reproducibility/main.py` (×2) | `get_safe_n_jobs(54.0)` → 1 | ✅ |
| `pipelines/jpcl_resubmission/main.py` (×2) | `get_safe_n_jobs(54.0)` → 1 | ✅ |
| `pipelines/temperature_sweep/sweep.py` (×2) | monkeypatched to `lambda: 1` | ✅ |
| `reproducibility/run_temp_sweep_only.py` (×2) | monkeypatched to `lambda: 1` | ✅ |

---

## Safe locations (confirmed no changes needed)

- `core/memory_manager.py:112` — `cpu_count() * 0.5` is a **warning threshold**, not an n_jobs assignment.
- `reproducibility/audit_convergence.py` — all audit runs use `n_traj=1` explicitly.
- `pipelines/convergence_audit/audit.py` — same.
- `reproducibility/main_with_resume.py` — calls `sim.simulate_dynamics()` which routes through `HopsSimulator` → `MemoryAwareJobScheduler` → n_jobs=1.
- `ParallelExecutor` in `utils/parallel_utils.py` — never instantiated in the active pipeline.
- `ResumableParallelExecutor` in `reproducibility/resume_capability.py` — handles checkpointing only.

---

## Expected runtime

```
Full FMO run (189 modes, L=8, K=2):
  modes_factor = 189 / 21 = 9.0
  traj_mem_gb  = 6.0 × 1.0 × 1.0 × 9.0 = 54 GB/traj
  n_jobs       = 1  (all paths)
  100 trajectories × ~9 min ≈ 15 h wall-time
```

**No code path in the codebase can launch more than 1 concurrent HOPS trajectory.**
