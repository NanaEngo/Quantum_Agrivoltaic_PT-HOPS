# AGENTS.md - Project Context Document

**Last updated:** 2026-05-02

## Project Overview

This repository contains two active research projects:

1. **Quantum-Enhanced Agrivoltaics** — Spectral bath engineering via non-Markovian dynamics in the FMO complex, targeting *The Journal of Physical Chemistry Letters* (JPCL). Manuscript ID: `jz-2026-00994t`. Status: **Major Revision in progress** (30-day deadline from 28-Apr-2026).

2. **Anderson Model Comparison** — Comparative study of the Anderson model in weak and strong interaction regimes using Julia (HierarchicalEOM.jl) and Python (QuTiP). Published in Physical Review B.

---

## Simulation Environment

All quantum dynamics simulations MUST be run using the MesoHOPS environment:

```bash
mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework/reproducibility/main.py
```

Any execution bypassing this wrapper may produce inconsistent results. The `main.py` orchestrator validates `parameters.yaml` (enforces L≥10, K≥10), checks MesoHOPS availability, runs the convergence audit, and generates figures.

---

## JPCL Revision — Current Status (2026-05-02)

### ✅ Completed fixes
- L=10, K=10 synchronized across: manuscript body, SI Tables S1 & S10, `constants.py`, `parameters.yaml`
- SI Test 3 time step: 0.1 fs → 0.5 fs (consistent with `parameters.yaml`)
- SI Section S1.1: Gaussian pulse temporal envelope E(t) = E₀ exp(-t²/2σ_t²) with FWHM=50 fs added
- Abstract terminology updated: "quantum control via selective vibronic excitation"
- Fleming2015 and Scholes2015 added to `references.bib` and cited in manuscript
- ENAQT reference (Wu et al. 2010) added to `references.bib` per Reviewer 2 comment 4
- Manuscript formatting: `\section{}` headings removed per JPCL Letter format; `\subsection*{}` used for paragraph headings; `\textbf{...}` bold run-ins for major divisions
- TOC Graphic: added via `\begin{tocentry}` in achemso class (correct mechanism)
- Cover Letter: updated with point-by-point response to Manuscript Formatting Request and Cover Art invitation
- Fake convergence CSVs quarantined as `.INVALID_FALLBACK_DATA.csv`
- `audit_convergence.py`: now detects MesoHOPS fallback, exits with error, and implements **Trace Preservation/Positivity checks**
- `main.py`: complete orchestrator (was a stub)
- `figure_generator.py`: Overhauled to support JPCL legibility standards (600 DPI, Time [fs] units, Panel labels (a)-(f), comparison traces)
- `environmental_factors.py`: Replaced seasonal "Time (days)" cycle with physically motivated static temperature sweeps (FR11)

### ⚠️ Requires MesoHOPS environment (cannot be done without real solver)
- Run actual L=10, K=10 simulations via `main.py` to generate valid convergence data
- Use the overhauled `FigureGenerator` to output final `Quantum_dynamics.png` and `ETR_Under_Environmental_Effects.pdf`
- Create FMO schematic figure (promised in response letter)

### 📋 Remaining open items
- (None) — All reviewer-requested code and bibliographic changes have been implemented. 12-mode spectral density verified in `constants.py` and `parameters.yaml`.

---

## Key Files

| File | Purpose |
|------|---------|
| `Redac_Paper1/Theory_Journals/JPCL/Manuscript_JPCL_26-05-02.tex` | Revised manuscript (achemso, JPCL Letter format) |
| `Redac_Paper1/Theory_Journals/JPCL/SI_JPCL_26-05-02.tex` | Revised Supporting Information |
| `Redac_Paper1/Theory_Journals/JPCL/Response_to_Reviewers_26-05-02.tex` | Point-by-point response letter |
| `Redac_Paper1/Theory_Journals/JPCL/Cover_Letter_JPCL_26-05-02.tex` | Cover letter (includes formatting response + cover art) |
| `Redac_Paper1/Theory_Journals/JPCL/references.bib` | BibTeX references |
| `Redac_Paper1/Theory_Journals/JPCL/Reviewers_Comments.md` | Original reviewer comments + journal formatting requests |
| `Redac_Paper1/Theory_Journals/JPCL/Reviewers_Comments_Answers.md` | Detailed draft answers |
| `Redac_Paper1/quantum_simulations_framework/parameters.yaml` | **Single source of truth** for all simulation parameters |
| `Redac_Paper1/quantum_simulations_framework/core/constants.py` | Python constants (must match `parameters.yaml`) |
| `Redac_Paper1/quantum_simulations_framework/reproducibility/main.py` | Single-entry pipeline orchestrator |
| `Redac_Paper1/quantum_simulations_framework/reproducibility/audit_convergence.py` | L=9,10,11 convergence audit |
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
- Hierarchy depth: **L = 10**
- Matsubara terms: **K = 10**
- Time step: **Δt = 0.5 fs**
- Pulse FWHM: **50 fs**, centered at t = 0
- Temperature: **295 K**
- Reorganization energy (Drude-Lorentz): **λ_D = 35 cm⁻¹**, γ_D = 50 cm⁻¹
- Vibronic modes: **12 modes** (Kleinekathöfer/Coker model)

---

## Directory Structure

```
Quantum_Agrivoltaic_PT-HOPS/
├── AGENTS.md                          # This file
├── README.md                          # Project overview
├── .gitignore
├── Redac_Paper1/
│   ├── Theory_Journals/JPCL/          # All JPCL submission files (dated filenames)
│   │   ├── Manuscript_JPCL_26-05-02.tex
│   │   ├── SI_JPCL_26-05-02.tex
│   │   ├── Response_to_Reviewers_26-05-02.tex
│   │   ├── Cover_Letter_JPCL_26-05-02.tex
│   │   ├── references.bib
│   │   ├── Reviewers_Comments.md
│   │   └── Reviewers_Comments_Answers.md
│   └── quantum_simulations_framework/ # Simulation codebase
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
