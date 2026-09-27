# Submission Package — Applied Energy (Elsevier)

Retarget of Paper 2 (Quantum Agrivoltaic Digital Twin) after the Nature Energy editor's transfer suggestion was declined (transfer journal carried an APC; targeting a Q1 journal with a good IF and no APC for Cameroon).

## Contents

AppliedEnergy_main_2609.tex : converted to elsarticle (preprint, 12pt), numbered bibliography (elsarticle-num), elsarticle frontmatter. Audited & refined 2026-09-23 (see Implementation_Plan_AppliedEnergy_260923.md §12–§16): numeric-consistency audit, horticulture-only scenario (tomato benchmark removed), condensed "Experimental testability" subsection + benchmark table (from the QST package),   PQC-vs-BB84 justification in Limitations. **19 pp** (condensed 2026-09-27), 0 error, 0 undefined references (audited 2026-09-26: reviewer round M1–M21 applied; triple-reading Tier-1 fixes 2026-09-27).

AppliedEnergy_SM_2609.tex : "Supplementary Material" (Elsevier terminology, retitled 2026-09-23; not "Supporting Information"). **27 pp**, 0 error.

AppliedEnergy_Cover_letter.tex : 1 page, structured on the 5 questions required by the AE Guide for Authors (novelty, audience, importance, native-speaker check, reviewer availability).

Highlights_AppliedEnergy.txt : 5 bullets, ≤ 85 chars each.

figures/Graphical_Abstract_wide.png : 2048×1024 AE-compliant wide canvas — the file to upload (the non-compliant square sources were removed in the 2026-09-26 cleanup).

## Numerical canon (2026-09-23 — validated against raw HPC data)

**Φ_FT = Γ_RC ∫ (P₃ + P₄) dt — NO prefactor 2** (Eq. 3 and SI Eq. S1). Validated by reproducing the June-2026 HPC runs (0.0768 / 0.0803 / 0.1685) from raw trapped_pop; the July-2026 scan_A* runs stored rc_yield = 2 × Φ_FT (double-counting bug, now fixed in ../src/orchestrator.py and ../src/digital_twin.py). See §16 of the implementation plan for the full evidence.

Canonical NPoM yield at V_mode = 1.2 nm³: **0.0799** (−91.8 % vs passive).

Γ_RC = 0.15 **fs⁻¹** effective (τ_trap ≈ 6.7 fs) — corrected 2026-09-25 from the printed "0.15 ps⁻¹", which contradicted Eq. (3) (bound 0.15).

Economic chain re-derived 2026-09-25, audited 2026-09-26: water credit **460 L/m²/yr** (1.26 mm/day × 365; ET open 4.51 − shield 3.25 mm/day at Rn = 14.05 MJ/m²/day, f_shade = 0.41 = GCR(1−τ_AVT)); electricity **180 kWh/m²/yr** guaranteed-yield account (revenue = carbon); **NEB_A = 72.6** / NEB_B = 84.2 kgCO₂e/m²/yr; Scenario B biomass **8.2** (0.8 × 0.98/0.95); revenue **30 075 USD** (fertilizer stream excluded), paybacks **4.32 / 6.17 / 2.68 yr**, NPV **+34 630 USD**, carbon credits **363 USD/yr (1.4 %)**.

No coherence-derived crop gain is monetized: crop production is the horticultural standard (8.2 kg/m²/yr) + quantum-fertiliser channel only (0.96 kg/m²/yr, Scenario A).

**Do not use July-2026 ****scan_A***** HDF5 ****rc_yield**** values raw** — divide by 2 or re-run with the corrected code.



Submission route: subscription (no APC). Replies to Dr T. Xiang stay private; Paper 1 SI correction lives in ../../Redac_Paper1/JPCL_Submission_Package_2026-06-20/SI_JPCL_26-06-20_CORRECTED.tex.
