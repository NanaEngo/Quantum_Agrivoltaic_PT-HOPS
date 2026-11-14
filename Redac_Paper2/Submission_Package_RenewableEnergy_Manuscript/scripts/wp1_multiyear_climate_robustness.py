#!/usr/bin/env python3
"""Fetch and model-check a separate 2014–2023 ERA5 weather-year ensemble.

The submission's 2023 inputs/configuration remain the canonical baseline. This
script stores annual Open-Meteo Archive responses separately, checks each year
for completeness and checks the fetched 2023 arrays against the saved baseline.
With the default behavior it then runs WP3 into a separate per-year output tree.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import yaml

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
WP1 = PACKAGE_ROOT / "data" / "wp1"
OUTPUT = WP1 / "multiyear_2014_2023"
WP3_OUTPUT = PACKAGE_ROOT / "data" / "wp3" / "multiyear_2014_2023"
API = "https://archive-api.open-meteo.com/v1/archive"
TIMEZONE = "Africa/Douala"
WIND_UNIT = "kmh"
HOURLY = (
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "shortwave_radiation",
    "direct_radiation",
    "diffuse_radiation",
    "terrestrial_radiation",
    "vapor_pressure_deficit",
)
CSV_FIELDS = ("time", *HOURLY)
SITE_FOR_CROP = {
    "arabica_coffee": "foumbot_coffee",
    "penja_white_pepper": "njombe_penja_pepper",
    "highland_tea": "djuttitsa_tea",
}


def expected_hour_count(year: int) -> int:
    """Return the number of hourly samples in a Gregorian calendar year."""
    return 8784 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 8760


def expected_times(year: int) -> list[str]:
    start = datetime(year, 1, 1)
    return [
        (start + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M")
        for i in range(expected_hour_count(year))
    ]


def validate_hourly(year: int, hourly: dict[str, list[Any]]) -> None:
    """Reject incomplete, duplicated, non-finite, or physically invalid years."""
    times = hourly.get("time", [])
    expected = expected_times(year)
    if times != expected:
        raise ValueError(
            f"{year}: timestamps are incomplete, duplicated, unordered, or not hourly "
            f"({len(times)} received, {len(expected)} expected)"
        )
    for name in HOURLY:
        values = hourly.get(name)
        if values is None or len(values) != len(expected):
            raise ValueError(f"{year}: missing or mis-sized hourly variable {name}")
        if any(value is None or not math.isfinite(float(value)) for value in values):
            raise ValueError(f"{year}: missing or non-finite value in {name}")
    ghi = hourly["shortwave_radiation"]
    diffuse = hourly["diffuse_radiation"]
    if any(float(v) < 0 for v in ghi) or any(float(v) < 0 for v in diffuse):
        raise ValueError(f"{year}: negative shortwave or diffuse radiation")
    if any(float(d) > float(g) + 2.0 for g, d in zip(ghi, diffuse, strict=True)):
        raise ValueError(f"{year}: diffuse radiation exceeds GHI by more than 2 W/m²")


def fetch_year(site: dict[str, Any], year: int) -> tuple[dict[str, Any], dict[str, list[Any]]]:
    params = {
        "latitude": site["latitude"],
        "longitude": site["longitude"],
        "elevation": site["elevation_m"],
        "start_date": f"{year}-01-01",
        "end_date": f"{year}-12-31",
        "hourly": ",".join(HOURLY),
        "timezone": TIMEZONE,
        "wind_speed_unit": WIND_UNIT,
    }
    request = Request(f"{API}?{urlencode(params)}", headers={"User-Agent": "Agrivoltaic-Reproducibility/1.0"})
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urlopen(request, timeout=180) as response:
                payload = json.load(response)
            hourly = payload.get("hourly", {})
            validate_hourly(year, hourly)
            return payload, hourly
        except (URLError, TimeoutError) as exc:
            last_error = exc
            if attempt == 3:
                break
            import time

            time.sleep(2**attempt)
    raise RuntimeError(f"Open-Meteo request failed for {site['site_key']} {year}: {last_error}")


def summarize_site_year(hourly: dict[str, list[Any]]) -> dict[str, Any]:
    months = [int(value[5:7]) for value in hourly["time"]]
    t = [float(v) for v in hourly["temperature_2m"]]
    rh = [float(v) for v in hourly["relative_humidity_2m"]]
    vpd = [float(v) for v in hourly["vapor_pressure_deficit"]]
    precip = [float(v) for v in hourly["precipitation"]]
    wind = [float(v) for v in hourly["wind_speed_10m"]]
    ghi = [float(v) for v in hourly["shortwave_radiation"]]
    diffuse = [float(v) for v in hourly["diffuse_radiation"]]

    def summarize(indices: list[int]) -> dict[str, Any]:
        if not indices:
            raise ValueError("Cannot summarize an empty season")
        sw_sum = sum(ghi[i] for i in indices)
        return {
            "hours": len(indices),
            "temperature_mean_c": sum(t[i] for i in indices) / len(indices),
            "temperature_min_c": min(t[i] for i in indices),
            "temperature_max_c": max(t[i] for i in indices),
            "relative_humidity_mean_pct": sum(rh[i] for i in indices) / len(indices),
            "vpd_mean_kpa": sum(vpd[i] for i in indices) / len(indices),
            "vpd_p95_kpa": sorted(vpd[i] for i in indices)[int(0.95 * (len(indices) - 1))],
            "precipitation_sum_mm": sum(precip[i] for i in indices),
            "wind_mean_kmh": sum(wind[i] for i in indices) / len(indices),
            "ghi_sum_kwh_m2": sw_sum / 1000.0,
            "ghi_mean_kwh_m2_day": sw_sum / 1000.0 / (len(indices) / 24.0),
            "diffuse_fraction": sum(diffuse[i] for i in indices) / sw_sum if sw_sum else 1.0,
        }

    all_i = list(range(len(months)))
    wet_i = [i for i, month in enumerate(months) if 6 <= month <= 10]
    dry_i = [i for i, month in enumerate(months) if month in (12, 1, 2)]
    return {
        "annual": summarize(all_i),
        "wet_jun_oct": summarize(wet_i),
        "dry_dec_feb": summarize(dry_i),
    }


def write_hourly_csv(path: Path, hourly: dict[str, list[Any]]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(CSV_FIELDS)
        writer.writerows(zip(*(hourly[name] for name in CSV_FIELDS), strict=True))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def check_2023_baseline(site: dict[str, Any], hourly: dict[str, list[Any]]) -> dict[str, Any]:
    """Compare current API output with the frozen 2023 input and record bounded deltas.

    Open-Meteo's current archive response differs slightly from the saved Penja
    thermodynamic series. All other site-variable pairs remain exact-match gates.
    These tolerances document source-snapshot drift; they are not model validation.
    """
    site_key = site["site_key"]
    baseline_path = WP1 / f"era5_2023_{site_key}.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))["hourly"]
    penja_tolerances = {
        "temperature_2m": 0.1,
        "relative_humidity_2m": 1.0,
        "vapor_pressure_deficit": 0.01,
    }
    diagnostics: dict[str, Any] = {}
    for variable in HOURLY:
        old = baseline[variable]
        new = hourly[variable]
        if len(old) != len(new):
            raise ValueError(
                f"Fetched 2023 {site_key} {variable} length {len(new)} differs from baseline {len(old)}"
            )
        deltas = [abs(float(a) - float(b)) for a, b in zip(old, new, strict=True)]
        max_abs = max(deltas, default=0.0)
        mean_abs = math.fsum(deltas) / len(deltas) if deltas else 0.0
        tolerance = penja_tolerances.get(variable, 0.0) if site_key == "njombe_penja_pepper" else 0.0
        within_tolerance = (
            max_abs == 0.0 if tolerance == 0.0 else max_abs <= tolerance + 1e-12
        )
        diagnostics[variable] = {
            "max_abs_difference": max_abs,
            "mean_abs_difference": mean_abs,
            "different_samples": sum(float(a) != float(b) for a, b in zip(old, new, strict=True)),
            "tolerance": tolerance,
            "within_tolerance": within_tolerance,
        }
        if not within_tolerance:
            raise ValueError(
                f"Fetched 2023 {site_key} {variable} max |delta|={max_abs:g} "
                f"exceeds documented tolerance {tolerance:g}"
            )
    return {
        "baseline_file": baseline_path.name,
        "policy": "Exact match except bounded current-archive thermodynamic deltas for Penja; not field validation.",
        "variables": diagnostics,
    }

def prepare_year_config(config: dict[str, Any], year: int, output_dir: Path) -> Path:
    year_config = json.loads(json.dumps(config))
    year_config["microclimate"]["climate_summary_dataset"] = f"climate_summary_{year}.json"
    for crop_key, site_key in SITE_FOR_CROP.items():
        if crop_key not in year_config["crops"]:
            raise KeyError(f"Canonical parameters.yaml is missing crop {crop_key}")
        year_config["crops"][crop_key]["climate_dataset"] = f"{site_key}_{year}.csv.gz"
    path = output_dir / f"parameters_{year}.yaml"
    path.write_text(yaml.safe_dump(year_config, sort_keys=False), encoding="utf-8")
    return path


def run_wp3(config_path: Path, year: int, output_dir: Path, workers: int) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    engine = Path(__file__).with_name("wp3_microclimate_crop_engine.py")
    command = [
        sys.executable,
        str(engine),
        "--config",
        str(config_path),
        "--output-dir",
        str(output_dir),
        "--workers",
        str(workers),
        "--no-hourly",
    ]
    subprocess.run(command, cwd=PACKAGE_ROOT, check=True)
    result = output_dir / "wp3_crop_microclimate_scenarios.csv"
    if not result.is_file():
        raise FileNotFoundError(f"WP3 did not create scenario output for {year}: {result}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2014)
    parser.add_argument("--end-year", type=int, default=2023)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--climate-only", action="store_true", help="Fetch and summarize weather without running WP3")
    parser.add_argument("--reuse-existing", action="store_true", help="Reuse existing compressed annual CSVs after validation")
    args = parser.parse_args()
    if args.start_year > args.end_year or args.workers < 1:
        parser.error("Require start-year <= end-year and workers >= 1")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    canonical_config = yaml.safe_load((PACKAGE_ROOT / "parameters.yaml").read_text(encoding="utf-8"))
    baseline_summary = json.loads((WP1 / "climate_summary_2023.json").read_text(encoding="utf-8"))
    sites = {
        crop_key: {
            "crop_key": crop_key,
            "site_key": site_key,
            **baseline_summary[site_key],
        }
        for crop_key, site_key in SITE_FOR_CROP.items()
    }

    manifest: dict[str, Any] = {
        "source": "Open-Meteo Archive API (ERA5 historical reanalysis)",
        "api": API,
        "timezone": TIMEZONE,
        "wind_speed_unit": WIND_UNIT,
        "years": list(range(args.start_year, args.end_year + 1)),
        "hourly_variables": list(HOURLY),
        "sites": {},
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "warning": "Reanalysis robustness is not field validation; 2023 remains the manuscript baseline.",
    }
    climate_rows: list[dict[str, Any]] = []
    for crop_key, site in sites.items():
        manifest["sites"][crop_key] = {
            "site_key": site["site_key"],
            "latitude": site["latitude"],
            "longitude": site["longitude"],
            "elevation_m": site["elevation_m"],
            "years": {},
        }
        for year in manifest["years"]:
            csv_path = output_dir / f"{site['site_key']}_{year}.csv.gz"
            if args.reuse_existing and csv_path.is_file():
                with gzip.open(csv_path, "rt", encoding="utf-8", newline="") as stream:
                    reader = csv.DictReader(stream)
                    rows = list(reader)
                if len(rows) != expected_hour_count(year) or [r["time"] for r in rows] != expected_times(year):
                    raise ValueError(f"Existing climate file failed validation: {csv_path}")
                hourly = {name: [r[name] for r in rows] for name in CSV_FIELDS}
                for variable in HOURLY:
                    hourly[variable] = [float(v) for v in hourly[variable]]
                validate_hourly(year, hourly)
                digest = hashlib.sha256(csv_path.read_bytes()).hexdigest()
                payload = {"elevation": site["elevation_m"]}
            else:
                payload, hourly = fetch_year(site, year)
                digest = write_hourly_csv(csv_path, hourly)

            baseline_comparison = check_2023_baseline(site, hourly) if year == 2023 else None
            summary = summarize_site_year(hourly)
            climate_rows.append({"year": year, "crop": crop_key, "site": site["site_key"], **summary["annual"]})
            site_summary = {
                "latitude": site["latitude"],
                "longitude": site["longitude"],
                "elevation_m": site["elevation_m"],
                "timezone": TIMEZONE,
                "utc_offset_seconds": 3600,
                "units": baseline_summary[site["site_key"]]["units"],
                **summary,
            }
            manifest["sites"][crop_key]["years"][str(year)] = {
                "hours": len(hourly["time"]),
                "sha256_gzip_csv": digest,
                "api_elevation_m": payload.get("elevation", site["elevation_m"]),
                "file": csv_path.name,
                "summary": summary,
                "baseline_comparison": baseline_comparison,
            }
            # Worker site matching accepts crop-key strings; keep a full named record per year.
            per_year_summary_path = output_dir / f"climate_summary_{year}.json"
            if not per_year_summary_path.exists():
                per_year_summary_path.write_text("{}", encoding="utf-8")
            summary_doc = json.loads(per_year_summary_path.read_text(encoding="utf-8"))
            summary_doc[crop_key] = site_summary
            per_year_summary_path.write_text(json.dumps(summary_doc, indent=2), encoding="utf-8")

    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    with (output_dir / "climate_annual_summary.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(climate_rows[0]))
        writer.writeheader()
        writer.writerows(climate_rows)

    if not args.climate_only:
        aggregate_rows: list[dict[str, Any]] = []
        for year in manifest["years"]:
            config_path = prepare_year_config(canonical_config, year, output_dir)
            year_output = WP3_OUTPUT / str(year)
            result_path = run_wp3(config_path, year, year_output, args.workers)
            with result_path.open("r", encoding="utf-8", newline="") as stream:
                for row in csv.DictReader(stream):
                    aggregate_rows.append({"year": year, **row})

        aggregate_path = WP3_OUTPUT / "wp3_multiyear_scenario_results.csv.gz"
        aggregate_path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(aggregate_path, "wt", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(aggregate_rows[0]))
            writer.writeheader()
            writer.writerows(aggregate_rows)
        (WP3_OUTPUT / "wp3_multiyear_weather_manifest.json").write_text(
            json.dumps({"years": manifest["years"], "climate_manifest": str(output_dir / "manifest.json"), "rows": len(aggregate_rows)}, indent=2),
            encoding="utf-8",
        )
    print(json.dumps({"climate_output": str(output_dir), "wp3_output": str(WP3_OUTPUT), "years": manifest["years"], "sites": len(sites), "wp3_run": not args.climate_only}, indent=2))


if __name__ == "__main__":
    main()
