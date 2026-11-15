# Data Analysis Report — Cameroon Tri-Crop ST-OPV Agro-Photovoltaics (WP1–WP6 Synthesis)

**Package:** `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript`  
**Configuration Baseline:** `parameters.yaml` (`framework_version: 2.5.0`)  
**Date:** `2026-11-15` (rev. 5 — adds `wp5d_tariff_residual_sensitivity.json`, splits Cameroon institutional citations across `ENEO_Tariff2024`, `SOCADEL2026Decree`, `IMF2026Cameroon`, `CSPH2026Diesel`, verifies HEOM spectrum independence, renames submission stems to `RENE_*_2611` + `Graphical_Abstract_RENE_2611.{png,pdf}`, and reconciles §7 final state cleanly; primary WP1–WP5 datasets unchanged)  
**Purpose:** Comprehensive quantitative synthesis of WP1–WP6 verified datasets underpinning the *Renewable Energy* (`RENE_main_2611.tex` + `RENE_SM_2611.tex`) manuscript, its figure audit (§6) and final verification gates (§7). Scenario labels in scripts/CSVs (`S0–S5`) map 1:1 to manuscript notation (`D0–D6`, where `D1` is natural agroforestry shade and `S4/D4` is `APT52`). All metrics below are traced directly to local primary JSON/CSV/NPZ artifacts and ledgered peer-reviewed sources (`0 USD/tCO₂e` carbon-credit baseline; `0%` direct grant/subsidy baseline).

---

## Executive Synthesis & Core Thesis

Across three contrasting Cameroon agro-ecological highlands (**Foumbot** — *Coffea arabica*, `1044 m`; **Njombe-Penja** — *Piper nigrum L.* Penja PGI white pepper, `273 m`; **Djuttitsa** — *Camellia sinensis* highland tea, `1400 m`), coupling first-principles transfer-matrix ST-OPV optics (`PM6:Y6`), open-quantum exciton–vibrational NESS bounds, hourly ERA5 `8760 h` microclimate + FvCB–Medlyn photosynthesis + FAO-56 soil water balance, and cooperative-scale TEA/LCA/Sobol propagation reveals three structurally decisive findings:

1. **Quantum coherence (`|Δη_NESS| ≤ 3.37 × 10⁻⁵`; `≤ 2.10 × 10⁻³` exact-HEOM envelope) is decoupled from macroscopic agrivoltaic performance (`Sobol S_Ti = 2.10 × 10⁻⁸` on `ΔNPV`, `≤ 2.59 × 10⁻⁷` worst-case HEOM/zero-carbon),** whereas **microclimatic shade–water–radiation partitioning** and **cooperative processing dispatch** drive `O(10⁴–10⁵ USD/ha)` economic divergence.
2. **A sharp Seasonal Sign-Inversion Regime governs tropical agrivoltaics:** shading increases yield cleanly during high-VPD, high-radiation dry hours (`+8.8%` to `+30.2%` across crops under `S3_OPV_APT44_GCR65` / manuscript `D3`, and up to `+49.7%` in irrigated *Penja* pepper `S5` / `D5`), whereas continuous fixed shading penalizes wet-season light-limited assimilation (`-15.88%` in Foumbot coffee, `-8.84%` in Djuttitsa tea, `-1.36%` in Penja white pepper under `APT44`; `+0.04%` at sparser `APT52`), turning total annual agronomic response negative in coffee (`-7.08%`), mildly negative in tea (`-3.35%`), and rainfed-positive in Penja white pepper (`+7.43%` to `+8.16%`) **for the canonical 2023 baseline year only**. Across the ten deterministic `2014–2023` ERA5 reruns (§3.4), Penja is annual-positive in `7/10` years (median `+2.99%`, mean `+2.73%`, range `−1.43%` to `+7.60%`), the shade-nearest OPV−c-Si annual contrast is positive in `8/10` years (SD `0.19` pp, range `−0.06` to `+0.50` pp), and coffee (median `-8.25%`) and tea (median `-3.36%`) are annual-negative in `10/10` years.
3. **Co-located processing load & cost/lifetime thresholds separate technical viability from financial parity:** On-site cooperative processing transforms Djuttitsa tea with overnight LFP BESS (`LSF = 99.92%`) into an electricity/cooling-integrated profit engine (`NPV = $860,825/ha`, `IRR = 35.52%`, `LCOE = $0.0886/kWh`, `LCA = 32.66 g CO₂e/kWh`), avoiding `393.2 tCO₂e/ha/yr`; however, without grid export (`off-grid no-export`), only high-load tea remains profitable (`+$319,794/ha` vs `-$379,752/ha` for coffee, while load-matched off-grid downsizing recovers positive NPV across all three crops at `0.07–0.39 ha`). Against elevated c-Si (`S2_cSi_GCR40` / `D2`), ST-OPV achieves **LCA break-even in `7.40–8.12 yr`**, while **NPV parity (`P = 11.0%–23.0%`) requires R2R module manufacturing costs near `$15/m²` paired with `T80* ≥ 16.33 yr` in Penja pepper (with coffee and tea not reaching parity inside the tested `≤ 25 yr` range)**.

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
- **Monsoon-open louver counterfactual (`S6` / manuscript `D6`, panels opened June–October):** nearly eliminates the wet-season PAR penalty — coffee wet ΔY `−15.88 % → −5.58 %` (annual `−7.08 % → +0.30 %`, rescue `+7.38` pp), tea wet `−8.84 % → +0.32 %` (annual `−3.35 % → +1.50 %`, `+4.85` pp), Penja pepper wet `−1.36 % → +0.34 %` (annual `+7.43 % → +8.65 %`). The cost is a `38.0 %–40.1 %` reduction in annual PV generation across ST-OPV and c-Si (coffee `1223.3 → 738.8` MWh/ha/yr), giving `ΔNPV = −$349.6k … −$678.2k/ha` vs fixed-tilt ST-OPV (and `−$349,596 … −$784,209/ha` across both technologies) and a break-even actuation CAPEX of **`$0.00/m²`** — the open-louver scenario never beats fixed-tilt `S3` (`D3`) on NPV and trails irrigated dynamic shading `S5` (`D5`) by `$357,696–$826,855/ha`. The wet-season loss is therefore light-harvest-limited (sub-saturation diffuse hours), not a correctable geometric-shade defect.
- **Synthetic climate stress (warm-dry: `ΔT +1.5 °C`, `RH −5 pp`, `precip ×0.75`, `GHI ×1.05`, diffuse `−0.05`; cool-cloudy: `ΔT −1.0 °C`, `RH +5 pp`, `precip ×1.25`, `GHI ×0.90`, diffuse `+0.08`):** confirms seasonal inversion at both ends — warm-dry flips Foumbot coffee annual OPV ΔY positive (`−7.08 % → +1.28 %`), amplifies Penja pepper (`+7.43 % → +16.67 %`, OPV−cSi gap `+1.38` pp) and tea (`−3.35 % → +1.67 %`). Cool-cloudy conditions deepen coffee and tea penalties (`−12.82 %` and `−7.77 %`); pepper remains slightly yield-positive (`+0.74 %`) but its OPV−cSi contrast changes sign from `+1.38` pp (warm-dry) to `−0.05` pp (cool-cloudy), a near-tie reversal. The OPV−cSi contrast remains negative for coffee and tea in both perturbations; the pepper technology ranking is not robust to these two synthetic stresses.

---

## 3.4 2014–2023 Deterministic Weather-Year Sensitivity (WP3, ERA5 reanalysis)

All values here are derived from the ten-year fixed-ERA5 multi-year rerun of the WP3 engine (`scripts/wp3_microclimate_crop_engine.py` with year-indexed climate CSVs) across the three Cameroon site–crop configurations (`arabica_coffee`, `penja_white_pepper`, `highland_tea`). These reruns use timestamp-aware solar geometry and are fully isolated from the canonical 2023 baseline: the 2023 `data/wp3/wp3_crop_microclimate_scenarios.csv` and all `data/wp1` climate CSVs remain untouched. The manifest is at `data/wp3/multiyear_2014_2023/wp3_multiyear_weather_manifest.json`.

The focal scenario `S3_OPV_APT44_GCR65` (manuscript `D3`) across the 10 years yields the following 10-year ranges, medians, and averages (sample SD, `ddof=1`):

| Crop | Avg. annual ΔY (`%`) | Median ΔY (`%`) | σ (`%`) | Min ΔY (`%`) | Max ΔY (`%`) | OPV-positive years / total (`n=10`) |
|---|---|---|---|---|---|---|
| Coffee | −8.62 | −8.25 | 1.26 | −11.45 | −7.08 | 0/10 |
| Penja Pepper | +2.73 | +2.99 | 3.20 | −1.43 | +7.60 | 7/10 |
| Highland Tea | −3.69 | −3.36 | 1.25 | −5.85 | −1.86 | 0/10 |

OPV−c-Si contrast (`ΔY_OPV − ΔY_cSi`, `D3 − D2`) likewise spans each crop decade:

| Crop | Avg. contrast (`pp`) | σ (`pp`) | Min (`pp`) | Max (`pp`) | Positive contrast years / total (`n=10`) |
|---|---|---|---|---|---|
| Coffee | −0.76 | 0.06 | −0.87 | −0.68 | 0/10 |
| Penja Pepper | +0.19 | 0.19 | −0.06 | +0.50 | 8/10 |
| Highland Tea | −1.10 | 0.06 | −1.19 | −1.02 | 0/10 |

**Key qualitative points:** The decade results are not a replacement for the canonical 2023 baseline; the 2023 decision table (§3.1) must stand alone. Penja’s sign-reversal range (`−0.06` to `+0.50` pp) means its technology ranking is conditionally dependent on the particular weather year — robust under some multi-year realizations but not others. The wet-season loss mechanism remains light-harvest limitation (sub-saturation diffuse hours), not correctable geometric shade. The quantum NESS bounds (`|Δη_NESS| ≤ 3.37×10⁻⁵`, HEOM envelope `≤ 2.10×10⁻³`) and their negligible Sobol sensitivity (`S_Ti(ΔNPV) ≤ 2.60×10⁻⁷`) carry over unchanged from §2 into this multi-year context.

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

### 4.3b Estimator stability of the Sobol decomposition (`wp5c`, 2026-11-14)

The published indices come from one scrambled sequence, so they were re-estimated on a resolution ladder (`N = 1250, 2500, 5000, 10,000` base draws) and across three independent scrambles (seeds `42`, `1234`, `2024`), crop by crop (`scripts/wp5c_sobol_convergence.py` → `data/wp5/wp5_sobol_convergence.json`). These are sampling diagnostics for a quasi-Monte Carlo estimator; they are not confidence intervals and they do not turn the deterministic ERA5 years of §3.4 into a probability sample.

- **Driver ranking:** module CAPEX remains the leading hardware driver of `ΔNPV` at every rung and under every scramble (coffee `S_Ti ≈ 0.343–0.349`, pepper `0.366–0.373`, tea `0.323–0.329`).
- **Resolution effect:** at the coarsest rung (`N = 1250`) the three hardware indices differ from their `N = 10,000` values by at most `0.007`.
- **Seed spread at `N = 10,000`:** `S_Ti(C_mod^OPV)` spans `0.343–0.345` (coffee), `0.366–0.369` (pepper), `0.323–0.325` (tea); `S_Ti(T80)` spans `≤ 0.0005`; `S_Ti(C_BOS^c-Si)` spans `≤ 0.0004`.
- **Exceedance probability:** `P(ΔNPV > 0)` spans `16.57–17.15 %` (coffee), `22.90–23.12 %` (pepper), `10.97–11.12 %` (tea) — at most `0.6 pp` across scrambles. The published `16.75 / 22.99 / 11.00 %` values sit inside these ranges.
- **Quantum index:** `S_Ti^Q` moves only in its third significant digit (`3.83–3.84 × 10⁻⁹` coffee, `2.103–2.107 × 10⁻⁸` pepper, `9.85–9.87 × 10⁻⁹` tea), so the scale-separation conclusion is insensitive to the scramble.

Reported in SM §S4.2 (`tab:sobol_convergence`) and in the main-text Sobol paragraph; guarded by `tests/test_wp5_tea_lca_sobol.py::test_sobol_convergence_and_seed_stability`.

---

---

### 4.4 Accepted-Export Sensitivity (`S5_export_acceptance_50pct`)

The baseline WP5 dispatch assumes full grid export of all otherwise-exportable energy. Because the cooperative electricity boundary is modeled, a transparent sensitivity splits the otherwise-exportable annual surplus into accepted export and curtailment (accepted-energy fraction, **not** an hourly kW interconnection cap). Values are verified against `data/wp5/wp5_export_acceptance_sensitivity_20261114.csv` (regenerable via `scripts/wp5_export_acceptance_sensitivity.py`, which runs WP5 in a temporary directory and never overwrites canonical outputs; provenance manifest `wp5_export_acceptance_sensitivity_20261114.json`).

| Crop (selected BESS) | Full-export NPV (`USD/ha`) | 50% accepted-export NPV (`USD/ha`) | ΔNPV vs full export (`USD/ha`) | No-export NPV (`USD/ha`) | Yr-1 export = curtailment (`kWh`) | 20-yr export = curtailment (`kWh`) |
|---|---|---|---|---|---|---|
| Coffee (`small_lfp_buffer_2h`) | `403,543.53` | `11,895.55` | `−391,647.98` | `−379,752.43` | `581,754.70` | `10,740,887.97` |
| Tea (`overnight_withering_bess`) | `860,825.08` | `590,309.49` | `−270,515.59` | `+319,793.89` | `401,726.30` | `7,418,850.25` |
| Penja Pepper (`small_lfp_buffer_2h`) | `368,372.49` | `43,412.03` | `−324,960.46` | `−281,548.43` | `482,696.45` | `8,911,992.58` |

The ordering is preserved across all three cases: full export > 50% accepted export > no export. At 50% acceptance the rejected energy is fully curtailed (Yr-1 export = curtailment; 20-year totals equal), the default full-export arithmetic is unchanged (acceptance fraction `1.0`), and the existing `S5_offgrid_no_export` control remains in the dataset.

### 4.5 Captive-at-Grid-Tariff & Year-20 Residual-Value Sensitivities (`wp5d_tariff_residual_sensitivity.json`)

Generated via `scripts/wp5d_tariff_residual_sensitivity.py` using canonical `wp5_tea_lca_sobol.py` DCF functions without modifying baseline CSVs:
- **Captive-at-MT-grid-tariff counterfactual** (`0.085–0.205 USD/kWh` vs. `0.45 USD/kWh` avoided diesel): Coffee and Penja pepper remain strongly NPV-positive (`D_3` `232.4–288.6` and `144.9–218.4 kUSD/ha`), changing `ΔNPV` by `< 2.4%`. In highland tea (`307.8 MWh/yr`), retaining `575 kWh` overnight BESS compresses `D_3` NPV to `3.5–285.4 kUSD/ha` (`IRR 10.1–19.0%`), whereas daytime-only no-BESS retains `187.1–363.6 kUSD/ha` (`IRR 18.0–25.0%`), showing why overnight LFP storage is driven by off-grid diesel substitution rather than grid arbitrage.
- **Year-20 residual-value sensitivity** (`5/25 = 20%` remaining life on `25-yr` c-Si): Baseline omits `36,000 USD/ha` module-only (`5,351 USD/ha` discounted at `10%` WACC) or `80,000 USD/ha` module+BOS (`11,891 USD/ha` discounted; `11.2–24.9k` at `6%`, `2.2–4.9k` at `15%`), slightly favoring ST-OPV (`1.3–3.5%` of `ΔNPV`). Adding c-Si's `5-yr` residual shifts Penja pepper `$15/m²` parity `T80*` from `16.33 yr` to `18.48 yr` (module-only) or `20.73 yr` (module+BOS).

---

## 5. Recommended Manuscript Framing Strategy (*Renewable Energy*)

1. **Refuse techno-optimistic bias & clarify matched-shade counterfactual:** Lead honestly with why ST-OPV presently loses `77%–89%` of baseline policy Monte Carlo NPV draws (`75%–88%` at fixed zero carbon) against elevated c-Si (`$35/m²` baseline), while demonstrating **exact quantitative levers** (`c_mod_opv ≤ $15/m²` AND `T80 ≥ 16.3 yr` for Penja pepper) plus the already favorable **carbon payback (`7.4–8.1 yr`)**. Emphasize matched-shade crop equivalence vs `S2_cSi_GCR40` (`<= 1.05 pp` difference; `phi_{spec+Q} = -0.21% to -0.67%`).
2. **Pair Agro-Seasonality with Crop–Climate Match:** Position **Njombe-Penja PGI White Pepper** (`+7.4%` to `+8.2%` rainfed yield gain via `+18.0%` thermal/VPD Shapley relief exceeding `-13.9%` PAR loss, plus `$350/ha/yr` avoided living-tutor cost) as the standout shade-tolerant candidate **for the canonical 2023 baseline year only**. This Penja result is baseline-specific, not a decade-robust claim: across the ten deterministic `2014–2023` ERA5 reruns Penja is annual-positive in only `7/10` years (§3.4), so cross-year generalization must be reported as conditional and paired with the open M8 field campaign before deployment claims are made. The conditional prescriptions remain: **drought-only dynamic shading or supplemental irrigation (`S5`)** in Foumbot coffee (`+38.2%` dry boost) and **captive factory BESS dispatch** in Djuttitsa tea.
3. **Quarantine Quantum Coherence to its Valid Boundary Condition:** Frame Section 4 around our bounded scale-separation analysis (`|Δη_NESS| ≤ 3.37 × 10⁻⁵`, HEOM envelope `≤ 2.10 × 10⁻³` → `S_Ti(ΔNPV) ≤ 2.60 × 10⁻⁷`), reconciling ultrafast 2DES/MesoHOPS coherence (`MAE = 0.22`) with CW solar reality rather than claiming macroscopic quantum crop yield gains.

---

## 6. Visual Audit of Manuscript Figures 1–6 & Mitigations Applied

All six figures (`figures/Fig1..Fig6.{pdf,png}`, listed below in manuscript appearance order alongside their file basenames; internal labels use display notation `D0–D4`) were rendered with `scienceplots` (`["science", "no-latex"]`) + `seaborn` (`0.13.2`), inspected visually at `180–200 DPI`, and refined iteratively before final `600 DPI` PNG/PDF locking:

1. **Manuscript Fig. 1 (`Fig1_Optical_Pareto_Spectral_TMM`):** Relocated `LUE=2.5%` / `3.5%` / `4.5%` contour labels inward with opaque white pills (`APT = 43.2%–53.5%`) so zero collision occurs with the lower-left legend or x-axis label; expanded Panel (b) `ylim` to `(0, 88)` (`ncol=2` legend) and Panel (c) `ylim` to `(0.922, 1.016)` so all spectral and R:FR curves clear the legends cleanly; legend uses focal `D3`/`D4` stack notation.
2. **Manuscript Fig. 2 (`Fig3_Microclimate_Cooling_Dry_Wet_Regimes`):** Extended Panel (a) `ylim` down to `(-3.35, 0.10)` with a 2-column bottom legend clearing all `ΔT_leaf` bars (`D0–D3`); repositioned Panel (b) regime callouts inside clean whitespace with white `bbox`; expanded Panel (c) `ylim` to `(-118, 34)` and moved the combined bar+line legend to `lower right` clear of all `ΔET_rad` bars.
3. **Manuscript Fig. 3 (`Fig4_Four_Lever_Causal_Attribution_Phase`):** Renamed Panel (a) title to `Exact Four-Lever Shapley Attribution` and legend entry to `Spectral (ePAR)`; raised Panel (a) `ylim` to `(-24.0, 34.5)` so the `+24.96%` `Pepper OPV APT44` stacked bar clears the `ncol=2` top legend; eliminated the `Tea` / `Penja Pepper` label collision in Panel (b) via leader-arrow offsets (`Penja Pepper` placed left at `1.42`, `Tea` right at `2.36`), boxed `Neutral (ΔY = 0%)` cleanly, and marked the `PAR95/Isat = 2.20` modeled domain boundary explicitly. **Attribution, not field causation:** the figure denotes Shapley apportionment of *modeled* assimilation responses; no paired field measurement exists.
4. **Manuscript Fig. 4 (`Fig5_Dispatch_TEA_LCA_BreakEven`):** Raised Panel (b) `ylim` to `(0, 42)` above the `32.7 gCO2e/kWh` Tea bar (`D2`, `D3`, `D4` notation); replaced vertical dark-on-red `ΔLCA = 0` text in Panel (c) with a horizontal white-backed badge (`ΔLCA = 0 (7.4 yr)`) and moved `ΔNPV = 0` to `(11.8, 0.24)` clear of the green R2R parity star (`$15/m², 16.3 yr`).
5. **Manuscript Fig. 5 (`Fig6_Sobol_Uncertainty_LER_Policy`):** Widened Panel (a) `xlim` to `(-540, 395)` to give `P(>c-Si)=23.0%` generous right padding; aligned Panel (b) so BOTH classical levers and the bounded quantum lever read from the same `ΔNPV` Sobol output (`S_Ti = 2.1 × 10⁻⁸ (bounded)`); standardized `USD/t` / `25 USD/tCO2e` typography in Panel (c).
6. **Manuscript Fig. 6 (`Fig2_Quantum_NESS_Bound_Benchmark`):** Standardized Panel (b) legend strings (`Open RC (no NPQ)`, `Quenched (NPQ 1.5 ns⁻¹)`) with `ylim(0, 41)` headroom above the `33.7 ppm` upper bound; raised Panel (c) log-scale `ylim` to `(1e-4, 320)` so the legend never overlaps the `Tea` or `Penja Pepper` classical bar.

---

## 7. Verification Gates & Manuscript Integration (WP6)

### 7.1 Current Final Package State (`2026-11-15 rev. 5`, Supersedes Intermediate Logs Below)

- **Manuscript & SM deliverables (`RENE_*_2611`):**
  - `RENE_main_2611.pdf` / `.tex`: **20 pp**, **4,705** clean prose words (**5,194** incl. captions; `scripts/count_body_words.py`), **243** abstract tokens (`pdftotext` `≤ 250`), **50** bibliography entries (`RENE_main_2611.bbl`). Zero `\authorcheck`, zero LaTeX errors, zero undefined refs/citations.
  - `RENE_SM_2611.pdf` / `.tex`: **13 pp** (`§S1–S9`, incl. Table `tab:sm_tariff_residual`), **21** bibliography entries (`RENE_SM_2611.bbl`, using split verified Cameroon refs `CameroonLaw2011_022`, `ENEO_Tariff2024`, `SOCADEL2026Decree`, `IMF2026Cameroon`, `CSPH2026Diesel`, `ONCC2024Coffee`).
  - `RENE_Cover_letter_2611.pdf` / `.tex`: **1 p.** (synced metrics, US English).
  - `RENE_Highlights_2611.txt` / `.tex` / `.pdf`: **1 p.** (`5` bullets, `67–80` plain chars `≤ 85`).
  - **Graphical Abstract:** `figures/Graphical_Abstract_RENE_2611.png` (`3590 × 1315 px`, `300 DPI`) + `.pdf` (`scripts/wp6_generate_graphical_abstract.py`, `≥ 1328 × 531 px` Elsevier spec).
- **Test & integrity suite:** **36/36 passed** (`4` subtests; `10/10` YAML blocks, `8/8` datasets via `make check test PYTHON=/home/taamangtchu/miniforge3/envs/qom/bin/python`). Includes WP5d tariff/residual test and `test_wp3b_stress_ranking_reversal_is_reported`.
- **Metadata & release ledger:** `ZENODO_UPLOAD_GUIDE.md` (`4/5` author ORCIDs recorded, PenavoraServer compute credit, no-grant Funding wording matching `RENE_main_2611.tex`); `docs/THREE_READING_AUDIT_20261115.md`; `docs/CHECKLIST_UPLOAD_RenewableEnergy_20261114.md`; `docs/CHECKSUMS_SHA256.txt` (`scripts/make_release_manifest.py`).
- **Remaining pre-portal items:** (1) `T. Goumai Vedekoi` ORCID iD; (2) reserve Zenodo dataset DOI; (3) read *Renewable Energy* Guide for Authors directly in browser (`403` to automated fetch); (4) M8 paired field campaign remains open and is explicitly NOT claimed complete.

### 7.2 Historical Intermediate Checkpoints (Superseded Records Kept for Audit Traceability)

- **WP1–WP5 data generation & M8/WP1b/WP2b/WP5c audits (2026-11-14 rev. 1–2):**
  - *Multi-year weather-year sensitivity (§3.4):* ten deterministic ERA5 reruns (`2014–2023`) on `1,240` focal-scenario rows (`data/wp3/multiyear_2014_2023/wp3_multiyear_scenario_results.csv.gz`); Penja annual-positive `7/10`; shade-nearest OPV−c-Si annual contrast positive `8/10` (`−0.06` to `+0.50` pp); coffee/tea negative `10/10`.
  - *Accepted-export accounting (§4.4):* `S5_export_acceptance_50pct` (`data/wp5/wp5_export_acceptance_sensitivity_20261114.csv`); `183/183` shared canonical rows unchanged (`max residual ≤ 4.66 × 10⁻⁹ kWh`).
  - *Device tolerance (WP2b):* `data/wp2/wp2_device_tolerance.json` (`4,000` draws: APT `40.30–47.75%`, PCE `9.18–10.61%`, photon conservation `4.44 × 10⁻¹⁶`).
  - *Structural wind screening (WP1b):* `data/wp1/wind_load_screening.json` (10 m wind max `4.58–7.03 m/s`, `13.1–30.9 Pa` vs `250–640 Pa` design speeds; no design pressure asserted).
  - *Field protocol (M8):* `docs/FIELD_VALIDATION_PROTOCOL_20261114.md`; *Figures:* `Fig1–Fig6` regenerated via `scripts/wp6_generate_figures.py`.
- **Early draft builds (`2026-11-14`, superseded by `§7.1`):** commit `6a5425c` initial build (`21 pp` main, `6 pp` SM, `72` refs, `~7,500` words) → compression & BMAD pass (`docs/ADVERSARIAL_PASS_20261114.md`, `docs/BMAD_REVIEW_20261114.md`, reducing `72 → 50` refs and `~7,500 → 4,827` prose words -> `20 pp` main / `9 pp` SM) → `REFINEMENT_AUDIT` + 3-reading pass (`19 pp` main / `12 pp` SM / `4,466` words) → Round-3 refinements + `RENE_*_2611` rename in `§7.1` above.
