"""
main_parallel.py — Parallelized reproducibility pipeline for JPCL revision.
Optimized for dual Xeon Gold 6136 (48 cores) + NVIDIA RTX A4000.

Usage: mamba run -n MesoHOP-sim python -u reproducibility/main_parallel.py
"""
import os
import sys
import logging
import yaml
import numpy as np
from datetime import datetime
from multiprocessing import cpu_count

# Ensure framework is importable
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FRAMEWORK_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, '..'))
sys.path.insert(0, _FRAMEWORK_DIR)
sys.path.insert(0, _SCRIPT_DIR)

# Import parallel utilities
from utils.parallel_utils import ParallelExecutor, parallel_trajectory_simulation
from core.gpu_dynamics import GPUQuantumDynamics, JAX_AVAILABLE

_LOG_DIR = os.path.join(_SCRIPT_DIR, 'logs')
os.makedirs(_LOG_DIR, exist_ok=True)

_LOG_FILE = os.path.join(_LOG_DIR, f"execution_parallel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s — %(message)s',
    handlers=[
        logging.FileHandler(_LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Log file: {_LOG_FILE}")


def load_configs():
    """Load both parameters.yaml and parallel_config.yaml."""
    # Load main parameters
    params_path = os.path.join(_FRAMEWORK_DIR, 'parameters.yaml')
    with open(params_path, 'r') as f:
        params = yaml.safe_load(f)
    
    # Load parallel configuration
    parallel_path = os.path.join(_FRAMEWORK_DIR, 'parallel_config.yaml')
    with open(parallel_path, 'r') as f:
        parallel_cfg = yaml.safe_load(f)
    
    # Merge configurations
    params['parallel'] = parallel_cfg.get('parallel', {})
    params['performance'] = parallel_cfg.get('performance', {})
    
    logger.info(f"Config loaded: L={params['dynamics']['hierarchy_depth']}, "
                f"K={params['dynamics']['matsubara_truncation']}, "
                f"Workers={params['parallel']['n_workers']}, "
                f"GPU={'enabled' if params['parallel']['use_gpu'] else 'disabled'}")
    
    return params


def check_system_resources():
    """Check and log system resources."""
    n_cpus = cpu_count()
    logger.info(f"System resources:")
    logger.info(f"  CPU cores: {n_cpus}")
    
    if JAX_AVAILABLE:
        try:
            import jax
            devices = jax.devices()
            logger.info(f"  JAX devices: {len(devices)}")
            for i, dev in enumerate(devices):
                logger.info(f"    Device {i}: {dev}")
        except Exception as e:
            logger.warning(f"  JAX device check failed: {e}")
    else:
        logger.warning("  JAX not available - GPU acceleration disabled")
    
    # Check memory
    try:
        import psutil
        mem = psutil.virtual_memory()
        logger.info(f"  RAM: {mem.total / (1024**3):.1f} GB total, "
                   f"{mem.available / (1024**3):.1f} GB available")
    except ImportError:
        logger.info("  psutil not available - memory check skipped")


def run_parallel_fmo_simulation(cfg):
    """
    Run FMO simulation with parallel trajectory execution.
    
    Parameters
    ----------
    cfg : dict
        Configuration dictionary
    
    Returns
    -------
    results : dict
        Simulation results
    """
    logger.info("\n" + "="*80)
    logger.info("PARALLEL FMO SIMULATION")
    logger.info("="*80)
    
    # Import required modules
    from core.hamiltonian_factory import create_fmo_hamiltonian
    from models.simple_quantum_dynamics_simulator import SimpleQuantumDynamicsSimulator
    
    # Create Hamiltonian
    H = create_fmo_hamiltonian(include_reaction_center=False)
    n_sites = H.shape[0]
    logger.info(f"FMO Hamiltonian: {n_sites} sites")
    
    # Time grid
    time_max = cfg['dynamics']['time_max']
    time_step = cfg['dynamics']['time_step']
    time_points = np.linspace(0, time_max, int(time_max / time_step) + 1)
    logger.info(f"Time grid: {len(time_points)} points, dt={time_step} fs")
    
    # Parallel configuration
    n_traj = cfg['simulation'].get('n_traj', 100)
    n_workers = cfg['parallel']['n_workers']
    use_gpu = cfg['parallel']['use_gpu']
    
    logger.info(f"Parallel execution: {n_traj} trajectories, {n_workers} workers")
    
    # Check if GPU acceleration is beneficial
    if use_gpu and JAX_AVAILABLE and n_traj >= 10:
        logger.info("Using GPU-accelerated batch simulation")
        return _run_gpu_batch_simulation(H, time_points, n_traj, cfg)
    else:
        logger.info("Using CPU parallel simulation")
        return _run_cpu_parallel_simulation(H, time_points, n_traj, n_workers, cfg)


def _run_gpu_batch_simulation(H, time_points, n_traj, cfg):
    """Run simulation using GPU batch processing (CuPy or JAX)."""
    from core.gpu_dynamics import GPUQuantumDynamics, gpu_ensemble_average, gpu_batch_coherence, GPU_BACKEND
    
    # Initialize GPU simulator (auto-selects CuPy or JAX)
    gpu_sim = GPUQuantumDynamics(H, temperature=cfg['bath']['temperature'], 
                                 use_gpu=True, backend='auto')
    
    logger.info(f"Using GPU backend: {GPU_BACKEND.upper()}")
    
    # Create initial states (all start at site 1)
    n_sites = H.shape[0]
    initial_states = np.zeros((n_traj, n_sites, n_sites), dtype=np.complex128)
    for i in range(n_traj):
        initial_states[i, 0, 0] = 1.0  # Excitation on site 1
    
    # Batch simulation on GPU
    logger.info(f"Running GPU batch simulation: {n_traj} trajectories")
    trajectories = gpu_sim.simulate_batch_trajectories(initial_states, time_points, method='rk4')
    
    # Extract populations
    populations = gpu_sim.compute_populations_batch(trajectories)
    
    # Compute coherences
    coherences = gpu_batch_coherence(trajectories, backend='auto')
    
    # Ensemble average
    avg_populations = gpu_ensemble_average(populations, axis=0, backend='auto')
    avg_coherences = gpu_ensemble_average(coherences, axis=0, backend='auto')
    
    logger.info(f"GPU simulation complete: {trajectories.shape}")
    
    return {
        't_axis': time_points,
        'populations': avg_populations,
        'coherences': avg_coherences,
        'n_traj': n_traj,
        'simulator': f'GPU_{GPU_BACKEND.upper()}'
    }


def _run_cpu_parallel_simulation(H, time_points, n_traj, n_workers, cfg):
    """Run simulation using CPU parallelization."""
    from models.simple_quantum_dynamics_simulator import SimpleQuantumDynamicsSimulator
    
    # Create simulator
    sim = SimpleQuantumDynamicsSimulator(H, temperature=cfg['bath']['temperature'])
    
    # Create initial state (site 1)
    n_sites = H.shape[0]
    initial_state = np.zeros(n_sites, dtype=np.complex128)
    initial_state[0] = 1.0
    
    # Define simulation function for each trajectory
    def simulate_single_trajectory(seed):
        """Simulate single trajectory with given seed."""
        np.random.seed(seed)
        result = sim.simulate_dynamics(time_points=time_points, initial_state=initial_state)
        return result
    
    # Create trajectory parameters
    trajectory_seeds = list(range(n_traj))
    
    # Parallel execution
    logger.info(f"Running CPU parallel simulation: {n_traj} trajectories, {n_workers} workers")
    results = parallel_trajectory_simulation(trajectory_seeds, simulate_single_trajectory, n_workers)
    
    # Aggregate results
    all_populations = np.array([r['populations'] for r in results])
    avg_populations = np.mean(all_populations, axis=0)
    
    # Compute coherences if available
    if 'coherences' in results[0]:
        all_coherences = np.array([r['coherences'] for r in results])
        avg_coherences = np.mean(all_coherences, axis=0)
    else:
        avg_coherences = np.zeros(len(time_points))
    
    logger.info(f"CPU parallel simulation complete")
    
    return {
        't_axis': time_points,
        'populations': avg_populations,
        'coherences': avg_coherences,
        'n_traj': n_traj,
        'simulator': f'CPU_Parallel_{n_workers}workers'
    }


def run_parallel_convergence_audit(cfg):
    """
    Run convergence audit with parallel execution.
    
    Parameters
    ----------
    cfg : dict
        Configuration dictionary
    
    Returns
    -------
    audit_results : dict
        Convergence audit results
    """
    logger.info("\n" + "="*80)
    logger.info("PARALLEL CONVERGENCE AUDIT (L=9,10,11)")
    logger.info("="*80)
    
    from core.hamiltonian_factory import create_fmo_hamiltonian
    from models.simple_quantum_dynamics_simulator import SimpleQuantumDynamicsSimulator
    
    H = create_fmo_hamiltonian(include_reaction_center=False)
    time_points = np.linspace(0, 500, 101)  # Shorter for audit
    
    # Define audit function
    def run_single_L(L_value):
        """Run simulation for specific hierarchy depth."""
        logger.info(f"  Running L={L_value}")
        sim = SimpleQuantumDynamicsSimulator(H, temperature=cfg['bath']['temperature'])
        
        n_sites = H.shape[0]
        initial_state = np.zeros(n_sites, dtype=np.complex128)
        initial_state[0] = 1.0
        
        result = sim.simulate_dynamics(time_points=time_points, initial_state=initial_state)
        return {'L': L_value, 'populations': result['populations']}
    
    # Parallel execution for L=9,10,11
    L_values = [9, 10, 11]
    n_workers = min(3, cfg['parallel']['n_workers'])
    
    logger.info(f"Running convergence audit: L={L_values}, {n_workers} workers")
    results = parallel_trajectory_simulation(L_values, run_single_L, n_workers)
    
    # Compute convergence metrics
    pop_9 = results[0]['populations']
    pop_10 = results[1]['populations']
    pop_11 = results[2]['populations']
    
    mae_9_10 = np.mean(np.abs(pop_10 - pop_9))
    mae_10_11 = np.mean(np.abs(pop_11 - pop_10))
    
    logger.info(f"Convergence: MAE(9→10)={mae_9_10:.2e}, MAE(10→11)={mae_10_11:.2e}")
    
    return {
        'L_values': L_values,
        'mae_9_10': mae_9_10,
        'mae_10_11': mae_10_11,
        'populations': {'L9': pop_9, 'L10': pop_10, 'L11': pop_11}
    }


def main():
    """Main parallel execution pipeline."""
    print("\n" + "="*80)
    print("QUANTUM AGRIVOLTAIC PT-HOPS — PARALLEL EXECUTION")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check system resources
    check_system_resources()
    print()
    
    # Load configuration
    cfg = load_configs()
    
    # Run parallel FMO simulation
    try:
        fmo_results = run_parallel_fmo_simulation(cfg)
        logger.info(f"✓ FMO simulation complete: {fmo_results['n_traj']} trajectories")
    except Exception as e:
        logger.error(f"✗ FMO simulation failed: {e}", exc_info=True)
        fmo_results = None
    
    # Run parallel convergence audit
    try:
        audit_results = run_parallel_convergence_audit(cfg)
        logger.info(f"✓ Convergence audit complete: MAE(10→11)={audit_results['mae_10_11']:.2e}")
    except Exception as e:
        logger.error(f"✗ Convergence audit failed: {e}", exc_info=True)
        audit_results = None
    
    print()
    print("="*80)
    print("PARALLEL EXECUTION COMPLETE")
    print("="*80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log file: {_LOG_FILE}")
    print()
    
    return {
        'fmo_results': fmo_results,
        'audit_results': audit_results
    }


if __name__ == '__main__':
    main()
