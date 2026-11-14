"""Regression checks for weather-year archive validation and 2023 parity policy."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import wp1_multiyear_climate_robustness as multiyear


class TestMultiyearClimateRobustness(unittest.TestCase):
    def test_calendar_hour_counts_include_leap_day(self) -> None:
        self.assertEqual(multiyear.expected_hour_count(2019), 8760)
        self.assertEqual(multiyear.expected_hour_count(2020), 8784)

    def test_penja_2023_source_drift_is_bounded_and_reported(self) -> None:
        site = {"site_key": "njombe_penja_pepper"}
        baseline = {name: [0.0, 1.0] for name in multiyear.HOURLY}
        current = {name: list(values) for name, values in baseline.items()}
        current["temperature_2m"] = [0.1, 1.0]
        current["relative_humidity_2m"] = [1.0, 1.0]
        current["vapor_pressure_deficit"] = [0.01, 1.0]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "era5_2023_njombe_penja_pepper.json").write_text(
                json.dumps({"hourly": baseline}), encoding="utf-8"
            )
            with patch.object(multiyear, "WP1", root):
                result = multiyear.check_2023_baseline(site, current)

        variables = result["variables"]
        self.assertTrue(variables["temperature_2m"]["within_tolerance"])
        self.assertEqual(variables["temperature_2m"]["different_samples"], 1)
        self.assertTrue(variables["relative_humidity_2m"]["within_tolerance"])
        self.assertTrue(variables["vapor_pressure_deficit"]["within_tolerance"])

    def test_parity_policy_rejects_excess_or_unapproved_drift(self) -> None:
        baseline = {name: [0.0, 1.0] for name in multiyear.HOURLY}
        penja = {name: list(values) for name, values in baseline.items()}
        penja["temperature_2m"] = [0.101, 1.0]
        coffee = {name: list(values) for name, values in baseline.items()}
        coffee["temperature_2m"] = [1e-9, 1.0]

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for site_key in ("njombe_penja_pepper", "foumbot_coffee"):
                (root / f"era5_2023_{site_key}.json").write_text(
                    json.dumps({"hourly": baseline}), encoding="utf-8"
                )
            with patch.object(multiyear, "WP1", root):
                with self.assertRaises(ValueError):
                    multiyear.check_2023_baseline(
                        {"site_key": "njombe_penja_pepper"}, penja
                    )
                with self.assertRaises(ValueError):
                    multiyear.check_2023_baseline(
                        {"site_key": "foumbot_coffee"}, coffee
                    )


if __name__ == "__main__":
    unittest.main()
