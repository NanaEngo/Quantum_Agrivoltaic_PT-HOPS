# WP5 Verification Summary — TEA, 8760 h Dispatch, Dual-FU LCA, Sobol QMC & 2D Regime Phase Maps

* **Script:** `scripts/wp5_tea_lca_sobol.py` (pandas-free, reads `parameters.yaml` `v2.5.0` & WP3 outputs)
* **Tests:** `tests/test_wp5_tea_lca_sobol.py`
* **Outputs:** `data/wp5/wp5_tea_lca_scenarios.csv`, `data/wp5/wp5_sobol_sensitivity.json`, `data/wp5/wp5_phase_maps.npz`, `data/wp5/wp5_validation_summary.json`

## 1. Cooperative Agro-Industrial 8760 h Dispatch & LFP Storage Regimes

One hectare (`10,000 m²`) of overhead PV produces `~650–1,480 MWh/yr` depending on `(GCR, APT)`, exceeding single-hectare farm crop processing demand (`21–684 kWh/ha/yr`) by three orders of magnitude. WP5 therefore models the `1 ha` agrivoltaic array as a cooperative agro-industrial hub sized to regional Cameroon estates (`COOP_CATCHMENT_HA`: `450 ha` Highland Tea factory = `307.8 MWh/yr` with `45%` overnight withering; `3,000 ha` Arabica Coffee union = `63.8 MWh/yr`; `2,000 ha` Penja Pepper drying/washing union = `72.0 MWh/yr`), displacing rural diesel (`0.45 USD/kWh`) with excess sold at marginal grid tariff (`0.085 USD/kWh`) under strict PV-to-load energy conservation (`max_dispatch_err = 4.42e-09 kWh`).

- **Highland Tea (`S3_OPV_APT44_GCR65`):**
  - `no_bess_daytime_only`: self-consumption `16.75%`, Load Solar Fraction `62.68%`, `NPV = $724,075/ha`, `IRR = 38.65%`, `LCOE = 0.0687 USD/kWh`, `28.46 gCO2e/kWh`
  - `small_lfp_buffer_2h`: self-consumption `19.86%`, Load Solar Fraction `74.30%`, `NPV = $785,722/ha`, `IRR = 39.02%`, `LCOE = 0.0727 USD/kWh`, `29.32 gCO2e/kWh`
  - `overnight_withering_bess`: self-consumption `26.70%`, Load Solar Fraction `99.92%`, `NPV = $860,825/ha`, `IRR = 35.52%`, `LCOE = 0.0886 USD/kWh`, `32.66 gCO2e/kWh`, net avoided `CO2` `= 393.2 tCO2e/ha/yr`
  - Off-grid without grid export (`S5_offgrid_no_export`): Tea remains strongly viable (`NPV = +$319,794/ha`, `IRR = 20.06%`, `DPBP = 6.61 yr`), whereas Coffee turns negative (`-$379,752/ha`) because coffee milling demand alone cannot amortize a full 1-ha array.

## 2. 20-Year DCF Benchmarks (`0 USD/t` Carbon, `0%` Subsidy) & Dual-FU ISO LCA Break-Even

| Crop | Scenario | NPV (`USD/ha`) | IRR (`%`) | DPBP (`yr`) | LCOE (`USD/kWh`) | LCA (`gCO2e/kWh`) | LER |
|---|---|---:|---:|---:|---:|---:|---:|
| Coffee | `S0_open_control` | 28,390 | — | — | — | — | 1.000 |
| Coffee | `S3_OPV_APT44_GCR65` (`2h`) | 403,544 | 26.16 | 3.95 | 0.0637 | 26.16 | 1.401 |
| Coffee | `S4_OPV_T80_15yr` (`2h`) | 584,211 | 31.93 | 3.79 | 0.0451 | 10.84 | 1.401 |
| Coffee | `S2_cSi_GCR40` (`2h`) | 779,311 | 34.77 | 3.52 | 0.0380 | 18.92 | 1.507 |
| Penja Pepper | `S0_open_control` | 55,689 | — | — | — | — | 1.000 |
| Penja Pepper | `S3_OPV_APT44_GCR65` (`2h`) | 368,372 | 24.74 | 5.73 | 0.0750 | 30.73 | 1.548 |
| Penja Pepper | `S4_OPV_T80_15yr` (`2h`) | 548,969 | 30.56 | 3.98 | 0.0532 | 12.78 | 1.548 |
| Penja Pepper | `S2_cSi_GCR40` (`2h`) | 709,051 | 32.55 | 3.80 | 0.0449 | 22.31 | 1.640 |
| Highland Tea | `S0_open_control` | 42,599 | — | — | — | — | 1.000 |
| Highland Tea | `S3_OPV_APT44_GCR65` (`over`) | 860,825 | 35.52 | 3.01 | 0.0886 | 32.66 | 1.429 |
| Highland Tea | `S4_OPV_T80_15yr` (`over`) | 1,042,110 | 39.71 | 2.93 | 0.0681 | 15.85 | 1.429 |
| Highland Tea | `S2_cSi_GCR40` (`over`) | 1,272,579 | 41.66 | 2.83 | 0.0555 | 23.46 | 1.548 |

- **Critical Non-Trivial Break-Even Findings (`S3_OPV_APT44_GCR65` vs `S2_cSi_GCR40`):**
  - **Carbon Intensity Parity ($T_{80,\text{LCA}}^*$):** Due to `3` module replacements over `20 yr`, `5-yr` baseline ST-OPV (`26.2–32.7 gCO2e/kWh`) temporarily trails `c-Si` (`18.9–23.5 gCO2e/kWh`), crossing carbon parity at **`T80_lca* = 7.42 yr` (Coffee), `7.40 yr` (Penja Pepper), and `8.12 yr` (Tea)**.
  - **NPV Parity ($T_{80,\text{NPV}}^*$):** At baseline module cost (`35 USD/m²`), lifetime extension alone (`T80 -> 25 yr`) cannot reach NPV parity with 20.5%-efficient `c-Si` (`T80_npv* = Inf`); roll-to-roll cost compression to `15 USD/m²` brings finite economic parity in **Penja Pepper at `T80* = 16.33 yr`** (`31.27 yr` in Coffee).

## 3. Global Sobol QMC Sensitivity (`N = 10,000`, Seed `42`)

- Joint probability `P(NPV_OPV > NPV_cSi)`: **`16.75%` (Coffee)**, **`22.99%` (Penja Pepper)**, **`11.00%` (Tea)**.
- Top 3 total-order variance drivers ($S_{Ti}$) for `Delta NPV(OPV - c-Si)`: `c_mod_opv_usd_m2` (`0.323–0.366`), `t80_opv_yr` (`0.247–0.267`), and `c_bos_si_usd_m2` (`0.150–0.170`).
- Quantum NESS antenna efficiency variance contribution on `NPV_OPV`: **$S_{Ti}(\Delta\eta_{\text{NESS}}) \le 1.0 \times 10^{-8}$** across all three crops, proving classical techno-economic and optical parameters dominate system risk by more than 7 orders of magnitude.
