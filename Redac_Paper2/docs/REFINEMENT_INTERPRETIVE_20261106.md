# Paper 2 Refinement — Inverting Description → Interpretation

**Date:** 2026-11-06 · **Target file:** `Submission_Package_AppliedEnergy_Manuscript/AppliedEnergy_main_2609.tex`
**Directive:** "paper 2 is more descriptive than interpretative. We shall reverse that" (user, 2026-11-06), executed per `~/skills` scientific-writing · scientific-critical-thinking · peer-review · deep-research workflows, after a seven-stream web search (Nov 2026).

**Method.** Interpretation = *mechanism* (why the numbers arise) + *comparison* (against measured field/industry baselines) + *implication* (what a reader would decide differently) + *falsification* (what observation would overturn it). The audit below flags where Results/Discussion stop at inventory and specifies the minimum interpretive move, each bound to verified web evidence (§E).

---

## 0. Diagnosis (section-level audit)

| Location | Present mode | Verdict |
|---|---|---|
| Intro "value chain" ¶ (L130) | interpretive | **Model to emulate** — argumentative, not inventory |
| F1–F3 falsifiable claims (L121–127) | interpretive | good spine; needs §E anchoring (below) |
| Canopy integration (L162–171) | interpretive | "accounting identity" + design envelope already correct |
| §SERS (L176–177) | **descriptive** | parameters + availability %, no utility argument |
| §Microclimate (L179–180) | **descriptive** | states 28% and 460 L; no "why", no field benchmark |
| §TEA (L182–183) | **descriptive** | three payback numbers, no positioning, no LER |
| §BB84 (L185–186) | **descriptive** | protocol inventory, no threat model |
| §Dynamic photo-protection (L173–174) | borderline | honest, but control law buys nothing yet |
| Discussion (L191–202) | thin | prior-art list exists; no mechanism chain, no coherence-stance |

The abstract (L81) is a *result inventory* — six numbers, zero "so what". The conclusions mirror it. That is the shape to flip.

---

## R1. Take a stance in the 2024–25 coherence reassessment (F1)

**Problem.** L105 says "the functional relevance of these quantum beats remains debated" — then never resolves it. An AE or biophysics-literate reviewer now knows about the 2025 reassessment (electronic coherences dephase in ~50–100 fs at physiological T; the surviving long-lived signals are vibronic/ground-state vibrations). F1 as currently phrased ("extends *exciton coherence* by 50%") risks reading as reliance on a discredited claim.

**Intervention.** Convert the hedge into a *position*: the dual-band mechanism operates on the **vibronic** channel (polaron-dressing, exciton–vibrational dissipation), which is precisely the survivor of the 2024–25 reassessment — so the design benefit is *robust to* the retraction wave rather than threatened by it. One new Discussion paragraph ("Quantum-mechanistic exposure") + one abstract clause ("vibronically assisted"). This strengthens F1 instead of softening it.

**Evidence to bind.** Nat. Commun. 15:3171 (2024, Zhu — already cited ✓); Miller-group PNAS 2017 114:8493 ("Nature does not rely on long-lived electronic quantum coherence") — present in snippet, fetch full bib; "Quantum biology revisited", Sci. Adv. (2025) reanalysis — **fetch exact authors/DOI before citing**; Collison–Scholes 2024 Nature retraction status — optional context, cite only once verified.

## R2. Reconcile the spectral budget explicitly (PAR vs. 750/820 nm)

**Problem.** The abstract/design highlight *transmitting narrow 750–820 nm bands* — crops run on 400–700 nm PAR. The paper never states where the canopy PAR comes from. A plant-scientist reviewer will read "transmit only the photosynthetically active wavelengths" (L101) and then the 750/820 passbands as a contradiction — the single most likely desk-rejection hook in the current text.

**Intervention.** One interpretive paragraph (Results §3.1 or Methods) laying out the **photon allocation ledger**: main OPV module transmits the PAR window for the canopy; the FMO/NPoM dual-band layer harvests only the red-edge/NIR fringe (~10.2 W/m² ≈ 1% of AM1.5G, already reported at L142 — repurpose it as the ledger's quantum line). Then state the design rule from the transparent-AV literature: PAR transmittance is the dominant yield predictor (fruiting-crop targets APT > 65%; pushing the absorption edge past 750 nm reduces yield penalty). Report **LER** for the modeled module (benchmark range 1.2–1.8) — AE's own currency, currently absent.

**Evidence.** Sci Rep 2023 (10.1038/s41598-023-28484-5, plant-transparent AV design); WSPV spectral-sharing review, Cell-affiliated 2024 (S2542435124003726); Tel Aviv APV yield 78%-of-control datum; MDPI 2026 Agronomy Japan AVS TEA (LER 1.2–1.8; DLI constraints govern coverage → links crop-light need to LCOE — perfect bridge for AE).

## R3. Promote the 750/820 passband from physics curiosity to photobiology control channel

**Problem.** The passband sits exactly on the phytochrome switch (R:FR; 660/730 nm window, FR = 700–750). Selectively transmitting 750/820 while attenuating mid-red *shifts the phytochrome photoequilibrium at the canopy* — i.e., the shield modulates shade-avoidance architecture (stem elongation, leaf expansion). The paper is silent on this, missing its best interpretive connection to its own PoC crop: **floriculture**, where stem length is a marketable quality trait.

**Intervention.** Add a short "spectral–physiological coupling" discussion: (i) mechanism (PPE shift direction under our transmittance, computed from the *modeled* band plan), (ii) implication for ornamental stem elongation, (iii) explicit falsifiable add-on to Experimental testability: measure R:FR under the module and PPE-driven traits vs. open field; quantification goes to SM as a band-ratio table (computed from our own transmittance inputs — no external claim). **Do not** assert a yield/stem effect numerically until the table is computed.

**Evidence.** Far-red/phytochrome mechanism (PMC9949677 spectral-conversion review; Pierik & de Wit 2014 cited therein; en.wikipedia "Far-red light" for the 700–750 nm band — prefer primary review for bib).

## R4. Make OPV lifetime the quantified headline barrier, not a bullet

**Problem.** LCA assumes 20-yr service life (L221). Measured OPV reality: outdoor-extrapolated Ts80 ≈ 2.5–6.2 yr; first field *module* studies 2–4.5 months; the current record lab cell ≈ 24,700 h (~16 yr predicted). The Limitations bullet "OPV encapsulation lifetime" (L206) under-sells the paper's most honest claim: even *with* module replacement every ~5 yr, does the stack stay net-positive?

**Intervention.** Recompute NEB/payback with a replacement-cycle scenario (embodied carbon + re-CAPEX every 5 yr, SM tables already supply CAPEX/m² and cradle-to-gate carbon — this is a two-row sensitivity, not new physics). Report: "the multifunctional benefit remains positive if module replacement interval exceeds ___ yr" → converts a weakness into the paper's sharpest *interpretive* contribution, exactly the "which barriers remain physical" question the intro promises (L121) but never answers at this layer.

**Evidence.** Zhang et al., Adv. Sci. 2018 5:1700434 (outdoor lifetime testing; Ts80 6.2 yr & 5000–7000 h sensitivity; cited 144×); Emmott et al., Sol. Energy Mater. Sol. Cells 2016 (in-situ modules, Ts80 2–4.5 months); 2025 Åbo/Aalto record 24,700 h result (fetch primary paper).

## R5. Position the economics against the AV-TEA literature (adopt LER + tornado)

**Problem.** §3.6 lists 4.32 yr / 6.17 yr / 2.68 yr with no benchmark — AE readers ask "compared to what?"

**Intervention.** (i) LER + DLI→coverage→LCOE coupling from the Japan 2026 MDPI Agronomy paper; (ii) regional anchor: **Applied Energy itself just published East-Africa AV TEA + stakeholder analysis (Randle-Boggis et al., Appl. Energy 2026, 128450)** — cite it as the deployment-context comparator, which doubles as a fit signal to the editor; (iii) convert the SI sensitivity into one main-text interpretive sentence naming the dominant lever (subsidy vs. CAPEX vs. water credit) — a tornado reading: "payback stays < 6.17 yr unless ___". Also interpret carbon-revenue share (~1.4%): state plainly that decarbonization value is *avoided-emissions utility*, not revenue — the paper already hints at this (L130); say it in §3.6 too.

## R6. Argue sentinel *utility*, not sentinel parameters

**Problem.** §3.4 reports EFs, soiling decay, ×10 matrix penalty — all engineering of the sensor; nothing about whether it *matters*.

**Intervention.** Frame as surveillance arithmetic: detection limit vs. **action thresholds** (e.g., imidacloprid harm level ~25 ppb EPA vs. demonstrated SERS at 0.4 ppb — two orders of margin; pM–ppt LODs for carbendazim/chlorpyrifos), then coverage: at α=1% sentinel fraction the diagnostics interrogate the module's own runoff/irrigation stream, not every leaf — a *spot-check* whose value is triggering the BB84-signed command loop (§3.7 connects!). The ×10 matrix penalty is no longer arbitrary: it matches the documented field bottleneck (waxy cuticles, humic acids, non-specific adsorption — MDPI Foods 2026 bottlenecks review). Keep DynamicCalibrator numbers; add the *why-it-suffices* paragraph and one falsifiable test (field sap recovery vs. buffer LOD, SM roadmap).

**Evidence.** Atta et al. PMC12794728 (LOD 10–100 pM pesticides); Kim & Barceló nanofinger (35 ppt drinking water); OceanInsight/Spectroscopy app-note (imidacloprid 0.4 ppb vs. 25 ppb EPA level); MDPI Foods 2026 15(17):3152 (lab-vs-field bottlenecks).

## R7. Give BB84 a threat model — or demote it honestly

**Problem.** §3.7 + Methods state the fallback is AES. NSA (June 2026) does not recommend QKD for national-security data transmission absent solved constraints; ANSSI guidance and IACR 2025 critical analyses: QKD ≈ key-agreement with heavy trust/rate caveats; pre-shared keys + AES-GCM win on practicality. Irrigation commands are not HNDL-grade targets *unless* the paper argues why (long-lived agronomic data sovereignty? GQAS pillar?). Current text invites "quantum layer as decoration" — the exact criticism the value-chain ¶ preempts for physics but not for security.

**Intervention.** Two sentences of honest security economics: QKD's marginal value = harvest-now-decrypt-later protection for the cooperative's *decades-lived* hydrological/market telemetry under GQAS data-sovereignty requirements; AES-GCM remains adequate for operational latency. Then *test it*: report the abort-rate and the fail-safe's cost impact (§3.6 already has the CAPEX/OPEX lines — add BB84 as a named cost item with its AES-only counterfactual, which the payback delta then prices). This converts §3.7 from gadget to interpreted claim, consistent with the paper's own F3 style.

**Evidence.** NSA PQC-hub article (2026-06, QKD not recommended); ANSSI "Should QKD be used" (2024/EN); IACR eprint 2025/173 (critical analysis of deployed QKD use cases); Tupkary et al., Rev. Mod. Phys. 98:035003 (2026, practical-proof gaps) — fetch exact titles/DOIs for bib.

## R8. Frame surgery (abstract → conclusions)

- **Abstract**: lead with the *question and the trade-off law* ("diagnostics are bought at 0.9 points of canopy yield per 1% sentinel area; the binding barrier is process engineering, not economics"), then numbers as evidence — currently numbers-as-plot.
- **Results**: every subsection gains a terminal interpretive sentence (R2/R4/R5/R6/R7 above supply theirs). §Dynamic photo-protection: state what the switch *protects* in system terms (passband integrity → crop spectral budget → revenue) and that the yield-level test is SM roadmap — already partly done.
- **Discussion**: add "Mechanism chain" ¶ (vibronic dressing → sentinel confinement → ET/VPD credit → payback) and "**What would change our conclusions**" ¶ (R4 replacement interval, R1 vibronic stance, R3 PPE risk) — the strongest interpretive device available and absent today.
- **Conclusions**: replace the mirrored-inventory with the barrier ranking the intro promised (physical: NPoM gap fab, fouling, encapsulation — with the R4 number; economic: tractable via local materials — already there).

---

## §E. Evidence register (verification status — scientific-writing evidence-binding)

| # | Source | Verified via | Supports | Status |
|---|---|---|---|---|
| E1 | Nat. Commun. 15:3171 (2024) Zhu et al. | URL+snippet ✓ | vibronic coherence sustainment | already cited in MS ✓ |
| E2 | PNAS 2017 114:8493 "Nature does not rely on long-lived…" | OSTI PDF snippet ✓ | electronic coherence dephasing | fetch full author list |
| E3 | "Quantum biology revisited" Sci. Adv. 2025 (MIT/MP/Lund reanalysis) | Zenodo summary ⚠ | 50–75 fs dephasing; vibronic origin | **fetch primary DOI — do not cite from blurb** |
| E4 | Sci. Rep. 2023 s41598-023-28484-5 | snippet ✓ | PAR transmittance dominates yield; APT>65% | cite |
| E5 | Cell Rep. Phys./Joule-affil. 2024 S2542435124003726 | snippet partial | WSPV spectral sharing | fetch title/authors |
| E6 | npj Sustain. Agric. 4:12 (2026) Maruyama | snippet ✓ | field microclimate deltas; −31% yield shade-avoidance | cite |
| E7 | Adv. Sci. 2018 5:1700434 Zhang et al. | snippet ✓ | Ts80 2.5–6.2 yr outdoor extrapolation | cite |
| E8 | Sol. Energy Mater. Sol. Cells 2016 Emmott et al. | snippet ✓ | module Ts80 2–4.5 months | cite |
| E9 | MDPI Agronomy 2026 16(18):1776 (Japan AVS TEA) | snippet ✓ | LER 1.2–1.8; DLI→LCOE coupling | cite |
| E10 | Appl. Energy 2026 128450 Randle-Boggis et al. | repo metadata ✓ | East-Africa AV TEA | cite — regional anchor |
| E11 | PMC12794728 Atta 2024; nanofinger 35 ppt; OceanInsight 0.4 ppb/25 ppb EPA | snippets ✓ | SERS LOD vs action thresholds | cite |
| E12 | MDPI Foods 2026 15(17):3152 | snippet ✓ | SERS matrix bottlenecks justify ×10 | cite |
| E13 | NSA 2026-06 QKD position; ANSSI guide; IACR 2025/173; RMP 98:035003 (2026) | snippets ✓ | QKD threat-model honesty | cite 1–2, not all |
| E14 | PMC9949677 spectral-conversion film (phytochrome/PPE) | snippet ✓ | R:FR mechanism | cite |

**Rule applied:** no number enters the manuscript until its primary source is opened and the bib entry verified (E3/E5 explicitly pending). Fabricated-DOI guard stays active (Session 29 incident).

---

## Suggested minimal patch map

| # | Touch | Size | Value |
|---|---|---|---|
| 1 | Discussion: "Quantum-mechanistic exposure" ¶ (R1) | +1 ¶ | immunizes F1 |
| 2 | Results §3.1: photon-allocation ledger + LER line (R2) | +0.5 ¶ | kills desk-reject hook |
| 3 | §3.5/SM: replacement-cycle NEB rows (R4) | SM table +2 rows, +2 sent. | answers intro's own question |
| 4 | §3.6: TEA positioning (R5) | +2 sent. | AE fit |
| 5 | §3.4: surveillance arithmetic (R6) | +2 sent. | utility claim |
| 6 | §3.7 + Limitations: security economics (R7) | +2 sent. | kills "quantum decoration" |
| 7 | Abstract + Conclusions rewrite (R8) | rewrite 2 blocks | the inversion itself |
| 8 | §3.1/§3.6: R:FR band table in SM (R3) | SM table | photobiology channel |

All edits stay within the existing F1–F3 architecture; nothing here changes the physics inputs, only their interpretation and one SM sensitivity (R4). Re-run `verify_acceptance.py` + PDF build after implementation.
