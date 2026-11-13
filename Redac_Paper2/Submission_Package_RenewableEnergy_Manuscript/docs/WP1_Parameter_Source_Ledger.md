# WP1 Parameter Source Ledger — Cameroon Tri-Crop ST-OPV Agro-Photovoltaics

**Package:** `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript`  
**Config Version:** `parameters.yaml` (`framework_version: "2.5.0"`)  
**Date:** `2026-11-12`  
**Audit Standard:** Zero fabricated values; every parameter traces either to a downloaded local primary dataset (`data/wp1/...`), a peer-reviewed primary table/equation (`DOI` / `PMCID`), or an explicitly tagged `BENCHMARK_RANGE` / `SURROGATE_RANGE` proxy with uncertainty bounds for Sobol/Monte Carlo propagation.

---

## 1. Microscopic LHCII Exciton Hamiltonian & Open Quantum Bath (`lhcii_hamiltonian`, `ness_solar_pumping`)

| Parameter (`parameters.yaml`) | Baseline Value | Sensitivity / Bounds | Local File / Artifact | Primary Literature Source (DOI / PMCID) | Notes |
|---|---|---|---|---|---|
| `hamiltonian_source` (14×14 matrices `H1, H2, H3`) | 3 verified 14×14 matrices (`b601..a614`) | Compare Novoderezhkin 2005/2011 vs Müh 2010 vs MMSIC-MD 2025 | `data/wp1/lhcii_hamiltonians_14site.json`, `data/wp1/PMC11736799.xml` | `10.1021/acs.jctc.4c01214` (Table 2 & Table 3); `10.1039/c1cp21079c`; `10.1021/jp106323e` | Symmetric 14×14 Hermitian matrices (`max_asymmetry = 0.0 cm⁻¹`); `a611–a612 = +129.0`, `a604–b606 = +114.0`, `a603–b609 = +98.0 cm⁻¹`. |
| `dipole_geometry_pdb` | 14 sites (`MG, NB, ND` Qy unit vectors) | `1RWT` (2.72 Å) vs `2BHW` (2.50 Å) | `data/wp1/lhcii_pdb_dipoles.json`, `1RWT.pdb`, `2BHW.pdb` | Liu et al. 2004 *Nature* (`PDB: 1RWT`); Standfuss et al. 2005 (`PDB: 2BHW`); Knox & Spring (`PMC12199089`, `10.1021/acsomega.4c11543`) | Non-orthogonal dipoles preserved for partial-secular Fano interference; `Chl a = 21.0 D²`, `Chl b = 14.7 D²`; `1RWT` `610–611` ($\kappa=-1.812$, $\cos\theta=+0.932$), `611–612` ($\kappa=+1.516$). |
| `drude_lorentz_lambda_cm1` | `50.87 cm⁻¹` | `[35.0, 140.0] cm⁻¹` | `data/wp1/lhcii_hamiltonians_14site.json`, `PMC12063655.xml` | Kim et al. 2025 *Sci. Adv.* (`10.1126/sciadv.ads0327`, `PMC12063655`); MD site reorg `117.9–160.1 cm⁻¹` (`PMC11736799`) | Renger spectral density integral $E_\lambda = 50.87\text{ cm}^{-1}$ (`S=0.65, s1=0.8, s2=0.5, omega1=0.5565, omega2=1.936 cm⁻¹`); Novoderezhkin over-damped lower bound `35.0 cm⁻¹`. |
| `drude_lorentz_gamma_cm1` | `50.0 cm⁻¹` | `[40.0, 100.0] cm⁻¹` | `data/wp1/lhcii_hamiltonians_14site.json` | Novoderezhkin et al. 2005/2011; Kim et al. 2025 (`PMC12063655`) | $\sim 100\text{ fs}$ protein bath correlation time at `295 K`. |
| `static_disorder_fwhm_cm1` | `110.0 cm⁻¹` | `[90.0, 120.0] cm⁻¹` | Literature benchmark (`Novoderezhkin 2005/2011`) | `10.1021/jp055148+`, `10.1039/c1cp21079c` | Gaussian site-energy inhomogeneous broadening over `200` realizations. |
| `resonant_mode_frequencies_cm1` | `[340.0, 740.0] cm⁻¹` | Reduced 2-mode MesoHOPS benchmark | Literature benchmark (FLN/2DES Chl $Q_y$) | Novoderezhkin & van Grondelle; 2DES LHCII benchmarks | Dominant Chl intramolecular modes coupled to $Q_y$; Kim et al. 2025 (`PMC12063655`) confirms protein bath suppresses room-T vibrational impact on steady EET rates. |
| `rc_trapping_rate_ps1` | `0.005 ps⁻¹` (`200 ps`) | `[0.0033, 0.5] ps⁻¹` | Literature benchmark (PSII–LHCII open RC) | Van Amerongen & Croce; `PMC12063655` | `100–300 ps` effective open-RC trapping yields $\Phi_{\text{PC}} \approx 0.91\text{–}0.95$; upper `0.5 ps⁻¹` (`2 ps`) tests isolated terminal-cluster exit sensitivity. |
| `nonradiative_decay_ns1` | `0.25 ns⁻¹` (`4.0 ns`) | `[0.25, 0.263] ns⁻¹` | Literature benchmark (unquenched LHCII) | `3.8–4.0 ns` unquenched LHCII fluorescence lifetime | Competes directly with RC trapping & $q_E$ NPQ sink under varying light intensity. |

---

## 2. ST-OPV Stack Optics, c-Si Counterfactual & LCA (`opv_technology`, `si_counterfactual`, `optical_radiative_model`)

| Parameter (`parameters.yaml`) | Baseline Value | Sensitivity / Bounds | Local File / Artifact | Primary Literature / Dataset Source | Notes |
|---|---|---|---|---|---|
| `optical_nk_dataset` | `300–1100 nm` at `1 nm` (`801` rows) |PM6:Y6 (`1:1.2`), D18:Y6, PM6, ITO, ZnO, MoO3, Ag | `data/wp1/optical_nk_stack_1nm.csv` | Zenodo ellipsometry `10.5281/zenodo.13732081` (`PM6`), `10.5281/zenodo.15624081` (`D18:Y6`); `SIMsalabim` (`nk_Y6.txt`, `nk_ITO.txt`); `refractiveindex.info` (`Glass_lowiron.csv`, `ITO_Konig.csv`, `ZnO_Stelling.csv`, `MoO3_Stelling.csv`, `Ag_Johnson.csv`) | Avoids constant-index `SIMsalabim/nk_Ag.txt` bug by substituting true dispersive Johnson & Christy `Ag_Johnson.csv`. |
| `solar_spectrum_dataset` | AM1.5G (`280–4000 nm`) | Standard terrestrial global tilt | `data/wp1/ASTMG173.csv` | ASTM G-173-03 (`NREL` standard reference spectrum) | Used in TMM `J_sc` and `APT`/`ePAR`/`R:FR` integration. |
| `reference_opaque_cell_pce_percent` | `16.27 %` | `[12.97, 16.27] %` (`53–212 nm`) | `data/wp1/PMC12816033.xml` | *Nat. Commun.* 2025 (`10.1038/s41467-025-67379-z`, Table 1: `75 nm` PM6:Y6) | `J_sc,EQE = 26.36 mA/cm²`, `PCE = 16.27%` at `75 nm`; TMM Pareto validation matches opaque `J_sc` within `10%`. |
| `pce_temp_coeff_per_c` (OPV) | `-0.00008 °C⁻¹` | `[-0.0002, +0.0002] °C⁻¹` | Verified NFA PM6:Y6 benchmark | `-0.008 %/°C` NFA OPV thermal coefficient | Near-zero thermal derating compared to c-Si under high-irradiance dry season. |
| `pce_temp_coeff_per_c` (c-Si) | `-0.0038 °C⁻¹` | `[-0.0042, -0.0032] °C⁻¹` | Standard mono-Si benchmark | `-0.38 %/°C` monocrystalline Si datasheet norm | Drives tropical midday c-Si efficiency loss. |
| `diffuse_fraction_highlands_range` | `[0.26, 0.50]` | Dry (`0.260–0.360`) vs Wet (`0.416–0.502`) | `data/wp1/climate_summary_2023.json` | Open-Meteo Archive ERA5 2023 hourly reanalysis (3 Cameroon sites) | Empirically replaces generic `[0.35, 0.65]` assumption with 8760 h site-specific diffuse decomposition. |
| `lca_embodied_carbon_module_kgco2e_m2` (OPV) | `20.0 kg CO₂e/m²` | `BENCHMARK_RANGE: [12.0, 55.0]` | Espinosa / Krebs / Urbina R2R OPV LCA benchmarks | *Energy Environ. Sci.* / *Sol. Energy Mater. Sol. Cells* R2R OPV cradle-to-gate LCA | Highly sensitive to ITO sputtering + Ag electrode vs 95% Ag recycling and grid carbon intensity. |
| `lca_embodied_carbon_module_kgco2e_m2` (c-Si) | `105.0 kg CO₂e/m²` | `BENCHMARK_RANGE: [55.0, 125.0]` | IEA-PVPS Task 12 benchmark | IEA-PVPS Task 12 mono-Si (`20.2 g CO₂-eq/kWh` module, `35.8 g/kWh` total over 30 yr @ 20.9% PCE) | Evaluated over 20–30 yr system lifetime using `20.2 g/kWh × ~1730 kWh/m²/yr × 30 yr ≈ 105 kg CO₂e/m²`. |

---

## 3. Cameroon 2023 Hourly Climate Datasets (`microclimate` + `crops.*.climate_dataset`)

Source: Open-Meteo Archive API (ERA5 2023 full-year hourly UTC, `8760 h` per site). Processed via `scripts/wp1_extract_climate_era5.py` into `data/wp1/climate_*_2023.csv` and `data/wp1/climate_summary_2023.json`.

| Site (`crop`) | Lat, Lon, Elev (ERA5 grid) | Annual $T_{\text{mean}}$ $[T_{\min}, T_{\max}]$ (°C) | Annual GHI ($\text{kWh m}^{-2}\text{ d}^{-1}$) | Diffuse Fraction (Ann / Wet / Dry) | Daytime Mean VPD (kPa) & Dry p95/max (kPa) | Annual Rain (mm) | Local CSV |
|---|---|---|---|---|---|---|---|
| Foumbot (`arabica_coffee`) | `5.518°N, 10.597°E, 1044 m` | `22.21 [14.0, 35.0]` | `5.382` (`1964.6 /yr`) | `0.365 / 0.416 / 0.260` | `1.381` (dry p95 `4.07`, max `4.85`) | `1904.5` | `data/wp1/climate_foumbot_coffee_2023.csv` |
| Djuttitsa (`highland_tea`) | `5.448°N, 10.066°E, 1400 m` | `19.86 [14.2, 31.0]` | `4.900` (`1788.6 /yr`) | `0.412 / 0.486 / 0.273` | `0.922` (dry p95 `3.03`, max `3.80`) | `2320.3` | `data/wp1/climate_djuttitsa_tea_2023.csv` |
| Njombe-Penja (`penja_white_pepper`) | `4.675°N, 9.680°E, 273 m` | `24.72 [19.8, 35.8]` | `4.593` (`1676.4 /yr`) | `0.461 / 0.502 / 0.360` | `0.890` (dry p95 `2.83`, max `4.75`) | `2321.0` | `data/wp1/climate_njombe_penja_pepper_2023.csv` |

*Explicit Surrogate Flags in `microclimate`*:
- `boundary_layer_conductance_mol_m2_s: 1.2` (`SURROGATE_RANGE: [0.6, 2.5]` computed from ERA5 daytime `wind_u10 = 1.35–2.88 m/s` and leaf characteristic width `0.05–0.12 m`).
- `rainfed_soil_awc_mm: 160.0` (`SURROGATE_RANGE: [120.0, 220.0]` volcanic Andosol/Ferralsol FAO-56 loam default; no destructive Cameroon soil core test in package).

---

## 4. Tri-Crop FvCB + Medlyn Ecophysiology (`crops`)

| Crop | Parameter | Value & Basis | Local Evidence / Literature Source | Notes / Calibration |
|---|---|---|---|---|
| **Arabica Coffee** (`Coffea arabica`) | `V_cmax25`, `J_max25`, `g_m25`, `g_m_shade_acclimation_ratio`, `R_d` | `58.1` (shade $C_c$) / `78.5` (sun $C_c$); `102.7` / `142.6`; `g_m=0.116` (sun) / `0.076` (shade, ratio `0.655`); `R_d=0.5–1.2` | `data/wp1/PMC3990704.xml` (Martins et al. 2014, *PLoS ONE* `PMC3990704`, Tables 1–3) | Explicit $C_c$-basis model (`Gamma*=39.6 ubar, Kc=10.3 uM, Ko=479 uM`); Ethier shade/sun `g_m` ratio `65/109 = 0.596`. |
| **Penja White Pepper** (`Piper nigrum L.`) | `V_cmax25`, `J_max25`, `g_0`, `g_1`, `photoinhibition_ppfd_threshold` | `44.6` ($C_i$-basis), `65.0` ($C_i$-basis), `g_0=0.01`, `g_1=3.4`, `900.0 umol m⁻² s⁻¹` | `data/wp1/PMC11622609.xml` (2024, `10.32615/ps.2024.030`); `data/wp1/Oliveira2018_Piper.html` (`10.1590/1413-70542018425020418`) | Calibrated in FvCB steady state against `PMC11622609` Control `T0` (`PAR=1200, 25°C`: `P_N=7.53±1.28, g_s=0.07±0.01, C_i=215.5±11.2`); `C_c`-basis `[65, 112]` explored in Sobol sensitivity. |
| **Highland Tea** (`Camellia sinensis`) | `A_sat`, `R_d`, `phi_max`, `V_cmax25`, `J_max25`, `photoinhibition_ppfd_threshold` | `10.4` (`6.16–18.82`), `R_d=1.03` (`0.57–1.86`), `phi_max=0.035` (`0.02–0.04`), `V_cmax25=48.0` `[40, 90]`, `J_max25=88.0` `[80, 160]`, `1200.0` | `data/wp1/PMC10957798.xml` (*Bot. Stud.* 2024, `10.1186/s40529-024-00416-0`); `data/wp1/PMC12354480.xml` (2025) | `PMC10957798` shows `Pn, Gs, ETR` saturate/decline above `<1500 umol m⁻² s⁻¹` PPFD (`Fv/Fm=0.73–0.76`). |

---

## 5. Techno-Economic & Industrial Load Parameters (`economics`, `crops.*.processing_*`)

| Parameter (`parameters.yaml`) | Baseline Value | Benchmark / Proxy Bounds | Provenance / Status |
|---|---|---|---|
| `opv_technology.module_cost_usd_per_m2` | `35.0 USD/m²` | `BENCHMARK_RANGE: [10.0, 45.0]` | Machui et al. 2014 *EES* (`9.21 EUR/m²` R2R), Mulligan et al. 2014 (`7.85 USD/m² ±30%`), Gambhir et al. 2016 (`0.28 USD/Wp`, IQR `0.23–0.34 USD/Wp`) up to early commercial `45 USD/m²`. |
| `opv_technology.bos_cost_usd_per_m2` | `20.0 USD/m²` | `BENCHMARK_RANGE: [12.0, 30.0]` | `BENCHMARK_RANGE` lightweight tensile/cable agrivoltaic structure proxy (no local Cameroon tender). |
| `si_counterfactual.module_cost_usd_per_m2` | `45.0 USD/m²` | `BENCHMARK_RANGE: [25.0, 65.0]` | Landed mono-Si `0.12–0.32 USD/Wp` @ `205 Wp/m²` Cameroon import benchmark. |
| `si_counterfactual.bos_structural_cost_usd_per_m2` | `55.0 USD/m²` | `BENCHMARK_RANGE: [35.0, 85.0]` | Elevated 3.5 m galvanized steel / concrete AV mounting `BENCHMARK_RANGE` proxy (no local Douala steel invoice). |
| `economics.bess_lfp_capex_usd_kwh` | `220.0 USD/kWh` | `BENCHMARK_RANGE: [108.0, 280.0]` | Cameroon Douala retail LFP quotes (`195–280 USD/kWh` verified 2024–2025 `5–10 kWh` packs) vs global factory-gate BNEF LFP (`70–108 USD/kWh`). |
| `economics.avoided_pepper_living_tutor_cost_usd_ha_yr` | `350.0 USD/ha/yr` | `BENCHMARK_RANGE: [200.0, 550.0]` | **Explicit regional proxy:** Embrapa Brazil *Gliricidia* vs dead/concrete staking (`27–46%` establishment cost reduction) — propagated with wide bounds pending primary Njombe-Penja survey. |
| `highland_tea.processing_electricity_kwh_tonne` | `380.0 kWh_el/t` | `[250.0, 600.0] kWh_el/t` (`55%` daytime / `45%` overnight) | Tea factory energy audit literature (`250–500 kWh_el/t` CTC/orthodox + up to `600 kWh_el/t` older estates; biomass thermal drying `4500 kWh_th/t` kept separate from electric load). |
