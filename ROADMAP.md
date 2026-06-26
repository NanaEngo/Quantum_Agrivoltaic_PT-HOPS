# Roadmap - Quantum Agrivoltaics PT-HOPS

## 1. Project Overview
This project integrates quantum dynamics with agricultural modeling, IoT security, and SERS diagnostics.

## 2. Completed Milestones (Paper 2 — Nature Energy)

### A. Results Refinement (Physics & Economics)
- [x] Audit constants (Quantum, Microclimate, LCA) vs `parameters.yaml`.
- [x] Modélisation de l'encrassement (soiling factor) and clean-cycle OPEX.
- [x] Run Baseline simulation (No NPoM coupling) to isolate yield drop (0.9800 vs 0.0768).
- [x] Sensitivity analysis on NPoM distance (V=1.2 nm³ optimal volume scan).
- [x] Refine Microclimate parameters (`WIND_SPEED_GREENHOUSE_FACTOR`).
- [x] Refine LCA Economics (CAPEX/Revenue scaled to 500 m² cooperative micro-module).
- [x] LCA: Ajouter coût annuel de nettoyage des panneaux (OPEX = 800 USD/yr).
- [x] Upgrade NEB calculation to Monte Carlo sensitivity analysis (10,000 iterations).

### B. Paper 2 Post-Production Refinements
- [x] Reference Paper 1 validation framework in Paper 2 SI.
- [x] Define metric correlating `SERS_readout` to `trap_yield` (eta_diag = I_180 / Phi_FT).
- [x] Stern-Volmer DynamicCalibrator correction for temperature and salinity.
- [x] Figure 2c regenerated with agricultural targets (1435 cm⁻¹ 2,4,5-T + CQD Pb²⁺) visible in the image.
- [x] QML signal processing (Axe 6) mentioned in Discussion with cross-ref to SI Section S10.
- [x] Cover Letter "2.7 yr" carbon credit claim corrected to honest 0.2% revenue contribution.
- [x] All 3 figures regenerated with proper multi-panel labels (a), (b), (c).
- [x] Payback/NPV precision: 3.2→4.23 yr, +14,600→+37,664 USD across all 3 files.
- [x] Φ_FT^global: 0.971→0.972 for consistency with Eq. φ_global.

### C. System Integration & Submission Prep
- [x] Nature Energy Manuscript V5 Submission Package created and consolidated in `Redac_Paper2/Submission_Package_Nature_Energy_Manuscript/` (**Sole directory for active editing and compilation**).
- [x] Supporting Information (SI) synchronized, merged, and compiled.
- [x] IoT Security (BB84 QKD) Integration (buried single-mode fiber, 4.8% noise, fail-safe exception).
- [x] Full-scale SERS Diagnostic molecular signature targets defined.

## 3. Next Steps

### A. Pre-Submission Quality Checks
- [ ] Compile manuscripts (Manuscript + SI + Cover Letter) with LaTeX to verify cross-refs.
- [ ] Update figure captions in Manuscript.tex to match the new 3-panel layouts.
- [ ] Update `plot_utils.py` (Paper2FigureGenerator) to match the new multi-panel code.
- [ ] Audit all in-text panel references (e.g. `\Cref{fig:npq_switch}a`) for correctness.
- [ ] Run full test suite (unit + integration).
- [ ] Final quality gates (10/10) check.

### B. Paper 2 Submission
- [ ] Generate single-column submission version (Manuscript.tex) from twocolumn draft.
- [ ] Verify journal compliance (Nature Energy author guidelines).
- [ ] Prepare cover letter and point-by-point response (if applicable).
- [ ] Submit via Nature Energy online portal.

### C. Future R&D Directions
- [ ] Multi-module field-scale telemetry deployment.
- [ ] Hardware-in-the-loop validation of QKD fail-safe routines.
- [ ] Experimental verification of SERS LODs on NPoM substrates under field fouling.
- [ ] Full-scale Monte Carlo LCA with correlated input distributions.
- [ ] Dielectric nanoantenna designs (Si, TiO₂) to minimize transport penalty.
- [ ] 2DES experiments with spatial light modulator pulse shaping.
- [ ] Quantum Machine Learning on edge processors for real-time anomaly detection.
