# Decision-Grade Research Report: Tri-Crop Spectral Agrivoltaics in Cameroon

**Doc Workspace:** `Submission_Package_RenewableEnergy_Manuscript/docs/research-agrivoltaic-opv-coffee-tea-penja-pepper/`  
**Date:** 2026-11-12 (Updated v2.2 — Physical Regimes & Interpretative Framing)  
**Target:** Elsevier *Renewable Energy*  

---

## 1. Executive Summary & Decision

We evaluated the physical consistency, scientific novelty, and feasibility of reformulating the agrivoltaics manuscript for *Renewable Energy* around three perennial cash crops in Cameroon:
1. **Arabica Coffee (*Coffea arabica*, Foumbot/Noun, ~1,050 m; Western Highlands zone 1,000–1,600 m):** Primary agroforestry baseline with finite mesophyll conductance $g_m$ (`0.04–0.15 mol m⁻² s⁻¹`, Martins & DaMatta). Proven shade tolerance (BREEDCAFS F1 hybrids under 25–40% shade).
2. **Highland Tea (*Camellia sinensis*, Djuttitsa/Bamboutos & Ndu/Donga-Mantung, 1,600–2,100 m):** Low canopy plucking table (1.0 m height) allowing standard mounting structures (2.2–2.4 m clearance). PV shading suppresses midday photoinhibition (`+9.3% to +15.3%` leaf yield in China PV-tea trials) and elevates theanine. Tea estates consume a median `~380 kWh_el/t` (`250–600 kWh_el/t`, separate from `4,500 kWh_th/t` biomass heat), split `55%` daytime CTC/sorting vs. `45%` **overnight withering** (evaluated across no-BESS, 2h LFP buffer, and full overnight BESS against $0.45\ \text{USD/kWh}$ diesel).
3. **Penja White Pepper (*Piper nigrum*, Moungo Volcanic Valley, 200–400 m):** High-value contrast / stress test. First PGI in Sub-Saharan Africa ($5,000\ \text{XAF/kg}$ farm-gate, $14,000\ \text{XAF/kg}$ certified export). Resolves a documented phytosanitary bottleneck: living *Spondias mombin* tutors succumb to *Armillaria* and *Phytopythium* root rot; engineered agrivoltaic trellises replace dying tutors while providing calibrated thermal and radiative moderation.

**Decision:** **APPROVED (v2.2 Methodological Revision).** By replacing speculative FMO/pulsed-HOPS analogies with **plant 14-site LHCII CW incoherent NESS + Modified Redfield–Förster**, adding **ePAR/R:FR**, **panel LWIR + Medlyn $g_s$–VPD leaf energy balance**, and benchmarking **ST-OPV directly against spaced opaque c-Si PV**, the study becomes a physically rigorous, interpretative decision atlas.

---

## 2. Gap & Novelty Verification Matrix

| Gap ID | Formulation | Status in Literature | Primary Literature & Technical Evidence |
|---|---|---|---|
| **G1′** | Spectrum-resolved ST-OPV (ePAR, R:FR, diffuse sky) + LWIR microclimate co-design over perennial tropical crops of divergent $I_{\text{sat}}$ | **OPEN (Targeted Multi-Crop Novelty)** | Chinese PV-tea trials use poly-Si (`10.3390/agriculture16010125`, `10.1002/agj2.70470`); Brazil/India cover agroforestry shade or grapes (`10.1590/1413-70542018425020418`, `10.1016/j.seta.2017.08.004`). None integrates spectral ST-OPV + LWIR + c-Si counterfactual across these perennial cash crops. |
| **G2′** | Incoherent CW-sunlight quantum-relevance bound in higher-plant 14-site LHCII coupled to two-regime FVCB–Medlyn assimilation | **OPEN (Rigorous Negative-Result Test)** | Corrects laser-pulsed FMO confusion: models thermal NESS (Brumer & Shapiro; Kassal et al.; Novoderezhkin 2011) and tests $\Delta \eta_{\text{NESS}}$ propagation across $A_j$ (shade) vs. $A_v$ (RuBisCO-limited) without fabricated pre-computation claims. |
| **G3′** | Tropical OPV lifetime-explicit TEA ($T_{80}=5\ \text{yr}$, 5-yr replacement) with Monte Carlo & Sobol sensitivity at 0% carbon revenue baseline | **OPEN** | Most agrivoltaic TEA omits tropical moisture degradation and leans on external carbon subsidies. |
| **G4** | Direct matching of PV generation to post-harvest on-farm electrical loads (tea withering/drying, coffee wet milling, pepper drying) | **OPEN** | Anchors LCOE displacement in verified diesel substitution ($0.45\ \text{USD/kWh}$) rather than ideal grid injection. |
| **G5** | Explicit economic & agronomic valuation of PGI / organic quality premiums and tutor pathology replacement | **OPEN** | Incorporates Penja PGI value density and *Spondias mombin* pathogen replacement. |
| **G6** | **ST-OPV vs. Spaced Opaque c-Si Technological Regime Boundary** across VPD, diffuse fraction, $T_{80}$, and BOS costs | **OPEN (Interpretative Core)** | Identifies exact phase boundaries where ST-OPV spectral selectivity + light framing defeats 25-year c-Si — and where mature c-Si remains superior. |

---

## 3. Crop Comparison & Coupled Ecophysiological Parameterization

All crop modeling moves beyond standalone light-response curves to a coupled **FVCB ($C_c = C_i - A/g_m$ with finite coffee $g_m$) + Medlyn stomatal conductance + Bidirectional PV–Leaf Energy Balance (SW + Panel LWIR)** architecture (`parameters.yaml` v2.4.0; full primary trait extraction scheduled in WP1, marked `[VERIFY]`):

$$A(I_{\text{ePAR}}, T_l, \text{VPD}_l) = \min\big(A_v(T_l, C_c),\ A_j(J)\big) - R_d(T_l), \qquad g_s = g_0 + 1.6\left(1 + \frac{g_1}{\sqrt{\text{VPD}_l}}\right)\frac{A}{C_a}$$

| Parameter | Symbol | Arabica Coffee | Highland Tea | Penja White Pepper | Unit |
|---|---|---|---|---|---|
| Light Saturation Point | $I_{\text{sat}}$ | $750 \pm 120$ | $850 \pm 100$ | $880 \pm 140$ | $\mu\text{mol}\cdot\text{m}^{-2}\cdot\text{s}^{-1}$ |
| Apparent Quantum Yield | $\phi_{\text{max}}$ | $0.042 \pm 0.005$ | $0.040 \pm 0.004$ | $0.048 \pm 0.006$ | $\text{mol}\ \text{CO}_2\cdot(\text{mol photons})^{-1}$ |
| Optimal Shade Range | $S_{\text{opt}}$ | 25% – 40% | 30% – 50% | 20% – 35% | % PAR reduction |
| Canopy / Clearance Height | $H_{\text{c}} / H_{\text{mount}}$ | 2.2 / 2.4 | **1.0 / 2.2** | 3.5 / 3.8 (trellis) | m |
| Processing Electrical Load | $E_{\text{proc}}$ | 25 (90% day) | **380 med. [250–600] (55% day / 45% night)** | 45 (85% day) | $\text{kWh}_{\text{el}}\text{/t}$ |
| Baseline / Premium Price | $P_{\text{base}} / P_{\text{prem}}$ | 2,400 / 3,100 | 1,800 / 2,600 | 5,000 / 14,000 | XAF/kg |
| Baseline Clean Yield | $Y_{\text{clean}}$ | $850 \pm 180$ | $1\,800 \pm 300$ | $800 \pm 220$ | $\text{kg/ha}$ |

---

## 4. Quantum Relevance Bound: Physical Regime & Scale-Bridging Protocol

Under natural sunlight, higher-plant light harvesting operates in an **incoherent Continuous-Wave Non-Equilibrium Steady State (NESS)** inside the **14-site LHCII monomer** (8 Chl *a*, 6 Chl *b*, 400–700 nm), not as pulsed wavepacket interference in NIR bacterial FMO.

1. **Primary Quantum Solver (Hybrid Modified Redfield – Generalized Förster):** Using Novoderezhkin et al. (2011) site energies/couplings (15 cm⁻¹ cutoff between strong intra-cluster Modified Redfield transfer and weak inter-cluster Generalized Förster hopping) with Drude-Lorentz + 48 vibrational modes, steady-state solar pumping computes $\eta_{\text{ET}}(T_{\text{OPV}})$ vs. $\eta_{\text{ET}}(\text{AM1.5G})$ over 200 static disorder realizations.
2. **MesoHOPS v1.8.0 Role (Targeted Error Bound):** `mesohops.tensor.HopsTensorTrajectory` is restricted to a reduced-bath benchmark (Drude-Lorentz + 2 dominant Chl vibrational modes at $\sim 340, 740\ \text{cm}^{-1}$, $N=32$) solely to verify the non-Markovian error envelope $|\eta_{\text{HOPS}} - \eta_{\text{mR-GF}}|$.
3. **Biochemical Propagation Hypothesis (To Be Computed in WP2/WP4):**
   - In the **electron-transport-limited low-light regime ($A = A_j$)**, $\partial A / \partial \eta_{\text{ET}} > 0$ proportionally to antenna efficiency shifts.
   - In the **RuBisCO-limited field-irradiance regime ($A = A_v$)**, $\partial A / \partial \eta_{\text{ET}} \equiv 0$.
   - The annual canopy multiplier $g_c = Y(\eta_{\text{ET}}^{\text{filt}}) / Y(\eta_{\text{ET}}^{\text{AM1.5G}})$ will be computed explicitly across cloudy and clear Cameroon seasons—testing quantitatively whether microscopic quantum routing makes any measurable macroscopic agronomic difference ($<0.5\%$ vs. classical optical/microclimate gains of $\mathcal{O}(10\%)$).
