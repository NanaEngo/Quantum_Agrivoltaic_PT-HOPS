# Manuscript Drafting Roadmap: Quantum Agrivoltaics Paper 2

**Date:** 2026-06-16  
**Authors:** Taamangtchu & Antigravity  
**Target Venue:** *Nature Energy* (APC-free subscription route)

---

## 1. Executive Structure (Main Manuscript)

### Section 1: Introduction
- **Scientific Context:** Land-use and light-sharing conflicts in conventional agrivoltaics.
- **Hypothesis:** Selective spectral bath engineering using semi-transparent Organic Photovoltaics (OPV) creates polariton-dressed exciton-vibronic states in biological light-harvesting complexes (FMO), protecting them while boosting solar conversion.
- **Methodological Scope:** Micro-to-macro bridging (MesoHOPS quantum dynamics $\to$ FAO-56 agricultural microclimate $\to$ Socioeconomic Life Cycle Assessment).

### Section 2: Results
- **Subsection 2.1: Microscopic Bio-Organic Interface & Strong Coupling**
  - Discussion of the 9x9 dressed Hamiltonian (8 FMO sites + 1 plasmonic cavity mode).
  - Energy funneling efficiency and trapping yield $\Phi_{FT}$ calculations.
  - **Figure 1 Integration:** Dynamics of exciton transport and Reaction Center trapping accumulation.
- **Subsection 2.2: In Situ Optomechanical SERS Diagnostics**
  - Non-destructive readout of vibrational signatures under ambient conditions.
  - OMIT dynamic photo-protection switch under exciton overload.
  - **Figure 2 Integration:** SERS Raman spectrum peak intensities (180, 740, and 1145 cm⁻¹).
- **Subsection 2.3: Crop Microclimate & Water-Energy-Food (WEF) Nexus**
  - Greenhouse evapotranspiration $ET_c$ reductions due to NIR/UV shielding.
  - Net Ecological Benefit (NEB) calculation under Scenario A (Quantum OPV), B (Static Shading), and C (Open Field).
  - **Figure 3 Integration:** LCA Scenario comparison (Avoided Emissions vs Crop Biomass).
- **Subsection 2.4: Socioeconomics & Telemetry Security**
  - CAPEX amortization through cooperative cost-sharing.
  - Telemetry authentication using simulated BB84 QKD keys.

### Section 3: Discussion & Policy Recommendations
- Mitigating the "Quantum Divide" between developed economies and smallholders.
- Policy framework for carbon-linked subsidies in high-tech agrivoltaics.

---

## 2. Supporting Information (SI) Outline

- **Section S1: Hamiltonian Parameterization & Bath Decomposition**
  - Full details of the 8-site FMO site energies and electronic couplings.
  - Matsubara pole conversion parameters for non-Markovian bath memory.
- **Section S2: FAO-56 Crop Parameterization**
  - Reference evapotranspiration constants and shading adjustment equations.
- **Section S3: BB84 QKD Protocol Security Details**
  - Noise scaling, QBER threshold calculations, and fail-safe local loops.

---

## 3. Automated Figure Production in Codebase

The codebase is configured to automatically output the publication figures immediately after running the global simulation orchestrator:
```bash
PYTHONPATH=. conda run -n MesoHOP-sim python Redac_Paper2/main.py
```
- **Figure 1 Location:** `Redac_Paper2/Graphics/Figure1_Quantum_Dynamics.png`
- **Figure 2 Location:** `Redac_Paper2/Graphics/Figure2_SERS_Readout.png`
- **Figure 3 Location:** `Redac_Paper2/Graphics/Figure3_LCA_NEB_Comparison.png`
