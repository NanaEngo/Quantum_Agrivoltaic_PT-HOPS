# Mitigation Plan: From a Strong Submission to a Reference Article

**Date:** 2026-11-13  
**Scope:** `Submission_Package_RenewableEnergy_Manuscript/`, Paper 2, target journal *Renewable Energy*  
**Evidence baseline:** `parameters.yaml` v2.5.0, WP1–WP6 package artifacts, and the manuscript/SI as present on 2026-11-13.

This is an evidence-led improvement plan, not a prediction of acceptance. The package is a multi-domain, model-based study; a “reference article” standard requires unusually clear decision logic, transparent system boundaries, independently testable claims, and a reproducible validation path. No field measurements or external validation are represented as completed unless the cited artifact demonstrates them.

## Central thesis to preserve

The paper’s strongest contribution is a **conditional deployment-screening framework** for tropical semi-transparent agrivoltaics: seasonal shade–water–radiation trade-offs determine crop compatibility; the cooperative load/export boundary determines financial outcomes; current ST-OPV spectral selectivity does not materially improve matched-shade crop performance; and the bounded CW quantum contribution is negligible at the modeled deployment scale. The result is not that ST-OPV universally wins. In the baseline comparison, elevated c-Si often retains higher NPV, coffee and tea can incur annual yield penalties, and Penja pepper’s advantage is small and climate-sensitive.

Keep this hierarchy visible throughout the abstract, introduction, results, discussion, figures, and cover letter. Avoid adding more domains or describing a conditional counterfactual as an observed deployment result.

## Mitigation register

| ID | Risk / opportunity | Required mitigation | Status |
|---|---|---|---|
| M1 | Seasonal-stress prose overstated the robustness of the pepper OPV–c-Si ranking. The saved WP3b output gives +1.38 percentage points under warm–dry stress but −0.05 points under cool–cloudy stress. | Correct the data report and explicitly describe the cool–cloudy result as a near-tie sign reversal. Preserve the stronger coffee/tea ranking statement only where supported. Add a regression test against the JSON output. | **Done in this pass** |
| M2 | Louver result could be misread as only a monsoon-period PV loss. | State that modeled annual PV generation falls by 38.0–39.9% for the three ST-OPV cases; retain SI wording that reports annual electricity-revenue loss. Distinguish agronomic rescue from the resulting NPV loss. | **Done in this pass** |
| M3 | Per-hectare economic functional unit and cooperative-scale factory loads invite a scale-matching objection. | State that NPV is per hectare of installed array; factory demand is scaled from the stated cooperative catchment and allocated per array hectare; surplus electricity is assumed exportable at the modeled tariff. Call this a modeled accounting/interconnection boundary, not a physically demonstrated energy-sharing arrangement. Do not change cashflows without new evidence. | **Done in this pass** |
| M4 | “Falsifiable” and “outperform” can imply a stronger empirical test or a single ranking across non-equivalent outcomes. | Describe results as model-based, testable counterfactual hypotheses; state comparisons separately for crop yield, LER, array NPV, and carbon intensity, with shade-matched OPV–c-Si comparisons identified. | **Done in this pass** |
| M5 | Conclusions generalize Penja trellis findings to other species and regions without data for those systems. | Recast other trellis crops and regions as candidates for screening and validation, not established beneficiaries; keep Cameroon results conditional on the modeled crops, sites, 2023 forcing, parameterization, and scenarios. | **Done in this pass** |
| M6 | The central result is obscured by the number of coupled methods and secondary metrics. | Use the central thesis above as the contribution hierarchy. In any later revision, prioritize the seasonal regime map, matched-shade comparison, and explicit economic boundary; keep the quantum result as a bounded scale-separation result rather than a parallel claim of agricultural quantum enhancement. | **Editorial rule; apply in all future revisions** |
| M7 | One weather year and literature-calibrated plant/hydraulic parameters limit external validity. | Before making climatological claims, add multi-year weather forcing and site-specific soil, canopy, and flux measurements, or narrow the claim to the 2023 ERA5 baseline plus stated synthetic stresses. The current package supports the latter only. | **Open: new data/analysis required** |
| M8 | Process-model outputs are not paired field outcomes. | Conduct paired open-sun, shade-tree, shade-matched c-Si, and ST-OPV plots at the three sites; record incident/transmitted PAR and spectrum, leaf/canopy temperature, VPD, soil moisture, gas exchange, phenology, disease, marketable yield, and module performance. Pre-register primary endpoints, plot-level replication, exclusions, and analysis. | **Protocol pre-registered 2026-11-14**, campaign not started: `docs/FIELD_VALIDATION_PROTOCOL_20261114.md` (four arms, paired estimands E1–E4, instrument list, analysis plan, exclusions, decision rule) + SM §S7.4. Replication tabled against assumed plot SD, because the model cannot supply field variance; at σ_d = 3 pp a 16-plot design cannot resolve the modelled 1.05 pp contrast. **No field data exist** |
| M9 | Device and structural assumptions need locally relevant validation. | Obtain independent optical/device checks for the modeled PM6:Y6 stack and local wind/load/contractor evidence for elevated structures, louvers, replacement, and maintenance. Keep laboratory stack validation distinct from field durability and agronomic validation. | **Specified 2026-11-14, measurements still absent**: `docs/DEVICE_STRUCTURAL_VALIDATION_REGISTER_20261114.md` + executed fabrication-tolerance audit (`data/wp2/wp2_device_tolerance.json`, 4000 draws) and site wind screening (`data/wp1/wind_load_screening.json`), SM §S7.1–S7.3. Acceptance criteria now numeric (APT ±2.3 pp, PCE ±0.44 pp, LUE ±1.3 %). No independent measurement, tender, or design load exists |
| M10 | QMC uncertainty summaries may be mistaken for numerical convergence or empirical probabilities. | Report the 10,000-base-sample Saltelli/Jansen setup as conditional model uncertainty, not a real-world frequency. Before upgrading probability language, run independent seeds or convergence/subsample diagnostics and provide uncertainty intervals for exceedance probabilities and Sobol indices. | **Done 2026-11-14**: resolution ladder (N = 1250–10 000) × three scrambles, SM §S4.2 + `tab:sobol_convergence`, `scripts/wp5c_sobol_convergence.py`, regression test |
| M11 | Reproducibility is not yet equivalent to independent reproducibility. | Release an immutable, versioned archive with source, exact environment lock, input data/provenance/licences, seeds, commands, generated tables/figures, and checksums; include a one-command reproduction path. A repository alone is not a durable archival DOI. | **Local part done 2026-11-14** (`docs/RELEASE_MANIFEST_20261114.md`, `docs/CHECKSUMS_SHA256.txt`, `scripts/make_release_manifest.py`); Zenodo DOI deposit remains external |
| M12 | Journal-specific submission compliance is not closed. | Fetch and follow the current *Renewable Energy* Guide for Authors; then create the upload checklist, verify declarations, highlights, graphical abstract requirements, source/PDF packaging, corresponding-author details, and ORCID. | **Checklist done 2026-11-14** (`docs/CHECKLIST_UPLOAD_RenewableEnergy_20261114.md`, plain-text highlights added). Two hard gates remain author decisions: 72 references vs reported limit 50, ≈7 500 body words vs 4 000–6 000. ORCID, funding statement and graphical abstract still missing |
| M13 | Adversarial review records may be stale and defenses may not match the final package. | Reconcile `docs/Adversarial_Stress_Test_Reviewer_Kill_Scenarios.md` against the current title, main text, SI, and data. Run separate BMAD adversarial and edge-case passes, followed by structure/prose editing and a verification-gap pass where a code or data change warrants one. Record only findings with exact locations and evidence; do not claim BMAD tooling was run unless it was. | **Register reconciled and one internal pass run 2026-11-14**: `docs/ADVERSARIAL_PASS_20261114.md` records eight findings with evidence, five fixed (stack thicknesses and design grid, k_RC ceiling contradiction, ratio definition, Fig. 4 caption, stale section numbers). A second stage then ran the BMAD `bmad-review` skill with its `adversarial` and `edge-case-hunter` lenses over the staged manuscript and SM (`docs/BMAD_REVIEW_20261114.md`): 14 + 9 findings, 17 fixed in text or captions, one refused and five recorded as stated scope boundaries. Both passes are **internal, not independent** — they were run by the agent that wrote the text — so an independent review remains outstanding. The pre-emptive reviewer reply is `docs/RESPONSE_TO_REVIEWERS_PREEMPTIVE_20261114.md` |

## Implemented corrections in this revision

1. Corrected the WP3b stress interpretation: the Penja pepper OPV–c-Si contrast changes sign between the two synthetic climate stresses and is nearly zero under cool–cloudy forcing.
2. Corrected the S6 cost description to annual PV generation loss and retained the distinction between seasonal yield rescue and lower modeled NPV.
3. Clarified the per-array-hectare financial unit and cooperative-catchment load/export assumption in the manuscript.
4. Reframed the research questions to separate endpoints and limited “falsifiable” language to model-testable hypotheses.
5. Recast cross-species and cross-region transfer as future validation, not a demonstrated result.
6. Added a regression test that reads the WP3b source JSON and checks the documented stress-ranking reversal.
7. Repaired the package Makefile’s migrated absolute Python path, removed the dead HPC sync target from its help interface, and aligned `make test` with the actual pytest suite.

## Verification completed in this pass

- `make check test` in `MesoHOP-sim`: configuration checks **10/10 blocks and 8/8 datasets pass**; **28 pytest tests pass**.
- `latexmk` compilation of `RE_main_2611.tex`, `RE_SM_2611.tex`, `RE_Cover_letter_2611.tex`, and `RE_Highlights_2611.tex`: **21, 6, 1, and 1 pages**, respectively; final logs contain no LaTeX errors, undefined references, or undefined citations.
- Builds were written under `/tmp/opencode/re-validation`; no generated PDFs or auxiliary build products were added to the package.
- These checks establish package consistency and buildability only. They do not substitute for field validation, multi-year climate robustness, independent replication, or the submission gates listed below.

## Stop conditions before submission

- Every numerical statement in the manuscript, SI, and report agrees with its primary artifact; no scenario ranking is called robust where a tested perturbation reverses it.
- NPV’s functional unit, catchment load allocation, export assumption, and physical boundary are explicit and consistent in Methods, tables, captions, and conclusions.
- Model validation is scoped to the component actually validated; no coupled crop/field validation is implied by an optics or quantum benchmark.
- The model-based limitation and need for paired field validation remain explicit.
- Full package tests and all LaTeX builds pass; citations and cross-references resolve.
- Current *Renewable Energy* author instructions, upload checklist, ORCID, and a durable data/code archive are completed or explicitly accepted as submission limitations.

## Applied workflow

This mitigation uses the academic-research quality gates (contribution, technical soundness, writing, experimental rigor, ethics/reproducibility) and LaTeX integrity checks. BMAD lens concepts are used as a staged checklist: adversarial claims/omissions, edge cases and boundary conditions, then structure/prose, followed by verification of changed claims. This document does not claim an official BMAD review run or replace independent domain-expert review.

## SuggestionsV261114 implementation (2026-11-14)

All six items from `docs/SuggestionsV261114.md` (repo root) implemented or assessed:

1. **Weather-year counterfactuals** — done. WP3 re-run for 2014–2023 (SM §S6.1 decade table with mean/SD/range and positive-year counts; report §3.4; main text qualification of Penja as baseline-specific, 7/10 years). Validation protocol now explicit as SM §S7.4 plus `docs/FIELD_VALIDATION_PROTOCOL_20261114.md` (four-arm paired layout, measured variables, computed replication, decision rule); paired field trials remain external (M8).
2. **Economic headline qualification** — done. Accepted-export accounting (SM §S6.2, report §4.4): NPV reported at $f_{\rm exp}=1/0.5/0$ with the 50%-acceptance collapse (271–392k USD/ha) stated as an accounting sensitivity, not a physical operating condition; NPV kept as an operating case, not a universal crop NPV; no claim that ST-OPV creates energy value by itself.
3. **Claim-to-evidence boundary** — done. `docs/DATA_ANALYSIS_REPORT_20261113.md` rev.3 is the claim-to-evidence register (M4); scenario robustness limited to tested perturbations.
4. **Decision relevance vs scientific novelty** — done. New main §4.5 "Decision map: when ST-OPV is defensible" with `tab:decision_map` (four axes: decade yield, shade-nearest OPV–c-Si contrast, offtake NPV at three export fractions, LCA break-even 7.40–8.12 yr → unfavorable/conditional/conditional verdicts) and a one-sentence decision rule; former §4.5 Limitations renumbered §4.6 (sections carry no labels, renumbering is safe).
5. **Publication-grade release** — partial. `docs/environment_lock_MesoHOP-sim.yml` added (pinned deps); weather/WP3 manifests with SHA-256 checksums and reproduction instructions already in SM §S6; versioned Zenodo DOI archive remains external (open).
6. **Title/framing** — assessed, no change needed. The title already leads with ST-OPV ("Cameroon Tri-Crop ST-OPV Agro-Photovoltaics…"); "quantum agrivoltaics" as a brand appears nowhere; the quantum result is bounded to a decoupling limit in the abstract, one Results subsection, and one Discussion sentence; cover letter and highlights use "quantum-channel contribution" / "open-quantum channel". T80* 16.33/31.27 yr and $15/m² thresholds were excluded from the decision map because they are untraceable to any package artifact (standing no-unverified-numbers rule).

## Second mitigation pass (2026-11-14): M10, M11, M12, M13 and manuscript typography

**M10 — estimator stability (closed).** `scripts/wp5c_sobol_convergence.py` re-estimates the
published decomposition on a resolution ladder (N = 1250, 2500, 5000, 10 000) crossed with three
scrambles (seeds 42, 1234, 2024) for all three crops, writing
`data/wp5/wp5_sobol_convergence.json`. Module CAPEX remains the leading hardware driver at every
rung and under every scramble; the three hardware indices move by at most 0.007 between the
coarsest rung and N = 10 000, and the exceedance probability by at most 0.6 percentage points
between scrambles. Reported in SM §S4.2 (`tab:sobol_convergence`), in the main-text Sobol
paragraph, and in `DATA_ANALYSIS_REPORT_20261113.md` §4.3b; guarded by
`test_sobol_convergence_and_seed_stability`. The intervals are described as sampling diagnostics,
never as confidence intervals or probabilities of future outcomes.

**M11 — archive (local part closed, DOI external).** `scripts/make_release_manifest.py` emits
SHA-256 checksums for the 133 files that determine a reported number or a compiled page
(`docs/CHECKSUMS_SHA256.txt`), and `docs/RELEASE_MANIFEST_20261114.md` records the one-command
reproduction path, the environment lock, seeds, and the residual licence/provenance gaps. A Zenodo
deposit with a DOI cannot be created from this repository and remains open.

**M12 — submission compliance (checklist closed; two hard gates open).**
`docs/CHECKLIST_UPLOAD_RenewableEnergy_20261114.md` maps every retrieved requirement to a measured
package state. The Guide for Authors page returns HTTP 403 to automated retrieval, so its wording
was transcribed from indexed excerpts and the checklist states that each line must be re-read in a
browser at upload time. Findings that are formatting and were fixed here: highlights rewritten as
5 bullets of 67–80 plain characters in `RE_Highlights_2611.txt` for the separate editable file.
Findings that are scientific scope decisions and were therefore **not** resolved unilaterally: 72
references against a reported maximum of 50, and ≈7 500 body words against a reported
4 000–6 000. A funding statement, ORCID iDs and a graphical abstract are still missing.

**M13 — adversarial register (reconciled; independent pass still open).** A dated appendix in
`docs/Adversarial_Stress_Test_Reviewer_Kill_Scenarios.md` maps eight stale statements (old working
title, Modified-Redfield/48-mode chemistry, MesoHOPS N = 32, "parameterized directly from field
trials", APT > 65 % pepper optimum, 90 % daytime coffee load, LUE 2.5–4.2 %, "2D regime maps" as
the only regime product) to the values now in the manuscript, and adds the three objections raised
after Revision 3 that the register did not answer (export monetisation, single weather year,
estimator stability). No BMAD tooling run is claimed.

**Manuscript typography and prose (this pass).** Normalised in `RE_main_2611.tex` and
`RE_SM_2611.tex`:

- `cleveref` everywhere: three bare `\ref` uses replaced (including `Supporting Material~\ref` →
  `\cref`), and three redundant `Table~\cref` / `Table~\ref` constructions removed so cross-document references
  print "Table S9"/"Section S3" once, not twice.
- `siunitx` everywhere: three `[\num{a},\num{b}]\,\unit{...}` interval idioms inside math replaced
  by `\qtyrange`, the two `30--35\%` escapes replaced by `\qtyrange{30}{35}{\percent}`, the switch
  uncertainty re-expressed as `\qty{\pm 0.21}{\percent}`, `\DeclareSIUnit\pp` declared in both
  preambles, and every unformatted table number in SM §S6 converted to `\num`/`\numrange`.
- `physics`: `\abs`/`\dd` retained, with the siunitx `\qty` override kept as
  `\AtBeginDocument{\RenewCommandCopy\qty\SI}` in both files.
- `xr`: both documents now resolve cross-references in both directions; the SM bibliography was
  moved behind §S6 (it previously printed before §S5 and §S6).
- Prose: the report-style mitigation paragraphs were rewritten as argumentative scientific prose
  with every number, hedge and claim preserved; "Crucially" and two "quantum leverage"
  formulations removed from the manuscript and "Crucially"/"Furthermore" from the cover letter.

**Verification after this pass.** `make check test`: configuration 10/10 blocks and 8/8 datasets,
**33/33 pytest tests**. `latexmk` on both documents in a shared output directory: **22 pp** main,
**8 pp** SM, 1 p cover letter and 1 p highlights, with zero LaTeX errors, zero undefined references
and zero undefined citations. These checks establish internal consistency and buildability only;
M8 (paired field campaign), M9 (device and structural validation), the independent adversarial
pass, and the DOI deposit remain open.
