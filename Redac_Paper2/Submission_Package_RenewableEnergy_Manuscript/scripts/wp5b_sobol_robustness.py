#!/usr/bin/env python3
"""
WP5b -- Adversarial robustness checks on the WP5 Saltelli/Jansen Sobol analysis.

Re-evaluates ``wp5_tea_lca_sobol.run_sobol_qmc`` (same seed, same N) under four
uncertainty-set variants, WITHOUT modifying the published WP5 outputs:

* ``published``   : as in WP5 (quantum lever ``eta_ness_shift_pct`` in [-0.02, 0.10] %,
                    carbon price in [0, 25] USD/tCO2e).
* ``heom_envelope``: quantum lever widened to +/-0.21 %, i.e. the exact 4-site
                    QuTiP-BoFiN HEOM-vs-Pauli efficiency gap |eta_HEOM - eta_Pauli| = 2.10e-3 (H2),
                    roughly 60x the Bloch--Redfield NESS bound (3.37e-5).
* ``zero_carbon`` : carbon price pinned to 0 USD/tCO2e (strict zero-carbon Monte Carlo).
* ``heom_zero_carbon``: both.

Output: ``data/wp5/wp5_sobol_robustness.json``.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import wp5_tea_lca_sobol as w

Q_ORIG = '("eta_ness_shift_pct", -0.02, 0.10)'
C_ORIG = '("carbon_price_usd_t", 0.0, 25.0)'
Q_HEOM = '("eta_ness_shift_pct", -0.21, 0.21)'
C_ZERO = '("carbon_price_usd_t", 0.0, 0.0)'


def _variant_sources() -> dict[str, str]:
    src = inspect.getsource(w.run_sobol_qmc)
    if Q_ORIG not in src or C_ORIG not in src:
        raise RuntimeError("WP5 parameter specification changed; update wp5b_sobol_robustness.py")
    return {
        "published": src,
        "heom_envelope": src.replace(Q_ORIG, Q_HEOM),
        "zero_carbon": src.replace(C_ORIG, C_ZERO),
        "heom_zero_carbon": src.replace(Q_ORIG, Q_HEOM).replace(C_ORIG, C_ZERO),
    }


def main() -> None:
    cfg = w.load_yaml(w.PARAMS_PATH)
    rows = w.load_wp3_scenarios(w.WP3_CSV_PATH)
    opv = {r["crop"]: r for r in rows if r["scenario_id"] == "S3_OPV_APT44_GCR65"}
    csi = {r["crop"]: r for r in rows if r["scenario_id"] == "S2_cSi_GCR40"}
    n = int(cfg["monte_carlo"]["n_samples"])
    seed = int(cfg["monte_carlo"]["random_seed"])

    out: dict[str, Any] = {"n_base_samples": n, "seed": seed, "n_params": 12,
                           "model_evaluations_per_crop": n * (12 + 2), "variants": {}}
    for name, src in _variant_sources().items():
        ns: dict[str, Any] = dict(vars(w))
        exec(compile(src, f"<wp5b:{name}>", "exec"), ns)  # noqa: S102 - controlled local source
        fn = ns["run_sobol_qmc"]
        out["variants"][name] = {}
        for crop in cfg["crops"]:
            r = fn(crop, cfg, opv[crop], csi[crop], n_samples=n, seed=seed)
            sd = r["sobol_delta_npv_opv_vs_csi"]
            so = r["sobol_npv_opv"]
            st = r["delta_npv_opv_minus_csi_stats_usd_ha"]
            out["variants"][name][crop] = {
                "prob_opv_beats_csi": st["prob_opv_beats_csi"],
                "delta_npv_p50_usd_ha": st["p50"],
                "quantum_S_Ti_delta_npv": sd["eta_ness_shift_pct"]["S_Ti"],
                "quantum_S_Ti_npv_opv": so["eta_ness_shift_pct"]["S_Ti"],
                "c_mod_opv_S_Ti_delta_npv": sd["c_mod_opv_usd_m2"]["S_Ti"],
                "t80_opv_S_Ti_delta_npv": sd["t80_opv_yr"]["S_Ti"],
                "c_bos_si_S_Ti_delta_npv": sd["c_bos_si_usd_m2"]["S_Ti"],
            }
            print(name, crop, json.dumps(out["variants"][name][crop]))

    dest = Path(w.WP5_DIR) / "wp5_sobol_robustness.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
