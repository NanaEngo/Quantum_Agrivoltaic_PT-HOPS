#!/usr/bin/env python3
"""
WP5c -- Convergence and seed-stability diagnostics for the WP5 Saltelli/Jansen Sobol run.

The published WP5 uncertainty analysis reports indices from a single scrambled
Sobol sequence (N = 10 000 base draws, seed 42). A single sequence cannot show
whether the reported indices are stable under the sampling they summarize, so
this script reuses ``wp5_tea_lca_sobol.run_sobol_qmc`` unchanged and repeats it
on a resolution ladder (N = 1250, 2500, 5000, 10000) crossed with three
independent scrambles (seeds 42, 1234, 2024) for each crop.

Reported quantities, per crop:

* ``N_ladder``      : total-order indices of the three hardware drivers on
                      ΔNPV at fixed seed, plus P(ΔNPV > 0), across N.
* ``seed_spread``   : min/median/max of the same quantities across the three
                      scrambles at the published N = 10 000.

These ranges are sampling diagnostics for a quasi-Monte Carlo estimator. They
are not confidence intervals for a population parameter and carry no
probabilistic interpretation about future deployments.

Output: ``data/wp5/wp5_sobol_convergence.json``.

Run: ``python3 scripts/wp5c_sobol_convergence.py``
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import wp5_tea_lca_sobol as w

LADDER_N = (1250, 2500, 5000, 10000)
SEEDS = (42, 1234, 2024)
LADDER_SEED = 42

DRIVERS = ("c_mod_opv_usd_m2", "t80_opv_yr", "c_bos_si_usd_m2")
QUANTUM = "eta_ness_shift_pct"


def _extract(result: dict[str, Any]) -> dict[str, float]:
    """Pull the reported indices and exceedance probability out of one run."""
    sd = result["sobol_delta_npv_opv_vs_csi"]
    st = result["delta_npv_opv_minus_csi_stats_usd_ha"]
    out = {
        "prob_opv_beats_csi": float(st["prob_opv_beats_csi"]),
        "delta_npv_p50_usd_ha": float(st["p50"]),
        "quantum_S_Ti_delta_npv": float(sd[QUANTUM]["S_Ti"]),
    }
    for d in DRIVERS:
        out[f"{d}_S_Ti"] = float(sd[d]["S_Ti"])
    return out


def main() -> None:
    cfg = w.load_yaml(w.PARAMS_PATH)
    rows = w.load_wp3_scenarios(w.WP3_CSV_PATH)
    opv = {r["crop"]: r for r in rows if r["scenario_id"] == "S3_OPV_APT44_GCR65"}
    csi = {r["crop"]: r for r in rows if r["scenario_id"] == "S2_cSi_GCR40"}
    n_pub = int(cfg["monte_carlo"]["n_samples"])

    out: dict[str, Any] = {
        "n_published": n_pub,
        "ladder_n": list(LADDER_N),
        "seeds": list(SEEDS),
        "n_params": 12,
        "note": (
            "Sampling diagnostics for a scrambled quasi-Monte Carlo Sobol estimator; "
            "not confidence intervals and not probabilities of future outcomes."
        ),
        "crops": {},
    }

    for crop in cfg["crops"]:
        ladder: dict[str, dict[str, float]] = {}
        for n in LADDER_N:
            ladder[str(n)] = _extract(
                w.run_sobol_qmc(crop, cfg, opv[crop], csi[crop], n_samples=n, seed=LADDER_SEED)
            )

        per_seed: dict[str, dict[str, float]] = {}
        for seed in SEEDS:
            per_seed[str(seed)] = _extract(
                w.run_sobol_qmc(crop, cfg, opv[crop], csi[crop], n_samples=n_pub, seed=seed)
            )

        keys = list(per_seed[str(SEEDS[0])].keys())
        spread = {}
        for k in keys:
            vals = np.array([per_seed[str(s)][k] for s in SEEDS], dtype=np.float64)
            spread[k] = {
                "min": float(vals.min()),
                "median": float(np.median(vals)),
                "max": float(vals.max()),
                "abs_spread": float(vals.max() - vals.min()),
            }

        out["crops"][crop] = {
            "N_ladder": ladder,
            "seed_runs": per_seed,
            "seed_spread": spread,
        }
        print(crop, json.dumps(spread["prob_opv_beats_csi"]))

    dest = Path(w.WP5_DIR) / "wp5_sobol_convergence.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
