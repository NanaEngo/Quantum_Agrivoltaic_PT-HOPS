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

## 3. Graphify Knowledge Graph (2026-06-28)

Full codebase graph built: **4,332 nodes · 6,034 edges · 439 communities · 136,691 input / 61,930 output tokens**.

### Key Discoveries
- **God Nodes**: HopsSimulator (59 edges), PublishManager (40), FigureGenerator (35) — core abstractions
- **NPoM-SERS Trade-off Chain**: `mode_volume_nm3 → g₀ = 120×√(1/V) cm⁻¹ → H_dressed[site,plasmon] = g₀ → 9×9 Hamiltonian → MesoHOPS → Φ_FT` traced across communities 96, 220, 237
- **Bridge Node**: `ANALYSIS_20260624_POST_PROD` connects quantum dynamics simulations (community 96) to NPoM figures (community 220/237)
- **Hyperedges** (selected):
  - NPoM Plasmonic Cavity Study: plasmon traps >82% population, 25× suppression
  - Cryogenic 77K: 2.1× Φ_FT recovery via reduced thermal decoherence
  - Paper 2 integrates 5 domains: quantum, microclimate, LCA, IoT, SERS
  - BMAD chain: PRD → Architecture → Epics → Readiness
  - Paper 2 coverage gaps: orchestrator 0%, plot_utils 0%, solver 51%

### Outputs
- `graphify-out/graph.html` — interactive visualization
- `graphify-out/GRAPH_REPORT.md` — full audit report
- `graphify-out/graph.json` — GraphRAG-ready data

## 4. Next Steps

### A. Pre-Submission Quality Checks
- [x] Compile manuscripts (Manuscript + SI + Cover Letter) with LaTeX to verify cross-refs.
- [x] Update figure captions in Manuscript_NatureEnergy_26-06-25.tex to match the new 3-panel layouts.
- [x] Update `plot_utils.py` (Paper2FigureGenerator) to match the new multi-panel code.
- [x] Audit all in-text panel references (e.g. `\Cref{fig:npq_switch}a`) for correctness.
- [x] Run full test suite (unit + integration).
- [x] Final quality gates (10/10) check.

### B. Paper 2 Submission
- [ ] Generate single-column submission version (Manuscript_NatureEnergy_26-06-25.tex) from twocolumn draft.
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

## 5. Pistons_Improvements260625.md Full Audit (2026-06-30)

All 37 axes from `Redac_Paper2/Pistes_Improvements260625.md` have been cross-referenced against `Manuscript_NatureEnergy_26-06-25.tex` and `SI.tex`. **Status: 37/37 COMPLETE.**

| Axe | Description | Status |
|-----|-------------|--------|
| 1 | Jumeau Numérique Agrivoltaïque | ✅ MS + SI |
| 2 | Robustesse Calibration Dynamique IoT | ✅ MS + SI |
| 3 | Modélisation Socio-Économique (LCA) | ✅ MS + SI |
| 4 | Ciblage Moléculaire Spécifique | ✅ MS + SI |
| 5 | Soiling Factor | ✅ MS |
| 6 | QML / Hybrid Signal Processing | ✅ MS + SI |
| 7 | Revêtements Zwitterioniques | ✅ MS + SI |
| 8 | Gravimétrie Quantique | ✅ MS + SI |
| 9 | QAOA Nexus Optimization | ✅ MS + SI |
| 10 | BB84 + GQAS + Data Sovereignty | ✅ MS + SI |
| 11 | Limites Multiexcitoniques | ✅ MS |
| 12 | Relégation 77 K → SI | ✅ MS + SI |
| 13 | \|E\|⁴ Picocavité Limits | ✅ MS Methods |
| 14 | Abrasion Mécanique Zwitterionique | ✅ MS Limitations + SI |
| 15 | Pertinence Temporelle Edge QML | ✅ MS Discussion |
| 16 | Gradiométrie Gravitationnelle | ✅ MS + SI |
| 17 | Performance Bonds (24-month sunset) | ✅ SI S5.4 |
| 18 | Budget Calcul QML/QAOA | ✅ MS + SI |
| 19 | Coût Fibre Optique (30 USD/m²) | ✅ SI S5.1 |
| 20 | Risque Écotoxique CdTe | ✅ SI S11.1 |
| 21 | NV Diagnostic Hors-Sol | ✅ SI S11.8 |
| 22 | Approximation FAO-56 | ✅ MS Methods |
| 23 | Diaphonie Humidité/Pb²⁺ | ✅ MS (Session 25) |
| 24 | Pertes Sifting/Privacy Amplification | ✅ SI S6.1 |
| 25 | Canopée Plasmonique 1% sentinel | ✅ MS Discussion |
| 26 | Limites QUBO 3→24 qubits | ✅ SI S11.4 |
| 27 | Incertitude FAO-56 ±10% | ✅ MS Limitations (Session 25) |
| 28 | Instabilité Numérique Baseline | ✅ MS Fig 1 caption (Session 25) |
| 29 | Rôle Secondaire Crédits Carbone | ✅ MS Limitations |
| 30 | OMIT Dissipation Cohérente | ✅ SI S4.2 |
| 31 | Tolérances GQAS | ✅ SI S11.9 |
| 32 | Dégradation LOD ×10 matrix | ✅ MS Limitations (Session 25) |
| 33 | FMO → LHCII Biophysical Mapping | ✅ SI S1.4 |
| 34 | Protocole Auto-Assemblage NPoM | ✅ SI S11.2 |
| 35 | Fallback Classique MILP | ✅ SI S11.4 |
| 36 | Ciblage GCF/BAD | ✅ MS Limitations (Session 25) |
| 37 | Zenodo DOIs + Code Availability | ✅ MS (Session 25) |
