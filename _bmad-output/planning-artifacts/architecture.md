stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
workflowType: 'architecture'
lastStep: 8
status: 'complete'
project_name: 'Quantum_Agrivoltaic_PT-HOPS'
user_name: 'Taamangtchu'
date: '2026-05-08'
completedAt: '2026-05-08'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
The architecture must support an 8-tier functional hierarchy, prioritizing the transition to a mandatory $L=9$ hierarchy depth using the **PT-HOPS/SBD** engine. This requires a decoupled parameter management system (`parameters.yaml`) and a robust convergence audit utility.

**Non-Functional Requirements:**
- **Accuracy**: Trace preservation ($10^{-6}$) and population positivity are non-negotiable.
- **Performance**: Optimization for 128 GB RAM server. K=2 (21 hierarchy modes at L=9) is mandatory — K=10 (77 modes) produces ~10¹¹ hierarchy states and causes OOM on 128 GB. TERMINATOR=True and Triangular STATIC_FILTERS reduce memory by ~50%. Time step synchronized to **2.0 fs**.
- **Reproducibility**: A single entry-point (`main.py`) must orchestrate the entire pipeline.

**Scale & Complexity:**
- Primary domain: Quantum Dynamics Simulation (Non-Markovian)
- Complexity level: Medium-High (Academic Peer-Review standard)
- Estimated architectural components: 5 (Parameter Schema, Solver Wrapper, Audit Utility, Validation Suite, Visualization Pipeline)

### Technical Constraints & Dependencies
- **Solver**: MesoHOPS (Python) with **PT-HOPS** and **SBD** extensions.
- **Environment**: Strict reliance on the `MesoHOP-sim` mamba environment.
- **Hardware**: Local execution only; memory optimization is critical for deep hierarchies (32GB RAM).

### Cross-Cutting Concerns Identified
- **Algorithmic Transparency**: Ensuring the transition from text-described PT-HOPS/SBD to Python code is exact.

## Starter Template & Framework Evaluation

### Primary Technology Domain
**Scientific Research Monorepo (Python-Centric)**. The project requires a structure that supports interactive development (Notebooks) while enforcing production-grade reproducibility for publication.

### Starter Strategy: Custom Reproducible Monorepo
Since this is a brownfield revision, we are adopting a **Hybrid Research Architecture** inspired by best practices in Python scientific computing (`uv`, `Snakemake`-style modularity).

**Selected Frameworks & Orchestration:**
- **Parameter Management**: `parameters.yaml` (YAML 1.2). This serves as the "Source of Truth".
- **Python Environment**: `MesoHOP-sim` (Mamba/Conda).
- **Documentation/Manuscript**: **Quarto** (latest version) for integrating code, data, and LaTeX (`.tex`) into a submission-ready package.
- **Visualization**: `Matplotlib` and `Seaborn`.

### Rationale for Selection
A custom monorepo approach ensures **Reproducibility**. By centralizing parameters in YAML, we eliminate the risk of manual entry errors between the main text, the SI, and the simulation scripts.

### Architectural Decisions Provided by Strategy:

**Language & Runtime:**
- Python 3.10+ (via `MesoHOP-sim`).
- Dedicated `data/converged/` directory for final $L=10$ results.

**Code Organization:**
- `src/pt_hops/`: Core PT-HOPS/SBD solver logic and pulse specifications.
- `parameters.yaml`: Global source of truth.
- `reproducibility/main.py`: The single-entry orchestration script (FR7).
- `reproducibility/optimize.py`: Parameter optimization suite (FR9).

## Core Architectural Decisions

**Decision Priority Analysis**

**Critical Decisions (Block Implementation):**
- **Parameter Synchronization**: `parameters.yaml` (YAML 1.2) is the single source of truth.
- **Methodology**: **PT-HOPS** with **SBD** (Stochastically Bundled Dissipators) for non-Markovian dynamics.
- **Convergence Audit**: **Relative Error Threshold (Frobenius Norm)** compared between $L=7, 8, 9$ (L-audit) AND between $K=1, 2, 3$ at fixed $L=9$ (K-audit). K=2 is the production standard at T=295 K (ν₁ ≈ 1300 cm⁻¹ ≫ γ_D = 50 cm⁻¹).
- **Pulse Specification**: Mandatory support for explicit functional forms and **relative timing/delays** between excitation and probes.
- **Data Interoperability**: Mandated HDF5 (`.h5`) for all simulation outputs.

**Important Decisions (Shape Architecture):**
- **Pulse Specification**: Mandatory support for explicit functional forms (Gaussian/Lorentzian envelopes, phase, time-delays).
- **Figure Generation**: Orchestrated via a `reproducibility/main.py` script that calls Matplotlib using the standardized `theme.py`.
- **Visualization Standard**: Every sub-plot (e.g., Fig 1b) must meet strict **contrast and font-size minimums** to ensure legibility in high-density panels.

### Data Architecture
- **Format**: HDF5 (using `h5py`).
- **Structure**: Hierarchical groups for `/metadata`, `/parameters`, and `/observables/populations`.
- **Validation**: Schema validation on `parameters.yaml` using a lightweight Python validator before simulation start.

### Synchronization & Communication
- **Shared Config**: `parameters.yaml`.

### Infrastructure & Deployment
- **Local Environment**: `mamba run -n MesoHOP-sim`.
- **Versioning**: All `environment.yml` and `requirements.txt` files committed to Git.

### Decision Impact Analysis
**Implementation Sequence:**
1. Initialize `parameters.yaml`.
2. Implement PT-HOPS/SBD solver wrapper in Python.
3. Implement HDF5 data export.
4. Create the `reproducibility/main.py` orchestrator.
## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
- **Parameter Validation**: Ensuring `parameters.yaml` matches the physical constraints (e.g., $L=10$).
- **Data Provenance**: Ensuring every HDF5 file has a reference back to the `parameters.yaml` version used.

### Naming Patterns
- **Python Code**: `snake_case` for functions/variables, `CamelCase` for Classes.
- **YAML Keys**: `snake_case` only.
- **File Names**: `kebab-case.py` (to match repository standard).

### Structure Patterns
- **Tests**: Unified `tests/unit` directory.
- **Outputs**: All $L=9$ results must be saved in `data/converged/` as `.h5` files.
- **Orchestration**: The `reproducibility/` folder contains only top-level scripts that call into `src/`.

### Process Patterns
- **Error Handling**: All solvers must catch numerical instability (e.g., NaN detection) and log it to `logs/instability.log`.
- **Validation Timing**: Convergence audits must be run *after* every production run.

### Enforcement Guidelines
**All AI Agents MUST:**
- Read parameters *only* from the centralized `parameters.yaml` (no hardcoding).
- Verify HDF5 file existence before attempting to plot.
## Project Structure & Boundaries

### Complete Project Directory Structure

```text
Quantum_Agrivoltaic_PT-HOPS/
├── parameters.yaml              # Global Config (YAML 1.2)
├── reproducibility/             # Orchestration Layer
│   ├── main.py                  # Entry Point (FR7)
│   ├── optimize.py              # Parameter sweep/optimization logic (FR9)
│   ├── audit_convergence.py     # L=10 Sufficiency Logic (NFR2)
│   └── logger.py                # Instability & NaN tracking
├── src/
│   ├── pt_hops/                 # PT-HOPS/SBD Implementation
│   │   ├── hamiltonian.py       # Multi-mode BChl Model (FR5)
│   │   ├── solver.py            # MesoHOPS wrapper
│   │   └── pulse.py             # Pulse functional forms (FR10)
│   └── visualization/           # Shared Plotting Logic (FR8)
│       ├── theme.py             # Visual Style Guide Tokens
│       └── generator.py
├── data/
│   ├── raw/                     # Baseline references
│   └── converged/               # Production L=10 HDF5 output
├── tests/                       # Validation Suite
│   └── unit/                    # Core logic tests
└── logs/                        # Execution History
```

### Architectural Boundaries

**API/Parameter Boundaries:**
Solvers are "Stateless Wrappers". They ingest `parameters.yaml` and emit `data/converged/*.h5`.

**Data Boundaries:**
HDF5 is the universal data exchange format. Group structure `/metadata/params` must match the flat keys in `parameters.yaml`.

### Requirements to Structure Mapping

**Feature: Mandatory Convergence Audit (NFR2)**
- Logic: `reproducibility/audit_convergence.py`
- Trigger: Called by `main.py` after simulation runs.

**Feature: Single Point of Entry (FR7)**
- Logic: `reproducibility/main.py`
- Action: Automates environment check → Production run → Audit → Figure export.

**Feature: Visual Consistency (FR8)**
- Logic: `src/visualization/theme.py`
## Architecture Validation Results

### Coherence Validation ✅
- **Decision Compatibility**: Multi-language orchestration via `main.py` is robust and aligns with the existing `MesoHOP-sim` environment.
- **Pattern Consistency**: `snake_case` usage across all layers (YAML, Py, Jl) prevents cognitive friction for agents.
- **Structure Alignment**: The monorepo structure cleanly separates core solvers from orchestration logic.

### Requirements Coverage Validation ✅
- **FR Category: Theoretical Modeling**: Supported by `src/pt_hops/`.
- **FR Category: Simulation Engine**: Supported by `reproducibility/main.py` and `parameters.yaml`.
- **Non-Functional Requirements**: Memory optimization and convergence audits are explicitly integrated into the `reproducibility/` layer.

### Implementation Readiness Validation ✅
- **Decision Completeness**: Versions and rationale are documented.
- **Structure Completeness**: Directory tree is granular and specific.

### Gap Analysis Results
- **Priority: Minor**: Exact HDF5 internal path schema (e.g., `/results/densmat`) needs a "Standardize or Die" rule during the first epic.
- **Priority: Important**: The visual style guide (`theme.py`) must be the very first file created to ensure figure consistency.

### Architecture Completeness Checklist
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** **READY FOR IMPLEMENTATION**
**Confidence Level**: **High**

**Key Strengths:**
- Single source of truth via `parameters.yaml`.
- Rigorous convergence audit logic mandated by architecture.
- Full support for multi-mode realistic spectral densities.

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all naming conventions strictly.
- Never hardcode a physics parameter; always pull from the `Config` object initialized from `parameters.yaml`.

**First Implementation Priority:**
Initialize the repository structure and create the `parameters.yaml` schema based on the PRD's physical constants.
