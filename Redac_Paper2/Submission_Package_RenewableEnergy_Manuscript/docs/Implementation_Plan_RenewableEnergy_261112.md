# Detailed Implementation Plan — *Renewable Energy* (Elsevier)

**Target Journal:** *Renewable Energy* (Elsevier, IF ~9.1)  
**Working Title:** *Classical Microclimate Versus Quantum Bounds: Spectral and Techno-Economic Regime Maps for Agrivoltaics Over Tropical Perennial Cash Crops*  
**Workspace:** `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/`  
**Date:** 2026-11-12 (Version 2.4 — Optical Pareto LUE, Factory Diurnal Dispatch & LCA Audit)  
**Single Source of Truth:** `parameters.yaml` (`v2.4.0`) · **Locked Technical Spec:** `docs/Model_Specification_Hamiltonian_Regimes_Scenarios_261112.md`

---

## 1. Strategic Positioning & Interpretative Shift

To transform the manuscript from a descriptive multi-model pipeline into a high-impact *Renewable Energy* research paper, the architecture shifts from **reporting simulated point outcomes** to **deriving causal decompositions and dimensionless regime boundaries**:

1. **Tri-Crop Contrast Across Cameroon's Agro-Ecological Gradient:** Three perennial cash crops sharing real agroforestry niches and distinct physiological/industrial bottlenecks:
   - **Arabica Coffee (*Coffea arabica*, Foumbot/Noun plateau, ~1,050 m):** Primary shade-adapted F1-hybrid baseline (optimal shade 25–40%), finite mesophyll conductance $g_m$ (`0.04–0.15 mol m⁻² s⁻¹`), wet milling ($25\ \text{kWh}_{\text{el}}\text{/t}$, `90%` daytime load).
   - **Penja White Pepper (*Piper nigrum* L., Njombé-Penja, 250 m):** Lowland high-value PGI spice facing living-tutor collapse (*Spondias mombin* root rot); elevated engineered agrivoltaic trellis ($3.5\ \text{m}$) acts simultaneously as disease-free mechanical tutor and thermal shield (`85%` daytime washing/drying load).
   - **Highland Tea (*Camellia sinensis*, Djuttitsa/Ndu, 1,850 m):** Low plucking table ($1.0\ \text{m}$, cheap standard clearance $2.2\ \text{m}$), high midday UV/PAR photoinhibition susceptibility, quality sensitivity (theanine preservation), and substantial electrical load (`380 kWh_el/t` median across `250–600 kWh_el/t`, separated from `4,500 kWh_th/t` biomass drying heat) split `55%` daytime CTC/sorting vs. `45%` **overnight withering** (evaluated across no-BESS, 2h LFP buffer, and full overnight BESS).
2. **Physical Honesty on Quantum Coherence Under Sunlight (No Uncomputed Numbers):** We explicitly test — rather than assume or inflate — whether spectral shaping by ST-OPVs alters antenna excitation transfer efficiency $\eta_{\text{ET}}$ in **higher-plant 14-site LHCII** under **continuous-wave incoherent thermal sunlight** (Non-Equilibrium Steady State, NESS), and bound its maximum propagation through the coupled FVCB–Medlyn biochemical system across both electron-transport-limited ($A_j$, deep shade) and RuBisCO-limited ($A_v$, field irradiance) regimes. No numerical upper bound is claimed until computed directly from the pipeline.
3. **Mandatory Technological Counterfactual (ST-OPV LUE Pareto vs. Spaced Opaque c-Si AV):** Rather than fixing an unphysical flat $10.5\%$ PCE across $\text{APT} \in [35\%, 70\%]$, the full TMM stack (`ITO/ZnO/PM6:Y6/MoO3/Ag/MoO3`) derives coupled $\text{PCE}(\text{APT})$ along the $\text{LUE} = \text{PCE} \times \text{APT}$ Pareto front ($T_{80}=5\ \text{yr}$ outdoor vs. $10\text{–}25\ \text{yr}$ sensitivity), benchmarked head-to-head against mature **spaced opaque monocrystalline c-Si** ($\text{PCE}=20.5\%$, $\beta_T = -0.38\,\%/^\circ\text{C}$, 25-yr life, $\text{GCR} \in [0.20, 0.70]$).

---

## 2. Scientific Methodology & Physical Approximation Hierarchy

### 2.1 Microscopic LHCII Model & Justification of Approximations

Previous drafts borrowed bacterial FMO Hamiltonians (absorbing 750–820 nm) and brute-force pulsed HOPS dynamics. This is physically inappropriate for higher plants:

| Physical Aspect | Legacy Draft Error | Revised Physically Consistent Formulation |
|---|---|---|
| **Pigment-Protein Complex** | 7/8-site bacterial FMO (NIR 750–820 nm) | **14-site plant LHCII monomer** (8 Chl *a* [602–604, 610–614], 6 Chl *b* [601, 605–609]; PAR 400–700 nm; Novoderezhkin et al., *PCCP* 2011) |
| **Illumination State** | Femtosecond pulsed excitation | **CW incoherent AM1.5G solar NESS**: steady thermal photon pumping $k_{\text{pump},\alpha}(T_{\text{OPV}})$ into exciton eigenstates without coherent laser beats (Brumer & Shapiro; Kassal et al.) |
| **Primary Quantum Solver** | Brute-force 100-traj 48-mode HOPS | **Hybrid Modified Redfield ($|J_{nm}|>15\ \text{cm}^{-1}$) – Generalized Förster ($|J_{nm}|\le 15\ \text{cm}^{-1}$)** retaining Drude-Lorentz + 48 vibrational modes ($N=200$ static disorder realizations) |
| **Role of MesoHOPS v1.8.0** | Heavy production sweeps | **Targeted Error-Bound Benchmark only:** `mesohops.tensor.HopsTensorTrajectory` ($N\approx 32$, reduced bath: Drude-Lorentz + 2 dominant resonant modes $\sim 340, 740\ \text{cm}^{-1}$) on the bottleneck Chl *b*→Chl *a* transfer pocket to quantify $|\eta_{\text{HOPS}} - \eta_{\text{mR-GF}}|$ |

#### Scale-Bridging Equations (LHCII NESS → FVCB Electron Transport)
1. **Steady-State Exciton Population $\rho_{\text{NESS}}$:** Under continuous solar irradiance $S_{\text{inc}}(\lambda) = S_{\text{AM1.5G}}(\lambda) T_{\text{OPV}}(\lambda)$, the exciton steady state solves:
   $$\mathcal{L}_{\text{mR-GF}}[\rho_{\text{NESS}}] + \mathcal{P}_{\text{solar}}[S_{\text{inc}}](\rho_g) - (\Gamma_{\text{RC}} + \Gamma_{\text{nr}})\rho_{\text{NESS}} = 0$$
   yielding trapped excitation quantum efficiency $\eta_{\text{ET}}(T_{\text{OPV}}) = \text{Tr}[\Gamma_{\text{RC}}\rho_{\text{NESS}}] / \text{Tr}[\mathcal{P}_{\text{solar}}[S_{\text{inc}}](\rho_g)]$, compared cleanly against unfiltered AM1.5G ($\Delta\eta_{\text{NESS}}$).
2. **Two-Regime Biochemical Coupling:**
   $$A(I_{\text{ePAR}}, T_l, \text{VPD}) = \min\big(A_v(T_l, C_i),\ A_j(J)\big) - R_d(T_l), \quad J = \frac{\phi_{\text{PSII}} \alpha_{\text{leaf}} \eta_{\text{ET}}^{\text{norm}} I_{\text{ePAR}} + J_{\max} - \sqrt{(\dots)^2 - 4\theta_J \dots}}{2\theta_J}$$
   - **Regime A (Deep Shade / Low Light, $A = A_j$):** $\partial A / \partial \eta_{\text{ET}} > 0$; spectral filtering effects on antenna routing propagate linearly into $J$, though bounded by $\Delta\eta_{\text{NESS}}$.
   - **Regime B (Midday Sun / Light-Saturating, $A = A_v$):** RuBisCO carboxylation caps assimilation; $\partial A / \partial \eta_{\text{ET}} \equiv 0$.
   - The true seasonal **quantum-relevance multiplier** $g_c = Y(\eta_{\text{ET}}^{\text{filt}}) / Y(\eta_{\text{ET}}^{\text{AM1.5G}})$ is integrated dynamically across hourly tropical irradiance histograms — never assumed beforehand.

---

### 2.2 Optical Radiative Transfer, Diffuse Sky & Spectral Metrics (ST-OPV vs. c-Si)

For ST-OPV stacks (PM6:Y6 baseline, tunable donor:acceptor and Ag electrode thicknesses scanning $\text{APT} \in [0.35, 0.70]$ and $\text{GCR} \in [0.30, 0.85]$), the **Transfer Matrix Method (TMM)** computes complex angle- and polarization-resolved transmittance $T_{\text{OPV}}(\lambda, \theta)$ over $300\text{–}2500\ \text{nm}$.

- **Cameroon Highland Sky Decomposition:** Effective transmitted spectral flux explicitly separates beam and isotropic diffuse sky components ($f_{\text{diff}} \in [0.26, 0.50]$ across ERA5 2023 wet/dry seasons):
  $$S_{\text{sub}}(\lambda, t) = S_{\text{beam}}(\lambda, t)\,T_{\text{OPV}}(\lambda, \theta_z(t)) + S_{\text{diff}}(\lambda, t)\int_0^{\pi/2} T_{\text{OPV}}(\lambda, \vartheta)\sin(2\vartheta)\,d\vartheta$$
- **Three Biological Spectral Diagnostics:**
  1. **Classical PAR ($400\text{–}700\ \text{nm}$)** & **Extended ePAR ($400\text{–}750\ \text{nm}$):** Captures Emerson enhancement of PSI/PSII balance by far-red photons where PM6:Y6 absorbs selectively.
  2. **Red:Far-Red Ratio ($\text{R:FR} = \Phi_{655\text{–}665}/\Phi_{725\text{–}735}$):** Tracks phytochrome photomorphogenic signaling (critical for Penja pepper internode elongation and tea flushing).
  3. **Spaced Opaque c-Si Counterfactual:** Evaluates geometric strip transmittance $T_{\text{Si}}(\lambda, t) = (1 - \text{GCR}_{\text{Si}}) + \text{GCR}_{\text{Si}}\cdot 0$ combined with higher electrical yield ($20.5\%$ PCE, $0.5\%/\text{yr}$ degradation, elevated $3.5\ \text{m}$ steel BOS) to reveal exact spectral vs. geometric trade-offs.

---

### 2.3 Leaf Energy Balance, Microclimate & Stomatal Coupling (Medlyn + FAO-56)

To avoid attributing all shade benefits to light alone, the leaf microclimate closes the **coupled steady-state energy budget**:
$$(1 - \rho_{\text{SW}})R_{\text{SW,sub}} + \varepsilon_l \Big[(1 - F_{l\to p})\varepsilon_{\text{sky}}\sigma T_a^4 + F_{l\to p}\varepsilon_p \sigma T_p^4 - \sigma T_l^4\Big] - H(T_l - T_a, g_b) - \lambda E(g_s, \text{VPD}_l) = 0$$
where panel temperature $T_p$ rises above ambient air temperature $T_a$ under solar absorption ($1 - \text{PCE} - T_{\text{SW}}$), injecting **downward longwave infrared (LWIR) flux** onto the canopy according to the mounting view factor $F_{l\to p}$ (particularly critical when mounting clearance drops to $2.2\ \text{m}$ over $1.0\ \text{m}$ tea).

Stomatal conductance follows the **Medlyn optimal model** coupled iteratively with FVCB assimilation $A$ and leaf-to-air vapor pressure deficit $\text{VPD}_l(T_l)$:
$$g_s = g_0 + 1.6\left(1 + \frac{g_1}{\sqrt{\text{VPD}_l}}\right)\frac{A}{C_a}$$
Combined with seasonal FAO-56 soil water deficit ($K_c = 0.95$ coffee, $1.05$ pepper, $1.00$ tea), this captures **midday stomatal reopening** under shading cooling ($T_l$ and $\text{VPD}_l$ drop) as well as midday **PSII photoinhibition relief** when $I_{\text{PAR}} < I_{\text{PI}}$.

---

### 2.4 Interpretative Decompositions & Dimensionless Regime Atlas

Instead of simply plotting NPV curves, the modeling outputs four interpretative diagnostics:

1. **Four-Lever Causal Attribution of Crop Yield Shift ($\Delta Y_{\text{crop}}$):** Exact Shapley/Oaxaca-style variance decomposition isolating:
   - $\Delta Y_{\text{PAR/PI}}$: Photosynthetic light saturation & photoinhibition relief;
   - $\Delta Y_{\text{therm}}$: Thermal cooling ($\Delta T_l$) net of downward panel LWIR flux;
   - $\Delta Y_{\text{VPD/H}_2\text{O}}$: Stomatal reopening via lower $\text{VPD}_l$ and retained soil moisture;
   - $\Delta Y_{\text{spec/Q}}$: ePAR PSI/PSII balance, R:FR shift, and bounded quantum $\Delta\eta_{\text{NESS}}$.
2. **$\Delta ET_c$ Partitioning:** Decomposes crop evapotranspiration savings into radiative ($R_n$ reduction) vs. aerodynamic/stomatal ($\text{VPD}_l, g_s$) terms.
3. **2D Dimensionless Regime Maps (Phase Diagrams):**
   - *Agronomic Phase Space:* $\big(\text{PAR}_{\text{peak}} / I_{\text{sat}},\ \text{VPD}_{\text{peak}}\big)$ identifying where shading increases yield (photoinhibition + VPD stress regimes) vs. where it penalizes yield (cloudy highland light-limitation regime).
   - *Technological Break-Even Boundary (ST-OPV vs. Spaced c-Si):* $\big(T_{80}^{\text{OPV}},\ C_{\text{mod}}^{\text{OPV}} / C_{\text{BOS}}^{\text{Si}}\big)$ and $(\text{GCR},\ \text{APT})$ contours showing the exact threshold where spectral selectivity + low-CAPEX mounting defeats 25-year c-Si.
4. **Techno-Economic Risk & LCA (ISO 14040/14044):**
   - 20-year DCF ($\text{WACC} = 10\%$ baseline, sensitivity $6\text{–}15\%$), **5-year ST-OPV replacement sinking fund**, captive diesel displacement ($0.45\ \text{USD/kWh}$ vs. $0.085\ \text{USD/kWh}$ grid), **zero carbon credit / zero subsidy baseline** (with $+25\ \text{USD/tCO}_2\text{e}$ and $40\%$ subsidy as sensitivity panels), and $N=10,000$ Monte Carlo Sobol indices ($S_i, S_{Ti}$).

---

## 3. Work Packages & Execution Roadmap

| WP | Deliverable | Gate / Verification Criterion |
|---|---|---|
| **WP1: Primary Parameter Extraction** `[DONE ✅ 2026-11-12]` | Extracted 3× 14×14 LHCII Hamiltonians (`H1, H2, H3`), `1RWT/2BHW` dipoles, dispersive `(n,k)` (`300–1100 nm`), FvCB–Medlyn traits (`PMC3990704`, `PMC11622609`, `PMC10957798`), and ERA5 2023 `8760 h` climate series (`data/wp1/`, `WP1_Parameter_Source_Ledger.md`). | Zero `[VERIFY]` tags remaining in `parameters.yaml` (`v2.5.0`); `make test` (`4/4` OK) passed. |
| **WP2: Quantum Bound & Validation** | Implement Modified Redfield–Förster + CW NESS solver (`scripts/quantum_ness.py`). Run targeted MesoHOPS v1.8.0 (`HopsTensorTrajectory`) benchmark ($N=32$) on HPC (`100.73.21.40`, `MesoHOP-sim-18`) after checking `free -g`. | Verify $|\eta_{\text{HOPS}} - \eta_{\text{mR-GF}}|$ error bound and compute exact $\Delta\eta_{\text{NESS}}$ & two-regime $g_c$ bounds. |
| **WP3: Optical TMM + ST-OPV vs. c-Si** | Angle/diffuse-resolved TMM (`ITO/ZnO/PM6:Y6/MoO3/Ag/MoO3`) resolving LUE-coupled $\text{PCE}(\text{APT})$ Pareto front + spaced c-Si counterfactual ($\beta_T=-0.38\,\%/^\circ\text{C}$); output PAR, ePAR, R:FR, soiling & solar electrical generation. | Reconcile simulated short-circuit $J_{sc}$ & $\text{LUE} = \text{PCE} \times \text{APT}$ (`2.5–4.2%`) against published PM6:Y6 and c-Si benchmarks. |
| **WP4: Microclimate & Crop Engine** | Coupled bidirectional $(T_{\text{pv}}, T_{\text{leaf}})$ + LWIR + Medlyn + FVCB (including finite coffee $g_m$) + FAO-56 (`8760 h`) engine producing seasonal $\Delta Y$, $\Delta ET_c$, WUE, and 4-lever attributions across Foumbot, Djuttitsa/Ndu, Penja. | Reproduce baseline monoculture yields ($850, 800, 1800\ \text{kg/ha}$), coffee cooling ($-2\text{ to }-4\ ^\circ\text{C}$), and tea PV-trial yield trend ($+9\text{ to }+15\%$). |
| **WP5: TEA, Dispatch, LCA & Phase Maps** | 20-year DCF (5-yr OPV replacement), diurnal load matching (`380 kWh_el/t` tea `[250–600]`, `55%` day / `45%` overnight withering, 3 LFP BESS options), dual-FU ISO LCA (`kgCO2e/ha/yr` vs `gCO2e/kWh`), 10k Sobol Monte Carlo, and 2D regime phase diagrams. | Positive vs. negative $\Delta\text{NPV}$ and carbon break-even $T_{80}^*$ boundaries cleanly separated across ST-OPV vs. c-Si counterfactuals. |
| **WP6: Manuscript Drafting** | Elsevier *Renewable Energy* LaTeX manuscript (~7,500–8,500 words, 6 publication-grade interpretative figures) + complete SM. | BMAD adversarial pre-submission review passes all 6 reviewer-kill scenarios. |
