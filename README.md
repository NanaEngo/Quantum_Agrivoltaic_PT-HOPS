# Quantum Dynamics & Spectral Bath Engineering

Computational framework, simulation pipelines, and manuscript source files for two research projects in non-Markovian quantum dynamics.

---

## 🚀 Quick Start

All simulations require the `MesoHOP-sim` conda environment.

### 💻 Laptop Mode (fast verification, L=3, n_traj=4)

```bash
mamba run -n MesoHOP-sim python \
  Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main.py \
  --config Redac_Paper1/quantum_simulations_framework_parallel_260509/laptop_parameters.yaml
```

Produces low-resolution figures and step-by-step CSVs in `reproducibility/results/` in ~10 min.

### 🏢 Production Mode (publication data, L=8, K=2, n_traj=100)

```bash
# Run the full production pipeline with L=8, dt=1.0fs, N=100
mamba run -n MesoHOP-sim python \
  Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/main.py \
  --config Redac_Paper1/quantum_simulations_framework_parallel_260509/parameters.yaml \
  --parallel
```

Requires 128 GB RAM, 24+ CPU cores. Monitor with:

```bash
tail -f Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/logs/execution_*.log
```

### 🖥️ Cluster (SLURM)

```bash
chmod +x Redac_Paper1/quantum_simulations_framework_parallel_260509/run_cluster.sh
./Redac_Paper1/quantum_simulations_framework_parallel_260509/run_cluster.sh
```

### 🧪 Full Test Suite

```bash
# All tests with live logging on screen
mamba run -n MesoHOP-sim python -m pytest \
  Redac_Paper1/quantum_simulations_framework_parallel_260509/tests/ -v

# JPCL 12-test SI validation suite only
mamba run -n MesoHOP-sim python -m pytest \
  Redac_Paper1/quantum_simulations_framework_parallel_260509/tests/test_jpcl_resubmission_suite.py -v

# 3-site dynamics smoke test
mamba run -n MesoHOP-sim python -m pytest \
  Redac_Paper1/quantum_simulations_framework_parallel_260509/tests/test_3site_dynamics.py -v
```

Test logs are written to `reproducibility/logs/tests_<YYYYMMDD>.log` and displayed live via `pytest.ini`.

### 🔍 Convergence Audit Only

```bash
mamba run -n MesoHOP-sim python \
  Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/audit_convergence.py
```

---

## 🌾 Project 1: Quantum-Enhanced Agrivoltaics

**Target Journal:** *The Journal of Physical Chemistry Letters* (JPCL) | **ID:** `jz-2026-00994t`  
**Status:** Major Revision in progress

Uses **PT-HOPS/SBD** (Process Tensor Hierarchy of Pure States with Stochastically Bundled Dissipators) to simulate excitonic energy transfer in the FMO complex. Investigates how dual-band spectral filtering (750 + 820 nm) selectively populates vibronic resonances to enhance quantum coherence.

### Key Performance Metrics (295 K)

| Metric | Filtered (750+820 nm) | Broadband | Enhancement |
|--------|----------------------|-----------|-------------|
| Coherence Lifetime | 420 ± 35 fs | 280 ± 25 fs | **+50%** |
| Transfer Yield | 89.2% | 71.4% | **+25%** |
| IPR (Delocalization) | 6.8 sites | 4.1 sites | **+66%** |

### Canonical Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Hierarchy depth | L = 8 | `parameters.yaml` |
| Matsubara terms | K = 2 | `parameters.yaml` |
| Time step | Δt = 1.0 fs | `parameters.yaml` |
| Temperature | 295 K | `parameters.yaml` |
| Reorganization energy | λ_D = 35 cm⁻¹ | `parameters.yaml` |
| Vibronic modes | 12 (Kleinekathöfer/Coker) | `parameters.yaml` |
| Disorder realizations | 100 | `parameters.yaml` |

---

## 🧪 Project 2: Anderson Model Comparison

**Publication:** *Physical Review B*

Comparative study of the Anderson model in weak and strong interaction regimes:
- **Julia**: `HierarchicalEOM.jl` (ASO space)
- **Python**: `QuTiP` (Tanimura formalism)

---

## 📂 Repository Structure

```
Quantum_Agrivoltaic_PT-HOPS/
├── Redac_Paper1/
│   ├── Theory_Journals_main/JPCL/          # Manuscript, SI, Response, Cover Letter
│   └── quantum_simulations_framework_parallel_260509/
│       ├── parameters.yaml                 # ← Single source of truth
│       ├── laptop_parameters.yaml          # Laptop-safe overrides (L=3, n_traj=4)
│       ├── pytest.ini                      # Live log config
│       ├── core/                           # HopsSimulator, constants, Hamiltonian
│       ├── extensions/                     # PT_HopsNoise, SBD_HopsTrajectory
│       ├── models/                         # QuantumDynamicsSimulator, etc.
│       ├── utils/                          # FigureGenerator (600 DPI), CSVDataStorage
│       ├── reproducibility/
│       │   ├── main.py                     # Pipeline entry point
│       │   ├── audit_convergence.py        # L/K convergence audit
│       │   ├── results/                    # Step-by-step CSVs (auto-generated)
│       │   └── logs/                       # Execution + test logs (auto-generated)
│       └── tests/
│           ├── conftest.py                 # Shared logger + PASS/FAIL hooks
│           ├── test_jpcl_resubmission_suite.py  # 12 SI validation tests
│           ├── test_3site_dynamics.py      # 3-site smoke test
│           └── test_*.py                  # Unit tests per module
├── notebooks/                             # Anderson model Jupyter notebooks
└── manuscrit/                             # Anderson model PRB source
```

---

## ⚙️ Technical Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| MesoHOPS | v1.6+ | PT-HOPS/SBD non-Markovian dynamics |
| Python | 3.10+ | Simulation framework |
| joblib | latest | Multi-core parallelization (2/3 of CPUs) |
| pytest | 9.0+ | Test suite with live logging |
| achemso | latest | JPCL LaTeX formatting |

---

## ⚠️ Research Stability Rules

1. **Parameter integrity** — read all physics values from `parameters.yaml`; never hardcode.
2. **No fake data** — never commit `*.INVALID_FALLBACK_DATA.csv`.
3. **HDF5 via LFS** — use Git LFS for files in `data/converged/`.
4. **Dated manuscripts** — all LaTeX files must include the date (e.g., `Manuscript_JPCL_26-05-08.tex`).
5. **Terminology** — SBD = **Stochastically Bundled Dissipators** (never "Spectrally Bundled").

---

## 📑 Citation & Contact

> *Spectral Engineering of Vibronic Coherence in Photosynthetic Complexes*, JPCL (2026), in revision. Manuscript ID: `jz-2026-00994t`

**Corresponding Author:** Steve Cabrel Teguia Kouam  
📧 [steve.teguia@facsciences-uy1.cm](mailto:steve.teguia@facsciences-uy1.cm)

---
*License: MIT*
