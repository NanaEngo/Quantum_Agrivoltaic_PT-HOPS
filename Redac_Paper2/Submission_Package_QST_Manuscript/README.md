# Submission Package — Quantum Science and Technology (IOP)

Second-journal package for Paper 2 (Quantum Agrivoltaic Digital Twin), derived
from the Nature Energy base. Target: IOP QST (subscription, $0 APC).

## Contents

- `Manuscript_QST_26-07-29.tex` : main manuscript (20 pp, 0 error,
  0 undefined). Reconciled 2026-09-23 to the corrected-yield canon: Φ_FT
  equation without prefactor 2, Table 2 canonical 7-point volume scan
  (0.0505 → 0.0799, monotone), Φ_global = 0.971, η_shield (1−η) semantics.
  Re-derived 2026-09-25: water credit 460 L/m²/yr (1.26 mm/day × 365),
  revenue 30 075 USD, paybacks 4.32/6.17/2.68 yr, NEB_A 72.6 kgCO₂e/m²/yr.
- `SI.tex` : 30 pp, 0 error. Same reconciliation (0.1599/83.7 % →
  0.0799/91.8 %).
- `Cover_Letter_QST.tex` : 2 pp, EIC, subscription route, 5 suggested
  reviewers.
- `references.bib`, `table_comparative_4runs.tex`,
  `AUDIT_JOURNAL_REFINEMENTS_2026-07-29.md` (audit journal),
  `verify_acceptance.py` (acceptance audit, 22 checks — run
  `python3 verify_acceptance.py`).

The inherited Nature Energy base was removed from this package during the
2026-09-26 cleanup; the reference copy lives in
`../../_archive/Submission_Package_Nature_Energy_Manuscript/` (checked by
check #12 of `verify_acceptance.py`).

## Figures (restored 2026-09-23)

The package was delivered without figure directories (the original PDFs had
been compiled elsewhere). Restored as `figures/` (the `Figures` symlink has
since been removed):

- Main: 4 figures extracted from the original main PDF (git HEAD).
- SI: 2 figures copied from the AE package (Compara 4Runs, NPoM ON vs OFF);
  1 extracted from the original SI PDF (Population Dynamics Local — carries
  no yield annotation, hence no vintage); **2 regenerated**:
  `Figure_SI_NPoM_VolumeScan_n20.png` (via `plot_volume_scan_light.py`,
  corrected from the obsolete hard-coded vintage to the canonical 7-point
  series) and `Figure_SI_Coupling_Regime_Diagram.png` (via new
  `plot_coupling_regime.py`, schematic only, no yield vintage).

## Numerical canon (2026-09-23 — validated against raw HPC data)

- **Φ_FT = Γ_RC ∫ (P₃ + P₄) dt — NO prefactor 2** (Eq. (3) and SI Eq. S1).
  Validated by reproducing the June-2026 HPC runs (0.0768 / 0.0803 / 0.1685)
  from raw `trapped_pop`; the July-2026 `scan_A*` runs stored
  `rc_yield = 2 × Φ_FT` (double-counting bug, now fixed in
  `../src/orchestrator.py` and `../src/digital_twin.py`). Full evidence in
  the AE package `Implementation_Plan_AppliedEnergy_260923.md` §16.
- Canonical NPoM yield at V_mode = 1.2 nm³: **0.0799** (−91.8 % vs passive);
  global canopy yield **0.971**.
- Γ_RC = 0.15 **fs⁻¹** effective (τ_trap ≈ 6.7 fs) — corrected 2026-09-25
  from the printed "0.15 ps⁻¹".
- Water credit **460 L/m²/yr** (1.26 mm/day × 365; corrects the ×365 error
  of the old 1300 L figure); electricity **180 kWh/m²/yr** guaranteed-yield
  account; **NEB_A = 72.6** kgCO₂e/m²/yr; revenue **30 075 USD**, paybacks
  **4.32 / 6.17 / 2.68 yr**, NPV **+34 630 USD**; no coherence-derived crop
  gain monetized.
- **Do not use July-2026 `scan_A*` HDF5 `rc_yield` values raw** — divide by 2
  or re-run with the corrected code.

## Acceptance audit

```bash
python3 verify_acceptance.py   # 22 checks, portable paths
```
