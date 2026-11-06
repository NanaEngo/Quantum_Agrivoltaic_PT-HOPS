# Submission Package — Solar Energy (Elsevier), V2611

Retarget of Paper 2 (Quantum Agrivoltaic Digital Twin): declined the Nature Energy editor's transfer suggestion (APC-carrying), submitted to Applied Energy (rejected 2026-11), retargeted here to *Solar Energy* — Q1, subscription route, **no APC**. Built from the Applied Energy package on 2026-11-06 with the interpretive refinement R1–R8 applied (proposal and evidence register: `../docs/REFINEMENT_INTERPRETIVE_20261106.md`).

## Contents

SolarEnergy_main_V2611.tex : elsarticle (preprint, 12pt), numbered bibliography (elsarticle-num). Inherits the full AE-era audit chain (numeric consistency, reviewer-round M1–M21, triple-reading Tier-1 fixes) **plus the 2026-11-06 interpretive patch**: argument-first abstract (trade-off law spine), photon-allocation ledger + land-use pointer in §3.1, SERS utility arithmetic vs EPA benchmarks (§3.4), microclimate benchmark ¶ (§3.5), TEA positioning ¶ (§3.6), BB84 threat-model honesty ¶ (§3.7), Discussion subsections "Exposure to the coherence controversy" and "What would change our conclusions", barrier-ranked Conclusions. Page count: rebuild pending (was 19 pp pre-patch).

SolarEnergy_SM_V2611.tex : "Supplementary Material" (Elsevier terminology). **27 pp** before the 2026-11-06 additions (land-use ledger LER ≈ 1.43; 5-yr OPV replacement-cycle durability stress test in SI-sec:socioeconomic) — rebuild pending.

SolarEnergy_Cover_letter.tex : 1 page; novelty, audience/fit for *Solar Energy*, significance, language-edited statement, reviewer availability.

Highlights_V2611.txt : 5 bullets, ≤ 85 chars each, trade-off-law lead, no first-ever claims.

figures/Graphical_Abstract_wide.png : 2048×1024 wide canvas (AE-compliant format; reuse for SE upload — confirm SE size rules at upload).

verify_acceptance.py : package acceptance audit (V2611 constants + interpretive canon checks). Run from this directory:
`~/miniforge3/bin/conda run -n MesoHOP-sim python verify_acceptance.py`

## Numerical canon (2026-09-23 — validated against raw HPC data; unchanged by the V2611 retarget)

**Φ_FT = Γ_RC ∫ (P₃ + P₄) dt — NO prefactor 2** (Eq. 3 and SI Eq. S1). Validated by reproducing the June-2026 HPC runs (0.0768 / 0.0803 / 0.1685) from raw trapped_pop; the July-2026 scan_A* runs stored rc_yield = 2 × Φ_FT (double-counting bug, now fixed in ../src/orchestrator.py and ../src/digital_twin.py). See §16 of the implementation plan for the full evidence.

Canonical NPoM yield at V_mode = 1.2 nm³: **0.0799** (−91.8 % vs passive).

Γ_RC = 0.15 **fs⁻¹** effective (τ_trap ≈ 6.7 fs) — corrected 2026-09-25 from the printed "0.15 ps⁻¹", which contradicted Eq. (3) (bound 0.15).

Economic chain re-derived 2026-09-25, audited 2026-09-26: water credit **460 L/m²/yr** (1.26 mm/day × 365; ET open 4.51 − shield 3.25 mm/day at Rn = 14.05 MJ/m²/day, f_shade = 0.41 = GCR(1−τ_AVT)); electricity **180 kWh/m²/yr** guaranteed-yield account (revenue = carbon); **NEB_A = 72.6** / NEB_B = 84.2 kgCO₂e/m²/yr; Scenario B biomass **8.2** (0.8 × 0.98/0.95); revenue **30 075 USD** (fertilizer stream excluded), paybacks **4.32 / 6.17 / 2.68 yr**, NPV **+34 630 USD**, carbon credits **363 USD/yr (1.4 %)**.

No coherence-derived crop gain is monetized: crop production is the horticultural standard (8.2 kg/m²/yr) + quantum-fertiliser channel only (0.96 kg/m²/yr, Scenario A).

**Do not use July-2026 scan_A\* HDF5 rc_yield values raw** — divide by 2 or re-run with the corrected code.

## V2611 evidence canon (added 2026-11-06 — no number/DOI enters the text unless registered)

New citations, all OpenAlex/Crossref-verified: Duan2017 (PNAS 114:8493, coherence reassessment anchor), Stallknecht2023 (Sci. Rep. 13:1903, PAR-transmittance design rule), Zhang2018 + Kettle2022 (outdoor OPV lifetime bounds), RandleBoggis2026 (Appl. Energy 423:128450, East-Africa TEA comparator), Vernier2026 (Agric. For. Meteorol. 390:111502, canopy-temperature moderation), Xu2017 (JAFC 65:6719, SERS pesticide LODs), Aquina2025 (IACR ePrint 2025/173, QKD-vs-PQC), EPA2021 (@Misc, imidacloprid chronic benchmark 500 µg/L). Derived quantities published in SM: LER ≈ 1.43 (0.68 × 0.75 indices) and the 5-yr replacement stress test (footprint ×4, NEB 72.6 → 47.1).

Submission route: subscription (no APC). Replies to Dr T. Xiang stay private; Paper 1 SI correction lives in ../../Redac_Paper1/JPCL_Submission_Package_2026-06-20/SI_JPCL_26-06-20_CORRECTED.tex.
