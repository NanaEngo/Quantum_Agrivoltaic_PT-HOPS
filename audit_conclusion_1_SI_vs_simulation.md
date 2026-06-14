# Audit Conclusion (1): SI “Additional quantum metrics” vs Simulation Data Consistency

## Scope
- Checked numeric targets in SI Section **S6: Additional quantum metrics**.
- Extracted simulation values at **t = 500 fs** from the available simulation dataset with matching column names.

## SI numeric targets (May 13, 2026)
From `Redac_Paper1/Theory_Journals_main/JPCL/SI_JPCL_26-05-13.tex` (and the submission package equivalent):
- **Filtered illumination** (t = 500 fs):
  - \(S_{\mathrm{vN}}(500\text{ fs}) = 0.51(6)\)
  - \(P(500\text{ fs}) = 0.82(4)\)
  - \(Q_{\mathrm{Mandel}}(500\text{ fs}) = 0.34(5)\)
- **Broadband illumination** (t = 500 fs):
  - \(S_{\mathrm{vN}}(500\text{ fs}) = 0.73(7)\)
  - \(P(500\text{ fs}) = 0.71(5)\)
  - Mandel Q broadband value not present in the S6 content that was read.

## Simulation numeric extraction (t = 500 fs)
From `Archive/simulation_data/quantum_metrics_evolution.csv`:
- At **t = 500.0 fs**:
  - `purity` = **0.2960526595114345**
  - `von_neumann_entropy` = **2.1284783687022784**

From `Archive/simulation_data/quantum_dynamics_hops_results.csv`:
- At **t = 500.0 fs** (exact):
  - `Entropy_VN` = **2.78868703e-02**
  - `Purity` = **9.91913480e-01**

## Consistency result (FAIL / Major mismatch)
Direct comparison vs SI S6 targets shows a large discrepancy:
- SI expects **purity ≈ 0.71 to 0.82**, but simulation gives **purity ≈ 0.296**.
- SI expects **SvN ≈ 0.51 to 0.73**, but simulation gives **von_neumann_entropy ≈ 2.128**.

### Interpretation (non-exhaustive)
This mismatch strongly suggests that at least one of the following is true:
1. SI S6 metrics were computed from a **different simulation run** (different parameter set and/or filtered vs broadband represented by a different dataset/condition).
2. The simulation’s `purity` and `von_neumann_entropy` columns use a **different convention** than SI (normalization, definition of the state ρ, log base/scaling for entropy, reduced vs full density matrix, etc.).
3. The “filtered” and “broadband” SI conditions are **not represented** in the single CSV `quantum_metrics_evolution.csv` in a way that maps one-to-one to SI.

## Status
- SI values are confirmed (extracted from LaTeX).
- One simulation dataset was extracted at exactly t = 500 fs.
- **Therefore the current mapping cannot validate SI S6 values**, and the audit result is **inconclusive/likely failing** until the correct filtered/broadband simulation datasets (late-March/May only per user request) and metric definitions/conventions are identified.
