"""
main.py — Single-entry reproducibility pipeline for JPCL revision.
Usage: mamba run -n MesoHOP-sim python reproducibility/main.py

Produces:
  reproducibility/results/convergence_audit_<hash>_<ts>.csv  — L=9,10,11 audit
  reproducibility/results/fmo_dynamics_<hash>_<ts>.csv       — full L=10 FMO run
  Theory_Journals/JPCL/Quantum_dynamics_<ts>.{pdf,png}       — Figure 1
  Theory_Journals/JPCL/ETR_Under_Environmental_Effects_<ts>.{pdf,png} — Figure 2
  reproducibility/logs/execution_<ts>.log                    — execution log
"""
import os
import sys
import logging
import yaml
import numpy as np
from datetime import datetime

# Ensure framework is importable regardless of CWD
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FRAMEWORK_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, '..'))
sys.path.insert(0, _FRAMEWORK_DIR)
sys.path.insert(0, _SCRIPT_DIR)

_LOG_DIR = os.path.join(_SCRIPT_DIR, 'logs')
os.makedirs(_LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(_LOG_DIR, f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_and_validate_config():
    config_path = os.path.join(_FRAMEWORK_DIR, 'parameters.yaml')
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)
    L = cfg['dynamics']['hierarchy_depth']
    K = cfg['dynamics']['matsubara_truncation']
    if L < 10:
        raise ValueError(f"hierarchy_depth={L} < 10. JPCL revision requires L=10.")
    if K < 10:
        raise ValueError(f"matsubara_truncation={K} < 10. JPCL revision requires K=10.")
    logger.info(f"Config validated: L={L}, K={K}, T={cfg['bath']['temperature']}K")
    return cfg


def check_environment():
    try:
        import mesohops
        version = getattr(mesohops, '__version__', 'unknown')
        print(f"  ✅ MesoHOPS {version} available")
        logger.info(f"MesoHOPS {version} available")
        return True
    except ImportError:
        print("  ❌ MesoHOPS NOT found. Run: mamba run -n MesoHOP-sim python reproducibility/main.py")
        logger.error("MesoHOPS not available")
        return False


def run_convergence_audit():
    print("\n[Step 2] Running convergence audit (L=9,10,11)...")
    from audit_convergence import run_convergence_audit as _audit
    audit_data = _audit()
    if audit_data:
        print(f"  ✅ Audit complete. MAE(10→11)={audit_data['audit_mae_10_11']:.2e}")
        print(f"  💾 Saved → {audit_data['csv_path']}")
    return audit_data


def run_full_fmo_simulation(cfg):
    """Run the full L=10 FMO simulation (filtered + broadband) and save results."""
    print("\n[Step 3] Running full FMO simulation (filtered + broadband)...")
    from core.hops_simulator import HopsSimulator
    from core.hamiltonian_factory import create_fmo_hamiltonian
    from utils.csv_data_storage import CSVDataStorage

    dyn = cfg['dynamics']
    bath = cfg['bath']
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    time_points = np.arange(0, dyn['time_max'], dyn['time_step'])

    results = {}
    for label in ['filtered', 'broadband']:
        print(f"  Running {label} excitation...")
        sim = HopsSimulator(
            H,
            temperature=bath['temperature'],
            reorganization_energy=bath['reorganization_energy'],
            drude_cutoff=bath['drude_cutoff'],
            max_hierarchy=dyn['hierarchy_depth'],
            k_matsubara=dyn['matsubara_truncation'],
            use_sbd=True,
            use_pt_hops=True,
        )
        data = sim.simulate_dynamics(time_points)
        results[label] = data
        logger.info(f"FMO {label} simulation complete. Simulator: {data.get('simulator','?')}")

    # Save both runs to CSV
    _results_dir = os.path.join(_SCRIPT_DIR, 'results')
    storage = CSVDataStorage(output_dir=_results_dir)
    metrics = {
        "pop_site1_broadband": results['broadband']['populations'][:, 0],
        "coherence_broadband": results['broadband']['coherences'],
    }
    csv_path = storage.save_quantum_dynamics_results(
        time_points,
        results['filtered']['populations'],
        results['filtered']['coherences'],
        metrics,
        filename_prefix="fmo_dynamics",
        config_dict=cfg,
    )
    print(f"  💾 FMO dynamics saved → {csv_path}")
    logger.info(f"FMO dynamics saved to {csv_path}")
    return results, time_points


def generate_figures(cfg, sim_results, time_points):
    """Generate all publication figures and save to JPCL directory."""
    print("\n[Step 4] Generating publication figures...")
    from utils.figure_generator import FigureGenerator

    jpcl_dir = os.path.abspath(os.path.join(
        _SCRIPT_DIR, '..', '..', 'Theory_Journals', 'JPCL'
    ))
    gen = FigureGenerator(figures_dir=jpcl_dir)

    filtered = sim_results['filtered']
    broadband = sim_results['broadband']

    # Figure 1: Quantum dynamics (filtered vs broadband overlay)
    quantum_metrics = {
        "qfi": filtered.get('qfi', np.zeros(len(time_points))),
        "entropy": filtered.get('entropy', np.zeros(len(time_points))),
    }
    fig1_path = gen.plot_quantum_dynamics(
        time_points,
        filtered['populations'],
        filtered['coherences'],
        quantum_metrics,
        filename_prefix="Quantum_dynamics",
        baseline_populations=broadband['populations'],
        baseline_coherences=broadband['coherences'],
    )
    print(f"  💾 Figure 1 saved → {fig1_path}")
    logger.info(f"Figure 1 saved to {fig1_path}")

    # Figure 2: Environmental robustness (temperature sweep)
    try:
        fig2_path = gen.plot_environmental_robustness(
            time_points,
            filtered['populations'],
            filtered['coherences'],
            filename_prefix="ETR_Under_Environmental_Effects",
        )
        print(f"  💾 Figure 2 saved → {fig2_path}")
        logger.info(f"Figure 2 saved to {fig2_path}")
    except AttributeError:
        print("  ℹ️  plot_environmental_robustness not available — skipping Figure 2")
        logger.warning("plot_environmental_robustness not found in FigureGenerator")


def main():
    print("=" * 60)
    print("  Quantum Agrivoltaic PT-HOPS — JPCL Reproducibility Pipeline")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: Validate config
    print("\n[Step 1] Loading and validating parameters.yaml...")
    try:
        cfg = load_and_validate_config()
        L = cfg['dynamics']['hierarchy_depth']
        K = cfg['dynamics']['matsubara_truncation']
        print(f"  ✅ L={L}, K={K}, T={cfg['bath']['temperature']}K — all mandates satisfied")
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        sys.exit(1)

    # Step 1b: Check environment
    print("\n[Step 1b] Checking MesoHOPS environment...")
    if not check_environment():
        print("\n⚠️  Cannot run simulations without MesoHOPS. Exiting.")
        sys.exit(1)

    # Step 2: Convergence audit — proves L=10 is sufficient
    audit_data = run_convergence_audit()

    # Step 3: Full FMO simulation — generates the actual paper data
    sim_results, time_points = run_full_fmo_simulation(cfg)

    # Step 4: Generate and save all figures
    generate_figures(cfg, sim_results, time_points)

    print("\n" + "=" * 60)
    print("  Pipeline complete.")
    print(f"  Results → {os.path.join(_SCRIPT_DIR, 'results')}")
    print(f"  Figures → Theory_Journals/JPCL/")
    print(f"  Logs    → {_LOG_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
