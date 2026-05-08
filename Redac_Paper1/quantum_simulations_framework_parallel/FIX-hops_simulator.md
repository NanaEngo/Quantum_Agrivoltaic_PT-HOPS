# FIX-hops_simulator.md

Fixes applied to `core/hops_simulator.py` to resolve runtime errors on the cluster.

---

## Fix 1 — `RuntimeError: No simulator available`

**File:** `core/hops_simulator.py` — `HopsSimulator.__init__`

**Error:**
```
File "core/hops_simulator.py", line 460, in simulate_dynamics
    raise RuntimeError("No simulator available")
RuntimeError: No simulator available
```

**Root cause:**
`_init_fallback()` was only called when `use_mesohops` was `False`. When MesoHOPS
initialised successfully (setting `system_param`), `use_mesohops` stayed `True` and
`fallback_sim` was never set. If MesoHOPS then failed *mid-run* (caught by the
`except (RuntimeError, ModuleNotFoundError)` branch in `simulate_dynamics`), the
code fell through to `fallback_sim` — which was `None` — and raised the error.

**Before:**
```python
if self.use_mesohops:
    self._init_mesohops(**kwargs)

# Initialize fallback only if MesoHOPS was not requested or failed without
# already initializing a fallback inside _init_mesohops
if not self.use_mesohops and self.fallback_sim is None:
    self._init_fallback(**kwargs)
```

**After:**
```python
if self.use_mesohops:
    self._init_mesohops(**kwargs)

# Always initialize fallback so it is available if MesoHOPS fails mid-run.
# _init_mesohops may have already set fallback_sim (on init failure path);
# skip re-initialization in that case.
if self.fallback_sim is None:
    self._init_fallback(**kwargs)
```

---

## Fix 2 — `TypeError: object of type 'int' has no len()`

**File:** `core/hops_simulator.py` — `_simulate_with_mesohops`

**Error:**
```
File "mesohops/basis/hops_hierarchy.py", line 123, in __init__
    if not len(param_i[0]) == self.n_hmodes:
TypeError: object of type 'int' has no len()
```

**Root cause:**
The `"Triangular"` static filter in MesoHOPS expects
`params = [boolean_by_mode, kmax_2]` where `params[0]` is a list of booleans of
length `n_hmodes`. The code was passing `[max_hierarchy]` — a list containing a
single integer — so `param_i[0]` resolved to the integer `max_hierarchy`, which
has no `len()`.

**Before:**
```python
hierarchy_param = {
    "MAXHIER": max_hierarchy,
    "TERMINATOR": True,
    "STATIC_FILTERS": [["Triangular", [max_hierarchy]]],
}
```

**After:**
```python
n_hmodes = len(self.system_param["GW_SYSBATH"])
hierarchy_param = {
    "MAXHIER": max_hierarchy,
    "TERMINATOR": True,
    "STATIC_FILTERS": [["Triangular", [[True] * n_hmodes, max_hierarchy]]],
}
```

`[True] * n_hmodes` applies the triangular filter to all hierarchy modes.
`max_hierarchy` as `kmax_2` imposes no additional per-mode truncation beyond
`MAXHIER`, which is the correct default.

---

## Fix 3 — `TrajectoryError: Timesteps(1.0) … do not match noise.param['TAU'] (2.0)`

**File:** `core/hops_simulator.py` — `_simulate_with_mesohops`

**Error:**
```
File "mesohops/trajectory/hops_trajectory.py", line 440, in propagate
    raise TrajectoryError(
TrajectoryError: Timesteps(1.0) that do not match noise.param['TAU'] (2.0)
not supported in current implementation of HOPSTrajectory.
```

**Root cause:**
The Runge-Kutta integrator uses `integrator_step = 0.5`, so the internal sub-step
passed to `_check_tau_step` is `tau * integrator_step = dt_save * 0.5`.
MesoHOPS requires `TAU` to divide this sub-step evenly
(`tau_step / TAU` must be an integer).

With `dt_save = 2.0 fs` (from `parameters.yaml`) and `TAU = dt_save = 2.0`:
- `tau_step = 2.0 * 0.5 = 1.0`
- `tau_step / TAU = 1.0 / 2.0 = 0.5` → not an integer → error.

**Before:**
```python
noise_param = {
    "SEED": kwargs.get("seed", 42),
    "MODEL": "FFT_FILTER",
    "TLEN": t_max + 50.0,
    "TAU": dt_save,
}
```

**After:**
```python
noise_param = {
    "SEED": kwargs.get("seed", 42),
    "MODEL": "FFT_FILTER",
    "TLEN": t_max + 50.0,
    # TAU must equal tau * integrator_step (RK uses integrator_step=0.5).
    # propagate(t_max, dt_save) passes tau=dt_save, so the internal
    # sub-step is dt_save * 0.5. TAU must divide that sub-step evenly.
    "TAU": dt_save * 0.5,
}
```

With `TAU = dt_save * 0.5 = 1.0`: `tau_step / TAU = 1.0 / 1.0 = 1` ✓.
The noise grid is sampled at the RK sub-step resolution, which is the minimum
required by MesoHOPS's `FFT_FILTER` noise model.
