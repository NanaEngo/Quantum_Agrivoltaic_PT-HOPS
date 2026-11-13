"""
Quantum Agrivoltaics Paper 2: CLI Entry Point.

Usage:
    PYTHONPATH=. python Redac_Paper2/main.py --solar-flux 950.0
"""

import argparse
import logging
import os
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from src.constants import DEFAULT_SOLAR_FLUX_W_M2
from src.logging_config import setup_logging
from src.orchestrator import run_global_simulation


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quantum Agrivoltaics Paper 2 — Simulation Orchestrator"
    )
    parser.add_argument(
        "--solar-flux",
        type=float,
        default=DEFAULT_SOLAR_FLUX_W_M2,
        help=f"Incident solar flux in W/m2 (default: {DEFAULT_SOLAR_FLUX_W_M2})",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to log file (default: None — console only)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging",
    )
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level, log_file=args.log_file)

    run_global_simulation(solar_flux=args.solar_flux)


if __name__ == "__main__":
    main()
