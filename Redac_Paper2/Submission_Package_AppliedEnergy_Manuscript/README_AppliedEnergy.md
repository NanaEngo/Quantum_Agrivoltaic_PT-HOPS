# Submission Package — Applied Energy (Elsevier)

Retarget of Paper 2 (Quantum Agrivoltaic Digital Twin) after the Nature Energy
editor's transfer suggestion was declined (transfer journal carried an APC;
targeting a Q1 journal with a good IF and no APC for Cameroon).

## Contents

- `Manuscript_AppliedEnergy_260923.tex` : converted to `elsarticle`
  (preprint, 12pt), numbered bibliography (`elsarticle-num`), elsarticle
  frontmatter. Audited & refined 2026-09-23 (see
  `Implementation_Plan_AppliedEnergy_260923.md` §12–§16): numeric-consistency
  audit, horticulture-only scenario (tomato benchmark removed), condensed
  "Experimental testability" subsection + benchmark table (from the QST
  package), PQC-vs-BB84 justification in Limitations. 35 pp, 0 error,
  0 overfull.
- `SI.tex` : "Supplementary Material" (Elsevier terminology, retitled
  2026-09-23; not "Supporting Information"). 24 pp, 0 error, 0 overfull.
- `Cover_Letter_AppliedEnergy.tex` : 1 page, structured on the 5 questions
  required by the AE Guide for Authors (novelty, audience, importance,
  native-speaker check, reviewer availability).
- `Highlights_AppliedEnergy.txt` : 5 bullets, ≤ 85 chars each.
- `figures/Graphical_Abstract_wide.png` : 2048×1024 AE-compliant wide
  canvas — the file to upload (replaces non-compliant square
  `Graphical_Abstract.png`; `Graphical_Abstract_fixed.png` is the
  label-repaired square source).

## Numerical canon (2026-09-23 — validated against raw HPC data)

- **Φ_FT = Γ_RC ∫ (P₃ + P₄) dt — NO prefactor 2** (Eq. 3 and SI Eq. S1).
  Validated by reproducing the June-2026 HPC runs (0.0768 / 0.0803 / 0.1685)
  from raw `trapped_pop`; the July-2026 `scan_A*` runs stored
  `rc_yield = 2 × Φ_FT` (double-counting bug, now fixed in
  `../src/orchestrator.py` and `../src/digital_twin.py`). See §16 of the
  implementation plan for the full evidence.
- Canonical NPoM yield at V_mode = 1.2 nm³: **0.0799** (−91.8 % vs passive).
- Quantum gain: **15 %** (economic chain 1.23 kg/m²/yr → 5.5 $/m²/yr →
  payback 4.23 yr with 30 % subsidy).
- Water credit 650 m³/yr derives from the 1300 L/m²/yr credit (SI S5), not
  from raw ΔETc.
- **Do not use July-2026 `scan_A*` HDF5 `rc_yield` values raw** — divide by 2
  or re-run with the corrected code.

Submission route: subscription (no APC). Replies to Dr T. Xiang stay private;
Paper 1 SI correction lives in
`../../Redac_Paper1/JPCL_Submission_Package_2026-06-20/SI_JPCL_26-06-20_CORRECTED.tex`.
