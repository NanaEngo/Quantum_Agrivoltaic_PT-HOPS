#!/usr/bin/env python3
"""WP3/WP4 Unit & Physical Verification Suite (Bidirectional T_pv <-> T_leaf + FvCB-Medlyn + Exact Shapley)."""

import csv
import json
import sys
import unittest
from pathlib import Path

import numpy as np

PKG_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PKG_ROOT / "scripts"
DATA_WP3 = PKG_ROOT / "data" / "wp3"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import wp3_microclimate_crop_engine as wp3  # noqa: E402


class TestWP3MicroclimateCrop(unittest.TestCase):
    def test_wp3_outputs_exist_and_schema(self):
        csv_path = DATA_WP3 / "wp3_crop_microclimate_scenarios.csv"
        sum_path = DATA_WP3 / "wp3_validation_summary.json"
        self.assertTrue(csv_path.exists())
        self.assertTrue(sum_path.exists())

        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertGreaterEqual(len(rows), 120)

        crops_seen = {r["crop"] for r in rows}
        self.assertEqual(crops_seen, {"arabica_coffee", "penja_white_pepper", "highland_tea"})

        for ck in crops_seen:
            npz_path = DATA_WP3 / f"hourly_{ck}.npz"
            self.assertTrue(npz_path.exists(), f"Missing hourly archive for {ck}")
            d = np.load(npz_path)
            self.assertEqual(len(d["sw_ghi"]), 8760)
            self.assertIn("S2_cSi_GCR40_pv_wm2", d)
            self.assertIn("S5_OPV_APT44_GCR65_Irrig_A", d)

    def test_energy_balance_and_shapley_and_et_conservation(self):
        with open(DATA_WP3 / "wp3_crop_microclimate_scenarios.csv", "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        for r in rows:
            res_e = float(r["max_energy_res_wm2"])
            res_s = float(r["shapley_residual_pct"])
            self.assertLess(res_e, 1e-3, f"Energy balance residual too large in {r['crop']} {r['scenario_id']}: {res_e}")
            self.assertLess(res_s, 1e-9, f"Shapley additivity residual too large in {r['crop']} {r['scenario_id']}: {res_s}")

            et_tot = float(r["transp_mm_yr"])
            et_rad = float(r["transp_rad_mm_yr"])
            et_aero = float(r["transp_aero_mm_yr"])
            self.assertAlmostEqual(et_tot, et_rad + et_aero, places=2)

            if r["scenario_id"] == "S0_open_control":
                self.assertAlmostEqual(float(r["delta_y_total_pct"]), 0.0, places=9)
                self.assertEqual(float(r["pv_mwh_ha_yr"]), 0.0)

    def test_baseline_yields_irrigation_and_cooling_bounds(self):
        with open(DATA_WP3 / "wp3_crop_microclimate_scenarios.csv", "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        by_key = {(r["crop"], r["scenario_id"]): r for r in rows}
        expected_base = {"arabica_coffee": 850.0, "penja_white_pepper": 800.0, "highland_tea": 1800.0}
        for ck, y_exp in expected_base.items():
            s0 = by_key[(ck, "S0_open_control")]
            s0_irr = by_key[(ck, "S0_open_irrigated")]
            s1 = by_key[(ck, "S1_agroforestry_shade")]
            self.assertAlmostEqual(float(s0["yield_kg_ha"]), y_exp, places=2)
            # Irrigation strictly increases open-field yield and eliminates dry soil stress
            self.assertGreater(float(s0_irr["delta_y_total_pct"]), 0.0)
            self.assertAlmostEqual(float(s0_irr["f_soil_dry_mean"]), 1.0, places=5)
            # Optimal shade cools dry-season daytime leaves within [-1.5, -3.5] C
            dt_dry = float(s1["dt_leaf_dry_day_c"])
            self.assertTrue(-3.5 <= dt_dry <= -1.5, f"Unexpected dry-day cooling for {ck}: {dt_dry}")

    def test_heavy_shade_turnover_and_view_factor_ordering(self):
        with open(DATA_WP3 / "wp3_crop_microclimate_scenarios.csv", "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        by_key = {(r["crop"], r["scenario_id"]): r for r in rows}

        # Excessive 70% shading must reduce wet-season assimilation & annual yield on all 3 crops
        for ck in ("arabica_coffee", "penja_white_pepper", "highland_tea"):
            heavy_csi = by_key[(ck, "S2_cSi_GCR70")]
            heavy_opv = by_key[(ck, "S3_OPV_APT20_GCR85")]
            self.assertLess(float(heavy_csi["delta_y_wet_pct"]), -15.0)
            self.assertLess(float(heavy_csi["delta_y_total_pct"]), -10.0)
            self.assertLess(float(heavy_opv["delta_y_total_pct"]), -10.0)

        # Confined 1.2 m tea clearance has stronger downward LWIR view factor than 1.4 m coffee or 1.5 m pepper
        flp_tea = float(by_key[("highland_tea", "S3_OPV_APT44_GCR65")]["view_factor_flp"])
        flp_coffee = float(by_key[("arabica_coffee", "S3_OPV_APT44_GCR65")]["view_factor_flp"])
        flp_pepper = float(by_key[("penja_white_pepper", "S3_OPV_APT44_GCR65")]["view_factor_flp"])
        self.assertGreater(flp_tea, flp_coffee)
        self.assertGreater(flp_coffee, flp_pepper)

    def test_ness_quantum_shift_bounded_biological_effect(self):
        cfg = wp3.load_config()
        crop_cfg = cfg["crops"]["arabica_coffee"]
        clim = wp3.load_site_climate(PKG_ROOT / crop_cfg["climate_dataset"], 5.52)
        n_h = len(clim["T_air_c"])
        ppfd = clim["sw_ghi"] * 1.4
        f_pi = np.ones(n_h)
        tl = clim["T_air_c"] + 1.5
        vpd = np.maximum(0.2, clim["vpd_air_kpa"])
        fsoil = np.full(n_h, 0.85)
        epar = np.ones(n_h)

        a_base, _ = wp3.evaluate_biochem_only_corner(clim, crop_cfg, ppfd, f_pi, tl, vpd, fsoil, epar, 1.0, 0.30)
        a_q, _ = wp3.evaluate_biochem_only_corner(clim, crop_cfg, ppfd, f_pi, tl, vpd, fsoil, epar, 1.0 + 3.4e-5, 0.30)
        rel_diff_pct = 100.0 * abs(a_q - a_base) / a_base
        self.assertLess(rel_diff_pct, 0.01)


if __name__ == "__main__":
    unittest.main()
