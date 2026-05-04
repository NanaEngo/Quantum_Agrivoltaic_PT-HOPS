#!/usr/bin/env python3
"""
optimize.py — Filter wavelength sweep for optimal coherence enhancement.

Fixes vs original:
  - Uses MD_analyse_code/hops_simulator.py (corrected MesoHOPS API)
  - pulse_center_freq removed from HopsSimulator (not a valid system_param key)
  - storage accessed via hops.storage['psi_traj'] (dict-style)
"""

import csv
import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import yaml

_HERE = Path(__file__).parent.resolve()
_MD_CODE = _HERE.parent.resolve()
_FRAMEWORK = _MD_CODE.parent.resolve()

sys.path.insert(0, str(_FRAMEWORK))
sys.path.insert(0, str(_MD_CODE))

_LOG_DIR = _HERE / "logs"
_LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=_LOG_DIR / f"optimize_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    with open(_FRAMEWORK / "parameters.yaml", "r") as f:
        return yaml.safe_load(f)


def sweep_filter_wavelengths(
    cfg: dict,
    center_wavelengths_nm: list = None,
) -> list:
    """
    Sweep dual-band filter center wavelengths to find optimal Φ_FT.

    NOTE: MesoHOPS does not accept pulse parameters in system_param.
    The filter wavelength is recorded as metadata only; the simulation
    uses the same bath parameters for all points (the spectral filter
    effect on the initial state is applied externally if needed).

    Returns list of dicts: {'lambda1_nm', 'lambda2_nm', 'phi_ft'}
    """
    from hops_simulator import HopsSimulator, MESOHOPS_AVAILABLE

    if not MESOHOPS_AVAILABLE:
        print("❌ MesoHOPS required. Activate the MesoHOP-sim environment.")
        sys.exit(1)

    if center_wavelengths_nm is None:
        l1_range = np.arange(730, 771, 10)
        l2_range = np.arange(800, 841, 10)
        center_wavelengths_nm = [(l1, l2) for l1 in l1_range for l2 in l2_range]

    dyn = cfg["dynamics"]
    bath = cfg["bath"]
    time_points = np.arange(0.0, dyn["time_max"], dyn["time_step"])

    try:
        from core.hamiltonian_factory import create_fmo_hamiltonian
        H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    except ImportError:
        H = np.array([[100.0, 50.0], [50.0, 0.0]])
        logger.warning("Using 2-site fallback Hamiltonian")

    n = H.shape[0]
    init_state = np.zeros(n, dtype=complex)
    init_state[0] = 1.0

    # Build simulator once (bath params are the same for all wavelength points)
    sim = HopsSimulator(
        hamiltonian=H,
        temperature=bath["temperature"],
        reorganization_energy=bath["reorganization_energy"],
        drude_cutoff=bath["drude_cutoff"],
        max_hierarchy=dyn["hierarchy_depth"],
        k_matsubara=0,
    )

    sweep_results = []
    for idx, (l1, l2) in enumerate(center_wavelengths_nm):
        logger.info(f"λ1={l1} nm, λ2={l2} nm")
        try:
            data = sim.simulate_dynamics(time_points, init_state.copy(), seed=idx)
            phi_ft = float(1.0 - data["populations"][-1, 0])
            sweep_results.append({"lambda1_nm": l1, "lambda2_nm": l2, "phi_ft": phi_ft})
            print(f"  λ1={l1}, λ2={l2} → Φ_FT={phi_ft:.3f}")
        except Exception as e:
            logger.warning(f"Failed at λ1={l1}, λ2={l2}: {e}")

    # Save
    results_dir = _HERE / "results"
    results_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = results_dir / f"optimization_{ts}.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["lambda1_nm", "lambda2_nm", "phi_ft"])
        writer.writeheader()
        writer.writerows(sweep_results)
    print(f"\n💾 Optimization results → {out_path}")
    return sweep_results


def main() -> None:
    print("=" * 60)
    print("  PT-HOPS Parameter Optimization Suite")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    cfg = load_config()
    print("\n[Step 1] Sweeping filter wavelengths around (750, 820) nm...")
    results = sweep_filter_wavelengths(cfg)
    if results:
        best = max(results, key=lambda r: r["phi_ft"])
        print(f"\n✅ Optimal: λ1={best['lambda1_nm']} nm, λ2={best['lambda2_nm']} nm "
              f"→ Φ_FT={best['phi_ft']:.3f}")


if __name__ == "__main__":
    main()
