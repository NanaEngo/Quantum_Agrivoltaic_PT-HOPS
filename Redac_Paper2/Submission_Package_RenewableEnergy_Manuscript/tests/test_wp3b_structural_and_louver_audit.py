"""Regression tests for WP3b coupled structural (AWC x g_b), monsoon-open louver, and climate stress audits."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent
AUDIT_JSON = PKG_ROOT / "data" / "wp3" / "wp3b_structural_and_louver_audit.json"


class TestWp3bStructuralAndLouverAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        assert AUDIT_JSON.exists(), f"Missing WP3b audit JSON: {AUDIT_JSON}"
        cls.data = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))

    def test_schema_and_center_matches_baseline_wp3_wp5(self) -> None:
        self.assertIn("awc_gb_sweep", self.data)
        self.assertIn("monsoon_louver_counterfactual", self.data)
        self.assertIn("synthetic_climate_stress", self.data)

        for crop in ("arabica_coffee", "penja_white_pepper", "highland_tea"):
            ag = self.data["awc_gb_sweep"][crop]
            self.assertEqual(len(ag["grid"]), 9)
            center = ag["center_awc160_gb1_2"]
            self.assertLess(center["baseline_verify_opv_abs_err_pp"], 1e-5)
            self.assertLess(center["baseline_verify_csi_abs_err_pp"], 1e-5)
            self.assertLessEqual(ag["opv_minus_csi_min_pp"], ag["opv_minus_csi_max_pp"])

            ml = self.data["monsoon_louver_counterfactual"][crop]
            for tech_key in ("s6_opv_apt44_gcr65", "s6_csi_gcr40"):
                d = ml[tech_key]
                self.assertLess(d["baseline_wp5_npv_abs_err_usd_ha"], 1.0)
                # Retracting panels June-October must raise annual crop yield vs fixed panels
                self.assertGreater(d["delta_y_rescue_pp"], 0.5)
                # Retracting panels June-October must reduce annual PV generation
                self.assertLess(d["delta_pv_mwh_ha_yr"], -10.0)
                self.assertGreaterEqual(d["break_even_actuation_capex_incl_om_usd_m2"], 0.0)

    def test_synthetic_climate_stress_monotonic_direction(self) -> None:
        for crop in ("arabica_coffee", "penja_white_pepper", "highland_tea"):
            cs = self.data["synthetic_climate_stress"][crop]
            self.assertIn("warm_dry_stress", cs)
            self.assertIn("baseline_2023_era5", cs)
            self.assertIn("cool_cloudy_stress", cs)
            # Warm-dry stress intensifies dry-season soil moisture relief under shade vs cool-cloudy
            self.assertGreater(
                cs["warm_dry_stress"]["opv_delta_y_pct"],
                cs["cool_cloudy_stress"]["opv_delta_y_pct"],
            )


if __name__ == "__main__":
    unittest.main()
