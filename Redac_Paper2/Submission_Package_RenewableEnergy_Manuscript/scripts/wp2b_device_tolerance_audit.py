#!/usr/bin/env python3
"""
WP2b -- Device-fabrication and angular-acceptance audit of the focal ST-OPV stack.

Mitigation item M9 asks for independent optical/device checks of the modelled PM6:Y6 stack.
An independent measurement cannot be run here, so this script instead quantifies what such a
measurement would have to reproduce and how far the modelled autarkic performance moves under
credible fabrication spread. It answers three questions:

1. *Thickness tolerance.* With layer thicknesses drawn from plausible roll-to-roll spreads
   (active layer sigma 5 %, Ag sigma 1 nm, capping MoO3 sigma 2 nm), how wide are the APT, PCE and
   LUE distributions around the focal APT44 design?
2. *One-at-a-time sensitivity.* Which layer dominates that spread?
3. *Angular acceptance.* How do APT and PCE fall with incidence angle, i.e. what beam/diffuse
   contrast must a gonioscopic measurement resolve?

Everything is evaluated with the same transfer-matrix engine and the same IQE calibration as the
published WP2 sweep (``wp2_tmm_opv``), so the numbers are directly comparable to
``data/wp2/tmm_pareto_opv.csv``. Photon conservation is re-checked on every evaluation.

Output: ``data/wp2/wp2_device_tolerance.json``
Run:    ``python3 scripts/wp2b_device_tolerance_audit.py``
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import wp2_tmm_opv as w

FOCAL = {"d_act_nm": 60.0, "d_ag_nm": 12.0, "d_cap_nm": 35.0}
SPREAD = {"d_act_nm": (60.0, 3.0), "d_ag_nm": (12.0, 1.0), "d_cap_nm": (35.0, 2.0)}
N_MC = 4000
SEED = 42
ANGLES_DEG = (0.0, 30.0, 45.0, 60.0, 75.0)
IQE_USED = 0.96  # as recorded in data/wp2/tmm_validation_summary.json


def _metrics(data: dict, d_act: float, d_ag: float, d_cap: float, theta: float) -> dict[str, float]:
    res = w.simulate_opv_exact_snell(data, d_act, d_ag, d_cap, theta_air_deg=theta)
    met = w.compute_spectral_metrics(data["wavelength_nm"], data["AM15G_W_m2_nm"], res, d_act, iqe=IQE_USED)
    conservation = float(
        np.max(np.abs(res["T"] + res["R"] + res["A_total"] - 1.0))
    )
    out = {
        "apt_par_pct": 100.0 * float(met["apt_par"]),
        "pce_pct": float(met["pce_pct"]),
        "lue_pct": float(met["lue_pct"]),
        "epar_ratio": float(met["epar_ratio"]),
        "conservation_error": conservation,
    }
    return out


def _summary(vals: np.ndarray) -> dict[str, float]:
    return {
        "p05": float(np.percentile(vals, 5)),
        "p50": float(np.percentile(vals, 50)),
        "p95": float(np.percentile(vals, 95)),
        "min": float(vals.min()),
        "max": float(vals.max()),
        "sd": float(vals.std(ddof=1)),
    }


def main() -> None:
    cfg = w.load_yaml(w.PKG_ROOT / "parameters.yaml")
    data = w.load_optical_dataset(w.PKG_ROOT / cfg["opv_technology"]["optical_nk_dataset"])

    nominal = _metrics(data, FOCAL["d_act_nm"], FOCAL["d_ag_nm"], FOCAL["d_cap_nm"], 0.0)

    # --- one-at-a-time tolerance probes (2 sigma) -------------------------------
    oat: dict[str, Any] = {}
    for key, (mu, sigma) in SPREAD.items():
        for sign, label in ((-1.0, "low"), (+1.0, "high")):
            args = dict(FOCAL)
            args[key] = mu + sign * 2.0 * sigma
            m = _metrics(data, args["d_act_nm"], args["d_ag_nm"], args["d_cap_nm"], 0.0)
            oat[f"{key}_2sigma_{label}"] = {
                "value_nm": round(args[key], 3),
                "apt_par_pct": round(m["apt_par_pct"], 3),
                "pce_pct": round(m["pce_pct"], 3),
                "lue_pct": round(m["lue_pct"], 3),
                "delta_apt_pp": round(m["apt_par_pct"] - nominal["apt_par_pct"], 3),
                "delta_pce_pp": round(m["pce_pct"] - nominal["pce_pct"], 3),
            }

    # --- correlated Monte Carlo over the fabrication spread --------------------
    rng = np.random.default_rng(SEED)
    draw = np.column_stack([
        rng.normal(SPREAD["d_act_nm"][0], SPREAD["d_act_nm"][1], N_MC),
        rng.normal(SPREAD["d_ag_nm"][0], SPREAD["d_ag_nm"][1], N_MC),
        rng.normal(SPREAD["d_cap_nm"][0], SPREAD["d_cap_nm"][1], N_MC),
    ])
    # Physical floors applied per layer; a global clip would also clamp the Ag and capping
    # columns and silently inflate their thickness.
    draw[:, 0] = np.clip(draw[:, 0], 40.0, None)
    draw[:, 1] = np.clip(draw[:, 1], 4.0, None)
    draw[:, 2] = np.clip(draw[:, 2], 0.0, None)
    apt, pce, lue, cons = [], [], [], []
    for d_act, d_ag, d_cap in draw:
        m = _metrics(data, float(d_act), float(d_ag), float(d_cap), 0.0)
        apt.append(m["apt_par_pct"]); pce.append(m["pce_pct"])
        lue.append(m["lue_pct"]); cons.append(m["conservation_error"])

    mc = {
        "n_draws": N_MC,
        "seed": SEED,
        "spread": {k: {"mean_nm": v[0], "sigma_nm": v[1]} for k, v in SPREAD.items()},
        "apt_par_pct": _summary(np.array(apt)),
        "pce_pct": _summary(np.array(pce)),
        "lue_pct": _summary(np.array(lue)),
        "max_conservation_error": float(max(cons)),
    }

    # --- angular acceptance ---------------------------------------------------
    ang = {}
    for theta in ANGLES_DEG:
        m = _metrics(data, FOCAL["d_act_nm"], FOCAL["d_ag_nm"], FOCAL["d_cap_nm"], theta)
        ang[f"{theta:g}"] = {
            "apt_par_pct": round(m["apt_par_pct"], 3),
            "pce_pct": round(m["pce_pct"], 3),
            "lue_pct": round(m["lue_pct"], 3),
        }

    out = {
        "focal_stack": FOCAL,
        "stack_architecture": cfg["opv_technology"]["stack_architecture"],
        "iqe_used": IQE_USED,
        "nominal": {k: round(v, 6) if isinstance(v, float) else v for k, v in nominal.items()},
        "one_at_a_time_2sigma": oat,
        "monte_carlo": mc,
        "angular_acceptance": ang,
        "note": (
            "Thickness spreads are illustrative fabrication tolerances, not measured line "
            "statistics; they define the reproducibility a laboratory check must meet, not a "
            "process capability claim."
        ),
    }

    dest = Path(w.DATA_WP2) / "wp2_device_tolerance.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("nominal", "monte_carlo", "angular_acceptance")}, indent=2))
    print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
