# Quantum Dynamics & Spectral Bath Engineering

This repository hosts the computational framework, simulation pipelines, and manuscript source files for two major research projects in non-Markovian quantum dynamics.

---

## 🚀 Quick Start (Execution Guide)

All simulations require the `MesoHOP-sim` environment. Choose your mode based on hardware availability:

### 💻 Local Verification (Laptop Mode)
**Goal:** Rapidly test logic, ensure environment is set up, and generate low-resolution figures.
*   **Parameters:** $L=3, N=4$.
*   **Command:**
    ```bash
    mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel/reproducibility/main.py --config Redac_Paper1/quantum_simulations_framework_parallel/laptop_parameters.yaml
    ```

### 🏢 Production Run (HPC / Cluster Mode)
**Goal:** Generate publication-quality data and figures for manuscript resubmission.
*   **Parameters:** $L=9, K=2$.
*   **Hardware:** 128 GB RAM, 24+ CPU cores recommended.
*   **Command:**
    ```bash
    mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel/reproducibility/main.py
    ```

### 🧪 Validation Suite
Verify the framework's mathematical integrity and SI compliance:
```bash
# Detailed output
mamba run -n MesoHOP-sim pytest Redac_Paper1/quantum_simulations_framework_parallel/tests/test_jpcl_resubmission_suite.py -sv

# Visual progress bar
mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework_parallel/tests/test_jpcl_resubmission_suite.py
```

---

## 🌾 Project 1: Quantum-Enhanced Agrivoltaics
**Target Journal:** *The Journal of Physical Chemistry Letters* (JPCL) | **ID:** `jz-2026-00994t`

### Physics Overview
This project uses **PT-HOPS/SBD** (Process Tensor Hierarchy of Pure States with Stochastically Bundled Dissipators) to simulate excitonic energy transfer in the FMO complex. We investigate how spectral engineering of the photon bath (via dual-band filtering) can selectively populate vibronic resonances to enhance quantum coherence.

### Key Performance Metrics (at 295 K)
| Metric | Filtered (750+820nm) | Broadband (Flat) | Enhancement |
|--------|----------------------|------------------|-------------|
| **Coherence Lifetime** | 420 ± 35 fs | 280 ± 25 fs | **+50%** |
| **Transfer Yield** | 89.2% | 71.4% | **+25%** |
| **IPR (Delocalization)** | 6.8 sites | 4.1 sites | **+66%** |

---

## 🧪 Project 2: Anderson Model Comparison
**Publication:** *Physical Review B*

A comparative study of the Anderson model in weak and strong interaction regimes, contrasting two state-of-the-art implementations:
-   **Julia**: `HierarchicalEOM.jl` (ASO space)
-   **Python**: `QuTiP` (Tanimura formalism)

*Focus: Spectral densities, impurity occupation, and differential conductance.*

---

## 📂 Repository Architecture

```bash
Quantum_Agrivoltaic_PT-HOPS/
├── Redac_Paper1/
│   ├── Theory_Journals/JPCL/          # LaTeX Source (Manuscript, SI, Response)
│   └── quantum_simulations_framework_parallel/ 
│       ├── parameters.yaml            # ← Single Source of Truth
│       ├── core/                      # Parallel Solver (joblib + MesoHOPS)
│       ├── reproducibility/           # Entry points & Convergence Audits
│       ├── tests/                     # 12-test SI Validation Suite
│       └── utils/                     # 600 DPI Figure Generator (JPCL Theme)
├── notebooks/                         # Anderson model Jupyter notebooks
└── manuscrit/                         # Anderson model PRB source
```

---

## ⚙️ Technical Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| **MesoHOPS** | v1.6+ | Non-Markovian Dynamics |
| **Python** | 3.10+ | Parallel Framework |
| **Joblib** | Latest | Multi-core acceleration |
| **achemso** | Latest | JPCL Formatting |

---

## ⚠️ Guidelines for Research Stability

1.  **Parameter Integrity**: Always read physics values from `parameters.yaml`. Never hardcode constants.
2.  **Version Control**: 
    *   Do not commit `*.INVALID_FALLBACK_DATA.csv`.
    *   Use Git LFS for HDF5 files in `data/converged/`.
    *   Date all manuscript versions (e.g., `Manuscript_JPCL_26-05-08.tex`).

---

## 📑 Citation & Contact

If you use this framework for your research, please cite:
> *Spectral Engineering of Vibronic Coherence in Photosynthetic Complexes*, JPCL (2026), in revision.

**Corresponding Author:** Steve Cabrel Teguia Kouam
📧 [steve.teguia@facsciences-uy1.cm](mailto:steve.teguia@facsciences-uy1.cm)

---
*License: MIT License*
