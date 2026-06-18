"""
Quantum Agrivoltaics Paper 2: CLI Entry Point.

Usage:
    PYTHONPATH=. python Redac_Paper2/main.py --solar-flux 950.0

Delegates all orchestration logic to src/orchestrator.py.
"""

import os
import sys
import argparse

# Disable Numba CUDA to avoid driver/NVML mismatch crashes on server
os.environ["NUMBA_DISABLE_CUDA"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Ensure project root is on the Python path
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from src.orchestrator import run_global_simulation


def main() -> None:
    """Parse CLI arguments and launch the simulation pipeline."""
    parser = argparse.ArgumentParser(
        description="Quantum Agrivoltaics Paper 2 — Simulation Orchestrator"
    )
    parser.add_argument(
        "--solar-flux",
        type=float,
        default=950.0,
        help="Incident solar flux in W/m2 (default: 950.0)",
    )
    args = parser.parse_args()

    run_global_simulation(solar_flux=args.solar_flux)


if __name__ == "__main__":
    main()
