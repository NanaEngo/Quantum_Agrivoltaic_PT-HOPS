#!/usr/bin/env python3
"""
WP3b: Structural & Operational Audit Beyond Fixed 2023 Single-Point Defaults.

Computes three rigorous physical/economic stress & counterfactual analyses using
the exact coupled WP3 FvCB-Medlyn-FAO56-LWIR engine and WP5 8760 h dispatch/DCF/LCA:
  1. Coupled 3x3 mechanistic (AWC x g_b) sweep over parameters.yaml SURROGATE_RANGE
     bounds: AWC in {120, 160, 220} mm x g_b in {0.6, 1.2, 2.5} mol m^-2 s^-1.
  2. Quantified seasonal monsoon-open louver counterfactual (S6_MonsoonOpen):
     June-October retracted open sky (GCR=0, tau=1) vs November-May active shade
     on S3 (ST-OPV APT44, GCR 0.65) and S2 (c-Si, GCR 0.40), with break-even
     actuation CAPEX headroom (USD m^-2 module) vs fixed arrays and S5 irrigation.
  3. Synthetic meteorological stress perturbations around the 2023 ERA5 baseline
     (warm-dry vs cool-cloudy) to bound inter-annual climatic sensitivity without
     extrapolating beyond available ERA5 data.

Outputs: data/wp3/wp3b_structural_and_louver_audit.json
"""

from __future__ import annotations

import copy
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PKG_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import wp3_microclimate_crop_engine as wp3
import wp5_tea_lca_sobol as wp5

DATA_WP2 = PKG_ROOT / "data" / "wp2"
DATA_WP3 = PKG_ROOT / "data" / "wp3"
DATA_WP5 = PKG_ROOT / "data" / "wp5"
OUT_PATH = DATA_WP3 / "wp3b_structural_and_louver_audit.json"


def _clearances_for_crop(crop_key: str, crop_cfg: dict, si_cfg: dict) -> tuple[float, float]:
    """Match exact engineered agronomic canopy clearances from wp3._crop_job_worker."""
    canopy_h = float(crop_cfg["canopy_height_m"])
    if crop_key == "highland_tea":
        return float(crop_cfg.get("mounting_clearance_m", 2.2)) - canopy_h, float(si_cfg["standard_mounting_height_m"]) - canopy_h
    if crop_key == "penja_white_pepper":
        return 1.5, 2.0
    return 1.4, 1.8


def _prepare_opv_apt44_context(
    cfg: dict[str, Any],
    pareto_designs: list[dict[str, Any]],
    tmm_lib: dict[str, Any],
    q_summary: dict[str, Any],
) -> dict[str, Any]:
    """Extract optical/PV parameters for the canonical S3_OPV_APT44_GCR65 module."""
    opv_cfg = cfg["opv_technology"]
    wl = np.asarray(tmm_lib["wavelength_nm"], dtype=np.float64)
    am15 = np.asarray(tmm_lib["am15_w_m2_nm"], dtype=np.float64)
    angles_grid = np.asarray(tmm_lib["incidence_angles_deg"], dtype=np.float64)
    par_mask = (wl >= 400.0) & (wl <= 700.0)
    epar_mask = (wl >= 400.0) & (wl <= 750.0)
    red_mask = (wl >= 655.0) & (wl <= 665.0)
    fr_mask = (wl >= 725.0) & (wl <= 735.0)
    trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))

    ph_am15 = am15 * wl
    am15_par_ph = float(trapz(ph_am15[par_mask], wl[par_mask]))
    am15_epar_ph = float(trapz(ph_am15[epar_mask], wl[epar_mask]))
    am15_red_ph = float(trapz(ph_am15[red_mask], wl[red_mask]))
    am15_fr_ph = float(trapz(ph_am15[fr_mask], wl[fr_mask]))
    am15_sw_tot = float(trapz(am15, wl))
    rfr_am15 = am15_red_ph / am15_fr_ph

    lib_apts = np.asarray(tmm_lib["design_apt_par"], dtype=np.float64)
    idx = int(np.argmin(np.abs(lib_apts - 0.44)))
    d_act = float(tmm_lib["design_d_act_nm"][idx])
    d_ag = float(tmm_lib["design_d_ag_nm"][idx])
    d_cap = float(tmm_lib["design_d_cap_nm"][idx])
    apt_val = float(lib_apts[idx])
    pce_val = float(tmm_lib["design_pce_pct"][idx])

    T_beam_ang = np.asarray(tmm_lib["T_beam"][idx], dtype=np.float64)
    T_diff_wl = np.asarray(tmm_lib["T_diff"][idx], dtype=np.float64)
    match_row = next(
        r for r in pareto_designs
        if abs(float(r["d_act_nm"]) - d_act) < 0.1
        and abs(float(r["d_ag_nm"]) - d_ag) < 0.1
        and abs(float(r["d_cap_nm"]) - d_cap) < 0.1
    )
    a_sw_opv = float(match_row["a_sw_300_1100"])

    eta_am15 = float(q_summary["hamiltonians"]["H2_Muh2010_diag_PDA"]["open_rc_no_npq"]["AM15G_full_sun"]["eta_partial_secular_mean"])
    tag_q = f"STOPV_APT_{apt_val * 100:.1f}pct_beam"
    if tag_q in q_summary["hamiltonians"]["H2_Muh2010_diag_PDA"]["open_rc_no_npq"]:
        eta_opv_ratio = float(q_summary["hamiltonians"]["H2_Muh2010_diag_PDA"]["open_rc_no_npq"][tag_q]["eta_partial_secular_mean"]) / eta_am15
    else:
        eta_opv_ratio = 1.000015

    return {
        "apt_val": apt_val,
        "pce_val": pce_val,
        "d_act": d_act,
        "d_ag": d_ag,
        "d_cap": d_cap,
        "a_sw_opv": a_sw_opv,
        "eta_opv_ratio": eta_opv_ratio,
        "beta_opv": float(opv_cfg["pce_temp_coeff_per_c"]),
        "eps_opv": float(opv_cfg["infrared_emissivity"]),
        "soil_opv_d": float(opv_cfg["soiling_derating_seasonal_range"][1]),
        "soil_opv_w": float(opv_cfg["soiling_derating_seasonal_range"][0]),
        "angles_grid": angles_grid,
        "rfr_am15": rfr_am15,
        "par_b_ang": np.array([trapz(T_beam_ang[a, par_mask] * ph_am15[par_mask], wl[par_mask]) / am15_par_ph for a in range(5)]),
        "epar_b_ang": np.array([trapz(T_beam_ang[a, epar_mask] * ph_am15[epar_mask], wl[epar_mask]) / am15_epar_ph for a in range(5)]),
        "sw_b_ang": np.array([trapz(T_beam_ang[a] * am15, wl) / am15_sw_tot for a in range(5)]),
        "red_b_ang": np.array([trapz(T_beam_ang[a, red_mask] * ph_am15[red_mask], wl[red_mask]) / am15_red_ph for a in range(5)]),
        "fr_b_ang": np.array([trapz(T_beam_ang[a, fr_mask] * ph_am15[fr_mask], wl[fr_mask]) / am15_fr_ph for a in range(5)]),
        "par_d": float(trapz(T_diff_wl[par_mask] * ph_am15[par_mask], wl[par_mask]) / am15_par_ph),
        "epar_d": float(trapz(T_diff_wl[epar_mask] * ph_am15[epar_mask], wl[epar_mask]) / am15_epar_ph),
        "sw_d": float(trapz(T_diff_wl * am15, wl) / am15_sw_tot),
        "red_d": float(trapz(T_diff_wl[red_mask] * ph_am15[red_mask], wl[red_mask]) / am15_red_ph),
        "fr_d": float(trapz(T_diff_wl[fr_mask] * ph_am15[fr_mask], wl[fr_mask]) / am15_fr_ph),
    }


def _opv_hourly_optics(climate: dict[str, np.ndarray], ctx: dict[str, Any], gcr: float) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute hourly tau_par, tau_sw, epar_over_par, r_fr_ratio for ST-OPV at given GCR."""
    zen = np.clip(climate["zenith_deg"], 0.0, 60.0)
    angles = ctx["angles_grid"]
    f_b, f_d = climate["f_beam"], climate["f_diff"]
    t_par_p = f_b * np.interp(zen, angles, ctx["par_b_ang"]) + f_d * ctx["par_d"]
    t_epar_p = f_b * np.interp(zen, angles, ctx["epar_b_ang"]) + f_d * ctx["epar_d"]
    t_sw_p = f_b * np.interp(zen, angles, ctx["sw_b_ang"]) + f_d * ctx["sw_d"]
    t_red_p = f_b * np.interp(zen, angles, ctx["red_b_ang"]) + f_d * ctx["red_d"]
    t_fr_p = f_b * np.interp(zen, angles, ctx["fr_b_ang"]) + f_d * ctx["fr_d"]

    tau_par = (1.0 - gcr) + gcr * t_par_p
    tau_epar = (1.0 - gcr) + gcr * t_epar_p
    tau_sw = (1.0 - gcr) + gcr * t_sw_p
    tau_red = (1.0 - gcr) + gcr * t_red_p
    tau_fr = (1.0 - gcr) + gcr * t_fr_p
    epar_over_par = tau_epar / np.maximum(tau_par, 1e-6)
    rfr_arr = ctx["rfr_am15"] * (tau_red / np.maximum(tau_fr, 1e-6))
    return tau_par, tau_sw, epar_over_par, rfr_arr


def _run_triplet_for_climate(
    crop_key: str,
    climate: dict[str, np.ndarray],
    cfg: dict[str, Any],
    micro_cfg: dict[str, Any],
    ctx: dict[str, Any],
    svf_bounds: tuple[float, float],
    gcr_opv: float = 0.65,
    gcr_si: float = 0.40,
    monsoon_open_months: list[int] | None = None,
) -> dict[str, Any]:
    """Run S0, S3 (OPV APT44 GCR65), and S2 (c-Si GCR40) consistently on given climate & micro_cfg."""
    crop_cfg = cfg["crops"][crop_key]
    si_cfg = cfg["si_counterfactual"]
    n_h = len(climate["T_air_c"])
    rfr_am15 = ctx["rfr_am15"]
    cl_opv, cl_si = _clearances_for_crop(crop_key, crop_cfg, si_cfg)
    baseline_kg = float(crop_cfg["baseline_clean_yield_kg_ha"])

    # S0 Open Control (rainfed)
    res_s0 = wp3.solve_coupled_microclimate_and_assimilation(
        climate=climate, crop_cfg=crop_cfg, micro_cfg=micro_cfg,
        tau_par=np.ones(n_h), tau_sw=np.ones(n_h), epar_over_par=np.ones(n_h),
        r_fr_ratio=np.full(n_h, rfr_am15), eta_ness_ratio=1.0,
        gcr=0.0, pce_pv_ref_pct=0.0, beta_pv_per_c=0.0, a_sw_panel=0.0, eps_pv=0.90,
        clearance_m=cl_opv, soiling_dry=0.0, soiling_wet=0.0, irrigated=False, svf_bounds=svf_bounds,
    )
    a_s0 = res_s0["A_net_annual_mol_m2"]
    et_s0 = res_s0["transp_mm_yr"]

    # OPV S3 (or S6 monsoon-open)
    tau_par_o, tau_sw_o, epar_o, rfr_o = _opv_hourly_optics(climate, ctx, gcr_opv)
    gcr_prof_o = None
    if monsoon_open_months:
        open_m = np.isin(climate["month"], monsoon_open_months)
        tau_par_o = np.where(open_m, 1.0, tau_par_o)
        tau_sw_o = np.where(open_m, 1.0, tau_sw_o)
        epar_o = np.where(open_m, 1.0, epar_o)
        rfr_o = np.where(open_m, rfr_am15, rfr_o)
        gcr_prof_o = np.where(open_m, 0.0, gcr_opv)

    res_opv = wp3.solve_coupled_microclimate_and_assimilation(
        climate=climate, crop_cfg=crop_cfg, micro_cfg=micro_cfg,
        tau_par=tau_par_o, tau_sw=tau_sw_o, epar_over_par=epar_o, r_fr_ratio=rfr_o,
        eta_ness_ratio=ctx["eta_opv_ratio"], gcr=gcr_opv, pce_pv_ref_pct=ctx["pce_val"],
        beta_pv_per_c=ctx["beta_opv"], a_sw_panel=ctx["a_sw_opv"], eps_pv=ctx["eps_opv"],
        clearance_m=cl_opv, soiling_dry=ctx["soil_opv_d"], soiling_wet=ctx["soil_opv_w"],
        irrigated=False, svf_bounds=svf_bounds, gcr_profile=gcr_prof_o,
    )

    # c-Si S2 (or S6 monsoon-open)
    pce_si = float(si_cfg["base_pce_percent"])
    beta_si = float(si_cfg["pce_temp_coeff_per_c"])
    eps_si = float(si_cfg["infrared_emissivity"])
    soil_si_d = float(si_cfg["soiling_derating_seasonal_range"][1])
    soil_si_w = float(si_cfg["soiling_derating_seasonal_range"][0])
    tau_geom = np.full(n_h, 1.0 - gcr_si)
    gcr_prof_s = None
    if monsoon_open_months:
        open_m = np.isin(climate["month"], monsoon_open_months)
        tau_geom = np.where(open_m, 1.0, tau_geom)
        gcr_prof_s = np.where(open_m, 0.0, gcr_si)

    res_si = wp3.solve_coupled_microclimate_and_assimilation(
        climate=climate, crop_cfg=crop_cfg, micro_cfg=micro_cfg,
        tau_par=tau_geom, tau_sw=tau_geom, epar_over_par=np.ones(n_h),
        r_fr_ratio=np.full(n_h, rfr_am15), eta_ness_ratio=1.0, gcr=gcr_si, pce_pv_ref_pct=pce_si,
        beta_pv_per_c=beta_si, a_sw_panel=0.90, eps_pv=eps_si,
        clearance_m=cl_si, soiling_dry=soil_si_d, soiling_wet=soil_si_w,
        irrigated=False, svf_bounds=svf_bounds, gcr_profile=gcr_prof_s,
    )

    def _pack(res: dict[str, Any]) -> dict[str, Any]:
        y_kg_ha = baseline_kg * (res["A_net_annual_mol_m2"] / a_s0)
        dy_pct = 100.0 * (res["A_net_annual_mol_m2"] - a_s0) / a_s0
        dy_wet_pct = 100.0 * (res["A_net_wet_mean"] - res_s0["A_net_wet_mean"]) / res_s0["A_net_wet_mean"]
        dy_dry_pct = 100.0 * (res["A_net_dry_mean"] - res_s0["A_net_dry_mean"]) / res_s0["A_net_dry_mean"]
        det_pct = 100.0 * (res["transp_mm_yr"] - et_s0) / et_s0
        return {
            "yield_kg_ha": float(y_kg_ha),
            "delta_y_total_pct": float(dy_pct),
            "delta_y_wet_pct": float(dy_wet_pct),
            "delta_y_dry_pct": float(dy_dry_pct),
            "delta_et_pct": float(det_pct),
            "pv_mwh_ha_yr": float(res["pv_mwh_ha_yr"]),
            "pv_gen_wm2": res["pv_gen_wm2"],
            "dt_leaf_dry_day_c": float(res["T_leaf_dry_day_mean_c"] - res_s0["T_leaf_dry_day_mean_c"]),
            "f_soil_dry_mean": float(res["f_soil_dry_mean"]),
        }

    opv_p = _pack(res_opv)
    si_p = _pack(res_si)
    return {
        "s0_A_annual_mol_m2": float(a_s0),
        "s0_et_mm_yr": float(et_s0),
        "s0_f_soil_dry_mean": float(res_s0["f_soil_dry_mean"]),
        "opv": opv_p,
        "csi": si_p,
        "opv_minus_csi_pp": float(opv_p["delta_y_total_pct"] - si_p["delta_y_total_pct"]),
    }


def _perturb_climate(climate: dict[str, np.ndarray], dt_c: float, drh_pp: float, precip_mult: float, ghi_mult: float, d_fdiff: float) -> dict[str, np.ndarray]:
    """Create a physically self-consistent synthetic meteorological stress perturbation around 2023 ERA5."""
    c_new = {k: v.copy() for k, v in climate.items()}
    c_new["T_air_c"] = climate["T_air_c"] + dt_c
    c_new["rh_pct"] = np.clip(climate["rh_pct"] + drh_pp, 15.0, 100.0)
    c_new["precip_mm"] = climate["precip_mm"] * precip_mult
    c_new["sw_ghi"] = climate["sw_ghi"] * ghi_mult
    e_s = wp3.sat_vapor_pressure_kpa(c_new["T_air_c"])
    c_new["vpd_air_kpa"] = np.maximum(0.02, e_s * (1.0 - c_new["rh_pct"] / 100.0))
    day = c_new["sw_ghi"] > 5.0
    f_diff_new = np.where(day, np.clip(climate["f_diff"] + d_fdiff, 0.05, 1.0), 1.0)
    c_new["f_diff"] = f_diff_new
    c_new["f_beam"] = 1.0 - f_diff_new
    return c_new


def _eval_tea_lca(
    technology: str,
    crop_key: str,
    gcr: float,
    yield_kg_ha: float,
    pv_mwh_ha_yr: float,
    pv_wm2: np.ndarray,
    irrigated: bool,
    cfg: dict[str, Any],
) -> dict[str, float]:
    """Evaluate exact WP5 8760 h dispatch + 20-year DCF TEA + Dual-FU LCA."""
    crop_cfg = cfg["crops"][crop_key]
    catchment = wp5.COOP_CATCHMENT_HA[crop_key]
    load_kw, _ = wp5.build_factory_load_profile(crop_key, crop_cfg, yield_kg_ha, catchment)
    bess_opt = "overnight_withering_bess" if crop_key == "highland_tea" else "small_lfp_buffer_2h"
    bess_kwh = wp5.size_bess_kwh(load_kw, float(crop_cfg["processing_daytime_load_fraction"]), bess_opt)
    disp = wp5.simulate_8760_dispatch(pv_wm2, load_kw, bess_kwh, float(cfg["economics"]["bess_roundtrip_efficiency"]))
    tea = wp5.evaluate_20yr_tea_lca(
        technology=technology, crop_name=crop_key, gcr=gcr,
        yield_kg_ha=yield_kg_ha, pv_kwh_yr_base=pv_mwh_ha_yr * 1000.0,
        dispatch_yr1=disp, bess_cap_kwh=bess_kwh, irrigated=irrigated, cfg=cfg,
    )
    return {
        "npv_usd_ha": float(tea["npv_usd_ha"]),
        "irr_pct": float(tea["irr_pct"]),
        "lcoe_usd_kwh": float(tea["lcoe_usd_kwh"]),
        "lca_pv_intensity_gco2e_kwh": float(tea["lca_pv_intensity_gco2e_kwh"]),
        "lca_net_area_kgco2e_ha_yr": float(tea["lca_net_area_kgco2e_ha_yr"]),
        "load_solar_fraction_pct": float(disp["load_solar_fraction_pct"]),
        "bess_kwh": float(bess_kwh),
    }


def main() -> None:
    t0 = time.perf_counter()
    cfg = wp3.load_config()
    with open(DATA_WP2 / "tmm_pareto_opv.csv", "r", encoding="utf-8") as f:
        pareto_designs = list(csv.DictReader(f))
    tmm_lib = dict(np.load(DATA_WP2 / "tmm_spectral_library.npz"))
    q_summary = json.loads((DATA_WP2 / "quantum_ness_summary.json").read_text(encoding="utf-8"))
    summary_wp1 = json.loads((PKG_ROOT / "data" / "wp1" / "climate_summary_2023.json").read_text(encoding="utf-8"))
    baseline_wp3_rows = wp5.load_wp3_scenarios(DATA_WP3 / "wp3_crop_microclimate_scenarios.csv")
    with open(DATA_WP5 / "wp5_tea_lca_scenarios.csv", "r", encoding="utf-8") as f:
        baseline_wp5_rows = list(csv.DictReader(f))

    ctx = _prepare_opv_apt44_context(cfg, pareto_designs, tmm_lib, q_summary)
    micro_base = copy.deepcopy(cfg["microclimate"])
    svf_bounds = tuple(float(x) for x in cfg["optical_radiative_model"]["panel_sky_view_factor_range"])
    awc_grid = [120.0, 160.0, 220.0]
    gb_grid = [0.6, 1.2, 2.5]
    crops = list(cfg["crops"].keys())
    horizon = int(cfg["economics"]["analysis_period_years"])
    wacc = float(cfg["economics"]["discount_rate_wacc"])
    pv_om_annuity = sum(1.0 / ((1.0 + wacc) ** y) for y in range(1, horizon + 1))

    # Load verified 8760h climate per crop (exact lat matching wp3_microclimate_crop_engine.py)
    climates: dict[str, dict[str, np.ndarray]] = {}
    for ck in crops:
        ccfg = cfg["crops"][ck]
        lat = float(ccfg.get("latitude", 5.2))
        for sk, sv in summary_wp1.items():
            if isinstance(sv, dict) and (sk.split("_")[-1] in ck or ck.split("_")[-1] in sk):
                lat = float(sv["latitude"])
                break
        climates[ck] = wp3.load_site_climate(PKG_ROOT / ccfg["climate_dataset"], lat)

    # 1. Coupled 3x3 (AWC x g_b) sweep
    awc_gb_sweep: dict[str, Any] = {}
    for ck in crops:
        grid_rows: list[dict[str, float]] = []
        base_wp3_opv = next(r for r in baseline_wp3_rows if r["crop"] == ck and r["scenario_id"] == "S3_OPV_APT44_GCR65")
        base_wp3_csi = next(r for r in baseline_wp3_rows if r["crop"] == ck and r["scenario_id"] == "S2_cSi_GCR40")
        for awc in awc_grid:
            for gb in gb_grid:
                mc = copy.deepcopy(micro_base)
                mc["rainfed_soil_awc_mm"] = awc
                mc["boundary_layer_conductance_mol_m2_s"] = gb
                res = _run_triplet_for_climate(ck, climates[ck], cfg, mc, ctx, svf_bounds)
                row = {
                    "awc_mm": awc,
                    "gb_mol_m2_s": gb,
                    "opv_delta_y_pct": res["opv"]["delta_y_total_pct"],
                    "csi_delta_y_pct": res["csi"]["delta_y_total_pct"],
                    "opv_minus_csi_pp": res["opv_minus_csi_pp"],
                    "opv_yield_kg_ha": res["opv"]["yield_kg_ha"],
                    "csi_yield_kg_ha": res["csi"]["yield_kg_ha"],
                    "opv_delta_et_pct": res["opv"]["delta_et_pct"],
                    "csi_delta_et_pct": res["csi"]["delta_et_pct"],
                    "s0_f_soil_dry_mean": res["s0_f_soil_dry_mean"],
                }
                if abs(awc - 160.0) < 1e-6 and abs(gb - 1.2) < 1e-6:
                    row["baseline_verify_opv_abs_err_pp"] = abs(res["opv"]["delta_y_total_pct"] - float(base_wp3_opv["delta_y_total_pct"]))
                    row["baseline_verify_csi_abs_err_pp"] = abs(res["csi"]["delta_y_total_pct"] - float(base_wp3_csi["delta_y_total_pct"]))
                grid_rows.append(row)

        opv_dys = [r["opv_delta_y_pct"] for r in grid_rows]
        csi_dys = [r["csi_delta_y_pct"] for r in grid_rows]
        gaps = [r["opv_minus_csi_pp"] for r in grid_rows]
        center = next(r for r in grid_rows if abs(r["awc_mm"] - 160.0) < 1e-6 and abs(r["gb_mol_m2_s"] - 1.2) < 1e-6)
        awc_gb_sweep[ck] = {
            "center_awc160_gb1_2": center,
            "opv_delta_y_min_pct": min(opv_dys),
            "opv_delta_y_max_pct": max(opv_dys),
            "csi_delta_y_min_pct": min(csi_dys),
            "csi_delta_y_max_pct": max(csi_dys),
            "opv_minus_csi_min_pp": min(gaps),
            "opv_minus_csi_max_pp": max(gaps),
            "grid": grid_rows,
        }

    # 2. Seasonal Monsoon-Open Louver Counterfactual (S6_MonsoonOpen: June-October open sky)
    monsoon_months = [6, 7, 8, 9, 10]
    monsoon_louver: dict[str, Any] = {}
    for ck in crops:
        fixed_phys = _run_triplet_for_climate(ck, climates[ck], cfg, micro_base, ctx, svf_bounds, monsoon_open_months=None)
        open_phys = _run_triplet_for_climate(ck, climates[ck], cfg, micro_base, ctx, svf_bounds, monsoon_open_months=monsoon_months)

        fixed_opv_tea = _eval_tea_lca("ST_OPV_PM6Y6", ck, 0.65, fixed_phys["opv"]["yield_kg_ha"], fixed_phys["opv"]["pv_mwh_ha_yr"], fixed_phys["opv"]["pv_gen_wm2"], False, cfg)
        open_opv_tea = _eval_tea_lca("ST_OPV_PM6Y6", ck, 0.65, open_phys["opv"]["yield_kg_ha"], open_phys["opv"]["pv_mwh_ha_yr"], open_phys["opv"]["pv_gen_wm2"], False, cfg)

        fixed_csi_tea = _eval_tea_lca("cSi_Opaque_AV", ck, 0.40, fixed_phys["csi"]["yield_kg_ha"], fixed_phys["csi"]["pv_mwh_ha_yr"], fixed_phys["csi"]["pv_gen_wm2"], False, cfg)
        open_csi_tea = _eval_tea_lca("cSi_Opaque_AV", ck, 0.40, open_phys["csi"]["yield_kg_ha"], open_phys["csi"]["pv_mwh_ha_yr"], open_phys["csi"]["pv_gen_wm2"], False, cfg)

        # Cross-check vs canonical baseline WP5 summary
        bess_opt_expected = "overnight_withering_bess" if ck == "highland_tea" else "small_lfp_buffer_2h"
        ref_wp5_opv = next(r for r in baseline_wp5_rows if r["crop"] == ck and r["scenario_id"] == "S3_OPV_APT44_GCR65" and r["bess_option"] == bess_opt_expected)
        ref_wp5_csi = next(r for r in baseline_wp5_rows if r["crop"] == ck and r["scenario_id"] == "S2_cSi_GCR40" and r["bess_option"] == bess_opt_expected)
        s5_opv_wp5 = next(r for r in baseline_wp5_rows if r["crop"] == ck and r["scenario_id"] == "S5_OPV_APT44_GCR65_Irrig" and r["bess_option"] == bess_opt_expected)
        s5_csi_wp5 = next(r for r in baseline_wp5_rows if r["crop"] == ck and r["scenario_id"] == "S5_cSi_GCR40_Irrig" and r["bess_option"] == bess_opt_expected)
        s5_opv_wp3 = next(r for r in baseline_wp3_rows if r["crop"] == ck and r["scenario_id"] == "S5_OPV_APT44_GCR65_Irrig")

        def _pack_louver(name: str, gcr: float, fx_p: dict[str, Any], op_p: dict[str, Any], fx_t: dict[str, float], op_t: dict[str, float], ref_wp5: dict[str, Any], s5_wp5: dict[str, Any]) -> dict[str, Any]:
            d_npv = op_t["npv_usd_ha"] - fx_t["npv_usd_ha"]
            area_m2 = 10000.0 * gcr
            # Break-even upfront louver CAPEX per m^2 module: (a) raw NPV gain / m^2, (b) inclusive of 1.5%/yr O&M annuity
            be_capex_raw = max(0.0, d_npv / area_m2)
            be_capex_om = max(0.0, d_npv / (area_m2 * (1.0 + wp5.PV_OM_FRAC_OF_CAPEX * pv_om_annuity)))
            return {
                "gcr": gcr,
                "fixed_delta_y_pct": fx_p["delta_y_total_pct"],
                "fixed_delta_y_wet_pct": fx_p["delta_y_wet_pct"],
                "fixed_pv_mwh_ha_yr": fx_p["pv_mwh_ha_yr"],
                "fixed_npv_usd_ha": fx_t["npv_usd_ha"],
                "fixed_lcoe_usd_kwh": fx_t["lcoe_usd_kwh"],
                "fixed_lca_gco2e_kwh": fx_t["lca_pv_intensity_gco2e_kwh"],
                "baseline_wp5_npv_abs_err_usd_ha": abs(fx_t["npv_usd_ha"] - float(ref_wp5["npv_usd_ha"])),
                "open_delta_y_pct": op_p["delta_y_total_pct"],
                "open_delta_y_wet_pct": op_p["delta_y_wet_pct"],
                "open_pv_mwh_ha_yr": op_p["pv_mwh_ha_yr"],
                "open_npv_usd_ha": op_t["npv_usd_ha"],
                "open_irr_pct": op_t["irr_pct"],
                "open_lcoe_usd_kwh": op_t["lcoe_usd_kwh"],
                "open_lca_gco2e_kwh": op_t["lca_pv_intensity_gco2e_kwh"],
                "open_load_solar_fraction_pct": op_t["load_solar_fraction_pct"],
                "delta_y_rescue_pp": op_p["delta_y_total_pct"] - fx_p["delta_y_total_pct"],
                "delta_pv_mwh_ha_yr": op_p["pv_mwh_ha_yr"] - fx_p["pv_mwh_ha_yr"],
                "delta_pv_pct": 100.0 * (op_p["pv_mwh_ha_yr"] - fx_p["pv_mwh_ha_yr"]) / fx_p["pv_mwh_ha_yr"],
                "delta_npv_vs_fixed_usd_ha": d_npv,
                "break_even_actuation_capex_raw_usd_m2": be_capex_raw,
                "break_even_actuation_capex_incl_om_usd_m2": be_capex_om,
                "s5_irrigated_npv_usd_ha": float(s5_wp5["npv_usd_ha"]),
                "open_minus_s5_npv_usd_ha": op_t["npv_usd_ha"] - float(s5_wp5["npv_usd_ha"]),
            }

        monsoon_louver[ck] = {
            "s5_opv_delta_y_pct": float(s5_opv_wp3["delta_y_total_pct"]),
            "s6_opv_apt44_gcr65": _pack_louver(
                "S6_OPV_APT44_GCR65_MonsoonOpen", 0.65,
                fixed_phys["opv"], open_phys["opv"], fixed_opv_tea, open_opv_tea, ref_wp5_opv, s5_opv_wp5
            ),
            "s6_csi_gcr40": _pack_louver(
                "S6_cSi_GCR40_MonsoonOpen", 0.40,
                fixed_phys["csi"], open_phys["csi"], fixed_csi_tea, open_csi_tea, ref_wp5_csi, s5_csi_wp5
            ),
        }

    # 3. Synthetic Meteorological Stress Envelope around verified 2023 ERA5
    stress_defs = {
        "baseline_2023_era5": {"dt_c": 0.0, "drh_pp": 0.0, "precip_mult": 1.0, "ghi_mult": 1.0, "d_fdiff": 0.0},
        "warm_dry_stress": {"dt_c": +1.5, "drh_pp": -5.0, "precip_mult": 0.75, "ghi_mult": 1.05, "d_fdiff": -0.05},
        "cool_cloudy_stress": {"dt_c": -1.0, "drh_pp": +5.0, "precip_mult": 1.25, "ghi_mult": 0.90, "d_fdiff": +0.08},
    }
    climate_stress: dict[str, Any] = {}
    for ck in crops:
        crop_stress: dict[str, Any] = {}
        for s_tag, p in stress_defs.items():
            c_pert = climates[ck] if s_tag == "baseline_2023_era5" else _perturb_climate(
                climates[ck], p["dt_c"], p["drh_pp"], p["precip_mult"], p["ghi_mult"], p["d_fdiff"]
            )
            res = _run_triplet_for_climate(ck, c_pert, cfg, micro_base, ctx, svf_bounds)
            crop_stress[s_tag] = {
                "opv_delta_y_pct": res["opv"]["delta_y_total_pct"],
                "csi_delta_y_pct": res["csi"]["delta_y_total_pct"],
                "opv_minus_csi_pp": res["opv_minus_csi_pp"],
                "opv_pv_mwh_ha_yr": res["opv"]["pv_mwh_ha_yr"],
                "csi_pv_mwh_ha_yr": res["csi"]["pv_mwh_ha_yr"],
                "opv_delta_et_pct": res["opv"]["delta_et_pct"],
                "s0_f_soil_dry_mean": res["s0_f_soil_dry_mean"],
                "opv_f_soil_dry_mean": res["opv"]["f_soil_dry_mean"],
            }
        climate_stress[ck] = crop_stress

    payload = {
        "metadata": {
            "description": "WP3b coupled structural (AWC x g_b), monsoon-open louver counterfactual, and 2023 synthetic climate stress audit.",
            "awc_grid_mm": awc_grid,
            "gb_grid_mol_m2_s": gb_grid,
            "monsoon_open_months": monsoon_months,
            "climate_stress_perturbations": stress_defs,
            "runtime_sec": round(time.perf_counter() - t0, 3),
        },
        "awc_gb_sweep": awc_gb_sweep,
        "monsoon_louver_counterfactual": monsoon_louver,
        "synthetic_climate_stress": climate_stress,
    }
    OUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("=== WP3b AUDIT SUMMARY ===")
    for ck in crops:
        ag = awc_gb_sweep[ck]
        print(
            f"[AWC x g_b] {ck}: OPV dY [{ag['opv_delta_y_min_pct']:+.2f}, {ag['opv_delta_y_max_pct']:+.2f}]% | "
            f"c-Si dY [{ag['csi_delta_y_min_pct']:+.2f}, {ag['csi_delta_y_max_pct']:+.2f}]% | "
            f"OPV-cSi [{ag['opv_minus_csi_min_pp']:+.2f}, {ag['opv_minus_csi_max_pp']:+.2f}] pp "
            f"(center err: {ag['center_awc160_gb1_2']['baseline_verify_opv_abs_err_pp']:.2e})"
        )
        ml = monsoon_louver[ck]
        for k in ("s6_opv_apt44_gcr65", "s6_csi_gcr40"):
            d = ml[k]
            print(
                f"[LOUVER] {ck} {k}: dY {d['fixed_delta_y_pct']:+.2f}% -> {d['open_delta_y_pct']:+.2f}% "
                f"(+{d['delta_y_rescue_pp']:.2f} pp) | PV {d['fixed_pv_mwh_ha_yr']:.1f} -> {d['open_pv_mwh_ha_yr']:.1f} MWh/ha/yr "
                f"({d['delta_pv_pct']:+.1f}%) | dNPV ${d['delta_npv_vs_fixed_usd_ha']:+,.0f}/ha | "
                f"max actuation ${d['break_even_actuation_capex_incl_om_usd_m2']:.2f}/m2 | "
                f"vs S5 ${d['open_minus_s5_npv_usd_ha']:+,.0f}/ha"
            )
        cs = climate_stress[ck]
        print(
            f"[STRESS] {ck}: warm-dry OPV {cs['warm_dry_stress']['opv_delta_y_pct']:+.2f}% (gap {cs['warm_dry_stress']['opv_minus_csi_pp']:+.2f} pp) | "
            f"base {cs['baseline_2023_era5']['opv_delta_y_pct']:+.2f}% | "
            f"cool-cloudy {cs['cool_cloudy_stress']['opv_delta_y_pct']:+.2f}% (gap {cs['cool_cloudy_stress']['opv_minus_csi_pp']:+.2f} pp)"
        )
    print(f"Wrote {OUT_PATH} in {payload['metadata']['runtime_sec']:.2f}s")


if __name__ == "__main__":
    main()
