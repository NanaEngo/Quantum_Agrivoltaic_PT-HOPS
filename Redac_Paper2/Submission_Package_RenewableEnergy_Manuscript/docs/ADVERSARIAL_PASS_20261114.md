# Adversarial and edge-case pass — 2026-11-14 (M13)

**What this is.** A recorded adversarial and edge-case review of `RE_main_2611.tex` and
`RE_SM_2611.tex` against their own artifacts, run as a verification-gap pass after the second
mitigation pass.

**What this is not.** It is **not independent**. The same agent that edited the manuscript ran it, so
it cannot substitute for external domain review, and no BMAD agent or BMAD tooling was executed.
M13's "independent adversarial/edge-case pass" therefore stays **open**; this file records what was
found in the pass that was actually run, so the external reviewer starts from a shorter list.

**Method.** Two lenses, applied to the compiled text rather than to intentions:

1. *Adversarial.* For each headline claim, ask what a hostile reviewer would demand as evidence;
   then open the artifact that claim rests on and compare the number, the unit and the scope.
2. *Edge case.* Where the model has boundaries (zero carbon price, zero export, k_RC endpoints,
   ±2σ thickness, one weather year, single AWC value), check that the text's wording survives them.

Every finding below cites the artifact that settles it. Findings marked **fixed** were corrected in
this pass; the rest are dispositions the authors must own.

---

## Findings

### F1 — Methods misstated the optical stack and the design space (major, fixed)

`RE_main_2611.tex` §2.3 and `RE_SM_2611.tex` §S1 described glass/ITO **140 nm** and ZnO **30 nm**,
and swept "d_act ∈ 40–140 nm, d_Ag ∈ 8–22 nm, d_cap ∈ 0–60 nm (120 grid stacks at 1 nm spacing)".

The executed model is neither. `parameters.yaml` records
`Barrier_PET/ITO(100nm)/ZnO(35nm)/...`, `wp2_tmm_opv.simulate_opv_exact_snell` defaults to
`d_ito_nm=100.0, d_zno_nm=35.0`, and `data/wp2/tmm_pareto_opv.csv` contains exactly the discrete sets
d_act ∈ {50, 60, 75, 90, 105, 120} nm, d_Ag ∈ {8, 10, 12, 14, 16} nm, d_cap ∈ {0, 20, 35, 50} nm
(6 × 5 × 4 = 120 stacks, no 1 nm spacing).

*Why it matters:* a reviewer reproducing the optics from the stated thicknesses would obtain a
different Pareto front and could not match APT = 44.12 %. This is the most consequential error the
pass found.

*Fixed:* both files now state ITO 100 nm, ZnO 35 nm and the discrete grid that was actually swept.

### F2 — The k_RC ceiling contradicted the paper's own baseline value (major, fixed)

The quantum section stated the bound "staying ≤ 1.181 × 10⁻⁵ across k_RC ∈ [0.0033, 0.5] /ps", yet
the same paragraph quotes 1.936 × 10⁻⁵ (H2) at k_RC = 0.005 /ps, which lies inside that interval.
`data/wp2/quantum_ness_summary.json` resolves it: the sweep sampled only three rates
(0.0033, 0.01, 0.5 /ps, giving 0.99, 1.11 and 1.18 × 10⁻⁵), and the dependence is non-monotonic, so
the interval wording was simply false while the sampled-point ceiling was right.

*Fixed:* the sentence now names the three sampled rates and states the H2 maximum (1.94 × 10⁻⁵)
rather than implying a bound over a continuum. It also now says the HEOM cross-check covers H2 and
H3, which is what the artifact contains — H1 was not cross-checked.

### F3 — A ratio mixed two different definitions (moderate, fixed)

"81.2–82.8 % of the c-Si generation" is the range of **per-crop decade means**
(81.21, 82.47, 82.75 from the multiyear CSV), whereas the neighbouring 2023 figure, 81.0–83.0 %, is a
**year-level envelope across crops**. Both numbers were right and both were unlabelled, so a reader
could not tell they were different statistics.

*Fixed:* each is now labelled as what it is (per-crop means vs 2023 envelope).

### F4 — Fig. 4 was titled as a causal result (minor, fixed earlier in this session)

Caption read "Causal mechanism and climate-envelope mapping" while §2.1 explicitly disclaims
econometric treatment effects. Retitled "Mechanism attribution and climate-envelope mapping".

### F5 — Field-testability of the central technology contrast was never stated (substantive, added)

The matched-shade ST-OPV–c–Si yield contrast is at most 1.05 pp. The modelled inter-year SD of that
contrast is 0.06–0.19 pp (shared weather), which is not a field variance. Applying standard paired
power arithmetic, a 16-plot design at σ_d = 3 pp cannot resolve 1.05 pp; ~71 paired plots per arm
would be needed. The paper therefore asserts a contrast that a realistic campaign could not detect.

*Disposition:* this is now stated rather than hidden — SM §S7.4, the replication table in
`docs/FIELD_VALIDATION_PROTOCOL_20261114.md` §3, and the framing of the results as screening
hypotheses. It is the single strongest argument for the paper's own scoping.

### F6 — AWC and g_b are read from literature, not measured (known, confirmed)

`RE_main_2611.tex` §2.4 uses AWC = 160 mm for all three crops and g_b = 1.2 mol m⁻² s⁻¹. The ±3×3
audit (`tab:sm_awc_gb_stress`) shows g_b, not AWC, drives the sign of ΔY (coffee −13.40 to +6.42 %).
The text says this. What it does not say is that the same AWC was applied to a 273 m sandy pepper
site and a 1400 m tea site, which is agronomically implausible beyond a screening model.

*Disposition:* accepted limitation; the mechanisms are already framed as literature-calibrated
surrogates and M8's protocol measures both quantities. Optionally the authors may add one clause
naming the single-AWC assumption explicitly.

### F7 — "Realizations" and "probability" language (minor, confirmed acceptable)

`P(ΔNPV > 0)` is a quasi-Monte Carlo sample proportion, not a forecast probability. The text
qualifies it as conditional everywhere except in the abstract, where "trails c-Si NPV in 77–89 % of
draws" is count-language and therefore defensible.

*Disposition:* no change.

### F8 — Single-window numbering inconsistency in planning docs (minor, fixed earlier)

The mitigation plan cited "SM §S9.1/S9.2/S9.3" while the SM contains S1–S7. Renumbered to the real
sections (§S6.1, §S6.2, §S7).

---

## Edge cases checked and found sound

| Edge case | Check | Result |
|---|---|---|
| Zero carbon price | `sections §3.4` and `tab:sm_sobol_robustness` | Exceedance rises to 24.71/18.51/12.34 %, ranking unchanged; text reports it |
| Zero export | `tab:export_acceptance` | Coffee −$379,752/ha, pepper −$281,548/ha, tea +$319,794/ha; text does not hide the collapse |
| Division by zero in LER / LSF | LER defined from yields, LSF from dispatch; both denominators strictly positive in every scenario row | No undefined values in `data/wp5/*.csv` |
| Sobol index bounds | All S_i, S_Ti in [0, 1] across 4 variants × 3 crops | Passes existing test |
| Photon conservation at extremes | 120 stacks + 4000 tolerance draws | max\|R+T+A−1\| = 4.44 × 10⁻¹⁶ throughout |
| Thickness floor in the tolerance MC | Ag ≥ 4 nm, cap ≥ 0 nm, active ≥ 40 nm | An earlier global clip at 40 nm inflated Ag and cap; found and fixed in `wp2b_device_tolerance_audit.py` before the results were used |
| Negative or zero NPV reported as payback | DPBP reported only where cash flow turns positive | Consistent with `tab:tea_lca` |
| One-year weather record | 2014–2023 reruns | Penja advantage withdrawn as a general claim (7/10 years) |
| k_RC interval endpoints | Sampled only at three rates | Now stated as sampled, not continuous (F2) |

## Residual risk the pass could not close

1. **No field data.** Everything agronomic is conditional on FvCB–Medlyn–FAO-56 structure. F5 shows
   the technology contrast is probably below field detectability, which limits what validation can
   ever return.
2. **One reanalysis product, one year, one AWC.** Decade reruns reduce but do not remove this.
3. **Structural class unvalidated.** See `docs/DEVICE_STRUCTURAL_VALIDATION_REGISTER_20261114.md`.
4. **External review still absent.** This pass is internal; a hostile reviewer will find things it
   did not look for, and the authors should assume that.

## Suggested next actions for an external reviewer

Read §2.3 against `data/wp2/tmm_pareto_opv.csv` (F1 shows this class of error occurs), read the
quantum bounds against `data/wp2/quantum_ness_summary.json` (F2), and treat every aggregate range as
suspect until its definition is stated (F3).
