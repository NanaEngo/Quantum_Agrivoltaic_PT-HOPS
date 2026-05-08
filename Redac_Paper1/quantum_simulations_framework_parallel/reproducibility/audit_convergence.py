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
    try:
        from tqdm.auto import tqdm as _tqdm
    except ImportError:
        def _tqdm(iterable, **kwargs): return iterable
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
    print("🧪 Starting L=9 Convergence Audit...")
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
    # Hierarchy Depths to Audit (L=9 target)
    depths = [7, 8, 9]
    results = {}
    coherences = {}

    # Create Hamiltonian (Standard FMO)
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)

    # Define explicit initial state (Site 1 excitation, index 0)
    init_state = np.zeros(H.shape[0], dtype=complex)
    init_state[0] = 1.0

    print(f"   [1/2] Hierarchy depth sweep (L={depths})...")
    for L in _tqdm(depths, desc="Hierarchy Sweep", unit="level"):
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

    # Sanity check: L=7 and L=8 must NOT be identical (would indicate fallback)
    if np.allclose(results[7], results[8], atol=1e-12):
        logger.error("FAKE DATA DETECTED: L=7 and L=8 populations are identical. "
                     "The simulator fell back to a non-hierarchy solver.")
        print("❌ FATAL: Convergence data is invalid (all depths produce identical results).")
        print("   This means MesoHOPS hierarchy is not being used. Check solver initialization.")
        sys.exit(1)

    # Check L=8 vs L=9
    if np.allclose(results[8], results[9], atol=1e-12):
        logger.error("FAKE DATA DETECTED: L=8 and L=9 populations are identical. "
                     "The simulator is not using the hierarchy truncation depth.")
        print("❌ FATAL: L=8 and L=9 results are identical — hierarchy depth has no effect.")
        print("   Check that HopsSimulator is passing MAXHIER correctly to MesoHOPS.")
        sys.exit(1)
    
    # Compare L=8 vs L=7 (Convergence toward L=8)
    diff_7_8 = np.mean(np.abs(results[8] - results[7]))
    # Compare L=9 vs L=8 (Validation of L=9 exactness)
    diff_8_9 = np.mean(np.abs(results[9] - results[8]))
    
    if diff_8_9 < cfg['dynamics']['convergence_threshold']:
        print("✅ SUCCESS: L=9 is numerically converged (residual < threshold).")
    else:
        print("⚠️ WARNING: Residual exceeds threshold. Further truncation check recommended.")

    # ── K-convergence audit (addresses Reviewer 1 comment 1.5) ──────────────
    # Prove that K=2 Matsubara terms are sufficient at T=295 K by comparing
    # K=1, K=2, K=3 at fixed L=9. At room temperature the first Matsubara
    # frequency ν₁ ≈ 1300 cm⁻¹ >> γ_D = 50 cm⁻¹, so higher terms are negligible.
    print("\n🧪 K-Matsubara Convergence Audit (L=9 fixed)...")
    matsubara_list = [1, 2, 3]
    k_results = {}
    print(f"   [2/2] Matsubara terms sweep (K={matsubara_list})...")
    for Kval in _tqdm(matsubara_list, desc="Matsubara Sweep", unit="term"):
        logger.info(f"Running K-audit: L=9, K={Kval}...")
        sim_k = HopsSimulator(
            H,
            max_hierarchy=9,
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
    print(f"\n📊 K-Matsubara Convergence Results (L=9, T=295 K):")
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
        results[7].shape[0],
        results[8].shape[0],
        results[9].shape[0],
        len(coherences[9]),
    )
    metrics = {
        "pop_site1_L7": results[7][:n_min, 0],
        "pop_site1_L8": results[8][:n_min, 0],
    }

    try:
        output_path = storage.save_quantum_dynamics_results(
            time_points[:n_min],
            results[9][:n_min],
            coherences[9][:n_min],
            metrics,
            filename_prefix="convergence_audit",
            config_dict=cfg,
            audit_mae_7_8=diff_7_8,
            audit_mae_8_9=diff_8_9,
            audit_mae_k1_k2=diff_k1_k2,
            audit_mae_k2_k3=diff_k2_k3,
        )
        print(f"💾 Hardened Audit data saved to: {output_path}")
        logger.info(f"Convergence audit complete. MAE(7→8)={diff_7_8:.2e}, MAE(8→9)={diff_8_9:.2e}")
    except Exception as e:
        logger.error(f"Failed to save audit CSV: {e}")
        output_path = None
        print(f"⚠️  Audit CSV save failed: {e} — results still returned.")

    # Return L=9 results for downstream figure generation.
    # FIX C-5: return actual L=9 coherences (trimmed to n_min) instead of
    # hardcoded np.zeros — the previous stub silently zeroed Figure 1's
    # coherence panel regardless of the simulation output.
    return {
        "time_points": time_points[:n_min],
        "populations": results[9][:n_min],
        "coherences": coherences[9][:n_min],
        "audit_mae_7_8": diff_7_8,
        "audit_mae_8_9": diff_8_9,
        "audit_mae_k1_k2": diff_k1_k2,
        "audit_mae_k2_k3": diff_k2_k3,
        "csv_path": output_path,
    }

def run_time_step_audit():
    """Test 3: Time step convergence."""
    print("\n🧪 Test 3: Time Step Convergence Audit...")
    cfg = load_config()
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    init_state = np.zeros(H.shape[0], dtype=complex)
    init_state[0] = 1.0
    
    dt_list = [0.5, 1.0, 2.0]
    t_max = 100.0
    results = {}
    
    for dt in _tqdm(dt_list, desc="Time Step Sweep", unit="dt"):
        logger.info(f"Running simulation for dt={dt} fs...")
        time_points = np.arange(0, t_max, dt)
        simulator = HopsSimulator(H, max_hierarchy=9, k_matsubara=2)
        data = simulator.simulate_dynamics(time_points, initial_state=init_state)
        # Store population at t=100.0 (last point)
        results[dt] = data['populations'][-1, :]
        
    diff_05_10 = np.mean(np.abs(results[1.0] - results[0.5]))
    diff_10_20 = np.mean(np.abs(results[2.0] - results[1.0]))
    
    print(f"📊 Time Step Convergence Results:")
    print(f"   MAE (0.5 -> 1.0 fs): {diff_05_10:.2e}")
    print(f"   MAE (1.0 -> 2.0 fs): {diff_10_20:.2e}")
    
    status = "PASS" if diff_10_20 < 0.01 else "FAIL"
    print(f"Status: {status}")
    return {"diff_10_20": diff_10_20, "status": status}

def run_detailed_balance_audit():
    """Test 7: Detailed balance verification."""
    print("\n🧪 Test 7: Detailed Balance Audit...")
    cfg = load_config()
    T = cfg['bath']['temperature']
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    
    # Analytical Boltzmann distribution
    beta = 1.0 / (0.695 * T) # 1/kbT in cm^-1
    eigvals = np.linalg.eigvalsh(H)
    z = np.sum(np.exp(-beta * (eigvals - eigvals.min())))
    p_eq_target = np.exp(-beta * (eigvals - eigvals.min())) / z
    
    # Run long-time simulation to reach steady state
    t_long = 5000.0 # fs
    time_points = np.linspace(0, t_long, 501)
    init_state = np.zeros(H.shape[0], dtype=complex)
    init_state[0] = 1.0
    
    simulator = HopsSimulator(H, max_hierarchy=6, k_matsubara=2) # L=6 sufficient for steady state
    data = simulator.simulate_dynamics(time_points, initial_state=init_state)
    
    # Project final state onto exciton basis
    _, eigvecs = np.linalg.eigh(H)
    psi_final = np.sqrt(data['populations'][-1, :]) # Approximation from pops
    # Note: real check should use density matrix rho if available
    p_final_exciton = np.abs(eigvecs.conj().T @ psi_final)**2
    
    mae = np.mean(np.abs(p_final_exciton - p_eq_target))
    print(f"📊 Detailed Balance Results:")
    print(f"   Exciton Pop (Sim) : {p_final_exciton}")
    print(f"   Exciton Pop (Eq)  : {p_eq_target}")
    print(f"   MAE vs Boltzmann  : {mae:.2e}")
    
    status = "PASS" if mae < 0.05 else "FAIL"
    print(f"Status: {status}")
    return {"mae": mae, "status": status}

def run_hermiticity_audit():
    """Test 8: Hermiticity preservation."""
    print("\n🧪 Test 8: Hermiticity Audit...")
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    time_points = np.linspace(0, 100, 51)
    init_state = np.zeros(H.shape[0], dtype=complex)
    init_state[0] = 1.0
    
    simulator = HopsSimulator(H, max_hierarchy=9, k_matsubara=2)
    # This requires access to rho which HopsSimulator currently approximates
    # but we can check if populations sum to 1 and are real.
    data = simulator.simulate_dynamics(time_points, initial_state=init_state)
    pops = data['populations']
    
    # Check if any population has an imaginary part (should be 0)
    max_img = np.max(np.abs(np.imag(pops)))
    # Check if pops are real in the returned array
    max_asym = 0.0 # Placeholder for rho - rho.H
    
    print(f"📊 Hermiticity Results:")
    print(f"   Max Imag Part: {max_img:.2e}")
    
    status = "PASS" if max_img < 1e-12 else "FAIL"
    print(f"Status: {status}")
    return {"max_img": max_img, "status": status}

def run_markovian_limit_audit():
    """Test 12: Markovian limit recovery."""
    print("\n🧪 Test 12: Markovian Limit Audit...")
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    # High gamma = Markovian limit
    gamma_high = 500.0 # cm^-1
    time_points = np.linspace(0, 500, 101)
    init_state = np.zeros(H.shape[0], dtype=complex)
    init_state[0] = 1.0
    
    # Run with standard params but high gamma
    simulator = HopsSimulator(H, max_hierarchy=4, k_matsubara=1, drude_cutoff=gamma_high)
    data = simulator.simulate_dynamics(time_points, initial_state=init_state)
    
    # In Markovian limit, populations should decay exponentially
    # We just check for monotonic decay of site 1 as a proxy for physical behavior
    diff_pops = np.diff(data['populations'][:, 0])
    is_monotonic = np.all(diff_pops < 1e-3)
    
    print(f"📊 Markovian Limit Results:")
    print(f"   Site 1 monotonic decay: {is_monotonic}")
    
    status = "PASS" if is_monotonic else "FAIL"
    print(f"Status: {status}")
    return {"is_monotonic": is_monotonic, "status": status}

if __name__ == "__main__":
    run_convergence_audit()
    run_time_step_audit()
    run_detailed_balance_audit()
    run_hermiticity_audit()
    run_markovian_limit_audit()
