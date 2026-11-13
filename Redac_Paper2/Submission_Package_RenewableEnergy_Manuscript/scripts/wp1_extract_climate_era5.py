#!/usr/bin/env python3
"""WP1 Climate Extraction: Process Open-Meteo ERA5 2023 (8760h) hourly datasets for Foumbot, Djuttitsa, and Njombe-Penja."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WP1 = ROOT / "data" / "wp1"

SITES = {
    "foumbot_coffee": "era5_2023_foumbot_coffee.json",
    "djuttitsa_tea": "era5_2023_djuttitsa_tea.json",
    "njombe_penja_pepper": "era5_2023_njombe_penja_pepper.json",
}

WET_MONTHS = {6, 7, 8, 9, 10}
DRY_MONTHS = {12, 1, 2}


def summarize_subset(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {}
    t_vals = [r["temperature_2m"] for r in rows]
    rh_vals = [r["relative_humidity_2m"] for r in rows]
    vpd_vals = [r["vapor_pressure_deficit"] for r in rows]
    wind_vals = [r["wind_speed_10m"] for r in rows]
    sw_vals = [r["shortwave_radiation"] for r in rows]
    diff_vals = [r["diffuse_radiation"] for r in rows]
    dir_vals = [r["direct_radiation"] for r in rows]
    precip_sum = sum(r["precipitation"] for r in rows)
    daylight_rows = [r for r in rows if r["shortwave_radiation"] > 10.0]
    day_vpd = [r["vapor_pressure_deficit"] for r in daylight_rows]
    day_wind_ms = [r["wind_speed_10m"] / 3.6 for r in daylight_rows]  # Open-Meteo wind_speed_10m is km/h unless specified -> check units!
    days = n / 24.0
    total_sw = sum(sw_vals)
    total_diff = sum(diff_vals)
    total_dir = sum(dir_vals)
    return {
        "hours": n,
        "days": round(days, 1),
        "t_mean_c": round(sum(t_vals) / n, 2),
        "t_min_c": round(min(t_vals), 2),
        "t_max_c": round(max(t_vals), 2),
        "rh_mean_pct": round(sum(rh_vals) / n, 2),
        "vpd_mean_kpa": round(sum(vpd_vals) / n, 3),
        "vpd_day_mean_kpa": round(sum(day_vpd) / len(day_vpd), 3) if day_vpd else 0.0,
        "vpd_p95_kpa": round(sorted(vpd_vals)[int(0.95 * (n - 1))], 3),
        "vpd_max_kpa": round(max(vpd_vals), 3),
        "ghi_kwh_m2_day": round((total_sw / 1000.0) / days, 3),
        "ghi_kwh_m2_yr_or_period": round(total_sw / 1000.0, 1),
        "diffuse_fraction": round(total_diff / total_sw, 4) if total_sw > 0 else 0.0,
        "direct_fraction": round(total_dir / total_sw, 4) if total_sw > 0 else 0.0,
        "precip_mm": round(precip_sum, 1),
        "wind_mean_kmh": round(sum(wind_vals) / n, 2),
        "wind_day_mean_ms": round(sum(day_wind_ms) / len(day_wind_ms), 2) if day_wind_ms else 0.0,
    }


def main() -> None:
    summary = {}
    for site, fname in SITES.items():
        fpath = WP1 / fname
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        h = data["hourly"]
        units = data.get("hourly_units", {})
        times = h["time"]
        if len(times) != 8760:
            raise RuntimeError(f"{site}: expected 8760 hours, got {len(times)}")

        cols = [
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
        ]
        rows = []
        csv_path = WP1 / f"climate_{site}_2023.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as cf:
            writer = csv.writer(cf)
            writer.writerow(cols)
            for i in range(len(times)):
                rec = {c: (times[i] if c == "time" else float(h[c][i])) for c in cols}
                rows.append(rec)
                writer.writerow([rec[c] for c in cols])

        wet_rows = [r for r in rows if int(r["time"][5:7]) in WET_MONTHS]
        dry_rows = [r for r in rows if int(r["time"][5:7]) in DRY_MONTHS]
        summary[site] = {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "elevation_m": data.get("elevation"),
            "units": units,
            "annual": summarize_subset(rows),
            "wet_jun_oct": summarize_subset(wet_rows),
            "dry_dec_feb": summarize_subset(dry_rows),
        }
        a = summary[site]["annual"]
        w = summary[site]["wet_jun_oct"]
        d = summary[site]["dry_dec_feb"]
        print(
            f"{site}: elev={data.get('elevation')} m | "
            f"T={a['t_mean_c']} C [{a['t_min_c']}, {a['t_max_c']}] | "
            f"GHI={a['ghi_kwh_m2_day']} kWh/m2/d | "
            f"f_diff ann={a['diffuse_fraction']:.3f} (wet={w['diffuse_fraction']:.3f}, dry={d['diffuse_fraction']:.3f}) | "
            f"VPD_day={a['vpd_day_mean_kpa']} (dry p95={d['vpd_p95_kpa']}, max={a['vpd_max_kpa']}) kPa | "
            f"rain={a['precip_mm']} mm | wind_u10={a['wind_day_mean_ms']} m/s | units_wind={units.get('wind_speed_10m')}"
        )

    with open(WP1 / "climate_summary_2023.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()
