# BMAD Adversarial Stress-Test: "How Would a Reviewer Kill This Paper?"

* **Document Code:** `AST-RE-261112-REV3`  
* **Target:** Elsevier *Renewable Energy*  
* **Manuscript Working Title:** *Spectrally Selective Agrivoltaic Co-Design for Perennial Cash Crops in Sub-Saharan Africa: A Multi-Crop Decision Framework * and a Bounded Test of Quantum Coherence Relevance*  
* **Date:** 2026-11-12 (Revision 3: Tri-Crop Arabica Coffee, Penja White Pepper, Highland Tea)  

---

## Executive Framing

In accordance with BMAD adversarial review principles (`bmad-brainstorming` and `bmad-review`), this document subjects the proposed research design to aggressive, worst-case reviewer skepticism. For every potential lethal objection raised by a *Renewable Energy* reviewer or editor, a concrete, mathematically defensible structural mitigation is established.

---

## Lethal Scenario Matrix & Preemptive Defenses

### Scenario 1: The "Scale Disconnect & Laser-vs-Sunlight" Objection (Quantum to Farm)
> **Reviewer Objection:**  
> *"This manuscript forces an absurd marriage between femtosecond-scale pulsed non-Markovian dynamics (HOPS on bacterial FMO) and a 20-year agricultural model in Cameroon. Natural sunlight is continuous-wave incoherent thermal light—there are no coherent beats—and RuBisCO kinetics wash out any sub-picosecond effect."*

- **Severity:** Fatal if unaddressed.
- **Root Vulnerability:** Previous drafts used bacterial FMO (750–820 nm), heavy brute-force pulsed HOPS sweeps, and uncomputed placeholder bounds.
- **The Defensive Counter-Strike:**
  1. **Right Complex & Right Regime:** Replace FMO entirely with the **14-site plant LHCII monomer** (8 Chl *a*, 6 Chl *b*, PAR 400–700 nm, Novoderezhkin et al. 2011) excited by **continuous-wave incoherent AM1.5G solar pumping (NESS)** via hybrid **Modified Redfield–Generalized Förster** ($15\ \text{cm}^{-1}$ cutoff, 48 vibrational modes). Use MesoHOPS v1.8.0 (`HopsTensorTrajectory`) strictly as a lightweight reduced-bath error-bound check ($N=32$).
  2. **Invert & Test the Hypothesis:** Do **not** assume quantum enhancement or cite uncomputed percentages upfront. Compute $\Delta \eta_{\text{NESS}}(T_{\text{OPV}})$ directly and propagate it across both FVCB–Medlyn regimes: low-light electron-transport limitation ($A_j$, where $\partial A/\partial \eta_{\text{ET}} > 0$) and midday RuBisCO limitation ($A_v$, where $\partial A/\partial \eta_{\text{ET}} \equiv 0$).
  3. **Falsifiable Bound:** Publish the computed canopy-integrated ratio $g_c$ alongside the exact 4-lever attribution showing whether classical optical/thermal/VPD mechanisms dominate over quantum routing.
  4. **Architectural Isolation:** Relegate the quantum scale-bound to a self-contained section (Section 4). If an editor removes it, the tri-crop classical/interpretative core stands 100% intact.

---

### Scenario 2: The "Tropical OPV Degradation" Objection
> **Reviewer Objection:**  
> *"Organic photovoltaics (OPV) degrade rapidly under tropical humidity and high UV. Calculating a 20-year Net Present Value (NPV) for an OPV system in Cameroon is unphysical and misleading. Outdoor modules without hermetic glass encapsulation will fail within 12 months."*

- **Severity:** Fatal for engineering credibility.
- **The Defensive Counter-Strike:**
  1. **Finite Lifetime Modeling ($T_{80}$):** We explicitly reject the 25-year OPV assumption. The baseline model sets OPV operational lifetime to $T_{80} = 5\ \text{years}$ (based on ISOS outdoor standards with atomic layer deposition ALD encapsulation).
  2. **Replacement CAPEX Sinking Fund:** Every 5 years, an explicit module replacement cost ($C_{\text{replace}} = 25\ \text{USD/m}^2$) is deducted from cash flows.
  3. **Global Sensitivity & Threshold Analysis:** We compute the exact **OPV break-even envelope**: what minimum lifetime ($T_{80}$) and maximum module cost ($\text{USD/m}^2$) are required for ST-OPV to outperform conventional silicon agrivoltaics?
  4. **Benchmarking Against Opaque Silicon:** Silicon agrivoltaics (with geometric strip shading) is evaluated side-by-side as a control scenario.

---

### Scenario 3: The "No Primary Agronomic Field Data" Objection
> **Reviewer Objection:**  
> *"The authors did not plant coffee, pepper, or tea under actual solar panels in Cameroon. The entire crop response is derived from equations. This lacks empirical validation."*

- **Severity:** High.
- **The Defensive Counter-Strike:**
  1. **Calibrated on Primary Agronomic Trials:** The crop growth models are parameterized directly from established field trials in Cameroon and peer-reviewed agrivoltaic studies:
     - *Coffee:* EU BREEDCAFS F1 hybrid trials (*Starmaya*, *Centroamericano* H1 vs. *Java*) conducted by CIRAD/IRAD in Foumbot (Noun division, Western Highlands).
     - *Tea:* Ecophysiological parameters from Djuttitsa/Ndu highland plantations and empirical PV-tea agrivoltaic field trials demonstrating +9% to +15% yield gains under midday PAR moderation.
     - *Penja Pepper:* Official PGI specifications (*Cahier des charges*) and CIRAD phytopathological surveys in Njombé-Penja (Moungo).
  2. **Framing as a "Pre-Deployment Decision Atlas":** Agrivoltaic installations for perennial tree crops require 20-year capital commitments. Field experimentation takes 5–8 years. An uncertainty-propagated decision framework is mathematically necessary *prior* to physical installation to prevent catastrophic capital loss.
  3. **Uncertainty Propagation:** We do not report single-point yield predictions. We report probabilistic distributions (Monte Carlo, $N = 10,000$) with wide agronomic confidence bands ($\pm 20\%$).

---

### Scenario 4: The "Structural Realism & Canopy Clearance" Objection
> **Reviewer Objection:**  
> *"Agrivoltaics over tropical perennial crops requires tall, heavy mounting structures that inflate CAPEX and are vulnerable to storm wind-shear."*

- **Severity:** Medium-High.
- **The Defensive Counter-Strike:**
  1. **Low Canopy Table Architecture:** Tea bushes are pruned and maintained as a flat plucking table at **1.0 m height**, and coffee shrubs are kept at **2.2 m**. A standard agrivoltaic mounting structure clearance of **2.2–2.4 m** is fully sufficient for routine manual and mechanized fieldwork.
  2. **Standard Agricultural Framing CAPEX:** Standard galvanized steel/aluminum agricultural mounting ($20\ \text{USD/m}^2$) is utilized without requiring expensive tall stilt framing.
  3. **Penja Pepper Trellis Dual-Functionality:** For Penja pepper, the mounting structure doubles as the physical vertical trellis ($3.5\ \text{m}$), replacing fragile living tutor trees (*Spondias mombin*). The capital cost of the solar frame is partially offset by avoiding annual living-tutor replacement and pruning labor.

---

### Scenario 5: The "Pepper Light-Hunger Paradox"
> **Reviewer Objection:**  
> *"Published literature indicates that black pepper (Piper nigrum) yields peak under full sunlight when water is sufficient. Shading Penja pepper with OPV will reduce the harvest of Africa's most lucrative spice."*

- **Severity:** Medium-High.
- **The Defensive Counter-Strike:**
  1. **Resolution of the Contradiction:** Penja pepper requires high PAR for spike development, but tropical leaf temperatures in Moungo exceed $38\ ^\circ\text{C}$ in open sun, triggering midday stomatal closure and photoinhibition.
  2. **Solving the Living Tutor Crisis:** In Penja, traditional living tutors (*Spondias mombin*) are dying of *Armillaria* and *Phytopythium* root rot, causing vine collapse. Agrivoltaic structures act as **disease-free engineered trellises** that replace the decaying living trees.
  3. **High-Transmittance Spectral Design:** The optimization framework for Penja pepper selects **ultra-high transparency** (APT > 65%, shade < 25%), demonstrating that optimal co-design is strictly crop-dependent.

---

### Scenario 6: The "Phantom Economics & Rural Power Utilization" Objection
> **Reviewer Objection:**  
> *"The economic payback relies on selling solar electricity to an unreliable grid or rural consumers with low purchasing power."*

- **Severity:** High.
- **The Defensive Counter-Strike:**
  1. **High-Value On-Farm Industrial Load & Overnight Reality Check:** Tea processing consumes `250–500 kWh_el/t` in modern CTC plants (median `380 kWh_el/t`; up to `600 kWh_el/t` in older estates, plus `~4,500 kWh_th/t` biomass heat). Crucially, ~45% of tea electricity is **overnight withering** (zero direct PV without storage), while 55% is daytime CTC/sorting/drying blowers. Coffee wet milling (`25 kWh/t`, 90% day) and pepper washing/drying (`45 kWh/t`, 85% day) align strongly with solar hours.
  2. **Honest Dispatch & Diesel Displacement Anchor:** We test 3 dispatch regimes explicitly (daytime-only PV matching without BESS, 2h LFP buffer for spoilage prevention, and full overnight LFP BESS at `220 USD/kWh`) against rural diesel ($0.45\ \text{USD/kWh}$) and marginal grid export ($0.085\ \text{USD/kWh}$).
  3. **Zero Carbon Dependency:** All primary financial metrics (NPV, IRR, DPBP) are reported **at 0 USD/t carbon revenue** and **0% subsidies**.

---

### Scenario 7: The "Radiative, Optical Conservation & Physiological Oversimplification" Objection
> **Reviewer Objection:**  
> *"Fixing 10.5% OPV efficiency at 70% transmittance violates photon conservation; simple shading ignores downward panel LWIR heating at 2.2 m clearance, ignores cloudy monsoon PAR deficits, omits finite coffee mesophyll conductance $g_m$, and fails to test whether OPV replacements worsen kg CO2e/kWh."*

- **Severity:** Fatal for *Renewable Energy* physics, PV, and agronomy reviewers.
- **The Defensive Counter-Strike:**
  1. **LUE-Coupled Optical Stack:** Full TMM (`ITO/ZnO/PM6:Y6/MoO3/Ag/MoO3`) derives $\text{PCE}(\text{APT})$ self-consistently along the $\text{LUE} = \text{PCE} \times \text{APT}$ Pareto front (`2.5–4.2%`), including seasonal Harmattan/monsoon soiling (`2–6%`).
  2. **Closed Bidirectional $(T_{\text{pv}}, T_{\text{leaf}})$ + Finite $g_m$ + 8760h Seasonality:** Couples panel LWIR emission ($F_{l\to p}\varepsilon_p\sigma T_p^4$), canopy latent cooling, Medlyn $g_s(\text{VPD}_l)$, **finite *C. arabica* $g_m$ (`0.04–0.15 mol m⁻² s⁻¹`)**, ePAR/R:FR, and hourly dry-vs-monsoon $f_{\text{diff}}$ resolution.
  3. **Dual-FU ISO LCA & 2D Regime Maps vs. Spaced c-Si:** Reports both $\text{kg CO}_2\text{e}/\text{ha}/\text{yr}$ and $\text{g CO}_2\text{e}/\text{kWh}$ to locate the exact $T_{80}^*$ break-even against 25-year spaced c-Si ($\beta_T=-0.38\,\%/^\circ\text{C}$).

---

## Reconciliation pass — 2026-11-14

**What was done.** This register was compared line by line against the package as it now stands
(`RE_main_2611.tex`, `RE_SM_2611.tex`, `parameters.yaml` `framework_version: 2.5.0`,
`docs/DATA_ANALYSIS_REPORT_20261113.md` rev. 3). The comparison is a verification-gap pass done by
direct reading; no BMAD agent or BMAD tooling was executed for it, and nothing below is offered as
an independent domain review.

**Status of the register.** The Scenario 1–7 arguments remain valid as *argument structure*: each
still names a real reviewer objection and the defence the manuscript actually makes. Several
numbers and one design claim inside them, however, predate the executed model and would
misrepresent the paper if quoted. They are listed here rather than overwritten, so the record of
what was claimed earlier stays visible.

| Location | Stale statement in this register | Current package value (verified) | Verified against |
|---|---|---|---|
| Header | Working title "*Spectrally Selective Agrivoltaic Co-Design … A Multi-Crop Decision Framework \* and a Bounded Test …*" (stray asterisk) | "Scale-Bridging Techno-Economic, Microclimatic, and Open-Quantum Assessment of Semi-Transparent Organic Agrivoltaics for Sub-Saharan Perennial Crops" | `RE_main_2611.tex` `\title` |
| Scenario 1 | "hybrid Modified Redfield–Generalized Förster (15 cm⁻¹ cutoff, 48 vibrational modes)"; MesoHOPS "N=32" | Bloch–Redfield partial-secular equilibrium and non-equilibrium steady states versus diagonal Pauli; Renger spectral density (λ_D = 50.87 cm⁻¹, γ_D = 50 cm⁻¹); three 14-site Hamiltonians (H1 Novoderezhkin, H2 Müh, H3 MMSIC-MD); N = 200 disorder draws; MesoHOPS 1.8.0 benchmark at N = 48 seeds over 2000 fs | `sec:methods_quantum`, `sec:quantum_bound` |
| Scenario 1 | "if an editor removes it, the tri-crop classical core stands intact … (Section 4)" | Still satisfied: the scale-separation analysis is the standalone §4, between Results (§3) and Discussion (§5) | section order in the compiled `RE_main_2611.pdf` |
| Scenario 3 | Model "parameterized directly" from BREEDCAFS/CIRAD field trials; "probabilistic distributions … with ±20 % confidence bands" | Inputs are literature-calibrated, not site-calibrated; no paired field measurements exist at the three sites; VPD/soil/conductance levers are scenario ranges, and the ten ERA5 years are deterministic reanalyses explicitly *not* a probability sample | `sec:interpretive`, `sec:weather_year_sensitivity`, `sec:disc_limits` |
| Scenario 5 | Pepper optimum "APT > 65 %, shade < 25 %" | No APT > 65 % design exists in the optical library (bounded at APT = 52.06 %); the modelled pepper optimum is APT 44–52 % at GCR 65 %, shade 36–41 %, with APT 56 %/GCR 50 % (25.9 % shade) giving +7.27 % | `sec:res_tmm`, `tab:agro_summary` |
| Scenario 6 | Coffee milling "25 kWh/t, 90 % day" | 25.0 kWh/t at 85 % daytime share (pepper 45.0 kWh/t at 85 %; tea 380 kWh/t at 55 % daytime, 45 % overnight) | `tab:sites`, `sec:methods_tea` |
| Scenario 6 | Diesel 0.45 USD/kWh, export 0.085 USD/kWh quoted without provenance | Export tariff 0.085 USD/kWh and diesel price are the modelled inputs; both are Sobol parameters, and export tariff is the leading driver of standalone bankability in coffee and pepper | `parameters.yaml`, `tab:sobol_dual` |
| Scenario 7 | LUE "2.5–4.2 %" | LUE_max = 4.424 % on the Pareto-optimal subset, 4.486 % grid peak, photon conservation |ΔR+T+A_tot−1| = 4.44×10⁻¹⁶ | `sec:res_tmm`, `fig:opt_pareto` |
| Scenario 7 | "2D regime maps" as the only regime product | Regime information is carried by the seasonal year map plus the phase diagram of `fig:shapley`b, and now also by the conditional screening tables `tab:decision_map`, `tab:weather_decade`, `tab:export_acceptance` | `sec:res_agro`, `sec:decision_map` |

**Objections this register does not answer, and the manuscript now does.** Three critiques raised
after Revision 3 are absent from the Scenario 1–7 set and are handled in the text:

1. *Export monetisation* (Scenario 6 assumes a buyer exists) — answered by `sec:export_acceptance`
   with the 50 %-acceptance and no-export cases, which turn coffee and pepper negative.
2. *Single weather year* — answered by the 2014–2023 sensitivity (`sec:weather_year_sensitivity`),
   which removes any decade-robust claim for Penja pepper.
3. *Estimator stability* — answered by the resolution ladder and scramble study in SM
   `sec:sm_sobol_convergence`; the driver ranking is unchanged and the exceedance probability
   varies by at most 0.6 percentage points.

**Standing limitation.** Every defence in this document is a modelling argument. None of them
constitutes field, device, or interconnection evidence, and no entry here should be cited as if it
did.

### Where a fresh pass changed the text (2026-11-14)

A later verification pass, recorded in `docs/ADVERSARIAL_PASS_20261114.md`, is a better starting
point than this file for what is currently true. It is **internal, not independent**, and it found
defects the Scenario 1–7 set never covered — most notably that the Methods described a different
optical stack (ITO 140 nm, ZnO 30 nm, 1 nm grid) from the one that produced the reported numbers,
and that the stated k_RC ceiling was contradicted by the paper's own baseline value. Read it before
reusing any defence here.
