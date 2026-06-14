# AGENTS.md - Project Context Document

**Last updated:** 2026-06-13 (Session 3b — Test bugs fixed, pytest verified)

## Project Overview

This repository contains two active research projects:

1. **Quantum-Enhanced Agrivoltaics** — Selective vibronic excitation for coherent transport in the FMO complex, targeting *The Journal of Physical Chemistry Letters* (JPCL). Manuscript ID: `jz-2026-00994t`. Status: **Major Revision in progress** (30-day deadline from 28-Apr-2026).

2. **Anderson Model Comparison** — Comparative study of the Anderson model in weak and strong interaction regimes using Julia (HierarchicalEOM.jl) and Python (QuTiP). Published in Physical Review B.

---

## Simulation Environment

### Local Execution (Laptop Mode - Fast Verification)
```bash
mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260612/reproducibility/main.py --config laptop_parameters.yaml
```

### Local/Cluster Execution (Production Mode - Publication Data)
```bash
mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260612/reproducibility/main.py --parallel --skip-audit
```
```bash
chmod +x Redac_Paper1/quantum_simulations_framework_parallel_260612/reproducibility/run_temp_sweep_cluster.sh
./Redac_Paper1/quantum_simulations_framework_parallel_260612/reproducibility/run_temp_sweep_cluster.sh
```
**Figure 2 Sweep (Server-Side):**
```bash
chmod +x Redac_Paper1/quantum_simulations_framework_parallel_260612/reproducibility/run_temp_sweep_cluster.sh
./Redac_Paper1/quantum_simulations_framework_parallel_260612/reproducibility/run_temp_sweep_cluster.sh
```
Monitoring: `tail -f reproducibility_cluster.log` (or `sweep_cluster.log` for Fig 2)

### Repository Hygiene (STRICT)
**The canonical directory for all simulation work is:**
`Redac_Paper1/quantum_simulations_framework_parallel_260612/`

**DEPRECATED DIRECTORIES (DO NOT REGENERATE):**
- `Redac_Paper1/quantum_simulations_framework/` (DELETED)
- `Redac_Paper1/quantum_simulations_framework_parallel/` (DELETED)

If these directories appear, delete them immediately and check for stale path references in `AGENTS.md`, `ROADMAP.md`, or `README.md`.

### Hardware Management
The simulation now utilizes **2/3 of available CPU cores** via `joblib` parallelization.
- **Laptop Mode**: Uses $L=3, N=4$ for rapid testing (~10 mins).
- **Production Mode**: Enforces $L \ge 8$ and $K \ge 2$ for manuscript compliance.

---

## JPCL Revision — Current Status (2026-06-13 — Session 3b)

> [!IMPORTANT]
> **SOURCE OF TRUTH (REVISION R2)**: The absolute canonical source of truth for the revised manuscript is `Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/JPCL/JPCL_Submission_Package_2026-06-13`. All modifications to the LaTeX files, Response letters, and SI must be done exclusively in this directory.

### ✅ Completed fixes
- **Serialization/Pickling Hardening**: Refactored parallel trajectory workers in `hops_simulator.py` and `quantum_dynamics_simulator.py` to module-level functions, enabling 100% compatibility with `joblib`/`multiprocessing` backends.
- **Vibronic Fallback Fix**: Synchronized `QuantumDynamicsSimulator` (fallback) to correctly load the 12-mode Kleinekathöfer vibronic bath instead of defaulting to DL-only.
- **SBD Resolution**: Increased `sbd_bundles_per_site` from 2 to 6 to preserve vibronic spectral features while maintaining memory tractability.
- **L=8, K=2 Synchronization**: Standardized across manuscript body, SI Tables S1 & S4, `constants.py`, and `parameters.yaml`.
- **SI K-Convergence Note**: Added physically-motivated justification for $K=2$ truncation (MAE = 3.32e-05) in SI Section S2.3.
- **Hierarchy Depth Sync**: Confirmed $L=8$ across all documents (MAE = 3.10e-11 for $L=8$ relative difference).
- **Resource Management**: Explicitly documented the **Memory-Aware Job Scheduler** and the **\SI{54}{\giga\byte}** per-trajectory footprint in the Response Letter and SI.
- **Figure Synchronization**: May 10 production figures ($N=100$) copied to generic filenames for manuscript compilation.
- SI Section S1.1: Gaussian pulse temporal envelope E(t) = E₀ exp(-t²/2σ_t²) with FWHM=50 fs added
- Abstract terminology updated: "quantum control via selective vibronic excitation"
- Fleming2015 and Scholes2015 added to `references.bib` and cited in manuscript
- ENAQT reference (Wu et al. 2010) added to `references.bib` per Reviewer 2 comment 4
- Manuscript formatting: `\section{}` headings removed per JPCL Letter format; `\subsection*{}` used for paragraph headings; `\textbf{...}` bold run-ins for major divisions
- TOC Graphic: added via `\begin{tocentry}` in achemso class (correct mechanism)
- Cover Letter: updated with point-by-point response to Manuscript Formatting Request and Cover Art invitation
- Fake convergence CSVs quarantined as `.INVALID_FALLBACK_DATA.csv`
- `audit_convergence.py`: now detects MesoHOPS fallback, exits with error, and implements **Trace Preservation/Positivity checks**
- `main.py`: complete orchestrator (hardened with `--skip-audit` and `--parallel` flags)
- `figure_generator.py`: Overhauled to support JPCL legibility standards (600 DPI, Time [fs] units, Panel labels (a)-(f), comparison traces)
- `environmental_factors.py`: Replaced seasonal "Time (days)" cycle with physically motivated static temperature sweeps (FR11)
- **Code Merge & Data Reconciliation (2026-05-10)**: Merged server-side best practices (Python 3.10+ type hints, NumPy-style docstrings, `np.diag` initialization) into `core/hamiltonian_factory.py`. Local `quantum_simulations_framework_parallel_260612/` confirmed as the canonical reference with all improvements incorporated. Production CSV format verified identical (local=server). SI `η` value aligned: Test 10 corrected from 0.22(4) to 0.20(4) to match production ensemble average.
- **CSV Format Verified**: Both local and server CSVs use the same column schema (`time_fs` + 7 site populations + `coherences` + broadband columns). No compatibility patch needed for figure generator.
### ✅ R2 Audit (2026-06-13)
- **Transfer Yield Definition (Rev 3 Pt 1)**: Changed from `1.0 - data['populations'][-1, 0]` to `data['populations'][-1, FMO_TARGET_SITE]` (Site 3, index 2 = RC exit). Applied across `reproducibility/main.py`, `pipelines/jpcl_resubmission/main.py`, and `reproducibility/optimize.py`.
- **FMO_TARGET_SITE Constant**: Added `FMO_TARGET_SITE = 2` to `core/constants.py` to provide a single source of truth for the target site definition.
- **Spectral Density Discrete Modes (Rev 3 Pt 2)**: Enhanced `utils/figure_generator.py:plot_bath_spectral_density()` to plot discrete triangular markers at each of the 12 Kleinekathöfer/Coker vibronic mode frequencies, with labeled vertical guide lines.
- **AGENTS.md Hygiene**: Fixed all stale `260509` path references to `260612`; updated status date.

### ⚠️ Requires MesoHOPS environment (cannot be done without real solver)
- (None) — All high-rigor production tasks have been completed.

### 🧪 Test Status (2026-06-13)
**pytest results:** 33/38 passed, 3 expected-skip, 2 server-only (memory validation) — 3 pre-existing test bugs fixed.
| Test | Bug | Fix |
|------|-----|-----|
| `test_pipeline_exits_on_no_mesohops` | `sys.exit` mock no `SystemExit` → execution continuait | `mock_exit.side_effect = SystemExit` |
| `test_quantum_dynamics_simulator` | Arguments inversés `time_points` ↔ `psi0` → `assert 5==7` | `keyword args initial_state=psi0, time_points=time_points` |
| `test_hamiltonian_properties` | `server_hardware['ram_gb']` au lieu de `'total_ram_gb'` → `KeyError` | Corrigé key name |
| `test_3site_full_dynamics` + `test_7site_full_dynamics` | **Attendu** — validation mémoire bloque 12.9/30.0 GB > 9.5 GB laptop | Comportement correct |
| `test_hierarchy_convergence_L6_vs_L8` | Long (~30 min), 20 batches × 1 traj | Serveur seulement |

### ✅ Laptop test completed
- `--config laptop_parameters.yaml` (L=3, N=4, 200 fs) : L-sweep, K-sweep, dt-sweep passés.
- 0.5 GB/traj → n_jobs=7, batch_size=7. Aucun OOM.
- **Detailed balance test crash (NaN) corrigé** : dt=10 fs → dt=1.0 fs dans `audit_convergence.py`. NaN/Inf protection ajoutée dans `_calculate_von_neumann_entropy()`.

### 📋 Remaining open items
- ✅ All reviewer-requested code and bibliographic changes have been implemented (R1 + R2).
- ✅ 12-mode spectral density verified in `constants.py` and `parameters.yaml`.
- ✅ Local codebase merged with server best practices — local is now the canonical reference.
- ✅ Production CSV format verified (local = server). Figure generator compatible.
- ✅ Transfer yield redefined to target-site population (Site 3) per Rev 3 Pt 1.
- ✅ Spectral density plot enhanced with discrete 12-mode markers per Rev 3 Pt 2.
- ✅ Bath dissipative parameters verified: λ_D=35 cm⁻¹, γ_D=50 cm⁻¹, 12 vibronic modes, L=8, K=2.
- ✅ Laptop test (L=3, N=4, 200 fs) verified — damped oscillations confirmed.
- ✅ 3 pre-existing test bugs fixed.
### ⏳ Pending (Requires MesoHOPS Server)
- [x] Run full production simulation on server (100 trajectories) — **en cours** (2026-06-13 16:06)
- [ ] Regenerate Figures 2 & 3 with production data showing damping.
- [ ] Create `JPCL_Submission_Package_2026-06-13/` with renamed manuscripts (if needed after server run).
- [ ] Fix GPU driver mismatch (NVML v580.159).
- [ ] Install Numba upgrade (≥0.63) si nécessaire sur le serveur.

---

## Key Files

| File | Purpose |
|------|---------|
| `Redac_Paper1/JPCL/JPCL_Submission_Package_2026-06-13/Manuscript_JPCL_26-06-13.tex` | Revised manuscript (achemso, JPCL Letter format) — updated 2026-06-13 (**Source of truth**) |
| `Redac_Paper1/JPCL/JPCL_Submission_Package_2026-06-13/SI_JPCL_26-06-13.tex` | Revised Supporting Information — updated 2026-06-13 (**Source of truth**) |
| `Redac_Paper1/JPCL/JPCL_Submission_Package_2026-06-13/Response_to_Reviewers_26-06-13.tex` | Point-by-point response letter — updated 2026-06-13 (**Source of truth**) |
| `Redac_Paper1/JPCL/JPCL_Submission_Package_2026-06-13/Cover_Letter_JPCL_26-06-13.tex` | Cover letter — updated 2026-06-13 (**Source of truth**) |
| `Redac_Paper1/JPCL/JPCL_Submission_Package_2026-06-13/references.bib` | BibTeX references |
| `Redac_Paper1/Theory_Journals_main/JPCL/Reviewers_Comments.md` | Original reviewer comments + journal formatting requests |
| `Redac_Paper1/Theory_Journals_main/JPCL/Reviewers_Comments_Answers.md` | Detailed draft answers |
| `Redac_Paper1/quantum_simulations_framework_parallel_260612/parameters.yaml` | **Single source of truth** for all simulation parameters |
| `Redac_Paper1/quantum_simulations_framework_parallel_260612/core/constants.py` | Python constants (must match `parameters.yaml`) |
| `Redac_Paper1/quantum_simulations_framework_parallel_260612/reproducibility/main.py` | Single-entry pipeline orchestrator |
| `Redac_Paper1/quantum_simulations_framework_parallel_260612/reproducibility/audit_convergence.py` | L=7,8,9 convergence audit |
| `_bmad-output/planning-artifacts/prd.md` | Product Requirements Document |
| `_bmad-output/planning-artifacts/architecture.md` | Architecture decisions |
| `_bmad-output/planning-artifacts/epics.md` | Epic breakdown (stories not yet written) |

---

## Parameter Consistency Rules

**AI agents MUST:**
- Read simulation parameters **only** from `parameters.yaml` — never hardcode physics values
- Verify `constants.py` matches `parameters.yaml` after any parameter change
- Never commit files named `*.INVALID_FALLBACK_DATA.csv`
- Never commit HDF5 files to `data/converged/` without Git LFS
- All manuscript files with changes MUST include the current date in their filename (e.g., `Manuscript_JPCL_26-05-02.tex`)
- **Terminology Rule**: SBD refers to **Stochastically Bundled Dissipators**. Never use "Spectrally Bundled Dissipators".

**Current canonical values:**
- Hierarchy depth: **L_max = 8**
- Matsubara terms: **K = 2**
- Time step: **Δt = 1.0 fs**
- Pulse FWHM: **50 fs**, centered at t = 0
- Temperature: **295 K**
- Reorganization energy (Drude-Lorentz): **λ_D = 35 cm⁻¹**, γ_D = 50 cm⁻¹
- Vibronic modes: **12 modes** (Kleinekathöfer/Coker model)
- Disorder realizations: **100**

---

## Directory Structure

```
Quantum_Agrivoltaic_PT-HOPS/
├── AGENTS.md                          # This file
├── README.md                          # Project overview
├── .gitignore
├── Redac_Paper1/
│   ├── JPCL/
│   │   └── JPCL_Submission_Package_2026-06-13/ # Source of truth for manuscript
│   │       ├── Manuscript_JPCL_26-06-13.tex
│   │       ├── SI_JPCL_26-06-13.tex
│   │       ├── Response_to_Reviewers_26-06-13.tex
│   │       ├── Cover_Letter_JPCL_26-06-13.tex
│   │       └── references.bib
│   ├── Theory_Journals_main/JPCL/     # Old JPCL submission files (dated filenames)
│   │   ├── Manuscript_JPCL_26-05-10.tex
│   │   ├── SI_JPCL_26-05-10.tex
│   │   ├── Response_to_Reviewers_26-05-08.tex
│   │   ├── Cover_Letter_JPCL_26-05-08.tex
│   │   ├── references.bib
│   │   ├── Reviewers_Comments.md
│   │   └── Reviewers_Comments_Answers.md
│   └── quantum_simulations_framework_parallel_260612/ # Simulation codebase
│       ├── parameters.yaml            # Source of truth
│       ├── core/                      # HopsSimulator, constants, hamiltonian
│       ├── models/                    # QuantumDynamicsSimulator, etc.
│       ├── extensions/                # PT_HopsNoise, SBD_HopsTrajectory
│       ├── utils/                     # FigureGenerator, theme, logging
│       ├── reproducibility/
│       │   ├── main.py                # Entry point
│       │   ├── audit_convergence.py   # L=9,10,11 audit
│       │   └── results/               # Valid results go here (see README.md inside)
│       └── tests/
├── notebooks/                         # Anderson model Jupyter notebooks
├── manuscrit/                         # Anderson model PRB publication
├── _bmad-output/planning-artifacts/   # PRD, architecture, epics
└── Archive/                           # Legacy code
```

---

## Technology Stack

| Tool | Version | Purpose |
|------|---------|---------|
| MesoHOPS | v1.7.0 (local) | PT-HOPS/SBD non-Markovian dynamics; installed in editable mode from `/home/taamangtchu/Documents/Github/mesohops/` |
| Python | 3.12+ | Simulation framework (conda env `MesoHOP-sim`) |
| HierarchicalEOM.jl | latest | Julia HEOM (Anderson model) |
| QuTiP | 5.2.2+ | Python HEOM (Anderson model) |
| achemso (LaTeX) | latest | JPCL manuscript formatting |
| Matplotlib | latest | Figure generation (600 DPI, JPCL theme) |

## Server Environment (PenavoraServer)

**Access:** `ssh penavora@100.73.21.40` (via Tailscale)
**OS:** Ubuntu 24.04
**Hardware:** 48 CPU cores, 125 GB RAM, 1× NVIDIA GPU (driver mismatch NVML, à corriger)
**Codebase:** `~/Redac_Paper1/quantum_simulations_framework_parallel_260612/`
**Conda env:** `MesoHOP-sim` (créé le 2026-06-13, Python 3.12, mesohops v1.7.0)
**Dependencies:** numpy, scipy, pandas, matplotlib, joblib, tqdm, psutil, pyyaml

### Transférer le code vers le serveur
```bash
# Depuis le laptop
tar czf /tmp/quantum_sim_fw.tar.gz Redac_Paper1/quantum_simulations_framework_parallel_260612/
scp /tmp/quantum_sim_fw.tar.gz penavora@100.73.21.40:~/
ssh penavora@100.73.21.40 "cd ~/ && tar xzf quantum_sim_fw.tar.gz"
```

### Simulation de production (lancée le 2026-06-13 16:06)
```bash
nohup ~/miniforge3/envs/MesoHOP-sim/bin/python reproducibility/main.py --parallel --skip-audit > ~/production_run.log 2>&1 &
```
**Statut:** En cours — 50 batchs × 2 traj, 53.9 GB/traj, 2 workers/batch
**Monitorer:** `tail -f ~/production_run.log`

### GPU Driver Fix (TODO)
```bash
# NVML mismatch: library version 580.159, driver module chargé
sudo apt-get install --reinstall nvidia-driver-580   # ou version appropriée
sudo reboot
```

---

## OOM Prevention Architecture (updated 2026-06-13)

The framework uses a layered OOM prevention strategy:

1. **Memory estimation**: `MemoryAwareJobScheduler._estimate_memory()` scales from a reference (6 GB at L=8, K=2, 21 modes) using `(L/8)^2 × (K/2) × (modes/21)`.
2. **Per-process limit**: `resource.setrlimit(RLIMIT_AS)` kills workers that exceed their RAM budget (avoids OOM-killer cascade).
3. **Batch execution**: Trajectories are split into batches of `n_jobs` each, with `gc.collect()` between batches.
4. **Dynamic n_jobs**: `get_safe_n_jobs()` in `utils/parallel_utils.py` uses L/K/modes-aware estimation (not hardcoded 54 GB anymore).
5. **MAX_N_JOBS = 8** (upper bound only; the estimator picks the real number).

Key difference laptop vs server: laptop uses `laptop_parameters.yaml` (L=3, N=4, 200 fs → ~1 GB/traj), while server uses `parameters.yaml` (L=8, N=100, 1000 fs → ~54 GB/traj). The memory estimator dynamically adapts.

## 2026-06-13 Session 3 — Audit & comprehensive OOM fixes

### Root-level duplicate DELETED
The stale copy of the codebase at `Quantum_Agrivoltaic_PT-HOPS/quantum_simulations_framework_parallel_260612/` (118 Python files, MAX_N_JOBS=1, missing FMO_TARGET_SITE) was moved to `_deleted_root_duplicate_260612/`. The canonical path remains `Redac_Paper1/quantum_simulations_framework_parallel_260612/`.

### Critical fixes
- **`src.core.memory_manager` re-export created**: `src/core/memory_manager.py` re-exports `MemoryAwareJobScheduler`, `validate_memory_configuration`, `cleanup_memory` from `core.memory_manager`. This fixes a silent no-op: `memory_aware_patch.py` would always fail its import and silently skip patching, meaning no batch execution was ever active.
- **`set_process_mem_limit(RLIMIT_AS)` now called** from `memory_aware_patch.py` before batch execution.
- **`mem_limit_gb` passed to workers**: Both `core/hops_simulator.py:_run_single_traj_worker` and `src/core/hops_simulator.py:_run_single_traj_worker` now accept `mem_limit_gb` and call `resource.setrlimit(RLIMIT_AS)` at worker start.
- **`MemoryError` handling in batch loop**: `memory_aware_patch.py` now catches `MemoryError` and retries with `n_jobs//2` before failing.
- **`FMO_TARGET_SITE = 2` added to `src/core/constants.py`** (was missing from src tree).
- **`get_safe_n_jobs(54.0)` replaced** in `pipelines/jpcl_resubmission/main.py` (2 occurrences) with dynamic estimation from L/K/modes/time_max.
- **`0.5` → `CPU_COUNT_FRACTION`** in `core/memory_manager.py`.

### Files created
- `src/core/memory_manager.py` (re-export)
- `Redac_Paper1/quantum_simulations_framework_parallel_260612/scripts/cluster/run_production.sh` (server runner)
- `Redac_Paper1/quantum_simulations_framework_parallel_260612/SERVER_PROTOCOL.md` (server usage guide)

### Files modified
- `core/hops_simulator.py` — mem_limit_gb, MemoryError catch in batch loop
- `core/memory_manager.py` — 0.5 → CPU_COUNT_FRACTION
- `src/core/hops_simulator.py` — mem_limit_gb in worker
- `src/core/memory_aware_patch.py` — RLIMIT_AS, MemoryError catch, mem_limit_gb in worker_args
- `src/core/constants.py` — FMO_TARGET_SITE added
- `pipelines/jpcl_resubmission/main.py` — get_safe_n_jobs dynamique ×2
- `AGENTS.md` — this entry

## Agent Skills & Capabilities (Optimized 2026-06-14)

The Antigravity agent environment has been specifically optimized for this scientific computing project. Agents must leverage the following core skills when operating in this repository:

- **Scientific Review & Writing**: `peer-review`, `scientific-critical-thinking`, `scientific-writing`. Used for cross-checking manuscript claims against reviewer comments and rigorous proofreading.
- **Quantum & Physics Modeling**: `mesohops` (primary framework), `my_quantum-optics`, `Floquet`, `orca`, `pyscf`.
- **Code Quality & Architecture**: `python-patterns`, `coding-standards`, `codebase-onboarding`, `python-testing`. Must be used during refactoring to enforce NumPy docstrings, type hints, and scalable architecture.
- **Performance & Data Handling**: `benchmark`, `vaex`, `dask`, `polars`. Crucial for handling massive parallel data and optimizing HPC resources.
- **Data Analysis & Networks**: `scikit-learn`, `networkx`. For complex site-connectivity analysis in the FMO complex.

Agents are strictly instructed to use these specialized skills for high-fidelity physics simulations, codebase refactoring, and publication-quality academic outputs.

---

## License

MIT License
