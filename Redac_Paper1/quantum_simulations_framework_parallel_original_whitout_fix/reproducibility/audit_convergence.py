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
    dt = cfg['dynamics']['time_step']
    K = cfg['dynamics']['matsubara_truncation']  # K=2 from parameters.yaml
    # Convergence audit uses 100 fs window — sufficient to see L-dependent
    # differences while keeping the noise buffer (TLEN = t_audit + 50) small.
    t_audit = 100.0
    time_points = np.arange(0, t_audit, dt)

    # Hierarchy Depths to Audit
    depths = [9, 10, 11]
    results = {}
    coherences = {}

    # Create Hamiltonian (Standard FMO)
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)

    # Define explicit initial state (Site 1 excitation, index 0)
    init_state = np.zeros(H.shape[0], dtype=complex)
    init_state[0] = 1.0

    for L in depths:
        logger.info(f"Running simulation for Hierarchy Depth L={L}, K={K}...")
        simulator = HopsSimulator(
            H,
            max_hierarchy=L,
            k_matsubara=K,
            use_sbd=False,   # SBD disabled for audit — tests pure hierarchy convergence
            use_pt_hops=False,
            vibronic_frequencies=np.array([]),  # DL-only bath for audit
            huang_rhys_factors=np.array([]),
            vibronic_damping=np.array([]),
        )

        sim_data = simulator.simulate_dynamics(time_points, initial_state=init_state)
        results[L] = sim_data['populations']
        coherences[L] = sim_data.get('coherences', np.zeros(len(time_points)))

    # Trace check: single HOPS trajectories lose norm stochastically.
    # Threshold of 0.5 catches catastrophic solver failure (>50% norm loss)
    # while tolerating the expected stochastic norm fluctuations of a single
    # HOPS trajectory. A mean trace of 0.01 (the previous threshold) would
    # only catch a completely collapsed wavefunction — 100× too permissive.
    # FIX M-2: raised threshold from 0.01 to 0.5.
    for L in depths:
        pops = results[L]
        traces = np.sum(pops, axis=1)
        mean_trace = np.mean(traces)
        if mean_trace < 0.5:  # catastrophic loss — indicates solver failure
            logger.error(f"L={L}: Catastrophic trace loss! Mean trace={mean_trace:.4f}")
            print(f"❌ FATAL: Catastrophic trace loss at L={L} (mean trace={mean_trace:.4f})")
            sys.exit(1)
        logger.info(f"L={L}: mean trace={mean_trace:.4f} (single trajectory — stochastic norm loss expected)")
    for L in depths:
        pops = results[L]

        # 1. Trace: single HOPS trajectories have stochastic norm loss — log but don't fail
        traces = np.sum(pops, axis=1)
        trace_dev = np.max(np.abs(traces - 1.0))
        logger.info(f"L={L}: max trace deviation={trace_dev:.2e} (single trajectory)")

        # 2. Positivity: diagonal elements must be >= 0 (physical requirement)
        min_pop = np.min(pops)
        if min_pop < -1e-3:
            logger.error(f"L={L}: Positivity violated! Min population: {min_pop:.2e}")
            print(f"❌ FATAL: Positivity failed at L={L} (min population {min_pop:.2e} < -1e-3)")
            sys.exit(1)

    print("✅ Positivity checks passed for all depths.")

    # Shape consistency guard before subtraction
    shapes = {L: results[L].shape for L in depths}
    if len(set(shapes.values())) > 1:
        logger.error(f"Shape mismatch across hierarchy depths: {shapes}")
        print(f"❌ FATAL: Population arrays have inconsistent shapes: {shapes}")
        sys.exit(1)

    # Sanity check: L=9 and L=10 must NOT be identical (would indicate fallback)
    if np.allclose(results[9], results[10], atol=1e-12):
        logger.error("FAKE DATA DETECTED: L=9 and L=10 populations are identical. "
                     "The simulator fell back to a non-hierarchy solver.")
        print("❌ FATAL: Convergence data is invalid (all depths produce identical results).")
        print("   This means MesoHOPS hierarchy is not being used. Check solver initialization.")
        sys.exit(1)

    # FIX M-1: also check L=10 vs L=11 — a noisy fallback could pass the L=9/10 check
    if np.allclose(results[10], results[11], atol=1e-12):
        logger.error("FAKE DATA DETECTED: L=10 and L=11 populations are identical. "
                     "The simulator is not using the hierarchy truncation depth.")
        print("❌ FATAL: L=10 and L=11 results are identical — hierarchy depth has no effect.")
        print("   Check that HopsSimulator is passing MAXHIER correctly to MesoHOPS.")
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

    # ── K-convergence audit (addresses Reviewer 1 comment 1.5) ──────────────
    # Prove that K=2 Matsubara terms are sufficient at T=295 K by comparing
    # K=1, K=2, K=3 at fixed L=10. At room temperature the first Matsubara
    # frequency ν₁ ≈ 1300 cm⁻¹ >> γ_D = 50 cm⁻¹, so higher terms are negligible.
    print("\n🧪 K-Matsubara Convergence Audit (L=10 fixed)...")
    k_depths = [1, 2, 3]
    k_results = {}
    for Kval in k_depths:
        logger.info(f"Running K-audit: L=10, K={Kval}...")
        sim_k = HopsSimulator(
            H,
            max_hierarchy=10,
            k_matsubara=Kval,
            use_sbd=False,
            use_pt_hops=False,
            vibronic_frequencies=np.array([]),
            huang_rhys_factors=np.array([]),
            vibronic_damping=np.array([]),
        )
        data_k = sim_k.simulate_dynamics(time_points, initial_state=init_state)
        k_results[Kval] = data_k['populations']
        logger.info(f"  K={Kval}: done")

    diff_k1_k2 = np.mean(np.abs(k_results[2] - k_results[1]))
    diff_k2_k3 = np.mean(np.abs(k_results[3] - k_results[2]))
    print(f"\n📊 K-Matsubara Convergence Results (L=10, T=295 K):")
    print(f"   MAE (K=1 → K=2) : {diff_k1_k2:.2e}")
    print(f"   MAE (K=2 → K=3) : {diff_k2_k3:.2e}")
    if diff_k2_k3 < cfg['dynamics']['convergence_threshold']:
        print("✅ K=2 is converged at T=295 K (residual < threshold).")
    else:
        print("⚠️ WARNING: K=2 may not be fully converged — consider K=3.")
        logger.warning(f"K-convergence marginal: MAE(K=2→K=3)={diff_k2_k3:.2e}")
        
    # Save results for SI using Hardened Storage
    from utils.csv_data_storage import CSVDataStorage
    _results_dir = os.path.join(os.path.dirname(__file__), 'results')
    storage = CSVDataStorage(output_dir=_results_dir)

    # Trim all arrays to the shortest common length before saving
    n_min = min(
        len(time_points),
        results[9].shape[0],
        results[10].shape[0],
        results[11].shape[0],
        len(coherences[10]),
    )
    metrics = {
        "pop_site1_L9": results[9][:n_min, 0],
        "pop_site1_L11": results[11][:n_min, 0],
    }

    try:
        output_path = storage.save_quantum_dynamics_results(
            time_points[:n_min],
            results[10][:n_min],
            coherences[10][:n_min],
            metrics,
            filename_prefix="convergence_audit",
            config_dict=cfg,
            audit_mae_9_10=diff_9_10,
            audit_mae_10_11=diff_10_11,
            audit_mae_k1_k2=diff_k1_k2,
            audit_mae_k2_k3=diff_k2_k3,
        )
        print(f"💾 Hardened Audit data saved to: {output_path}")
        logger.info(f"Convergence audit complete. MAE(9→10)={diff_9_10:.2e}, MAE(10→11)={diff_10_11:.2e}")
    except Exception as e:
        logger.error(f"Failed to save audit CSV: {e}")
        output_path = None
        print(f"⚠️  Audit CSV save failed: {e} — results still returned.")

    # Return L=10 results for downstream figure generation.
    # FIX C-5: return actual L=10 coherences (trimmed to n_min) instead of
    # hardcoded np.zeros — the previous stub silently zeroed Figure 1's
    # coherence panel regardless of the simulation output.
    return {
        "time_points": time_points[:n_min],
        "populations": results[10][:n_min],
        "coherences": coherences[10][:n_min],
        "audit_mae_9_10": diff_9_10,
        "audit_mae_10_11": diff_10_11,
        "audit_mae_k1_k2": diff_k1_k2,
        "audit_mae_k2_k3": diff_k2_k3,
        "csv_path": output_path,
    }

if __name__ == "__main__":
    run_convergence_audit()
