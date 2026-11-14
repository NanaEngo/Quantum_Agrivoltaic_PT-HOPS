# Response to reviewers — pre-emptive package (2026-11-14)

**Purpose.** This file is *not* a reply to a decision letter we have received. It is the reply we would
send if the reviewer raised the issues our own adversarial and edge-case passes surfaced
(`docs/ADVERSARIAL_PASS_20261114.md`, `docs/BMAD_REVIEW_20261114.md`). Writing it now forces each
objection to be answered in the manuscript rather than in prose, and gives the editor a short map of
what changed.

**Manuscript state this reply refers to.** `RE_main_2611.tex` (**21 pp**; 4 567 words of prose,
5 886 words including captions, excluding tables and references; **50 references**) and
`RE_SM_2611.tex` (**9 pp**, S1–S7). Zero LaTeX errors, zero undefined references or citations.

**How to read it.** Each entry gives the anticipated comment, what the manuscript says now, where, and
— where no answer is possible — the explicit concession. Concessions are labelled rather than
softened. Nothing here claims field, laboratory, or structural evidence that the package does not
contain.

---

## Anticipated comments and responses

### 1. "The Methods describe a stack that does not match your results."

Was true. The Methods stated ITO 140 nm and ZnO 30 nm and a continuous 1 nm design grid; the executed
model uses ITO 100 nm, ZnO 35 nm and a discrete grid of d_act ∈ {50, 60, 75, 90, 105, 120} nm,
d_Ag ∈ {8, 10, 12, 14, 16} nm, d_cap ∈ {0, 20, 35, 50} nm (120 stacks).

**Fixed.** §2.3 and SM §S1 now state the thicknesses and the grid that produced the numbers.
*Reviewer check:* `parameters.yaml` (`Barrier_...ITO(100nm)/ZnO(35nm)`) and
`data/wp2/tmm_pareto_opv.csv` (the 120 rows).

### 2. "Your k_RC ceiling contradicts your own baseline bound."

Was true. The text claimed a bound ≤ 1.181 × 10⁻⁵ across k_RC ∈ [0.0033, 0.5] /ps while quoting
1.936 × 10⁻⁵ on H2 at k_RC = 0.005 /ps, a point inside that interval.

**Fixed.** The sentence now names the three sampled rates {0.0033, 0.01, 0.5} /ps, reports the H2
maximum of 1.94 × 10⁻⁵, states that the dependence is non-monotonic, and restricts the HEOM
cross-check to H2 and H3 — the two Hamiltonians it was actually run on.
*Reviewer check:* `data/wp2/quantum_ness_summary.json` (`k_rc_sensitivity_H2`).

### 3. "81.2–82.8 % and 81.0–83.0 % are different statistics presented as one."

Correct — one was the range of per-crop decade means, the other the 2023 envelope across crops.

**Fixed.** Both are now labelled by definition, in the main text and in SM §S6.1.

### 4. "How sensitive are the optics to what a fab can actually hold?"

**Answered with an executed audit, not a claim.** SM §S7.1–S7.2 and `data/wp2/wp2_device_tolerance.json`:
4 000 thickness draws (active ±5 %, Ag ±1 nm, cap ±2 nm, seed 42). APT 40.30–47.75 % (p05–p95,
SD 2.29 pp), PCE 9.18–10.61 % (SD 0.44 pp), LUE 4.24–4.43 % (SD 0.06 pp, 1.3 % of nominal), photon
conservation 4.44 × 10⁻¹⁶ on every draw. Ag thickness dominates; LUE is the tolerance-insensitive
metric. Acceptance criteria are fixed in `docs/DEVICE_STRUCTURAL_VALIDATION_REGISTER_20261114.md`.

**Boundary we accept:** we cannot report an independent optical measurement of the stack, and the
tolerance spreads are illustrative rather than measured line statistics. Draws were truncated at
Ag ≥ 4 nm and cap ≥ 0 nm, so the reported tails are conservative (stated in the Table S9 caption).

**Open item:** stack tolerance is not propagated into crop yield and NPV. We bound it through APT
(±2.3 pp) rather than running the full chain, and the response is to say so, not to imply it was done.

### 5. "What load do those elevated structures actually have to survive?"

**Answered as a screening, with the design class refused.** SM §S7.3 and
`data/wp1/wind_load_screening.json`: the shipped ERA5 year gives 10 m hourly means of
1.18–1.89 m/s (annual), p99 2.94–5.31 m/s, maxima 4.58–7.03 m/s, zero hours above 10 m/s, i.e.
13.1–30.9 Pa at the record maximum — one to two orders of magnitude below the 250–640 Pa implied by
candidate basic velocities of 20–32 m/s. A one-year record of hourly means cannot bound a design load,
so **no design pressure is asserted**. What a local annex must supply is listed explicitly (basic
velocity, terrain category, orography factor, altitude correction).

### 6. "A 1.05 pp technology contrast cannot be resolved by any affordable field trial."

**Conceded, and now stated.** SM §S7.4 and `docs/FIELD_VALIDATION_PROTOCOL_20261114.md` table
replication against *assumed* plot-level SD: at σ_d = 3 pp a 16-plot design cannot resolve 1.05 pp
(~71 paired plots per arm). The modelled inter-year SD (0.06–0.19 pp) reflects shared weather, not
plot variance, so we do not derive a sample size from it. The paper frames its results as screening
hypotheses for exactly this reason.

### 7. "Shapley attribution is not a causal identification strategy."

**Agreed.** §2.1 says the decomposition apportions modelled yield among internal physical pathways
and does not identify econometric treatment effects; the abstract now says the decomposition
*attributes the modelled shift* rather than that it *exposes* a mechanism, and Fig. 4 is retitled
"Mechanism attribution".

### 8. "Your carbon-abatement figure needs the displaced factors."

**Fixed.** §3.3 now states the factors: displaced diesel 0.80 kgCO₂e/kWh and displaced grid
electricity 0.28 kgCO₂e/kWh (both model constants), and labels the result counterfactual.

### 9. "Probability language on a designed sample."

**Fixed.** "Realizations" → "sampled parameter vectors" where the reference is the Saltelli design;
the abstract's "in 77–89 % of draws" is count-language and stays.

### 10. "Tea: NPV up while IRR falls?"

**Fixed.** §3.3 notes that the battery adds revenue and capex, so NPV rises while IRR falls.

### 11. "Negative off-grid NPV next to a positive p05 NPV looks contradictory."

**Fixed.** §3.4 labels the off-grid figure as the no-export case with array capex sunk, distinct from
the standalone-profitability distribution.

### 12. "You name black pepper, vanilla, and passionfruit as candidates."

**Fixed.** Now labelled untested extrapolations requiring species- and species-site validation.

### 13. "You claim a falsifiable test but describe only a model."

**Fixed.** The positioning table now names the pre-registered field protocol (SM §S7.4) as the test,
rather than calling the model itself falsifiable.

### 14. "Is the quantum section decorative, given S_Ti ≈ 10⁻⁸?"

It is a scoping result, and it is stated as one: the CW-NESS bound (≤ 3.37 × 10⁻⁵), the HEOM envelope
(2.10 × 10⁻³), the widened-perturbation Sobol index (≤ 2.58 × 10⁻⁷) and the conclusion that classical
shade timing, dispatch, and encapsulation govern deployment. The section exists so that the premise
underlying spectrally tailored agrivoltaics is tested rather than assumed, and its null result is
reported with the same prominence as the positive ones.

### 15. "One ERA5 year, one AWC value, one reanalysis product."

**Conceded with quantification.** SM §S6.1 (2014–2023 reruns: coffee −8.22 ± 1.11 %, pepper
+1.85 ± 2.01 % with 7/10 positive years, tea −3.54 ± 0.97 %, all 0/10) and SM §S6.3 (3×3 AWC × g_b
audit: g_b governs the sign of ΔY, AWC moves it by 0.47–2.63 pp). §5.3 states that both are
literature-calibrated surrogates outside the twelve-parameter Sobol ensemble.

### 16. "Your reference list and length."

**Addressed.** The bibliography is now **50 references**, all cited in text and in the Supporting
Material; 22 redundant co-citations were removed from sentences that already carried a primary
source. Main text is **4 567 words of prose** (5 886 including captions), within the 4 000–6 000 range.

---

## What this manuscript does not claim

| Not claimed | Where said |
|---|---|
| Field validation, realized farm yields, or project returns | §2.1, §3.6, §5.3, SM §S7.4 |
| A bankable grid interconnection | §2.6, §3.5, SM §S6.2 |
| A structural design or wind-load class | SM §S7.3 |
| An independent optical measurement of the stack | SM §S7.1 |
| That spectral selectivity or quantum coherence drives agronomic outcomes | §3.2–§3.4, §4 |
| That "realizations" are a probability sample | §3.4, SM §S6.1 |

## Files a reviewer will want

`parameters.yaml` (v2.5.0) · `data/wp2/tmm_pareto_opv.csv` · `data/wp2/wp2_device_tolerance.json` ·
`data/wp2/quantum_ness_summary.json` · `data/wp1/wind_load_screening.json` ·
`data/wp5/wp5_sobol_convergence.json` · `docs/CHECKSUMS_SHA256.txt` ·
`docs/FIELD_VALIDATION_PROTOCOL_20261114.md` · `docs/DEVICE_STRUCTURAL_VALIDATION_REGISTER_20261114.md`
