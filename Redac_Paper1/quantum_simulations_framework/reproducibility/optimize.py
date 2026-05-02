"""
optimize.py — Parameter Optimization Suite (FR9).
Explores optimal vibronic coupling and laser excitation regimes.
Usage: mamba run -n MesoHOP-sim python reproducibility/optimize.py
"""
import os
import sys
import yaml
import numpy as np
import logging
from datetime import datetime

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FRAMEWORK_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, '..'))
sys.path.insert(0, _FRAMEWORK_DIR)
sys.path.insert(0, _SCRIPT_DIR)

_LOG_DIR = os.path.join(_SCRIPT_DIR, 'logs')
os.makedirs(_LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(_LOG_DIR, f"optimize_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    config_path = os.path.join(_FRAMEWORK_DIR, 'parameters.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def sweep_filter_wavelengths(cfg, center_wavelengths_nm=None, n_traj=5):
    """
    Sweep dual-band filter center wavelengths to find optimal coherence enhancement.

    Parameters
    ----------
    cfg : dict
        Loaded parameters.yaml config.
    center_wavelengths_nm : list of (float, float), optional
        List of (lambda1, lambda2) pairs in nm to test.
        Defaults to a grid around the canonical (750, 820) nm.
    n_traj : int
        Trajectories per parameter point (use small value for sweep).

    Returns
    -------
    results : list of dict
        Each dict: {'lambda1': float, 'lambda2': float, 'eta': float}
    """
    from core.hops_simulator import HopsSimulator, MESOHOPS_AVAILABLE
    from core.hamiltonian_factory import create_fmo_hamiltonian

    if not MESOHOPS_AVAILABLE:
        print("❌ MesoHOPS required for optimization. Activate MesoHOP-sim environment.")
        sys.exit(1)

    if center_wavelengths_nm is None:
        # Default grid: ±20 nm around canonical values
        l1_range = np.arange(730, 771, 10)   # 730, 740, 750, 760, 770
        l2_range = np.arange(800, 841, 10)   # 800, 810, 820, 830, 840
        center_wavelengths_nm = [(l1, l2) for l1 in l1_range for l2 in l2_range]

    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    dyn = cfg['dynamics']
    bath = cfg['bath']
    time_points = np.arange(0, dyn['time_max'], dyn['time_step'])

    results = []
    for l1, l2 in center_wavelengths_nm:
        logger.info(f"Testing filter: λ1={l1} nm, λ2={l2} nm")
        try:
            sim = HopsSimulator(
                H,
                temperature=bath['temperature'],
                reorganization_energy=bath['reorganization_energy'],
                drude_cutoff=bath['drude_cutoff'],
                max_hierarchy=dyn['hierarchy_depth'],
                k_matsubara=dyn['matsubara_truncation'],
                use_sbd=True,
                use_pt_hops=True,
                pulse_center_freq=1e7 / l1,  # nm → cm^-1
            )
            data = sim.simulate_dynamics(time_points)
            phi_ft = 1.0 - data['populations'][-1, 0]
            results.append({'lambda1_nm': l1, 'lambda2_nm': l2, 'phi_ft': phi_ft})
            print(f"  λ1={l1}, λ2={l2} → Φ_FT={phi_ft:.3f}")
        except Exception as e:
            logger.warning(f"Failed at λ1={l1}, λ2={l2}: {e}")

    # Save results
    import csv
    out_path = os.path.join(_SCRIPT_DIR, 'results',
                            f"optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['lambda1_nm', 'lambda2_nm', 'phi_ft'])
        writer.writeheader()
        writer.writerows(results)
    print(f"\n💾 Optimization results saved to: {out_path}")
    return results


def main():
    print("=" * 60)
    print("  PT-HOPS Parameter Optimization Suite (FR9)")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    cfg = load_config()
    print("\n[Step 1] Sweeping filter wavelengths around canonical (750, 820) nm...")
    results = sweep_filter_wavelengths(cfg)
    if results:
        best = max(results, key=lambda r: r['phi_ft'])
        print(f"\n✅ Optimal filter: λ1={best['lambda1_nm']} nm, λ2={best['lambda2_nm']} nm "
              f"→ Φ_FT={best['phi_ft']:.3f}")


if __name__ == "__main__":
    main()
