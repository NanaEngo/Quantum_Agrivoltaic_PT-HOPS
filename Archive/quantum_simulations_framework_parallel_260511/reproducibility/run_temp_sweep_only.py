"""
Standalone script to run ONLY the Figure 2 temperature sweep and disorder sampling.
Reads configuration from parameters.yaml, respecting the n_workers parameter.
"""
import os
import sys
import numpy as np
import logging

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FRAMEWORK_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, '..'))
if _FRAMEWORK_DIR not in sys.path:
    sys.path.insert(0, _FRAMEWORK_DIR)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from reproducibility.main import load_and_validate_config, _run_temperature_sweep, _build_disorder_samples
from src.core.hamiltonian_factory import create_fmo_hamiltonian
from src.visualization.figure_generator import FigureGenerator
from src.core.constants import DEFAULT_N_DISORDER

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Standalone Temperature Sweep (JPCL Figure 2)")
    parser.add_argument("--parallel", action="store_true", help="Enable hardware-aware parallel execution")
    parser.add_argument("--n_jobs", type=int, default=None, help="Force a specific number of parallel workers")
    parser.add_argument("--no-resume", action="store_true", help="Disable resume logic (restart from scratch)")
    return parser.parse_args()

_ARGS = parse_args()

# Monkeypatch parallel_utils based on CLI flags
import utils.parallel_utils as pu
if _ARGS.n_jobs is not None:
    pu.get_safe_n_jobs = lambda *args, **kwargs: _ARGS.n_jobs
elif _ARGS.parallel:
    # Use the original hardware-aware logic
    pass
else:
    # Default to safe sequential mode for laptops
    pu.get_safe_n_jobs = lambda *args, **kwargs: 1

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import glob
import pandas as pd
from datetime import datetime
from joblib import Parallel, delayed

def get_completed_tasks(pattern="temp_sweep_progress_*.csv"):
    log_dir = os.path.join(_FRAMEWORK_DIR, 'reproducibility', 'logs')
    files = glob.glob(os.path.join(log_dir, pattern))
    completed = {}
    
    for f in files:
        try:
            df = pd.read_csv(f)
            if 'temperature_k' in df.columns:
                for _, row in df.iterrows():
                    key = (float(row['temperature_k']), str(row['label']), int(row['seed']))
                    completed[key] = float(row['phi'])
            elif 'seed' in df.columns and 'eta' in df.columns:
                 for _, row in df.iterrows():
                    if not pd.isna(row['eta']):
                        completed[int(row['seed'])] = float(row['eta'])
        except Exception as e:
            logger.warning(f"Could not read log {f}: {e}")
    return completed

def run_sweep_with_resume(cfg, H, time_points):
    from reproducibility.main import _run_trajectory_worker
    from multiprocessing import Manager
    
    bath = cfg['bath']
    dyn = cfg['dynamics']
    pulse_cfg = cfg.get('pulse', {})
    filter_cfg = cfg.get('spectral_filter', None)
    n_traj_sweep = cfg.get('simulation', {}).get('n_traj_temp_sweep', 10)
    
    if _ARGS.no_resume:
        completed = {}
        print("  [Resume] Resume logic disabled via --no-resume.")
    else:
        completed = get_completed_tasks("temp_sweep_progress_*.csv")
        print(f"  [Resume] Found {len(completed)} completed trajectories in logs.")
    
    temperatures = np.array([285, 290, 295, 300, 305, 310], dtype=float)
    
    manager = Manager()
    lock = manager.Lock()
    log_dir = os.path.join(_FRAMEWORK_DIR, 'reproducibility', 'logs')
    new_log = os.path.join(log_dir, f"temp_sweep_progress_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(new_log, 'w') as f:
        f.write("temperature_k,label,seed,phi\n")
        
    tasks = []
    for T in temperatures:
        for i in range(n_traj_sweep):
            for label, seed_offset in [('filtered', 1000), ('broadband', 2000)]:
                key = (float(T), label, seed_offset + i)
                if key not in completed:
                    tasks.append((T, label, seed_offset + i))
                else:
                    # Pass the existing result
                    pass

    print(f"  [Resume] {len(tasks)} trajectories remaining to simulate.")
    
    if tasks:
        # We use n_jobs=1 from the monkeypatch above
        results_flat = Parallel(n_jobs=pu.get_safe_n_jobs())(
            delayed(_run_trajectory_worker)(T, label, s, lock, new_log, bath, dyn, pulse_cfg, filter_cfg, H, time_points) 
            for T, label, s in tasks
        )
        # Update completed dict with new results
        for (T, label, s), phi in zip(tasks, results_flat):
            if phi is not None:
                completed[(float(T), label, s)] = phi

    # Re-group and calculate eta
    eta_temp = np.zeros(len(temperatures))
    eta_temp_err = np.zeros(len(temperatures))
    
    for i, T in enumerate(temperatures):
        samples = []
        for j in range(n_traj_sweep):
            phi_f = completed.get((float(T), 'filtered', 1000 + j))
            phi_b = completed.get((float(T), 'broadband', 2000 + j))
            if phi_f is not None and phi_b is not None:
                samples.append((phi_f - phi_b) / max(phi_b, 1e-6))
        
        if samples:
            eta_temp[i] = np.mean(samples)
            eta_temp_err[i] = np.std(samples) if len(samples) > 1 else 0.04
            print(f"  T={T:.0f}K: η = {eta_temp[i]:.4f} ± {eta_temp_err[i]:.4f} ({len(samples)} samples)")
            
    return temperatures, eta_temp, eta_temp_err

def run_disorder_with_resume(cfg, H, time_points):
    from reproducibility.main import _run_single_disorder
    from multiprocessing import Manager
    
    bath = cfg['bath']
    dyn = cfg['dynamics']
    pulse_cfg = cfg.get('pulse', {})
    filter_cfg = cfg.get('spectral_filter', None)
    n_samples = cfg.get('simulation', {}).get('n_disorder_samples', 100)
    sigma_disorder = cfg.get('simulation', {}).get('disorder_sigma_cm', 50.0)
    rng_seed = 42
    
    if _ARGS.no_resume:
        completed = {}
        print("  [Resume] Resume logic disabled via --no-resume.")
    else:
        completed = get_completed_tasks("disorder_sweep_progress_*.csv")
        print(f"  [Resume] Found {len(completed)} completed disorder realizations.")
    
    manager = Manager()
    lock = manager.Lock()
    log_dir = os.path.join(_FRAMEWORK_DIR, 'reproducibility', 'logs')
    new_log = os.path.join(log_dir, f"disorder_sweep_progress_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(new_log, 'w') as f:
        f.write("seed,label,subseed,eta\n")
        
    seeds = [rng_seed + i for i in range(n_samples)]
    remaining_seeds = [s for s in seeds if s not in completed]
    
    print(f"  [Resume] {len(remaining_seeds)} disorder realizations remaining.")
    
    results = []
    if remaining_seeds:
        results = Parallel(n_jobs=pu.get_safe_n_jobs())(
            delayed(_run_single_disorder)(s, lock, new_log, bath, dyn, pulse_cfg, filter_cfg, H, time_points, sigma_disorder) 
            for s in remaining_seeds
        )
    
    # Combine
    all_eta = list(completed.values()) + [r for r in results if r is not None]
    return np.array(all_eta)

def run_sweep_only():
    print("=" * 60)
    print("  Executing Standalone Temperature Sweep & Disorder Sampling (RESUME MODE)")
    print("=" * 60)
    
    cfg = load_and_validate_config()
    dyn = cfg['dynamics']
    time_points = np.arange(0, dyn['time_max'], dyn['time_step'])
    
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    
    print("\n[Step 1] Running temperature sweep (285–310 K)...")
    temperatures, eta_temp, eta_temp_err = run_sweep_with_resume(cfg, H, time_points)
    
    print("\n[Step 2] Running disorder sampling...")
    disorder_samples = run_disorder_with_resume(cfg, H, time_points)
    
    if len(disorder_samples) == 0:
        raise RuntimeError("Disorder sampling produced no valid samples")
        
    print("\n[Step 3] Generating Figure 2...")
    jpcl_dir = os.path.abspath(os.path.join(_SCRIPT_DIR, '..', '..', 'Theory_Journals_main', 'JPCL'))
    gen = FigureGenerator(figures_dir=jpcl_dir)
    
    fig2_path = gen.plot_environmental_robustness(
        temperatures, eta_temp, eta_temp_err, disorder_samples,
        filename_prefix="ETR_Under_Environmental_Effects",
    )
    print(f"\n✅ Figure 2 successfully saved to: {fig2_path}")

if __name__ == "__main__":
    run_sweep_only()
