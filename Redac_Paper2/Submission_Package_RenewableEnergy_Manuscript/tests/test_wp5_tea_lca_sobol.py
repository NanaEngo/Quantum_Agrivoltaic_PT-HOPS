#!/usr/bin/env python3
"""Unit and conservation tests for WP5 TEA, dispatch, LCA, break-even, Sobol, and phase maps."""

import csv
import json
import sys
import unittest
from pathlib import Path

import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from wp5_tea_lca_sobol import (  # noqa: E402
    build_factory_load_profile,
    load_yaml,
    simulate_8760_dispatch,
    size_bess_kwh,
)


class TestWP5TeaLcaSobol(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cfg = load_yaml(BASE_DIR / "parameters.yaml")
        cls.wp5_dir = BASE_DIR / "data" / "wp5"
        with open(cls.wp5_dir / "wp5_tea_lca_scenarios.csv", "r", encoding="utf-8") as fh:
            cls.rows = list(csv.DictReader(fh))
        with open(cls.wp5_dir / "wp5_validation_summary.json", "r", encoding="utf-8") as fh:
            cls.summary = json.load(fh)
        with open(cls.wp5_dir / "wp5_sobol_sensitivity.json", "r", encoding="utf-8") as fh:
            cls.sobol = json.load(fh)
        cls.phase = np.load(cls.wp5_dir / "wp5_phase_maps.npz")

    def test_dispatch_conservation_and_rte_bound(self) -> None:
        """Hourly PV-factory-LFP dispatch conserves energy and obeys RTE <= 0.90."""
        tea_cfg = self.cfg["crops"]["highland_tea"]
        load_kw, ann_kwh = build_factory_load_profile("highland_tea", tea_cfg, 1800.0, 450.0)
        self.assertAlmostEqual(float(np.sum(load_kw)), ann_kwh, places=5)

        npz = np.load(BASE_DIR / "data" / "wp3" / "hourly_highland_tea.npz")
        pv_wm2 = npz["S3_OPV_APT44_GCR65_pv_wm2"]

        d_nobess = simulate_8760_dispatch(pv_wm2, load_kw, 0.0, 0.90)
        cap_over = size_bess_kwh(load_kw, tea_cfg["processing_daytime_load_fraction"], "overnight_withering_bess")
        d_over = simulate_8760_dispatch(pv_wm2, load_kw, cap_over, 0.90)

        self.assertLess(d_nobess["energy_balance_err_kwh"], 1e-6)
        self.assertLess(d_over["energy_balance_err_kwh"], 1e-6)
        self.assertGreater(d_over["e_self_consumed_kwh"], d_nobess["e_self_consumed_kwh"])
        self.assertLessEqual(d_over["effective_rte"], 0.900001)
        self.assertLess(self.summary["max_dispatch_energy_err_kwh"], 1e-5)

    def test_dispatch_export_acceptance_splits_surplus_and_validates(self) -> None:
        kwargs = {
            "pv_wm2": np.array([0.3, 0.0]),
            "load_kw": np.array([1.0, 0.0]),
            "bess_cap_kwh": 0.0,
            "bess_rte": 0.9,
            "allow_grid_export": True,
        }
        dispatch = simulate_8760_dispatch(**kwargs, export_acceptance_fraction=0.5)

        self.assertAlmostEqual(dispatch["e_direct_kwh"], 1.0)
        self.assertAlmostEqual(dispatch["e_export_kwh"], 1.0)
        self.assertAlmostEqual(dispatch["e_curtail_kwh"], 1.0)
        self.assertLess(dispatch["energy_balance_err_kwh"], 1e-12)

        for fraction in (-0.01, 1.01, np.nan, np.inf):
            with self.subTest(export_acceptance_fraction=fraction):
                with self.assertRaises(ValueError):
                    simulate_8760_dispatch(**kwargs, export_acceptance_fraction=fraction)

    def test_baseline_zero_carbon_zero_subsidy_and_s4_monotonic(self) -> None:
        """Baseline scenarios carry zero carbon/subsidy revenue, and S4 T80 extension strictly helps."""
        baselines = [r for r in self.rows if r["wp5_variant"] == "baseline_zero_credit"]
        self.assertGreater(len(baselines), 50)
        for r in baselines:
            self.assertEqual(float(r["carbon_price_usd_t"]), 0.0)
            self.assertEqual(float(r["subsidy_rate"]), 0.0)
            self.assertEqual(int(r["certified_price"]), 0)

        for crop in ("arabica_coffee", "penja_white_pepper", "highland_tea"):
            bess_tgt = "overnight_withering_bess" if crop == "highland_tea" else "small_lfp_buffer_2h"
            subset = {
                r["wp5_variant"]: r
                for r in self.rows
                if r["crop"] == crop and r["scenario_id"] == "S3_OPV_APT44_GCR65" and r["bess_option"] == bess_tgt
            }
            s3 = subset["baseline_zero_credit"]
            s4_15 = subset["S4_OPV_encapsulated_T80_15yr"]
            s4_25 = subset["S4_OPV_encapsulated_T80_25yr"]
            self.assertGreater(float(s4_15["npv_usd_ha"]), float(s3["npv_usd_ha"]))
            self.assertGreater(float(s4_25["npv_usd_ha"]), float(s4_15["npv_usd_ha"]))
            self.assertLess(float(s4_15["lca_pv_intensity_gco2e_kwh"]), float(s3["lca_pv_intensity_gco2e_kwh"]))
            self.assertLess(float(s4_25["lca_pv_intensity_gco2e_kwh"]), float(s4_15["lca_pv_intensity_gco2e_kwh"]))

    def test_dual_fu_lca_breakeven_and_ler(self) -> None:
        """Carbon break-even T80* sits in physical window and LER > 1.35 on balanced APT44_GCR65."""
        for crop, info in self.summary["break_even_t80_by_crop"].items():
            t80_lca = float(info["t80_lca_breakeven_yr"])
            self.assertGreater(t80_lca, 5.0, msg=f"{crop} T80_lca* unexpectedly <= 5 yr")
            self.assertLess(t80_lca, 15.0, msg=f"{crop} T80_lca* unexpectedly >= 15 yr")

        irrig_opv = [r for r in self.rows if r["scenario_id"] == "S5_OPV_APT44_GCR65_Irrig"]
        self.assertGreaterEqual(len(irrig_opv), 3)
        for r in irrig_opv:
            self.assertGreater(float(r["ler"]), 1.35)

    def test_sobol_qmc_bounds_and_quantum_bound(self) -> None:
        """Sobol indices stay bounded in [0,1] and quantum NESS sensitivity is negligible."""
        self.assertEqual(self.summary["n_sobol_base_samples"], 10000)
        for crop, res in self.sobol.items():
            for pname, vals in res["sobol_delta_npv_opv_vs_csi"].items():
                self.assertGreaterEqual(vals["S_i"], 0.0, msg=f"{crop} {pname} S_i < 0")
                self.assertLessEqual(vals["S_Ti"], 1.0, msg=f"{crop} {pname} S_Ti > 1")
            q_sti = res["sobol_npv_opv"]["eta_ness_shift_pct"]["S_Ti"]
            q_sti_diff = res["sobol_delta_npv_opv_vs_csi"]["eta_ness_shift_pct"]["S_Ti"]
            self.assertLess(q_sti, 1e-4, msg=f"{crop} quantum S_Ti (NPV_OPV) too large: {q_sti}")
            self.assertLess(q_sti_diff, 1e-4, msg=f"{crop} quantum S_Ti (Delta NPV) too large: {q_sti_diff}")
            top_driver = max(
                res["sobol_delta_npv_opv_vs_csi"].items(), key=lambda kv: kv[1]["S_Ti"]
            )[0]
            self.assertIn(top_driver, ("c_mod_opv_usd_m2", "t80_opv_yr", "c_bos_si_usd_m2"))

        rob_path = BASE_DIR / "data" / "wp5" / "wp5_sobol_robustness.json"
        self.assertTrue(rob_path.exists(), "Missing wp5_sobol_robustness.json adversarial sensitivity ledger")
        rob = json.loads(rob_path.read_text(encoding="utf-8"))
        for vname, crops_map in rob["variants"].items():
            for crop, vals in crops_map.items():
                self.assertLess(vals["quantum_S_Ti_delta_npv"], 1e-5, msg=f"{vname}/{crop} S_Ti unexpectedly large")
                self.assertGreater(vals["prob_opv_beats_csi"], 0.05)
                self.assertLess(vals["prob_opv_beats_csi"], 0.35)

    def test_phase_maps_sign_transitions(self) -> None:
        """Agronomic phase map and LCA break-even grids contain valid zero-contour sign changes."""
        dy = self.phase["agro_delta_y_pct"]
        self.assertEqual(dy.shape, (30, 30))
        self.assertLess(float(np.min(dy)), 0.0)
        self.assertGreater(float(np.max(dy)), 0.0)
        for crop in ("arabica_coffee", "penja_white_pepper", "highland_tea"):
            dlca = self.phase[f"{crop}_delta_lca_grid"]
            self.assertEqual(dlca.shape, (23, 25))
            self.assertLess(float(np.min(dlca)), 0.0)
            self.assertGreater(float(np.max(dlca)), 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
