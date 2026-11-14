#!/usr/bin/env python3
"""WP3 & WP4: Coupled Microclimate (T_pv <-> T_leaf + LWIR), 8760h FvCB-Medlyn-FAO56
Physiology Engine, Seasonal Water Balance, and Exact 4-Lever Causal Attribution.

Covers:
  - 3 Cameroon crops/sites across agro-ecological gradient (2023 ERA5 8760h):
      1. arabica_coffee      (Foumbot, 1044 m, Cc-basis w/ finite gm acclimation)
      2. penja_white_pepper  (Njombe-Penja, 273 m, Ci-basis w/ elevated trellis)
      3. highland_tea        (Djuttitsa, 1400 m, Ci-basis w/ close 2.2 m clearance)
  - Bidirectional coupled steady-state energy balance for PV module (T_pv) and
    canopy leaf (T_leaf), including sky view factor F_{l->p} downward LWIR flux.
  - Coupled FvCB (Aj/Av) + Medlyn stomatal model + FAO-56 daily/hourly rainfed
    soil-water balance (AWC = 160 mm) + midday PSII photoinhibition relief.
  - Self-consistent TMM ST-OPV Pareto strata (GCR 0.30-0.85, beta_T = -0.008%/C) vs.
    spaced opaque monocrystalline c-Si counterfactual (GCR 0.20-0.70, beta_T = -0.38%/C)
    and natural agroforestry shade counterfactual (S1).
  - Exact 16-corner Shapley causal decomposition of yield shift Delta_Y into:
      [1] PAR saturation & photoinhibition relief (Delta_Y_PAR_PI)
      [2] Net thermal leaf shift incl. panel LWIR   (Delta_Y_therm)
      [3] Stomatal VPD + soil-moisture reopening    (Delta_Y_VPD_H2O)
      [4] Spectral ePAR / R:FR & bounded NESS       (Delta_Y_spec_Q)
  - Hourly 8760h outputs saved for WP5 TEA / BESS dispatch / LCA / Monte Carlo.

Usage:
  python scripts/wp3_microclimate_crop_engine.py [--workers 16]
"""

from __future__ import annotations

import os

for _env_var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
    os.environ.setdefault(_env_var, "1")

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
import gzip
import json
import math
from pathlib import Path
import time
from typing import Any, Dict, List, Tuple

import numpy as np
import yaml

PKG_ROOT = Path(__file__).resolve().parent.parent
DATA_WP1 = PKG_ROOT / "data" / "wp1"
DATA_WP2 = PKG_ROOT / "data" / "wp2"
DATA_WP3 = PKG_ROOT / "data" / "wp3"

SIGMA_SB = 5.670374419e-8  # W m^-2 K^-4
CP_AIR_MOL = 29.19         # J mol^-1 K^-1
LAMBDA_VAP_MOL = 44010.0   # J mol^-1 at ~25 C
CA_PPM = 420.0             # Atmospheric CO2 ppm (2023 baseline)
O2_MMOL_MOL = 210.0        # Atmospheric O2 mmol mol^-1
LEAF_EMISSIVITY = 0.96
LEAF_SW_ABSORPTIVITY = 0.50  # Whole-shortwave (300-2500nm) leaf absorption (1 - rho_SW - tau_SW ~ 0.50; PAR ~0.85)
PAR_ABS_LEAF = 0.85


def load_config(config_path: Path | None = None) -> dict:
    """Load parameters from the package baseline or an explicitly supplied config."""
    path = config_path or (PKG_ROOT / "parameters.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_config_path(config_root: Path, value: str | Path) -> Path:
    """Resolve a dataset path relative to its config, while allowing absolute paths."""
    path = Path(value)
    return path if path.is_absolute() else config_root / path


def sat_vapor_pressure_kpa(T_c: np.ndarray | float) -> np.ndarray | float:
    """Tetens formula for saturation vapor pressure (kPa) at T in degC."""
    return 0.61078 * np.exp((17.27 * T_c) / (T_c + 237.3))


def solar_zenith_hourly(lat_deg: float, hours_idx: np.ndarray) -> np.ndarray:
    """Compute hourly solar zenith; accept legacy row indexes or ISO timestamps.

    Timestamp inputs use calendar day-of-year and 365/366-day declination. Numeric
    inputs retain the original 365-day behavior for compatibility with callers.
    """
    lat_rad = np.deg2rad(lat_deg)
    values = np.asarray(hours_idx)
    if np.issubdtype(values.dtype, np.number):
        doy = (values // 24) + 1.0
        year_days = np.full(values.shape, 365.0)
        hour_of_day = values % 24
    else:
        timestamps = [datetime.fromisoformat(str(value)) for value in values]
        doy = np.asarray([stamp.timetuple().tm_yday for stamp in timestamps], dtype=np.float64)
        year_days = np.asarray(
            [366.0 if (stamp.year % 4 == 0 and (stamp.year % 100 != 0 or stamp.year % 400 == 0)) else 365.0
             for stamp in timestamps],
            dtype=np.float64,
        )
        hour_of_day = np.asarray(
            [stamp.hour + stamp.minute / 60.0 + stamp.second / 3600.0 for stamp in timestamps],
            dtype=np.float64,
        )
    # Solar declination (Cooper)
    decl = np.deg2rad(23.45 * np.sin(np.deg2rad(360.0 * (284.0 + doy) / year_days)))
    # Local solar hour angle (assume ERA5 timestamps are UTC; Cameroon ~10E -> +0.67h)
    solar_time = (hour_of_day + 0.67) % 24.0
    hra = np.deg2rad(15.0 * (solar_time - 12.0))
    cos_z = np.sin(lat_rad) * np.sin(decl) + np.cos(lat_rad) * np.cos(decl) * np.cos(hra)
    cos_z = np.clip(cos_z, 0.0, 1.0)
    return np.rad2deg(np.arccos(cos_z))


def load_site_climate(csv_path: Path, lat_deg: float) -> Dict[str, np.ndarray]:
    """Load a single calendar year's ERA5 CSV (plain or gzip) without pandas."""
    cols: Dict[str, List[float]] = {
        "T_air_c": [],
        "rh_pct": [],
        "precip_mm": [],
        "wind_10m_ms": [],
        "sw_ghi": [],
        "sw_direct": [],
        "sw_diffuse": [],
        "vpd_air_kpa": [],
    }
    months: List[int] = []
    timestamps: List[str] = []
    opener = gzip.open if str(csv_path).endswith(".gz") else open
    with opener(csv_path, "rt", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamps.append(row["time"])
            cols["T_air_c"].append(float(row["temperature_2m"]))
            cols["rh_pct"].append(float(row["relative_humidity_2m"]))
            cols["precip_mm"].append(float(row["precipitation"]))
            cols["wind_10m_ms"].append(float(row["wind_speed_10m"]) / 3.6)
            cols["sw_ghi"].append(float(row["shortwave_radiation"]))
            cols["sw_direct"].append(float(row["direct_radiation"]))
            cols["sw_diffuse"].append(float(row["diffuse_radiation"]))
            cols["vpd_air_kpa"].append(float(row["vapor_pressure_deficit"]))
            months.append(int(row["time"][5:7]))

    out = {k: np.asarray(v, dtype=np.float64) for k, v in cols.items()}
    out["month"] = np.asarray(months, dtype=np.int32)
    out["hour_idx"] = np.arange(len(months), dtype=np.int32)
    out["zenith_deg"] = solar_zenith_hourly(lat_deg, np.asarray(timestamps, dtype=str))
    # Safe partitioning into beam & diffuse fractions
    ghi = out["sw_ghi"]
    f_diff = np.where(ghi > 5.0, np.clip(out["sw_diffuse"] / np.maximum(ghi, 1e-6), 0.0, 1.0), 1.0)
    out["f_diff"] = f_diff
    out["f_beam"] = 1.0 - f_diff
    return out


def compute_view_factor_leaf_to_panel(gcr: float, clearance_m: float, svf_bounds: Tuple[float, float]) -> float:
    """Estimate downward LWIR view factor F_{l->p} from GCR and canopy-to-panel clearance.

    Lower mounting clearance (e.g. Djuttitsa tea 1.2 m) exposes leaves to a larger
    panel solid angle than elevated trellises (Penja pepper 3.5 m).
    """
    if gcr <= 1e-6:
        return 0.0
    # Infinite-strip approximation factor modulated by clearance (half-strip W ~ 1.0 m)
    w_half = 1.0
    h = max(0.8, clearance_m)
    geom_base = 1.0 / math.sqrt(1.0 + (h / w_half) ** 2)
    f_min, f_max = svf_bounds
    # Clamped effective view factor scaled by panel GCR
    f_eff = np.clip(geom_base, f_min, f_max) * gcr
    return float(np.clip(f_eff, 0.0, 0.85))


def arrhenius_peaked_kattge(T_k: np.ndarray, val25: float, Ha: float, Hd: float, T_opt_c: float) -> np.ndarray:
    """Kattge & Knorr (2007) peaked Arrhenius temperature response for Vcmax and Jmax."""
    R = 8.31446
    T_ref = 298.15
    T_opt_k = T_opt_c + 273.15
    dS = (Hd / T_opt_k) + R * math.log(Ha / max(1.0, Hd - Ha))
    num = np.exp(Ha * (T_k - T_ref) / (T_ref * R * T_k)) * (1.0 + np.exp((T_ref * dS - Hd) / (T_ref * R)))
    den = 1.0 + np.exp((T_k * dS - Hd) / (T_k * R))
    return val25 * (num / den)


def arrhenius_simple(T_k: np.ndarray, val25: float, Ha: float) -> np.ndarray:
    R = 8.31446
    T_ref = 298.15
    return val25 * np.exp(Ha * (T_k - T_ref) / (T_ref * R * T_k))


def crop_ecophys_regime(crop_cfg: dict) -> Tuple[float, float, float, float]:
    """Return Kattge & Knorr (2007) T_growth-acclimated (Topt_Vcmax, Topt_Jmax) & canopy projection (k_beam, k_diff)."""
    name = crop_cfg["scientific_name"]
    if "Coffea" in name:
        return 31.0, 28.0, 0.72, 0.88
    if "Piper" in name:
        return 33.0, 30.0, 0.72, 0.88
    # Camellia sinensis (coolest 1400 m Djuttitsa T_growth) pruned flat plucking table
    return 30.0, 26.5, 0.85, 0.94


def compute_dynamic_photoinhibition(ppfd_top: np.ndarray, i_pi: float) -> np.ndarray:
    """Dynamic PSII qI photodamage state with 4 h D1 protein repair time constant."""
    decay = math.exp(-1.0 / 4.0)
    dmg = 0.0
    qI = np.zeros_like(ppfd_top, dtype=np.float64)
    for t in range(len(ppfd_top)):
        ex = max(0.0, float(ppfd_top[t]) - i_pi) / 1000.0
        dmg = min(0.55, dmg * decay + 0.16 * (ex ** 1.3))
        qI[t] = dmg
    return 1.0 - qI


def prepare_fvcb_acclimation(crop_cfg: dict, shade_mean: float) -> Tuple[float, float, float, float, float, str, float, float, float, float]:
    """Return acclimated (Vcmax25, Jmax25, gm25, Rd25, alpha_j_base, basis, g0, g1, theta_j, i_pi)."""
    fvcb = crop_cfg["fvcb_medlyn"]
    basis = fvcb["basis"]
    accl_w = min(1.0, max(0.0, (shade_mean - 0.10) / 0.50))
    if "V_cmax25_sun_cc" in fvcb:
        Vcmax25 = (1.0 - accl_w) * float(fvcb["V_cmax25_sun_cc"]) + accl_w * float(fvcb["V_cmax25"])
        Jmax25 = (1.0 - accl_w) * float(fvcb["J_max25_sun_cc"]) + accl_w * float(fvcb["J_max25"])
        gm25 = float(fvcb["g_m25"]) * ((1.0 - accl_w) + accl_w * float(fvcb["g_m_shade_acclimation_ratio"]))
        Rd25 = (1.0 - accl_w) * 1.2 + accl_w * 0.55
    else:
        Vcmax25 = float(fvcb["V_cmax25"])
        Jmax25 = float(fvcb["J_max25"])
        gm25 = 1e6
        Rd25 = float(crop_cfg["R_d"])
    alpha_j_base = max(0.28, min(0.40, float(crop_cfg["phi_max"]) * 7.2)) * (1.0 + 0.06 * accl_w)
    return (
        Vcmax25,
        Jmax25,
        gm25,
        Rd25,
        alpha_j_base,
        basis,
        float(fvcb["g_0"]),
        float(fvcb["g_1"]),
        float(crop_cfg["theta"]),
        float(fvcb["photoinhibition_ppfd_threshold"]),
    )


def compute_fao56_soil_stress(
    precip_mm: np.ndarray,
    sw_ghi: np.ndarray,
    T_air_c: np.ndarray,
    vpd_kpa: np.ndarray,
    tau_sw: np.ndarray,
    kc_crop: float,
    awc_mm: float = 160.0,
    irrigated: bool = False,
) -> np.ndarray:
    """Hourly FAO-56 bucket water balance returning stomatal water-stress factor f_soil in [0.20, 1.0].

    Under agrivoltaic shading, reduced net radiation lowers soil evaporation and
    transpiration demand (ETc), preserving dry-season soil moisture longer than open field.
    """
    n_h = len(precip_mm)
    if irrigated:
        return np.ones(n_h, dtype=np.float64)

    # Hourly Hargreaves/Priestley-Taylor-scaled reference ET0 proxy calibrated to Cameroon highlands (~3.5-5.5 mm/day)
    day_mask = sw_ghi > 5.0
    rn_proxy_wm2 = np.where(day_mask, 0.62 * sw_ghi * tau_sw, 0.0)
    # Priestley-Taylor + VPD aerodynamic term (mm/hour)
    T_k = T_air_c + 273.15
    delta_es = 4098.0 * sat_vapor_pressure_kpa(T_air_c) / ((T_air_c + 237.3) ** 2)
    gamma_psy = 0.066  # kPa/C
    et0_rad = (delta_es / (delta_es + gamma_psy)) * rn_proxy_wm2 * 3600.0 / 2.45e6
    et0_aero = np.where(day_mask, 0.055 * vpd_kpa, 0.005 * vpd_kpa)
    etc_pot_h = np.maximum(0.0, kc_crop * (1.15 * et0_rad + et0_aero))

    # Daily/hourly soil water tracking initialized at 80% of AWC in Jan (or quasi-periodic 2-year spinup!)
    raw_mm = 0.50 * awc_mm  # Readily Available Water (p ~ 0.50 for perennial tree/shrub crops)
    soil_w = 0.85 * awc_mm
    f_stress = np.ones(n_h, dtype=np.float64)
    # Spinup 1 year so Jan 1 reflects post-dry transition consistently
    for pass_idx in range(2):
        for t in range(n_h):
            # Soil moisture stress ks (FAO-56 eq. 84; deep-rooted perennial floor >= 0.38)
            ks = 1.0 if soil_w >= (awc_mm - raw_mm) else max(0.38, soil_w / max(1e-6, awc_mm - raw_mm))
            if pass_idx == 1:
                f_stress[t] = ks
            # Effective rainfall (runoff cap above 25 mm/h + canopy interception 1 mm/rain event)
            eff_rain = min(precip_mm[t], 22.0) * 0.88
            soil_w = min(awc_mm, max(0.0, soil_w + eff_rain - ks * etc_pot_h[t]))
    return f_stress


def solve_fvcb_medlyn_step(
    ppfd_par_can: np.ndarray,
    ppfd_epar_can: np.ndarray,
    f_pi: np.ndarray,
    T_leaf_k: np.ndarray,
    vpd_leaf_kpa: np.ndarray,
    f_soil: np.ndarray,
    eta_ness_ratio: float,
    traits: Tuple[float, float, float, float, float, str, float, float, float, float],
    Topt_v: float,
    Topt_j: float,
    gs_h: np.ndarray,
    Ci_h: np.ndarray,
    A_net_h: np.ndarray,
    n_inner: int = 6,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Shared FvCB + Medlyn coupled stomatal solver used by both energy balance and Shapley corners."""
    Vcmax25, Jmax25, gm25, Rd25, alpha_j_base, basis, g0, g1, theta_j, _ = traits
    alpha_j_eff = alpha_j_base * eta_ness_ratio
    Vcmax_t = arrhenius_peaked_kattge(T_leaf_k, Vcmax25, 65330.0, 200000.0, Topt_v)
    Jmax_t = arrhenius_peaked_kattge(T_leaf_k, Jmax25, 43540.0, 200000.0, Topt_j)
    Rd_t = arrhenius_simple(T_leaf_k, Rd25, 46390.0)
    Gamma_star = arrhenius_simple(T_leaf_k, 42.75, 37830.0)
    Kc_t = arrhenius_simple(T_leaf_k, 404.9, 79430.0)
    Ko_t = arrhenius_simple(T_leaf_k, 278.4, 36380.0)
    gm_t = arrhenius_simple(T_leaf_k, gm25, 49600.0) if basis == "chloroplastic_Cc" else gm25

    i_abs_j = alpha_j_eff * PAR_ABS_LEAF * ppfd_epar_can * f_pi
    disc = np.maximum(0.0, (i_abs_j + Jmax_t) ** 2 - 4.0 * theta_j * i_abs_j * Jmax_t)
    J_t = (i_abs_j + Jmax_t - np.sqrt(disc)) / (2.0 * theta_j)
    Km_t = Kc_t * (1.0 + O2_MMOL_MOL / Ko_t)
    vpd_safe = np.maximum(0.08, vpd_leaf_kpa)

    for _ in range(n_inner):
        Cc = Ci_h - (A_net_h / gm_t) if basis == "chloroplastic_Cc" else Ci_h
        Cc = np.maximum(Gamma_star + 5.0, Cc)
        Av = Vcmax_t * (Cc - Gamma_star) / (Cc + Km_t)
        Aj = J_t * (Cc - Gamma_star) / (4.0 * Cc + 8.0 * Gamma_star)
        A_new = np.where(ppfd_par_can > 2.0, np.minimum(Av, Aj) - Rd_t, -Rd_t)
        gs_target = np.clip(
            np.where(
                ppfd_par_can > 2.0,
                g0 + 1.6 * (1.0 + (g1 * f_soil) / np.sqrt(vpd_safe)) * np.maximum(0.0, A_new) / CA_PPM,
                g0,
            ),
            g0,
            1.2,
        )
        gs_h = 0.55 * gs_target + 0.45 * gs_h
        Ci_h = 0.55 * np.clip(CA_PPM - 1.6 * A_new / np.maximum(gs_h, 1e-4), Gamma_star + 10.0, CA_PPM) + 0.45 * Ci_h
        A_net_h = 0.55 * A_new + 0.45 * A_net_h
    return A_net_h, gs_h, Ci_h


def solve_coupled_microclimate_and_assimilation(
    climate: Dict[str, np.ndarray],
    crop_cfg: dict,
    micro_cfg: dict,
    tau_par: np.ndarray,
    tau_sw: np.ndarray,
    epar_over_par: np.ndarray,
    r_fr_ratio: np.ndarray,
    eta_ness_ratio: float,
    gcr: float,
    pce_pv_ref_pct: float,
    beta_pv_per_c: float,
    a_sw_panel: float,
    eps_pv: float,
    clearance_m: float,
    soiling_dry: float,
    soiling_wet: float,
    degrad_yr0_mult: float = 1.0,
    irrigated: bool = False,
    svf_bounds: Tuple[float, float] = (0.25, 0.75),
    gcr_profile: np.ndarray | None = None,
) -> Dict[str, Any]:
    """Solve coupled hourly T_pv <-> T_leaf <-> FvCB-Medlyn system across 8760 hours."""
    T_air_c = climate["T_air_c"]
    T_air_k = T_air_c + 273.15
    rh_pct = np.clip(climate["rh_pct"], 5.0, 100.0)
    sw_ghi = climate["sw_ghi"]
    u10_ms = climate["wind_10m_ms"]
    month = climate["month"]
    n_h = len(T_air_c)

    # Altitude-corrected atmospheric pressure [kPa] & wind speed scaling
    elev_m = float(crop_cfg["altitude_m"])
    p_atm_kpa = 101.325 * math.exp(-elev_m / 8400.0)
    # Ambient air vapor pressure e_a [kPa]
    e_s_air = sat_vapor_pressure_kpa(T_air_c)
    e_a = e_s_air * (rh_pct / 100.0)

    # Sky emissivity (Brunt-style / Swinbank clear+cloud estimate from RH & Ta)
    eps_sky = np.clip(0.72 + 0.005 * T_air_c + 0.12 * (rh_pct / 100.0), 0.70, 0.96)
    lw_sky = eps_sky * SIGMA_SB * (T_air_k**4)

    # Wind at canopy height (exponential canopy drag sheltering) -> leaf boundary-layer & PV convection
    canopy_h = max(0.5, float(crop_cfg["canopy_height_m"]))
    u_canopy = np.maximum(0.25, 0.65 * u10_ms * (math.log(canopy_h / 0.05) / math.log(10.0 / 0.05)))
    u_panel = np.maximum(0.45, u10_ms * (math.log((canopy_h + clearance_m) / 0.05) / math.log(10.0 / 0.05)))
    gb_base = float(micro_cfg["boundary_layer_conductance_mol_m2_s"])
    # Sheltered orchard/shrub one-sided vapor boundary-layer conductance ~ 0.60 * gb_base
    gb_h = (0.60 * gb_base) * np.sqrt(u_canopy / 0.8)
    # Forced + natural convection on panel (both faces: 2 * h_c)
    hc_panel = 5.7 + 3.8 * u_panel

    # View factor F_{l->p} (scalar or time-varying for retractable louver audits)
    F_lp = compute_view_factor_leaf_to_panel(gcr, clearance_m, svf_bounds)
    if gcr_profile is not None:
        gcr_pv_h = np.asarray(gcr_profile, dtype=np.float64)
        F_lp_h: np.ndarray | float = np.where(gcr_pv_h > 1e-6, F_lp, 0.0)
    else:
        gcr_pv_h = np.full(n_h, gcr, dtype=np.float64)
        F_lp_h = F_lp

    # FAO-56 soil water balance (depends on shaded tau_sw)
    crop_name = crop_cfg["scientific_name"]
    if "Coffea" in crop_name:
        kc_crop = float(micro_cfg["fao56_kc_coffee"])
    elif "Piper" in crop_name:
        kc_crop = float(micro_cfg["fao56_kc_pepper"])
    else:
        kc_crop = float(micro_cfg["fao56_kc_tea"])
    awc_mm = float(micro_cfg["rainfed_soil_awc_mm"])
    f_soil = compute_fao56_soil_stress(
        climate["precip_mm"], sw_ghi, T_air_c, climate["vpd_air_kpa"], tau_sw, kc_crop, awc_mm, irrigated=irrigated
    )

    # Seasonal soiling on PV: dry Dec-Mar -> soiling_dry; wet Apr-Nov -> soiling_wet
    soiling_h = np.where(np.isin(month, [12, 1, 2, 3]), soiling_dry, soiling_wet)
    eff_pce_base = (pce_pv_ref_pct / 100.0) * (1.0 - soiling_h) * degrad_yr0_mult

    # Crop thermal optima & canopy beam/diffuse projection factors
    Topt_v, Topt_j, k_beam_can, k_diff_can = crop_ecophys_regime(crop_cfg)
    canopy_light_proj = k_beam_can * climate["f_beam"] + k_diff_can * climate["f_diff"]

    # Sub-canopy SW, top-canopy PAR (photoinhibition driver) & canopy-integrated PAR
    sw_sub = sw_ghi * tau_sw
    ppfd_top_sub = sw_ghi * 2.02 * tau_par
    ppfd_par_can = ppfd_top_sub * canopy_light_proj
    ppfd_epar_can = ppfd_par_can * epar_over_par

    # Crop physiological traits (Martins acclimation & persistent 4h D1 photoinhibition)
    shade_mean = float(np.mean(1.0 - tau_par[sw_ghi > 50.0])) if np.any(sw_ghi > 50.0) else 0.0
    traits = prepare_fvcb_acclimation(crop_cfg, shade_mean)
    g0, i_pi = traits[6], traits[9]
    f_pi = compute_dynamic_photoinhibition(ppfd_top_sub, i_pi)

    # Coupled fixed-point iteration across 8760 hours: T_pv <-> T_leaf <-> (A, gs)
    T_pv_c = T_air_c.copy()
    T_leaf_c = T_air_c.copy()
    gs_h = np.full(n_h, g0 + 0.08, dtype=np.float64)
    A_net_h = np.zeros(n_h, dtype=np.float64)
    Ci_h = np.full(n_h, 0.7 * CA_PPM, dtype=np.float64)

    # Underside of planar upper leaf views warm interior canopy/soil (~T_air_k)
    lw_up_under = LEAF_EMISSIVITY * SIGMA_SB * (T_air_k**4)
    sunlit_sw_proj = 0.92  # Effective sunlit-leaf solar intercept incl. local ground/leaf scatter

    for _it in range(14):
        T_leaf_k = T_leaf_c + 273.15
        T_pv_k = T_pv_c + 273.15

        # 1. Update FvCB + Medlyn at current T_leaf and VPD_leaf
        e_s_leaf = sat_vapor_pressure_kpa(T_leaf_c)
        vpd_leaf_kpa = np.maximum(0.08, e_s_leaf - e_a)
        A_net_h, gs_h, Ci_h = solve_fvcb_medlyn_step(
            ppfd_par_can, ppfd_epar_can, f_pi, T_leaf_k, vpd_leaf_kpa, f_soil,
            eta_ness_ratio, traits, Topt_v, Topt_j, gs_h, Ci_h, A_net_h, n_inner=6
        )

        relax = 0.7 if _it < 6 else 1.0
        # 2. Newton update for PV panel temperature T_pv (coupled to canopy T_leaf LWIR)
        if np.any(gcr_pv_h > 1e-6):
            pce_inst = np.maximum(0.01, eff_pce_base * (1.0 + beta_pv_per_c * (T_pv_c - 25.0)))
            q_abs_pv = sw_ghi * np.maximum(0.0, a_sw_panel - pce_inst)
            f_pv = q_abs_pv - 2.0 * hc_panel * (T_pv_c - T_air_c) - eps_pv * (SIGMA_SB * (T_pv_k**4) - lw_sky) - eps_pv * SIGMA_SB * ((T_pv_k**4) - (T_leaf_k**4))
            df_pv = 2.0 * hc_panel + 8.0 * eps_pv * SIGMA_SB * (T_pv_k**3)
            T_pv_new = T_pv_c + relax * (f_pv / df_pv)
            T_pv_c = np.where(gcr_pv_h > 1e-6, T_pv_new, T_air_c)
        else:
            T_pv_c = T_air_c.copy()

        # 3. Newton update for two-sided planar Leaf temperature T_leaf from coupled energy balance
        T_pv_k = T_pv_c + 273.15
        lw_down = (1.0 - F_lp_h) * lw_sky + F_lp_h * eps_pv * SIGMA_SB * (T_pv_k**4)
        q_sw_leaf = sunlit_sw_proj * LEAF_SW_ABSORPTIVITY * sw_sub
        gt_w = (gs_h * gb_h) / np.maximum(gs_h + gb_h, 1e-6)
        e_s_leaf = sat_vapor_pressure_kpa(T_leaf_c)
        s_vp = np.where(e_s_leaf > e_a, 4098.0 * e_s_leaf / ((T_leaf_c + 237.3) ** 2), 0.0)
        rn_now = q_sw_leaf + LEAF_EMISSIVITY * (lw_down + lw_up_under - 2.0 * SIGMA_SB * (T_leaf_k**4))
        le_now = LAMBDA_VAP_MOL * gt_w * (np.maximum(0.0, e_s_leaf - e_a) / p_atm_kpa)
        gb_sens = 1.25 * gb_h  # Two-sided sensible exchange tempered by planar leaf boundary-layer interference
        h_now = CP_AIR_MOL * gb_sens * (T_leaf_c - T_air_c)
        res_now = rn_now - h_now - le_now
        df_tl = 8.0 * LEAF_EMISSIVITY * SIGMA_SB * (T_leaf_k**3) + CP_AIR_MOL * gb_sens + LAMBDA_VAP_MOL * gt_w * (s_vp / p_atm_kpa)
        T_leaf_c = np.clip(T_leaf_c + relax * (res_now / df_tl), T_air_c - 8.0, T_air_c + 20.0)

    # Final diagnostics after convergence (use consistent gb_sens in Penman-Monteith split too)
    T_leaf_k = T_leaf_c + 273.15
    T_pv_k = T_pv_c + 273.15
    e_s_leaf = sat_vapor_pressure_kpa(T_leaf_c)
    e_s_air_d = sat_vapor_pressure_kpa(T_air_c)
    vpd_leaf_kpa = np.maximum(0.05, e_s_leaf - e_a)
    gt_w = (gs_h * gb_h) / np.maximum(gs_h + gb_h, 1e-6)
    lw_down = (1.0 - F_lp_h) * lw_sky + F_lp_h * eps_pv * SIGMA_SB * (T_pv_k**4)
    rn_leaf = sunlit_sw_proj * LEAF_SW_ABSORPTIVITY * sw_sub + LEAF_EMISSIVITY * (lw_down + lw_up_under - 2.0 * SIGMA_SB * (T_leaf_k**4))
    le_leaf_wm2 = LAMBDA_VAP_MOL * gt_w * (np.maximum(0.0, e_s_leaf - e_a) / p_atm_kpa)
    gb_sens = 1.25 * gb_h
    h_sens_wm2 = CP_AIR_MOL * gb_sens * (T_leaf_c - T_air_c)
    energy_res_wm2 = rn_leaf - h_sens_wm2 - le_leaf_wm2

    # Exact Penman-Monteith radiative vs aerodynamic/stomatal ET partitioning
    s_air = 4098.0 * e_s_air_d / ((T_air_c + 237.3) ** 2)
    gamma_psy = (CP_AIR_MOL * p_atm_kpa) / LAMBDA_VAP_MOL
    gamma_star = gamma_psy * (gb_sens / np.maximum(gt_w, 1e-6))
    le_rad_wm2 = (s_air / (s_air + gamma_star)) * rn_leaf
    le_aero_wm2 = le_leaf_wm2 - le_rad_wm2

    # Crop transpiration in mm/yr (1 W m^-2 * 3600 s / 2.45e6 J kg^-1 -> mm/h)
    transp_mm_h = np.maximum(0.0, le_leaf_wm2) * 3600.0 / 2.45e6
    transp_rad_mm_h = np.maximum(0.0, le_rad_wm2) * 3600.0 / 2.45e6
    transp_aero_mm_h = transp_mm_h - transp_rad_mm_h
    # PV electricity generation (W m^-2 of ground area = GCR * GHI * PCE(Tp))
    if np.any(gcr_pv_h > 1e-6):
        pce_inst = np.maximum(0.01, eff_pce_base * (1.0 + beta_pv_per_c * (T_pv_c - 25.0)))
        pv_gen_wm2 = gcr_pv_h * sw_ghi * pce_inst
    else:
        pv_gen_wm2 = np.zeros(n_h, dtype=np.float64)

    # Dry-season (months 12,1,2) & wet-season (6,7,8,9,10) masks for diagnostics
    day_mask = sw_ghi > 50.0
    dry_day = day_mask & np.isin(month, [12, 1, 2])
    wet_day = day_mask & np.isin(month, [6, 7, 8, 9, 10])

    return {
        "A_net_umol_m2_s": A_net_h,
        "A_net_annual_mol_m2": float(np.sum(A_net_h) * 3600.0 * 1e-6),
        "A_net_dry_mean": float(np.mean(A_net_h[dry_day])),
        "A_net_wet_mean": float(np.mean(A_net_h[wet_day])),
        "T_leaf_c": T_leaf_c,
        "T_leaf_day_mean_c": float(np.mean(T_leaf_c[day_mask])),
        "T_leaf_dry_day_mean_c": float(np.mean(T_leaf_c[dry_day])),
        "T_leaf_p95_c": float(np.percentile(T_leaf_c[day_mask], 95)),
        "T_pv_c": T_pv_c,
        "T_pv_day_mean_c": float(np.mean(T_pv_c[day_mask])),
        "T_pv_p95_c": float(np.percentile(T_pv_c[day_mask], 95)),
        "vpd_leaf_kpa": vpd_leaf_kpa,
        "vpd_leaf_day_mean_kpa": float(np.mean(vpd_leaf_kpa[day_mask])),
        "vpd_leaf_p95_kpa": float(np.percentile(vpd_leaf_kpa[day_mask], 95)),
        "gs_mol_m2_s": gs_h,
        "gs_day_mean": float(np.mean(gs_h[day_mask])),
        "transp_mm_yr": float(np.sum(transp_mm_h)),
        "transp_rad_mm_yr": float(np.sum(transp_rad_mm_h)),
        "transp_aero_mm_yr": float(np.sum(transp_aero_mm_h)),
        "transp_dry_mm": float(np.sum(transp_mm_h[np.isin(month, [12, 1, 2])])),
        "transp_wet_mm": float(np.sum(transp_mm_h[np.isin(month, [6, 7, 8, 9, 10])])),
        "rn_leaf_wm2": rn_leaf,
        "rn_leaf_day_mean_wm2": float(np.mean(rn_leaf[day_mask])),
        "f_soil": f_soil,
        "f_soil_dry_mean": float(np.mean(f_soil[np.isin(month, [12, 1, 2])])),
        "f_pi_day_mean": float(np.mean(f_pi[day_mask])),
        "par_sub_day_mean": float(np.mean(ppfd_par_can[day_mask])),
        "par_to_ipi_ratio": float(np.mean(ppfd_top_sub[day_mask]) / i_pi),
        "ppfd_par_can": ppfd_par_can,
        "f_pi": f_pi,
        "pv_gen_wm2": pv_gen_wm2,
        "pv_kwh_m2_yr": float(np.sum(pv_gen_wm2) * 1e-3),
        "pv_mwh_ha_yr": float(np.sum(pv_gen_wm2) * 10.0 * 1e-3),  # 10,000 m2/ha * 1e-3 kWh/Wh = 10 kWh -> *1e-3 = MWh
        "max_energy_residual_wm2": float(np.max(np.abs(energy_res_wm2))),
        "F_lp_view_factor": F_lp,
        "mean_par_transmission": float(np.mean(tau_par[day_mask])),
    }


def evaluate_biochem_only_corner(
    climate: Dict[str, np.ndarray],
    crop_cfg: dict,
    ppfd_par_can: np.ndarray,
    f_pi: np.ndarray,
    T_leaf_c: np.ndarray,
    vpd_leaf_kpa: np.ndarray,
    f_soil: np.ndarray,
    epar_over_par: np.ndarray,
    eta_ness_ratio: float,
    shade_mean_accl: float,
) -> Tuple[float, float]:
    """Fast corner evaluation for Exact 4-Lever Shapley Attribution using the shared FvCB-Medlyn kernel."""
    Topt_v, Topt_j, _, _ = crop_ecophys_regime(crop_cfg)
    traits = prepare_fvcb_acclimation(crop_cfg, shade_mean_accl)
    g0 = traits[6]
    gs_h = np.full_like(T_leaf_c, g0 + 0.08)
    A_net_h = np.zeros_like(T_leaf_c)
    Ci_h = np.full_like(T_leaf_c, 0.7 * CA_PPM)
    A_net_h, gs_h, _ = solve_fvcb_medlyn_step(
        ppfd_par_can, ppfd_par_can * epar_over_par, f_pi, T_leaf_c + 273.15,
        vpd_leaf_kpa, f_soil, eta_ness_ratio, traits, Topt_v, Topt_j, gs_h, Ci_h, A_net_h, n_inner=10
    )
    return float(np.sum(A_net_h) * 3600.0 * 1e-6), float(np.mean(gs_h[climate["sw_ghi"] > 50.0]))


def compute_exact_shapley_4levers(
    climate: Dict[str, np.ndarray],
    crop_cfg: dict,
    res_open: Dict[str, Any],
    res_av: Dict[str, Any],
    epar_over_par_av: np.ndarray,
    eta_ness_av: float,
    baseline_yield_kg_ha: float,
) -> Dict[str, float]:
    """Exact 16-corner Shapley attribution of relative crop yield change (S_AV - S0) across 4 levers."""
    a_open = res_open["A_net_annual_mol_m2"]
    cache: Dict[Tuple[int, int, int, int], float] = {}
    shade_av = 1.0 - res_av["mean_par_transmission"]

    for b_par in (0, 1):
        for b_th in (0, 1):
            for b_vpd in (0, 1):
                for b_sp in (0, 1):
                    key = (b_par, b_th, b_vpd, b_sp)
                    if key == (0, 0, 0, 0):
                        cache[key] = a_open
                        continue
                    if key == (1, 1, 1, 1):
                        cache[key] = res_av["A_net_annual_mol_m2"]
                        continue
                    ppfd = res_av["ppfd_par_can"] if b_par else res_open["ppfd_par_can"]
                    fpi = res_av["f_pi"] if b_par else res_open["f_pi"]
                    tl = res_av["T_leaf_c"] if b_th else res_open["T_leaf_c"]
                    vpd = res_av["vpd_leaf_kpa"] if b_vpd else res_open["vpd_leaf_kpa"]
                    fsoil = res_av["f_soil"] if b_vpd else res_open["f_soil"]
                    epar = epar_over_par_av if b_sp else np.ones_like(epar_over_par_av)
                    eta = eta_ness_av if b_sp else 1.0
                    accl = shade_av if b_par else 0.0
                    a_val, _ = evaluate_biochem_only_corner(
                        climate, crop_cfg, ppfd, fpi, tl, vpd, fsoil, epar, eta, accl
                    )
                    cache[key] = a_val

    # Standard Shapley weights for n=4 players: w(|S|) = |S|! * (n - |S| - 1)! / n!
    weights = {0: 1.0 / 4.0, 1: 1.0 / 12.0, 2: 1.0 / 12.0, 3: 1.0 / 4.0}
    phi = [0.0, 0.0, 0.0, 0.0]
    for mask_int in range(16):
        bits = [(mask_int >> i) & 1 for i in range(4)]
        for i in range(4):
            if bits[i] == 0:
                s_card = sum(bits)
                w = weights[s_card]
                bits_with = list(bits)
                bits_with[i] = 1
                diff = cache[tuple(bits_with)] - cache[tuple(bits)]
                phi[i] += w * diff

    # Convert annual mol CO2 to relative percentage & kg/ha yield shifts
    scale_pct = 100.0 / a_open
    scale_kg = baseline_yield_kg_ha / a_open
    total_pct = (res_av["A_net_annual_mol_m2"] - a_open) * scale_pct
    return {
        "delta_y_total_pct": float(total_pct),
        "delta_y_total_kg_ha": float((res_av["A_net_annual_mol_m2"] - a_open) * scale_kg),
        "lever_par_pi_pct": float(phi[0] * scale_pct),
        "lever_therm_pct": float(phi[1] * scale_pct),
        "lever_vpd_h2o_pct": float(phi[2] * scale_pct),
        "lever_spec_q_pct": float(phi[3] * scale_pct),
        "shapley_residual_pct": float(abs(total_pct - sum(phi) * scale_pct)),
    }


def _crop_job_worker(args: Tuple[Any, ...]) -> List[Dict[str, Any]]:
    """Run full scenario matrix + ST-OPV Pareto & c-Si GCR sweeps for one crop."""
    crop_key, cfg, pareto_designs, tmm_lib_dict, q_summary, save_hourly = args[:6]
    config_root = Path(args[6]) if len(args) > 6 else PKG_ROOT
    output_dir = Path(args[7]) if len(args) > 7 else DATA_WP3
    crop_cfg = cfg["crops"][crop_key]
    micro_cfg = cfg["microclimate"]
    opv_cfg = cfg["opv_technology"]
    si_cfg = cfg["si_counterfactual"]
    opt_cfg = cfg["optical_radiative_model"]
    svf_bounds = tuple(float(x) for x in opt_cfg["panel_sky_view_factor_range"])

    climate = load_site_climate(resolve_config_path(config_root, crop_cfg["climate_dataset"]), float(crop_cfg.get("latitude", 5.2)))
    # Note: read exact lat from climate_summary_2023.json
    csum = json.loads(resolve_config_path(config_root, micro_cfg["climate_summary_dataset"]).read_text(encoding="utf-8"))
    for sk, sv in csum.items():
        if sk.split("_")[-1] in crop_key or crop_key.split("_")[-1] in sk:
            climate = load_site_climate(resolve_config_path(config_root, crop_cfg["climate_dataset"]), float(sv["latitude"]))
            break

    n_h = len(climate["T_air_c"])
    baseline_kg = float(crop_cfg["baseline_clean_yield_kg_ha"])
    canopy_h = float(crop_cfg["canopy_height_m"])
    # Engineered agronomic clearances
    if crop_key == "highland_tea":
        clearance_opv = float(crop_cfg.get("mounting_clearance_m", 2.2)) - canopy_h  # 1.2 m (confined)
        clearance_si = float(si_cfg["standard_mounting_height_m"]) - canopy_h      # 2.5 m
    elif crop_key == "penja_white_pepper":
        clearance_opv = 1.5   # 5.0m engineered trellis over 3.5m vine (ventilated)
        clearance_si = 2.0
    else:  # arabica_coffee
        clearance_opv = 1.4
        clearance_si = 1.8

    # Map quantum NESS ratio from WP2 H2 (and note bounded < 3.4e-5 across H1/H2/H3)
    eta_am15_h2 = float(q_summary["hamiltonians"]["H2_Muh2010_diag_PDA"]["open_rc_no_npq"]["AM15G_full_sun"]["eta_partial_secular_mean"])
    # TMM library interpolation helpers for zenith angles [0,15,30,45,60]
    angles_grid = np.asarray(tmm_lib_dict["incidence_angles_deg"], dtype=np.float64)
    wl = np.asarray(tmm_lib_dict["wavelength_nm"], dtype=np.float64)
    am15 = np.asarray(tmm_lib_dict["am15_w_m2_nm"], dtype=np.float64)
    par_mask = (wl >= 400.0) & (wl <= 700.0)
    epar_mask = (wl >= 400.0) & (wl <= 750.0)
    red_mask = (wl >= 655.0) & (wl <= 665.0)
    fr_mask = (wl >= 725.0) & (wl <= 735.0)
    _trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))
    # Photon weights (lambda * E)
    ph_am15 = am15 * wl
    am15_par_ph = float(_trapz(ph_am15[par_mask], wl[par_mask]))
    am15_epar_ph = float(_trapz(ph_am15[epar_mask], wl[epar_mask]))
    am15_red_ph = float(_trapz(ph_am15[red_mask], wl[red_mask]))
    am15_fr_ph = float(_trapz(ph_am15[fr_mask], wl[fr_mask]))
    am15_sw_tot = float(_trapz(am15, wl))
    epar_par_am15 = am15_epar_ph / am15_par_ph
    rfr_am15 = am15_red_ph / am15_fr_ph

    # 1. Run S0 Open-Field Control Baseline (rainfed)
    res_s0 = solve_coupled_microclimate_and_assimilation(
        climate=climate,
        crop_cfg=crop_cfg,
        micro_cfg=micro_cfg,
        tau_par=np.ones(n_h),
        tau_sw=np.ones(n_h),
        epar_over_par=np.ones(n_h),
        r_fr_ratio=np.full(n_h, rfr_am15),
        eta_ness_ratio=1.0,
        gcr=0.0,
        pce_pv_ref_pct=0.0,
        beta_pv_per_c=0.0,
        a_sw_panel=0.0,
        eps_pv=0.90,
        clearance_m=clearance_opv,
        soiling_dry=0.0,
        soiling_wet=0.0,
        irrigated=False,
        svf_bounds=svf_bounds,
    )
    a_s0 = res_s0["A_net_annual_mol_m2"]
    et_s0 = res_s0["transp_mm_yr"]

    # Helper to run + attribute any scenario
    rows_out: List[Dict[str, Any]] = []
    hourly_exports: Dict[str, np.ndarray] = {
        "S0_Tleaf": res_s0["T_leaf_c"],
        "S0_A": res_s0["A_net_umol_m2_s"],
    }

    def record_scenario(
        scenario_id: str,
        tech: str,
        gcr: float,
        apt: float,
        pce_ref: float,
        d_act: float,
        d_ag: float,
        d_cap: float,
        tau_par: np.ndarray,
        tau_sw: np.ndarray,
        epar_ratio: np.ndarray,
        rfr_arr: np.ndarray,
        eta_ratio: float,
        beta_pv: float,
        a_sw_panel: float,
        eps_pv: float,
        clearance_m: float,
        soiling_d: float,
        soiling_w: float,
        irrigated: bool = False,
        export_key: str | None = None,
    ) -> Dict[str, Any]:
        res = solve_coupled_microclimate_and_assimilation(
            climate=climate,
            crop_cfg=crop_cfg,
            micro_cfg=micro_cfg,
            tau_par=tau_par,
            tau_sw=tau_sw,
            epar_over_par=epar_ratio,
            r_fr_ratio=rfr_arr,
            eta_ness_ratio=eta_ratio,
            gcr=gcr,
            pce_pv_ref_pct=pce_ref,
            beta_pv_per_c=beta_pv,
            a_sw_panel=a_sw_panel,
            eps_pv=eps_pv,
            clearance_m=clearance_m,
            soiling_dry=soiling_d,
            soiling_wet=soiling_w,
            irrigated=irrigated,
            svf_bounds=svf_bounds,
        )
        shap = compute_exact_shapley_4levers(climate, crop_cfg, res_s0, res, epar_ratio, eta_ratio, baseline_kg)
        # Water saving & WUE + Radiative/Aerodynamic ET partitioning
        delta_et_pct = 100.0 * (res["transp_mm_yr"] - et_s0) / et_s0
        delta_et_rad_mm = res["transp_rad_mm_yr"] - res_s0["transp_rad_mm_yr"]
        delta_et_aero_mm = res["transp_aero_mm_yr"] - res_s0["transp_aero_mm_yr"]
        wue_s0 = baseline_kg / max(1e-6, et_s0)  # kg/ha per mm (= 0.1 kg/m3)
        y_kg_ha = baseline_kg * (res["A_net_annual_mol_m2"] / a_s0)
        wue_sc = y_kg_ha / max(1e-6, res["transp_mm_yr"])
        delta_wue_pct = 100.0 * (wue_sc - wue_s0) / wue_s0

        # Empirical tea-under-PV & coffee-cooling alignment metrics
        day_m = climate["sw_ghi"] > 50.0
        dt_leaf_day = float(np.mean(res["T_leaf_c"][day_m] - res_s0["T_leaf_c"][day_m]))
        dt_leaf_dry_day = res["T_leaf_dry_day_mean_c"] - res_s0["T_leaf_dry_day_mean_c"]
        dt_pv_excess_day = res["T_pv_day_mean_c"] - float(np.mean(climate["T_air_c"][day_m])) if gcr > 0 else 0.0

        row = {
            "crop": crop_key,
            "scenario_id": scenario_id,
            "technology": tech,
            "irrigated": int(irrigated),
            "gcr": gcr,
            "apt_par": apt,
            "d_act_nm": d_act,
            "d_ag_nm": d_ag,
            "d_cap_nm": d_cap,
            "pce_ref_pct": pce_ref,
            "effective_par_trans": res["mean_par_transmission"],
            "effective_shade_pct": 100.0 * (1.0 - res["mean_par_transmission"]),
            "r_fr_mean": float(np.mean(rfr_arr[day_m])),
            "epar_boost_pct": float((np.mean(epar_ratio[day_m]) - 1.0) * 100.0),
            "eta_ness_ratio": eta_ratio,
            "view_factor_flp": res["F_lp_view_factor"],
            "yield_kg_ha": y_kg_ha,
            "delta_y_total_pct": shap["delta_y_total_pct"],
            "lever_par_pi_pct": shap["lever_par_pi_pct"],
            "lever_therm_pct": shap["lever_therm_pct"],
            "lever_vpd_h2o_pct": shap["lever_vpd_h2o_pct"],
            "lever_spec_q_pct": shap["lever_spec_q_pct"],
            "shapley_residual_pct": shap["shapley_residual_pct"],
            "delta_y_dry_pct": 100.0 * (res["A_net_dry_mean"] - res_s0["A_net_dry_mean"]) / res_s0["A_net_dry_mean"],
            "delta_y_wet_pct": 100.0 * (res["A_net_wet_mean"] - res_s0["A_net_wet_mean"]) / res_s0["A_net_wet_mean"],
            "t_leaf_day_c": res["T_leaf_day_mean_c"],
            "t_leaf_dry_day_c": res["T_leaf_dry_day_mean_c"],
            "t_pv_day_c": res["T_pv_day_mean_c"],
            "dt_leaf_day_c": dt_leaf_day,
            "dt_leaf_dry_day_c": dt_leaf_dry_day,
            "dt_pv_excess_day_c": dt_pv_excess_day,
            "t_leaf_p95_c": res["T_leaf_p95_c"],
            "t_pv_p95_c": res["T_pv_p95_c"],
            "vpd_leaf_day_kpa": res["vpd_leaf_day_mean_kpa"],
            "vpd_leaf_p95_kpa": res["vpd_leaf_p95_kpa"],
            "gs_day_mean": res["gs_day_mean"],
            "rn_leaf_day_wm2": res["rn_leaf_day_mean_wm2"],
            "par_to_ipi_ratio": res["par_to_ipi_ratio"],
            "f_pi_day_mean": res["f_pi_day_mean"],
            "f_soil_dry_mean": res["f_soil_dry_mean"],
            "transp_mm_yr": res["transp_mm_yr"],
            "transp_rad_mm_yr": res["transp_rad_mm_yr"],
            "transp_aero_mm_yr": res["transp_aero_mm_yr"],
            "delta_et_rad_mm": delta_et_rad_mm,
            "delta_et_aero_mm": delta_et_aero_mm,
            "delta_et_pct": delta_et_pct,
            "delta_wue_pct": delta_wue_pct,
            "pv_mwh_ha_yr": res["pv_mwh_ha_yr"],
            "pv_kwh_m2_yr": res["pv_kwh_m2_yr"],
            "max_energy_res_wm2": res["max_energy_residual_wm2"],
        }
        rows_out.append(row)
        if save_hourly and export_key is not None:
            hourly_exports[f"{export_key}_pv_wm2"] = res["pv_gen_wm2"]
            hourly_exports[f"{export_key}_Tleaf"] = res["T_leaf_c"]
            hourly_exports[f"{export_key}_Tpv"] = res["T_pv_c"]
            hourly_exports[f"{export_key}_A"] = res["A_net_umol_m2_s"]
        return row

    # Record S0 explicitly
    record_scenario(
        "S0_open_control", "Open_Field", 0.0, 1.0, 0.0, 0.0, 0.0, 0.0,
        np.ones(n_h), np.ones(n_h), np.ones(n_h), np.full(n_h, rfr_am15), 1.0,
        0.0, 0.0, 0.90, clearance_opv, 0.0, 0.0, irrigated=False
    )
    # Record S0 irrigated reference for S5
    record_scenario(
        "S0_open_irrigated", "Open_Field_Irrigated", 0.0, 1.0, 0.0, 0.0, 0.0, 0.0,
        np.ones(n_h), np.ones(n_h), np.ones(n_h), np.full(n_h, rfr_am15), 1.0,
        0.0, 0.0, 0.90, clearance_opv, 0.0, 0.0, irrigated=True
    )

    # 2. Record S1 Natural Agroforestry Shade (optimal shade midpoint per crop: coffee 32.5%, pepper 27.5%, tea 40%)
    s_nat = 0.5 * (float(crop_cfg["optimum_shade_min"]) + float(crop_cfg["optimum_shade_max"]))
    record_scenario(
        "S1_agroforestry_shade", "Natural_Shade", 0.0, 1.0 - s_nat, 0.0, 0.0, 0.0, 0.0,
        np.full(n_h, 1.0 - s_nat), np.full(n_h, 1.0 - s_nat), np.ones(n_h), np.full(n_h, 0.85 * rfr_am15), 1.0,
        0.0, 0.0, 0.94, clearance_opv, 0.0, 0.0, irrigated=False
    )

    # 3. Record S2 Spaced Opaque c-Si AV across GCR [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]
    pce_si = float(si_cfg["base_pce_percent"])
    beta_si = float(si_cfg["pce_temp_coeff_per_c"])
    eps_si = float(si_cfg["infrared_emissivity"])
    soil_si_d = float(si_cfg["soiling_derating_seasonal_range"][1])
    soil_si_w = float(si_cfg["soiling_derating_seasonal_range"][0])
    for gcr_si in [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]:
        t_geom = np.full(n_h, 1.0 - gcr_si)
        exp_k = f"S2_cSi_GCR{int(round(gcr_si * 100))}"
        record_scenario(
            exp_k, "cSi_Opaque_AV", gcr_si, 0.0, pce_si, 0.0, 0.0, 0.0,
            t_geom, t_geom, np.ones(n_h), np.full(n_h, rfr_am15), 1.0,
            beta_si, 0.90, eps_si, clearance_si, soil_si_d, soil_si_w,
            irrigated=False, export_key=exp_k
        )
        if abs(gcr_si - 0.40) < 0.01:
            record_scenario(
                "S5_cSi_GCR40_Irrig", "cSi_Opaque_AV", gcr_si, 0.0, pce_si, 0.0, 0.0, 0.0,
                t_geom, t_geom, np.ones(n_h), np.full(n_h, rfr_am15), 1.0,
                beta_si, 0.90, eps_si, clearance_si, soil_si_d, soil_si_w,
                irrigated=True, export_key="S5_cSi_GCR40_Irrig"
            )
    # Also evaluate empirical Tea-under-PV check at 47% shade (GCR = 0.47 c-Si & ST-OPV equivalent PAR=53%)
    if crop_key == "highland_tea":
        record_scenario(
            "VAL_cSi_Shade47pct", "cSi_Opaque_AV", 0.47, 0.0, pce_si, 0.0, 0.0, 0.0,
            np.full(n_h, 0.53), np.full(n_h, 0.53), np.ones(n_h), np.full(n_h, rfr_am15), 1.0,
            beta_si, 0.90, eps_si, clearance_si, soil_si_d, soil_si_w, irrigated=False
        )

    # 4. Record S3/S4 ST-OPV Pareto Strata across GCR [0.30, 0.45, 0.60, 0.75, 0.85]
    # Select representative Pareto strata spanning APT 20% -> 56% + peak LUE (43.7% & 44.1% & 52.1% & 35.0%)
    beta_opv = float(opv_cfg["pce_temp_coeff_per_c"])
    eps_opv = float(opv_cfg["infrared_emissivity"])
    soil_opv_d = float(opv_cfg["soiling_derating_seasonal_range"][1])
    soil_opv_w = float(opv_cfg["soiling_derating_seasonal_range"][0])
    target_apts = [0.20, 0.28, 0.35, 0.44, 0.52, 0.56]
    lib_apts = np.asarray(tmm_lib_dict["design_apt_par"], dtype=np.float64)

    for t_apt in target_apts:
        idx = int(np.argmin(np.abs(lib_apts - t_apt)))
        d_act = float(tmm_lib_dict["design_d_act_nm"][idx])
        d_ag = float(tmm_lib_dict["design_d_ag_nm"][idx])
        d_cap = float(tmm_lib_dict["design_d_cap_nm"][idx])
        apt_val = float(lib_apts[idx])
        pce_val = float(tmm_lib_dict["design_pce_pct"][idx])
        T_beam_ang = np.asarray(tmm_lib_dict["T_beam"][idx], dtype=np.float64)  # (5, n_wl)
        T_diff_wl = np.asarray(tmm_lib_dict["T_diff"][idx], dtype=np.float64)

        # Compute spectral integrals per angle [0,15,30,45,60]
        par_b_ang = np.array([_trapz(T_beam_ang[a, par_mask] * ph_am15[par_mask], wl[par_mask]) / am15_par_ph for a in range(5)])
        epar_b_ang = np.array([_trapz(T_beam_ang[a, epar_mask] * ph_am15[epar_mask], wl[epar_mask]) / am15_epar_ph for a in range(5)])
        sw_b_ang = np.array([_trapz(T_beam_ang[a] * am15, wl) / am15_sw_tot for a in range(5)])
        red_b_ang = np.array([_trapz(T_beam_ang[a, red_mask] * ph_am15[red_mask], wl[red_mask]) / am15_red_ph for a in range(5)])
        fr_b_ang = np.array([_trapz(T_beam_ang[a, fr_mask] * ph_am15[fr_mask], wl[fr_mask]) / am15_fr_ph for a in range(5)])

        par_d = float(_trapz(T_diff_wl[par_mask] * ph_am15[par_mask], wl[par_mask]) / am15_par_ph)
        epar_d = float(_trapz(T_diff_wl[epar_mask] * ph_am15[epar_mask], wl[epar_mask]) / am15_epar_ph)
        sw_d = float(_trapz(T_diff_wl * am15, wl) / am15_sw_tot)
        red_d = float(_trapz(T_diff_wl[red_mask] * ph_am15[red_mask], wl[red_mask]) / am15_red_ph)
        fr_d = float(_trapz(T_diff_wl[fr_mask] * ph_am15[fr_mask], wl[fr_mask]) / am15_fr_ph)

        zen_clipped = np.clip(climate["zenith_deg"], 0.0, 60.0)
        par_b_h = np.interp(zen_clipped, angles_grid, par_b_ang)
        epar_b_h = np.interp(zen_clipped, angles_grid, epar_b_ang)
        sw_b_h = np.interp(zen_clipped, angles_grid, sw_b_ang)
        red_b_h = np.interp(zen_clipped, angles_grid, red_b_ang)
        fr_b_h = np.interp(zen_clipped, angles_grid, fr_b_ang)

        f_b = climate["f_beam"]
        f_d = climate["f_diff"]
        t_par_panel = f_b * par_b_h + f_d * par_d
        t_epar_panel = f_b * epar_b_h + f_d * epar_d
        t_sw_panel = f_b * sw_b_h + f_d * sw_d
        t_red_panel = f_b * red_b_h + f_d * red_d
        t_fr_panel = f_b * fr_b_h + f_d * fr_d

        # Absorbed SW inside OPV stack (look up from Pareto CSV row)
        match_row = next(r for r in pareto_designs if abs(float(r["d_act_nm"]) - d_act) < 0.1 and abs(float(r["d_ag_nm"]) - d_ag) < 0.1 and abs(float(r["d_cap_nm"]) - d_cap) < 0.1)
        a_sw_opv = float(match_row["a_sw_300_1100"])

        # Match exact NESS quantum ratio from WP2 summary
        tag_q = f"STOPV_APT_{apt_val * 100:.1f}pct_beam"
        if tag_q in q_summary["hamiltonians"]["H2_Muh2010_diag_PDA"]["open_rc_no_npq"]:
            eta_opv_ratio = float(q_summary["hamiltonians"]["H2_Muh2010_diag_PDA"]["open_rc_no_npq"][tag_q]["eta_partial_secular_mean"]) / eta_am15_h2
        else:
            eta_opv_ratio = 1.000015

        for gcr_opv in [0.35, 0.50, 0.65, 0.75, 0.85]:
            tau_par = (1.0 - gcr_opv) + gcr_opv * t_par_panel
            tau_epar = (1.0 - gcr_opv) + gcr_opv * t_epar_panel
            tau_sw = (1.0 - gcr_opv) + gcr_opv * t_sw_panel
            tau_red = (1.0 - gcr_opv) + gcr_opv * t_red_panel
            tau_fr = (1.0 - gcr_opv) + gcr_opv * t_fr_panel
            epar_over_par = (tau_epar / np.maximum(tau_par, 1e-6)) * 1.0  # Relative to open AM1.5G baseline (=1.0)
            rfr_arr = rfr_am15 * (tau_red / np.maximum(tau_fr, 1e-6))
            exp_k = f"S3_OPV_APT{int(round(apt_val * 100))}_GCR{int(round(gcr_opv * 100))}"
            record_scenario(
                exp_k, "ST_OPV_PM6Y6", gcr_opv, apt_val, pce_val, d_act, d_ag, d_cap,
                tau_par, tau_sw, epar_over_par, rfr_arr, eta_opv_ratio,
                beta_opv, a_sw_opv, eps_opv, clearance_opv, soil_opv_d, soil_opv_w,
                irrigated=False,
                export_key=exp_k if (abs(t_apt - 0.35) < 0.02 or abs(t_apt - 0.44) < 0.02 or abs(t_apt - 0.52) < 0.02) else None,
            )
            if abs(t_apt - 0.44) < 0.02 and abs(gcr_opv - 0.65) < 0.01:
                record_scenario(
                    "S5_OPV_APT44_GCR65_Irrig", "ST_OPV_PM6Y6", gcr_opv, apt_val, pce_val, d_act, d_ag, d_cap,
                    tau_par, tau_sw, epar_over_par, rfr_arr, eta_opv_ratio,
                    beta_opv, a_sw_opv, eps_opv, clearance_opv, soil_opv_d, soil_opv_w,
                    irrigated=True, export_key="S5_OPV_APT44_GCR65_Irrig",
                )

    if save_hourly:
        output_dir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(output_dir / f"hourly_{crop_key}.npz", sw_ghi=climate["sw_ghi"], T_air_c=climate["T_air_c"], **hourly_exports)

    return rows_out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--config", type=Path, default=None, help="Alternate WP3 YAML configuration")
    parser.add_argument("--output-dir", type=Path, default=None, help="Isolated output directory for this run")
    parser.add_argument("--no-hourly", action="store_true", help="Do not save per-hour scenario arrays")
    args = parser.parse_args()
    config_path = args.config.resolve() if args.config else PKG_ROOT / "parameters.yaml"
    config_root = config_path.parent
    canonical_config = (PKG_ROOT / "parameters.yaml").resolve()
    if config_path != canonical_config and args.output_dir is None:
        parser.error("--output-dir is required when using a noncanonical --config")
    output_dir = args.output_dir.resolve() if args.output_dir else DATA_WP3

    t0 = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    cfg = load_config(config_path)
    with open(DATA_WP2 / "tmm_pareto_opv.csv", "r", encoding="utf-8") as f:
        pareto_designs = list(csv.DictReader(f))
    tmm_lib = dict(np.load(DATA_WP2 / "tmm_spectral_library.npz"))
    q_summary = json.loads((DATA_WP2 / "quantum_ness_summary.json").read_text(encoding="utf-8"))

    crops = list(cfg["crops"].keys())
    all_rows: List[Dict[str, Any]] = []
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(crops))) as pool:
            futs = [pool.submit(_crop_job_worker, (c, cfg, pareto_designs, tmm_lib, q_summary, not args.no_hourly, config_root, output_dir)) for c in crops]
            for fut in as_completed(futs):
                all_rows.extend(fut.result())
    else:
        for c in crops:
            all_rows.extend(_crop_job_worker((c, cfg, pareto_designs, tmm_lib, q_summary, not args.no_hourly, config_root, output_dir)))

    # Sort deterministically
    all_rows.sort(key=lambda r: (r["crop"], r["technology"], r["gcr"], r["apt_par"], r["scenario_id"]))

    csv_out = output_dir / "wp3_crop_microclimate_scenarios.csv"
    fieldnames = list(all_rows[0].keys())
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    # Empirical & interpretative verification summary
    summary: Dict[str, Any] = {
        "n_scenarios_total": len(all_rows),
        "wall_time_s": float(time.perf_counter() - t0),
        "max_energy_residual_wm2": float(max(r["max_energy_res_wm2"] for r in all_rows)),
        "max_shapley_residual_pct": float(max(r["shapley_residual_pct"] for r in all_rows)),
        "by_crop_empirical_checks": {},
    }
    for ck in crops:
        crows = [r for r in all_rows if r["crop"] == ck]
        s0 = next(r for r in crows if r["scenario_id"] == "S0_open_control")
        s1 = next(r for r in crows if r["scenario_id"] == "S1_agroforestry_shade")
        csi_opt = [r for r in crows if r["technology"] == "cSi_Opaque_AV" and not r["irrigated"] and 0.25 <= r["gcr"] <= 0.45]
        opv_opt = [r for r in crows if r["technology"] == "ST_OPV_PM6Y6" and not r["irrigated"] and 0.25 <= (1.0 - r["effective_par_trans"]) <= 0.45]
        best_opv = max(opv_opt, key=lambda r: r["delta_y_total_pct"]) if opv_opt else crows[0]
        best_csi = max(csi_opt, key=lambda r: r["delta_y_total_pct"]) if csi_opt else crows[0]
        summary["by_crop_empirical_checks"][ck] = {
            "s0_yield_kg_ha": s0["yield_kg_ha"],
            "s0_t_leaf_day_c": round(s0["t_leaf_day_c"], 2),
            "s0_t_leaf_dry_day_c": round(s0["t_leaf_dry_day_c"], 2),
            "s1_delta_y_pct": round(s1["delta_y_total_pct"], 2),
            "s1_dt_leaf_dry_day_c": round(s1["dt_leaf_dry_day_c"], 2),
            "best_opv_shade_scenario": best_opv["scenario_id"],
            "best_opv_delta_y_pct": round(best_opv["delta_y_total_pct"], 2),
            "best_opv_dt_leaf_dry_day_c": round(best_opv["dt_leaf_dry_day_c"], 2),
            "best_opv_dt_pv_excess_day_c": round(best_opv["dt_pv_excess_day_c"], 2),
            "best_opv_levers_pct": {
                "PAR_PI": round(best_opv["lever_par_pi_pct"], 3),
                "therm": round(best_opv["lever_therm_pct"], 3),
                "VPD_H2O": round(best_opv["lever_vpd_h2o_pct"], 3),
                "spec_Q": round(best_opv["lever_spec_q_pct"], 4),
            },
            "best_opv_delta_et_pct": round(best_opv["delta_et_pct"], 2),
            "best_opv_delta_et_rad_mm": round(best_opv["delta_et_rad_mm"], 2),
            "best_opv_delta_et_aero_mm": round(best_opv["delta_et_aero_mm"], 2),
            "best_opv_pv_mwh_ha_yr": round(best_opv["pv_mwh_ha_yr"], 1),
            "best_csi_scenario": best_csi["scenario_id"],
            "best_csi_delta_y_pct": round(best_csi["delta_y_total_pct"], 2),
            "best_csi_pv_mwh_ha_yr": round(best_csi["pv_mwh_ha_yr"], 1),
        }
        if ck == "highland_tea":
            val_tea = next((r for r in crows if r["scenario_id"] == "VAL_cSi_Shade47pct"), None)
            if val_tea:
                summary["by_crop_empirical_checks"][ck]["tea_47pct_shade_delta_y_pct"] = round(val_tea["delta_y_total_pct"], 2)

    sum_out = output_dir / "wp3_validation_summary.json"
    sum_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
