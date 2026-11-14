# BMAD review run — 2026-11-14 (M13, BMAD tooling)

**Skill used:** `bmad-review` (installed from `bmad-code-org/BMAD-METHOD`, `npx skills add … --skill bmad-review`) into
`.agents/skills/bmad-review/`. Lenses run: `adversarial` (`references/lens-adversarial.md`) and `edge-case-hunter`
(`references/lens-edge-case-hunter.md`). Lenses `verification-gap`, `structure`, `prose` were not run.

**Content reviewed:** `RE_main_2611.tex` + `RE_SM_2611.tex`, concatenated and staged as one UTF-8 text file
(`/tmp/bmadrev/content.txt`, 848 lines) before the lenses ran. Class: *docs* (a manuscript and its supporting
material). Review date 2026-11-14; package state after the second mitigation pass.

**Honest scope.** The BMAD lenses were executed as specified — the workflow file, both lens files, the staged-content
step and the findings shapes are the shipped ones. They were **executed by the same agent that wrote the text**, so
this is BMAD *tooling* on an internal pass, not an independent review. M13's "independent adversarial/edge-case pass"
therefore remains open: independence is a property of the reviewer, not of the tool. Claims supplied to the edge-case
lens were the M8/M9/M13 status rows of `docs/OUTSTANDING_REFERENCE_ARTICLE_MITIGATION_PLAN_20261113.md`; those three
claims were checked and **all three survived falsification** (tolerance SDs, zero hours above 10 m/s, 1.05 pp
contrast), so the claims step produced no findings and is not repeated below.

Nothing here is padded: the adversarial lens requires ≥10 findings and produced 14; the edge-case lens produced 9
unhandled paths, all genuine.

---

## Findings (JSON, canonical shape)

```json
[
  {"lens":"adversarial","location":"Abstract, sentence 3","trigger_condition":"'Shapley attribution exposes a seasonal inversion' claims discovery from a deterministic decomposition","guard_snippet":"'a four-lever Shapley decomposition attributes the modelled yield shift to ...'","potential_consequence":"Reviewer reads a causal/observational result where only a model identity is shown"},
  {"lens":"adversarial","location":"Abstract, sentence 4","trigger_condition":"'spectral selectivity adds -0.2 to -0.7 %' states a negative contribution as an addition","guard_snippet":"'spectral and quantum selectivity contributes -0.2 to -0.7 pp'","potential_consequence":"Sign and unit ambiguity in the one sentence most readers will quote"},
  {"lens":"adversarial","location":"sec:res_agro, first sentence","trigger_condition":"'demonstrate a decisive seasonal regime inversion' — a simulation cannot demonstrate a field regime","guard_snippet":"'show, within the modelled canopy, a seasonal sign inversion'","potential_consequence":"Overclaim targeted by any agronomist reviewer"},
  {"lens":"adversarial","location":"tab:lit_matrix, last row","trigger_condition":"'Falsifiable counterfactual test across 5 scales' — the model itself is not falsifiable","guard_snippet":"name the measurement that would falsify it (paired field trial, SM S7.4)","potential_consequence":"Positioning claim with no stated test"},
  {"lens":"adversarial","location":"sec:methods_tmm, tolerance sentence","trigger_condition":"'beam transmittance falls from 44 % at normal incidence to 33 % at 60 deg' mislabels APT as beam transmittance","guard_snippet":"'PAR-averaged transmittance (APT) falls from 44.12 to 33.07 %'","potential_consequence":"Optics reviewer detects a definitional error and distrusts the rest of the optical section"},
  {"lens":"adversarial","location":"sec:res_tmm, opaque benchmark sentence","trigger_condition":"'reproducing the experimental PM6:Y6 benchmark' when PCE is 15.50 vs 16.27 % measured","guard_snippet":"'reproduces it to within 5 % relative (15.50 vs 16.27 %)'","potential_consequence":"A 4.7 % gap described as reproduction invites a rebuttal on model validation"},
  {"lens":"adversarial","location":"sec:res_tea, dispatch paragraph","trigger_condition":"NPV rises 724 075 -> 860 825 USD/ha while IRR falls 38.65 -> 35.52 %, unexplained","guard_snippet":"state that the BESS adds revenue but also raises capex, so NPV up and IRR down","potential_consequence":"Apparent internal inconsistency in the flagship techno-economic result"},
  {"lens":"adversarial","location":"sec:res_tea, abatement sentence","trigger_condition":"393.2 tCO2e/ha/yr net abatement for ~1113 MWh/ha/yr implies ~0.35 tCO2e/MWh without stating the displaced factor","guard_snippet":"report the diesel/grid emission factors used and mark the figure counterfactual","potential_consequence":"Carbon claim looks physically implausible to a lifecycle reviewer"},
  {"lens":"adversarial","location":"sec:res_sobol, first paragraph","trigger_condition":"'in 79-89 % of realizations' describes quasi-Monte-Carlo sample vectors as realizations of a probability model","guard_snippet":"'in 77.0-89.0 % of the sampled parameter vectors'","potential_consequence":"Probabilistic reading of a designed sample, then challenged on representativeness"},
  {"lens":"adversarial","location":"sec:methods_tea, dispatch boundary","trigger_condition":"Off-grid NPV of -379.8 kUSD/ha sits beside standalone p05 of +145 kUSD without noting they are different counterfactuals","guard_snippet":"label the off-grid figure as the no-export case with capex sunk","potential_consequence":"Reader concludes the economics contradict themselves"},
  {"lens":"adversarial","location":"sec:disc_mech, pepper sentence","trigger_condition":"'PGI Penja white pepper has the most favorable rainfed yield response' in present tense while 7/10 years is the evidence","guard_snippet":"'in the 2023 baseline, and in 7 of 10 reanalysis years'","potential_consequence":"Contradiction with the paper's own weather-year qualification"},
  {"lens":"adversarial","location":"sec:disc_mech, trellis crops sentence","trigger_condition":"Black pepper, vanilla and passionfruit named as candidates with no evidence or citation","guard_snippet":"mark explicitly as untested extrapolation","potential_consequence":"Speculative generalisation a reviewer will ask to delete"},
  {"lens":"adversarial","location":"fig:tea_lca caption","trigger_condition":"Caption describes storage sizing but omits the 2 h BESS case that the text reports","guard_snippet":"enumerate no-storage / 2 h / overnight in panel (a)","potential_consequence":"Figure and text disagree on how many configurations exist"},
  {"lens":"adversarial","location":"global: tolerance-audit propagation","trigger_condition":"APT tolerance spread is quantified but never propagated to crop yield or NPV","guard_snippet":"state that stack tolerance enters yield through APT and bound that path, or declare it out of scope","potential_consequence":"Tolerance audit reads as decorative once a reviewer asks what it changes"}
]
```

## Findings (edge-case lens — unhandled paths only)

```json
[
  {"lens":"edge-case-hunter","location":"sec:methods_quantum / eq:ness_bound","trigger_condition":"max |dEta| quoted without stating sign convention for crops","guard_snippet":"state that crops see signed dEta in [-bound,+bound]","potential_consequence":"Widened envelope silently doubles the modelled effect"},
  {"lens":"edge-case-hunter","location":"tab:sm_tolerance","trigger_condition":"thickness draws were truncated (Ag >= 4 nm, cap >= 0 nm) but the caption does not say so","guard_snippet":"report the truncation bounds in the caption","potential_consequence":"Reported spread not reproducible from the stated Gaussians"},
  {"lens":"edge-case-hunter","location":"fig:tea_lca panel (c) / sec:res_tea","trigger_condition":"parity frontier parameterised by module-to-BOS cost ratio, undefined if c-Si BOS cost -> 0","guard_snippet":"state the sampled BOS range (35-85 USD/m2) on the axis","potential_consequence":"Axis endpoint undefined; reader cannot reproduce the frontier"},
  {"lens":"edge-case-hunter","location":"parity thresholds, T80 -> 0","trigger_condition":"T80 appearing in a denominator with no lower bound stated","guard_snippet":"state the frontier is evaluated for T80 >= 1 yr","potential_consequence":"Unbounded replacement capex as T80 -> 0"},
  {"lens":"edge-case-hunter","location":"sec:sm_tmm, angle domain","trigger_condition":"angular average integrated to 80 deg but no statement for theta > 80 deg","guard_snippet":"state the truncation and its effect on the hemispherical average","potential_consequence":"Missing near-grazing contribution unquantified"},
  {"lens":"edge-case-hunter","location":"sec:sm_weather_decade","trigger_condition":"leap years give 8784 hourly samples while statistics say 8760","guard_snippet":"state the per-year sample count used in F_lp and annual sums","potential_consequence":"0.3 % basis mismatch between years"},
  {"lens":"edge-case-hunter","location":"sec:res_agro, heavy-shade case","trigger_condition":"yields reported to -28.1 % with no statement that assimilation stays positive","guard_snippet":"state the lower clamp on daily assimilation","potential_consequence":"Under heavy shade the model could in principle produce negative assimilation"},
  {"lens":"edge-case-hunter","location":"tab:sm_awc_gb_stress","trigger_condition":"AWC swept 120-220 mm but not toward 0 or saturation","guard_snippet":"state why the physical extremes are excluded","potential_consequence":"Water-stress response extrapolated beyond the audited box"},
  {"lens":"edge-case-hunter","location":"sec:res_sobol, zero-carbon variant","trigger_condition":"carbon price = 0 is handled, negative carbon price is not","guard_snippet":"state the sampled carbon range [0,25] USD/tCO2e and that negatives are excluded","potential_consequence":"Reader cannot tell whether a carbon-tax scenario was tested"}
]
```

---

## Disposition in this pass

| # | Lens | Finding | Disposition |
|---|---|---|---|
| A1 | adversarial | "Shapley attribution exposes" | fixed — "attributes the modelled shift" |
| A2 | adversarial | "spectral selectivity adds −0.2 to −0.7 %" | fixed — "contributes … pp" |
| A3 | adversarial | "demonstrate a decisive seasonal regime inversion" | fixed — "show, within the modelled canopy" |
| A4 | adversarial | "falsifiable counterfactual test" | fixed — names the field protocol as the test |
| A5 | adversarial | APT mislabelled as beam transmittance | fixed — APT named |
| A6 | adversarial | "reproducing" a 4.7 % gap | fixed — "to within 5 % relative" |
| A7 | adversarial | NPV up / IRR down unexplained | fixed — one clause |
| A8 | adversarial | abatement factor unstated | fixed — diesel factor and counterfactual flag |
| A9 | adversarial | "realizations" for QMC vectors | fixed — "sampled parameter vectors" |
| A10 | adversarial | off-grid vs standalone counterfactuals | fixed — labelled |
| A11 | adversarial | present-tense pepper claim | fixed — 2023 baseline + 7/10 years |
| A12 | adversarial | untested trellis crops | fixed — "untested extrapolation" |
| A13 | adversarial | Fig. 5 caption omits 2 h case | fixed — three configurations named |
| A14 | adversarial | tolerance never propagated | open — carried to the response letter as a stated scope boundary |
| E1–E9 | edge-case | sign convention, draw truncation, BOS range, T80 lower bound, angle truncation, leap-year basis, assimilation clamp, AWC extremes, negative carbon | E2/E3/E5/E6 fixed in captions/text; E1, E4, E7, E8, E9 recorded as stated scope in the response letter |

**Tally, stated exactly:** of 23 findings, **17 are fixed in the built text** (A1–A13, E2, E3, E5, E6),
**one is refused** (A14, stack tolerance not propagated to yield — declared as scope in the reviewer
reply), and **five are recorded as stated scope** rather than fixed (E1 sign convention is handled in
SM text but not re-run, E4/E8/E9 are sampling-range statements, E7 is not clamped in the model and is
therefore not claimed).

**Still not independent.** A second reviewer with no stake in the text would find issues none of these lenses reached,
which is exactly why M13 stays open until an external reviewer signs off.

---

## Post-run state (what the manuscript says after the fixes)

- Main text **21 pp**, **4 567 words** of prose (**5 886** including captions, excluding tables and references); bibliography **50** entries after 22 redundant co-citations were removed.
- Every A1–A13 fix is present in the built PDF, not only in the source; verified by searching the compiled text for each replaced phrase.
- The one deliberate refusal: A14 (propagating stack-tolerance into crop yield and NPV) is not done. It is recorded as a stated scope boundary in the pre-emptive reviewer reply rather than implied to be complete.
