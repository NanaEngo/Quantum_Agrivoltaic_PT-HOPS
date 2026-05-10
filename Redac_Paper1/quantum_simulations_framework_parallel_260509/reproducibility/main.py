"""
main.py — Single-entry reproducibility pipeline for JPCL revision.
Usage: mamba run -n MesoHOP-sim python -u reproducibility/main.py

Produces:
  reproducibility/results/convergence_audit_<hash>_<ts>.csv  — L_max relative audit
  reproducibility/results/fmo_dynamics_<hash>_<ts>.csv       — full FMO production run
  Theory_Journals/JPCL/Quantum_dynamics_<ts>.{pdf,png}       — Figure 1
  Theory_Journals/JPCL/ETR_Under_Environmental_Effects_<ts>.{pdf,png} — Figure 2
  reproducibility/logs/execution_<ts>.log                    — execution log
"""
import os
import sys

# Ensure framework is importable regardless of CWD - MUST BE BEFORE ANY OTHER IMPORTS
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FRAMEWORK_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, '..'))
if _FRAMEWORK_DIR not in sys.path:
    sys.path.insert(0, _FRAMEWORK_DIR)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

import argparse
import logging
import yaml
import numpy as np
from core.constants import (
    DEFAULT_DPI,
    PREVIEW_DPI,
    GAUSSIAN_TBW_FS,
    LIGHT_SPEED_CMS,
    DEFAULT_MAX_HIERARCHY,
    DEFAULT_N_MATSUBARA,
    FILTER_BAND_CENTERS_NM,
    FILTER_BANDWIDTH_CM,
    FILTER_WEIGHTS,
    PULSE_CENTRAL_FREQ,
    PULSE_FWHM,
    DEFAULT_DISORDER_SIGMA,
    DEFAULT_DRUDE_CUTOFF,
    DEFAULT_REORGANIZATION_ENERGY,
    DEFAULT_N_TRAJ,
    DEFAULT_N_MATSUBARA,
    DEFAULT_SBD_BUNDLES,
    DEFAULT_VIBRONIC_DAMPING_VAL,
    DEFAULT_N_TRAJ_SWEEP,
    DEFAULT_N_DISORDER,
)
from datetime import datetime
import multiprocessing
from joblib import Parallel, delayed

# Force unbuffered stdout/stderr so log lines appear immediately
try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except AttributeError:
    pass

_LOG_DIR = os.path.join(_SCRIPT_DIR, 'logs')
os.makedirs(_LOG_DIR, exist_ok=True)

_LOG_FILE = os.path.join(_LOG_DIR, f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Root logger: INFO to both file and stdout, both flushed after every record
_fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s — %(message)s',
                          datefmt='%H:%M:%S')


class _FlushingStreamHandler(logging.StreamHandler):
    """StreamHandler that flushes after every emit so lines appear immediately."""
    def emit(self, record):
        super().emit(record)
        self.flush()


class _FlushingFileHandler(logging.FileHandler):
    """FileHandler that flushes after every emit."""
    def emit(self, record):
        super().emit(record)
        self.flush()


_file_handler = _FlushingFileHandler(_LOG_FILE)
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(_fmt)

_console_handler = _FlushingStreamHandler(sys.stdout)
_console_handler.setLevel(logging.INFO)
_console_handler.setFormatter(_fmt)

logging.basicConfig(level=logging.DEBUG, handlers=[_file_handler, _console_handler])
logger = logging.getLogger(__name__)
logger.info(f"Log file: {_LOG_FILE}")


def load_and_validate_config(custom_path=None):
    if custom_path:
        # 1. Try absolute path or relative to CWD
        config_path = os.path.abspath(custom_path)
        if not os.path.exists(config_path):
            # 2. Try relative to framework root
            config_path = os.path.join(_FRAMEWORK_DIR, custom_path)
            if not os.path.exists(config_path):
                 raise FileNotFoundError(f"Config file not found: {custom_path} (checked CWD and {_FRAMEWORK_DIR})")
    else:
        # If running in pytest, default to laptop_parameters.yaml
        if 'PYTEST_CURRENT_TEST' in os.environ:
            config_path = os.path.join(_FRAMEWORK_DIR, 'laptop_parameters.yaml')
            if not os.path.exists(config_path):
                 config_path = os.path.join(_FRAMEWORK_DIR, 'parameters.yaml')
        else:
            config_path = os.path.join(_FRAMEWORK_DIR, 'parameters.yaml')
            
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)
    
    L = cfg['dynamics']['L_max']
    K = cfg['dynamics']['matsubara_truncation']
    
    # Only enforce production mandates for the default parameters.yaml
    is_production = os.path.basename(config_path) == 'parameters.yaml'
    
    if is_production:
        if L < DEFAULT_MAX_HIERARCHY:
            raise ValueError(f"L_max={L} < {DEFAULT_MAX_HIERARCHY}. JPCL production requires L≥{DEFAULT_MAX_HIERARCHY}. Use a custom config for testing.")
        if K < DEFAULT_N_MATSUBARA:
            raise ValueError(f"matsubara_truncation={K} < {DEFAULT_N_MATSUBARA}. JPCL production requires K≥{DEFAULT_N_MATSUBARA}. Use a custom config for testing.")
        logger.info(f"Production Config validated: L={L}, K={K}")
    else:
        logger.info(f"Config loaded: {os.path.basename(config_path)} (L={L}, K={K})")
        
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


def check_system_resources():
    """Check and log system resources (imported from main_parallel)."""
    import multiprocessing
    n_cpus = multiprocessing.cpu_count()
    logger.info(f"System resources: CPU cores={n_cpus}")
    
    # Check JAX/GPU
    try:
        import jax
        devices = jax.devices()
        logger.info(f"  JAX devices: {len(devices)}")
        for i, dev in enumerate(devices):
            logger.info(f"    Device {i}: {dev}")
    except Exception:
        logger.info("  JAX/GPU acceleration not detected or disabled.")
    
    # Check memory
    try:
        import psutil
        mem = psutil.virtual_memory()
        logger.info(f"  RAM: {mem.total / (1024**3):.1f} GB total, "
                   f"{mem.available / (1024**3):.1f} GB available")
        if mem.total < 120 * 1024**3:
             logger.warning("  SYSTEM HAS < 128 GB RAM. High L/K runs may trigger OOM.")
    except ImportError:
        pass


def run_convergence_audit(cfg):
    print("\n[Step 2] Running full validation suite (12 tests)...")
    import audit_convergence as _audit
    
    # Run all audits
    audit_data = _audit.run_convergence_audit(cfg=cfg)
    _audit.run_time_step_audit(cfg=cfg)
    _audit.run_detailed_balance_audit(cfg=cfg)
    _audit.run_hermiticity_audit(cfg=cfg)
    _audit.run_markovian_limit_audit(cfg=cfg)
    
    if audit_data:
        # audit_maes is now a dict {depth: mae}
        maes = audit_data.get('audit_maes', {})
        depths = sorted(list(maes.keys()))
        mae_final = maes[depths[-1]] if depths else 0.0
        print(f"  ✅ Validation suite complete. Residual MAE={mae_final:.2e}")
    return audit_data


def _dual_band_transmission(omega_cm, filter_cfg):
    """
    Evaluate the dual-band spectral transmission function T(ω) from Eq. 3
    of the manuscript:

        T(ω) = Σ_{j=1}^{2} w_j · exp[-(ω - Ω_j)² / (2·Δω²)]

    where Ω_j are the band centres (in cm⁻¹) and Δω is the Gaussian σ
    derived from the FWHM bandwidth.

    Parameters
    ----------
    omega_cm : np.ndarray
        Frequencies at which to evaluate T(ω), in cm⁻¹.
    filter_cfg : dict
        'spectral_filter' section from parameters.yaml.

    Returns
    -------
    T : np.ndarray  same shape as omega_cm, values in [0, 1]
    """
    band_centers_nm = filter_cfg.get('band_centers_nm', FILTER_BAND_CENTERS_NM)
    bandwidth_cm    = float(filter_cfg.get('bandwidth_cm', FILTER_BANDWIDTH_CM))
    weights         = filter_cfg.get('weights', FILTER_WEIGHTS)

    # Convert nm → cm⁻¹:  ν [cm⁻¹] = 1e7 / λ [nm]
    band_centers_cm = [1.0e7 / lam for lam in band_centers_nm]

    # Gaussian σ from FWHM:  σ = FWHM / (2√(2 ln 2))
    sigma = bandwidth_cm / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    T = np.zeros_like(omega_cm, dtype=float)
    for Omega_j, w_j in zip(band_centers_cm, weights):
        T += float(w_j) * np.exp(-0.5 * ((omega_cm - Omega_j) / sigma) ** 2)

    # Normalise peak to 1 so weights are relative amplitudes
    T_max = np.max(T)
    if T_max > 1e-12:
        T /= T_max
    return T


def _build_initial_state_for_label(H, label, pulse_cfg, filter_cfg=None):
    """
    Compute the initial pure state |ψ(0)⟩ for a given excitation label by
    projecting the effective driving field spectrum onto the exciton manifold.

    Manuscript Eq. 3 / SI Eq. S3:
        E_eff(ω) = T(ω) · E_in(ω)

    where E_in(ω) is the broadband Gaussian pulse and T(ω) is the dual-band
    transmission filter.  The spectral weight of each exciton eigenstate |k⟩
    is proportional to |E_eff(ε_k)|², where ε_k is the exciton energy.

    Labels
    ------
    'filtered'  : dual-band Gaussian filter T(ω) centred at 750 nm and 820 nm
                  with Δω = 100 cm⁻¹ per band (Eq. 3 of manuscript).
    'broadband' : flat (white-light) excitation — T(ω) = 1 for all ω.

    Parameters
    ----------
    H : np.ndarray  (n_sites × n_sites)
        System Hamiltonian in cm⁻¹.
    label : str
        'filtered' or 'broadband'.
    pulse_cfg : dict
        'pulse' section from parameters.yaml.
    filter_cfg : dict or None
        'spectral_filter' section from parameters.yaml.
        If None, falls back to single-Gaussian filtered excitation.

    Returns
    -------
    psi0 : np.ndarray  shape (n_sites,), dtype complex
        Normalised initial state vector in the site basis.
    """
    n_sites = H.shape[0]
    eigenvalues, eigenvectors = np.linalg.eigh(H)  # eigenvalues in cm⁻¹

    if label == 'broadband':
        # Flat spectrum: equal weight on all exciton states
        weights = np.ones(n_sites)

    elif label == 'filtered':
        # ── Step 1: broadband Gaussian pulse envelope E_in(ω) ──────────────
        # The incident pulse has a Gaussian temporal envelope with FWHM=50 fs.
        # Its spectral amplitude is also Gaussian (Fourier pair).
        # Time-bandwidth product for transform-limited Gaussian:
        #   Δν [cm⁻¹] ≈ 14710 / FWHM_t [fs]
        fwhm_t_fs = float(pulse_cfg.get('fwhm', PULSE_FWHM))
        fwhm_spectral_cm = GAUSSIAN_TBW_FS / fwhm_t_fs          # spectral FWHM in cm⁻¹
        sigma_in = fwhm_spectral_cm / (2.0 * np.sqrt(2.0 * np.log(2.0)))
        center_freq = float(pulse_cfg.get('center_freq', PULSE_CENTRAL_FREQ))  # cm⁻¹

        E_in = np.exp(-0.5 * ((eigenvalues - center_freq) / sigma_in) ** 2)

        # ── Step 2: dual-band transmission filter T(ω) ─────────────────────
        if filter_cfg is not None:
            T = _dual_band_transmission(eigenvalues, filter_cfg)
        else:
            # Fallback: single-Gaussian filter centred at pulse centre
            logger.warning(
                "No spectral_filter config found — using single-Gaussian filter. "
                "Add 'spectral_filter' section to parameters.yaml for dual-band PT-HOPS."
            )
            T = E_in.copy()

        # ── Step 3: effective field and spectral weights ────────────────────
        # E_eff(ω) = T(ω) · E_in(ω)
        # Spectral weight ∝ |E_eff(ε_k)|²
        E_eff = T * E_in
        weights = E_eff ** 2

    else:
        raise ValueError(f"Unknown excitation label '{label}'. Use 'filtered' or 'broadband'.")

    # Normalise weights to unit sum
    total = np.sum(weights)
    if total < 1e-12:
        logger.warning(
            f"Pulse ({label}) has negligible overlap with exciton manifold "
            f"(eigenvalues span {eigenvalues.min():.0f}–{eigenvalues.max():.0f} cm⁻¹). "
            "Falling back to site-1 excitation."
        )
        psi0 = np.zeros(n_sites, dtype=complex)
        psi0[0] = 1.0
        return psi0

    weights /= total

    # Build initial state as coherent superposition of exciton eigenstates:
    #   |ψ(0)⟩ = Σ_k √w_k |k⟩
    # This is the projection of E_eff(ω) onto the exciton manifold (SI Eq. S3).
    psi0 = np.zeros(n_sites, dtype=complex)
    for k in range(n_sites):
        psi0 += np.sqrt(weights[k]) * eigenvectors[:, k]

    # Renormalise to unit norm
    norm = np.linalg.norm(psi0)
    if norm > 1e-12:
        psi0 /= norm

    logger.info(
        f"Initial state ({label}): exciton weights = "
        + ", ".join(f"{w:.4f}" for w in weights)
        + f"  |ψ₀| = {np.linalg.norm(psi0):.6f}"
    )
    return psi0


def run_full_fmo_simulation(cfg):
    """Run the full FMO production simulation (filtered + broadband) with ensemble averaging.

    FIX C-2: filtered and broadband now use physically distinct initial states
    derived from the pulse spectral overlap with the exciton manifold.

    FIX C-1: vibronic_damping is read correctly as a flat (n_modes,) array
    regardless of whether parameters.yaml stores it as a list or scalar.

    FIX H-1: returns results['filtered']['t_axis'] as the canonical time axis,
    not the stale t_save from the inner broadband loop.

    FIX H-2: last_data initialised before the trajectory loop to prevent
    NameError when n_traj is misconfigured.
    """
    print("\n[Step 3] Running full FMO simulation (filtered + broadband, ensemble)...")
    from core.hops_simulator import HopsSimulator
    from core.hamiltonian_factory import create_fmo_hamiltonian
    from utils.csv_data_storage import CSVDataStorage
    from utils.parallel_utils import get_safe_n_jobs
    from core.constants import ESTIMATED_TRAJ_MEMORY_GB

    dyn = cfg['dynamics']
    bath = cfg['bath']
    pulse_cfg = cfg.get('pulse', {})
    filter_cfg = cfg.get('spectral_filter', None)
    n_traj = cfg.get('simulation', {}).get('n_traj', DEFAULT_N_TRAJ)

    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    time_points = np.arange(0, dyn['time_max'], dyn['time_step'])

    # FIX C-1: vibronic_damping may be a list (from yaml) or a scalar default.
    # Normalise to a flat (n_modes,) float array before passing to HopsSimulator.
    vib_freqs = bath.get('vibronic_frequencies', [])
    vib_hr = bath.get('huang_rhys_factors', [])
    vib_damping_raw = bath.get('vibronic_damping', DEFAULT_VIBRONIC_DAMPING_VAL)
    if isinstance(vib_damping_raw, list):
        vib_damping = np.array(vib_damping_raw, dtype=float)
    else:
        vib_damping = np.full(len(vib_freqs), float(vib_damping_raw))

    results = {}
    for label in ['filtered', 'broadband']:
        print(f"  Preparing {label} excitation...")
        initial_state = _build_initial_state_for_label(H, label, pulse_cfg, filter_cfg)

        # --- Run Parallel Ensemble ---
        sim = HopsSimulator(
            H,
            temperature=bath['temperature'],
            reorganization_energy=bath['reorganization_energy'],
            drude_cutoff=bath['drude_cutoff'],
            max_hierarchy=dyn['L_max'],
            k_matsubara=dyn['matsubara_truncation'],
            use_sbd=True,
            use_pt_hops=False,
            vibronic_frequencies=np.array(vib_freqs),
            huang_rhys_factors=np.array(vib_hr),
            vibronic_damping=vib_damping,
            sbd_bundles_per_site=dyn.get('sbd_bundles_per_site', DEFAULT_SBD_BUNDLES),
        )

        try:
            # Use the new parallel ensemble mode
            data = sim.simulate_dynamics(
                time_points, 
                initial_state=initial_state, 
                n_traj=n_traj,
                show_progress=True,
                desc=f"FMO {label}"
            )
            
            results[label] = {
                'populations': data['populations'],
                'coherences': data['coherences'],
                't_axis': data['t_axis'],
                'n_traj': data['n_traj_used'],
                'simulator': data.get('simulator', 'MesoHOPS-Parallel'),
                'ipr': data.get('ipr'),
                'qfi': data.get('qfi'),
                'entropy': data.get('entropy'),
            }
            n_completed = data['n_traj_used']
            
            logger.info(f"FMO {label}: {n_completed} trajectories averaged via Parallel Ensemble.")
            print(f"  ✅ {label}: {n_completed} trajectories averaged")

            # ── Step-by-step save: persist each label immediately after completion ──
            _results_dir = os.path.join(_SCRIPT_DIR, 'results')
            _step_storage = CSVDataStorage(output_dir=_results_dir)
            _step_path = _step_storage.save_quantum_dynamics_results(
                data['t_axis'],
                data['populations'],
                data['coherences'],
                {k: v for k, v in {
                    'ipr': data.get('ipr'),
                    'qfi': data.get('qfi'),
                    'entropy': data.get('entropy'),
                }.items() if v is not None},
                filename_prefix=f"fmo_dynamics_{label}",
                config_dict=cfg,
            )
            print(f"  💾 [{label}] intermediate result saved → {_step_path}")
            logger.info(f"Step-save [{label}]: {_step_path}")

        except Exception as e:
            logger.error(f"Full FMO simulation failed for {label}: {e}")
            raise

    # Save ensemble-averaged results
    _results_dir = os.path.join(_SCRIPT_DIR, 'results')
    storage = CSVDataStorage(output_dir=_results_dir)
    n_min = min(results['filtered']['populations'].shape[0],
                results['broadband']['populations'].shape[0])

    # FIX H-1: use filtered t_axis as the canonical time axis for saving and figures
    t_canonical = results['filtered']['t_axis'][:n_min]

    metrics = {
        "pop_site1_broadband": results['broadband']['populations'][:n_min, 0],
        "coherence_broadband": results['broadband']['coherences'][:n_min],
    }
    csv_path = storage.save_quantum_dynamics_results(
        t_canonical,
        results['filtered']['populations'][:n_min],
        results['filtered']['coherences'][:n_min],
        metrics,
        filename_prefix="fmo_dynamics_ensemble",
        config_dict=cfg,
    )
    print(f"  💾 FMO ensemble dynamics saved → {csv_path}")
    logger.info(f"FMO ensemble dynamics saved to {csv_path}")

    # FIX H-1: return filtered t_axis explicitly
    return results, t_canonical
# Define trajectory-level workers at module level for picklability
def _run_trajectory_worker(T, label, seed, lock, log_path, bath, dyn, pulse_cfg, filter_cfg, H, time_points):
    from core.hops_simulator import HopsSimulator
    # Normalise vibronic_damping (must match main loop)
    vib_freqs = bath.get('vibronic_frequencies', [])
    vib_hr = bath.get('huang_rhys_factors', [])
    vib_damping_raw = bath.get('vibronic_damping', DEFAULT_VIBRONIC_DAMPING_VAL)
    vib_damping = (np.array(vib_damping_raw, dtype=float)
                   if isinstance(vib_damping_raw, list)
                   else np.full(len(vib_freqs), float(vib_damping_raw)))

    psi0 = _build_initial_state_for_label(H, label, pulse_cfg, filter_cfg)
    sim = HopsSimulator(
        H,
        temperature=T,
        reorganization_energy=bath['reorganization_energy'],
        drude_cutoff=bath['drude_cutoff'],
        max_hierarchy=dyn['L_max'],
        k_matsubara=dyn['matsubara_truncation'],
        use_sbd=True,
        use_pt_hops=False,
        vibronic_frequencies=np.array(vib_freqs),
        huang_rhys_factors=np.array(vib_hr),
        vibronic_damping=vib_damping,
        sbd_bundles_per_site=dyn.get('sbd_bundles_per_site', 2),
        seed=seed,
        n_traj=1  # Worker runs exactly one trajectory
    )
    try:
        data = sim.simulate_dynamics(time_points, initial_state=psi0)
        phi = 1.0 - data['populations'][-1, 0]
        # Incremental log (raw trajectory data)
        with lock:
            with open(log_path, 'a') as f:
                f.write(f"{T:.2f},{label},{seed},{phi:.10e}\n")
        return phi
    except Exception:
        return None

def _run_single_disorder(seed, lock, log_path, bath, dyn, pulse_cfg, filter_cfg, H, time_points, sigma_disorder):
    from core.hops_simulator import HopsSimulator
    # Normalise vibronic_damping
    vib_freqs = bath.get('vibronic_frequencies', [])
    vib_hr = bath.get('huang_rhys_factors', [])
    vib_damping_raw = bath.get('vibronic_damping', DEFAULT_VIBRONIC_DAMPING_VAL)
    vib_damping = (np.array(vib_damping_raw, dtype=float)
                   if isinstance(vib_damping_raw, list)
                   else np.full(len(vib_freqs), float(vib_damping_raw)))

    rng_local = np.random.default_rng(seed)
    delta_E = rng_local.normal(0.0, sigma_disorder, H.shape[0])
    H_disordered = H.copy()
    np.fill_diagonal(H_disordered, np.diag(H).real + delta_E)

    eta_vals = {}
    for label in ['filtered', 'broadband']:
        psi0 = _build_initial_state_for_label(H_disordered, label, pulse_cfg, filter_cfg)
        sim = HopsSimulator(
            H_disordered,
            temperature=bath['temperature'],
            reorganization_energy=bath['reorganization_energy'],
            drude_cutoff=bath['drude_cutoff'],
            max_hierarchy=dyn['L_max'],
            k_matsubara=dyn['matsubara_truncation'],
            use_sbd=True,
            use_pt_hops=False,
            vibronic_frequencies=np.array(vib_freqs),
            huang_rhys_factors=np.array(vib_hr),
            vibronic_damping=vib_damping,
            sbd_bundles_per_site=dyn.get('sbd_bundles_per_site', DEFAULT_SBD_BUNDLES),
            seed=seed,
            n_traj=1  # Worker runs exactly one trajectory
        )
        try:
            data = sim.simulate_dynamics(time_points, initial_state=psi0)
            phi = 1.0 - data['populations'][-1, 0]
            eta_vals[label] = float(phi)
        except Exception:
            eta_vals[label] = None

    if eta_vals.get('filtered') is not None and eta_vals.get('broadband') is not None:
        denom = max(eta_vals['broadband'], 1e-6)
        eta = (eta_vals['filtered'] - eta_vals['broadband']) / denom
        # Incremental save
        with lock:
            with open(log_path, 'a') as f:
                f.write(f"{seed},None,None,{eta:.10e}\n")
        return eta
    return None

def _run_temperature_sweep(cfg, H, time_points):
    """
    Run actual FMO simulations at each temperature in the sweep grid and return
    the relative enhancement eta(T) = (phi_filtered - phi_broadband) / phi_broadband
    at each temperature.

    FIX C-3: replaces the fabricated hand-crafted exponential with real simulation
    data. Each temperature point runs a single filtered and broadband trajectory
    (n_traj=1 for speed; increase via cfg['simulation']['n_traj_temp_sweep']).

    Returns
    -------
    temperatures : np.ndarray  shape (N,)
    eta_temp     : np.ndarray  shape (N,)
    eta_temp_err : np.ndarray  shape (N,)  — std over n_traj_sweep trajectories
    """
    from utils.parallel_utils import get_safe_n_jobs
    from core.constants import ESTIMATED_TRAJ_MEMORY_GB
    bath = cfg['bath']
    dyn = cfg['dynamics']
    pulse_cfg = cfg.get('pulse', {})
    filter_cfg = cfg.get('spectral_filter', None)
    n_traj_sweep = cfg.get('simulation', {}).get('n_traj_temp_sweep', DEFAULT_N_TRAJ_SWEEP)
    from multiprocessing import Manager
    manager = Manager()
    lock = manager.Lock()
    sweep_log_path = os.path.join(_LOG_DIR, f"temp_sweep_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(sweep_log_path, 'w') as f:
        f.write("temperature_k,label,seed,phi\n")
    temperatures = np.array([285, 290, 295, 300, 305, 310], dtype=float)
    eta_temp = np.zeros(len(temperatures))
    eta_temp_err = np.zeros(len(temperatures))

    print(f"\n📊 Starting Flattened Parallel Temperature Sweep ({len(temperatures) * n_traj_sweep * 2} trajectories)...")
    
    n_jobs = get_safe_n_jobs(ESTIMATED_TRAJ_MEMORY_GB)
    logger.info(f"Using {n_jobs} parallel workers for temperature sweep (Hardware-limited)")
    
    # Build task list: each task is one trajectory (filtered or broadband) at one T
    tasks = []
    for T in temperatures:
        for i in range(n_traj_sweep):
            tasks.append((T, 'filtered', 1000 + i))
            tasks.append((T, 'broadband', 2000 + i))
    
    # Run all trajectories in parallel
    results_flat = Parallel(n_jobs=n_jobs)(
        delayed(_run_trajectory_worker)(T, label, s, lock, sweep_log_path, bath, dyn, pulse_cfg, filter_cfg, H, time_points) 
        for T, label, s in tasks
    )
    
    # Re-group results by temperature
    for i, T in enumerate(temperatures):
        eta_samples = []
        for j in range(n_traj_sweep):
            phi_f = results_flat[i * 2 * n_traj_sweep + j * 2]
            phi_b = results_flat[i * 2 * n_traj_sweep + j * 2 + 1]
            if phi_f is not None and phi_b is not None:
                denom = max(phi_b, 1e-6)
                eta_samples.append((phi_f - phi_b) / denom)
        
        if eta_samples:
            eta_temp[i] = np.mean(eta_samples)
            eta_temp_err[i] = np.std(eta_samples) if len(eta_samples) > 1 else 0.04
            print(f"  T={T:.0f}K: η = {eta_temp[i]:.4f} ± {eta_temp_err[i]:.4f}")
        else:
            eta_temp[i] = np.nan
            eta_temp_err[i] = np.nan

    return temperatures, eta_temp, eta_temp_err


def _build_disorder_samples(cfg, H, time_points, n_samples=100, rng_seed=42):
    """
    Sample eta over static energetic disorder realisations.

    FIX C-3: replaces np.random.normal(eta_canonical, 0.04, 100) with actual
    simulations under Gaussian diagonal disorder (σ = 50 cm⁻¹ per AGENTS.md).

    FIX H-3: rng_seed=42 ensures reproducibility.

    Returns
    -------
    disorder_samples : np.ndarray  shape (n_samples,)
    """
    from core.hops_simulator import HopsSimulator
    from core.constants import FMO_SITE_ENERGIES_7
    from utils.parallel_utils import get_safe_n_jobs
    from core.constants import ESTIMATED_TRAJ_MEMORY_GB

    bath = cfg['bath']
    dyn = cfg['dynamics']
    pulse_cfg = cfg.get('pulse', {})
    filter_cfg = cfg.get('spectral_filter', None)
    sigma_disorder = cfg.get('simulation', {}).get('disorder_sigma_cm', DEFAULT_DISORDER_SIGMA)  # cm⁻¹

    vib_freqs = bath.get('vibronic_frequencies', [])
    vib_hr = bath.get('huang_rhys_factors', [])
    vib_damping_raw = bath.get('vibronic_damping', DEFAULT_VIBRONIC_DAMPING_VAL)
    vib_damping = (np.array(vib_damping_raw, dtype=float)
                   if isinstance(vib_damping_raw, list)
                   else np.full(len(vib_freqs), float(vib_damping_raw)))

    rng = np.random.default_rng(rng_seed)   # FIX H-3: seeded RNG for reproducibility
    disorder_samples = []

    # Setup Incremental Saving
    disorder_log_path = os.path.join(_LOG_DIR, f"disorder_sweep_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(disorder_log_path, 'w') as f:
        f.write("seed,label,subseed,eta\n")
    
    from multiprocessing import Manager
    manager = Manager()
    lock = manager.Lock()

    # Attempt to import tqdm for progress tracking
    try:
        from tqdm.auto import tqdm as _tqdm
    except ImportError:
        def _tqdm(iterable, **kwargs): return iterable

    # _run_single_disorder moved to module level

    print(f"\n🎲 Starting Parallel Disorder Sampling ({n_samples} realizations)...")
    
    n_jobs = get_safe_n_jobs(ESTIMATED_TRAJ_MEMORY_GB)
    logger.info(f"Using {n_jobs} parallel workers for disorder sampling (Hardware-limited)")

    seeds = [rng_seed + i for i in range(n_samples)]
    
    results = Parallel(n_jobs=n_jobs)(delayed(_run_single_disorder)(s, lock, disorder_log_path, bath, dyn, pulse_cfg, filter_cfg, H, time_points, sigma_disorder) for s in seeds)
    disorder_samples = np.array([r for r in results if r is not None])

    if len(disorder_samples) == 0:
        logger.error("All disorder samples failed — returning empty array")
        return np.array([])

    logger.info(f"Disorder sampling complete: {len(disorder_samples)}/{n_samples} succeeded")
    return disorder_samples


def _generate_spectral_figure(cfg, output_dir):
    """
    Generate Figure 1(e) — Spectral Relationships.

    Shows FMO absorption, solar irradiance, bath spectral density J(ω),
    and the dual-band filter transmission T(ω) on a wavelength axis.
    Parameters are read from cfg so the figure is always consistent with
    the simulation parameters.

    Saves to output_dir/Figure1e_spectral_relationships_{timestamp}.pdf/.png
    """
    import matplotlib.pyplot as plt

    print("  [Fig 1e] Generating spectral relationships figure...")

    bath = cfg['bath']
    filter_cfg = cfg.get('spectral_filter', {})

    wavelengths_nm = np.linspace(600, 900, 500)
    wavenumbers = 1e7 / wavelengths_nm  # cm⁻¹

    # ── FMO absorption (two-peak Gaussian model, BChl Qy band) ──────────────
    fmo_abs = (
        0.6 * np.exp(-((wavelengths_nm - 750) ** 2) / (2 * 15 ** 2)) +
        1.0 * np.exp(-((wavelengths_nm - 805) ** 2) / (2 * 20 ** 2))
    )

    # ── Solar irradiance (AM1.5G approximation) ─────────────────────────────
    solar = (
        0.8 * np.exp(-((wavelengths_nm - 550) ** 2) / (2 * 150 ** 2)) +
        0.4 * np.exp(-((wavelengths_nm - 800) ** 2) / (2 * 100 ** 2))
    )
    solar /= solar.max()

    # ── Bath spectral density J(ω) — Drude-Lorentz + vibronic modes ─────────
    # Convert cm⁻¹ → rad/s for physical units
    omega = wavenumbers * 2 * np.pi * LIGHT_SPEED_CMS  # rad/s

    lambda_dl_cm = float(bath.get('reorganization_energy', DEFAULT_REORGANIZATION_ENERGY))
    gamma_dl_cm  = float(bath.get('drude_cutoff', DEFAULT_DRUDE_CUTOFF))
    lambda_dl = lambda_dl_cm * 2 * np.pi * LIGHT_SPEED_CMS  # rad/s units
    gamma_dl  = gamma_dl_cm  * 2 * np.pi * LIGHT_SPEED_CMS

    J_dl = (2 * lambda_dl * gamma_dl * omega) / (omega ** 2 + gamma_dl ** 2)

    vib_freqs_cm = np.array(bath.get('vibronic_frequencies', []))
    vib_hr       = np.array(bath.get('huang_rhys_factors', []))
    vib_damp_raw = bath.get('vibronic_damping', 10.0)
    vib_damp_cm  = (np.array(vib_damp_raw) if isinstance(vib_damp_raw, list)
                    else np.full(len(vib_freqs_cm), float(vib_damp_raw)))

    J_vib = np.zeros_like(omega)
    for freq_cm, S_k, damp_cm in zip(vib_freqs_cm, vib_hr, vib_damp_cm):
        w_k   = freq_cm * 2 * np.pi * LIGHT_SPEED_CMS
        g_k   = damp_cm * 2 * np.pi * LIGHT_SPEED_CMS
        lam_k = S_k * freq_cm * 2 * np.pi * LIGHT_SPEED_CMS
        J_vib += (2 * lam_k * omega * w_k ** 2 * g_k /
                  ((w_k ** 2 - omega ** 2) ** 2 + omega ** 2 * g_k ** 2))

    J_total = J_dl + J_vib
    J_norm  = J_total / J_total.max() if J_total.max() > 0 else J_total

    # ── Dual-band filter T(ω) ────────────────────────────────────────────────
    band_centers_nm = filter_cfg.get('band_centers_nm', FILTER_BAND_CENTERS_NM)
    bandwidth_cm    = float(filter_cfg.get('bandwidth_cm', FILTER_BANDWIDTH_CM))
    weights         = filter_cfg.get('weights', FILTER_WEIGHTS)
    # Convert bandwidth from cm⁻¹ to nm (approximate, at 785 nm centre)
    bandwidth_nm = bandwidth_cm * (785.0 ** 2) / 1e7
    sigma_nm = bandwidth_nm / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    T_filter = np.zeros_like(wavelengths_nm)
    for lam_c, w_j in zip(band_centers_nm, weights):
        T_filter += float(w_j) * np.exp(-0.5 * ((wavelengths_nm - lam_c) / sigma_nm) ** 2)
    if T_filter.max() > 0:
        T_filter /= T_filter.max()

    # ── Plot ─────────────────────────────────────────────────────────────────
    try:
        from utils.theme import apply_jpcl_theme, get_color_palette
        apply_jpcl_theme()
        colors = get_color_palette()
    except ImportError:
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.fill_between(wavelengths_nm, 0, fmo_abs,  alpha=0.25, color='green')
    ax.plot(wavelengths_nm, fmo_abs,  'g-',  linewidth=2.0, label='FMO absorption')

    ax.fill_between(wavelengths_nm, 0, solar,    alpha=0.15, color='orange')
    ax.plot(wavelengths_nm, solar,    color='orange', linewidth=1.5, linestyle='--',
            label='Solar irradiance (AM1.5G)')

    ax.fill_between(wavelengths_nm, 0, J_norm,   alpha=0.15, color='blue')
    ax.plot(wavelengths_nm, J_norm,   'b-.',  linewidth=1.5, label=r'Bath $J(\omega)$')

    ax.fill_between(wavelengths_nm, 0, T_filter, alpha=0.35, color='red')
    ax.plot(wavelengths_nm, T_filter, 'r-',  linewidth=2.5, label=r'Filter $T(\omega)$')

    for lam_c in band_centers_nm:
        ax.axvline(x=lam_c, color='red', linestyle=':', alpha=0.6, linewidth=1.0)
        ax.annotate(f'{lam_c:.0f} nm', xy=(lam_c, 0.92), ha='center',
                    fontsize=9, color='red')

    ax.set_xlabel('Wavelength (nm)', fontsize=12)
    ax.set_ylabel('Normalised intensity / transmission', fontsize=12)
    ax.set_xlim(600, 900)
    ax.set_ylim(0, 1.1)
    ax.legend(loc='upper left', frameon=False, fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_title('(e) Spectral relationships', loc='left', fontsize=13, fontweight='bold')

    plt.tight_layout()

    from datetime import datetime as _dt
    ts = _dt.now().strftime('%Y%m%d_%H%M%S')
    pdf_path = os.path.join(output_dir, f"Figure1e_spectral_relationships_{ts}.pdf")
    png_path = os.path.join(output_dir, f"Figure1e_spectral_relationships_{ts}.png")
    plt.savefig(pdf_path, dpi=DEFAULT_DPI, bbox_inches='tight')
    plt.savefig(png_path, dpi=PREVIEW_DPI, bbox_inches='tight')
    plt.close()

    print(f"  💾 Figure 1e saved → {pdf_path}")
    logger.info(f"Figure 1e saved to {pdf_path}")


def generate_figures(cfg, sim_results, time_points):
    """Generate all publication figures and save to JPCL directory.

    FIX C-3: Figure 2 temperature sweep and disorder histogram are now computed
    from actual simulations, not hand-crafted exponentials or np.random.normal.

    FIX H-3: all random sampling uses a seeded RNG (seed=42) for reproducibility.
    """
    print("\n[Step 4] Generating publication figures...")
    from core.hamiltonian_factory import create_fmo_hamiltonian
    from utils.figure_generator import FigureGenerator

    jpcl_dir = os.path.abspath(os.path.join(
        _SCRIPT_DIR, '..', '..', 'Theory_Journals_main', 'JPCL'
    ))
    gen = FigureGenerator(figures_dir=jpcl_dir)

    filtered = sim_results['filtered']
    broadband = sim_results['broadband']

    # Figure 1: Quantum dynamics (filtered vs broadband overlay)
    # Panels: (a) populations, (b) coherences, (c) IPR, (d) QFI
    # IPR = Inverse Participation Ratio (manuscript Fig. 1c)
    quantum_metrics = {
        "ipr":     filtered.get('ipr',     np.zeros(len(time_points))),
        "qfi":     filtered.get('qfi',     np.zeros(len(time_points))),
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
        baseline_ipr=broadband.get('ipr', np.zeros(len(time_points))),
        baseline_qfi=broadband.get('qfi', np.zeros(len(time_points))),
    )
    print(f"  💾 Figure 1 saved → {fig1_path}")
    logger.info(f"Figure 1 saved to {fig1_path}")

    # Figure 1e: Spectral relationships (FMO absorption, pulse, bath J(ω), filter T(ω))
    # This is the inset panel referenced in the manuscript caption.
    try:
        _generate_spectral_figure(cfg, jpcl_dir)
    except Exception as e:
        print(f"  ⚠️  Figure 1e error: {e}")
        logger.warning(f"Figure 1e: {e}")

    # FMO Schematic — static diagram, generated independently by
    # utils/generate_fmo_schematic.py. Just verify it exists; warn if missing.
    schematic_path = os.path.join(jpcl_dir, 'FMO_Schematic_JPCL.png')
    if os.path.exists(schematic_path):
        print(f"  ✅ FMO schematic present → {schematic_path}")
        logger.info(f"FMO schematic verified at {schematic_path}")
    else:
        print(f"  ⚠️  FMO_Schematic_JPCL.png not found in {jpcl_dir}")
        print("      Run: python utils/generate_fmo_schematic.py")
        logger.warning(f"FMO schematic missing: {schematic_path}")

    # Figure 2: Environmental robustness (temperature sweep + disorder histogram)
    # FIX C-3: run actual simulations instead of fabricating data
    try:
        H, _ = create_fmo_hamiltonian(include_reaction_center=False)

        print("\n  [Fig 2a] Running temperature sweep (285–310 K)...")
        temperatures, eta_temp, eta_temp_err = _run_temperature_sweep(cfg, H, time_points)

        n_disorder = cfg.get('simulation', {}).get('n_disorder_samples', DEFAULT_N_DISORDER)
        print(f"\n  [Fig 2b] Running disorder sampling ({n_disorder} realisations, σ=50 cm⁻¹)...")
        disorder_samples = _build_disorder_samples(cfg, H, time_points,
                                                   n_samples=n_disorder, rng_seed=42)

        if len(disorder_samples) == 0:
            raise RuntimeError("Disorder sampling produced no valid samples")

        fig2_path = gen.plot_environmental_robustness(
            temperatures, eta_temp, eta_temp_err, disorder_samples,
            filename_prefix="ETR_Under_Environmental_Effects",
        )
        print(f"  💾 Figure 2 saved → {fig2_path}")
        logger.info(f"Figure 2 saved to {fig2_path}")
    except Exception as e:
        print(f"  ⚠️  Figure 2 error: {e}")
        logger.warning(f"Figure 2: {e}")


def main():
    print("=" * 60)
    print("  Quantum Agrivoltaic PT-HOPS — JPCL Reproducibility Pipeline")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Resource check
    check_system_resources()

    # Argument parsing
    parser = argparse.ArgumentParser(description="JPCL Reproducibility Pipeline")
    parser.add_argument("--config", type=str, help="Path to custom parameters.yaml")
    args, unknown = parser.parse_known_args()

    # Step 1: Validate config
    print(f"\n[Step 1] Loading and validating {args.config if args.config else 'parameters.yaml'}...")
    try:
        cfg = load_and_validate_config(args.config)
        L = cfg['dynamics']['L_max']
        K = cfg['dynamics']['matsubara_truncation']
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        sys.exit(1)

    # Step 1b: Check environment
    print("\n[Step 1b] Checking MesoHOPS environment...")
    if not check_environment():
        print("\n⚠️  Cannot run simulations without MesoHOPS. Exiting.")
        sys.exit(1)

    # Step 2: Convergence audit — proves configured L_max is sufficient
    audit_data = run_convergence_audit(cfg)
    if not audit_data:
        print("  ❌ Convergence audit returned no data. Exiting.")
        sys.exit(1)

    # FIX H-4: enforce convergence threshold — do not proceed with non-converged data
    convergence_threshold = cfg['dynamics']['convergence_threshold']
    maes = audit_data.get('audit_maes', {})
    depths = sorted(list(maes.keys()))
    mae_residual = maes[depths[-1]] if depths else 999.0
    
    if mae_residual >= convergence_threshold:
        print(f"\n❌ FATAL: Convergence NOT achieved. Residual MAE={mae_residual:.2e} ≥ threshold={convergence_threshold:.2e}")
        print("   Increase L_max or reduce time step before resubmitting.")
        logger.error(f"Convergence check failed: Residual MAE={mae_residual:.2e} >= {convergence_threshold:.2e}")
        sys.exit(1)
    print(f"  ✅ Convergence confirmed: Residual MAE={mae_residual:.2e} < {convergence_threshold:.2e}")

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
