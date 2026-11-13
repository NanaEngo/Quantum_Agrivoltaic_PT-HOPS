# WP3 & WP4 Verification Summary (`8760 h` Bidirectional Microclimate, FvCB–Medlyn Ecophysiology & Exact Shapley Attribution)

**Date:** 2026-11-13
**Package:** `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/`
**Engine:** `scripts/wp3_microclimate_crop_engine.py`
**Test Suite:** `tests/test_wp3_microclimate_crop.py` (`Ran 14 tests in 0.287s — OK` locally; verified across WP1 + WP2 + WP3)

---

## 1. Coupled Physics & Numerical Closure (`124` Scenarios across `3` Crops)

- **Wall Time (`--workers 3`):** `15.08 s`
- **Maximum Energy Balance Residual ($\max |R_n - H - LE|$):** `1.569e-05 W/m²` (coupled 14-iteration Newton–Raphson solver for $T_{\text{pv}} \leftrightarrow T_{\text{leaf}} \leftrightarrow (A_{\text{net}}, g_s)$ across 8760 hourly ERA5 steps).
- **Maximum Exact 4-Lever Shapley Residual:** `7.105e-15 %` (exact 16-corner attribution across `PAR_PI`, `therm`, `VPD_H2O`, and `spec_Q`).
- **Penman–Monteith ET Partitioning Conservation:** exact algebraic split $LE = LE_{\text{rad}} + LE_{\text{aero}}$ (`|ET - (ET_rad + ET_aero)| < 1e-2 mm/yr` on all 124 scenarios).
- **Biophysical Formulation:**
  - Two-sided planar sunlit leaf energy balance ($0.92 \times \alpha_{\text{SW}} G_{\text{sub}}$, downward sky+array LWIR modulated by clearance-dependent view factor $F_{l\to p}$, underside vegetation LWIR at $T_{\text{air}}$, sheltered canopy boundary-layer conductance $g_b$).
  - Kattge & Knorr (2007) $T_{\text{growth}}$-acclimated peaked Arrhenius optima ($T_{\text{opt},V}/T_{\text{opt},J} = 31.0/28.0\ ^\circ\text{C}$ Foumbot *Coffea arabica*, $33.0/30.0\ ^\circ\text{C}$ Penja *Piper nigrum*, $30.0/26.5\ ^\circ\text{C}$ Djuttitsa *Camellia sinensis*).
  - Dynamic PSII photoinhibition $q_I$ state with $\tau_{\text{repair}} = 4.0\text{ h}$ D1 protein repair time constant.
  - Martins et al. (2014) $C_c$-basis finite mesophyll conductance acclimation ($g_{m25}$) on *Coffea arabica*; $C_i$-basis FvCB–Medlyn on *Piper nigrum* and *Camellia sinensis*.
  - FAO-56 hourly bucket water balance (`AWC = 160.0 mm` with deep perennial stress floor $k_s \ge 0.38$, 1-year spinup).

---

## 2. Empirical & Interpretative Benchmark Results

| Crop (Site, Altitude) | Open $S_0$ Base (kg/ha) | $S_0$ Dry Day $T_l$ (°C) | $S_1$ Agroforestry $\Delta Y$ / $\Delta T_l^{\text{dry}}$ | Representative ST-OPV (`APT`, `GCR`) | ST-OPV $\Delta Y_{\text{ann}}$ ($\Delta Y_{\text{dry}}$ / $\Delta Y_{\text{wet}}$) | Shapley Levers `[PAR_PI, therm, VPD_H2O, spec_Q]` (%) | $\Delta ET_c$ / $\Delta WUE$ (%) | PV Yield (MWh/ha/yr) |
|---|---:|---:|---|---|---|---:|---:|---:|
| **Arabica Coffee** (Foumbot, 1044 m) | 850.0 | 31.08 | `-2.35%` / `-2.13 °C` | `S3_OPV_APT56_GCR50` (sh `25.7%`) | **`-1.21%`** (`+9.02%` / `-6.96%`) | `[-10.82, +6.45, +3.37, -0.210]` | `-8.36%` / `+7.80%` | 717.0 |
| **Penja White Pepper** (Njombe-Penja, 273 m) | 800.0 | 32.81 | `+7.96%` / `-1.77 °C` | `S3_OPV_APT52_GCR65` (sh `36.0%`) | **`+8.16%`** (`+27.56%` / `+0.04%`) | `[-13.93, +17.99, +4.64, -0.551]` | `-6.11%` / `+15.19%` | 870.2 |
| **Highland Tea** (Djuttitsa, 1400 m) | 1800.0 | 27.79 | `-1.81%` / `-2.48 °C` | `S3_OPV_APT56_GCR50` (sh `25.8%`) | **`+0.01%`** (`+11.26%` / `-3.47%`) | `[-6.99, +4.73, +2.48, -0.207]` | `-7.64%` / `+8.29%` | 652.5 |

### Key Non-Trivial Physical Findings (Honest Regime Trade-offs)
1. **Dry-vs-Monsoon Phase Inversion:** Across all three sites, agrivoltaic shading rescues dry-season assimilation (`+8.8% to +30.2%` rainfed, `+38% to +50%` under irrigated `S5` dry-season relief) by cooling sunlit leaves by `-1.6 to -2.7 °C` (right within BREEDCAFS `-2 to -4 °C` tropical observations) and lowering $ET_c$ (`-6.1% to -16.6%`). Conversely, excessive static shade (`S2_cSi_GCR70`, `S3_OPV_APT20_GCR85`, `70%` shade) causes severe monsoon PAR deficit (`-23.6% to -38.9%` wet-season loss) and negative annual yield (`-16.8% to -28.1%`).
2. **Highland Tea Altitude/Cloud Contrast (`VAL_cSi_Shade47pct`):** At cool cloudy Djuttitsa (1400 m; monsoon $T_{\text{air}} \approx 21\ ^\circ\text{C}$, $G_{\text{day}} \approx 399\ \text{W/m}^2$), 47% opaque static c-Si shading yields `+17.64%` in dry season (and `+42.58%` under `S5` dry-season irrigation at GCR 40%) but incurs `-11.15%` monsoon PAR penalty, yielding `-4.98%` annual net (`-0.03%` at `GCR=30%`, `+0.01%` under `OPV_APT56_GCR50`). High-APT (`\ge 52%`) ST-OPV or modest GCR (`\le 30%`) avoids cool-monsoon over-shading while generating `652–1031 MWh/ha/yr`.
3. **Confined LWIR Clearance Effect ($F_{l\to p}$):** Confined `1.2 m` tea clearance increases downward array LWIR view factor ($F_{l\to p} = 0.416$ at GCR 65%) relative to `1.4 m` coffee ($0.378$) and `1.5 m` ventilated Penja pepper trellis ($0.361$).
4. **WP2 $\Delta\eta_{\text{NESS}}$ & Spectral Filtering (`spec_Q`):** PM6:Y6 acceptor absorption (`700–850 nm`) slightly depresses ePAR/PAR (`spec_Q = -0.21% to -0.55%`), while the WP2 LHCII quantum coherence shift ($\Delta\eta_{\text{NESS}} < 3.4 \times 10^{-5}$) bounds $< 0.01\%$ impact on annual canopy carbon fixation, quantitatively falsifying quantum-assisted agricultural enhancement claims.

---

## 3. Verification Outputs on Disk

- `data/wp3/wp3_crop_microclimate_scenarios.csv` (`124` scenario rows, `S0`–`S5` + `VAL_cSi_Shade47pct`)
- `data/wp3/wp3_validation_summary.json`
- `data/wp3/hourly_arabica_coffee.npz`, `data/wp3/hourly_penja_white_pepper.npz`, `data/wp3/hourly_highland_tea.npz` (`8760 h` arrays ready for WP5)
- `tests/test_wp3_microclimate_crop.py`
