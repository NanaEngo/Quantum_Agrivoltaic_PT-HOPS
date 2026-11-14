#!/usr/bin/env python3
"""
WP1b -- Site wind statistics and structural-load screening for the three modelled sites.

Mitigation item M9 asks for locally relevant wind/load/contractor evidence for the elevated
structures. Such evidence cannot be obtained from this package, and a design wind speed must not be
invented. This script therefore does two limited, auditable things:

1. Extracts what the shipped 2023 ERA5 record *does* contain about wind at each site (hourly 10 m
   means): annual and seasonal means, percentiles, and the record maximum. These are ordinary
   operating statistics, not design values; hourly means systematically understate gusts.
2. Reports the dynamic pressure 0.5 rho v^2 across a *range* of candidate basic wind speeds, so the
   load class a local annex supplies can be read off directly instead of being assumed.

Output: ``data/wp1/wind_load_screening.json``
Run:    ``python3 scripts/wp1_wind_load_screening.py``
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

PKG_ROOT = Path(__file__).resolve().parent.parent
DATA_WP1 = PKG_ROOT / "data" / "wp1"

SITES = {
    "foumbot_coffee": "climate_foumbot_coffee_2023.csv",
    "njombe_penja_pepper": "climate_njombe_penja_pepper_2023.csv",
    "djuttitsa_tea": "climate_djuttitsa_tea_2023.csv",
}
AIR_DENSITY = 1.25  # kg/m3, EN 1991-1-4 default
CANDIDATE_VB_MS = (20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0)


def _read_kmh(path: Path) -> np.ndarray:
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return np.array([float(r["wind_speed_10m"]) for r in rows], dtype=np.float64) / 3.6


def main() -> None:
    out: dict[str, Any] = {
        "source": "ERA5 hourly 10 m wind speed, 2023 (data/wp1/climate_*_2023.csv)",
        "caveat": (
            "Hourly means, not 10-min means or gusts. They describe ordinary operating wind at the "
            "sites and cannot supply a basic wind velocity v_b,0, which requires the national annex "
            "map, a terrain category and an orography factor."
        ),
        "dynamic_pressure": {
            "formula": "q_p = 0.5 * rho * v^2, rho = 1.25 kg/m3",
            "table_Pa": {
                f"{v:g}": round(0.5 * AIR_DENSITY * v**2, 1) for v in CANDIDATE_VB_MS
            },
        },
        "sites": {},
    }

    for site, fname in SITES.items():
        v = _read_kmh(DATA_WP1 / fname)
        n = v.size
        wet = v[5 * 730: 10 * 730] if n >= 10 * 730 else v
        out["sites"][site] = {
            "hours": int(n),
            "mean_ms": round(float(v.mean()), 3),
            "p50_ms": round(float(np.percentile(v, 50)), 3),
            "p95_ms": round(float(np.percentile(v, 95)), 3),
            "p99_ms": round(float(np.percentile(v, 99)), 3),
            "max_ms": round(float(v.max()), 3),
            "wet_season_mean_ms": round(float(wet.mean()), 3),
            "hours_above_10ms": int((v > 10.0).sum()),
            "hours_above_15ms": int((v > 15.0).sum()),
            "q_at_record_max_Pa": round(0.5 * AIR_DENSITY * float(v.max()) ** 2, 1),
        }

    dest = DATA_WP1 / "wind_load_screening.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out["sites"], indent=2))
    print(json.dumps(out["dynamic_pressure"], indent=2))
    print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
