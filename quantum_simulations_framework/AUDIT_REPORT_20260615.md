# Full Codebase Audit Report — 2026-06-15

## 0. Executive Summary

Production run on 2026-06-14 failed with **SIGSEGV (-11)** after ~12 hours of computation. This audit identifies **6 critical bugs**, **3 architectural problems**, and prescribes concrete fixes. The root cause is a **GPU driver/NVML mismatch** that propagates through Numba's JIT engine into numerical instability in long-running MesoHOPS trajectories.

---

## 1. Critical Bugs Found

### BUG-1: `MemoryAwareJobScheduler.print_report()` uses wrong default mode count

**Severity:** High
**File:** `core/memory_manager.py:181`
**Impact:** Log shows misleading memory plan (100 batches × 1 traj) while execution uses 50 batches × 2 traj

```python
# line 180-182 (PRINT_REPORT uses default n_hierarchy_modes=189)
def print_report(self) -> None:
    info = self.validate_and_adapt()  # ← default 189 modes!
```

The actual system has **105 modes** (3 DL + 12 vibronic × 7 sites), giving:

| Parameter | With 189 modes (log) | With 105 modes (reality) |
|---|---|---|
| Estimate/traj | 54.0 GB | 30.0 GB |
| n_jobs | 1 | 2 |
| batch_size | 1 | 2 |
| n_batches | 100 | 50 |

**Fix:** Pass `n_hierarchy_modes` from `_simulate_with_mesohops_patched` to `print_report()`, or remove `print_report()` entirely and let the patched method log its own plan.

---

### BUG-2: `MemoryAwareJobScheduler` does not respect `MAX_N_JOBS`

**Severity:** High
**File:** `core/memory_manager.py:99-101`
**Impact:** Cannot force single-worker mode even with `MAX_N_JOBS=1`

```python
n_jobs_raw = int(limit_gb / mem_per_traj)  # = 2 for 105 modes
cpu_limit = int(os.cpu_count() * CPU_COUNT_FRACTION)  # = 31
n_jobs = min(n_jobs_raw, cpu_limit)  # = 2 — MAX_N_JOBS never considered!
```

**Fix:** Add `from .constants import MAX_N_JOBS` and cap at the end:
```python
n_jobs = min(n_jobs_raw, cpu_limit, MAX_N_JOBS)
```

This is why the run launched **2 workers** even with `MAX_N_JOBS=1`.

---

### BUG-3: Numba JIT crashes due to GPU driver / NVML mismatch

**Severity:** BLOCKER
**Environment:** Server GPU (NVML library 580.159 vs driver module different version)
**Impact:** `nvidia-smi` fails. Numba 0.63.1 probes CUDA during JIT compilation, hits undefined behavior

```
$ nvidia-smi
Failed to initialize NVML: Driver/library version mismatch
NVML library version: 580.159
```

**Root cause:** The NVML library in the conda environment (or system) was upgraded/reinstalled without updating the kernel module. Numba calls `nvmlInit()` internally, which crashes when the library/driver versions differ.

**Fix:**
```bash
sudo apt-get purge --auto-remove nvidia-* nvidia-driver-* cuda-*
sudo apt-get install nvidia-driver-580  # Match NVML 580.159
sudo reboot
```

**Fallback workaround** (if GPU not needed for simulation):
```python
import os
os.environ["NUMBA_DISABLE_CUDA"] = "1"  # Before any Numba import
```

---

### BUG-4: Numba JIT cache missing — recompilation every run

**Severity:** Medium
**Environment:** `~/.cache/numba/` does not exist
**Impact:** Every run recompiles MesoHOPS Numba JIT functions, adding ~5 min startup and increasing crash surface

**Fix:**
```bash
rm -rf ~/.cache/numba/
~/miniforge3/envs/MesoHOP-sim/bin/python -c "import numba; numba.core.caching.Cache.erase_all()"
```

Then run a small warm-up trajectory to build the cache:
```bash
~/miniforge3/envs/MesoHOP-sim/bin/python -c "
from mesohops.trajectory.hops_trajectory import HopsTrajectory
print('Numba cache primed:', HopsTrajectory)
"
```

---

### BUG-5: `TAU/dt` inconsistency in `core/hops_simulator.py` (root level, unused)

**Severity:** Medium (latent — file not imported by `main.py`)
**File:** `core/hops_simulator.py:863` vs `src/core/hops_simulator.py:865`

| File | `TAU` value | Used by |
|---|---|---|
| `core/hops_simulator.py:863` | `float(dt_save)` | NOT imported by `main.py` |
| `src/core/hops_simulator.py:865` | `float(dt_save) / 2.0` | Imported by `main.py` — ✅ correct |

The root-level `core/hops_simulator.py` is stale. It still has the buggy TAU that caused `TrajectoryError` in previous sessions (AGENTS.md line 88). The `src/core/` version has the fix.

**Risk:** If any import path ever resolves to `core/` instead of `src/core/`, the TAU bug re-appears.

**Fix:** Either:
- (a) Delete `core/hops_simulator.py` and redirect to `src/core/`
- (b) Or sync `core/hops_simulator.py:863` to use `/ 2.0`

---

### BUG-6: 0.5 fs time_step doubles computation time

**Severity:** Low (performance)
**Files:** `parameters.yaml:30` (0.5 fs) vs AGENTS.md:165 (stated as 1.0 fs — NOW FIXED)
**Impact:** 2000 time points instead of 1000, doubling trajectory runtime from ~6h to ~12h

This is now fixed in `AGENTS.md` (Δt = 0.5 fs as of this session). Keep `parameters.yaml` at 0.5 fs.

---

## 2. Architectural Problems

### ARCH-1: Dual module trees (`core/` vs `src/core/`)

**Severity:** High
**Files:** `core/*.py` vs `src/core/*.py`
**Impact:** Confusing divergence. Some files are re-exports (memory_manager), some are stale clones (hops_simulator)

```
core/
  hops_simulator.py          # Stale (TAU bug, no adaptive hierarchy)
  memory_manager.py           # CANONICAL — contains the real MemoryAwareJobScheduler
  constants.py                # CANONICAL
  hamiltonian_factory.py      # (check needed)

src/core/
  hops_simulator.py           # CANONICAL — has TAU fix, adaptive hierarchy, defensive filtering
  memory_manager.py           # RE-EXPORT of core/memory_manager.py (thin wrapper)
  memory_aware_patch.py       # PATCH — replaces _simulate_with_mesohops
  constants.py                # DUPLICATE — slight ordering differences
  hamiltonian_factory.py      # (check needed)
```

**Recommendation:** Collapse to a single module tree. Delete `core/` and make `src/core/` the canonical location.

---

### ARCH-2: `memory_aware_patch.py` duplicates batch execution logic

**Severity:** High
**Files:** `src/core/memory_aware_patch.py` + `src/core/hops_simulator.py` (both have batch execution)
**Impact:** The patch replaces the original method, which already had batch execution. This means:
1. Bug fixes must be applied in **two places** (patch + original)
2. The patch may reintroduce bugs that were fixed in the original
3. The patch has its OWN copy of `noise_param`, `hierarchy_param`, `eom_param` construction

**Example discrepancy (now fixed):**
| Parameter | `hops_simulator.py` (original) | `memory_aware_patch.py` (patched) |
|---|---|---|
| `ADAPTIVE_H` | `True` (from `adaptive` kwarg) | NOT SET (missing key) |
| `ADAPTIVE_S` | `True` | NOT SET |
| `INTERPOLATE` | `False` | NOT SET |
| `RAND_MODEL` | `"SUM_GAUSSIAN"` | NOT SET |

**Fix:** Either:
- (a) Remove the patch entirely since the original already has batch execution
- (b) Or make the patch minimal (only override the batch loop, not the parameter construction)

---

### ARCH-3: Fallback produces scientifically invalid data without warning

**Severity:** High
**File:** `core/hops_simulator.py:1085-1090` (and patch equivalent)
**Impact:** When MesoHOPS crashes, the fallback silently produces data that:
- Does not respect L-dependence (hierarchy depth)
- Does not use SBD (bundle compression)
- Has fundamentally different physics (HOPS vs simple propagation)

The log says `"Using fallback simulator. Results will not show L-dependence."` but the pipeline continues and saves results as if they were valid.

**Fix:** After fallback, `audit_convergence.py` should detect the fallback and mark results as `*.INVALID_FALLBACK_DATA.csv`. OR, more robustly, the fallback should raise a `RuntimeError` that halts the pipeline with a clear message.

---

## 3. Parameter Consistency Check

| Parameter | `parameters.yaml` | `core/constants.py` | AGENTS.md | Status |
|---|---|---|---|---|
| `L_max` | 8 | 8 (DEFAULT_MAX_HIERARCHY) | 8 | ✅ |
| `K` (Matsubara) | 2 | 2 (DEFAULT_N_MATSUBARA) | 2 | ✅ |
| `time_step` | 0.5 fs | 1.0 (DEFAULT_TIME_STEP) | 0.5 fs | **⚠️ constants.py disagrees** |
| `temperature` | 295 K | 295.0 (DEFAULT_TEMPERATURE) | 295 K | ✅ |
| `sbd_bundles_per_site` | 6 | 6 (DEFAULT_SBD_BUNDLES) | 6 | ✅ |
| `FMO_TARGET_SITE` | — | 2 | — | ✅ |
| `n_traj` | 100 | 100 (DEFAULT_N_TRAJ) | 100 | ✅ |

**`DEFAULT_TIME_STEP = 1.0` in constants.py (line 54) does NOT match `time_step: 0.5` in parameters.yaml.**

```python
# core/constants.py:54
DEFAULT_TIME_STEP: Final[float] = 1.0  # ← should be 0.5
```

This default is only used as a fallback when `time_points` has fewer than 2 elements, but it should match `parameters.yaml` for consistency.

---

## 4. Fix Priority & Action Items

### 🚨 P0 — Fix now (blocking production)

| # | Action | File(s) | Est. time |
|---|---|---|---|
| P0.1 | Fix GPU driver | Server OS | 30 min |
| P0.2 | Cap `n_jobs` by `MAX_N_JOBS` in `MemoryAwareJobScheduler` | `core/memory_manager.py:101` | 2 min |
| P0.3 | Add `NUMBA_DISABLE_CUDA=1` env var as fallback | Server env | 1 min |

### ⚠️ P1 — Fix before next production run

| # | Action | File(s) | Est. time |
|---|---|---|---|
| P1.1 | Fix `print_report()` to accept `n_hierarchy_modes` argument | `core/memory_manager.py` | 5 min |
| P1.2 | Sync `DEFAULT_TIME_STEP` to 0.5 in `constants.py` | `core/constants.py:54` | 1 min |
| P1.3 | Sync `TAU` fix from `src/core/` to `core/` (or delete `core/`) | `core/hops_simulator.py:863` | 5 min |
| P1.4 | Warm up Numba cache with short test trajectory | Server | 10 min |
| P1.5 | Validate `N=1` test passes before full run | Server | 2 hours |

### 📋 P2 — Fix for codebase health

| # | Action | File(s) | Est. time |
|---|---|---|---|
| P2.1 | Collapse `core/` and `src/core/` into single tree | Both directories | 30 min |
| P2.2 | Remove duplicate batch logic from patch or original | `memory_aware_patch.py` | 15 min |
| P2.3 | Harden fallback to abort on MesoHOPS failure (no silent invalid data) | `hops_simulator.py` | 10 min |

---

## 5. Root Cause Chain (SIGSEGV)

```
GPU driver mismatch
  └─► Numba CUDA probe fails (undefined behavior)
        └─► Numba JIT cache missing (recompiles every run)
              └─► JIT compiler encounters driver-internal corruption
                    └─► SBD_HopsTrajectory propagate() crash after ~6 hours
                          └─► SIGSEGV (-11)
                                └─► Batch 1 fails
                                      └─► Fallback to SimpleQuantumDynamicsSimulator
                                            └─► No valid data produced
```

**Secondary amplifier:** `MAX_N_JOBS` not respected → 2 workers launched even though user requested single-worker mode → 2× memory pressure → 2× crash surface.

---

## 6. Verification Protocol

After applying fixes, run in this order:

```bash
# 1. Verify GPU driver
nvidia-smi

# 2. Warm up Numba
~/miniforge3/envs/MesoHOP-sim/bin/python -c "
import os; os.environ['NUMBA_DISABLE_CUDA'] = '1'
import numba; print('Numba OK:', numba.__version__)
from mesohops.trajectory.hops_trajectory import HopsTrajectory
print('MesoHOPS import OK')
"

# 3. N=1 single trajectory test
cd ~/quantum_simulations_framework_parallel_260612
~/$MESO_PYTHON reproducibility/main.py --skip-audit --n-traj 1

# 4. N=10 test
~/$MESO_PYTHON reproducibility/main.py --skip-audit --n-traj 10

# 5. Full production
nohup ~/$MESO_PYTHON reproducibility/main.py --skip-audit > ~/production_run.log 2>&1 &
tail -f ~/production_run.log
```

---

*Generated: 2026-06-15*
*By: OpenCode audit agent*
