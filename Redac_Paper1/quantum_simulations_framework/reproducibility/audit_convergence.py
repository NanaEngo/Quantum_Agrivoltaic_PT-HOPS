import os
import sys
import yaml
import numpy as np
import pandas as pd
import logging
from datetime import datetime

# Add framework to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from core.hops_simulator import HopsSimulator, MESOHOPS_AVAILABLE
    from core.hamiltonian_factory import create_fmo_hamiltonian
except ImportError as e:
    print(f"❌ Framework import error: {e}")
    sys.exit(1)

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'parameters.yaml'))
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_convergence_audit():
    """
    Perform L=9, 10, 11 convergence audit to satisfy Reviewer 1 mandate.
    Detects fallback mode (fake data) and raises an error if MesoHOPS is unavailable.
    """
    print("🧪 Starting L=10 Convergence Audit...")
    cfg = load_config()

    # Guard: require real MesoHOPS
    if not MESOHOPS_AVAILABLE:
        logger.error("MesoHOPS is NOT available. Convergence audit requires the real solver.")
        print("❌ FATAL: MesoHOPS not found. Activate the MesoHOP-sim environment:")
        print("   mamba run -n MesoHOP-sim python reproducibility/audit_convergence.py")
        sys.exit(1)

    # Simulation Parameters
    t_max = cfg['dynamics']['time_max']
    dt = cfg['dynamics']['time_step']
    K = cfg['dynamics']['matsubara_truncation']  # K=10 from parameters.yaml
    time_points = np.arange(0, t_max, dt)

    # Hierarchy Depths to Audit
    depths = [9, 10, 11]
    results = {}

    # Create Hamiltonian (Standard FMO)
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)

    for L in depths:
        logger.info(f"Running simulation for Hierarchy Depth L={L}, K={K}...")
        simulator = HopsSimulator(
            H,
            max_hierarchy=L,
            use_sbd=True,
            use_pt_hops=True
        )

        sim_data = simulator.simulate_dynamics(time_points, n_traj=10)
        results[L] = sim_data['populations']

    # Sanity check: L=9 and L=10 must NOT be identical (would indicate fallback)
    if np.allclose(results[9], results[10], atol=1e-12):
        logger.error("FAKE DATA DETECTED: L=9 and L=10 populations are identical. "
                     "The simulator fell back to a non-hierarchy solver.")
        print("❌ FATAL: Convergence data is invalid (all depths produce identical results).")
        print("   This means MesoHOPS hierarchy is not being used. Check solver initialization.")
        sys.exit(1)
    
    # Compare L=10 vs L=9 (Convergence toward L=10)
    diff_9_10 = np.mean(np.abs(results[10] - results[9]))
    # Compare L=10 vs L=11 (Validation of L=10 exactness)
    diff_10_11 = np.mean(np.abs(results[11] - results[10]))
    
    print(f"\n📊 Convergence Audit Results:")
    print(f"   - MAE (L=9 -> L=10): {diff_9_10:.2e}")
    print(f"   - MAE (L=10 -> L=11): {diff_10_11:.2e}")
    
    if diff_10_11 < cfg['dynamics']['convergence_threshold']:
        print("✅ SUCCESS: L=10 is numerically converged (residual < threshold).")
    else:
        print("⚠️ WARNING: Residual exceeds threshold. Further truncation check recommended.")
        
    # Save results for SI using Hardened Storage
    from utils.csv_data_storage import CSVDataStorage
    storage = CSVDataStorage(output_dir="reproducibility/results")
    
    # Pack metrics for storage
    metrics = {
        "pop_site1_L9": results[9][:, 0],
        "pop_site1_L11": results[11][:, 0],
    }
    
    output_path = storage.save_quantum_dynamics_results(
        time_points,
        results[10],
        np.zeros(len(time_points)), # Placeholder coherences
        metrics,
        filename_prefix="convergence_audit",
        config_dict=cfg,
        audit_mae_9_10=diff_9_10,
        audit_mae_10_11=diff_10_11
    )
    print(f"💾 Hardened Audit data saved to: {output_path}")

if __name__ == "__main__":
    run_convergence_audit()
