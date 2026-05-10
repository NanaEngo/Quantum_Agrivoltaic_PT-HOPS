# AGENTS.md - Project Context Document

**Last updated:** 2026-05-10

## Project Overview

This repository contains two active research projects:

1. **Quantum-Enhanced Agrivoltaics** — Spectral bath engineering via non-Markovian dynamics in the FMO complex, targeting *The Journal of Physical Chemistry Letters* (JPCL). Manuscript ID: `jz-2026-00994t`. Status: **Major Revision in progress** (30-day deadline from 28-Apr-2026).

2. **Anderson Model Comparison** — Comparative study of the Anderson model in weak and strong interaction regimes using Julia (HierarchicalEOM.jl) and Python (QuTiP). Published in Physical Review B.

---

## Simulation Environment

### Local Execution (Laptop Mode - Fast Verification)
```bash
mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main.py --config laptop_parameters.yaml
```

### Local/Cluster Execution (Production Mode - Publication Data)
```bash
mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main.py --parallel --skip-audit
```
```bash
chmod +x run_cluster.sh
./run_cluster.sh
```
Monitoring: `tail -f reproducibility_cluster.log`

### Hardware Management
The simulation now utilizes **2/3 of available CPU cores** via `joblib` parallelization.
- **Laptop Mode**: Uses $L=3, N=4$ for rapid testing (~10 mins).
- **Production Mode**: Enforces $L \ge 8$ and $K \ge 2$ for manuscript compliance.

---

## JPCL Revision — Current Status (2026-05-10)

### ✅ Completed fixes
- **Serialization/Pickling Hardening**: Refactored parallel trajectory workers in `hops_simulator.py` and `quantum_dynamics_simulator.py` to module-level functions, enabling 100% compatibility with `joblib`/`multiprocessing` backends.
- **Vibronic Fallback Fix**: Synchronized `QuantumDynamicsSimulator` (fallback) to correctly load the 12-mode Kleinekathöfer vibronic bath instead of defaulting to DL-only.
- **SBD Resolution**: Increased `sbd_bundles_per_site` from 2 to 6 to preserve vibronic spectral features while maintaining memory tractability.
- **L=8, K=2 Synchronization**: Standardized across manuscript body, SI Tables S1 & S4, `constants.py`, and `parameters.yaml`.
- **SI K-Convergence Note**: Added physically-motivated justification for $K=2$ truncation (MAE = 3.42e-05) in SI Section S2.3.
- SI Test 3 time step: 0.1 fs → 2.0 fs (consistent with `parameters.yaml`)
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
- **Production Ensemble**: Successfully executed the $L=8, K=2$ production ensemble via `main.py` (verified via 100-trajectory results in `reproducibility/results/`).
- **Publication Figures**: Generated final `Quantum_dynamics.png` and `ETR_Under_Environmental_Effects.pdf` using the overhauled `FigureGenerator`.
- **FMO Schematic**: Created the promised FMO structural schematic (`FMO_Schematic_JPCL.png`).

### ⚠️ Requires MesoHOPS environment (cannot be done without real solver)
- (None) — All high-rigor production tasks have been completed.

### 📋 Remaining open items
- (None) — All reviewer-requested code and bibliographic changes have been implemented. 12-mode spectral density verified in `constants.py` and `parameters.yaml`.

---

## Key Files

| File | Purpose |
|------|---------|
| `Redac_Paper1/Theory_Journals_main/JPCL/Manuscript_JPCL_26-05-08.tex` | Revised manuscript (achemso, JPCL Letter format) |
| `Redac_Paper1/Theory_Journals_main/JPCL/SI_JPCL_26-05-08.tex` | Revised Supporting Information |
| `Redac_Paper1/Theory_Journals_main/JPCL/Response_to_Reviewers_26-05-08.tex` | Point-by-point response letter |
| `Redac_Paper1/Theory_Journals_main/JPCL/Cover_Letter_JPCL_26-05-08.tex` | Cover letter (includes formatting response + cover art) |
| `Redac_Paper1/Theory_Journals_main/JPCL/references.bib` | BibTeX references |
| `Redac_Paper1/Theory_Journals_main/JPCL/Reviewers_Comments.md` | Original reviewer comments + journal formatting requests |
| `Redac_Paper1/Theory_Journals_main/JPCL/Reviewers_Comments_Answers.md` | Detailed draft answers |
| `Redac_Paper1/quantum_simulations_framework_parallel/parameters.yaml` | **Single source of truth** for all simulation parameters |
| `Redac_Paper1/quantum_simulations_framework_parallel/core/constants.py` | Python constants (must match `parameters.yaml`) |
| `Redac_Paper1/quantum_simulations_framework_parallel/reproducibility/main.py` | Single-entry pipeline orchestrator |
| `Redac_Paper1/quantum_simulations_framework_parallel/reproducibility/audit_convergence.py` | L=7,8,9 convergence audit |
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
│   ├── Theory_Journals_main/JPCL/     # All JPCL submission files (dated filenames)
│   │   ├── Manuscript_JPCL_26-05-08.tex
│   │   ├── SI_JPCL_26-05-08.tex
│   │   ├── Response_to_Reviewers_26-05-08.tex
│   │   ├── Cover_Letter_JPCL_26-05-08.tex
│   │   ├── references.bib
│   │   ├── Reviewers_Comments.md
│   │   └── Reviewers_Comments_Answers.md
│   └── quantum_simulations_framework_parallel/ # Simulation codebase
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
| MesoHOPS | v1.6 | PT-HOPS/SBD non-Markovian dynamics |
| Python | 3.10+ | Simulation framework |
| HierarchicalEOM.jl | latest | Julia HEOM (Anderson model) |
| QuTiP | 5.2.2+ | Python HEOM (Anderson model) |
| achemso (LaTeX) | latest | JPCL manuscript formatting |
| Matplotlib | latest | Figure generation (600 DPI, JPCL theme) |

## License

MIT License
