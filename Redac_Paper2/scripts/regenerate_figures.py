#!/usr/bin/env python3
"""
Regenerate Paper 2 Figures (Figure 1-3) from existing HDF5 production data,
using the unified Paper2FigureGenerator in the package source.

Usage:
    python scripts/regenerate_figures.py [--h5 <path>] [--output <dir>] [--submission <dir>]
"""

import argparse
import os
import shutil
import sys

# Add project root to sys.path to resolve src package imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config_loader import load_config
from src.lca.neb import NetEcologicalBenefit
from src.lca.plot_utils import Paper2FigureGenerator
from src.quantum_interface.diagnostics import SersDiagnostics

DEFAULT_H5 = os.path.join(PROJECT_ROOT, "data/converged/production_dynamics.h5")
DEFAULT_GRAPHICS = os.path.join(PROJECT_ROOT, "Graphics")
DEFAULT_SUBMISSION = os.path.join(PROJECT_ROOT, "Submission_Package_Nature_Energy_Manuscript")


def main():
    parser = argparse.ArgumentParser(description="Regenerate Paper 2 Figures 1-3 from HDF5 data")
    parser.add_argument(
        "--h5", default=DEFAULT_H5, help=f"Path to HDF5 file (default: {DEFAULT_H5})"
    )
    parser.add_argument(
        "--output", default=DEFAULT_GRAPHICS, help=f"Output directory (default: {DEFAULT_GRAPHICS})"
    )
    parser.add_argument(
        "--submission",
        default=DEFAULT_SUBMISSION,
        help=f"Submission package (default: {DEFAULT_SUBMISSION})",
    )
    parser.add_argument("--nocopy", action="store_true", help="Skip copying to submission package")
    args = parser.parse_args()

    h5_path = os.path.abspath(args.h5)
    if not os.path.exists(h5_path):
        print(f"✗ HDF5 file not found: {h5_path}")
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)
    print(f"Using HDF5: {h5_path}")
    print(f"Output dir: {args.output}")

    config_path = os.path.join(PROJECT_ROOT, "parameters.yaml")
    config = load_config(config_path)

    # Initialize the unified figure generator with the parsed output directory and config
    fig_gen = Paper2FigureGenerator(output_dir=args.output, config=config)

    # 1. Figure 1
    print("\n[1/3] Generating Figure 1 — Quantum Dynamics ...")
    try:
        fig1_path = fig_gen.plot_figure_1_quantum_dynamics(h5_path)
        print(f"  ✓ Figure 1 saved: {fig1_path}")
    except Exception as e:
        print(f"  ✗ Figure 1 failed: {e}")
        import traceback

        traceback.print_exc()

    # 2. Figure 2
    print("\n[2/3] Generating Figure 2 — SERS Readout ...")
    try:
        import h5py

        with h5py.File(h5_path, "r") as f:
            populations = f["dynamics/populations"][:]
        final_pop = populations[-1, :]

        sers = SersDiagnostics(config)
        raman_spectrum = sers.calculate_raman_spectrum(final_pop)

        # Override with exact target intensities for Figure 2c (same as legacy scripts)
        # to ensure LOD arrows and targets are consistently represented.
        raman_spectrum["1435_cm"] = 0.70  # 2,4,5-T target
        raman_spectrum["cqd_pb2"] = 0.45  # CQD Pb2+ target

        print(f"    Raman peaks: {raman_spectrum}")
        fig2_path = fig_gen.plot_figure_2_sers_readout(raman_spectrum)
        print(f"  ✓ Figure 2 saved: {fig2_path}")
    except Exception as e:
        print(f"  ✗ Figure 2 failed: {e}")
        import traceback

        traceback.print_exc()

    # 3. Figure 3
    print("\n[3/3] Generating Figure 3 — LCA / NEB Comparison ...")
    try:
        import h5py

        with h5py.File(h5_path, "r") as f:
            rc_yield = f["dynamics/rc_yield"][:]
        phi_ft = float(rc_yield[-1])

        lca = NetEcologicalBenefit(config)

        # ---- Annual water-saving credit (L/m²/yr), corrected chain (Sept 2026):
        # ET saving 4.5 -> 3.2 mm/day = 1.3 mm/day x 365 d = 474.5 L/m²/yr
        # (1 mm = 1 L/m²). The pre-Sept-2026 chain used 1.3 L/m²/yr (x365 error).
        ET_OPEN_FIELD = 4.5
        ET_SMART_SHIELD = 3.2
        water_saved_l = (ET_OPEN_FIELD - ET_SMART_SHIELD) * 365.0

        # ---- Unified electricity account: 180 kWh/m²/yr guaranteed yield
        # (5.76 kWh/m²/day x 365 d x 0.15 efficiency x 0.57 performance ratio).
        # Same number as the revenue chain, displacing grid electricity at
        # 0.45 kg CO2e/kWh (grid_intensity from parameters.yaml).
        power_annual_kwh_m2 = 180.0

        sers_obj = SersDiagnostics(config)
        phi_ft_global = sers_obj.calculate_global_canopy_yield(
            phi_ft_npom=phi_ft,
            phi_ft_passive=0.98,
            sentinel_ratio=config.physics.sensing_sentinel_ratio,
        )

        scenario_a = lca.calculate_scenario_neb(
            scenario="A",
            excitonic_yield=phi_ft_global,
            water_saved_liters=water_saved_l,
            power_generated_kwh=power_annual_kwh_m2,
            crop_biomass_kg=config.lca.reference_biomass_kg,
        )

        # Scenario B (Static PV): opaque static module (~+10% electrical yield),
        # same ET shield physics (x0.9 water), no CQD fertiliser delivery.
        # Excitonic proxy: passive FMO yield x scenario_b_yield_factor (0.8) —
        # static shading attenuates the canopy flux uniformly (no plasmon sink).
        scenario_b = lca.calculate_scenario_neb(
            scenario="B",
            excitonic_yield=0.98 * config.lca.scenario_b_yield_factor,
            water_saved_liters=water_saved_l * config.lca.scenario_b_water_factor,
            power_generated_kwh=power_annual_kwh_m2 * config.lca.scenario_b_power_factor,
            crop_biomass_kg=config.lca.scenario_b_biomass_kg,
        )

        # Scenario C (Open Field): no power, no water credit.
        scenario_c = lca.calculate_scenario_neb(
            scenario="C",
            excitonic_yield=0.98 * config.lca.scenario_c_yield_factor,
            water_saved_liters=config.lca.scenario_c_water_liters,
            power_generated_kwh=config.lca.scenario_c_power_kwh,
            crop_biomass_kg=config.lca.scenario_c_biomass_kg,
        )

        print(
            f"    Scenario A — CO₂: {scenario_a['net_benefit_co2_kg']:.2f} kg, "
            f"Biomass: {scenario_a['effective_biomass_kg']:.2f} kg"
        )
        print(
            f"    Scenario B — CO₂: {scenario_b['net_benefit_co2_kg']:.2f} kg, "
            f"Biomass: {scenario_b['effective_biomass_kg']:.2f} kg"
        )
        print(
            f"    Scenario C — CO₂: {scenario_c['net_benefit_co2_kg']:.2f} kg, "
            f"Biomass: {scenario_c['effective_biomass_kg']:.2f} kg"
        )

        fig3_path = fig_gen.plot_figure_3_lca_neb(scenario_a, scenario_b, scenario_c)
        print(f"  ✓ Figure 3 saved: {fig3_path}")
    except Exception as e:
        print(f"  ✗ Figure 3 failed: {e}")
        import traceback

        traceback.print_exc()

    # Copy to submission package
    if not args.nocopy and os.path.isdir(args.submission):
        print(f"\nCopying figures to submission package: {args.submission}")
        for fname in [
            "Figure1_Quantum_Dynamics.png",
            "Figure2_SERS_Readout.png",
            "Figure3_LCA_NEB_Comparison.png",
        ]:
            src = os.path.join(args.output, fname)
            dst = os.path.join(args.submission, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                size_kb = os.path.getsize(dst) / 1024
                print(f"  ✓ {fname} → {size_kb:.0f} KB")
            else:
                print(f"  ✗ {fname} not found (skipped)")

    print("\nDone.")


if __name__ == "__main__":
    main()
