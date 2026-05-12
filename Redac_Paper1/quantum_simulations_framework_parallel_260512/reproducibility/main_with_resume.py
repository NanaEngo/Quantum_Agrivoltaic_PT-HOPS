"""
from typing import Set
main.py — Enhanced reproducibility pipeline with resume capability

Features:
  - Step-by-step result saving (intermediate checkpoints)
  - Resume from last successful checkpoint after OOM/failure
  - Execution state tracking and recovery information
  - Incremental progress logging for long-running tasks

Usage:
  # First run
  mamba run -n MesoHOP-sim python -u reproducibility/main.py --config config/laptop_parameters.yaml
  
  # Resume after OOM
  mamba run -n MesoHOP-sim python -u reproducibility/main.py --resume
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
import pandas as pd
from datetime import datetime
import multiprocessing
from joblib import Parallel, delayed

# Import resume capability
from resume_capability import (
    create_resume_checkpoint,
    print_recovery_instructions,
)

from src.core.constants import (
    DEFAULT_DPI, PREVIEW_DPI, GAUSSIAN_TBW_FS, LIGHT_SPEED_CMS,
    DEFAULT_MAX_HIERARCHY, DEFAULT_N_MATSUBARA, FILTER_BAND_CENTERS_NM,
    FILTER_BANDWIDTH_CM, FILTER_WEIGHTS, PULSE_CENTRAL_FREQ, PULSE_FWHM,
    DEFAULT_DISORDER_SIGMA, DEFAULT_DRUDE_CUTOFF, DEFAULT_REORGANIZATION_ENERGY,
    DEFAULT_N_TRAJ, DEFAULT_SBD_BUNDLES, DEFAULT_VIBRONIC_DAMPING_VAL,
    DEFAULT_N_TRAJ_SWEEP, DEFAULT_N_DISORDER, BASE_TRAJ_MEMORY_GB,
)

# Force unbuffered stdout/stderr
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

# Silence verbose external libraries
logging.getLogger('numba').setLevel(logging.WARNING)
logging.getLogger('jax').setLevel(logging.WARNING)
logger.info(f"Log file: {_LOG_FILE}")

# Initialize checkpoint system
checkpoint, saver, executor = create_resume_checkpoint()


def load_and_validate_config(custom_path=None):
    if custom_path:
        config_path = os.path.abspath(custom_path)
        if not os.path.exists(config_path):
            config_path = os.path.join(_FRAMEWORK_DIR, custom_path)
            if not os.path.exists(config_path):
                 raise FileNotFoundError(f"Config file not found: {custom_path}")
    else:
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
    
    is_production = os.path.basename(config_path) == 'parameters.yaml'
    
    if is_production:
        if L < 8:
            raise ValueError(f"hierarchy_depth={L} < 8. Production requires L≥8.")
        if K < 2:
            raise ValueError(f"matsubara_truncation={K} < 2. JPCL production requires K≥2.")
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
    """Check and log system resources."""
    import multiprocessing
    n_cpus = multiprocessing.cpu_count()
    logger.info(f"System resources: CPU cores={n_cpus}")
    
    try:
        import jax
        devices = jax.devices()
        logger.info(f"  JAX devices: {len(devices)}")
    except Exception:
        logger.info("  JAX/GPU acceleration not detected or disabled.")
    
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
    """Run convergence audit with checkpoint saving."""
    if checkpoint.is_step_complete("convergence_audit"):
        print("\n[Step 2] Convergence audit already completed (resuming)...")
        result_path = checkpoint.get_result_path("convergence_audit")
        logger.info(f"Skipping convergence audit (already completed at {result_path})")
        return None
    
    print("\n[Step 2] Running full validation suite (12 tests)...")
    import audit_convergence as _audit
    
    try:
        audit_data = _audit.run_convergence_audit(cfg=cfg)
        _audit.run_time_step_audit(cfg=cfg)
        _audit.run_detailed_balance_audit(cfg=cfg)
        _audit.run_hermiticity_audit(cfg=cfg)
        _audit.run_markovian_limit_audit(cfg=cfg)
        
        if audit_data:
            maes = audit_data.get('audit_maes', {})
            depths = sorted(list(maes.keys()))
            mae_final = maes[depths[-1]] if depths else 0.0
            print(f"  ✅ Validation suite complete. Residual MAE={mae_final:.2e}")
            
            # Save audit results
            config_hash = checkpoint.state.get("config_hash", "unknown")
            result_path = saver.save_convergence_audit(audit_data, config_hash)
            checkpoint.mark_step_complete("convergence_audit", result_path)
        
        return audit_data
    except Exception as e:
        checkpoint.mark_step_failed("convergence_audit", str(e))
        raise


def _dual_band_transmission(omega_cm, filter_cfg):
    """Evaluate dual-band spectral transmission function T(ω)."""
    band_centers_nm = filter_cfg.get('band_centers_nm', FILTER_BAND_CENTERS_NM)
    bandwidth_cm    = float(filter_cfg.get('bandwidth_cm', FILTER_BANDWIDTH_CM))
    weights         = filter_cfg.get('weights', FILTER_WEIGHTS)

    band_centers_cm = [1.0e7 / lam for lam in band_centers_nm]
    sigma = bandwidth_cm / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    T = np.zeros_like(omega_cm, dtype=float)
    for Omega_j, w_j in zip(band_centers_cm, weights):
        T += float(w_j) * np.exp(-0.5 * ((omega_cm - Omega_j) / sigma) ** 2)

    T_max = np.max(T)
    if T_max > 1e-12:
        T /= T_max
    return T


def _build_initial_state_for_label(H, label, pulse_cfg, filter_cfg=None):
    """Compute initial state for filtered or broadband excitation."""
    n_sites = H.shape[0]
    eigenvalues, eigenvectors = np.linalg.eigh(H)

    if label == 'broadband':
        weights = np.ones(n_sites)
    elif label == 'filtered':
        fwhm_t_fs = float(pulse_cfg.get('fwhm', PULSE_FWHM))
        fwhm_spectral_cm = GAUSSIAN_TBW_FS / fwhm_t_fs
        sigma_in = fwhm_spectral_cm / (2.0 * np.sqrt(2.0 * np.log(2.0)))
        center_freq = float(pulse_cfg.get('center_freq', PULSE_CENTRAL_FREQ))

        E_in = np.exp(-0.5 * ((eigenvalues - center_freq) / sigma_in) ** 2)

        if filter_cfg is not None:
            T = _dual_band_transmission(eigenvalues, filter_cfg)
        else:
            logger.warning("No spectral_filter config found — using single-Gaussian filter.")
            T = E_in.copy()

        E_eff = T * E_in
        weights = E_eff ** 2
    else:
        raise ValueError(f"Unknown excitation label '{label}'.")

    total = np.sum(weights)
    if total < 1e-12:
        logger.warning(f"Pulse ({label}) has negligible overlap with exciton manifold.")
        psi0 = np.zeros(n_sites, dtype=complex)
        psi0[0] = 1.0
        return psi0

    weights /= total

    psi0 = np.zeros(n_sites, dtype=complex)
    for k in range(n_sites):
        psi0 += np.sqrt(weights[k]) * eigenvectors[:, k]

    norm = np.linalg.norm(psi0)
    if norm > 1e-12:
        psi0 /= norm

    logger.info(f"Initial state ({label}): exciton weights = "
                + ", ".join(f"{w:.4f}" for w in weights)
                + f"  |ψ₀| = {np.linalg.norm(psi0):.6f}")
    return psi0


def run_full_fmo_simulation(cfg):
    """Run FMO simulation with step-by-step result saving."""
    print("\n[Step 3] Running full FMO simulation (filtered + broadband, ensemble)...")
    from src.core.hops_simulator import HopsSimulator
    from src.core.hamiltonian_factory import create_fmo_hamiltonian
    from utils.parallel_utils import get_safe_n_jobs

    dyn = cfg['dynamics']
    bath = cfg['bath']
    pulse_cfg = cfg.get('pulse', {})
    filter_cfg = cfg.get('spectral_filter', None)
    n_traj = cfg.get('simulation', {}).get('n_traj', DEFAULT_N_TRAJ)

    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    time_points = np.arange(0, dyn['time_max'], dyn['time_step'])

    vib_freqs = bath.get('vibronic_frequencies', [])
    vib_hr = bath.get('huang_rhys_factors', [])
    vib_damping_raw = bath.get('vibronic_damping', DEFAULT_VIBRONIC_DAMPING_VAL)
    if isinstance(vib_damping_raw, list):
        vib_damping = np.array(vib_damping_raw, dtype=float)
    else:
        vib_damping = np.full(len(vib_freqs), float(vib_damping_raw))

    results = {}
    config_hash = checkpoint.state.get("config_hash", "unknown")
    
    for label in ['filtered', 'broadband']:
        step_name = f"fmo_simulation_{label}"
        
        # Check if already completed
        if checkpoint.is_step_complete(step_name):
            print(f"  [{label}] Already completed (resuming)...")
            result_path = checkpoint.get_result_path(step_name)
            logger.info(f"Skipping {label} simulation (already completed at {result_path})")
            # Load from saved file
            df = pd.read_csv(result_path)
            results[label] = {
                'populations': df[[c for c in df.columns if c.startswith('population_')]].values,
                'coherences': df['coherences'].values,
                't_axis': df['time_fs'].values,
                'n_traj': n_traj,
                'simulator': 'MesoHOPS-Parallel',
                'ipr': df.get('ipr', np.zeros(len(df))).values if 'ipr' in df.columns else None,
                'qfi': df.get('qfi', np.zeros(len(df))).values if 'qfi' in df.columns else None,
                'entropy': df.get('entropy', np.zeros(len(df))).values if 'entropy' in df.columns else None,
            }
            continue
        
        print(f"  Preparing {label} excitation...")
        initial_state = _build_initial_state_for_label(H, label, pulse_cfg, filter_cfg)

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
                'n_traj': data.get('n_traj_used', n_traj),
                'simulator': data.get('simulator', 'MesoHOPS-Parallel'),
                'ipr': data.get('ipr'),
                'qfi': data.get('qfi'),
                'entropy': data.get('entropy'),
            }
            n_completed = data.get('n_traj_used', n_traj)
            
            logger.info(f"FMO {label}: {n_completed} trajectories averaged via Parallel Ensemble.")
            print(f"  ✅ {label}: {n_completed} trajectories averaged")

            # ── STEP-BY-STEP SAVE: persist immediately after completion ──
            metrics = {k: v for k, v in {
                'ipr': data.get('ipr'),
                'qfi': data.get('qfi'),
                'entropy': data.get('entropy'),
            }.items() if v is not None}
            
            result_path = saver.save_fmo_dynamics_intermediate(
                label, data['t_axis'], data['populations'], data['coherences'],
                config_hash, metrics
            )
            checkpoint.mark_step_complete(step_name, result_path)
            print(f"  💾 [{label}] intermediate result saved → {result_path}")
            logger.info(f"Step-save [{label}]: {result_path}")

        except MemoryError as e:
            checkpoint.mark_step_failed(step_name, f"OOM: {str(e)}")
            print(f"\n❌ OUT OF MEMORY during {label} simulation")
            print(f"   Checkpoint saved. Resume with: mamba run -n MesoHOP-sim python -u reproducibility/main.py --resume")
            logger.error(f"OOM during {label} simulation: {e}")
            raise
        except Exception as e:
            checkpoint.mark_step_failed(step_name, str(e))
            logger.error(f"Full FMO simulation failed for {label}: {e}")
            raise

    return results, time_points


def generate_figures(cfg, sim_results, time_points):
    """Generate publication figures with checkpoint saving."""
    print("\n[Step 4] Generating publication figures...")
    from src.core.hamiltonian_factory import create_fmo_hamiltonian
    from src.visualization.figure_generator import FigureGenerator

    jpcl_dir = os.path.abspath(os.path.join(
        _SCRIPT_DIR, '..', '..', 'Theory_Journals_main', 'JPCL'
    ))
    gen = FigureGenerator(figures_dir=jpcl_dir)

    filtered = sim_results['filtered']
    broadband = sim_results['broadband']

    # Figure 1
    if not checkpoint.is_step_complete("figure_1"):
        try:
            _n_t = len(filtered["t_axis"])
            quantum_metrics = {
                "ipr": filtered.get("ipr") if filtered.get("ipr") is not None else np.zeros(_n_t),
                "qfi": filtered.get("qfi") if filtered.get("qfi") is not None else np.zeros(_n_t),
                "entropy": filtered.get("entropy") if filtered.get("entropy") is not None else np.zeros(_n_t),
            }
            fig1_path = gen.plot_quantum_dynamics(
                filtered["t_axis"],
                filtered["populations"],
                filtered["coherences"],
                quantum_metrics,
                filename_prefix="Quantum_dynamics",
                baseline_populations=broadband["populations"],
                baseline_coherences=broadband["coherences"],
                baseline_ipr=broadband.get("ipr") if broadband.get("ipr") is not None else np.zeros(_n_t),
                baseline_qfi=broadband.get("qfi") if broadband.get("qfi") is not None else np.zeros(_n_t),
            )
            checkpoint.mark_step_complete("figure_1", fig1_path)
            print(f"  💾 Figure 1 saved → {fig1_path}")
            logger.info(f"Figure 1 saved to {fig1_path}")
        except Exception as e:
            checkpoint.mark_step_failed("figure_1", str(e))
            print(f"  ⚠️  Figure 1 error: {e}")
            logger.warning(f"Figure 1: {e}")


def main():
    print("=" * 60)
    print("  Quantum Agrivoltaic PT-HOPS — JPCL Reproducibility Pipeline")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    check_system_resources()

    parser = argparse.ArgumentParser(description="JPCL Reproducibility Pipeline")
    parser.add_argument("--config", type=str, help="Path to custom parameters.yaml")
    parser.add_argument("--skip-audit", action="store_true", help="Skip Step 2 convergence audit")
    parser.add_argument("--parallel", action="store_true", help="Run with parallel trajectories")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint")
    parser.add_argument("--n-traj", type=int, help="Override n_traj from config")
    parser.add_argument("--n-traj-sweep", type=int, help="Override n_traj_temp_sweep")
    args = parser.parse_args()

    # Step 1: Validate config
    print(f"\n[Step 1] Loading and validating {args.config if args.config else 'parameters.yaml'}...")
    try:
        cfg = load_and_validate_config(args.config)
        if args.n_traj:
            cfg['simulation']['n_traj'] = args.n_traj
        if args.n_traj_sweep:
            cfg['simulation']['n_traj_temp_sweep'] = args.n_traj_sweep
        
        # Set config hash for checkpoint tracking
        config_hash = checkpoint.set_config_hash(cfg)
        logger.info(f"Config hash: {config_hash}")
        
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

    # Step 2: Convergence audit
    if not getattr(args, 'skip_audit', False):
        try:
            audit_data = run_convergence_audit(cfg)
            if audit_data:
                convergence_threshold = cfg['dynamics']['convergence_threshold']
                maes = audit_data.get('audit_maes', {})
                depths = sorted(list(maes.keys()))
                mae_residual = maes[depths[-1]] if depths else 999.0
                
                if mae_residual >= convergence_threshold:
                    print(f"\n❌ FATAL: Convergence NOT achieved. Residual MAE={mae_residual:.2e} ≥ {convergence_threshold:.2e}")
                    logger.error(f"Convergence check failed")
                    sys.exit(1)
                print(f"  ✅ Convergence confirmed: Residual MAE={mae_residual:.2e} < {convergence_threshold:.2e}")
        except Exception as e:
            print(f"\n❌ Convergence audit failed: {e}")
            print_recovery_instructions(checkpoint)
            sys.exit(1)
    else:
        print("\n[Step 2] SKIPPING convergence audit (using pre-validated results).")
        logger.info("Skipping convergence audit as requested by user.")

    # Step 3: Full FMO simulation
    try:
        sim_results, time_points = run_full_fmo_simulation(cfg)
    except MemoryError:
        print_recovery_instructions(checkpoint)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FMO simulation failed: {e}")
        print_recovery_instructions(checkpoint)
        sys.exit(1)

    # Step 4: Generate figures
    try:
        generate_figures(cfg, sim_results, time_points)
    except Exception as e:
        print(f"\n❌ Figure generation failed: {e}")
        print_recovery_instructions(checkpoint)
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  Pipeline complete.")
    print(f"  Results → {os.path.join(_SCRIPT_DIR, 'results')}")
    print(f"  Figures → Theory_Journals/JPCL/")
    print(f"  Logs    → {_LOG_DIR}")
    print("=" * 60)
    
    checkpoint.mark_step_complete("pipeline_complete")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        print_recovery_instructions(checkpoint)
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed: {e}")
        print_recovery_instructions(checkpoint)
        sys.exit(1)
