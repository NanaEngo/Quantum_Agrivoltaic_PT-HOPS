# Data Analysis Report — Cameroon Tri-Crop ST-OPV Agro-Photovoltaics (WP1–WP6 Synthesis)

**Package:** `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript`  
**Configuration Baseline:** `parameters.yaml` (`framework_version: 2.5.0`)  
**Date:** `2026-11-13` (rev. 2 — adds WP3b coupled audit §3.3 and final verification gates §7)  
**Purpose:** Comprehensive quantitative synthesis of WP1–WP6 verified datasets underpinning the *Renewable Energy* (`RE_main_2611.tex` + `RE_SM_2611.tex`) manuscript, its figure audit (§6) and final verification gates (§7). All metrics below are traced directly to local primary JSON/CSV/NPZ artifacts and ledgered peer-reviewed sources (`0 USD/tCO₂e` carbon-credit baseline; `0%` direct grant/subsidy baseline).

---

## Executive Synthesis & Core Thesis

Across three contrasting Cameroon agro-ecological highlands (**Foumbot** — *Coffea arabica*, `1044 m`; **Njombe-Penja** — *Piper nigrum L.* Penja PGI white pepper, `273 m`; **Djuttitsa** — *Camellia sinensis* highland tea, `1400 m`), coupling first-principles transfer-matrix ST-OPV optics (`PM6:Y6`), open-quantum exciton–vibrational NESS bounds, hourly ERA5 `8760 h` microclimate + FvCB–Medlyn photosynthesis + FAO-56 soil water balance, and cooperative-scale TEA/LCA/Sobol propagation reveals three structurally decisive findings:

1. **Quantum coherence (`|Δη_NESS| ≤ 3.37 × 10⁻⁵`; `≤ 2.10 × 10⁻³` exact-HEOM envelope) is decoupled from macroscopic agrivoltaic performance (`Sobol S_Ti = 2.10 × 10⁻⁸` on `ΔNPV`, `≤ 2.59 × 10⁻⁷` worst-case HEOM/zero-carbon),** whereas **microclimatic shade–water–radiation partitioning** and **cooperative processing dispatch** drive `O(10⁴–10⁵ USD/ha)` economic divergence.
2. **A sharp Seasonal Sign-Inversion Regime governs tropical agrivoltaics:** shading increases yield cleanly during high-VPD, high-radiation dry hours (`+8.8%` to `+30.2%` across crops under `S3_OPV_APT44_GCR65`, and up to `+49.7%` in irrigated *Penja* pepper `S5`), whereas continuous fixed shading penalizes wet-season light-limited assimilation (`-15.9%` in Foumbot coffee, `-8.6%` in Djuttitsa tea, `0.0%` in Penja white pepper), turning total annual agronomic response negative in coffee (`-7.08%`), mildly negative in tea (`-3.35%`), and robustly **rainfed-positive in Penja white pepper (`+7.43%` to `+8.16%`)**.
3. **Co-located processing load & cost/lifetime thresholds separate technical viability from financial parity:** On-site cooperative processing transforms Djuttitsa tea with overnight LFP BESS (`LSF = 99.92%`) into an electricity/cooling-integrated profit engine (`NPV = $860,825/ha`, `IRR = 35.52%`, `LCOE = $0.0886/kWh`, `LCA = 32.66 g CO₂e/kWh`), avoiding `393.2 tCO₂e/ha/yr`; however, without grid export (`off-grid no-export`), only high-load tea remains profitable (`+$319,794/ha` vs `-$379,752/ha` for coffee). Against elevated c-Si (`S2_cSi_GCR40`), ST-OPV achieves **LCA break-even in `7.40–8.12 yr`**, while **NPV parity (`P = 11.0%–23.0%`) requires R2R module manufacturing costs near `$15/m²` paired with operational lifetime `T80* ≥ 16.33 yr` (pepper) or `31.27 yr` (coffee)**.

---

## 1. Site Climate & Botanical Separation (WP1)

### 1.1 ERA5 2023 Site Climes (`8760 h/site`)

| Crop & Site | Elev. (`m`) | Annual $T_{\text{mean}}$ $[T_{\min}, T_{\max}]$ (`°C`) | GHI (`kWh m⁻² d⁻¹` / `yr⁻¹`) | Diffuse Fraction (Ann / Wet / Dry) | Daytime Mean VPD (Dry p95 / max, `kPa`) | Rain (`mm/yr`) |
|---|---|---|---|---|---|---|
| **Arabica Coffee** (Foumbot, `5.518°N, 10.597°E`) | `1044` | `22.21 [14.0, 35.0]` | `5.382` (`1964.6`) | `0.365 / 0.416 / 0.260` | `1.381` (`4.07 / 4.85`) | `1904.5` |
| **Penja White Pepper** (Njombe-Penja, `4.675°N, 9.680°E`) | `273` | `24.72 [19.8, 35.8]` | `4.593` (`1676.4`) | `0.461 / 0.502 / 0.360` | `0.890` (`2.83 / 4.75`) | `2321.0` |
| **Highland Tea** (Djuttitsa, `5.448°N, 10.066°E`) | `1400` | `19.86 [14.2, 31.0]` | `4.900` (`1788.6`) | `0.412 / 0.486 / 0.273` | `0.922` (`3.03 / 3.80`) | `2320.3` |

### 1.2 Penja White Pepper (*Poivre blanc de Penja*, IGP) vs Generic Black Pepper Verification

A dedicated parameter audit confirmed zero conflation between PGI **Penja white pepper** and generic black pepper across `parameters.yaml` (`v2.5.0`) and `docs/WP1_Parameter_Source_Ledger.md`:
- **Clean dry white pepper yield (`800.0 kg/ha`)**: reflects ~24% dry white kernel recovery from red-ripe berries (vs ~33–36% whole-berry dried black pepper).
- **Farm-gate & PGI export pricing (`5,000 XAF/kg` baseline within `3,500–6,000 XAF/kg`; `14,000 XAF/kg` certified PGI upper tier)**: reflects processed white kernels rather than unretted black pepper.
- **Post-harvest electric demand (`45.0 kWh_el/t`, `85%` daytime share)**: explicitly sized for water-retting pump circulation (7–10 days), mechanical pulp decortication/washing, and fan-assisted solar drying specific to Penja white pepper.
- **Ecophysiological gas exchange (`Piper nigrum L.`)**: shared at species level from `PMC11622609` and `Oliveira2018_Piper` (`V_cmax25 = 44.6`, `J_max25 = 65.0 μmol m⁻² s⁻¹`, `g_0 = 0.01`, `g_1 = 3.4`, photoinhibition PPFD threshold `900 μmol m⁻² s⁻¹`).

---

## 2. Transfer-Matrix Optical Pareto & Quantum NESS Bounds (WP2)

### 2.1 Optical Pareto Frontier (`120` Stacks, `PM6:Y6`)
- Energy balance verification: max `|R + T + A - 1| = 4.44 × 10⁻¹⁶`.
- Opaque validation (`75 nm` Ag): `J_sc = 25.701 mA/cm²`, `PCE = 15.501%` vs experimental benchmark `16.27%` (*Nat. Commun.* 2025, `10.1038/s41467-025-67379-z`).
- Across `24` Pareto-optimal designs (`23` retained in `parameters.yaml`): `APT ∈ [14.54%, 52.06%]`, maximum Light Utilization Efficiency `LUE_max = 4.424%` (YAML) / `4.486%` (full grid).
- **Focal ST-OPV stack (`APT44`):** `d_act = 60 nm`, `d_Ag = 12 nm`, `d_cap = 35 nm` → **`APT = 44.12%`**, **`PCE = 9.93%`** (standard AM1.5G), selectively absorbing UV and NIR (`700–900 nm`) while transmitting blue/green/red PAR bands (`R:FR` spectral ratio preserved near natural canopy levels).

### 2.2 Quantum NESS Bound & MesoHOPS v1.8.0 Cross-Verification
- Under CW solar steady state (`N = 200` static disorder realizations, `T = 295 K`) across three published 14-site LHCII Hamiltonians (`H1`, `H2`, `H3`) using non-orthogonal `1RWT`/`2BHW` dipoles:
  - Open RC (`k_rc = 0.005 ps⁻¹`): **`max |Δη_NESS| = 3.370 × 10⁻⁵` (`H1`), `1.936 × 10⁻⁵` (`H2`), `6.125 × 10⁻⁶` (`H3`)**.
  - Quenched NPQ (`1.5 ns⁻¹`): `3.06 × 10⁻⁵` (`H1`), `1.83 × 10⁻⁵` (`H2`), `5.96 × 10⁻⁶` (`H3`).
  - Sweeping `k_rc ∈ [0.0033, 0.5] ps⁻¹`: **`|Δη_NESS| ≤ 1.181 × 10⁻⁵`**.
  - 4-site exact QuTiP-BoFiN HEOM cross-check: `|η_HEOM - η_Pauli| = 0.00210` (`H2`), `0.000106` (`H3`).
- Full non-Markovian 14-site **MesoHOPS v1.8.0** pulsed-excitation benchmark (`N = 48`, `2000 fs`, max trace norm deviation `≤ 1.11 × 10⁻¹⁵`):
  - Transient site-population MAE vs secular Pauli (`H2_DL_K1 = 0.0198`, `H3_DL_K1 = 0.2017`, `H3_DL_K1_Vib340 = 0.2200`; `p_terminal_final_hops = 0.0835` vs `pauli = 0.4035`), confirming **substantial transient vibronic coherence on femtosecond–picosecond pulsed timescales (WP2/Paper 1 consistency)** that washes out completely under incoherent continuous-wave (`CW`) solar illumination (`Δη_NESS ~ 10⁻⁵`).

---

## 3. Microclimate, Seasonal Regime Inversion & 4-Lever Shapley Attribution (WP3–WP4)

Energy balance residual across all `124` scenario runs is `≤ 1.569 × 10⁻⁵ W/m²` and Shapley additivity residual is `≤ 7.105 × 10⁻¹⁵ %`.

### 3.1 Focal Scenario Performance Across Crops (`S0`–`S5`)

| Crop | Scenario | Canopy Shade (`%`) | Annual $\Delta Y$ (`%`) | Dry $\Delta Y$ (`%`) | Wet $\Delta Y$ (`%`) | Dry $\Delta T_{\text{leaf}}$ (`°C`) | Low-PPFD Fraction $F_{\text{lp}}$ | $\Delta \text{ET}$ (`%`) | $\Delta \text{WUE}$ (`%`) | PV Yield (`MWh/ha/yr`) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Coffee** | `S3_OPV_APT56_GCR50` | `25.7` | `-1.21` | `+9.02` | `-6.96` | `-1.61` | `0.291` | `-8.36` | `+7.80` | `717.0` |
| **Coffee** | `S3_OPV_APT44_GCR65` | `40.6` | `-7.08` | `+8.82` | `-15.88` | `-2.51` | `0.378` | `-16.56` | `+11.35` | `1223.3` |
| **Coffee** | `S5_OPV_APT44_GCR65_Irrig` | `40.6` | `+0.22` | `+38.23` | `-15.88` | `-3.45` | `0.378` | `+0.07` | `+0.15` | `1223.3` |
| **Penja Pepper** | `S3_OPV_APT56_GCR50` | `25.9` | `+7.27` | `+19.57` | `+1.53` | `-1.69` | `0.277` | `-3.53` | `+11.19` | `611.7` |
| **Penja Pepper** | `S3_OPV_APT52_GCR65` | `36.0` | `+8.16` | `+27.56` | `+0.04` | `-2.39` | `0.361` | `-6.11` | `+15.19` | `870.2` |
| **Penja Pepper** | `S3_OPV_APT44_GCR65` | `40.8` | `+7.43` | `+30.24` | `-1.36` | `-2.67` | `0.361` | `-7.28` | `+15.87` | `1043.7` |
| **Penja Pepper** | `S5_OPV_APT44_GCR65_Irrig` | `40.8` | `+12.25` | `+49.68` | `-1.36` | `-3.10` | `0.361` | `+2.96` | `+9.02` | `1043.7` |
| **Highland Tea** | `S3_OPV_APT56_GCR50` | `25.8` | `+0.01` | `+11.26` | `-3.47` | `-1.51` | `0.320` | `-7.64` | `+8.29` | `652.5` |
| **Highland Tea** | `S3_OPV_APT44_GCR65` | `40.7` | `-3.35` | `+15.98` | `-8.84` | `-2.40` | `0.416` | `-13.64` | `+11.92` | `1113.3` |
| **Highland Tea** | `VAL_cSi_Shade47pct` | `47.0` | `-4.98` | `+17.64` | `-11.15` | `-2.70` | `0.175` | `-15.04` | `+11.83` | `1615.3` |
| **Highland Tea** | `S5_OPV_APT44_GCR65_Irrig` | `40.7` | `+2.47` | `+41.38` | `-8.84` | `-3.17` | `0.416` | `+1.72` | `+0.74` | `1113.3` |

*(All rows above verified directly against `data/wp3/wp3_crop_microclimate_scenarios.csv`; `S2_cSi_GCR40` gives Coffee `ΔY = -6.38%`, Tea `-2.30%`, Penja Pepper `+6.95%`; `LER` reaches `1.401–1.548` under `S3_OPV_APT44_GCR65` and `1.474–1.596` under `S5_OPV_APT44_GCR65_Irrig`.)*
- **Heavy shade penalty (`70%` c-Si `S2_cSi_GCR70` or `S3_OPV_APT20_GCR85`):** severe yield loss of **`-16.8%` to `-28.1%`**, establishing an agronomic upper shade ceiling well below `50%` for all three crops.

### 3.2 Physical Mechanism & 4-Lever Causal Attribution (`Shapley`)
- **Penja White Pepper `S3_OPV_APT52_GCR65` (`+8.16%` annual):** Shapley decomposition demonstrates that **thermal/VPD relief (`+18.00%`)** and **soil-moisture conservation (`+4.64%`)** decisively outweigh the **direct PAR reduction penalty (`-13.93%`)**, while **spectral R:FR/diffuse quality (`-0.55%`)** is a second-order contributor (`sum = +8.16%`, residual `≤ 7.1×10⁻¹⁵%`).
- **Low-PPFD threshold inversion (`VPD_p95` vs `F_lp`):** In cloudy wet months (`diffuse fraction 0.42–0.50`), `36.1%–41.6%` of daytime hours under `GCR=65%` fall into low-PPFD light-limitation, driving the negative wet-season ΔY in Foumbot coffee (`-15.88%`) and Djuttitsa tea, whereas Njombe-Penja white pepper's low saturating irradiance (`900 μmol m⁻² s⁻¹` photoinhibition threshold, shade-adapted *Piper* vine) avoids wet-season loss (`+0.04%`).

---

### 3.3 WP3b Coupled Hydraulics Sweep, Monsoon-Open Louver Counterfactual & Climate Stress

All values verified directly against `data/wp3/wp3b_structural_and_louver_audit.json` (regenerable via `scripts/wp3b_structural_and_louver_audit.py`, reproduced by `tests/test_wp3b_structural_and_louver_audit.py`).

- **Soil-plant hydraulics sweep (`AWC ∈ {120, 160, 220}` mm × `g_b ∈ {0.6, 1.2, 2.5}` mol m⁻² s⁻¹):** the focal `S3_OPV_APT44_GCR65` annual ΔY spans `−13.40 % … +6.42 %` (coffee), `−4.42 % … +29.17 %` (Penja pepper) and `−8.21 % … +6.13 %` (tea). The matched-shade c-Si counterfactual tracks it closely: the OPV−cSi gap stays within **`−1.14 … +2.41` pp** across the whole 9-cell grid (coffee `−0.96…−0.22` pp, pepper `−0.47…+2.41` pp, tea `−1.14…−0.89` pp), and the grid center reproduces the WP3 focal run to `≤ 8.9 × 10⁻¹⁶` pp — crop-ranking conclusions are insensitive to hydraulic-parameter uncertainty.
- **Monsoon-open louver counterfactual (`S6`, panels opened June–October):** nearly eliminates the wet-season PAR penalty — coffee wet ΔY `−15.88 % → −5.58 %` (annual `−7.08 % → +0.30 %`, rescue `+7.38` pp), tea wet `−8.84 % → +0.32 %` (annual `−3.35 % → +1.50 %`, `+4.85` pp), Penja pepper wet `−1.36 % → +0.34 %` (annual `+7.43 % → +8.65 %`). The honest cost: monsoon PV output collapses `−38.0 % … −39.9 %` (coffee `1223.3 → 738.8` MWh/ha/yr), giving `ΔNPV = −$349.6k … −$678.2k/ha` vs fixed tilt and a break-even actuation CAPEX of **`$0.00/m²`** — the open-louver scenario never beats fixed-tilt `S3` on NPV and trails irrigated dynamic shading `S5` by `$357.7k–717.2k/ha`. The wet-season loss is therefore light-harvest-limited (sub-saturation diffuse hours), not a correctable geometric-shade defect.
- **Synthetic climate stress (warm-dry: `ΔT +1.5 °C`, `RH −5 pp`, `precip ×0.75`, `GHI ×1.05`, diffuse `−0.05`; cool-cloudy: `ΔT −1.0 °C`, `RH +5 pp`, `precip ×1.25`, `GHI ×0.90`, diffuse `+0.08`):** confirms the seasonal inversion mechanism at both ends — warm-dry flips Foumbot coffee annual OPV ΔY positive (`−7.08 % → +1.28 %`), amplifies Penja pepper (`+7.43 % → +16.67 %`, OPV−cSi gap `+1.38` pp) and tea (`→ +1.67 %`); cool-cloudy deepens penalties (coffee `−12.82 %`, tea `−7.77 %`, pepper `+0.74 %`, gaps `−0.05…−1.10` pp). The sign of the OPV-vs-c-Si crop ranking is robust under both perturbations.

---

## 4. Cooperative Dispatch, TEA/LCA Break-Even & Sobol Global Sensitivity (WP5)

### 4.1 Processing Catchment Dispatch (`S3_OPV_APT44_GCR65`, `0 USD/tCO₂e`, `0%` Subsidy)
- **Cooperative electricity loads:** Coffee `3000 ha → 63.8 MWh/yr`; Penja Pepper `2000 ha → 72.0 MWh/yr`; Djuttitsa Tea `450 ha → 307.8 MWh/yr` (`45%` overnight withering share).
- **Djuttitsa Tea BESS sensitivity (`S3_OPV_APT44_GCR65`):**
  - `no_bess`: `LSF = 62.68%`, `NPV = $724,075/ha`, `IRR = 38.65%`, `LCA = 28.46 g CO₂e/kWh`
  - `2h_buffer`: `LSF = 74.30%`, `NPV = $785,722/ha`, `IRR = 39.02%`
  - `overnight_bess`: `LSF = 99.92%`, `NPV = $860,825/ha`, `IRR = 35.52%`, `LCOE = $0.0886/kWh`, `LCA = 32.66 g CO₂e/kWh`, avoiding `393.2 tCO₂e/ha/yr`.
- **Off-grid without export (`off-grid no-export`):** Tea remains strongly viable (`NPV = +$319,794/ha`, `IRR = 20.06%`) due to high captive factory load, whereas low-load Coffee turns deeply negative (`NPV = -$379,752/ha`).

### 4.2 Break-Even Thresholds ($T_{80}^*$) vs Elevated c-Si (`S2_cSi_GCR40`)
- **LCA Carbon Break-Even ($T_{80,\text{LCA}}^*$):** `7.42 yr` (Coffee), `7.40 yr` (Penja Pepper), `8.12 yr` (Tea) — well within realistic mid-term encapsulated NFA stability targets (`~8–10 yr`).
- **Economic Break-Even ($T_{80,\text{NPV}}^*$):**
  - At current early-commercial OPV module cost (`$35/m²`): **`Inf`** across all 3 crops (NPV parity cannot be reached via lifetime extension alone before year-30 horizon).
  - At mature R2R manufacturing target (**`$15/m²`**): **`16.33 yr`** (Penja White Pepper), **`31.27 yr`** (Arabica Coffee), and **`Inf`** (Tea, because c-Si higher areal power density captures more grid/dispatch revenue under identical `GCR`).

### 4.3 Sobol Global Sensitivity (`N = 10,000` Saltelli Sequences, Seed 42)
- **Probability of ST-OPV NPV exceeding elevated c-Si (`P(NPV_OPV > NPV_Si)`):**
  - **Penja White Pepper:** **`22.99%`** (median `ΔNPV = -$105.3k/ha`, `p05–p95: [-$394.4k, +$116.9k]`)
  - **Arabica Coffee:** **`16.75%`** (median `ΔNPV = -$139.3k/ha`, `[-$437.6k, +$90.2k]`)
  - **Highland Tea:** **`11.00%`** (median `ΔNPV = -$176.0k/ha`, `[-$490.0k, +$58.0k]`)
- **Total-order Sobol indices ($S_{T_i}$) for $\Delta\text{NPV} = \text{NPV}_{\text{OPV}} - \text{NPV}_{\text{Si}}$:**
  1. `c_mod_opv` (`OPV module cost`): **`0.323 – 0.366`** (dominant driver)
  2. `t80_opv` (`OPV T80 lifetime`): **`0.247 – 0.267`**
  3. `c_bos_si` (`elevated c-Si steel/concrete BOS cost`): **`0.150 – 0.170`**
  4. **Quantum NESS bound (`Δη_NESS`):** **`2.10 × 10⁻⁸` max on comparative `ΔNPV`** (`3.83 × 10⁻⁹` Coffee, `2.10 × 10⁻⁸` Pepper, `9.85 × 10⁻⁹` Tea; on single-system `NPV_OPV`: `1.16 × 10⁻⁹`, `7.15 × 10⁻⁹`, `1.89 × 10⁻⁹`). Under adversarial `wp5b_sobol_robustness.py` checks widening the quantum envelope to `±0.21%` (4-site HEOM gap) and fixing `0 USD/tCO₂e` (`zero_carbon`), `S_Ti(ΔNPV) ≤ 2.59 × 10⁻⁷` and `P(>c-Si) = 12.33%–24.72%`, proving microscopic–macroscopic decoupling in steady-state deployment economics.

---

## 5. Recommended Manuscript Framing Strategy (*Renewable Energy*)

1. **Refuse techno-optimistic bias & clarify matched-shade counterfactual:** Lead honestly with why ST-OPV presently loses `77%–89%` of baseline policy Monte Carlo NPV draws (`75%–88%` at fixed zero carbon) against elevated c-Si (`$35/m²` baseline), while demonstrating **exact quantitative levers** (`c_mod_opv ≤ $15/m²` AND `T80 ≥ 16.3 yr` for Penja pepper) plus the already favorable **carbon payback (`7.4–8.1 yr`)**. Emphasize matched-shade crop equivalence vs `S2_cSi_GCR40` (`<= 1.05 pp` difference; `phi_{spec+Q} = -0.21% to -0.67%`).
2. **Pair Agro-Seasonality with Crop–Climate Match:** Position **Njombe-Penja PGI White Pepper** (`+7.4%` to `+8.2%` rainfed yield gain via `+18.0%` thermal/VPD Shapley relief exceeding `-13.9%` PAR loss, plus `$350/ha/yr` avoided living-tutor cost) as the standout wet/dry resilient shade-crop archetype, while prescribing **drought-only dynamic shading or supplemental irrigation (`S5`)** in Foumbot coffee (`+38.2%` dry boost) and **captive factory BESS dispatch** in Djuttitsa tea.
3. **Quarantine Quantum Coherence to its Valid Boundary Condition:** Frame Section 4 around our bounded scale-separation analysis (`|Δη_NESS| ≤ 3.37 × 10⁻⁵`, HEOM envelope `≤ 2.10 × 10⁻³` → `S_Ti(ΔNPV) ≤ 2.60 × 10⁻⁷`), reconciling ultrafast 2DES/MesoHOPS coherence (`MAE = 0.22`) with CW solar reality rather than claiming macroscopic quantum crop yield gains.

---

## 6. Visual Audit of Figures 1–6 & Mitigations Applied

All six figures (`figures/Fig1..Fig6.{pdf,png}`) were rendered with `scienceplots` (`["science", "no-latex"]`) + `seaborn` (`0.13.2`), inspected visually at `180–200 DPI`, and refined iteratively before final `600 DPI` PNG/PDF locking:

1. **Fig. 1 (`Fig1_Optical_Pareto_Spectral_TMM`):** Relocated `LUE=2.5%` / `3.5%` / `4.5%` contour labels inward with opaque white pills (`APT = 43.2%–53.5%`) so zero collision occurs with the lower-left legend or x-axis label; expanded Panel (b) `ylim` to `(0, 88)` (`ncol=2` legend) and Panel (c) `ylim` to `(0.922, 1.016)` so all spectral and R:FR curves clear the legends cleanly.
2. **Fig. 2 (`Fig2_Quantum_NESS_Bound_Benchmark`):** Standardized Panel (b) legend strings (`Open RC (no NPQ)`, `Quenched (NPQ 1.5 ns⁻¹)`) with `ylim(0, 41)` headroom above the `33.7 ppm` upper bound; raised Panel (c) log-scale `ylim` to `(1e-4, 320)` so the legend never overlaps the `Tea` or `Penja Pepper` classical bar.
3. **Fig. 3 (`Fig3_Microclimate_Cooling_Dry_Wet_Regimes`):** Extended Panel (a) `ylim` down to `(-3.35, 0.10)` with a 2-column bottom legend clearing all `ΔT_leaf` bars; repositioned Panel (b) regime callouts inside clean whitespace with white `bbox`; expanded Panel (c) `ylim` to `(-118, 34)` and moved the combined bar+line legend to `lower right` clear of all `ΔET_rad` bars.
4. **Fig. 4 (`Fig4_Four_Lever_Causal_Attribution_Phase`):** Raised Panel (a) `ylim` to `(-24.0, 34.5)` so the `+24.96%` `Pepper OPV APT44` stacked bar clears the `ncol=2` top legend; eliminated the `Tea` / `Penja Pepper` label collision in Panel (b) via leader-arrow offsets (`Penja Pepper` placed left at `1.42`, `Tea` right at `2.36`), boxed `Neutral (ΔY = 0%)` cleanly, and marked the `PAR95/Isat = 2.20` modeled domain boundary explicitly.
5. **Fig. 5 (`Fig5_Dispatch_TEA_LCA_BreakEven`):** Raised Panel (b) `ylim` to `(0, 42)` above the `32.7 gCO2e/kWh` Tea bar; replaced vertical dark-on-red `ΔLCA = 0` text in Panel (c) with a horizontal white-backed badge (`ΔLCA = 0 (7.4 yr)`) and moved `ΔNPV = 0` to `(11.8, 0.24)` clear of the green R2R parity star (`$15/m², 16.3 yr`).
6. **Fig. 6 (`Fig6_Sobol_Uncertainty_LER_Policy`):** Widened Panel (a) `xlim` to `(-540, 395)` to give `P(>c-Si)=23.0%` generous right padding; aligned Panel (b) so BOTH classical levers and the bounded quantum lever read from the same `ΔNPV` Sobol output (`S_Ti = 2.1 × 10⁻⁸ (bounded)`); standardized `USD/t` / `25 USD/tCO2e` typography in Panel (c).

---

## 7. Verification Gates & Manuscript Integration (WP6)

- **Integrity tests:** `27 passed` (`pytest`, `MesoHOP-sim` env, verified `2026-11-13`) across `tests/test_wp1_data_integrity.py`, `test_wp2_tmm_and_quantum.py`, `test_wp3_microclimate_crop.py`, `test_wp3b_structural_and_louver_audit.py`, `test_wp5_tea_lca_sobol.py`, `test_wp6_manuscript_integrity.py` — including config consistency against `parameters.yaml` (`framework_version: 2.5.0`) via `scripts/check_config.py`.
- **Compilation (pdflatex + bibtex, zero errors / zero undefined references or citations):** `RE_main_2611.pdf` **21 pp**, `RE_SM_2611.pdf` **6 pp**, `RE_Cover_letter_2611.pdf` **1 p**, `RE_Highlights_2611.pdf` **1 p**.
- **Figures:** `Fig1`–`Fig6` (`pdf` + `png`) regenerated end-to-end by `scripts/wp6_generate_figures.py` from the primary `data/wp*` artifacts audited above.
- **Open before upload:** fetch + read the *Renewable Energy* Guide for Authors (never fetched); create an RE-specific upload checklist; ORCID pending.
