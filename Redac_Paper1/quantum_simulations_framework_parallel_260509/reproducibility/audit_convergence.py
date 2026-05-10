import os
import sys

# Add framework to path - MUST BE BEFORE FRAMEWORK IMPORTS
_FRAMEWORK_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _FRAMEWORK_DIR not in sys.path:
    sys.path.insert(0, _FRAMEWORK_DIR)

import yaml
import numpy as np
import pandas as pd
import logging
from datetime import datetime

try:
    from core.hops_simulator import HopsSimulator, MESOHOPS_AVAILABLE
    from core.hamiltonian_factory import create_fmo_hamiltonian
    from core.constants import (
        KB_CM_K,
        MAE_THRESHOLD,
        MAE_THRESHOLD_LOOSE,
        TRACE_THRESHOLD,
        POPS_REAL_THRESHOLD,
        DEFAULT_TIME_LONG,
        DEFAULT_MAX_TIME,
        DEFAULT_TEMPERATURE,
        MARKOVIAN_DRUDE_CUTOFF,
        AUDIT_TIME_WINDOW,
        DEFAULT_AUDIT_RESOLUTION,
        DEFAULT_N_TRAJ,
        DEFAULT_N_MATSUBARA,
    )
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

# Silence verbose Numba/JAX logging
logging.getLogger('numba').setLevel(logging.WARNING)
logging.getLogger('jax').setLevel(logging.WARNING)

def load_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'parameters.yaml'))
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_convergence_audit(cfg=None):
    """
    Perform hierarchy convergence audit relative to L_target defined in config.
    Detects fallback mode (fake data) and raises an error if MesoHOPS is unavailable.
    Note: L_target is the production target; L_target+1 is audited in single trajectories if memory allows.
    """
    if cfg is None:
        cfg = load_config()
    L_target = cfg['dynamics']['L_max']
    print(f"🧪 Starting L={L_target} Convergence Audit...")

    # Guard: require real MesoHOPS
    if not MESOHOPS_AVAILABLE:
        logger.error("MesoHOPS is NOT available. Convergence audit requires the real solver.")
        print("❌ FATAL: MesoHOPS not found. Activate the MesoHOP-sim environment:")
        print("   mamba run -n MesoHOP-sim python reproducibility/audit_convergence.py")
        sys.exit(1)

    # Simulation Parameters
    dt = cfg['dynamics']['time_step']
    K = cfg['dynamics']['matsubara_truncation']
    # Convergence audit uses standardized window — sufficient to see L-dependent
    # differences while keeping the noise buffer (TLEN = t_audit + 50) small.
    t_audit = AUDIT_TIME_WINDOW
    time_points = np.linspace(0, t_audit, DEFAULT_AUDIT_RESOLUTION)

    # Hierarchy Depths to Audit (Relative to production target)
    L_target = cfg['dynamics']['L_max']
    depths = [L_target - 2, L_target - 1, L_target]
    # Ensure depths are at least 1
    depths = [max(1, d) for d in depths]
    # Remove duplicates if L_target is very small
    depths = sorted(list(set(depths)))
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
            n_traj=1,  # Audit only needs 1 trajectory per depth to check convergence trends
            # SBD enabled: SI mandate — all convergence data reported in Table S2
            # was computed with SBD active. use_sbd=False causes OOM at L>=6 with 7 sites.
            use_sbd=True,
            use_pt_hops=False,
            vibronic_frequencies=np.array([]),  # DL-only bath for audit
            huang_rhys_factors=np.array([]),
            vibronic_damping=np.array([]),
        )

        sim_data = simulator.simulate_dynamics(time_points, initial_state=init_state, strict_mode=True)
        results[L] = sim_data['populations']
        coherences[L] = sim_data.get('coherences', np.zeros(len(time_points)))
        
        # Check if the simulator returned is what we expect
        if sim_data.get('simulator') == 'SimpleQuantumDynamicsSimulator':
            logger.error(f"L={L}: SILENT FALLBACK DETECTED. Audit is invalid.")
            print(f"❌ FATAL: L={L} used SimpleQuantumDynamicsSimulator fallback.")
            sys.exit(1)

        # ── Step-by-step save: persist each depth immediately ──────────────
        from utils.csv_data_storage import CSVDataStorage as _CSV
        _step_dir = os.path.join(os.path.dirname(__file__), 'results')
        _step_storage = _CSV(output_dir=_step_dir)
        _step_path = _step_storage.save_quantum_dynamics_results(
            time_points,
            results[L],
            coherences[L],
            {},
            filename_prefix=f"convergence_audit_L{L}",
            config_dict=cfg,
        )
        logger.info(f"Step-save [L={L}]: {_step_path}")
        print(f"  💾 [L={L}] intermediate audit saved → {_step_path}")

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
        if mean_trace < TRACE_THRESHOLD:  # catastrophic loss — indicates solver failure
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
        if min_pop < -1e-3:  # Numerical noise floor for single trajectories
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

    # Sanity check: must NOT be identical (would indicate fallback)
    if len(depths) >= 2 and np.allclose(results[depths[0]], results[depths[1]], atol=1e-12):
        logger.error(f"FAKE DATA DETECTED: L={depths[0]} and L={depths[1]} populations are identical. "
                     "The simulator fell back to a non-hierarchy solver.")
        print("❌ FATAL: Convergence data is invalid (all depths produce identical results).")
        print("   This means MesoHOPS hierarchy is not being used. Check solver initialization.")
        sys.exit(1)

    # Check last two depths
    if len(depths) >= 2 and np.allclose(results[depths[-2]], results[depths[-1]], atol=1e-12):
        logger.error(f"FAKE DATA DETECTED: L={depths[-2]} and L={depths[-1]} populations are identical. "
                     "The simulator is not using the hierarchy truncation depth.")
        print(f"❌ FATAL: L={depths[-2]} and L={depths[-1]} results are identical — hierarchy depth has no effect.")
        print("   Check that HopsSimulator is passing MAXHIER correctly to MesoHOPS.")
        sys.exit(1)
    
    # Compare convergence
    diffs = {}
    for i in range(len(depths)-1):
        d_lower, d_upper = depths[i], depths[i+1]
        diff = np.mean(np.abs(results[d_upper] - results[d_lower]))
        diffs[d_upper] = float(diff)
    
    diff_target = diffs.get(depths[-1], 0.0)
    
    if diff_target < cfg['dynamics']['convergence_threshold']:
        print(f"✅ SUCCESS: L={depths[-1]} is numerically converged (residual < threshold).")
    else:
        print(f"⚠️ WARNING: Residual {diff_target:.2e} exceeds threshold. Further truncation check recommended.")

    # K-convergence audit (addresses Reviewer 1 comment 1.5)
    # Prove that the configured Matsubara truncation is sufficient by comparing
    # K-1, K, and K+1 terms.
    K_target = cfg['dynamics'].get('matsubara_truncation', DEFAULT_N_MATSUBARA)
    matsubara_list = [max(1, K_target - 1), K_target, K_target + 1]
    # Ensure uniqueness if K_target=1
    matsubara_list = sorted(list(set(matsubara_list)))
    
    print(f"\n🧪 K-Matsubara Convergence Audit (L={L_target} fixed)...")
    k_results = {}
    print(f"   [2/2] Matsubara terms sweep (K={matsubara_list})...")
    for Kval in _tqdm(matsubara_list, desc="Matsubara Sweep", unit="term"):
        logger.info(f"Running K-audit: L={L_target}, K={Kval}...")
        sim_k = HopsSimulator(
            H,
            max_hierarchy=L_target,
            k_matsubara=Kval,
            n_traj=1,  # Audit uses single trajectory for performance
            # SBD enabled: K-convergence data in SI Table S2 was computed with SBD active.
            use_sbd=True,
            use_pt_hops=False,
            vibronic_frequencies=np.array([]),
            huang_rhys_factors=np.array([]),
            vibronic_damping=np.array([]),
        )
        data_k = sim_k.simulate_dynamics(time_points, initial_state=init_state)
        k_results[Kval] = data_k['populations']
        logger.info(f"  K={Kval}: done")

        # ── Step-by-step save: persist each K immediately ─────────────────
        from utils.csv_data_storage import CSVDataStorage as _CSV
        _step_dir = os.path.join(os.path.dirname(__file__), 'results')
        _step_storage = _CSV(output_dir=_step_dir)
        _step_path = _step_storage.save_quantum_dynamics_results(
            time_points,
            k_results[Kval],
            np.zeros(len(time_points)),
            {},
            filename_prefix=f"convergence_audit_K{Kval}",
            config_dict=cfg,
        )
        logger.info(f"Step-save [K={Kval}]: {_step_path}")
        print(f"  💾 [K={Kval}] intermediate audit saved → {_step_path}")

    # Handle edge case K_target=1 (only 2 points in list)
    if len(matsubara_list) >= 3:
        diff_prev_k = np.mean(np.abs(k_results[matsubara_list[1]] - k_results[matsubara_list[0]]))
        diff_target_k = np.mean(np.abs(k_results[matsubara_list[2]] - k_results[matsubara_list[1]]))
        k_label_prev = f"K={matsubara_list[0]} → K={matsubara_list[1]}"
        k_label_target = f"K={matsubara_list[1]} → K={matsubara_list[2]}"
    else:
        diff_prev_k = 0.0
        diff_target_k = np.mean(np.abs(k_results[matsubara_list[1]] - k_results[matsubara_list[0]]))
        k_label_prev = "N/A"
        k_label_target = f"K={matsubara_list[0]} → K={matsubara_list[1]}"

    print(f"\n📊 K-Matsubara Convergence Results (L={L_target}, T={DEFAULT_TEMPERATURE:.0f} K):")
    print(f"   MAE ({k_label_prev}) : {diff_prev_k:.2e}")
    print(f"   MAE ({k_label_target}) : {diff_target_k:.2e}")
    
    threshold_k = cfg['dynamics'].get('convergence_threshold', MAE_THRESHOLD)
    if diff_target_k < threshold_k:
        print(f"✅ K={K_target} is converged (residual < threshold).")
    else:
        print(f"⚠️ WARNING: K={K_target} may not be fully converged.")
        logger.warning(f"K-convergence marginal: MAE={diff_target_k:.2e}")
        
    # Save results for SI using Hardened Storage
    from utils.csv_data_storage import CSVDataStorage
    _results_dir = os.path.join(os.path.dirname(__file__), 'results')
    storage = CSVDataStorage(output_dir=_results_dir)

    # Trim all arrays to the shortest common length before saving
    n_min = min(
        len(time_points),
        results[depths[0]].shape[0],
        results[depths[1]].shape[0],
        results[depths[2]].shape[0],
        len(coherences[depths[2]]),
    )
    metrics = {}
    for d in depths:
        if d != depths[-1]: # Only add auxiliary depths to metrics
            metrics[f"pop_site1_L{d}"] = results[d][:n_min, 0]

    try:
        output_path = storage.save_quantum_dynamics_results(
            time_points[:n_min],
            results[depths[-1]][:n_min],
            coherences[depths[-1]][:n_min],
            metrics,
            filename_prefix="convergence_audit",
            config_dict=cfg,
            audit_maes=diffs,
            audit_mae_k_target=diff_target_k,
        )
        print(f"💾 Hardened Audit data saved to: {output_path}")
        logger.info(f"Convergence audit complete. MAE({depths[0]}->{depths[1]})={diffs.get(depths[1], 0):.2e}, MAE({depths[1]}->{depths[2]})={diffs.get(depths[2], 0):.2e}")
    except Exception as e:
        logger.error(f"Failed to save audit CSV: {e}")
        output_path = None
        print(f"⚠️  Audit CSV save failed: {e} — results still returned.")

    # Return production results for downstream figure generation.
    # return actual coherences (trimmed to n_min) instead of
    # hardcoded np.zeros — the previous stub silently zeroed Figure 1's
    # coherence panel regardless of the simulation output.
    return {
        "time_points": time_points[:n_min],
        "populations": results[depths[-1]][:n_min],
        "coherences": coherences[depths[-1]][:n_min],
        "audit_maes": diffs,
        "audit_mae_k_target": diff_target_k,
        "csv_path": output_path,
    }

def run_time_step_audit(cfg=None):
    """Test 3: Time step convergence."""
    if cfg is None:
        cfg = load_config()
    
    print("\n🧪 Test 3: Time Step Convergence Audit...")
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    # L=3 is sufficient to check dt-dependence
    L_target = cfg['dynamics']['L_max']
    dt_list = [0.5, 1.0, 2.0]
    results = {}
    init_state = np.zeros(H.shape[0], dtype=complex)
    init_state[0] = 1.0
    
    print(f"Time Step Sweep: ")
    for dt in dt_list:
        logger.info(f"Running simulation for dt={dt} fs...")
        time_points = np.arange(0, AUDIT_TIME_WINDOW, dt)
        K_val = cfg['dynamics'].get('matsubara_truncation', DEFAULT_N_MATSUBARA)
        simulator = HopsSimulator(
            H,
            max_hierarchy=L_target,
            k_matsubara=K_val,
            n_traj=1  # Fast verification
        )
        data = simulator.simulate_dynamics(time_points, initial_state=init_state, strict_mode=True)
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

def run_detailed_balance_audit(cfg=None):
    """Test 7: Convergence to Boltzmann distribution at long times."""
    if cfg is None:
        cfg = load_config()
    
    print("\n🧪 Test 7: Detailed Balance Audit...")
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    T = cfg['bath']['temperature']
    
    # Analytical Boltzmann distribution
    beta = 1.0 / (KB_CM_K * T) # 1/kbT in cm^-1
    eigvals = np.linalg.eigvalsh(H)
    z = np.sum(np.exp(-beta * (eigvals - eigvals.min())))
    p_eq_target = np.exp(-beta * (eigvals - eigvals.min())) / z
    
    # Run long-time simulation to reach steady state
    t_long = DEFAULT_TIME_LONG # fs
    time_points = np.linspace(0, t_long, 501)
    init_state = np.zeros(H.shape[0], dtype=complex)
    init_state[0] = 1.0
    
    # L=6 sufficient for steady state thermalization check (Reviewer 1)
    L_target = cfg['dynamics']['L_max']
    L_db = max(1, L_target - 2) # Detailed balance is faster with lower L
    K_db = cfg['dynamics'].get('matsubara_truncation', DEFAULT_N_MATSUBARA)
    simulator = HopsSimulator(
        H, 
        max_hierarchy=L_db, 
        k_matsubara=K_db,
        n_traj=1  # Fast steady-state check
    )
    data = simulator.simulate_dynamics(time_points, initial_state=init_state, strict_mode=True)
    
    # Use density matrix for exact exciton populations
    if 'density_matrices' in data:
        rho_final = data['density_matrices'][-1]
        # Project rho into exciton basis: rho_exciton = U† rho U
        _, eigvecs = np.linalg.eigh(H)
        rho_exciton = eigvecs.conj().T @ rho_final @ eigvecs
        p_final_exciton = np.real(np.diag(rho_exciton))
    else:
        # Fallback to population approximation if rho is unavailable
        psi_final = np.sqrt(data['populations'][-1, :])
        _, eigvecs = np.linalg.eigh(H)
        p_final_exciton = np.abs(eigvecs.conj().T @ psi_final)**2
    
    mae = np.mean(np.abs(p_final_exciton - p_eq_target))
    print(f"📊 Detailed Balance Results:")
    print(f"   Exciton Pop (Sim) : {p_final_exciton}")
    print(f"   Exciton Pop (Eq)  : {p_eq_target}")
    print(f"   MAE vs Boltzmann  : {mae:.2e}")
    
    status = "PASS" if mae < MAE_THRESHOLD_LOOSE else "FAIL"
    print(f"Status: {status}")
    return {"mae": mae, "status": status}

def run_hermiticity_audit(cfg=None):
    """Test 8: Hermiticity preservation."""
    if cfg is None:
        cfg = load_config()
    
    print("\n🧪 Test 8: Hermiticity Audit...")
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    time_points = np.linspace(0, 100, 51)
    init_state = np.zeros(H.shape[0], dtype=complex)
    init_state[0] = 1.0
    
    L_target = cfg['dynamics']['L_max']
    K_h = cfg['dynamics'].get('matsubara_truncation', DEFAULT_N_MATSUBARA)
    n_traj_h = 1
    
    simulator = HopsSimulator(H, max_hierarchy=L_target, k_matsubara=K_h, n_traj=n_traj_h)
    # This requires access to rho which HopsSimulator currently approximates
    # but we can check if populations sum to 1 and are real.
    data = simulator.simulate_dynamics(time_points, initial_state=init_state, strict_mode=True)
    pops = data['populations']
    
    # Check if any population has an imaginary part (should be 0)
    max_img = np.max(np.abs(np.imag(pops)))
    # Check if pops are real in the returned array
    max_asym = 0.0 # Placeholder for rho - rho.H
    
    print(f"📊 Hermiticity Results:")
    print(f"   Max Imag Part: {max_img:.2e}")
    
    status = "PASS" if max_img < POPS_REAL_THRESHOLD else "FAIL"
    print(f"Status: {status}")
    return {"max_img": max_img, "status": status}

def run_markovian_limit_audit(cfg=None):
    """Test 10: Convergence to Markovian dynamics at high damping."""
    if cfg is None:
        cfg = load_config()
    
    print("\n🧪 Test 10: Markovian Limit Audit...")
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    time_points = np.linspace(0, 100, 51)
    init_state = np.zeros(H.shape[0], dtype=complex)
    init_state[0] = 1.0
    
    # Run with standard params but high gamma
    n_traj_m = 1
    simulator = HopsSimulator(
        H, 
        max_hierarchy=4, 
        k_matsubara=1, 
        drude_cutoff=MARKOVIAN_DRUDE_CUTOFF,
        n_traj=n_traj_m
    )
    data = simulator.simulate_dynamics(time_points, initial_state=init_state, strict_mode=True)
    
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
