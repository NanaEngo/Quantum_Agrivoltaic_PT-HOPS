#!/usr/bin/env python3
"""
Compute verified refinement counterfactuals & sensitivities from canonical WP1-WP5 data:
  1. Exact energy-matched c-Si counterfactual (GCR_EM ~ 32-33%) + S2_cSi_GCR30 selected BESS.
  2. Load-matched off-grid array sizing (fraction alpha of 1 ha supplying captive load).
  3. Parametric ground-mounted PV-only counterfactual (GCR 0.70, zero crop revenue).
  4. Bounded photomorphogenic R:FR sensitivity on focal ST-OPV APT44.
  5. Exact split of Shapley phi_{spec+Q} into pure spectral phi_spec vs quantum phi_Q.
  6. kW-scaled inverter/interconnection sensitivity on Delta NPV (ST-OPV vs c-Si).

Writes: data/wp5/wp5_refinement_extensions_20261114.json
"""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from scipy.optimize import brentq

import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PKG_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import wp3_microclimate_crop_engine as wp3
import wp5_tea_lca_sobol as wp5

DATA_DIR = PKG_ROOT / "data"
OUT_JSON = DATA_DIR / "wp5" / "wp5_refinement_extensions_20261114.json"

CROPS = ("arabica_coffee", "penja_white_pepper", "highland_tea")


def _load_climate_for_crop(cfg: dict[str, Any], crop_key: str) -> dict[str, np.ndarray]:
    crop_cfg = cfg["crops"][crop_key]
    micro_cfg = cfg["microclimate"]
    csum = json.loads(
        wp3.resolve_config_path(PKG_ROOT, micro_cfg["climate_summary_dataset"]).read_text(encoding="utf-8")
    )
    lat = float(crop_cfg.get("latitude", 5.2))
    for sk, sv in csum.items():
        if sk.split("_")[-1] in crop_key or crop_key.split("_")[-1] in sk:
            lat = float(sv["latitude"])
            break
    return wp3.load_site_climate(wp3.resolve_config_path(PKG_ROOT, crop_cfg["climate_dataset"]), lat)


def _clearance_for_csi(crop_key: str, crop_cfg: dict[str, Any], si_cfg: dict[str, Any]) -> float:
    canopy_h = float(crop_cfg["canopy_height_m"])
    if crop_key == "highland_tea":
        return float(si_cfg["standard_mounting_height_m"]) - canopy_h
    if crop_key == "penja_white_pepper":
        return 2.0
    return 1.8


def _clearance_for_opv(crop_key: str, crop_cfg: dict[str, Any]) -> float:
    canopy_h = float(crop_cfg["canopy_height_m"])
    if crop_key == "highland_tea":
        return float(crop_cfg.get("mounting_clearance_m", 2.2)) - canopy_h
    if crop_key == "penja_white_pepper":
        return 1.5
    return 1.4


def _bess_for_crop(crop_key: str) -> str:
    return "overnight_withering_bess" if crop_key == "highland_tea" else "small_lfp_buffer_2h"


def main() -> None:
    cfg = yaml.safe_load((PKG_ROOT / "parameters.yaml").read_text(encoding="utf-8"))
    wp3_rows = wp5.load_wp3_scenarios(DATA_DIR / "wp3" / "wp3_crop_microclimate_scenarios.csv")
    by_wp3 = {(r["crop"], r["scenario_id"]): r for r in wp3_rows}

    tmm_npz = np.load(DATA_DIR / "wp2" / "tmm_spectral_library.npz")
    q_summary = json.loads((DATA_DIR / "wp2" / "quantum_ness_summary.json").read_text(encoding="utf-8"))

    # Max c-Si PV reference at GCR=0.70 (LER denominator)
    e_pv_ref = {
        c: float(by_wp3[(c, "S2_cSi_GCR70")]["pv_mwh_ha_yr"])
        for c in CROPS
    }

    si_cfg = cfg["si_counterfactual"]
    opv_cfg = cfg["opv_technology"]
    micro_cfg = cfg["microclimate"]
    opt_cfg = cfg["optical_radiative_model"]
    svf_bounds = tuple(float(x) for x in opt_cfg["panel_sky_view_factor_range"])
    rte = float(cfg["economics"]["bess_roundtrip_efficiency"])

    pce_si = float(si_cfg["base_pce_percent"])
    beta_si = float(si_cfg["pce_temp_coeff_per_c"])
    eps_si = float(si_cfg["infrared_emissivity"])
    soil_si_d = float(si_cfg["soiling_derating_seasonal_range"][1])
    soil_si_w = float(si_cfg["soiling_derating_seasonal_range"][0])

    # Load AM15 & APT44 spectrum once for Shapley split + R:FR sensitivity
    wl = np.asarray(tmm_npz["wavelength_nm"], dtype=np.float64)
    am15 = np.asarray(tmm_npz["am15_w_m2_nm"], dtype=np.float64)
    angles_grid = np.asarray(tmm_npz["incidence_angles_deg"], dtype=np.float64)
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
    epar_par_am15 = am15_epar_ph / am15_par_ph

    lib_apts = np.asarray(tmm_npz["design_apt_par"], dtype=np.float64)
    idx_44 = int(np.argmin(np.abs(lib_apts - 0.44)))
    apt_44 = float(lib_apts[idx_44])
    pce_44 = float(tmm_npz["design_pce_pct"][idx_44])
    T_beam_44 = np.asarray(tmm_npz["T_beam"][idx_44], dtype=np.float64)
    T_diff_44 = np.asarray(tmm_npz["T_diff"][idx_44], dtype=np.float64)

    pareto_csv = DATA_DIR / "wp2" / "tmm_pareto_opv.csv"
    import csv as _csv
    with open(pareto_csv, "r", encoding="utf-8") as fh:
        pareto_rows = [r for r in _csv.DictReader(fh) if int(float(r["is_pareto_all"])) == 1]
    d_act_44 = float(tmm_npz["design_d_act_nm"][idx_44])
    d_ag_44 = float(tmm_npz["design_d_ag_nm"][idx_44])
    d_cap_44 = float(tmm_npz["design_d_cap_nm"][idx_44])
    match_44 = next(
        r for r in pareto_rows
        if abs(float(r["d_act_nm"]) - d_act_44) < 0.1
        and abs(float(r["d_ag_nm"]) - d_ag_44) < 0.1
        and abs(float(r["d_cap_nm"]) - d_cap_44) < 0.1
    )
    a_sw_44 = float(match_44["a_sw_300_1100"])
    eta_am15 = float(q_summary["hamiltonians"]["H2_Muh2010_diag_PDA"]["open_rc_no_npq"]["AM15G_full_sun"]["eta_partial_secular_mean"])
    eta_opv_44 = float(q_summary["hamiltonians"]["H2_Muh2010_diag_PDA"]["open_rc_no_npq"][f"STOPV_APT_{apt_44*100:.1f}pct_beam"]["eta_partial_secular_mean"]) / eta_am15

    results: dict[str, Any] = {
        "energy_matched_csi": {},
        "s2_csi_gcr30_selected_bess": {},
        "load_matched_offgrid": {},
        "ground_mounted_pv_only": {},
        "spectral_rfr_sensitivity": {},
        "shapley_split_spec_vs_q": {},
        "inverter_kw_sensitivity": {},
        "multiyear_decade_2014_2023": {},
    }

    for crop_key in CROPS:
        crop_cfg = cfg["crops"][crop_key]
        climate = _load_climate_for_crop(cfg, crop_key)
        n_h = len(climate["T_air_c"])
        baseline_kg = float(crop_cfg["baseline_clean_yield_kg_ha"])
        catchment = wp5.COOP_CATCHMENT_HA[crop_key]
        bess_opt = _bess_for_crop(crop_key)
        day_frac = float(crop_cfg["processing_daytime_load_fraction"])
        cl_si = _clearance_for_csi(crop_key, crop_cfg, si_cfg)
        cl_opv = _clearance_for_opv(crop_key, crop_cfg)
        npz_hourly = np.load(DATA_DIR / "wp3" / f"hourly_{crop_key}.npz")

        row_opv44 = by_wp3[(crop_key, "S3_OPV_APT44_GCR65")]
        row_csi40 = by_wp3[(crop_key, "S2_cSi_GCR40")]
        row_csi30 = by_wp3[(crop_key, "S2_cSi_GCR30")]
        row_csi70 = by_wp3[(crop_key, "S2_cSi_GCR70")]
        row_s0 = by_wp3[(crop_key, "S0_open_control")]

        # Reference open control & OPV44 in WP3
        res_s0 = wp3.solve_coupled_microclimate_and_assimilation(
            climate=climate, crop_cfg=crop_cfg, micro_cfg=micro_cfg,
            tau_par=np.ones(n_h), tau_sw=np.ones(n_h), epar_over_par=np.ones(n_h),
            r_fr_ratio=np.full(n_h, rfr_am15), eta_ness_ratio=1.0, gcr=0.0,
            pce_pv_ref_pct=0.0, beta_pv_per_c=0.0, a_sw_panel=0.0, eps_pv=0.90,
            clearance_m=cl_opv, soiling_dry=0.0, soiling_wet=0.0, irrigated=False,
            svf_bounds=svf_bounds,
        )
        a_s0 = res_s0["A_net_annual_mol_m2"]

        # ------------------------------------------------------------------
        # 1. Exact Energy-Matched c-Si (matching S3_OPV_APT44_GCR65 MWh/ha/yr)
        # ------------------------------------------------------------------
        target_pv_mwh = float(row_opv44["pv_mwh_ha_yr"])

        def _csi_run_at_gcr(g: float) -> dict[str, Any]:
            t_geom = np.full(n_h, 1.0 - g)
            return wp3.solve_coupled_microclimate_and_assimilation(
                climate=climate, crop_cfg=crop_cfg, micro_cfg=micro_cfg,
                tau_par=t_geom, tau_sw=t_geom, epar_over_par=np.ones(n_h),
                r_fr_ratio=np.full(n_h, rfr_am15), eta_ness_ratio=1.0, gcr=g,
                pce_pv_ref_pct=pce_si, beta_pv_per_c=beta_si, a_sw_panel=0.90, eps_pv=eps_si,
                clearance_m=cl_si, soiling_dry=soil_si_d, soiling_wet=soil_si_w,
                irrigated=False, svf_bounds=svf_bounds,
            )

        gcr_em = float(brentq(lambda g: _csi_run_at_gcr(g)["pv_mwh_ha_yr"] - target_pv_mwh, 0.25, 0.45, xtol=1e-6))
        res_em = _csi_run_at_gcr(gcr_em)
        yield_em_kg = baseline_kg * (res_em["A_net_annual_mol_m2"] / a_s0)
        dy_em_pct = 100.0 * (res_em["A_net_annual_mol_m2"] - a_s0) / a_s0
        ler_em = (yield_em_kg / baseline_kg) + (res_em["pv_mwh_ha_yr"] / e_pv_ref[crop_key])
        load_em, _ = wp5.build_factory_load_profile(crop_key, crop_cfg, yield_em_kg, catchment)
        bess_em = wp5.size_bess_kwh(load_em, day_frac, bess_opt)
        disp_em = wp5.simulate_8760_dispatch(res_em["pv_gen_wm2"], load_em, bess_em, rte, allow_grid_export=True)
        tea_em = wp5.evaluate_20yr_tea_lca(
            "cSi_Opaque_AV", crop_key, gcr_em, yield_em_kg,
            res_em["pv_mwh_ha_yr"] * 1000.0, disp_em, bess_em, False, cfg,
        )
        results["energy_matched_csi"][crop_key] = {
            "gcr_em": gcr_em,
            "effective_shade_pct": gcr_em * 100.0,
            "target_opv_pv_mwh_ha_yr": target_pv_mwh,
            "csi_em_pv_mwh_ha_yr": res_em["pv_mwh_ha_yr"],
            "delta_y_annual_pct": dy_em_pct,
            "yield_kg_ha": yield_em_kg,
            "ler": ler_em,
            "npv_usd_ha": tea_em["npv_usd_ha"],
            "irr_pct": tea_em["irr_pct"],
            "dpbp_yr": tea_em["dpbp_yr"],
            "lcoe_usd_kwh": tea_em["lcoe_usd_kwh"],
            "lca_pv_intensity_gco2e_kwh": tea_em["lca_pv_intensity_gco2e_kwh"],
        }

        # Complete S2_cSi_GCR30 selected BESS (reference anchor already in WP3)
        pv30_wm2 = wp5.resolve_pv_wm2(npz_hourly, row_csi30)
        load30, _ = wp5.build_factory_load_profile(crop_key, crop_cfg, float(row_csi30["yield_kg_ha"]), catchment)
        bess30 = wp5.size_bess_kwh(load30, day_frac, bess_opt)
        disp30 = wp5.simulate_8760_dispatch(pv30_wm2, load30, bess30, rte, allow_grid_export=True)
        tea30 = wp5.evaluate_20yr_tea_lca(
            "cSi_Opaque_AV", crop_key, 0.30, float(row_csi30["yield_kg_ha"]),
            float(row_csi30["pv_mwh_ha_yr"]) * 1000.0, disp30, bess30, False, cfg,
        )
        results["s2_csi_gcr30_selected_bess"][crop_key] = {
            "pv_mwh_ha_yr": float(row_csi30["pv_mwh_ha_yr"]),
            "delta_y_annual_pct": float(row_csi30["delta_y_total_pct"]),
            "ler": (float(row_csi30["yield_kg_ha"]) / baseline_kg) + (float(row_csi30["pv_mwh_ha_yr"]) / e_pv_ref[crop_key]),
            "npv_usd_ha": tea30["npv_usd_ha"],
            "lcoe_usd_kwh": tea30["lcoe_usd_kwh"],
            "lca_pv_intensity_gco2e_kwh": tea30["lca_pv_intensity_gco2e_kwh"],
        }

        # ------------------------------------------------------------------
        # 2. Load-Matched Off-Grid Sizing (ST-OPV APT44, allow_grid_export=False)
        # Keep cooperative load fixed & resize installed PV footprint alpha in (0, 1]
        # on the 1-ha parcel (remaining 1-alpha ha stays open-sun S0; avoided tutor scales with alpha).
        # ------------------------------------------------------------------
        pv_opv_wm2 = wp5.resolve_pv_wm2(npz_hourly, row_opv44)
        pv_csi_wm2 = wp5.resolve_pv_wm2(npz_hourly, row_csi40)
        load_opv_full, annual_load_kwh = wp5.build_factory_load_profile(crop_key, crop_cfg, float(row_opv44["yield_kg_ha"]), catchment)
        bess_load = wp5.size_bess_kwh(load_opv_full, day_frac, bess_opt)

        # Open-control baseline NPV for parcel comparison
        tea_s0 = wp5.evaluate_20yr_tea_lca(
            "Open_Field", crop_key, 0.0, baseline_kg, 0.0,
            {"e_load_kwh": annual_load_kwh, "e_self_consumed_kwh": 0.0, "e_export_kwh": 0.0, "e_curtail_kwh": 0.0, "e_bess_loss_kwh": 0.0},
            0.0, False, cfg,
        )

        best_offgrid_opv = None
        for alpha in np.linspace(0.03, 1.00, 98):
            y_mix = (1.0 - alpha) * baseline_kg + alpha * float(row_opv44["yield_kg_ha"])
            load_mix, _ = wp5.build_factory_load_profile(crop_key, crop_cfg, y_mix, catchment)
            bess_mix = wp5.size_bess_kwh(load_mix, day_frac, bess_opt)
            pv_scaled_wm2 = alpha * pv_opv_wm2
            disp_og = wp5.simulate_8760_dispatch(pv_scaled_wm2, load_mix, bess_mix, rte, allow_grid_export=False)
            # Effective GCR over 1-ha parcel is 0.65 * alpha (so CAPEX scales with alpha)
            # Note: tutor saving applies to shaded alpha ha; subtract (1-alpha)*tutor cleanly
            tea_og = wp5.evaluate_20yr_tea_lca(
                "ST_OPV_PM6Y6", crop_key, 0.65 * float(alpha), y_mix,
                float(row_opv44["pv_mwh_ha_yr"]) * float(alpha) * 1000.0,
                disp_og, bess_mix, False, cfg, allow_grid_export=False,
            )
            # Correct tutor saving on un-shaded (1-alpha) fraction if pepper
            if crop_key == "penja_white_pepper":
                ann_tutor = float(cfg["economics"]["avoided_pepper_living_tutor_cost_usd_ha_yr"])
                wacc = float(cfg["economics"]["discount_rate_wacc"])
                pv_factor = sum(1.0 / ((1.0 + wacc) ** t) for t in range(1, 21))
                tea_og["npv_usd_ha"] -= (1.0 - float(alpha)) * ann_tutor * pv_factor
            cand = {
                "alpha_ha": float(alpha),
                "module_area_m2": 6500.0 * float(alpha),
                "npv_usd_ha": float(tea_og["npv_usd_ha"]),
                "delta_npv_vs_s0_usd_ha": float(tea_og["npv_usd_ha"] - tea_s0["npv_usd_ha"]),
                "lsf_pct": float(disp_og["load_solar_fraction_pct"]),
                "self_consumption_pct": float(disp_og["self_consumption_pct"]),
                "lcoe_usd_kwh": float(tea_og["lcoe_usd_kwh"]),
                "pv_gen_mwh_yr": float(row_opv44["pv_mwh_ha_yr"]) * float(alpha),
            }
            if best_offgrid_opv is None or cand["npv_usd_ha"] > best_offgrid_opv["npv_usd_ha"]:
                best_offgrid_opv = cand

        results["load_matched_offgrid"][crop_key] = {
            "s0_baseline_npv_usd_ha": float(tea_s0["npv_usd_ha"]),
            "allocated_coop_load_mwh_yr": annual_load_kwh / 1000.0,
            "best_load_matched_st_opv": best_offgrid_opv,
        }

        # ------------------------------------------------------------------
        # 3. Ground-Mounted PV-Only Counterfactual (c-Si GCR 0.70, yield = 0)
        # ------------------------------------------------------------------
        pv70_wm2 = wp5.resolve_pv_wm2(npz_hourly, row_csi70)
        load_pvonly, _ = wp5.build_factory_load_profile(crop_key, crop_cfg, baseline_kg, catchment)
        bess_pvonly = wp5.size_bess_kwh(load_pvonly, day_frac, bess_opt)
        disp_pvonly = wp5.simulate_8760_dispatch(pv70_wm2, load_pvonly, bess_pvonly, rte, allow_grid_export=True)

        pvonly_by_bos = {}
        for c_bos_g in (15.0, 25.0, 35.0):
            tea_g = wp5.evaluate_20yr_tea_lca(
                "cSi_Opaque_AV", crop_key, 0.70, 0.0,
                float(row_csi70["pv_mwh_ha_yr"]) * 1000.0, disp_pvonly, bess_pvonly, False, cfg,
                c_bos_si_override=c_bos_g,
            )
            # Zero tutor saving cleanly (already 0 since yield=0? No, technology=='cSi_Opaque_AV' triggers tutor_savings for pepper!)
            if crop_key == "penja_white_pepper":
                ann_tutor = float(cfg["economics"]["avoided_pepper_living_tutor_cost_usd_ha_yr"])
                wacc = float(cfg["economics"]["discount_rate_wacc"])
                pv_factor = sum(1.0 / ((1.0 + wacc) ** t) for t in range(1, 21))
                tea_g["npv_usd_ha"] -= ann_tutor * pv_factor
            pvonly_by_bos[f"bos_{int(c_bos_g)}"] = {
                "npv_usd_ha": float(tea_g["npv_usd_ha"]),
                "lcoe_usd_kwh": float(tea_g["lcoe_usd_kwh"]),
            }

        tea_opv_base = wp5.evaluate_20yr_tea_lca(
            "ST_OPV_PM6Y6", crop_key, 0.65, float(row_opv44["yield_kg_ha"]),
            float(row_opv44["pv_mwh_ha_yr"]) * 1000.0,
            wp5.simulate_8760_dispatch(pv_opv_wm2, load_opv_full, bess_load, rte, allow_grid_export=True),
            bess_load, False, cfg,
        )
        load_csi40, _ = wp5.build_factory_load_profile(crop_key, crop_cfg, float(row_csi40["yield_kg_ha"]), catchment)
        bess_csi40 = wp5.size_bess_kwh(load_csi40, day_frac, bess_opt)
        tea_csi40_base = wp5.evaluate_20yr_tea_lca(
            "cSi_Opaque_AV", crop_key, 0.40, float(row_csi40["yield_kg_ha"]),
            float(row_csi40["pv_mwh_ha_yr"]) * 1000.0,
            wp5.simulate_8760_dispatch(pv_csi_wm2, load_csi40, bess_csi40, rte, allow_grid_export=True),
            bess_csi40, False, cfg,
        )

        b15 = pvonly_by_bos["bos_15"]["npv_usd_ha"]
        b35 = pvonly_by_bos["bos_35"]["npv_usd_ha"]
        slope_bos = (b35 - b15) / 20.0
        c_be_ground = 15.0 + (float(tea_csi40_base["npv_usd_ha"]) - b15) / slope_bos

        results["ground_mounted_pv_only"][crop_key] = {
            "gcr70_pv_mwh_ha_yr": float(row_csi70["pv_mwh_ha_yr"]),
            "parametric_bos_usd_m2": pvonly_by_bos,
            "elevated_csi_gcr40_npv": float(tea_csi40_base["npv_usd_ha"]),
            "focal_opv_apt44_npv": float(tea_opv_base["npv_usd_ha"]),
            "break_even_c_bos_ground_usd_m2": float(c_be_ground),
        }

        # ------------------------------------------------------------------
        # 4. Shapley split phi_spec vs phi_Q + 5. Bounded R:FR sensitivity
        # ------------------------------------------------------------------
        # Recompute hourly arrays bit-for-bit identically to wp3_microclimate_crop_engine.py
        t_beam_par = np.array([
            float(trapz(T_beam_44[ai, par_mask] * ph_am15[par_mask], wl[par_mask])) / am15_par_ph
            for ai in range(len(angles_grid))
        ])
        t_beam_epar = np.array([
            float(trapz(T_beam_44[ai, epar_mask] * ph_am15[epar_mask], wl[epar_mask])) / am15_epar_ph
            for ai in range(len(angles_grid))
        ])
        t_beam_sw = np.array([
            float(trapz(T_beam_44[ai, :] * am15, wl)) / am15_sw_tot
            for ai in range(len(angles_grid))
        ])
        t_beam_red = np.array([
            float(trapz(T_beam_44[ai, red_mask] * ph_am15[red_mask], wl[red_mask])) / am15_red_ph
            for ai in range(len(angles_grid))
        ])
        t_beam_fr = np.array([
            float(trapz(T_beam_44[ai, fr_mask] * ph_am15[fr_mask], wl[fr_mask])) / am15_fr_ph
            for ai in range(len(angles_grid))
        ])

        zen_clipped = np.clip(climate["zenith_deg"], 0.0, 60.0)
        tb_par_h = np.interp(zen_clipped, angles_grid, t_beam_par)
        tb_epar_h = np.interp(zen_clipped, angles_grid, t_beam_epar)
        tb_sw_h = np.interp(zen_clipped, angles_grid, t_beam_sw)
        tb_red_h = np.interp(zen_clipped, angles_grid, t_beam_red)
        tb_fr_h = np.interp(zen_clipped, angles_grid, t_beam_fr)

        td_par = float(trapz(T_diff_44[par_mask] * ph_am15[par_mask], wl[par_mask])) / am15_par_ph
        td_epar = float(trapz(T_diff_44[epar_mask] * ph_am15[epar_mask], wl[epar_mask])) / am15_epar_ph
        td_sw = float(trapz(T_diff_44 * am15, wl)) / am15_sw_tot
        td_red = float(trapz(T_diff_44[red_mask] * ph_am15[red_mask], wl[red_mask])) / am15_red_ph
        td_fr = float(trapz(T_diff_44[fr_mask] * ph_am15[fr_mask], wl[fr_mask])) / am15_fr_ph

        gcr_opv = 0.65
        tau_par = (1.0 - gcr_opv) + gcr_opv * (climate["f_beam"] * tb_par_h + climate["f_diff"] * td_par)
        tau_epar = (1.0 - gcr_opv) + gcr_opv * (climate["f_beam"] * tb_epar_h + climate["f_diff"] * td_epar)
        tau_sw = (1.0 - gcr_opv) + gcr_opv * (climate["f_beam"] * tb_sw_h + climate["f_diff"] * td_sw)
        tau_red = (1.0 - gcr_opv) + gcr_opv * (climate["f_beam"] * tb_red_h + climate["f_diff"] * td_red)
        tau_fr = (1.0 - gcr_opv) + gcr_opv * (climate["f_beam"] * tb_fr_h + climate["f_diff"] * td_fr)
        epar_over_par = tau_epar / np.maximum(tau_par, 1e-6)
        rfr_arr = rfr_am15 * (tau_red / np.maximum(tau_fr, 1e-6))

        beta_opv = float(opv_cfg["pce_temp_coeff_per_c"])
        eps_opv = float(opv_cfg["infrared_emissivity"])
        soil_opv_d = float(opv_cfg["soiling_derating_seasonal_range"][1])
        soil_opv_w = float(opv_cfg["soiling_derating_seasonal_range"][0])

        res_full = wp3.solve_coupled_microclimate_and_assimilation(
            climate=climate, crop_cfg=crop_cfg, micro_cfg=micro_cfg,
            tau_par=tau_par, tau_sw=tau_sw, epar_over_par=epar_over_par, r_fr_ratio=rfr_arr,
            eta_ness_ratio=eta_opv_44, gcr=gcr_opv, pce_pv_ref_pct=pce_44, beta_pv_per_c=beta_opv,
            a_sw_panel=a_sw_44, eps_pv=eps_opv, clearance_m=cl_opv,
            soiling_dry=soil_opv_d, soiling_wet=soil_opv_w, irrigated=False, svf_bounds=svf_bounds,
        )
        res_spec_only = wp3.solve_coupled_microclimate_and_assimilation(
            climate=climate, crop_cfg=crop_cfg, micro_cfg=micro_cfg,
            tau_par=tau_par, tau_sw=tau_sw, epar_over_par=epar_over_par, r_fr_ratio=rfr_arr,
            eta_ness_ratio=1.0, gcr=gcr_opv, pce_pv_ref_pct=pce_44, beta_pv_per_c=beta_opv,
            a_sw_panel=a_sw_44, eps_pv=eps_opv, clearance_m=cl_opv,
            soiling_dry=soil_opv_d, soiling_wet=soil_opv_w, irrigated=False, svf_bounds=svf_bounds,
        )
        sh_full = wp3.compute_exact_shapley_4levers(climate, crop_cfg, res_s0, res_full, epar_over_par, eta_opv_44, baseline_kg)
        sh_spec = wp3.compute_exact_shapley_4levers(climate, crop_cfg, res_s0, res_spec_only, epar_over_par, 1.0, baseline_kg)

        results["shapley_split_spec_vs_q"][crop_key] = {
            "eta_opv_44_ratio": float(eta_opv_44),
            "phi_spec_plus_q_pct": sh_full["lever_spec_q_pct"],
            "phi_spec_only_pct": sh_spec["lever_spec_q_pct"],
            "phi_q_marginal_pp": float(sh_full["lever_spec_q_pct"] - sh_spec["lever_spec_q_pct"]),
            "delta_y_full_pct": sh_full["delta_y_total_pct"],
        }

        # Bounded R:FR sensitivity: modulate Vcmax & Jmax in fvcb_medlyn by {-2%, +2%, +5%} under elevated R:FR
        rfr_shift = {}
        for m_label, mult in (("minus_2pct", 0.98), ("plus_2pct", 1.02), ("plus_5pct", 1.05)):
            mod_cfg = copy.deepcopy(crop_cfg)
            fm = mod_cfg["fvcb_medlyn"]
            for k in ("V_cmax25", "J_max25", "V_cmax25_sun_cc", "J_max25_sun_cc"):
                if k in fm:
                    fm[k] = float(fm[k]) * mult
            res_rfr = wp3.solve_coupled_microclimate_and_assimilation(
                climate=climate, crop_cfg=mod_cfg, micro_cfg=micro_cfg,
                tau_par=tau_par, tau_sw=tau_sw, epar_over_par=epar_over_par, r_fr_ratio=rfr_arr,
                eta_ness_ratio=eta_opv_44, gcr=gcr_opv, pce_pv_ref_pct=pce_44, beta_pv_per_c=beta_opv,
                a_sw_panel=a_sw_44, eps_pv=eps_opv, clearance_m=cl_opv,
                soiling_dry=soil_opv_d, soiling_wet=soil_opv_w, irrigated=False, svf_bounds=svf_bounds,
            )
            dy_rfr = 100.0 * (res_rfr["A_net_annual_mol_m2"] - a_s0) / a_s0
            rfr_shift[m_label] = {
                "delta_y_pct": dy_rfr,
                "spread_vs_csi_gcr40_pp": dy_rfr - float(row_csi40["delta_y_total_pct"]),
            }
        results["spectral_rfr_sensitivity"][crop_key] = {
            "baseline_delta_y_pct": float(row_opv44["delta_y_total_pct"]),
            "csi_gcr40_delta_y_pct": float(row_csi40["delta_y_total_pct"]),
            "r_fr_opv": float(row_opv44["r_fr_mean"]),
            "r_fr_open_csi": float(row_s0["r_fr_mean"]),
            "r_fr_rel_increase_pct": 100.0 * (float(row_opv44["r_fr_mean"]) / float(row_s0["r_fr_mean"]) - 1.0),
            "bounded_capacity_shifts": rfr_shift,
        }

        # ------------------------------------------------------------------
        # 6. Inverter & Interconnection kW-Scaling Sensitivity (100, 150, 200 USD/kWp)
        # ST-OPV APT44 GCR 0.65: 6500 m2 * 0.0993 kWp/m2 = 645.45 kWp/ha
        # c-Si GCR 0.40:        4000 m2 * 0.205  kWp/m2 = 820.00 kWp/ha
        # ------------------------------------------------------------------
        kwp_opv = 6500.0 * (pce_44 / 100.0)
        kwp_csi = 4000.0 * (pce_si / 100.0)
        base_dnpv = float(tea_opv_base["npv_usd_ha"] - tea_csi40_base["npv_usd_ha"])
        kw_sens = {}
        for usd_per_kwp in (100.0, 150.0, 200.0):
            # Upfront kW-scaled inverter/interconnection + Year-10 inverter replacement (discounted at 10%)
            inv_disc_opv = kwp_opv * usd_per_kwp * (1.0 + 1.0 / (1.10 ** 10))
            inv_disc_csi = kwp_csi * usd_per_kwp * (1.0 + 1.0 / (1.10 ** 10))
            dnpv_adj = (float(tea_opv_base["npv_usd_ha"]) - inv_disc_opv) - (float(tea_csi40_base["npv_usd_ha"]) - inv_disc_csi)
            kw_sens[f"usd_{int(usd_per_kwp)}_kwp"] = {
                "inv_disc_opv_usd_ha": inv_disc_opv,
                "inv_disc_csi_usd_ha": inv_disc_csi,
                "delta_npv_opv_minus_csi_usd_ha": dnpv_adj,
                "change_in_delta_npv_usd_ha": dnpv_adj - base_dnpv,
            }
        results["inverter_kw_sensitivity"][crop_key] = {
            "kwp_opv_ha": kwp_opv,
            "kwp_csi_ha": kwp_csi,
            "base_delta_npv_usd_ha": base_dnpv,
            "cases": kw_sens,
        }

    # 7. Multiyear 2014-2023 decade statistics (median, mean, sd, min, max)
    import gzip, statistics
    from collections import defaultdict
    my_map: dict[tuple[str, str], list[float]] = defaultdict(list)
    with gzip.open(DATA_DIR / "wp3" / "multiyear_2014_2023" / "wp3_multiyear_scenario_results.csv.gz", "rt", encoding="utf-8") as fh:
        for row in _csv.DictReader(fh):
            my_map[(row["crop"], row["scenario_id"])].append(float(row["delta_y_total_pct"]))
    for scen_id in ("S3_OPV_APT44_GCR65", "S2_cSi_GCR40"):
        results["multiyear_decade_2014_2023"][scen_id] = {}
        for crop_key in CROPS:
            ys = my_map[(crop_key, scen_id)]
            results["multiyear_decade_2014_2023"][scen_id][crop_key] = {
                "n_years": len(ys),
                "mean_pct": float(statistics.mean(ys)),
                "median_pct": float(statistics.median(ys)),
                "sd_pct": float(statistics.stdev(ys)),
                "min_pct": float(min(ys)),
                "max_pct": float(max(ys)),
            }

    OUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
