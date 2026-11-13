#!/usr/bin/env python3
"""Validation script for parameters.yaml configuration."""

import sys
from pathlib import Path

def main():
    config_path = Path(__file__).resolve().parent.parent / "parameters.yaml"
    if not config_path.exists():
        print(f"Error: {config_path} does not exist", file=sys.stderr)
        sys.exit(1)

    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except ImportError:
        try:
            from ruamel.yaml import YAML
            yaml_loader = YAML(typ="safe")
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml_loader.load(f)
        except ImportError:
            print("Error: Neither PyYAML nor ruamel.yaml is installed.", file=sys.stderr)
            sys.exit(1)

    prov = cfg.get("provenance", {})
    version = prov.get("framework_version", "unknown")
    journal = prov.get("target_journal", "unknown")
    crops = list(cfg.get("crops", {}).keys())

    required_sections = [
        "lhcii_hamiltonian",
        "ness_solar_pumping",
        "opv_technology",
        "si_counterfactual",
        "optical_radiative_model",
        "crops",
        "microclimate",
        "economics",
        "scenarios",
        "monte_carlo",
    ]
    missing = [sec for sec in required_sections if sec not in cfg]
    if missing:
        print(f"Error: Missing required sections in parameters.yaml: {missing}", file=sys.stderr)
        sys.exit(1)

    base_dir = config_path.parent
    dataset_refs = [
        ("lhcii_hamiltonian.hamiltonian_source", cfg["lhcii_hamiltonian"].get("hamiltonian_source")),
        ("lhcii_hamiltonian.dipole_geometry_pdb", cfg["lhcii_hamiltonian"].get("dipole_geometry_pdb")),
        ("opv_technology.optical_nk_dataset", cfg["opv_technology"].get("optical_nk_dataset")),
        ("opv_technology.solar_spectrum_dataset", cfg["opv_technology"].get("solar_spectrum_dataset")),
        ("microclimate.climate_summary_dataset", cfg["microclimate"].get("climate_summary_dataset")),
    ]
    for crop_name, crop_cfg in cfg["crops"].items():
        dataset_refs.append((f"crops.{crop_name}.climate_dataset", crop_cfg.get("climate_dataset")))

    missing_files = []
    for key, rel_path in dataset_refs:
        if not rel_path or not (base_dir / rel_path).exists():
            missing_files.append(f"{key}={rel_path}")
    if missing_files:
        print(f"Error: Missing WP1 dataset files referenced in parameters.yaml: {missing_files}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Configuration verified successfully:")
    print(f"   - Framework Version: {version}")
    print(f"   - Target Journal:    {journal}")
    print(f"   - Configured Crops:  {', '.join(crops)}")
    print(f"   - Validated Blocks:  {len(required_sections)}/{len(required_sections)}")
    print(f"   - Validated Datasets:{len(dataset_refs)}/{len(dataset_refs)}")

if __name__ == "__main__":
    main()
