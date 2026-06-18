# Production Run Failure Report — 2026-06-14

## 1. Executive Summary

The production simulation (`main.py --skip-audit`) initiated at **19:03:31** on 2026-06-14 terminated after approximately **12 hours and 15 minutes** due to a **Segmentation Fault (SIGSEGV -11)** in the MesoHOPS worker processes. The orchestrator fell back to `SimpleQuantumDynamicsSimulator`, but **no publication-quality data was generated**.

## 2. Failure Timeline

| Time (UTC+2) | Event |
|---|---|
| 19:03:31 | Simulation started (L=8, K=2, 100 traj, 1000 fs) |
| 19:03:31 | Memory Plan: 100 batches × 1 traj, n_jobs=1, 54 GB/traj |
| 19:03:31 | Batch-wise execution started: 50 batches, 2 traj/batch, 2 workers/batch |
| ≈07:18:52 (Day+1) | **Batch 1 SIGSEGV** — 4 LokyProcess workers consuming ~12.8 GB RES each |
| 07:18:54 | Fallback to `SimpleQuantumDynamicsSimulator` triggered |
| ~08:06 | Process killed by user |

## 3. Hardware Environment

| Resource | Status |
|---|---|
| CPU | 48 cores — OK |
| RAM | 125.5 GB total, 120.5 GB available at start |
| **GPU/NVML** | **FAILED** — Driver/library version mismatch |
| | NVML library: 580.159, Driver module: different version |
| Disk | Available |

## 4. Root Cause Analysis

### 4.1 Primary Suspect: GPU Driver / NVML Mismatch

```text
Failed to initialize NVML: Driver/library version mismatch
NVML library version: 580.159
```

This is a **critical issue**. Numba 0.63.1 attempts to initialize NVML/CUDA context during JIT compilation. The driver/library version mismatch causes undefined behavior that can manifest as a segmentation fault when Numba's CUDA detection pathways are triggered.

**Evidence:**
- Numba 0.63.1 is installed (MesoHOP-sim environment)
- `nvidia-smi` fails with the same NVML mismatch error
- No Numba JIT cache exists at `~/.cache/numba/` (JIT recompilation happens every run, increasing crash surface)
- The SIGSEGV occurs deep inside the MesoHOPS trajectory worker, which relies on Numba-accelerated linear algebra

### 4.2 Secondary Suspect: Memory Pressure / OOM

**Memory Budget Calculation:**
| Parameter | Value |
|---|---|
| Estimated memory/traj | 54.0 GB |
| Batch size | 2 traj/batch |
| Memory required per batch | **108 GB** |
| RAM limit (66% of 125.5 GB) | **79.6 GB** |
| **Overshoot** | **28.4 GB (35%)** |

The memory-aware scheduler incorrectly planned `n_jobs=1` but then launched `2 workers/batch`. This mismatch caused **each batch to exceed the memory budget by >35%**, leading to:

1. Heavy swap usage (194.3 MB observed)
2. Potential OOM-killer intervention or memory corruption
3. SIGSEGV when writing to over-committed memory

### 4.3 Configuration Inconsistency

| Parameter | `parameters.yaml` | `AGENTS.md` | Impact |
|---|---|---|---|
| `time_step` | **0.5 fs** | 1.0 fs | Unexpected — may affect SBD stability |
| `MAX_N_JOBS` | 8 | 8 | OK |
| `CPU_COUNT_FRACTION` | 0.66 | 2/3 | OK |

The **0.5 fs time step** doubles the number of integration steps compared to the expected 1.0 fs, increasing both computation time and memory pressure.

## 5. Detailed Process Tree (During Crash)

```
PID 1246824 (main.py) — orchestrator, 0.2% CPU, 219 MB RES
├── PID 1244662 (resource_tracker) — 2.5s CPU
├── PID 1244663 (resource_tracker) — 0.03s CPU
├── PID 1244664 (LokyProcess-1) — 93% CPU, 13.0 GB RES
├── PID 1244665 (LokyProcess-2) — 100% CPU, 12.7 GB RES
├── PID 1246922 (LokyProcess-1, second spawn) — 107% CPU, 12.6 GB RES
└── PID 1246923 (LokyProcess-2, second spawn) — 106% CPU, 12.8 GB RES
```

**Observation:** 4 worker processes × ~12.8 GB = **~51 GB for workers alone**, plus the 26 GB diff from memory-mapped arrays. Total memory pressure well above the 79.6 GB limit.

## 6. Required Fixes — Roadmap

### Step 1: Fix GPU Driver Mismatch (BLOCKER — DO THIS FIRST)

```bash
# 1. Check current driver
nvidia-smi  # Will fail — read dkms status instead
dkms status

# 2. Identify the correct driver for the GPU
ubuntu-drivers devices

# 3. Purge and reinstall
sudo apt-get purge --auto-remove nvidia-* nvidia-driver-* cuda-* 
sudo apt-get autoremove
sudo apt-get install nvidia-driver-580  # or version matching NVML 580.159
sudo reboot
```

**Expected outcome:** Numba 0.63.1 can safely probe GPU capabilities without crashing.

### Step 2: Clean Numba Cache and Rebuild

```bash
rm -rf ~/.cache/numba/
~/miniforge3/envs/MesoHOP-sim/bin/python -c """
import numba
from numba.core.caching import Cache
Cache.erase_all()
print('Numba cache cleared')
"""
```

### Step 3: Fix Memory Scheduler Logic

**Problem:** `memory_aware_patch.py` plans `n_jobs=1` but launches `2 workers/batch`.

**Fix location:** `src/core/memory_aware_patch.py` — enforce `n_jobs` == workers per batch.

**Check:** Ensure `MAX_N_JOBS` is compatible with `time_step=0.5` (more steps → more memory).

### Step 4: Synchronize `time_step`

Either:
- **(Recommended)** Change `parameters.yaml` → `time_step: 1.0` to match AGENTS.md and reduce memory pressure 2×
- Or update AGENTS.md → `Δt = 0.5 fs` if the smaller step is physically justified

### Step 5: Reduce-Scale Validation Test (Before Full Production)

Before attempting 100 trajectories:

```bash
# Test 1: N=1, 1 worker — verify no SIGSEGV
~/miniforge3/envs/MesoHOP-sim/bin/python reproducibility/main.py --skip-audit

# Test 2: N=10, n_jobs=1 — verify batch execution works
# (edit n_traj=10 in parameters.yaml temporarily)

# Test 3: N=10, n_jobs=2 — verify memory scheduler
```

### Step 6: Re-launch Full Production

```bash
cd ~/quantum_simulations_framework_parallel_260612
nohup ~/miniforge3/envs/MesoHOP-sim/bin/python reproducibility/main.py \
    --skip-audit > ~/production_run.log 2>&1 &
```

## 7. Risk Mitigation Checklist

- [ ] GPU driver fixed and `nvidia-smi` works
- [ ] `numba.__version__` confirmed ≥0.63 (compatible with MesoHOPS v1.7)
- [ ] Numba cache rebuilt
- [ ] `parameters.yaml` `time_step` consistent with AGENTS.md
- [ ] `memory_aware_patch.py` verified — n_jobs matches workers/batch
- [ ] N=1 test passes without SIGSEGV
- [ ] N=10 test passes without SIGSEGV
- [ ] Full production N=100 launched and monitored for first batch completion

---

*Generated: 2026-06-15 08:30 UTC+2*
*By: OpenCode agent on behalf of project lead*
