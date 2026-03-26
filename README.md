# Quantum-Enhanced Agrivoltaics & Strongly Correlated Systems

This repository contains the research framework, simulation codebase, and manuscript source files for two primary research areas in quantum dynamics:

1.  **Quantum-Enhanced Agrivoltaics**: Spectral Bath Engineering via Non-Markovian Dynamics.
2.  **Anderson Model Comparison**: A comparative study of the Anderson model in weak and strong interaction regimes (Julia vs. Python).

**Official Repository**: [https://github.com/NanaEngo/Quantum_Agrivoltaic_PT-HOPS.git](https://github.com/NanaEngo/Quantum_Agrivoltaic_PT-HOPS.git)

---

## 🌾 Project 1: Quantum-Enhanced Agrivoltaics
Our framework leverages the quantum mechanical nature of photosynthetic energy transfer to optimize agrivoltaic systems, co-locating solar energy generation with high-productivity agricultural production.

## 📄 Manuscript Status

- **Status**: Ready for Submission
- **Target Journal**: *Energy & Environmental Science* (EES)
- **Primary Objective**: Leveraging non-Markovian coherence in the FMO complex to enhance photosynthetic ETR under semi-transparent OPVs.

### Key Validated Metrics
- **Photosynthetic Enhancement**: \SI{25.0}{\percent} ETR increase via vibronic resonance matching.
- **Photovoltaic Performance**: \SI{18.83}{\percent} PCE for the balanced dual-band configuration.
- **System ETR**: \SI{80.51}{\percent} (retaining agricultural productivity under shading).
- **Eco-Compatibility**: PM6-derivative B-index of **101.5** (highly biodegradable).
- **Environmental Stability**: \SI{0.17}{\percent} annual degradation in both PCE and ETR.

---

## 🧪 Project 2: Comparative Study of the Anderson Model
This project systematically analyzes key observables of a single impurity coupled to two fermionic reservoirs (Anderson model), comparing performance in weak and strong interaction regimes using multiple numerical implementations.

### Implementation Methods
- **Julia (HierarchicalEOM.jl)**: HEOM in the extended space of Auxiliary Statistical Operators (ASOs).
- **Python (QuTiP)**: HEOM implementation following the Tanimura formalism.

### Research Objectives
- **Spectral density** $A(\omega)$
- **Impurity occupation** $\langle n_\sigma \rangle$
- **Time-dependent current** $I(\omega)$
- **Differential conductance** $G(\omega)$

---

## 🛠 Technical Stack & Environment

### Computational Engines
- **MesoHOPS (adHOPS) v1.6**: Core non-Markovian dynamics for photosynthetic systems.
- **HierarchicalEOM.jl (Julia 1.10+)**: Efficient HEOM for deep hierarchy structures.
- **QuTiP (Python 3.10+)**: User-friendly HEOM prototyping following Tanimura formalism.
- **ORCA v6.1.0**: DFT calculations for molecular properties (wB97X-D4/def2-SVP).

### Environment Specification
- **Hardware**: AMD Ryzen 5 5500U | 40 GB RAM.
- **Python Environment**: `mamba run -n MesoHOP-sim ...`
- **Julia Dependencies**: `QuantumToolbox`, `CairoMakie`.

---

## 📂 Project Structure

```text
.
├── notebooks/                       # Core Research Notebooks
│   ├── populations_{jl,py}.ipynb    # Anderson Model Populations
│   ├── DOS_{jl,py}.ipynb            # Anderson Model Density of States
│   ├── current_and_cond_py.ipynb    # Anderson Model Transport
│   └── quantum_coherence_...py      # Agrivoltaics Driver
├── Redac_Paper1/                    # Manuscript Editorial Directory (Agrivoltaics)
│   ├── Q_Agrivoltaics_EES_Main.tex  # LaTeX source
│   └── Graphics/                    # Verified figures
├── manuscrit/                       # Anderson Model Publication Resources
│   ├── article_theodore2_humanized.pdf # Published in PRB
│   └── article_theodore2_humanized.tex # Paper LaTeX source
├── simulation_data/                 # Archived simulation logs
└── Archive/                         # Legacy codebase and reference materials
```

---

## 🚀 Getting Started

### Installation
Please refer to [INSTALLATION.md](INSTALLATION.md) for detailed environment setup and dependency installation instructions.

### Running Simulations
The primary simulation suite can be executed via the main driver script:
```bash
python quantum_simulations_framework/quantum_coherence_agrivoltaics_mesohops_complete.py
```

### Building the Manuscript
To compile the submission documents, ensure you have a complete TeX distribution (e.g., TeX Live 2025) and use `latexmk`:
```bash
latexmk -pdf Q_Agrivoltaics_EES_Main.tex Supporting_Info_EES.tex Cover_Letter_EES.tex
```

---

## 📑 Core Research Contributions

1. **Spectral Bath Engineering**: A methodology for Identifying quantum-enhanced processes in nature and engineering artificial environments to maximize those resources.
2. **PT-HOPS & SBD**: Scalable non-Markovian dynamics framework achieving \num{10}x speedup over standard HEOM.
3. **Quantum Reactivity Descriptors**: Mechanistic prediction of OPV biodegradability via Fukui functions and chemical hardness.
4. **Pareto-Optimal Cogeneration**: Dual-band splitting strategy (\SI{440.4}{\nano\meter} and \SI{668.4}{\nano\meter}) for simultaneous energy-food maximization.

---

## 🤝 Citation & Contact

If you use this framework or data in your research, please cite our corresponding *Energy & Environmental Science* article.

**Corresponding Author**: Steve Cabrel Teguia Kouam ([steve.teguia@facsciences-uy1.cm](mailto:steve.teguia@facsciences-uy1.cm))