# Quantum-Enhanced Agrivoltaics & Strongly Correlated Systems

This repository contains the research framework, simulation codebase, and manuscript source files for two primary research areas in quantum dynamics:

1. **Quantum-Enhanced Agrivoltaics**: Spectral Bath Engineering via Non-Markovian Dynamics in the FMO complex.
2. **Anderson Model Comparison**: A comparative study of the Anderson model in weak and strong interaction regimes (Julia vs. Python).

**Official Repository**: [https://github.com/NanaEngo/Quantum_Agrivoltaic_PT-HOPS.git](https://github.com/NanaEngo/Quantum_Agrivoltaic_PT-HOPS.git)

---

## 🌾 Project 1: Quantum-Enhanced Agrivoltaics

### Manuscript Status

| Field | Value |
|-------|-------|
| **Journal** | *The Journal of Physical Chemistry Letters* (JPCL) |
| **Manuscript ID** | `jz-2026-00994t` |
| **Status** | **Major Revision in progress** — deadline 28-May-2026 |
| **Last updated** | 2026-05-02 |

### What this project does

Uses PT-HOPS/SBD (Process Tensor Hierarchy of Pure States with Stochastically Bundled Dissipators) to simulate excitonic energy transfer in the FMO photosynthetic complex under spectrally engineered photon baths. Dual-band optical filtering (750 nm + 820 nm) selectively populates vibronic resonances, extending coherence lifetimes by 20–50% and improving forward transfer yields by 25% at 295 K.

### Key results

| Metric | Filtered | Broadband | Enhancement |
|--------|----------|-----------|-------------|
| Coherence lifetime τ_c | 420 ± 35 fs | 280 ± 25 fs | +50% |
| Forward transfer yield Φ_FT | 89.2% | 71.4% | +25% |
| IPR (delocalization) | 6.8 sites | 4.1 sites | +66% |

### Running simulations

All simulations **must** use the `MesoHOP-sim` mamba environment:

```bash
mamba run -n MesoHOP-sim python Redac_Paper1/quantum_simulations_framework/reproducibility/main.py
```

The pipeline validates parameters (L=10, K=10), checks MesoHOPS availability, runs the L=9/10/11 convergence audit, and generates figures. It will **exit with an error** if MesoHOPS is not available, preventing invalid fallback data from being saved.

### 🚀 HPC & Cluster Deployment

For remote servers or clusters, use the provided environment and execution scripts to ensure stable, background processing:

1. **Environment Setup**:
   ```bash
   mamba env create -f environment.yml
   # or
   pip install -r requirements.txt
   ```

2. **Background Execution**:
   To prevent simulation interruption if your terminal disconnects, use the generic cluster script:
   ```bash
   ./run_cluster.sh
   ```
   This script triggers `nohup` and redirects all output to `reproducibility_cluster.log`.

3. **Monitoring Results**:
   ```bash
   tail -f reproducibility_cluster.log
   ```

### Canonical simulation parameters

All parameters are defined in `Redac_Paper1/quantum_simulations_framework/parameters.yaml` — the single source of truth. Never hardcode physics values.

| Parameter | Value |
|-----------|-------|
| Hierarchy depth L | **10** |
| Matsubara terms K | **10** |
| Time step Δt | **0.5 fs** |
| Pulse FWHM | **50 fs**, centered at t = 0 |
| Temperature | **295 K** |
| λ_D (Drude-Lorentz) | **35 cm⁻¹** |
| γ_D | **50 cm⁻¹** |
| Vibronic modes | **12** (Kleinekathöfer/Coker) |

---

## 🧪 Project 2: Anderson Model Comparison

Comparative study of a single magnetic impurity coupled to two fermionic reservoirs, comparing weak and strong interaction regimes using:

- **Julia** — `HierarchicalEOM.jl` (HEOM in extended ASO space)
- **Python** — `QuTiP` (Tanimura formalism)

**Status**: Published in *Physical Review B*.

Observables studied: spectral density A(ω), impurity occupation ⟨n_σ⟩, time-dependent current I(t), differential conductance G(ω).

---

## 🛠 Technical Stack

| Tool | Version | Purpose |
|------|---------|---------|
| MesoHOPS (adHOPS) | v1.6 | PT-HOPS/SBD non-Markovian dynamics |
| Python | 3.10+ | Simulation framework |
| HierarchicalEOM.jl | latest | Julia HEOM (Anderson model) |
| QuTiP | 5.2.2+ | Python HEOM (Anderson model) |
| achemso (LaTeX) | latest | JPCL manuscript formatting |
| Matplotlib | latest | Figures (600 DPI, JPCL theme) |

**Hardware**: AMD Ryzen 5 5500U | 40 GB RAM (local only, no HPC).

---

## 📂 Repository Structure

```
Quantum_Agrivoltaic_PT-HOPS/
├── Redac_Paper1/
│   ├── Theory_Journals/JPCL/          # Manuscript, SI, response letter, cover letter
│   └── quantum_simulations_framework/ # Simulation codebase
│       ├── parameters.yaml            # ← Single source of truth for all parameters
│       ├── core/                      # HopsSimulator, constants, Hamiltonian
│       ├── models/                    # QuantumDynamicsSimulator, spectral optimizer
│       ├── extensions/                # PT_HopsNoise, SBD_HopsTrajectory
│       ├── utils/                     # FigureGenerator (600 DPI), JPCL theme
│       ├── reproducibility/
│       │   ├── main.py                # ← Single entry point
│       │   ├── audit_convergence.py   # L=9,10,11 convergence audit
│       │   └── results/               # Valid HDF5/CSV results (see README inside)
│       └── tests/
├── notebooks/                         # Anderson model Jupyter notebooks
├── manuscrit/                         # Anderson model PRB publication
├── _bmad-output/planning-artifacts/   # PRD, architecture, epics
└── Archive/                           # Legacy code
```

---

## ⚠️ Important Rules for Contributors

- **Never commit** `*.INVALID_FALLBACK_DATA.csv` files — these are quarantined fake results from MesoHOPS fallback runs
- **Never commit** HDF5 files to `data/converged/` without Git LFS configured
- **Always** read parameters from `parameters.yaml`, never hardcode physics values
- **Always** date manuscript filenames: `Manuscript_JPCL_YY-MM-DD.tex`

---

## 📑 Citation

If you use this framework, please cite the corresponding JPCL article (in revision).

**Corresponding Author**: Steve Cabrel Teguia Kouam — [steve.teguia@facsciences-uy1.cm](mailto:steve.teguia@facsciences-uy1.cm)

## License

MIT License
