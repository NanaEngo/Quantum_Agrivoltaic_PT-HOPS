#!/usr/bin/env python3
"""WP2 Unit & Physical Verification Suite (TMM ST-OPV + LHCII Quantum NESS + HEOM)."""

import csv
import json
import sys
import unittest
from pathlib import Path

import numpy as np

PKG_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PKG_ROOT / "scripts"
DATA_WP2 = PKG_ROOT / "data" / "wp2"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import wp2_tmm_opv as tmm  # noqa: E402
import wp2_quantum_ness as qn  # noqa: E402


class TestWP2TMMAndQuantum(unittest.TestCase):
    def test_tmm_photon_conservation_and_angles(self):
        cfg = tmm.load_yaml(PKG_ROOT / "parameters.yaml")
        data = tmm.load_optical_dataset(PKG_ROOT / cfg["opv_technology"]["optical_nk_dataset"])
        for ang in (0.0, 30.0, 60.0):
            res = tmm.simulate_opv_exact_snell(data, d_act_nm=60.0, d_ag_nm=10.0, d_cap_nm=20.0, theta_air_deg=ang)
            tot = res["T"] + res["R"] + res["A_total"]
            self.assertLess(np.max(np.abs(tot - 1.0)), 1e-11, f"Energy conservation failed at theta={ang}")
            self.assertTrue(np.all(res["T"] >= -1e-12))
            self.assertTrue(np.all(res["R"] >= -1e-12))
            self.assertTrue(np.all(res["A_active"] >= -1e-12))
            self.assertTrue(np.all(res["A_active"] <= res["A_total"] + 1e-10))

    def test_tmm_pareto_outputs_and_monotonicity(self):
        csv_path = DATA_WP2 / "tmm_pareto_opv.csv"
        npz_path = DATA_WP2 / "tmm_spectral_library.npz"
        sum_path = DATA_WP2 / "tmm_validation_summary.json"
        self.assertTrue(csv_path.exists())
        self.assertTrue(npz_path.exists())
        self.assertTrue(sum_path.exists())

        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        pareto = sorted([r for r in rows if int(r["is_pareto_all"]) == 1], key=lambda x: float(x["apt_par"]))
        self.assertGreaterEqual(len(pareto), 10)
        for i in range(len(pareto) - 1):
            self.assertGreater(float(pareto[i]["pce_pct"]), float(pareto[i + 1]["pce_pct"]))

        summary = json.loads(sum_path.read_text(encoding="utf-8"))
        self.assertLess(summary["max_energy_conservation_error"], 1e-12)
        pce_75 = summary["opaque_validation"]["opaque_75nm"]["pce_pct"]
        self.assertTrue(14.5 <= pce_75 <= 16.5, f"Unexpected 75nm opaque PCE: {pce_75}")

    def test_detailed_balance_and_achromatic_neutrality(self):
        ham_data = json.loads((PKG_ROOT / "data" / "wp1" / "lhcii_hamiltonians_14site.json").read_text(encoding="utf-8"))
        H2 = np.asarray(ham_data["hamiltonians_cm1"]["H2_Muh2010_diag_PDA"], dtype=np.float64)
        temp_k = 295.0
        evals, _, W = qn.build_eet_rate_matrix(H2, lam_dl=50.87, gamma_dl=50.0, temp_k=temp_k)
        kT = qn.KB_CM1_PER_K * temp_k
        for i in range(14):
            for j in range(i + 1, 14):
                if W[j, i] > 1e-12 and W[i, j] > 1e-12:
                    ratio_calc = W[j, i] / W[i, j]
                    ratio_exact = np.exp((evals[i] - evals[j]) / kT)
                    self.assertAlmostEqual(ratio_calc / ratio_exact, 1.0, places=6)

    def test_quantum_ness_summary_and_heom(self):
        qsum_path = DATA_WP2 / "quantum_ness_summary.json"
        qcsv_path = DATA_WP2 / "quantum_ness_spectra_matrix.csv"
        self.assertTrue(qsum_path.exists(), "quantum_ness_summary.json not generated yet")
        self.assertTrue(qcsv_path.exists())

        qsum = json.loads(qsum_path.read_text(encoding="utf-8"))
        self.assertEqual(len(qsum["hamiltonians"]), 3)
        for h_name, hres in qsum["hamiltonians"].items():
            r_am = hres["open_rc_no_npq"]["AM15G_full_sun"]
            r_csi = hres["open_rc_no_npq"]["Neutral_cSi_40pct"]
            self.assertTrue(0.70 <= r_am["eta_partial_secular_mean"] <= 0.99, f"{h_name} eta out of range")
            # Achromatic attenuation keeps quantum efficiency per absorbed photon invariant
            self.assertLess(
                abs(r_csi["eta_partial_secular_mean"] - r_am["eta_partial_secular_mean"]),
                1e-9,
                f"Neutral c-Si changed eta in {h_name}",
            )

        for hv_key in ("heom_validation_H2", "heom_validation_H3"):
            hv = qsum[hv_key]
            self.assertLess(hv["abs_eta_error"], 0.05, f"HEOM vs Redfield-Forster error too high in {hv_key}")

    def test_mesohops_14site_hpc_benchmark(self):
        mh_path = DATA_WP2 / "mesohops_hpc_benchmark.json"
        self.assertTrue(mh_path.exists(), "mesohops_hpc_benchmark.json not found")
        mh = json.loads(mh_path.read_text(encoding="utf-8"))
        self.assertEqual(mh["mesohops_mode"], "production_benchmark")
        results = mh["results"]
        for key in (
            "H2_Muh2010_diag_PDA_DL_K1",
            "H3_MMSIC_MD_2025_full_DL_K1",
            "H3_MMSIC_MD_2025_full_DL_K1_Vib340",
        ):
            self.assertIn(key, results)
            entry = results[key]
            self.assertEqual(entry["n_sites"], 14)
            self.assertLess(entry["max_norm_deviation"], 1e-12)
            self.assertTrue(0.0 < entry["p_terminal_final_hops"] < 1.0)
        self.assertLess(results["H2_Muh2010_diag_PDA_DL_K1"]["terminal_mae_0_tmax"], 0.05)


    def test_device_tolerance_audit(self):
        """Fabrication-tolerance audit reproduces the nominal stack and stays in tolerance (M9)."""
        path = DATA_WP2 / "wp2_device_tolerance.json"
        self.assertTrue(path.exists(), "wp2_device_tolerance.json missing (run wp2b_device_tolerance_audit.py)")
        d = json.loads(path.read_text(encoding="utf-8"))
        nom = d["nominal"]
        # Nominal evaluation must reproduce the published focal-stack numbers.
        self.assertAlmostEqual(nom["apt_par_pct"], 44.118, places=2)
        self.assertAlmostEqual(nom["pce_pct"], 9.927, places=2)
        self.assertLess(nom["conservation_error"], 1e-12)
        mc = d["monte_carlo"]
        self.assertEqual(mc["n_draws"], 4000)
        self.assertLess(mc["max_conservation_error"], 1e-12)
        # Distribution must bracket the nominal value and stay physically bounded.
        self.assertLess(mc["apt_par_pct"]["p05"], mc["apt_par_pct"]["p50"])
        self.assertLess(mc["apt_par_pct"]["p50"], mc["apt_par_pct"]["p95"])
        self.assertGreater(mc["apt_par_pct"]["min"], 0.0)
        self.assertLess(mc["apt_par_pct"]["max"], 100.0)
        # LUE must be far stiffer than APT under the same thickness spread: relative SD
        # stays below 2 % for LUE while APT exceeds 4 %.
        rel_sd_lue = mc["lue_pct"]["sd"] / nom["lue_pct"]
        rel_sd_apt = mc["apt_par_pct"]["sd"] / nom["apt_par_pct"]
        self.assertLess(rel_sd_lue, 0.02, msg=f"LUE relative SD too large: {rel_sd_lue}")
        self.assertGreater(rel_sd_apt, 0.04, msg=f"APT relative SD expected larger: {rel_sd_apt}")
        # Angular decay must be monotone over the sampled angles.
        ang = d["angular_acceptance"]
        seq = [ang[k]["apt_par_pct"] for k in ("0", "30", "45", "60", "75")]
        self.assertTrue(all(a > b for a, b in zip(seq, seq[1:])), f"APT not monotone with angle: {seq}")
        for k, v in ang.items():
            self.assertGreater(v["pce_pct"], 0.0, msg=f"non-positive PCE at {k} deg")


if __name__ == "__main__":
    unittest.main(verbosity=2)
