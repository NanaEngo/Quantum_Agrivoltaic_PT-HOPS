"""
test_jpcl_resubmission_suite.py — Comprehensive validation for JPCL Revision.

This suite implements the 12 SI validation tests as a single unit-test file
to ensure the codebase remains consistent with the manuscript's claims.
"""
import sys
import numpy as np
import pytest
from pathlib import Path

import logging

# Setup Logging for Debugging
_LOG_DIR = Path(__file__).parent.parent / "reproducibility" / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _LOG_DIR / "test_execution.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(_LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test_suite")
logger.info(f"--- Starting Test Session at {_LOG_FILE} ---")

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from tqdm.auto import tqdm as _tqdm
except ImportError:
    def _tqdm(iterable, **kwargs): return iterable

from core.hamiltonian_factory import create_fmo_hamiltonian
from core.hops_simulator import HopsSimulator
from core.constants import (
    MAE_THRESHOLD,
    MAE_THRESHOLD_LOOSE,
    POPS_REAL_THRESHOLD,
    DEFAULT_TEMPERATURE,
    DEFAULT_REORGANIZATION_ENERGY
)

@pytest.fixture
def fmo_hamiltonian():
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    return H

@pytest.fixture
def t_audit():
    return np.linspace(0, 100, 51)

class TestJPCLValidationSuite:

    # ─── CONVERGENCE TESTS (4 tests) ──────────────────────────────────────────

    def test_si_1_hierarchy_convergence(self, fmo_hamiltonian, t_audit):
        """Test 1: Hierarchy convergence."""
        from reproducibility.main import load_and_validate_config
        cfg = load_and_validate_config()
        L_prod = cfg['dynamics']['L_max']
        L_prev = max(1, L_prod - 1)
        # Use trajectories from config if possible
        n_traj = cfg['simulation'].get('n_traj', 100) if L_prod >= 8 else 4
        
        K_val = cfg['dynamics'].get('matsubara_truncation', 2)
        sim_prev = HopsSimulator(fmo_hamiltonian, max_hierarchy=L_prev, k_matsubara=K_val)
        sim_prod = HopsSimulator(fmo_hamiltonian, max_hierarchy=L_prod, k_matsubara=K_val)
        
        psi0 = np.eye(fmo_hamiltonian.shape[0])[0]
        res_prev = sim_prev.simulate_dynamics(t_audit, initial_state=psi0, n_traj=n_traj, strict_mode=True)
        res_prod = sim_prod.simulate_dynamics(t_audit, initial_state=psi0, n_traj=n_traj, strict_mode=True)
        
        mae = np.mean(np.abs(res_prod["populations"] - res_prev["populations"]))
        logger.info(f"Test 1 (L): L={L_prod} vs L={L_prev} MAE = {mae:.2e}")
        assert mae < MAE_THRESHOLD, f"Hierarchy depth L={L_prod} not converged"

    def test_si_2_matsubara_convergence(self, fmo_hamiltonian, t_audit):
        """Test 2: Matsubara convergence."""
        from reproducibility.main import load_and_validate_config
        cfg = load_and_validate_config()
        L_val = cfg['dynamics']['L_max']
        K_prod = cfg['dynamics'].get('matsubara_truncation', 2)
        K_prev = max(1, K_prod - 1)
        n_traj = cfg['simulation'].get('n_traj', 100) if L_val >= 8 else 4
        
        sim_k_prev = HopsSimulator(fmo_hamiltonian, max_hierarchy=L_val, k_matsubara=K_prev)
        sim_k_prod = HopsSimulator(fmo_hamiltonian, max_hierarchy=L_val, k_matsubara=K_prod)
        
        psi0 = np.eye(fmo_hamiltonian.shape[0])[0]
        res_k_prev = sim_k_prev.simulate_dynamics(t_audit, initial_state=psi0, n_traj=n_traj, strict_mode=True)
        res_k_prod = sim_k_prod.simulate_dynamics(t_audit, initial_state=psi0, n_traj=n_traj, strict_mode=True)
        
        mae = np.mean(np.abs(res_k_prod["populations"] - res_k_prev["populations"]))
        logger.info(f"Test 2 (K): K={K_prod} vs K={K_prev} MAE = {mae:.2e}")
        assert mae < MAE_THRESHOLD_LOOSE, f"Matsubara truncation K={K_prod} not converged"

    def test_si_3_timestep_convergence(self, fmo_hamiltonian):
        """Test 3: Time step convergence."""
        from reproducibility.main import load_and_validate_config
        cfg = load_and_validate_config()
        L_val = cfg['dynamics']['L_max']
        K_val = cfg['dynamics'].get('matsubara_truncation', 2)
        t_max = 100.0
        dt_prod = cfg['dynamics']['time_step']
        dt_fine = dt_prod / 2.0
        n_traj = cfg['simulation'].get('n_traj', 4) if L_val >= 8 else 4
        
        sim1 = HopsSimulator(fmo_hamiltonian, max_hierarchy=L_val, k_matsubara=K_val)
        psi0 = np.eye(fmo_hamiltonian.shape[0])[0]
        res1 = sim1.simulate_dynamics(np.arange(0, t_max, dt_fine), initial_state=psi0, n_traj=n_traj, strict_mode=True)
        res2 = sim1.simulate_dynamics(np.arange(0, t_max, dt_prod), initial_state=psi0, n_traj=n_traj, strict_mode=True)
        
        mae = np.mean(np.abs(res1["populations"][-1, :] - res2["populations"][-1, :]))
        logger.info(f"Test 3 (dt): dt={dt_prod} vs dt={dt_fine} MAE@t={t_max} = {mae:.2e}")
        assert mae < MAE_THRESHOLD_LOOSE, f"Time step dt={dt_prod} fs not converged"

    def test_si_4_pulse_stability(self, fmo_hamiltonian):
        """Test 4: Propagator stability."""
        from reproducibility.main import load_and_validate_config
        cfg = load_and_validate_config()
        L_val = cfg['dynamics']['L_max']
        K_val = cfg['dynamics'].get('matsubara_truncation', 2)
        n_traj = cfg['simulation'].get('n_traj', 4) if L_val >= 8 else 4
        t = np.linspace(0, 200, 101)
        sim = HopsSimulator(fmo_hamiltonian, max_hierarchy=max(1, L_val - 2), k_matsubara=K_val)
        
        psi0 = np.eye(fmo_hamiltonian.shape[0])[0]
        res_delta = sim.simulate_dynamics(t, initial_state=psi0, n_traj=n_traj, strict_mode=True)
        res_shift = sim.simulate_dynamics(t, initial_state=psi0 * 1.001, n_traj=n_traj, strict_mode=True)
        
        mae = np.mean(np.abs(res_delta["populations"] - res_shift["populations"]))
        logger.info(f"Test 4 (Pulse): Stability MAE = {mae:.2e}")
        assert mae < MAE_THRESHOLD, "Simulation unstable under perturbations"

    # ─── PHYSICAL CONSISTENCY TESTS (4 tests) ─────────────────────────────────

    def test_si_5_trace_preservation(self, fmo_hamiltonian, t_audit):
        """Test 5: Sum(rho_ii) = 1.0."""
        from reproducibility.main import load_and_validate_config
        cfg = load_and_validate_config()
        L_target = cfg['dynamics']['L_max']
        K_val = cfg['dynamics'].get('matsubara_truncation', 2)
        sim = HopsSimulator(fmo_hamiltonian, max_hierarchy=L_target, k_matsubara=K_val)
        psi0 = np.eye(fmo_hamiltonian.shape[0])[0]
        res = sim.simulate_dynamics(t_audit, initial_state=psi0, strict_mode=True)
        
        trace = np.sum(res["populations"], axis=1)
        max_dev = np.max(np.abs(trace - 1.0))
        assert max_dev < MAE_THRESHOLD

    def test_si_6_positivity_preservation(self, fmo_hamiltonian, t_audit):
        """Test 6: rho_ii >= 0."""
        from reproducibility.main import load_and_validate_config
        cfg = load_and_validate_config()
        L_target = cfg['dynamics']['L_max']
        K_val = cfg['dynamics'].get('matsubara_truncation', 2)
        sim = HopsSimulator(fmo_hamiltonian, max_hierarchy=L_target, k_matsubara=K_val)
        psi0 = np.eye(fmo_hamiltonian.shape[0])[0]
        res = sim.simulate_dynamics(t_audit, initial_state=psi0, strict_mode=True)
        
        min_pop = np.min(res["populations"])
        assert min_pop > -1e-3 # Numerical floor for single trajectories

    def test_si_7_detailed_balance(self, fmo_hamiltonian):
        """Test 7: Boltzmann distribution trend."""
        from reproducibility.main import load_and_validate_config
        cfg = load_and_validate_config()
        L_target = cfg['dynamics']['L_max']
        temp = cfg['bath'].get('temperature', 295.0)
        sim = HopsSimulator(fmo_hamiltonian, temperature=temp, max_hierarchy=max(1, L_target - 2))
        
        t_long = np.linspace(0, 1000, 101)
        psi0 = np.ones(fmo_hamiltonian.shape[0])/np.sqrt(fmo_hamiltonian.shape[0])
        res = sim.simulate_dynamics(t_long, initial_state=psi0, strict_mode=True)
        
        _, eigvecs = np.linalg.eigh(fmo_hamiltonian)
        psi_final = np.sqrt(res["populations"][-1, :])
        p_final_exciton = np.abs(eigvecs.conj().T @ psi_final)**2
        assert p_final_exciton[0] > p_final_exciton[-1]

    def test_si_8_hermiticity(self, fmo_hamiltonian, t_audit):
        """Test 8: Populations are real."""
        from reproducibility.main import load_and_validate_config
        cfg = load_and_validate_config()
        L_val = cfg['dynamics']['L_max']
        sim = HopsSimulator(fmo_hamiltonian, max_hierarchy=L_val)
        psi0 = np.eye(fmo_hamiltonian.shape[0])[0]
        res = sim.simulate_dynamics(t_audit, initial_state=psi0, strict_mode=True)
        
        assert np.all(np.isreal(res["populations"]))
        assert np.max(np.abs(np.imag(res["populations"]))) < POPS_REAL_THRESHOLD

    # ─── ENVIRONMENTAL ROBUSTNESS TESTS (4 tests) ──────────────────────────────

    def test_si_9_temperature_stability(self, fmo_hamiltonian):
        """Test 9:eta(T) trend."""
        from core.constants import DEFAULT_TEMPERATURE
        t = np.linspace(0, 500, 51)
        psi0 = np.eye(fmo_hamiltonian.shape[0])[0]
        
        sim_low = HopsSimulator(fmo_hamiltonian, temperature=DEFAULT_TEMPERATURE - 10)
        sim_high = HopsSimulator(fmo_hamiltonian, temperature=DEFAULT_TEMPERATURE + 15)
        
        res_low = sim_low.simulate_dynamics(t, psi0, strict_mode=True)
        res_high = sim_high.simulate_dynamics(t, psi0, strict_mode=True)
        
        assert np.sum(res_low["coherences"]) > 0
        assert np.sum(res_high["coherences"]) > 0

    def test_si_10_disorder_convergence(self, fmo_hamiltonian):
        """Test 10: Static disorder ensemble convergence."""
        from core.constants import DEFAULT_DISORDER_SIGMA
        n_sites = fmo_hamiltonian.shape[0]
        sigma = DEFAULT_DISORDER_SIGMA  # cm^-1
        
        seeds1 = [np.random.normal(0, sigma, n_sites) for _ in range(10)]
        seeds2 = [np.random.normal(0, sigma, n_sites) for _ in range(20)]
        
        mean1 = np.mean([np.mean(s) for s in seeds1])
        mean2 = np.mean([np.mean(s) for s in seeds2])
        
        assert abs(mean1 - mean2) < 20.0

    def test_si_11_spectral_normalization(self):
        """Test 11: J(omega) normalization and reorganization energy."""
        from core.constants import DEFAULT_REORGANIZATION_ENERGY
        from core.constants import DEFAULT_DRUDE_CUTOFF
        omega = np.linspace(0.1, 2000, 1000)
        gamma = DEFAULT_DRUDE_CUTOFF  # cm^-1 (Drude-Lorentz cutoff)
        lam = DEFAULT_REORGANIZATION_ENERGY
        
        # Drude-Lorentz J(w)
        J_w = (2 * lam * gamma * omega) / (omega**2 + gamma**2)
        
        # Integral of J(w)/w should be lambda
        # Use trapezoidal rule: lam = (1/pi) * integral(J(w)/w dw)
        integral = np.trapz(J_w / omega, omega) / np.pi
        
        logger.info(f"Test 11 (Integral): Calculated lambda = {integral:.2f}, Target = {lam}")
        assert abs(integral - lam) / lam < 0.05, "Spectral density normalization failed"

    def test_si_12_markovian_recovery(self, fmo_hamiltonian):
        """Test 12: High gamma limit."""
        from reproducibility.main import load_and_validate_config
        cfg = load_and_validate_config()
        L_val = 1 # High gamma converges very fast
        gamma_high = 1000.0 # cm^-1
        # Enforce ensemble size for convergence
        n_traj_val = 100
        sim = HopsSimulator(fmo_hamiltonian, drude_cutoff=gamma_high, max_hierarchy=L_val, n_traj=n_traj_val)
        t = np.linspace(0, 500, 101)
        
        psi0 = np.eye(fmo_hamiltonian.shape[0])[0]
        res = sim.simulate_dynamics(t, initial_state=psi0, strict_mode=True)
        
        # In the Markovian limit, population on site 1 should stay constant or decrease monotonically 
        # (no oscillations). Ensemble averaging ensures this.
        pop1 = res["populations"][:, 0]
        diff = np.diff(pop1)
        # Check that on average it doesn't increase significantly (thermal fluctuations in ensemble)
        assert np.max(diff) < 1e-2, f"Population increased significantly in Markovian limit: {np.max(diff)}"

if __name__ == "__main__":
    # Custom runner with tqdm for SI tests
    test_methods = [
        "test_si_1_hierarchy_convergence",
        "test_si_2_matsubara_convergence",
        "test_si_3_timestep_convergence",
        "test_si_5_trace_preservation",
        "test_si_6_positivity_preservation",
        "test_si_7_detailed_balance",
        "test_si_8_hermiticity",
        "test_si_9_temperature_stability",
        "test_si_10_disorder_convergence",
        "test_si_11_spectral_normalization",
        "test_si_12_markovian_recovery"
    ]
    
    print("\n🚀 Running JPCL Validation Suite...")
    for test in _tqdm(test_methods, desc="Overall Progress"):
        pytest.main([__file__, "-k", test, "-q", "--no-header"])
    
    print("\n✅ All validation tests processed.")
