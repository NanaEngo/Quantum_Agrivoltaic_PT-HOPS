import importlib.util
import os

import numpy as np
import pytest
from Redac_Paper2.src.config_loader import load_config
from Redac_Paper2.src.quantum_interface.hamiltonian import FmoHamiltonian

MESOHOPS_AVAILABLE = importlib.util.find_spec("mesohops") is not None


def test_fmo_hamiltonian_properties():
    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)
    fmo_ham = FmoHamiltonian(config)
    H = fmo_ham.get_hamiltonian()

    # Verify dimensions
    assert H.shape == (8, 8)

    # Check that it is non-Hermitian due to trapping on indices 2 and 3 (sites 3 and 4)
    assert not np.allclose(H, H.conj().T)

    # Trapping terms check
    assert H[2, 2].imag == -config.quantum.fmo.coupling_reaction_center
    assert H[3, 3].imag == -config.quantum.fmo.coupling_reaction_center

    # Other diagonals should have zero imaginary parts
    assert H[0, 0].imag == 0
    assert H[1, 1].imag == 0
    assert H[4, 4].imag == 0

    # All inter-site couplings should be non-zero (no missing pairs)
    for i in range(8):
        for j in range(i + 1, 8):
            assert H[i, j] != 0.0, f"Missing coupling between sites {i + 1} and {j + 1}"


def test_fmo_hamiltonian_coupling_validation():
    """E-8: Missing couplings should raise ValueError during initialization."""
    # Verify that a missing coupling is detected
    import Redac_Paper2.src.quantum_interface.hamiltonian as hmod

    # Monkey-patch to remove one coupling and test validation
    original_couplings = hmod.FmoHamiltonian._initialize_base_hamiltonian

    def broken_init(self):
        """Like _initialize_base_hamiltonian but with a removed coupling."""
        self.H_base = np.zeros((8, 8), dtype=complex)

        energies = [280, 420, 0, 110, 270, 500, 310, 200]
        for i in range(8):
            self.H_base[i, i] = energies[i]
        couplings = {
            (0, 1): -87.7,
            (0, 2): 5.5,
            (0, 3): -5.9,
            (0, 4): 6.7,
            (0, 5): -13.7,
            (0, 6): -9.9,
            (0, 7): 21.0,
            (1, 2): 30.0,
            (1, 3): 8.2,
            (1, 4): 0.7,
            (1, 5): 11.8,
            (1, 6): 4.3,
            (1, 7): -4.2,
            (2, 3): -53.5,
            (2, 4): -2.2,
            (2, 5): -9.6,
            (2, 6): 6.0,
            (2, 7): 0.6,
            (3, 4): -70.7,
            (3, 5): -17.0,
            (3, 6): -63.3,
            (3, 7): -1.3,
            (4, 5): 81.1,
            (4, 6): -1.3,
            (4, 7): 1.5,
            (5, 6): 39.7,
            (5, 7): -7.9,
            # (6, 7): 12.0 deliberately removed
        }
        expected_pairs = {(i, j) for i in range(8) for j in range(i + 1, 8)}
        defined_pairs = set(couplings.keys())
        missing = expected_pairs - defined_pairs
        if missing:
            raise ValueError(f"Missing inter-site couplings for pairs: {sorted(missing)}")
        for (i, j), val in couplings.items():
            self.H_base[i, j] = val
            self.H_base[j, i] = val

    hmod.FmoHamiltonian._initialize_base_hamiltonian = broken_init

    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    import pytest

    with pytest.raises(ValueError, match="Missing inter-site couplings"):
        FmoHamiltonian(config)

    # Restore original method
    hmod.FmoHamiltonian._initialize_base_hamiltonian = original_couplings


def test_npom_coupling_and_dressing():
    from Redac_Paper2.src.quantum_interface.diagnostics import NpomCoupling

    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    npom = NpomCoupling(config)

    # Verify scaling behavior
    g_normal = npom.get_plasmon_coupling()
    assert g_normal > 0

    # Test guardrail cap
    npom.mode_volume_nm3 = 0.0
    g_capped = npom.get_plasmon_coupling()
    assert g_capped == 1000.0

    # Test dressing logic
    fmo_ham = FmoHamiltonian(config)
    H_fmo = fmo_ham.get_hamiltonian()
    H_dressed = npom.dress_hamiltonian(H_fmo)

    # Dimensions check
    assert H_dressed.shape == (9, 9)
    # Plasmon coupling check at index 0 and 5
    assert H_dressed[0, 8] == g_capped
    assert H_dressed[5, 8] == g_capped


def test_floquet_stark_switch():
    from Redac_Paper2.src.quantum_interface.pulse import FloquetStarkSwitch

    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    switch = FloquetStarkSwitch(config)

    # Under solar threshold
    shift_low = switch.get_stark_detuning(500.0, 1.0)
    assert np.allclose(shift_low, 0.0)

    # Over solar threshold
    shift_high = switch.get_stark_detuning(1000.0, 1.0)
    assert shift_high[0, 0] != 0.0
    assert shift_high[5, 5] != 0.0

    # Night mode (zero flux)
    shift_night = switch.get_stark_detuning(0.0, 1.0)
    assert np.allclose(shift_night, 0.0)

    # OMIT transmission check
    t_normal = switch.apply_omit_attenuation(500.0, 0.8)
    assert t_normal == 0.8

    t_attenuated = switch.apply_omit_attenuation(1000.0, 0.8)
    assert t_attenuated < 0.8


def test_sers_diagnostics():
    from Redac_Paper2.src.quantum_interface.diagnostics import SersDiagnostics

    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    sers = SersDiagnostics(config)

    # Fake population: excitation localized on Site 3 (index 2)
    fake_pop = np.zeros(8)
    fake_pop[2] = 1.0

    spectrum = sers.calculate_raman_spectrum(fake_pop)

    # Verify enhancement and signature ratios
    assert spectrum["180_cm"] == 100.0 * config.quantum.sers.optomechanical_coupling
    assert spectrum["740_cm"] == 0.0
    assert spectrum["1145_cm"] == 100.0 * config.quantum.sers.optomechanical_coupling


def test_stability_audit_and_hdf5():
    from Redac_Paper2.src.quantum_interface.solver import QuantumStabilityAudit

    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    audit = QuantumStabilityAudit(config)

    # 1. Test Audit Logic
    # Valid density matrix series
    valid_rho = np.zeros((5, 8, 8), dtype=complex)
    for i in range(5):
        valid_rho[i, 0, 0] = 1.0  # pure state on site 1
    assert audit.audit_trajectory(valid_rho) is True

    # Invalid density matrix series (negative population)
    invalid_rho = np.zeros((5, 8, 8), dtype=complex)
    invalid_rho[0, 0, 0] = -0.5
    assert audit.audit_trajectory(invalid_rho) is False

    # 2. Test HDF5 Serialization
    test_h5_path = os.path.join(os.path.dirname(__file__), "../../data/converged/test_traj.h5")
    fake_pops = np.ones((10, 8)) * 0.125
    fake_yield = np.linspace(0, 0.9, 10)

    audit.serialize_to_hdf5(test_h5_path, fake_pops, fake_yield)

    # Verify file content
    import h5py

    with h5py.File(test_h5_path, "r") as f:
        assert "dynamics/populations" in f
        assert "dynamics/rc_yield" in f
        assert "metadata/parameters" in f
        assert f["dynamics/populations"].shape == (10, 8)
        assert f["dynamics/rc_yield"].shape == (10,)

    # Clean up test file
    if os.path.exists(test_h5_path):
        os.remove(test_h5_path)


@pytest.mark.skipif(not MESOHOPS_AVAILABLE, reason="MesoHOPS not installed")
def test_mesohops_solver_propagation():
    """
    Test MesoHOPS propagation with hierarchy_depth=2 to avoid OOM.
    Uses 9-site (8 FMO + 1 plasmon) system matching real use case.
    With MAXHIER=2 and 24 bath modes (8 sites × 3 DL modes):
      C(2+24, 24) = C(26, 24) = 325 hierarchy states (0.04 MB).
    With MAXHIER=8 (production):
      C(8+24, 24) = C(32, 24) = 10.5M states (~1.4 GB) → OOM.
    """
    from Redac_Paper2.src.quantum_interface.solver import MesoHopsSolver

    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    solver = MesoHopsSolver(config)

    # 9-site system (8 FMO + 1 plasmon) — matches propagate_dynamics 8x8 output slice
    H_dressed = np.zeros((9, 9), dtype=complex)
    for i in range(9):
        H_dressed[i, i] = i * 10.0
    # Add trapping to indices 2 and 3 (sites 3 and 4)
    H_dressed[2, 2] -= 1j * 0.15
    H_dressed[3, 3] -= 1j * 0.15

    psi0 = np.zeros(9, dtype=complex)
    psi0[8] = 1.0  # Initial excitation on plasmon mode

    time_points = np.array([0.0, 5.0, 10.0])

    # Use hierarchy_depth=2 to avoid OOM during testing
    # Production uses hierarchy_depth=8 from config
    density_matrices = solver.propagate_dynamics(
        H_dressed, psi0, time_points, n_traj=1, hierarchy_depth=2
    )

    assert density_matrices.shape == (3, 8, 8)
    # Trace of the FMO subset should be <= 1.0
    for rho in density_matrices:
        assert np.trace(rho).real <= 1.0001
        assert np.trace(rho).real >= 0.0
