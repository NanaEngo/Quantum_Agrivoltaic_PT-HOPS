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
| M8 | Process-model outputs are not paired field outcomes. | Conduct paired open-sun, shade-tree, shade-matched c-Si, and ST-OPV plots at the three sites; record incident/transmitted PAR and spectrum, leaf/canopy temperature, VPD, soil moisture, gas exchange, phenology, disease, marketable yield, and module performance. Pre-register primary endpoints, plot-level replication, exclusions, and analysis. | **Open: field campaign required** |
| M9 | Device and structural assumptions need locally relevant validation. | Obtain independent optical/device checks for the modeled PM6:Y6 stack and local wind/load/contractor evidence for elevated structures, louvers, replacement, and maintenance. Keep laboratory stack validation distinct from field durability and agronomic validation. | **Open: external validation required** |
| M10 | QMC uncertainty summaries may be mistaken for numerical convergence or empirical probabilities. | Report the 10,000-base-sample Saltelli/Jansen setup as conditional model uncertainty, not a real-world frequency. Before upgrading probability language, run independent seeds or convergence/subsample diagnostics and provide uncertainty intervals for exceedance probabilities and Sobol indices. | **Open: additional analysis required** |
| M11 | Reproducibility is not yet equivalent to independent reproducibility. | Release an immutable, versioned archive with source, exact environment lock, input data/provenance/licences, seeds, commands, generated tables/figures, and checksums; include a one-command reproduction path. A repository alone is not a durable archival DOI. | **Open: archive/release required** |
| M12 | Journal-specific submission compliance is not closed. | Fetch and follow the current *Renewable Energy* Guide for Authors; then create the upload checklist, verify declarations, highlights, graphical abstract requirements, source/PDF packaging, corresponding-author details, and ORCID. | **Open: pre-submission gate** |
| M13 | Adversarial review records may be stale and defenses may not match the final package. | Reconcile `docs/Adversarial_Stress_Test_Reviewer_Kill_Scenarios.md` against the current title, main text, SI, and data. Run separate BMAD adversarial and edge-case passes, followed by structure/prose editing and a verification-gap pass where a code or data change warrants one. Record only findings with exact locations and evidence; do not claim BMAD tooling was run unless it was. | **Open: final independent review** |

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

1. **Weather-year counterfactuals** — done. WP3 re-run for 2014–2023 (SM S9.1 decade table with min/median/max, seasonal ranges; report §3.4; main text qualification of Penja as baseline-specific, 7/10 years). Validation protocol now explicit as SM §S9.3 (paired-plot design, measured variables, analysis criteria); paired field trials remain external (M8).
2. **Economic headline qualification** — done. Accepted-export accounting (SM §S9.2, report §4.4): NPV reported at $f_{\rm exp}=1/0.5/0$ with the 50%-acceptance collapse (271–392k USD/ha) stated as an accounting sensitivity, not a physical operating condition; NPV kept as an operating case, not a universal crop NPV; no claim that ST-OPV creates energy value by itself.
3. **Claim-to-evidence boundary** — done. `docs/DATA_ANALYSIS_REPORT_20261113.md` rev.3 is the claim-to-evidence register (M4); scenario robustness limited to tested perturbations.
4. **Decision relevance vs scientific novelty** — done. New main §4.5 "Decision map: when ST-OPV is defensible" with `tab:decision_map` (four axes: decade yield, shade-nearest OPV–c-Si contrast, offtake NPV at three export fractions, LCA break-even 7.40–8.12 yr → unfavorable/conditional/conditional verdicts) and a one-sentence decision rule; former §4.5 Limitations renumbered §4.6 (sections carry no labels, renumbering is safe).
5. **Publication-grade release** — partial. `docs/environment_lock_MesoHOP-sim.yml` added (pinned deps); weather/WP3 manifests with SHA-256 checksums and reproduction instructions already in SM §S9; versioned Zenodo DOI archive remains external (open).
6. **Title/framing** — assessed, no change needed. The title already leads with ST-OPV ("Cameroon Tri-Crop ST-OPV Agro-Photovoltaics…"); "quantum agrivoltaics" as a brand appears nowhere; the quantum result is bounded to a decoupling limit in the abstract, one Results subsection, and one Discussion sentence; cover letter and highlights use "quantum-channel contribution" / "open-quantum channel". T80* 16.33/31.27 yr and $15/m² thresholds were excluded from the decision map because they are untraceable to any package artifact (standing no-unverified-numbers rule).
