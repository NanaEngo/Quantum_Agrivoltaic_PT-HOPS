#!/usr/bin/env python3
"""Rebuild the focused WP5 export-acceptance sensitivity without replacing canonical outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from scripts import wp5_tea_lca_sobol as wp5

OUTPUT_DIR = PACKAGE_ROOT / "data" / "wp5"
OUTPUT_CSV = OUTPUT_DIR / "wp5_export_acceptance_sensitivity_20261114.csv"
OUTPUT_MANIFEST = OUTPUT_DIR / "wp5_export_acceptance_sensitivity_20261114.json"
FOCAL_SCENARIO = "S3_OPV_APT44_GCR65"
VARIANTS = {"baseline_zero_credit", "S5_export_acceptance_50pct", "S5_offgrid_no_export"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    """Run WP5 in a temporary output root and save only the three policy cases per crop."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    canonical_wp5_dir = wp5.WP5_DIR
    with tempfile.TemporaryDirectory(prefix="wp5-export-sensitivity-", dir="/tmp/opencode") as temp_dir:
        scratch_dir = Path(temp_dir)
        wp5.WP5_DIR = scratch_dir
        try:
            wp5.main()
        finally:
            wp5.WP5_DIR = canonical_wp5_dir

        source_csv = scratch_dir / "wp5_tea_lca_scenarios.csv"
        source_manifest = json.loads((scratch_dir / "wp5_validation_summary.json").read_text(encoding="utf-8"))
        with source_csv.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            focal_rows = [
                row
                for row in reader
                if row["scenario_id"] == FOCAL_SCENARIO and row["wp5_variant"] in VARIANTS
            ]
            fieldnames = reader.fieldnames

        rows: list[dict[str, str]] = []
        variant_order = (
            "baseline_zero_credit",
            "S5_export_acceptance_50pct",
            "S5_offgrid_no_export",
        )
        for crop in sorted({row["crop"] for row in focal_rows}):
            policy_rows = [
                row
                for row in focal_rows
                if row["crop"] == crop
                and row["wp5_variant"] in variant_order[1:]
            ]
            selected_bess = {row["bess_option"] for row in policy_rows}
            selected_variants = {row["wp5_variant"] for row in policy_rows}
            if len(policy_rows) != 2 or len(selected_bess) != 1 or selected_variants != set(variant_order[1:]):
                raise RuntimeError(f"Expected one selected-BESS pair of policy rows for {crop}")
            bess_option = next(iter(selected_bess))
            for variant in variant_order:
                matching = [
                    row
                    for row in focal_rows
                    if row["crop"] == crop
                    and row["bess_option"] == bess_option
                    and row["wp5_variant"] == variant
                ]
                if len(matching) != 1:
                    raise RuntimeError(f"Expected one {variant} row for {crop}/{bess_option}")
                rows.append(matching[0])

        if len(rows) != 9:
            raise RuntimeError(f"Expected 9 focal-policy rows (3 crops × 3 policies); found {len(rows)}")

        with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    config = wp5.load_yaml(wp5.PARAMS_PATH)
    manifest: dict[str, Any] = {
        "generated_date": date.today().isoformat(),
        "framework_version": config["provenance"]["framework_version"],
        "scope": "S3 OPV APT44 versus the existing zero-export and full-export controls, for each crop's selected BESS option.",
        "export_acceptance_fraction": 0.5,
        "interpretation": "The fraction is the share of otherwise-exportable annual energy accepted for export; it is not an hourly kW interconnection cap.",
        "scenario_id": FOCAL_SCENARIO,
        "variants": sorted(VARIANTS),
        "row_count": len(rows),
        "wp5_validation_summary": source_manifest,
        "inputs": {
            "parameters_yaml_sha256": sha256(wp5.PARAMS_PATH),
            "wp5_script_sha256": sha256(Path(wp5.__file__)),
            "wp3_scenarios_csv_sha256": sha256(wp5.WP3_CSV_PATH),
            "wp1_summary_sha256": sha256(wp5.WP1_SUMMARY_PATH),
        },
        "output_csv_sha256": sha256(OUTPUT_CSV),
        "canonical_wp5_outputs_overwritten": False,
    }
    OUTPUT_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")
    print(f"Wrote provenance to {OUTPUT_MANIFEST}")


if __name__ == "__main__":
    main()
