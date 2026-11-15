#!/usr/bin/env python3
"""
Focused WP5 Round-3 sensitivities (without altering canonical WP5 CSVs):
  1. Captive-at-grid-tariff counterfactual: re-evaluate D3 (APT44 GCR65) and
     D2 (c-Si GCR40) crediting/billing factory self-consumption at ARSEL MT
     grid tariffs (0.085, 0.10, 0.15, 0.205 USD/kWh) vs. baseline 0.45 USD/kWh
     avoided diesel genset (both with selected BESS and daytime-only no-BESS).
  2. Year-20 residual-value sensitivity: quantify unconsumed capital credit at
     Year 20 (5/25 = 20% of 25-yr c-Si module-only or module+BOS CAPEX, and
     prorated remaining OPV active-layer life when T80 does not divide 20 yr),
     alongside the shift in Delta NPV = NPV_OPV - NPV_Si and pepper T80*.

Writes: data/wp5/wp5d_tariff_residual_sensitivity.json
"""

from __future__ import annotations

import copy
import json
import math
import sys
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import brentq

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from scripts import wp5_tea_lca_sobol as wp5

CROPS = ("arabica_coffee", "penja_white_pepper", "highland_tea")
SCENARIOS = ("S3_OPV_APT44_GCR65", "S2_cSi_GCR40")
CAPTIVE_TARIFFS_USD_KWH = (0.45, 0.205, 0.15, 0.10, 0.085)
DATA_DIR = PACKAGE_ROOT / "data"
OUT_JSON = DATA_DIR / "wp5" / "wp5d_tariff_residual_sensitivity.json"


def _selected_bess(crop_name: str) -> str:
    return "overnight_withering_bess" if crop_name == "highland_tea" else "small_lfp_buffer_2h"


def _run_dcf_with_overrides(
    row: dict[str, Any],
    bess_option: str,
    cfg: dict[str, Any],
    *,
    captive_tariff_usd_kwh: float | None = None,
    t80_opv_override: float | None = None,
    c_mod_opv_override: float | None = None,
    c_rep_opv_override: float | None = None,
    wacc_override: float | None = None,
    csi_residual_mode: str = "none",
) -> dict[str, float]:
    """Run WP5 8760h dispatch + 20yr DCF with optional captive tariff & Yr-20 c-Si salvage."""
    crop_name = row["crop"]
    crop_cfg = cfg["crops"][crop_name]
    catchment = wp5.COOP_CATCHMENT_HA[crop_name]

    npz_data = np.load(wp5.WP3_DIR / f"hourly_{crop_name}.npz")
    pv_wm2 = wp5.resolve_pv_wm2(npz_data, row)
    pv_kwh_yr_base = float(row["pv_mwh_ha_yr"]) * 1000.0
    load_kw, _ = wp5.build_factory_load_profile(crop_name, crop_cfg, float(row["yield_kg_ha"]), catchment)
    bess_cap = wp5.size_bess_kwh(load_kw, float(crop_cfg["processing_daytime_load_fraction"]), bess_option)
    dispatch = wp5.simulate_8760_dispatch(
        pv_wm2,
        load_kw,
        bess_cap,
        bess_rte=float(cfg["economics"]["bess_roundtrip_efficiency"]),
        allow_grid_export=True,
        export_acceptance_fraction=1.0,
    )

    cfg_local = copy.deepcopy(cfg)
    if captive_tariff_usd_kwh is not None:
        cfg_local["economics"]["diesel_generation_cost_usd_kwh"] = float(captive_tariff_usd_kwh)

    out = wp5.evaluate_20yr_tea_lca(
        technology=row["technology"],
        crop_name=crop_name,
        gcr=float(row["gcr"]),
        yield_kg_ha=float(row["yield_kg_ha"]),
        pv_kwh_yr_base=pv_kwh_yr_base,
        dispatch_yr1=dispatch,
        bess_cap_kwh=bess_cap,
        irrigated=bool(int(row["irrigated"])),
        cfg=cfg_local,
        t80_opv_override=t80_opv_override,
        c_mod_opv_override=c_mod_opv_override,
        c_rep_opv_override=c_rep_opv_override,
        wacc_override=wacc_override,
        allow_grid_export=True,
    )

    if row["technology"] == "cSi_Opaque_AV" and csi_residual_mode != "none":
        horizon = int(cfg_local["economics"]["analysis_period_years"])
        wacc = float(wacc_override if wacc_override is not None else cfg_local["economics"]["discount_rate_wacc"])
        si_cfg = cfg_local["si_counterfactual"]
        si_life = float(si_cfg["lifetime_years"])
        rem_frac = max(0.0, (si_life - horizon) / si_life)
        area_m2 = 10000.0 * float(row["gcr"])
        if csi_residual_mode == "module_only":
            cap_base = area_m2 * float(si_cfg["module_cost_usd_per_m2"])
        elif csi_residual_mode == "module_and_bos":
            cap_base = area_m2 * (float(si_cfg["module_cost_usd_per_m2"]) + float(si_cfg["bos_structural_cost_usd_per_m2"]))
        else:
            raise ValueError(f"Unknown csi_residual_mode: {csi_residual_mode}")
        salvage_undisc = rem_frac * cap_base
        salvage_disc = salvage_undisc / ((1.0 + wacc) ** horizon)
        out["salvage_undisc_usd_ha"] = salvage_undisc
        out["salvage_disc_usd_ha"] = salvage_disc
        out["npv_with_salvage_usd_ha"] = out["npv_usd_ha"] + salvage_disc
    else:
        out["salvage_undisc_usd_ha"] = 0.0
        out["salvage_disc_usd_ha"] = 0.0
        out["npv_with_salvage_usd_ha"] = out["npv_usd_ha"]

    out["bess_cap_kwh"] = bess_cap
    return out


def main() -> None:
    cfg = wp5.load_yaml(wp5.PARAMS_PATH)
    wp3_rows = wp5.load_wp3_scenarios(wp5.WP3_CSV_PATH)
    by_wp3 = {(r["crop"], r["scenario_id"]): r for r in wp3_rows}

    # 1. Captive-at-grid-tariff counterfactual
    captive_results: dict[str, Any] = {}
    for crop in CROPS:
        sel_bess = _selected_bess(crop)
        bess_modes = [sel_bess] + (["no_bess_daytime_only"] if sel_bess != "no_bess_daytime_only" else [])
        crop_entry: dict[str, Any] = {}
        for bmode in bess_modes:
            tariff_rows: list[dict[str, Any]] = []
            for tariff in CAPTIVE_TARIFFS_USD_KWH:
                r_opv = _run_dcf_with_overrides(by_wp3[(crop, "S3_OPV_APT44_GCR65")], bmode, cfg, captive_tariff_usd_kwh=tariff)
                r_csi = _run_dcf_with_overrides(by_wp3[(crop, "S2_cSi_GCR40")], bmode, cfg, captive_tariff_usd_kwh=tariff)
                tariff_rows.append({
                    "captive_tariff_usd_kwh": tariff,
                    "label": "baseline_diesel_0.45" if abs(tariff - 0.45) < 1e-9 else f"grid_mt_{tariff:.3f}",
                    "opv_npv_usd_ha": round(r_opv["npv_usd_ha"], 2),
                    "opv_irr_pct": None if math.isnan(r_opv["irr_pct"]) else round(r_opv["irr_pct"], 2),
                    "opv_dpbp_yr": None if math.isnan(r_opv["dpbp_yr"]) else round(r_opv["dpbp_yr"], 2),
                    "csi_npv_usd_ha": round(r_csi["npv_usd_ha"], 2),
                    "csi_irr_pct": None if math.isnan(r_csi["irr_pct"]) else round(r_csi["irr_pct"], 2),
                    "delta_npv_opv_minus_csi_usd_ha": round(r_opv["npv_usd_ha"] - r_csi["npv_usd_ha"], 2),
                    "bess_cap_kwh_opv": r_opv["bess_cap_kwh"],
                })
            crop_entry[bmode] = tariff_rows
        captive_results[crop] = crop_entry

    # 2. Year-20 residual-value sensitivity (WACC=10% base + 6%/15% bounds + pepper R2R parity T80*)
    residual_results: dict[str, Any] = {"by_crop_wacc10": {}, "wacc_stress_tea_and_pepper": {}, "opv_t80_salvage_check_pepper": {}, "pepper_r2r_15_parity_t80": {}}
    for crop in CROPS:
        sel_bess = _selected_bess(crop)
        opv_base = _run_dcf_with_overrides(by_wp3[(crop, "S3_OPV_APT44_GCR65")], sel_bess, cfg)
        csi_none = _run_dcf_with_overrides(by_wp3[(crop, "S2_cSi_GCR40")], sel_bess, cfg, csi_residual_mode="none")
        csi_mod = _run_dcf_with_overrides(by_wp3[(crop, "S2_cSi_GCR40")], sel_bess, cfg, csi_residual_mode="module_only")
        csi_all = _run_dcf_with_overrides(by_wp3[(crop, "S2_cSi_GCR40")], sel_bess, cfg, csi_residual_mode="module_and_bos")
        residual_results["by_crop_wacc10"][crop] = {
            "opv_npv_usd_ha": round(opv_base["npv_usd_ha"], 2),
            "opv_rem_frac_at_t80_5": 0.0,
            "csi_npv_no_salvage_usd_ha": round(csi_none["npv_usd_ha"], 2),
            "csi_module_only_salvage_undisc_usd_ha": round(csi_mod["salvage_undisc_usd_ha"], 2),
            "csi_module_only_salvage_disc_usd_ha": round(csi_mod["salvage_disc_usd_ha"], 2),
            "csi_npv_module_salvage_usd_ha": round(csi_mod["npv_with_salvage_usd_ha"], 2),
            "csi_mod_bos_salvage_undisc_usd_ha": round(csi_all["salvage_undisc_usd_ha"], 2),
            "csi_mod_bos_salvage_disc_usd_ha": round(csi_all["salvage_disc_usd_ha"], 2),
            "csi_npv_mod_bos_salvage_usd_ha": round(csi_all["npv_with_salvage_usd_ha"], 2),
            "delta_npv_baseline_usd_ha": round(opv_base["npv_usd_ha"] - csi_none["npv_usd_ha"], 2),
            "delta_npv_with_csi_mod_salvage_usd_ha": round(opv_base["npv_usd_ha"] - csi_mod["npv_with_salvage_usd_ha"], 2),
            "delta_npv_with_csi_mod_bos_salvage_usd_ha": round(opv_base["npv_usd_ha"] - csi_all["npv_with_salvage_usd_ha"], 2),
        }

    for wacc in (0.06, 0.10, 0.15):
        csi_mod = _run_dcf_with_overrides(by_wp3[("penja_white_pepper", "S2_cSi_GCR40")], _selected_bess("penja_white_pepper"), cfg, wacc_override=wacc, csi_residual_mode="module_only")
        csi_all = _run_dcf_with_overrides(by_wp3[("penja_white_pepper", "S2_cSi_GCR40")], _selected_bess("penja_white_pepper"), cfg, wacc_override=wacc, csi_residual_mode="module_and_bos")
        residual_results["wacc_stress_tea_and_pepper"][f"wacc_{int(round(wacc*100))}pct"] = {
            "csi_module_only_salvage_disc_usd_ha": round(csi_mod["salvage_disc_usd_ha"], 2),
            "csi_mod_bos_salvage_disc_usd_ha": round(csi_all["salvage_disc_usd_ha"], 2),
        }

    # Check non-divisor OPV T80 (e.g. T80=7, 12, 16 yr) in Penja pepper with proportional c_rep = 15 * (30/35)
    c_rep_r2r15 = 15.0 * (
        float(cfg["opv_technology"]["replacement_cost_usd_per_m2"])
        / float(cfg["opv_technology"]["module_cost_usd_per_m2"])
    )
    for t80_val in (5.0, 7.0, 12.0, 16.0):
        opv_row = by_wp3[("penja_white_pepper", "S3_OPV_APT44_GCR65")]
        r_opv = _run_dcf_with_overrides(opv_row, _selected_bess("penja_white_pepper"), cfg, t80_opv_override=t80_val, c_mod_opv_override=15.0, c_rep_opv_override=c_rep_r2r15)
        residual_results["opv_t80_salvage_check_pepper"][f"t80_{int(t80_val)}yr_at_15usd"] = {
            "opv_npv_usd_ha": round(r_opv["npv_usd_ha"], 2),
            "pv_rep_disc_net_of_salvage_usd_ha": round(r_opv["pv_rep_disc_usd_ha"], 2),
        }

    # Re-solve Penja pepper R2R $15/m^2 parity T80* against c-Si with no salvage, module salvage, and module+BOS salvage
    pep_opv = by_wp3[("penja_white_pepper", "S3_OPV_APT44_GCR65")]
    pep_csi = by_wp3[("penja_white_pepper", "S2_cSi_GCR40")]
    pep_bess = _selected_bess("penja_white_pepper")
    for mode_key in ("none", "module_only", "module_and_bos"):
        target_csi = _run_dcf_with_overrides(pep_csi, pep_bess, cfg, csi_residual_mode=mode_key)["npv_with_salvage_usd_ha"]
        def _diff(t80_x: float) -> float:
            return _run_dcf_with_overrides(pep_opv, pep_bess, cfg, t80_opv_override=t80_x, c_mod_opv_override=15.0, c_rep_opv_override=c_rep_r2r15)["npv_usd_ha"] - target_csi
        lo, hi = _diff(2.0), _diff(35.0)
        t80_star = float(brentq(_diff, 2.0, 35.0)) if lo * hi < 0 else None
        residual_results["pepper_r2r_15_parity_t80"][mode_key] = {
            "target_csi_npv_usd_ha": round(target_csi, 2),
            "t80_star_yr": None if t80_star is None else round(t80_star, 2),
        }

    payload = {
        "generated_date": date.today().isoformat(),
        "framework_version": cfg["provenance"]["framework_version"],
        "captive_at_grid_tariff_sensitivity": captive_results,
        "year20_residual_value_sensitivity": residual_results,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
