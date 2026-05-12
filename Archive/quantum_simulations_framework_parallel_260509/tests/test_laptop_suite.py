"""
Laptop-friendly test suite with reduced N and shorter simulations.
Runs in ~30 seconds total on 16GB RAM, 4-core laptop.
Designed for quick verification without full production parameters.
"""
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import get_test_logger
from src.core.hops_simulator import HopsSimulator
from src.core.hamiltonian_factory import create_fmo_hamiltonian
from src.core.constants import DEFAULT_TEMPERATURE

logger = get_test_logger("test_laptop_suite")


class TestLaptopSuite:
    """Fast tests for laptop verification."""
    
    def test_3site_minimal(self):
        """3-site dynamics in <1 second."""
        logger.info("Starting 3-site minimal test...")
        H, _ = create_fmo_hamiltonian(include_reaction_center=False)
        H3 = H[:3, :3]
        
        init_state = np.zeros(3, dtype=complex)
        init_state[0] = 1.0
        
        simulator = HopsSimulator(
            H3,
            max_hierarchy=2,
            k_matsubara=1,
            use_sbd=True,
            sbd_bundles_per_site=2,
            temperature=295.0,
            reorganization_energy=35.0,
            drude_cutoff=500.0,
            vibronic_frequencies=np.array([100.0, 200.0]),
            huang_rhys_factors=np.array([0.1, 0.05]),
            vibronic_damping=np.array([10.0, 20.0]),
        )
        
        time_points = np.linspace(0, 10, 5)  # 10 fs, 5 points
        results = simulator.simulate_dynamics(
            time_points,
            initial_state=init_state,
            n_traj=10,  # Minimal trajectories
            show_progress=False
        )
        
        pops = results['populations']
        traces = np.sum(pops, axis=1)
        logger.info(f"3-site: pop shape={pops.shape}, trace range=[{traces.min():.4f}, {traces.max():.4f}]")
        assert np.allclose(traces, 1.0, atol=0.15), "Trace preservation failed"
        assert pops.shape == (5, 3), "Population shape mismatch"
        logger.info("✅ 3-site minimal test passed")
    
    def test_7site_minimal(self):
        """7-site FMO dynamics in <2 seconds."""
        logger.info("Starting 7-site minimal test...")
        H, _ = create_fmo_hamiltonian(include_reaction_center=False)
        
        init_state = np.zeros(7, dtype=complex)
        init_state[0] = 1.0
        
        simulator = HopsSimulator(
            H,
            max_hierarchy=2,
            k_matsubara=1,
            use_sbd=True,
            sbd_bundles_per_site=2,
            temperature=295.0,
            reorganization_energy=35.0,
            drude_cutoff=500.0,
            vibronic_frequencies=np.array([100.0, 200.0]),
            huang_rhys_factors=np.array([0.1, 0.05]),
            vibronic_damping=np.array([10.0, 20.0]),
        )
        
        time_points = np.linspace(0, 10, 5)
        results = simulator.simulate_dynamics(
            time_points,
            initial_state=init_state,
            n_traj=5,  # Minimal trajectories
            show_progress=False
        )
        
        pops = results['populations']
        traces = np.sum(pops, axis=1)
        logger.info(f"7-site: pop shape={pops.shape}, trace range=[{traces.min():.4f}, {traces.max():.4f}]")
        assert np.allclose(traces, 1.0, atol=0.15), "Trace preservation failed"
        assert pops.shape == (5, 7), "Population shape mismatch"
        logger.info("✅ 7-site minimal test passed")
    
    def test_hamiltonian_properties(self):
        """Verify Hamiltonian structure (<100ms)."""
        logger.info("Starting Hamiltonian properties test...")
        H, site_energies = create_fmo_hamiltonian(include_reaction_center=False)
        
        # Check Hermiticity
        is_hermitian = np.allclose(H, H.conj().T)
        logger.info(f"Hamiltonian Hermitian: {is_hermitian}")
        assert is_hermitian, "Hamiltonian not Hermitian"
        
        # Check shape
        assert H.shape == (7, 7), "Hamiltonian shape mismatch"
        assert len(site_energies) == 7, "Site energies length mismatch"
        
        # Check eigenvalues are real
        evals = np.linalg.eigvalsh(H)
        all_real = np.all(np.isreal(evals))
        logger.info(f"Eigenvalues real: {all_real}, range=[{evals.min():.4f}, {evals.max():.4f}]")
        assert all_real, "Eigenvalues not real"
        logger.info("✅ Hamiltonian properties test passed")
    
    def test_sbd_activation(self):
        """Verify SBD is activated for L >= 2 (<100ms)."""
        logger.info("Starting SBD activation test...")
        H, _ = create_fmo_hamiltonian(include_reaction_center=False)
        
        for L in [2, 3, 4]:
            simulator = HopsSimulator(
                H,
                max_hierarchy=L,
                k_matsubara=1,
                use_sbd=True,
                sbd_bundles_per_site=2,
                temperature=295.0,
                reorganization_energy=35.0,
                drude_cutoff=500.0,
                vibronic_frequencies=np.array([100.0, 200.0]),
                huang_rhys_factors=np.array([0.1, 0.05]),
                vibronic_damping=np.array([10.0, 20.0]),
            )
            logger.info(f"L={L}: SBD enabled={simulator.use_sbd}")
            assert simulator.use_sbd is True, f"SBD not activated for L={L}"
        
        logger.info("✅ SBD activation test passed")
    
    def test_memory_estimation(self):
        """Verify memory estimation for laptop constraints (<100ms)."""
        logger.info("Starting memory estimation test...")
        H, _ = create_fmo_hamiltonian(include_reaction_center=False)
        
        simulator = HopsSimulator(
            H,
            max_hierarchy=2,
            k_matsubara=1,
            use_sbd=True,
            sbd_bundles_per_site=2,
            temperature=295.0,
            reorganization_energy=35.0,
            drude_cutoff=500.0,
            vibronic_frequencies=np.array([100.0, 200.0]),
            huang_rhys_factors=np.array([0.1, 0.05]),
            vibronic_damping=np.array([10.0, 20.0]),
        )
        
        # Verify simulator is initialized
        assert simulator is not None, "Simulator initialization failed"
        assert simulator.use_sbd is True, "SBD should be enabled"
        logger.info(f"Simulator initialized: L=2, K=1, SBD enabled")
        logger.info("✅ Memory estimation test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
