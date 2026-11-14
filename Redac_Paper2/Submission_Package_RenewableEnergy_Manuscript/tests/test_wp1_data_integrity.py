#!/usr/bin/env python3
"""WP1 Data Integrity & Physical Consistency Tests.

Verifies all primary datasets extracted in WP1 and ensures full consistency
with parameters.yaml (zero [VERIFY] placeholders remaining).
"""

import csv
import json
import unittest
from pathlib import Path

import numpy as np

try:
    import yaml

    def _load_yaml(path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
except ImportError:
    from ruamel.yaml import YAML

    def _load_yaml(path: Path) -> dict:
        y = YAML(typ="safe")
        with open(path, "r", encoding="utf-8") as f:
            return y.load(f)

PKG_ROOT = Path(__file__).resolve().parent.parent
DATA_WP1 = PKG_ROOT / "data" / "wp1"


def load_config():
    return _load_yaml(PKG_ROOT / "parameters.yaml")


class TestWP1DataIntegrity(unittest.TestCase):
    def test_parameters_yaml_no_verify_and_paths_exist(self):
        raw_text = (PKG_ROOT / "parameters.yaml").read_text(encoding="utf-8")
        self.assertNotIn("[VERIFY", raw_text, "parameters.yaml still contains unresolved [VERIFY] tags")

        cfg = load_config()
        self.assertEqual(cfg["provenance"]["framework_version"], "2.5.0")

        paths_to_check = [
            cfg["lhcii_hamiltonian"]["hamiltonian_source"],
            cfg["lhcii_hamiltonian"]["dipole_geometry_pdb"],
            cfg["opv_technology"]["optical_nk_dataset"],
            cfg["opv_technology"]["solar_spectrum_dataset"],
            cfg["microclimate"]["climate_summary_dataset"],
        ]
        for crop_cfg in cfg["crops"].values():
            paths_to_check.append(crop_cfg["climate_dataset"])

        for rel_path in paths_to_check:
            self.assertTrue((PKG_ROOT / rel_path).exists(), f"Missing referenced WP1 dataset: {rel_path}")

    def test_climate_era5_hourly_integrity(self):
        expected_cols = {
            "time",
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
            "shortwave_radiation",
            "direct_radiation",
            "diffuse_radiation",
            "terrestrial_radiation",
            "vapor_pressure_deficit",
        }
        sites = [
            "climate_foumbot_coffee_2023.csv",
            "climate_djuttitsa_tea_2023.csv",
            "climate_njombe_penja_pepper_2023.csv",
        ]
        summary = json.loads((DATA_WP1 / "climate_summary_2023.json").read_text(encoding="utf-8"))
        self.assertEqual(len(summary), 3)

        for fname in sites:
            with open(DATA_WP1 / fname, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                cols = set(reader.fieldnames or [])
                rows = list(reader)
            self.assertEqual(len(rows), 8760, f"{fname} must have 8760 hourly rows, got {len(rows)}")
            self.assertTrue(expected_cols.issubset(cols), f"Missing columns in {fname}")
            vpd = np.array([float(r["vapor_pressure_deficit"]) for r in rows])
            sw = np.array([float(r["shortwave_radiation"]) for r in rows])
            diff = np.array([float(r["diffuse_radiation"]) for r in rows])
            self.assertTrue(np.all(np.isfinite(vpd)) and np.all(vpd >= 0.0))
            self.assertTrue(np.all(np.isfinite(sw)) and np.all(sw >= 0.0))
            self.assertTrue(np.all(np.isfinite(diff)) and np.all(diff >= 0.0))
            self.assertTrue(np.all(diff <= sw + 2.0))

    def test_lhcii_hamiltonians_and_dipoles(self):
        ham = json.loads((DATA_WP1 / "lhcii_hamiltonians_14site.json").read_text(encoding="utf-8"))
        self.assertEqual(len(ham["site_order"]), 14)
        for name, mat_list in ham["hamiltonians_cm1"].items():
            mat = np.asarray(mat_list, dtype=float)
            self.assertEqual(mat.shape, (14, 14), f"{name} shape mismatch: {mat.shape}")
            self.assertTrue(np.all(np.isfinite(mat)))
            self.assertLess(np.max(np.abs(mat - mat.T)), 1e-9, f"{name} is not symmetric")
            diag = np.diag(mat)
            self.assertTrue(np.all((diag > 14000.0) & (diag < 17000.0)), f"{name} diagonal outside Qy band")

        dip = json.loads((DATA_WP1 / "lhcii_pdb_dipoles.json").read_text(encoding="utf-8"))
        for pdb_key in ("1RWT_chainA", "2BHW_chainA"):
            sites = dip[pdb_key]["sites"]
            self.assertEqual(len(sites), 14, f"{pdb_key} must have 14 Chl sites")
            for site in sites:
                u = np.asarray(site["qy_unit_vec_nb_to_nd"], dtype=float)
                self.assertLess(abs(np.linalg.norm(u) - 1.0), 1e-5, f"Non-unit dipole in {pdb_key}")

    def test_optical_nk_stack_and_am15g(self):
        with open(DATA_WP1 / "optical_nk_stack_1nm.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            nk_cols = list(reader.fieldnames or [])
            nk_rows = list(reader)
        self.assertEqual(len(nk_rows), 801, f"Expected 801 wavelength rows (300-1100 nm), got {len(nk_rows)}")
        self.assertTrue(np.isclose(float(nk_rows[0]["wavelength_nm"]), 300.0))
        self.assertTrue(np.isclose(float(nk_rows[-1]["wavelength_nm"]), 1100.0))

        for col in nk_cols:
            vals = np.array([float(r[col]) for r in nk_rows])
            self.assertTrue(np.all(np.isfinite(vals)), f"NaNs found in {col} of optical_nk_stack_1nm.csv")
            if col.endswith("_n"):
                self.assertTrue(np.all(vals > 0.0), f"Non-positive refractive index in {col}")
            if col.endswith("_k"):
                self.assertTrue(np.all(vals >= -1e-9), f"Negative extinction coefficient in {col}")

        am15 = DATA_WP1 / "ASTMG173.csv"
        self.assertTrue(am15.exists())
        self.assertGreaterEqual(len(am15.read_text(encoding="utf-8").splitlines()), 2000)


    def test_wind_load_screening_consistency(self):
        """Site wind screening stays inside the ERA5 record and its load table is monotone (M9)."""
        path = DATA_WP1 / "wind_load_screening.json"
        self.assertTrue(path.exists(), "wind_load_screening.json missing (run wp1_wind_load_screening.py)")
        d = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(len(d["sites"]), 3)
        for site, v in d["sites"].items():
            self.assertEqual(v["hours"], 8760, msg=site)
            self.assertTrue(0.0 <= v["p50_ms"] <= v["p95_ms"] <= v["p99_ms"] <= v["max_ms"], msg=site)
        q = d["dynamic_pressure"]["table_Pa"]
        keys = sorted(q, key=float)
        vals = [q[k] for k in keys]
        self.assertTrue(all(a < b for a, b in zip(vals, vals[1:])), "dynamic pressure not monotone in v")
        # The record maximum must be far below any plausible design dynamic pressure.
        record_max = max(s["q_at_record_max_Pa"] for s in d["sites"].values())
        self.assertLess(record_max, min(vals))


if __name__ == "__main__":
    unittest.main(verbosity=2)
