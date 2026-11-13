#!/usr/bin/env python3
"""
WP5: Coupled 8760 h Agro-Industrial Dispatch, 20-Year DCF Techno-Economics,
Dual-Functional-Unit ISO 14040/14044 LCA, Break-Even Envelopes, N=10,000 Sobol
Global Sensitivity Analysis, and 2D Agronomic/Technological Regime Phase Maps.

Reads all economic, crop, PV lifetime/CAPEX/LCA, and Monte Carlo settings from
``parameters.yaml`` and physical microclimate/PV outputs from WP3
(``data/wp3/wp3_crop_microclimate_scenarios.csv`` and ``data/wp3/hourly_*.npz``).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import brentq
from scipy.stats import qmc

BASE_DIR = Path(__file__).resolve().parent.parent
PARAMS_PATH = BASE_DIR / "parameters.yaml"
WP1_SUMMARY_PATH = BASE_DIR / "data" / "wp1" / "climate_summary_2023.json"
WP3_CSV_PATH = BASE_DIR / "data" / "wp3" / "wp3_crop_microclimate_scenarios.csv"
WP3_DIR = BASE_DIR / "data" / "wp3"
WP5_DIR = BASE_DIR / "data" / "wp5"

# Cooperative agro-industrial catchment scaling per 1 ha agrivoltaic hub
# (typical Cameroon cooperative washing station / tea factory microgrid estate)
COOP_CATCHMENT_HA: dict[str, float] = {
    "arabica_coffee": 3000.0,      # ~63.8 MWh/yr Foumbot cooperative washing/hulling hub
    "penja_white_pepper": 2000.0,  # ~72.0 MWh/yr Njombé-Penja spice washing/drying hub
    "highland_tea": 450.0,         # ~307.8 MWh/yr Djuttitsa/Ndu CTC + overnight withering factory
}

# Representative emission & operational constants anchored to literature
DIESEL_EF_KG_PER_KWH = 0.80        # Small-scale rural diesel genset (kgCO2e/kWh)
CAMEROON_GRID_EF_KG_PER_KWH = 0.28 # Cameroon national grid mix (hydro + thermal gas/HFO)
BESS_LFP_EF_KG_PER_KWH = 75.0      # Cradle-to-gate LFP pack embodied carbon (kgCO2e/kWh cap)
PV_OM_FRAC_OF_CAPEX = 0.015       # Annual O&M + inverter sinking allowance (1.5%/yr of initial PV CAPEX)
DRIP_IRRIG_CAPEX_USD_HA = 1800.0   # Supplemental dry-season drip hardware for S5 irrigated runs
DRIP_IRRIG_OM_USD_HA_YR = 250.0    # Water pumping + drip line maintenance for S5


def load_yaml(path: Path) -> dict[str, Any]:
    """Load parameters.yaml without external dependencies outside yaml/ruamel."""
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except ImportError:
        from ruamel.yaml import YAML
        loader = YAML(typ="safe")
        with open(path, "r", encoding="utf-8") as fh:
            return loader.load(fh)


def resolve_pv_wm2(npz_data: Any, row: dict[str, Any]) -> np.ndarray:
    """Fetch exact 8760 h PV flux (W/m2) or rescale matching-GCR APT44 template to preserve exact energy."""
    sid = row["scenario_id"]
    key = f"{sid}_pv_wm2"
    if key in npz_data:
        return np.asarray(npz_data[key], dtype=np.float64)
    gcr_pct = int(round(float(row["gcr"]) * 100.0))
    if row["technology"] == "ST_OPV_PM6Y6":
        tpl_key = f"S3_OPV_APT44_GCR{gcr_pct}_pv_wm2"
    else:
        tpl_key = f"S2_cSi_GCR{gcr_pct}_pv_wm2"
    tpl = np.asarray(npz_data[tpl_key], dtype=np.float64)
    tpl_sum = float(np.sum(tpl))
    target_wm2_sum = float(row["pv_mwh_ha_yr"]) * 100.0  # MWh/ha -> kWh/m2 (*0.1) -> sum(W/m2) (*1000*0.1 = *100)
    return tpl * (target_wm2_sum / tpl_sum) if tpl_sum > 0.0 else tpl


def load_wp3_scenarios(path: Path) -> list[dict[str, Any]]:
    """Load WP3 summary CSV rows using Python stdlib csv."""
    numeric_cols = {
        "irrigated", "gcr", "apt_par", "d_act_nm", "d_ag_nm", "d_cap_nm", "pce_ref_pct",
        "effective_par_trans", "effective_shade_pct", "r_fr_mean", "epar_boost_pct",
        "eta_ness_ratio", "view_factor_flp", "yield_kg_ha", "delta_y_total_pct",
        "lever_par_pi_pct", "lever_therm_pct", "lever_vpd_h2o_pct", "lever_spec_q_pct",
        "shapley_residual_pct", "delta_y_dry_pct", "delta_y_wet_pct", "t_leaf_day_c",
        "t_leaf_dry_day_c", "t_pv_day_c", "dt_leaf_day_c", "dt_leaf_dry_day_c",
        "dt_pv_excess_day_c", "t_leaf_p95_c", "t_pv_p95_c", "vpd_leaf_day_kpa",
        "vpd_leaf_p95_kpa", "gs_day_mean", "rn_leaf_day_wm2", "par_to_ipi_ratio",
        "f_pi_day_mean", "f_soil_dry_mean", "transp_mm_yr", "transp_rad_mm_yr",
        "transp_aero_mm_yr", "delta_et_rad_mm", "delta_et_aero_mm", "delta_et_pct",
        "delta_wue_pct", "pv_mwh_ha_yr", "pv_kwh_m2_yr", "max_energy_res_wm2",
    }
    rows: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            parsed: dict[str, Any] = {}
            for k, v in row.items():
                if k in numeric_cols:
                    parsed[k] = float(v)
                else:
                    parsed[k] = v
            rows.append(parsed)
    return rows


def build_factory_load_profile(
    crop_name: str,
    crop_cfg: dict[str, Any],
    yield_kg_ha: float,
    catchment_ha: float,
    tea_kwh_per_t_override: float | None = None,
) -> tuple[np.ndarray, float]:
    """
    Construct a normalized 8760 h agro-processing electricity demand series (kW)
    honoring seasonal harvest weighting and exact day/overnight split.
    """
    if crop_name == "highland_tea":
        kwh_per_t = (
            float(tea_kwh_per_t_override)
            if tea_kwh_per_t_override is not None
            else float(crop_cfg["processing_electricity_kwh_tonne"])
        )
    else:
        kwh_per_t = float(crop_cfg["processing_energy_kwh_tonne"])

    annual_kwh = (yield_kg_ha / 1000.0) * kwh_per_t * catchment_ha
    day_frac = float(crop_cfg["processing_daytime_load_fraction"])
    night_frac = 1.0 - day_frac

    hours = np.arange(8760, dtype=np.int32)
    hod = hours % 24
    doy = hours // 24  # 0..364

    # Harvest seasonality multiplier: tea peaks Mar-Nov wet flush; coffee/pepper peak Oct-Feb
    if crop_name == "highland_tea":
        season_w = 1.0 + 0.35 * np.sin(2.0 * np.pi * (doy - 80.0) / 365.0)
    elif crop_name == "arabica_coffee":
        season_w = 1.0 + 0.45 * np.cos(2.0 * np.pi * (doy - 340.0) / 365.0)
    else:  # penja_white_pepper: main harvest Dec-Mar + wet-season drying boost
        season_w = 1.0 + 0.35 * np.cos(2.0 * np.pi * (doy - 20.0) / 365.0)
    season_w = np.clip(season_w, 0.35, None)

    # Hourly weights partitioned strictly into daytime factory shift vs overnight troughs/fans
    day_mask = (hod >= 8) & (hod < 17)      # 9 h daytime processing window (CTC/milling/drying)
    night_mask = ~day_mask                  # 15 h evening/overnight withering & fans

    w_day = np.where(day_mask, season_w, 0.0)
    w_night = np.where(night_mask, season_w, 0.0)
    w_day *= (day_frac * annual_kwh) / np.sum(w_day)
    w_night *= (night_frac * annual_kwh) / np.sum(w_night)

    load_kw = w_day + w_night
    return load_kw, float(annual_kwh)


def size_bess_kwh(
    load_kw: np.ndarray,
    day_frac: float,
    bess_option: str,
) -> float:
    """Determine nominal LFP storage capacity (kWh) from the 3 WP5 dispatch regimes."""
    if bess_option == "no_bess_daytime_only":
        return 0.0
    hours = np.arange(8760) % 24
    day_mask = (hours >= 8) & (hours < 17)
    if bess_option == "small_lfp_buffer_2h":
        mean_day_kw = float(np.mean(load_kw[day_mask]))
        return round(2.0 * mean_day_kw / 0.85, 2)  # 2 h daytime buffer at 85% usable DoD
    if bess_option == "overnight_withering_bess":
        daily_loads = load_kw.reshape(365, 24)
        night_mask_24 = ~day_mask[:24]
        overnight_daily_kwh = np.sum(daily_loads[:, night_mask_24], axis=1)
        p90_night_kwh = float(np.percentile(overnight_daily_kwh, 90.0))
        return round(p90_night_kwh / 0.85, 2)  # 90th-percentile night load covered cleanly
    raise ValueError(f"Unknown BESS dispatch option: {bess_option}")


def simulate_8760_dispatch(
    pv_wm2: np.ndarray,
    load_kw: np.ndarray,
    bess_cap_kwh: float,
    bess_rte: float = 0.90,
    allow_grid_export: bool = True,
) -> dict[str, float]:
    """
    Hourly energy conservation dispatch (1 ha AV hub).
    1 ha PV kW_ac(t) = pv_wm2(t) * 10,000 m^2/ha / 1,000 W/kW = pv_wm2(t) * 10.0.
    Returns annual kWh flows, fractions, cycles, and exact residual check.
    """
    pv_kw = np.asarray(pv_wm2, dtype=np.float64) * 10.0
    load_kw = np.asarray(load_kw, dtype=np.float64)

    direct_kw = np.minimum(pv_kw, load_kw)
    surplus = pv_kw - direct_kw
    deficit = load_kw - direct_kw

    e_direct = float(np.sum(direct_kw))
    e_pv = float(np.sum(pv_kw))
    e_load = float(np.sum(load_kw))

    if bess_cap_kwh <= 0.0:
        e_export = float(np.sum(surplus)) if allow_grid_export else 0.0
        e_curtail = 0.0 if allow_grid_export else float(np.sum(surplus))
        e_diesel = float(np.sum(deficit))
        return {
            "e_pv_kwh": e_pv,
            "e_load_kwh": e_load,
            "e_direct_kwh": e_direct,
            "e_bess_in_kwh": 0.0,
            "e_bess_out_kwh": 0.0,
            "e_bess_loss_kwh": 0.0,
            "e_export_kwh": e_export,
            "e_curtail_kwh": e_curtail,
            "e_diesel_kwh": e_diesel,
            "e_self_consumed_kwh": e_direct,
            "self_consumption_pct": (100.0 * e_direct / e_pv) if e_pv > 0 else 0.0,
            "load_solar_fraction_pct": (100.0 * e_direct / e_load) if e_load > 0 else 0.0,
            "effective_rte": 0.0,
            "energy_balance_err_kwh": abs(e_pv - (e_direct + e_export + e_curtail)),
        }

    eta_c = math.sqrt(bess_rte)
    eta_d = math.sqrt(bess_rte)
    soc_min = 0.15 * bess_cap_kwh
    soc_max = 1.00 * bess_cap_kwh
    soc_init = 0.50 * bess_cap_kwh
    soc = soc_init
    p_max_kw = 0.5 * bess_cap_kwh  # C/2 LFP charge/discharge limit

    e_bess_in = 0.0
    e_bess_out = 0.0
    e_export = 0.0
    e_curtail = 0.0
    e_diesel = 0.0

    for t in range(len(pv_kw)):
        s = surplus[t]
        d = deficit[t]
        if s > 0.0:
            headroom_grid = (soc_max - soc) / eta_c
            ch_grid = min(s, p_max_kw, headroom_grid)
            soc += ch_grid * eta_c
            e_bess_in += ch_grid
            rem_surplus = s - ch_grid
            if allow_grid_export:
                e_export += rem_surplus
            else:
                e_curtail += rem_surplus
        elif d > 0.0:
            avail_ac = (soc - soc_min) * eta_d
            dis_ac = min(d, p_max_kw, avail_ac)
            soc -= dis_ac / eta_d
            e_bess_out += dis_ac
            e_diesel += (d - dis_ac)

    delta_soc = soc - soc_init
    e_self = e_direct + e_bess_out
    e_bess_loss = e_bess_in - e_bess_out - delta_soc
    # Exact PV balance: e_pv == e_direct + e_bess_in + e_export + e_curtail
    pv_err = abs(e_pv - (e_direct + e_bess_in + e_export + e_curtail))
    eff_rte = (e_bess_out / e_bess_in) if e_bess_in > 1e-9 else 0.0

    return {
        "e_pv_kwh": e_pv,
        "e_load_kwh": e_load,
        "e_direct_kwh": e_direct,
        "e_bess_in_kwh": e_bess_in,
        "e_bess_out_kwh": e_bess_out,
        "e_bess_loss_kwh": e_bess_loss,
        "e_export_kwh": e_export,
        "e_curtail_kwh": e_curtail,
        "e_diesel_kwh": e_diesel,
        "e_self_consumed_kwh": e_self,
        "self_consumption_pct": (100.0 * e_self / e_pv) if e_pv > 0 else 0.0,
        "load_solar_fraction_pct": (100.0 * e_self / e_load) if e_load > 0 else 0.0,
        "effective_rte": eff_rte,
        "energy_balance_err_kwh": pv_err,
    }


def evaluate_20yr_tea_lca(
    technology: str,
    crop_name: str,
    gcr: float,
    yield_kg_ha: float,
    pv_kwh_yr_base: float,
    dispatch_yr1: dict[str, float],
    bess_cap_kwh: float,
    irrigated: bool,
    cfg: dict[str, Any],
    t80_opv_override: float | None = None,
    c_mod_opv_override: float | None = None,
    c_rep_opv_override: float | None = None,
    c_bos_opv_override: float | None = None,
    c_bos_si_override: float | None = None,
    wacc_override: float | None = None,
    carbon_price_usd_t: float = 0.0,
    subsidy_rate: float = 0.0,
    certified_price: bool = False,
    lca_mod_opv_override: float | None = None,
    lca_bos_si_override: float | None = None,
    allow_grid_export: bool = True,
) -> dict[str, float]:
    """
    Evaluate 20-year DCF financials (NPV, IRR, DPBP, LCOE, LER) and Dual-FU ISO LCA
    for open control (S0/S1), c-Si AV (S2/S5), or ST-OPV AV (S3/S4/S5).
    Zero carbon credit & zero subsidy by default.
    """
    econ = cfg["economics"]
    opv_cfg = cfg["opv_technology"]
    si_cfg = cfg["si_counterfactual"]
    crop_cfg = cfg["crops"][crop_name]

    horizon = int(econ["analysis_period_years"])
    wacc = float(wacc_override if wacc_override is not None else econ["discount_rate_wacc"])
    fx = float(econ["currency_rate_xaf_per_usd"])
    diesel_usd_kwh = float(econ["diesel_generation_cost_usd_kwh"])
    export_usd_kwh = float(econ["grid_export_tariff_usd_kwh"]) if allow_grid_export else 0.0
    bess_usd_kwh = float(econ["bess_lfp_capex_usd_kwh"])
    bess_life = float(econ["bess_lifetime_years"])

    if certified_price:
        for pk in ("certified_organic_price_xaf_kg", "certified_pgi_price_xaf_kg", "certified_premium_price_xaf_kg"):
            if pk in crop_cfg:
                price_xaf = float(crop_cfg[pk])
                break
        else:
            price_xaf = float(crop_cfg["farmgate_price_xaf_kg"])
    else:
        price_xaf = float(crop_cfg["farmgate_price_xaf_kg"])
    crop_rev_annual = yield_kg_ha * (price_xaf / fx)

    # Avoided Penja living tutor upkeep (only when engineered AV frame is installed)
    tutor_savings = (
        float(econ["avoided_pepper_living_tutor_cost_usd_ha_yr"])
        if (crop_name == "penja_white_pepper" and technology in ("ST_OPV_PM6Y6", "cSi_Opaque_AV"))
        else 0.0
    )

    area_mod_m2 = 10000.0 * gcr
    # 1-ha crop-specific processing demand for open-field farm accounting
    e_load_coop_yr = dispatch_yr1["e_load_kwh"]
    catchment_ha = COOP_CATCHMENT_HA[crop_name]
    e_load_1ha_yr = e_load_coop_yr / max(catchment_ha, 1.0)

    # Non-PV control baselines (S0 / S1): 1-ha crop + 1-ha diesel processing share + optional irrigation
    if technology in ("Open_Field", "Open_Field_Irrigated", "Natural_Shade", "Open_Control", "Agroforestry_Shade"):
        irrig_capex = DRIP_IRRIG_CAPEX_USD_HA if irrigated else 0.0
        irrig_om = DRIP_IRRIG_OM_USD_HA_YR if irrigated else 0.0
        cf0 = -irrig_capex
        annual_net = crop_rev_annual - irrig_om - e_load_1ha_yr * diesel_usd_kwh
        pv_cf = sum(annual_net / ((1.0 + wacc) ** yr) for yr in range(1, horizon + 1))
        npv = cf0 + pv_cf

        # Control emissions: 1-ha crop diesel processing burden
        annual_diesel_co2 = e_load_1ha_yr * DIESEL_EF_KG_PER_KWH
        return {
            "npv_usd_ha": npv,
            "irr_pct": float("nan"),
            "dpbp_yr": float("nan"),
            "lcoe_usd_kwh": float("nan"),
            "capex_initial_usd_ha": irrig_capex,
            "pv_rep_disc_usd_ha": 0.0,
            "pv_elec_disc_mwh_ha": 0.0,
            "annual_crop_rev_usd_ha": crop_rev_annual,
            "annual_pv_rev_usd_ha": 0.0,
            "lca_embodied_20yr_kgco2e_ha": 0.0,
            "lca_net_area_kgco2e_ha_yr": annual_diesel_co2,
            "lca_pv_intensity_gco2e_kwh": float("nan"),
            "lca_displaced_tco2e_ha_yr": 0.0,
        }

    # PV system hardware cost & degradation schedules
    if technology == "ST_OPV_PM6Y6":
        t80 = float(t80_opv_override if t80_opv_override is not None else opv_cfg["t80_lifetime_years"])
        deg_rate = (
            float(opv_cfg["degradation_rate_annual"])
            if (t80_opv_override is None or abs(t80 - 5.0) < 1e-6)
            else (1.0 - (0.80 ** (1.0 / max(t80, 1.0))))
        )
        c_mod = float(c_mod_opv_override if c_mod_opv_override is not None else opv_cfg["module_cost_usd_per_m2"])
        c_rep = float(c_rep_opv_override if c_rep_opv_override is not None else opv_cfg["replacement_cost_usd_per_m2"])
        c_bos = float(c_bos_opv_override if c_bos_opv_override is not None else opv_cfg["bos_cost_usd_per_m2"])
        lca_mod = float(lca_mod_opv_override if lca_mod_opv_override is not None else opv_cfg["lca_embodied_carbon_module_kgco2e_m2"])
        lca_bos = float(opv_cfg["lca_embodied_carbon_bos_kgco2e_m2"])
    elif technology == "cSi_Opaque_AV":
        t80 = float(si_cfg["lifetime_years"])
        deg_rate = float(si_cfg["degradation_rate_annual"])
        c_mod = float(si_cfg["module_cost_usd_per_m2"])
        c_rep = 0.0
        c_bos = float(c_bos_si_override if c_bos_si_override is not None else si_cfg["bos_structural_cost_usd_per_m2"])
        lca_mod = float(si_cfg["lca_embodied_carbon_module_kgco2e_m2"])
        lca_bos = float(lca_bos_si_override if lca_bos_si_override is not None else si_cfg["lca_embodied_carbon_bos_kgco2e_m2"])
    else:
        raise ValueError(f"Unsupported technology: {technology}")

    pv_capex_gross = area_mod_m2 * (c_mod + c_bos)
    bess_capex_gross = bess_cap_kwh * bess_usd_kwh
    irrig_capex = DRIP_IRRIG_CAPEX_USD_HA if irrigated else 0.0
    capex_initial = (1.0 - subsidy_rate) * (pv_capex_gross + bess_capex_gross) + irrig_capex

    pv_om_annual = PV_OM_FRAC_OF_CAPEX * pv_capex_gross + (DRIP_IRRIG_OM_USD_HA_YR if irrigated else 0.0)

    # Year-by-year PV cycle age, replacements, cashflows & emissions
    rep_years: list[float] = []
    if c_rep > 0.0 and t80 < horizon:
        k = 1
        while k * t80 < horizon - 1e-9:
            rep_years.append(k * t80)
            k += 1

    # Continuous/fractional prorated residual value at year 20 for smooth break-even sensitivity
    if len(rep_years) > 0:
        last_install = rep_years[-1]
        rem_frac = max(0.0, (last_install + t80 - horizon) / t80)
        n_mod_gens = 1.0 + len(rep_years) - rem_frac
    elif t80 > horizon:
        # Linear allocation of long-lived c-Si or >20 yr encapsulated OPV over 20-yr horizon
        n_mod_gens = horizon / t80
        rem_frac = 0.0
    else:
        n_mod_gens = 1.0
        rem_frac = 0.0

    # Schedule replacement cashflows at integer years + smooth end-of-horizon salvage for module remaining life
    rep_cost_per_event = area_mod_m2 * c_rep * (1.0 - subsidy_rate)
    rep_by_yr = np.zeros(horizon + 1, dtype=np.float64)
    for ry in rep_years:
        idx = min(horizon, max(1, int(round(ry))))
        # Interpolate discounted exact cost smoothly between floor/ceil integer years
        f_yr = int(math.floor(ry))
        c_yr = int(math.ceil(ry))
        if f_yr == c_yr:
            rep_by_yr[idx] += rep_cost_per_event
        else:
            w_hi = ry - f_yr
            rep_by_yr[f_yr] += (1.0 - w_hi) * rep_cost_per_event
            rep_by_yr[min(horizon, c_yr)] += w_hi * rep_cost_per_event

    # BESS replacement at Year 10
    if bess_cap_kwh > 0.0 and bess_life < horizon:
        bess_idx = int(round(bess_life))
        rep_by_yr[bess_idx] += bess_cap_kwh * bess_usd_kwh * (1.0 - subsidy_rate)
        bess_gens = horizon / bess_life
    elif bess_cap_kwh > 0.0:
        bess_gens = horizon / bess_life
    else:
        bess_gens = 0.0

    salvage_yr20 = rem_frac * rep_cost_per_event if len(rep_years) > 0 else 0.0

    # Baseline Yr 1 dispatch ratios
    f_self = (dispatch_yr1["e_self_consumed_kwh"] / pv_kwh_yr_base) if pv_kwh_yr_base > 1e-9 else 0.0
    f_exp = (dispatch_yr1["e_export_kwh"] / pv_kwh_yr_base) if pv_kwh_yr_base > 1e-9 else 0.0
    e_bess_loss_yr1 = dispatch_yr1["e_bess_loss_kwh"]

    cashflows = np.zeros(horizon + 1, dtype=np.float64)
    cashflows[0] = -capex_initial

    disc_pv_costs = capex_initial - irrig_capex
    disc_pv_kwh = 0.0
    cum_pv_kwh = 0.0
    cum_self_kwh = 0.0
    cum_exp_kwh = 0.0

    for yr in range(1, horizon + 1):
        # Age since last module install (smooth cyclic age for T80 resets)
        active_install = 0.0
        for ry in rep_years:
            if ry <= (yr - 1) + 1e-9:
                active_install = ry
        mod_age = max(0.0, (yr - 1) - active_install)
        deg_factor = (1.0 - deg_rate) ** mod_age

        pv_yr = pv_kwh_yr_base * deg_factor
        # Maintain self-consumption cap at cooperative factory load; do not charge remaining coop diesel to 1-ha AV asset
        self_yr = min(e_load_coop_yr, pv_yr * f_self)
        exp_yr = max(0.0, pv_yr - self_yr - e_bess_loss_yr1 * deg_factor) if allow_grid_export else 0.0

        # Avoided factory diesel revenue + grid export revenue (less 1-ha crop's own processing burden)
        pv_rev_yr = self_yr * diesel_usd_kwh + exp_yr * export_usd_kwh - e_load_1ha_yr * diesel_usd_kwh
        # Carbon revenue credit (0 at baseline; >0 in policy sensitivity)
        co2_displaced_yr_t = (self_yr * DIESEL_EF_KG_PER_KWH + exp_yr * CAMEROON_GRID_EF_KG_PER_KWH) / 1000.0
        carbon_rev_yr = co2_displaced_yr_t * carbon_price_usd_t

        cf_yr = crop_rev_annual + tutor_savings + pv_rev_yr + carbon_rev_yr - pv_om_annual - rep_by_yr[yr]
        if yr == horizon:
            cf_yr += salvage_yr20
        cashflows[yr] = cf_yr

        disc_factor = 1.0 / ((1.0 + wacc) ** yr)
        pv_only_cost_yr = (pv_om_annual - (DRIP_IRRIG_OM_USD_HA_YR if irrigated else 0.0)) + rep_by_yr[yr] - (salvage_yr20 if yr == horizon else 0.0)
        disc_pv_costs += pv_only_cost_yr * disc_factor
        disc_pv_kwh += pv_yr * disc_factor

        cum_pv_kwh += pv_yr
        cum_self_kwh += self_yr
        cum_exp_kwh += exp_yr

    discounts = np.array([(1.0 + wacc) ** t for t in range(horizon + 1)], dtype=np.float64)
    npv = float(np.sum(cashflows / discounts))
    pv_rep_disc = float(sum(rep_by_yr[t] / discounts[t] for t in range(1, horizon + 1)) - salvage_yr20 / discounts[horizon])

    # IRR (if sign change exists)
    try:
        if cashflows[0] < 0.0 and np.sum(cashflows[1:]) > -cashflows[0]:
            irr = brentq(lambda r: float(np.sum(cashflows / ((1.0 + r) ** np.arange(horizon + 1)))), -0.25, 2.5) * 100.0
        else:
            irr = float("nan")
    except ValueError:
        irr = float("nan")

    # Discounted payback period (DPBP)
    cum_disc = np.cumsum(cashflows / discounts)
    dpbp = float("nan")
    for t in range(1, horizon + 1):
        if cum_disc[t] >= 0.0 and cum_disc[t - 1] < 0.0:
            frac = -cum_disc[t - 1] / max(cum_disc[t] - cum_disc[t - 1], 1e-9)
            dpbp = (t - 1) + frac
            break

    lcoe = (disc_pv_costs / disc_pv_kwh) if disc_pv_kwh > 1e-6 else float("nan")

    # ISO 14040/14044 Dual-FU LCA
    embodied_20yr_kg = area_mod_m2 * (n_mod_gens * lca_mod + lca_bos) + bess_gens * bess_cap_kwh * BESS_LFP_EF_KG_PER_KWH
    pv_co2_intensity_g_kwh = (1000.0 * embodied_20yr_kg / cum_pv_kwh) if cum_pv_kwh > 1e-6 else float("nan")
    avg_displaced_t_yr = ((cum_self_kwh * DIESEL_EF_KG_PER_KWH + cum_exp_kwh * CAMEROON_GRID_EF_KG_PER_KWH) / horizon) / 1000.0
    net_area_kg_ha_yr = embodied_20yr_kg / horizon + e_load_1ha_yr * DIESEL_EF_KG_PER_KWH - avg_displaced_t_yr * 1000.0

    return {
        "npv_usd_ha": npv,
        "irr_pct": irr,
        "dpbp_yr": dpbp,
        "lcoe_usd_kwh": lcoe,
        "capex_initial_usd_ha": capex_initial,
        "pv_rep_disc_usd_ha": pv_rep_disc,
        "pv_elec_disc_mwh_ha": disc_pv_kwh / 1000.0,
        "annual_crop_rev_usd_ha": crop_rev_annual,
        "annual_pv_rev_usd_ha": (cum_self_kwh * diesel_usd_kwh + cum_exp_kwh * export_usd_kwh) / horizon,
        "lca_embodied_20yr_kgco2e_ha": embodied_20yr_kg,
        "lca_net_area_kgco2e_ha_yr": net_area_kg_ha_yr,
        "lca_pv_intensity_gco2e_kwh": pv_co2_intensity_g_kwh,
        "lca_displaced_tco2e_ha_yr": avg_displaced_t_yr,
    }


def _evaluate_crop_break_even_worker(task: tuple[str, dict[str, Any], dict[str, Any], dict[str, Any], np.ndarray, np.ndarray]) -> dict[str, Any]:
    """Solve break-even OPV T80* (economic NPV & carbon gCO2e/kWh) and 2D (T80, cost_ratio) phase map."""
    crop_name, cfg, opv_row, csi_row, t80_grid, ratio_grid = task
    crop_cfg = cfg["crops"][crop_name]
    catchment = COOP_CATCHMENT_HA[crop_name]

    npz_data = np.load(WP3_DIR / f"hourly_{crop_name}.npz")
    pv_opv = resolve_pv_wm2(npz_data, opv_row)
    pv_csi = resolve_pv_wm2(npz_data, csi_row)

    load_opv, _ = build_factory_load_profile(crop_name, crop_cfg, float(opv_row["yield_kg_ha"]), catchment)
    load_csi, _ = build_factory_load_profile(crop_name, crop_cfg, float(csi_row["yield_kg_ha"]), catchment)

    # Evaluate under default daytime + 2h buffer or overnight BESS
    bess_opt = "overnight_withering_bess" if crop_name == "highland_tea" else "small_lfp_buffer_2h"
    bess_opv = size_bess_kwh(load_opv, float(crop_cfg["processing_daytime_load_fraction"]), bess_opt)
    bess_csi = size_bess_kwh(load_csi, float(crop_cfg["processing_daytime_load_fraction"]), bess_opt)
    disp_opv = simulate_8760_dispatch(pv_opv, load_opv, bess_opv, float(cfg["economics"]["bess_roundtrip_efficiency"]))
    disp_csi = simulate_8760_dispatch(pv_csi, load_csi, bess_csi, float(cfg["economics"]["bess_roundtrip_efficiency"]))

    res_csi = evaluate_20yr_tea_lca(
        "cSi_Opaque_AV", crop_name, float(csi_row["gcr"]), float(csi_row["yield_kg_ha"]),
        float(csi_row["pv_mwh_ha_yr"]) * 1000.0, disp_csi, bess_csi, bool(csi_row["irrigated"]), cfg
    )

    def _delta_npv_at_t80(t80_val: float, c_mod_val: float | None = None, c_rep_val: float | None = None) -> float:
        res_opv = evaluate_20yr_tea_lca(
            "ST_OPV_PM6Y6", crop_name, float(opv_row["gcr"]), float(opv_row["yield_kg_ha"]),
            float(opv_row["pv_mwh_ha_yr"]) * 1000.0, disp_opv, bess_opv, bool(opv_row["irrigated"]), cfg,
            t80_opv_override=t80_val, c_mod_opv_override=c_mod_val, c_rep_opv_override=c_rep_val,
        )
        return res_opv["npv_usd_ha"] - res_csi["npv_usd_ha"]

    def _delta_lca_at_t80(t80_val: float) -> float:
        res_opv = evaluate_20yr_tea_lca(
            "ST_OPV_PM6Y6", crop_name, float(opv_row["gcr"]), float(opv_row["yield_kg_ha"]),
            float(opv_row["pv_mwh_ha_yr"]) * 1000.0, disp_opv, bess_opv, bool(opv_row["irrigated"]), cfg,
            t80_opv_override=t80_val,
        )
        return res_opv["lca_pv_intensity_gco2e_kwh"] - res_csi["lca_pv_intensity_gco2e_kwh"]

    # Root-find break-even T80* over [2.0, 35.0] yr
    try:
        f_lo, f_hi = _delta_npv_at_t80(2.0), _delta_npv_at_t80(35.0)
        if f_lo * f_hi < 0.0:
            t80_npv_star = float(brentq(_delta_npv_at_t80, 2.0, 35.0))
        elif f_lo >= 0.0:
            t80_npv_star = 2.0
        else:
            t80_npv_star = float("inf")
    except Exception:
        t80_npv_star = float("nan")

    try:
        g_lo, g_hi = _delta_lca_at_t80(2.0), _delta_lca_at_t80(35.0)
        if g_lo * g_hi < 0.0:
            t80_lca_star = float(brentq(_delta_lca_at_t80, 2.0, 35.0))
        elif g_lo <= 0.0:
            t80_lca_star = 2.0
        else:
            t80_lca_star = float("inf")
    except Exception:
        t80_lca_star = float("nan")

    # Solve roll-to-roll target (C_mod = 15 USD/m2) break-even T80* too
    c_rep_ratio = float(cfg["opv_technology"]["replacement_cost_usd_per_m2"]) / float(cfg["opv_technology"]["module_cost_usd_per_m2"])
    try:
        f_r2r_lo = _delta_npv_at_t80(2.0, 15.0, 15.0 * c_rep_ratio)
        f_r2r_hi = _delta_npv_at_t80(35.0, 15.0, 15.0 * c_rep_ratio)
        if f_r2r_lo * f_r2r_hi < 0.0:
            t80_npv_r2r15_star = float(brentq(lambda x: _delta_npv_at_t80(x, 15.0, 15.0 * c_rep_ratio), 2.0, 35.0))
        elif f_r2r_lo >= 0.0:
            t80_npv_r2r15_star = 2.0
        else:
            t80_npv_r2r15_star = float("inf")
    except Exception:
        t80_npv_r2r15_star = float("nan")

    # 2D Break-even grid (T80_opv, C_mod_opv / C_bos_si)
    c_bos_si_nom = float(cfg["si_counterfactual"]["bos_structural_cost_usd_per_m2"])
    delta_npv_grid = np.zeros((len(t80_grid), len(ratio_grid)), dtype=np.float64)
    delta_lca_grid = np.zeros((len(t80_grid), len(ratio_grid)), dtype=np.float64)
    for i, t80_v in enumerate(t80_grid):
        for j, r_v in enumerate(ratio_grid):
            c_mod_v = float(r_v) * c_bos_si_nom
            c_rep_v = c_mod_v * c_rep_ratio
            r_opv = evaluate_20yr_tea_lca(
                "ST_OPV_PM6Y6", crop_name, float(opv_row["gcr"]), float(opv_row["yield_kg_ha"]),
                float(opv_row["pv_mwh_ha_yr"]) * 1000.0, disp_opv, bess_opv, bool(opv_row["irrigated"]), cfg,
                t80_opv_override=float(t80_v), c_mod_opv_override=c_mod_v, c_rep_opv_override=c_rep_v,
            )
            delta_npv_grid[i, j] = r_opv["npv_usd_ha"] - res_csi["npv_usd_ha"]
            delta_lca_grid[i, j] = r_opv["lca_pv_intensity_gco2e_kwh"] - res_csi["lca_pv_intensity_gco2e_kwh"]

    return {
        "crop": crop_name,
        "opv_ref_scenario": opv_row["scenario_id"],
        "csi_ref_scenario": csi_row["scenario_id"],
        "bess_option_ref": bess_opt,
        "t80_npv_breakeven_yr": t80_npv_star,
        "t80_npv_breakeven_r2r15_yr": t80_npv_r2r15_star,
        "t80_lca_breakeven_yr": t80_lca_star,
        "delta_npv_grid": delta_npv_grid,
        "delta_lca_grid": delta_lca_grid,
    }


def run_sobol_qmc(
    crop_name: str,
    cfg: dict[str, Any],
    opv_row: dict[str, Any],
    csi_row: dict[str, Any],
    n_samples: int = 10000,
    seed: int = 42,
) -> dict[str, Any]:
    """
    Vectorized Saltelli / Jansen QMC Sobol sensitivity analysis (N=10,000 base draws)
    comparing ΔNPV = NPV(ST-OPV) - NPV(c-Si) AND OPV NPV(USD/ha) across 12 uncertain
    techno-economic, agronomic, and bounded quantum NESS inputs.
    """
    crop_cfg = cfg["crops"][crop_name]
    econ = cfg["economics"]
    opv_cfg = cfg["opv_technology"]
    si_cfg = cfg["si_counterfactual"]
    catchment = COOP_CATCHMENT_HA[crop_name]

    npz_data = np.load(WP3_DIR / f"hourly_{crop_name}.npz")
    pv_opv = resolve_pv_wm2(npz_data, opv_row)
    pv_csi = resolve_pv_wm2(npz_data, csi_row)
    load_opv, _ = build_factory_load_profile(crop_name, crop_cfg, float(opv_row["yield_kg_ha"]), catchment)
    load_csi, _ = build_factory_load_profile(crop_name, crop_cfg, float(csi_row["yield_kg_ha"]), catchment)

    bess_opt = "overnight_withering_bess" if crop_name == "highland_tea" else "small_lfp_buffer_2h"
    bess_opv_nom = size_bess_kwh(load_opv, float(crop_cfg["processing_daytime_load_fraction"]), bess_opt)
    bess_csi_nom = size_bess_kwh(load_csi, float(crop_cfg["processing_daytime_load_fraction"]), bess_opt)
    disp_opv = simulate_8760_dispatch(pv_opv, load_opv, bess_opv_nom, float(econ["bess_roundtrip_efficiency"]))
    disp_csi = simulate_8760_dispatch(pv_csi, load_csi, bess_csi_nom, float(econ["bess_roundtrip_efficiency"]))

    # 12 uncertain parameters anchored to parameters.yaml bounds
    param_specs = [
        ("t80_opv_yr", 3.0, 25.0),
        ("c_mod_opv_usd_m2", 10.0, 45.0),
        ("c_bos_opv_usd_m2", 12.0, 30.0),
        ("c_bos_si_usd_m2", 35.0, 85.0),
        ("wacc", 0.06, 0.15),
        ("diesel_usd_kwh", 0.30, 0.60),
        ("export_tariff_usd_kwh", 0.04, 0.12),
        ("bess_usd_kwh", 108.0, 280.0),
        ("crop_price_mult", 0.80, 1.35),
        ("yield_gain_mult", 0.80, 1.20),
        ("eta_ness_shift_pct", -0.02, 0.10),  # Conservative +/- bound bracketing WP2 Delta_eta_NESS
        ("carbon_price_usd_t", 0.0, 25.0),
    ]
    d = len(param_specs)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        sampler = qmc.Sobol(d=2 * d, scramble=True, seed=seed)
        ab = sampler.random(n=n_samples)
    A_u = ab[:, :d]
    B_u = ab[:, d:]

    lows = np.array([p[1] for p in param_specs], dtype=np.float64)
    highs = np.array([p[2] for p in param_specs], dtype=np.float64)

    a_opv = 10000.0 * float(opv_row["gcr"])
    a_csi = 10000.0 * float(csi_row["gcr"])
    e_opv_yr1 = float(opv_row["pv_mwh_ha_yr"]) * 1000.0
    e_csi_yr1 = float(csi_row["pv_mwh_ha_yr"]) * 1000.0
    y_opv_kg = float(opv_row["yield_kg_ha"])
    y_csi_kg = float(csi_row["yield_kg_ha"])
    fx = float(econ["currency_rate_xaf_per_usd"])
    price_usd_kg = float(crop_cfg["farmgate_price_xaf_kg"]) / fx
    tutor_save = float(econ["avoided_pepper_living_tutor_cost_usd_ha_yr"]) if crop_name == "penja_white_pepper" else 0.0

    f_self_opv = disp_opv["e_self_consumed_kwh"] / e_opv_yr1
    f_exp_opv = disp_opv["e_export_kwh"] / e_opv_yr1
    f_self_csi = disp_csi["e_self_consumed_kwh"] / e_csi_yr1
    f_exp_csi = disp_csi["e_export_kwh"] / e_csi_yr1
    e_load = disp_opv["e_load_kwh"]
    e_load_1ha = e_load / max(catchment, 1.0)

    c_mod_si = float(si_cfg["module_cost_usd_per_m2"])
    d_si = float(si_cfg["degradation_rate_annual"])
    c_rep_ratio = float(opv_cfg["replacement_cost_usd_per_m2"]) / float(opv_cfg["module_cost_usd_per_m2"])
    yrs = np.arange(1, 21, dtype=np.float64)[:, None]  # (20, 1)

    def _eval_batch(u_mat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Vectorized 20-year DCF evaluator across N samples."""
        X = lows + u_mat * (highs - lows)
        t80 = X[:, 0]
        c_mod_opv = X[:, 1]
        c_bos_opv = X[:, 2]
        c_bos_si = X[:, 3]
        wacc = X[:, 4]
        p_diesel = X[:, 5]
        p_exp = X[:, 6]
        c_bess = X[:, 7]
        p_mult = X[:, 8]
        y_mult = X[:, 9]
        q_shift = 1.0 + X[:, 10] / 100.0
        p_co2 = X[:, 11]

        disc = 1.0 / ((1.0 + wacc[None, :]) ** yrs)  # (20, N)

        # --- ST-OPV ---
        d_opv = 1.0 - (0.80 ** (1.0 / t80))
        c_rep_opv = c_mod_opv * c_rep_ratio * a_opv
        pv_capex_opv = a_opv * (c_mod_opv + c_bos_opv)
        om_opv = PV_OM_FRAC_OF_CAPEX * pv_capex_opv

        # Smooth replacement annuity & cycling degradation across T80 in [3, 25]
        n_cycles = np.maximum(0.0, np.ceil(20.0 / t80) - 1.0)
        # Expected discounted module replacement cashflow using uniform renewal times t_k = k*T80 < 20
        rep_disc_opv = np.zeros(len(t80), dtype=np.float64)
        for k in range(1, 7):
            tk = k * t80
            active = tk < 20.0
            rep_disc_opv += np.where(active, c_rep_opv / ((1.0 + wacc) ** tk), 0.0)
        last_tk = np.floor((20.0 - 1e-6) / t80) * t80
        rem_frac = np.where(last_tk > 0.0, np.maximum(0.0, (last_tk + t80 - 20.0) / t80), 0.0)
        rep_disc_opv -= rem_frac * c_rep_opv / ((1.0 + wacc) ** 20.0)

        bess_capex_opv = bess_opv_nom * c_bess
        bess_disc_opv = bess_capex_opv * (1.0 + 1.0 / ((1.0 + wacc) ** 10.0))

        # Cyclic module age over 20 years: ((yr-1) mod T80)
        mod_age_opv = np.mod(yrs - 1.0, t80[None, :])
        deg_opv = (1.0 - d_opv[None, :]) ** mod_age_opv
        pv_opv_t = e_opv_yr1 * deg_opv
        self_opv_t = np.minimum(e_load, pv_opv_t * f_self_opv)
        exp_opv_t = np.maximum(0.0, pv_opv_t * f_exp_opv)

        crop_rev_opv = (y_opv_kg * y_mult * q_shift) * (price_usd_kg * p_mult)
        co2_opv_t = (self_opv_t * DIESEL_EF_KG_PER_KWH + exp_opv_t * CAMEROON_GRID_EF_KG_PER_KWH) / 1000.0
        cf_opv_t = (
            crop_rev_opv[None, :]
            + tutor_save
            + self_opv_t * p_diesel[None, :]
            + exp_opv_t * p_exp[None, :]
            - e_load_1ha * p_diesel[None, :]
            + co2_opv_t * p_co2[None, :]
            - om_opv[None, :]
        )
        npv_opv = -pv_capex_opv - rep_disc_opv - bess_disc_opv + np.sum(cf_opv_t * disc, axis=0)

        # --- c-Si Counterfactual ---
        pv_capex_si = a_csi * (c_mod_si + c_bos_si)
        om_si = PV_OM_FRAC_OF_CAPEX * pv_capex_si
        bess_disc_si = (bess_csi_nom * c_bess) * (1.0 + 1.0 / ((1.0 + wacc) ** 10.0))
        deg_si = (1.0 - d_si) ** (yrs - 1.0)
        pv_si_t = e_csi_yr1 * deg_si
        self_si_t = np.minimum(e_load, pv_si_t * f_self_csi)
        exp_si_t = np.maximum(0.0, pv_si_t * f_exp_csi)
        crop_rev_si = (y_csi_kg * y_mult) * (price_usd_kg * p_mult)
        co2_si_t = (self_si_t * DIESEL_EF_KG_PER_KWH + exp_si_t * CAMEROON_GRID_EF_KG_PER_KWH) / 1000.0
        cf_si_t = (
            crop_rev_si[None, :]
            + tutor_save
            + self_si_t * p_diesel[None, :]
            + exp_si_t * p_exp[None, :]
            - e_load_1ha * p_diesel[None, :]
            + co2_si_t * p_co2[None, :]
            - om_si[None, :]
        )
        npv_si = -pv_capex_si - bess_disc_si + np.sum(cf_si_t * disc, axis=0)
        return npv_opv, npv_opv - npv_si

    yA_opv, yA_diff = _eval_batch(A_u)
    yB_opv, yB_diff = _eval_batch(B_u)

    def _sobol_indices(yA: np.ndarray, yB: np.ndarray, eval_AB_list: list[np.ndarray]) -> dict[str, dict[str, float]]:
        var_y = float(np.var(np.concatenate([yA, yB]), ddof=1))
        out: dict[str, dict[str, float]] = {}
        for idx, (pname, _, _) in enumerate(param_specs):
            yAB = eval_AB_list[idx]
            # Saltelli 2010 first-order & Jansen total-order estimators
            s_i = float(np.mean(yB * (yAB - yA)) / var_y) if var_y > 1e-12 else 0.0
            s_ti = float(0.5 * np.mean((yA - yAB) ** 2) / var_y) if var_y > 1e-12 else 0.0
            out[pname] = {
                "S_i": max(0.0, min(1.0, s_i)),
                "S_Ti": max(0.0, min(1.0, s_ti)),
                "raw_S_i": s_i,
                "raw_S_Ti": s_ti,
            }
        return out

    ab_opv_list: list[np.ndarray] = []
    ab_diff_list: list[np.ndarray] = []
    for i in range(d):
        AB_i = A_u.copy()
        AB_i[:, i] = B_u[:, i]
        y_opv_i, y_diff_i = _eval_batch(AB_i)
        ab_opv_list.append(y_opv_i)
        ab_diff_list.append(y_diff_i)

    sobol_opv = _sobol_indices(yA_opv, yB_opv, ab_opv_list)
    sobol_diff = _sobol_indices(yA_diff, yB_diff, ab_diff_list)

    return {
        "n_base_samples": n_samples,
        "seed": seed,
        "opv_ref_scenario": opv_row["scenario_id"],
        "csi_ref_scenario": csi_row["scenario_id"],
        "npv_opv_stats_usd_ha": {
            "mean": float(np.mean(yA_opv)),
            "std": float(np.std(yA_opv)),
            "p05": float(np.percentile(yA_opv, 5)),
            "p50": float(np.percentile(yA_opv, 50)),
            "p95": float(np.percentile(yA_opv, 95)),
        },
        "delta_npv_opv_minus_csi_stats_usd_ha": {
            "mean": float(np.mean(yA_diff)),
            "std": float(np.std(yA_diff)),
            "p05": float(np.percentile(yA_diff, 5)),
            "p50": float(np.percentile(yA_diff, 50)),
            "p95": float(np.percentile(yA_diff, 95)),
            "prob_opv_beats_csi": float(np.mean(yA_diff > 0.0)),
        },
        "sobol_npv_opv": sobol_opv,
        "sobol_delta_npv_opv_vs_csi": sobol_diff,
    }


def build_agronomic_phase_grid() -> dict[str, np.ndarray]:
    """
    Evaluate analytical-ecophysiological FVCB-Medlyn + PSII photoinhibition response
    over a 30x30 grid of (PAR_peak / I_sat, VPD_peak_kPa) representing tropical
    ST-OPV shade (tau_PAR = 0.72, dT_leaf = -1.6 C, dVPD_frac = -0.18).
    """
    par_ratio_grid = np.linspace(0.50, 2.20, 30)  # Peak clear-sky PAR / crop I_sat
    vpd_peak_grid = np.linspace(0.60, 4.50, 30)   # Dry-season daytime peak VPD (kPa)
    delta_y_pct = np.zeros((len(par_ratio_grid), len(vpd_peak_grid)), dtype=np.float64)

    # Normalized diurnal sunlit kernel weights (8 daytime bins symmetric around solar noon)
    hod_rel = np.sin(np.linspace(0.15, np.pi - 0.15, 10))
    tau_opv = 0.72  # Effective GCR=0.50, APT=0.44 sub-panel PAR transmittance
    theta_q = 0.70

    for i, r_par in enumerate(par_ratio_grid):
        for j, vpd_pk in enumerate(vpd_peak_grid):
            par_open = r_par * hod_rel  # Normalized to I_sat = 1.0
            par_sh = par_open * tau_opv
            vpd_open = vpd_pk * (0.45 + 0.55 * hod_rel)
            vpd_sh = np.maximum(0.2, vpd_open * 0.82)

            # Rectangular hyperbola + Medlyn stomatal VPD attenuation + excess-PAR photoinhibition
            gs_open = 1.0 / (1.0 + 0.42 * np.sqrt(np.maximum(0.2, vpd_open - 0.8)))
            gs_sh = 1.0 / (1.0 + 0.42 * np.sqrt(np.maximum(0.2, vpd_sh - 0.8)))

            pi_open = 1.0 - 0.28 * np.maximum(0.0, par_open - 1.15) ** 1.25
            pi_sh = 1.0 - 0.28 * np.maximum(0.0, par_sh - 1.15) ** 1.25
            pi_open = np.clip(pi_open, 0.55, 1.0)
            pi_sh = np.clip(pi_sh, 0.55, 1.0)

            # Non-rectangular light limitation
            def _nrh(x: np.ndarray) -> np.ndarray:
                return (x + 1.0 - np.sqrt(np.maximum(0.0, (x + 1.0) ** 2 - 4.0 * theta_q * x))) / (2.0 * theta_q)

            # Thermal supra-optimal penalty tied to peak VPD/solar load (>2.0 kPa dry stress proxy)
            therm_pen_open = 1.0 - 0.055 * np.maximum(0.0, vpd_open - 1.8) ** 1.3
            therm_pen_sh = 1.0 - 0.055 * np.maximum(0.0, vpd_open * 0.84 - 1.8) ** 1.3

            a_open = np.sum(_nrh(par_open) * gs_open * pi_open * therm_pen_open)
            a_sh = np.sum(_nrh(par_sh) * gs_sh * pi_sh * therm_pen_sh)
            delta_y_pct[i, j] = 100.0 * (a_sh - a_open) / max(a_open, 1e-9)

    return {
        "par_ratio_grid": par_ratio_grid,
        "vpd_peak_grid": vpd_peak_grid,
        "delta_y_pct": delta_y_pct,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run WP5 TEA/LCA/Sobol and Regime Phase Maps.")
    parser.add_argument("--workers", type=int, default=3, help="Parallel worker processes.")
    parser.add_argument("--n-sobol", type=int, default=None, help="Override Monte Carlo Sobol sample size.")
    return parser.parse_args()


def main() -> None:
    t0 = time.perf_counter()
    args = parse_args()
    cfg = load_yaml(PARAMS_PATH)
    WP5_DIR.mkdir(parents=True, exist_ok=True)

    wp3_rows = load_wp3_scenarios(WP3_CSV_PATH)
    with open(WP1_SUMMARY_PATH, "r", encoding="utf-8") as fh:
        wp1_summary = json.load(fh)

    n_sobol = int(args.n_sobol if args.n_sobol is not None else cfg["monte_carlo"]["n_samples"])
    seed = int(cfg["monte_carlo"]["random_seed"])
    bess_options = list(cfg["economics"]["bess_dispatch_options"])
    rte = float(cfg["economics"]["bess_roundtrip_efficiency"])

    # Compute standalone ground c-Si reference yield per crop (max S2 PV yield as LER PV baseline)
    pv_standalone_ref: dict[str, float] = {}
    s0_yields: dict[str, float] = {}
    for row in wp3_rows:
        c = row["crop"]
        if row["scenario_id"] == "S0_open_control":
            s0_yields[c] = float(row["yield_kg_ha"])
        if row["technology"] == "cSi_Opaque_AV":
            pv_standalone_ref[c] = max(pv_standalone_ref.get(c, 0.0), float(row["pv_mwh_ha_yr"]))

    # Load all hourly npz once per crop
    hourly_cache = {c: np.load(WP3_DIR / f"hourly_{c}.npz") for c in cfg["crops"]}

    # Build full WP5 TEA/LCA scenario table across S0..S5 & 3 BESS options
    tea_rows: list[dict[str, Any]] = []
    # Map S0 open control NPV/LCA by crop first
    s0_metrics: dict[tuple[str, str], dict[str, float]] = {}

    # Pre-compute S0_open_control baseline NPV by crop before delta comparisons
    for row in wp3_rows:
        if row["scenario_id"] == "S0_open_control":
            crop_name = row["crop"]
            crop_cfg = cfg["crops"][crop_name]
            load_kw, _ = build_factory_load_profile(crop_name, crop_cfg, float(row["yield_kg_ha"]), COOP_CATCHMENT_HA[crop_name])
            zero_disp = simulate_8760_dispatch(np.zeros(8760), load_kw, 0.0, rte)
            s0_metrics[(crop_name, "baseline")] = evaluate_20yr_tea_lca(
                row["technology"], crop_name, 0.0, float(row["yield_kg_ha"]),
                0.0, zero_disp, 0.0, bool(row["irrigated"]), cfg
            )

    # Evaluate S0/S1 controls (zero PV, pure diesel factory load)
    for row in wp3_rows:
        sid = row["scenario_id"]
        crop_name = row["crop"]
        if sid not in ("S0_open_control", "S0_open_irrigated", "S1_agroforestry_shade"):
            continue
        crop_cfg = cfg["crops"][crop_name]
        load_kw, load_kwh = build_factory_load_profile(crop_name, crop_cfg, float(row["yield_kg_ha"]), COOP_CATCHMENT_HA[crop_name])
        zero_disp = simulate_8760_dispatch(np.zeros(8760), load_kw, 0.0, rte)
        res = evaluate_20yr_tea_lca(
            row["technology"], crop_name, 0.0, float(row["yield_kg_ha"]),
            0.0, zero_disp, 0.0, bool(row["irrigated"]), cfg
        )
        tea_rows.append({
            "crop": crop_name,
            "scenario_id": sid,
            "wp5_variant": "control",
            "technology": row["technology"],
            "bess_option": "none_diesel_baseline",
            "bess_cap_kwh": 0.0,
            "gcr": 0.0,
            "apt_par": 0.0,
            "irrigated": int(row["irrigated"]),
            "t80_opv_yr": 0.0,
            "carbon_price_usd_t": 0.0,
            "subsidy_rate": 0.0,
            "certified_price": 0,
            "yield_kg_ha": round(float(row["yield_kg_ha"]), 2),
            "pv_mwh_ha_yr": 0.0,
            "ler": round(float(row["yield_kg_ha"]) / s0_yields[crop_name], 4),
            "self_consumption_pct": 0.0,
            "load_solar_fraction_pct": 0.0,
            "npv_usd_ha": round(res["npv_usd_ha"], 2),
            "delta_npv_vs_s0_usd_ha": round(res["npv_usd_ha"] - s0_metrics[(crop_name, "baseline")]["npv_usd_ha"], 2),
            "irr_pct": "",
            "dpbp_yr": "",
            "lcoe_usd_kwh": "",
            "capex_initial_usd_ha": round(res["capex_initial_usd_ha"], 2),
            "pv_rep_disc_usd_ha": 0.0,
            "lca_embodied_20yr_kgco2e_ha": 0.0,
            "lca_net_area_kgco2e_ha_yr": round(res["lca_net_area_kgco2e_ha_yr"], 2),
            "lca_pv_intensity_gco2e_kwh": "",
            "lca_displaced_tco2e_ha_yr": 0.0,
            "dispatch_err_kwh": 0.0,
        })

    # Identify best OPV & c-Si scenarios per crop for detailed S2/S3/S4/S5 + Sobol runs
    best_opv_by_crop: dict[str, dict[str, Any]] = {}
    best_csi_by_crop: dict[str, dict[str, Any]] = {}
    for row in wp3_rows:
        c = row["crop"]
        sid = row["scenario_id"]
        if row["technology"] == "ST_OPV_PM6Y6" and sid.startswith("S3_OPV"):
            if c not in best_opv_by_crop or float(row["yield_kg_ha"]) > float(best_opv_by_crop[c]["yield_kg_ha"]):
                best_opv_by_crop[c] = row
        elif row["technology"] == "cSi_Opaque_AV" and sid.startswith("S2_cSi"):
            if c not in best_csi_by_crop or float(row["yield_kg_ha"]) > float(best_csi_by_crop[c]["yield_kg_ha"]):
                best_csi_by_crop[c] = row

    # Evaluate ALL WP3 PV scenarios across daytime baseline, plus selected focal scenarios across all 3 BESS options & S4/S5
    focal_ids_per_crop = {
        c: {
            best_opv_by_crop[c]["scenario_id"],
            best_csi_by_crop[c]["scenario_id"],
            "S2_cSi_GCR40",
            "S3_OPV_APT44_GCR65",
            "S5_cSi_GCR40_Irrig",
            "S5_OPV_APT44_GCR65_Irrig",
        }
        for c in cfg["crops"]
    }

    max_dispatch_err_kwh = 0.0
    for row in wp3_rows:
        sid = row["scenario_id"]
        crop_name = row["crop"]
        tech = row["technology"]
        if tech not in ("ST_OPV_PM6Y6", "cSi_Opaque_AV") or sid == "VAL_cSi_Shade47pct":
            continue
        crop_cfg = cfg["crops"][crop_name]
        pv_wm2 = resolve_pv_wm2(hourly_cache[crop_name], row)
        load_kw, _ = build_factory_load_profile(crop_name, crop_cfg, float(row["yield_kg_ha"]), COOP_CATCHMENT_HA[crop_name])

        options_for_row = bess_options if sid in focal_ids_per_crop[crop_name] else ["no_bess_daytime_only"]
        for bess_opt in options_for_row:
            bess_cap = size_bess_kwh(load_kw, float(crop_cfg["processing_daytime_load_fraction"]), bess_opt)
            disp = simulate_8760_dispatch(pv_wm2, load_kw, bess_cap, rte, allow_grid_export=True)
            max_dispatch_err_kwh = max(max_dispatch_err_kwh, disp["energy_balance_err_kwh"])

            variants: list[tuple[str, dict[str, Any]]] = [("baseline_zero_credit", {})]
            # S4 Encapsulated ST-OPV (T80 = 15 yr & 25 yr) + S5 Policy/Price sensitivities on focal APT44_GCR65
            if sid == "S3_OPV_APT44_GCR65" and bess_opt == ("overnight_withering_bess" if crop_name == "highland_tea" else "small_lfp_buffer_2h"):
                variants.extend([
                    ("S4_OPV_encapsulated_T80_15yr", {"t80_opv_override": 15.0}),
                    ("S4_OPV_encapsulated_T80_25yr", {"t80_opv_override": 25.0}),
                    ("S5_carbon25_policy", {"carbon_price_usd_t": 25.0}),
                    ("S5_subsidy40_policy", {"subsidy_rate": 0.40}),
                    ("S5_certified_crop_price", {"certified_price": True}),
                    ("S5_wacc_6pct", {"wacc_override": 0.06}),
                    ("S5_wacc_15pct", {"wacc_override": 0.15}),
                    ("S5_offgrid_no_export", {"allow_grid_export": False}),
                ])

            for vname, overrides in variants:
                allow_exp = overrides.get("allow_grid_export", True)
                disp_v = disp if allow_exp else simulate_8760_dispatch(pv_wm2, load_kw, bess_cap, rte, allow_grid_export=False)
                res = evaluate_20yr_tea_lca(
                    tech, crop_name, float(row["gcr"]), float(row["yield_kg_ha"]),
                    float(row["pv_mwh_ha_yr"]) * 1000.0, disp_v, bess_cap, bool(row["irrigated"]), cfg,
                    t80_opv_override=overrides.get("t80_opv_override"),
                    wacc_override=overrides.get("wacc_override"),
                    carbon_price_usd_t=overrides.get("carbon_price_usd_t", 0.0),
                    subsidy_rate=overrides.get("subsidy_rate", 0.0),
                    certified_price=overrides.get("certified_price", False),
                    allow_grid_export=allow_exp,
                )
                ler = (float(row["yield_kg_ha"]) / s0_yields[crop_name]) + (float(row["pv_mwh_ha_yr"]) / pv_standalone_ref[crop_name])
                tea_rows.append({
                    "crop": crop_name,
                    "scenario_id": sid,
                    "wp5_variant": vname,
                    "technology": tech,
                    "bess_option": bess_opt,
                    "bess_cap_kwh": round(bess_cap, 2),
                    "gcr": float(row["gcr"]),
                    "apt_par": round(float(row["apt_par"]), 4),
                    "irrigated": int(row["irrigated"]),
                    "t80_opv_yr": round(float(overrides.get("t80_opv_override", cfg["opv_technology"]["t80_lifetime_years"] if tech == "ST_OPV_PM6Y6" else cfg["si_counterfactual"]["lifetime_years"])), 2),
                    "carbon_price_usd_t": float(overrides.get("carbon_price_usd_t", 0.0)),
                    "subsidy_rate": float(overrides.get("subsidy_rate", 0.0)),
                    "certified_price": int(overrides.get("certified_price", False)),
                    "yield_kg_ha": round(float(row["yield_kg_ha"]), 2),
                    "pv_mwh_ha_yr": round(float(row["pv_mwh_ha_yr"]), 2),
                    "ler": round(ler, 4),
                    "self_consumption_pct": round(disp_v["self_consumption_pct"], 2),
                    "load_solar_fraction_pct": round(disp_v["load_solar_fraction_pct"], 2),
                    "npv_usd_ha": round(res["npv_usd_ha"], 2),
                    "delta_npv_vs_s0_usd_ha": round(res["npv_usd_ha"] - s0_metrics[(crop_name, "baseline")]["npv_usd_ha"], 2),
                    "irr_pct": "" if math.isnan(res["irr_pct"]) else round(res["irr_pct"], 2),
                    "dpbp_yr": "" if math.isnan(res["dpbp_yr"]) else round(res["dpbp_yr"], 2),
                    "lcoe_usd_kwh": round(res["lcoe_usd_kwh"], 4),
                    "capex_initial_usd_ha": round(res["capex_initial_usd_ha"], 2),
                    "pv_rep_disc_usd_ha": round(res["pv_rep_disc_usd_ha"], 2),
                    "lca_embodied_20yr_kgco2e_ha": round(res["lca_embodied_20yr_kgco2e_ha"], 1),
                    "lca_net_area_kgco2e_ha_yr": round(res["lca_net_area_kgco2e_ha_yr"], 1),
                    "lca_pv_intensity_gco2e_kwh": round(res["lca_pv_intensity_gco2e_kwh"], 2),
                    "lca_displaced_tco2e_ha_yr": round(res["lca_displaced_tco2e_ha_yr"], 2),
                    "dispatch_err_kwh": round(disp_v["energy_balance_err_kwh"], 9),
                })

    # Write wp5_tea_lca_scenarios.csv
    csv_path = WP5_DIR / "wp5_tea_lca_scenarios.csv"
    fieldnames = list(tea_rows[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tea_rows)

    # Parallel break-even T80* & 2D technological phase surface on focal equal-shade LUE pair (APT44_GCR65 vs cSi_GCR40)
    focal_opv_by_crop: dict[str, dict[str, Any]] = {}
    focal_csi_by_crop: dict[str, dict[str, Any]] = {}
    for row in wp3_rows:
        if row["scenario_id"] == "S3_OPV_APT44_GCR65":
            focal_opv_by_crop[row["crop"]] = row
        elif row["scenario_id"] == "S2_cSi_GCR40":
            focal_csi_by_crop[row["crop"]] = row

    t80_grid = np.linspace(3.0, 25.0, 23)
    ratio_grid = np.linspace(0.18, 0.90, 25)  # C_mod_OPV / C_BOS_cSi
    be_tasks = [
        (c, cfg, focal_opv_by_crop[c], focal_csi_by_crop[c], t80_grid, ratio_grid)
        for c in cfg["crops"]
    ]
    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(be_tasks))) as pool:
            be_results = list(pool.map(_evaluate_crop_break_even_worker, be_tasks))
    else:
        be_results = [_evaluate_crop_break_even_worker(t) for t in be_tasks]

    # Run N=10,000 QMC Sobol global sensitivity per crop on focal balanced LUE pair
    sobol_summary: dict[str, Any] = {}
    for c in cfg["crops"]:
        sobol_summary[c] = run_sobol_qmc(
            c, cfg, focal_opv_by_crop[c], focal_csi_by_crop[c], n_samples=n_sobol, seed=seed
        )

    with open(WP5_DIR / "wp5_sobol_sensitivity.json", "w", encoding="utf-8") as fh:
        json.dump(sobol_summary, fh, indent=2)

    # Build 2D Agronomic & Tech Phase Maps archive (NPZ)
    agro_grid = build_agronomic_phase_grid()
    # Site dimensionless coords (PAR_p95_day / I_sat, dry-season VPD_p95) from WP1/WP3
    wp1_site_keys = {
        "arabica_coffee": "foumbot_coffee",
        "penja_white_pepper": "njombe_penja_pepper",
        "highland_tea": "djuttitsa_tea",
    }
    site_map_coords = {}
    for c, wp1_k in wp1_site_keys.items():
        sw_day = hourly_cache[c]["sw_ghi"]
        sw_p95_day = float(np.percentile(sw_day[sw_day > 50.0], 95.0))
        par_p95_day = 2.07 * sw_p95_day  # ~45% SW fraction * 4.6 umol/J
        i_sat = float(cfg["crops"][c]["I_sat"])
        vpd_p95 = float(wp1_summary[wp1_k]["dry_dec_feb"]["vpd_p95_kpa"])
        site_map_coords[c] = [par_p95_day / i_sat, vpd_p95]

    npz_payload: dict[str, Any] = {
        "agro_par_ratio_grid": agro_grid["par_ratio_grid"],
        "agro_vpd_peak_grid": agro_grid["vpd_peak_grid"],
        "agro_delta_y_pct": agro_grid["delta_y_pct"],
        "tech_t80_grid": t80_grid,
        "tech_cost_ratio_grid": ratio_grid,
    }
    break_even_summary: dict[str, Any] = {}
    for br in be_results:
        c = br["crop"]
        npz_payload[f"{c}_delta_npv_grid"] = br["delta_npv_grid"]
        npz_payload[f"{c}_delta_lca_grid"] = br["delta_lca_grid"]
        npz_payload[f"{c}_site_coord"] = np.array(site_map_coords[c], dtype=np.float64)
        break_even_summary[c] = {
            "opv_ref_scenario": br["opv_ref_scenario"],
            "csi_ref_scenario": br["csi_ref_scenario"],
            "bess_option_ref": br["bess_option_ref"],
            "t80_npv_breakeven_yr": br["t80_npv_breakeven_yr"],
            "t80_npv_breakeven_r2r15_yr": br["t80_npv_breakeven_r2r15_yr"],
            "t80_lca_breakeven_yr": br["t80_lca_breakeven_yr"],
            "site_par_over_isat": round(site_map_coords[c][0], 3),
            "site_dry_vpd_p95_kpa": round(site_map_coords[c][1], 3),
        }

    np.savez_compressed(WP5_DIR / "wp5_phase_maps.npz", **npz_payload)

    # Validation summary JSON
    summary_payload = {
        "n_tea_lca_rows": len(tea_rows),
        "n_sobol_base_samples": n_sobol,
        "max_dispatch_energy_err_kwh": max_dispatch_err_kwh,
        "coop_catchment_ha": COOP_CATCHMENT_HA,
        "break_even_t80_by_crop": break_even_summary,
        "sobol_highlights": {
            c: {
                "delta_npv_p05_p50_p95_usd_ha": [
                    round(sobol_summary[c]["delta_npv_opv_minus_csi_stats_usd_ha"]["p05"], 1),
                    round(sobol_summary[c]["delta_npv_opv_minus_csi_stats_usd_ha"]["p50"], 1),
                    round(sobol_summary[c]["delta_npv_opv_minus_csi_stats_usd_ha"]["p95"], 1),
                ],
                "prob_opv_beats_csi": round(sobol_summary[c]["delta_npv_opv_minus_csi_stats_usd_ha"]["prob_opv_beats_csi"], 4),
                "top3_S_Ti_delta_npv": sorted(
                    ((k, round(v["S_Ti"], 5)) for k, v in sobol_summary[c]["sobol_delta_npv_opv_vs_csi"].items()),
                    key=lambda kv: -kv[1],
                )[:3],
                "quantum_eta_ness_S_Ti_npv_opv": round(sobol_summary[c]["sobol_npv_opv"]["eta_ness_shift_pct"]["S_Ti"], 8),
            }
            for c in cfg["crops"]
        },
        "wall_time_s": round(time.perf_counter() - t0, 3),
    }
    with open(WP5_DIR / "wp5_validation_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary_payload, fh, indent=2)

    print(
        f"✅ WP5 complete in {summary_payload['wall_time_s']:.2f}s | "
        f"rows={len(tea_rows)} | Sobol N={n_sobol} | max_disp_err={max_dispatch_err_kwh:.2e} kWh"
    )


if __name__ == "__main__":
    main()
