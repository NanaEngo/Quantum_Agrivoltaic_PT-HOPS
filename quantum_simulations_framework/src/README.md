# Simulation Framework Architecture (`src/`)

Modular source code for the canonical Paper-1 (JPCL) PT-HOPS/SBD framework: non-Markovian
exciton dynamics with stochastic trajectories, memory-aware parallelism, and the agrivoltaic
coupling models that sit downstream of the quantum layer.

**Last updated:** 2026-11-14 · **Version:** `quantum_simulations_framework/parameters.yaml`
(`version: 1.0.0`) · **Status:** canonical framework for Paper 1; Paper 2 carries its own
self-contained evidence base in `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/`.

---

## Directory map

### 1. `core/` — numerical foundations
- **`hops_simulator.py`** — PT-HOPS/SBD trajectory generation (module-level workers so
  `joblib`/`multiprocessing` can pickle them).
- **`hamiltonian_factory.py`** — exciton–vibronic Hamiltonian construction.
- **`memory_manager.py`** — `MemoryAwareJobScheduler`: per-worker `RLIMIT_AS`, batching, `gc` between
  batches.
- **`constants.py`** — physical constants, unit conversions, canonical production values.

### 2. `quantum/` — dynamics and spectroscopy
- **`analysis.py`** — population kinetics, coherence metrics, energy-transfer efficiency.
- **`spectroscopy.py`** — linear absorption and 2D electronic spectroscopy signals.
- **`spectral_optimization.py`** — bath spectral-density engineering.
- **`quantum_dynamics_simulator.py`** — fallback propagator when MesoHOPS is unavailable
  (loads the 12-mode vibronic bath, not DL-only).

### 3. `agrivoltaic/` — downstream models
`coupling_model.py`, `environmental_factors.py`, `lca_analyzer.py`,
`techno_economic_model.py`, `eco_design_analyzer.py`, `biodegradability_analyzer.py`.

### 4. `extensions/` — solver enhancements
- **`stochastic_bundling.py`** — Stochastically Bundled Dissipators (SBD). *SBD never means
  "spectrally bundled dissipators".*
- **`mesohops_adapters.py`** — version-agnostic adapters (production pinned to MesoHOPS 1.7.0;
  1.8.0 exists only as an evaluation environment).

### 5. `io/` and `visualization/`
`csv_storage.py` (SHA-256 metadata integrity), `orca_wrapper.py`, `figure_generator.py`
(600 DPI publication theme), `fmo_schematic.py`, `theme.py`.

### 6. `utils/`
`parallel_utils.py` (`estimate_memory_per_traj`, `get_safe_n_jobs`), `gpu_detection.py`
(reports hardware; there is no GPU propagation path in this framework), `logging_config.py`.

---

## Conventions

- **Production configuration:** `L = 8`, `K = 2`, SBD = 3, `Δt = 0.5 fs`, 100 disorder
  realizations, 295 K. Laptop verification mode (`laptop_parameters.yaml`) relaxes to
  `L = 3`, `N = 4`; production runs must not.
- **Parameters** come only from `parameters.yaml`; `core/constants.py` must match it after any change.
- **Code style:** NumPy docstrings, Python 3.12 type hints, `ruff` for lint and format.
  There is no `mypy` gate in this repository.
- **NumPy ≥ 2:** the user-site `~/.local/lib/python3.12/site-packages` shadows the conda env, so
  `np.trapz` is gone — use `np.trapezoid`.
- **Units:** energy in cm⁻¹, time in fs, temperature in K.
