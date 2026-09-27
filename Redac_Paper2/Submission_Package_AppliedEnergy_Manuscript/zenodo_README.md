# Quantum Agrivoltaics Paper 2 — Data & Code Archive

**Title:** Spectral Co-Design of Agrivoltaic Modules for Multifunctional Net Energy Benefit: A Quantum-Guided Digital Twin

**Authors:** Teguia Kouam S.C., Goumai Vedekoi T., Tchapet Njafa J.-P., Nguenang J.-P., Nana Engo S.G.

**Journal:** Applied Energy (Elsevier) — submitted September 2026

**Corresponding author:** Steve Cabrel Teguia Kouam (steve.teguia@facsciences-uy1.cm)

---

## Overview

This archive contains all source code, production data, parameter files, manuscript LaTeX sources, figures, and verification scripts necessary to reproduce the results reported in the manuscript. The archive is **self-contained** — it does not depend on any external repository.

## Contents

```
zenodo_package/
├── README.md                          # This file
├── LICENSE                            # CC BY 4.0 (data) + MIT (code)
├── MANIFEST.txt                       # Complete file listing
├── main.py                           # CLI entry point
├── pyproject.toml                     # Python packaging (dependencies)
├── parameters.yaml                    # Single source of truth for all parameters
│
├── src/                               # Digital-twin framework (Python ≥3.12)
│   ├── quantum_interface/             #   8-site FMO + 9×9 NPoM Hamiltonian,
│   │                                  #   PT-HOPS/SBD solver, pulse shaping,
│   │                                  #   SERS diagnostics, MPS/QKRR signal processing
│   ├── microclimate/fao56.py          #   FAO-56 Penman–Monteith
│   ├── lca/                           #   Net Ecological Benefit + LCA
│   ├── materials/                     #   Zwitterionic coatings, MOF models
│   ├── algorithms/                    #   QAOA network scheduling
│   ├── geophysics/                    #   Quantum gravimetry model
│   └── iot_security/                  #   BB84 QKD, data sovereignty, GQAS
│
├── data/converged/
│   └── production_dynamics.h5         # Production HDF5 (L=8, K=2, Δt=0.2 fs)
│
├── scripts/                           # Figure generation, table extraction,
│                                      # production launch, verification
├── tests/                             # Unit + integration tests (pytest)
│
└── manuscript/                        # LaTeX source + compiled PDFs + figures
    ├── AppliedEnergy_main_2609.tex/pdf
    ├── AppliedEnergy_SM_2609.tex/pdf
    ├── AppliedEnergy_Cover_letter.tex/pdf
    ├── references.bib                 # ~193 BibTeX entries
    └── figures/                       # 5 main + 2 SI + graphical abstract
```

## Requirements

- **Python** ≥ 3.12
- **Core dependencies:** numpy ≥1.26, pyyaml ≥6.0, pydantic ≥2.5, h5py ≥3.11, matplotlib ≥3.8
- **Trajectory propagation:** mesohops ≥1.7.0 (not needed for analysis/figures)
- **Tests:** pytest ≥7.4, pytest-cov ≥4.1
- **LaTeX:** texlive with elsarticle, siunitx, physics, mhchem, cleveref, hyperref

## Quick Start

```bash
pip install -e .                           # Install dependencies
python main.py --solar-flux 950.0          # Run digital-twin orchestrator
python scripts/check_h5_vals.py            # Inspect production HDF5
python scripts/regenerate_figures.py       # Regenerate all figures
pytest tests/unit/ -v                      # Run unit tests
```

## Production Parameters

| Parameter | Value |
|---|---|
| Hierarchy depth L | 8 |
| Matsubara terms K | 2 |
| Time step Δt | 0.2 fs |
| Temperature T | 295 K |
| Trapping rate Γ_RC | 0.15 fs⁻¹ |
| SBD bundles per site | 3 |
| Simulation window | 1000 fs |

## Key Results

| Observable | Value | Manuscript ref. |
|---|---|---|
| Forward transfer yield (filtered) | Φ_FT = 0.89 ± 0.03 | SM Table S2 |
| NPoM yield (V=1.2 nm³) | Φ_FT = 0.0799 | Table 1 |
| Global canopy yield (α=0.01) | 0.971 | Eq. 1 |
| Local transport suppression | 91.8% | Table 1 |
| Coherence lifetime (filtered) | 420 ± 35 fs | SM Table S2 |
| ET reduction (FAO-56) | 28% (±10%) | Section 2.5 |
| Net Ecological Benefit | 72.6 kgCO₂e/m²/yr | Section 2.6 |
| Payback (30% subsidy) | 4.32 yr | Section 2.6 |

## Citation

```bibtex
@article{TeguiaKouam2026AE,
  author  = {Teguia Kouam, Steve Cabrel and Goumai Vedekoi, Theodore and
             Tchapet Njafa, Jean-Pierre and Nguenang, Jean-Pierre and
             Nana Engo, Serge Guy},
  title   = {Spectral Co-Design of Agrivoltaic Modules for Multifunctional
             Net Energy Benefit: A Quantum-Guided Digital Twin},
  journal = {Applied Energy},
  year    = {2026},
  note    = {Submitted}
}
```

## License

- **Data, figures, manuscript:** CC BY 4.0
- **Source code:** MIT License

See `LICENSE` for full details.

## Contact

Steve Cabrel Teguia Kouam — steve.teguia@facsciences-uy1.cm
