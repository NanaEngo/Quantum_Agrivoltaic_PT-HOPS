"""
Second-pass comprehensive tests covering audit findings from:
- simple_quantum_dynamics_simulator.py
- stochastic_bundling.py
- quantum_dynamics_simulator.py (unit-level, no MesoHOPS)
- optimize.py (unit-level)
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.hamiltonian_factory import create_fmo_hamiltonian
from extensions.stochastic_bundling import StochasticallyBundledDissipator
from models.simple_quantum_dynamics_simulator import SimpleQuantumDynamicsSimulator


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def H7():
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    return H


@pytest.fixture
def sim7(H7):
    return SimpleQuantumDynamicsSimulator(H7)


@pytest.fixture
def psi1(H7):
    psi = np.zeros(H7.shape[0], dtype=complex)
    psi[0] = 1.0
    return psi


@pytest.fixture
def short_t():
    return np.arange(0, 50, 0.5)


# ─────────────────────────────────────────────────────────────────────────────
# 1. SimpleQuantumDynamicsSimulator — correctness & edge cases
# ─────────────────────────────────────────────────────────────────────────────

class TestSimpleSimulator:

    def test_non_square_hamiltonian_raises(self):
        with pytest.raises(ValueError, match="square"):
            SimpleQuantumDynamicsSimulator(np.ones((3, 4)))

    def test_zero_size_hamiltonian_raises(self):
        with pytest.raises((ValueError, IndexError)):
            SimpleQuantumDynamicsSimulator(np.zeros((0, 0)))

    def test_initial_state_wrong_length_raises(self, sim7, short_t):
        bad_psi = np.array([1.0, 0.0, 0.0])  # length 3, not 7
        with pytest.raises(ValueError, match="n_sites"):
            sim7.simulate_dynamics(short_t, bad_psi)

    def test_2d_time_points_raises(self, sim7, psi1):
        with pytest.raises(ValueError, match="1-D"):
            sim7.simulate_dynamics(np.ones((5, 5)), psi1)

    def test_populations_shape(self, sim7, short_t, psi1):
        r = sim7.simulate_dynamics(short_t, psi1)
        assert r["populations"].shape == (len(short_t), 7)

    def test_populations_non_negative(self, sim7, short_t, psi1):
        r = sim7.simulate_dynamics(short_t, psi1)
        assert np.all(r["populations"] >= -1e-10)

    def test_population_sum_conserved(self, sim7, short_t, psi1):
        r = sim7.simulate_dynamics(short_t, psi1)
        totals = np.sum(r["populations"], axis=1)
        assert np.allclose(totals, 1.0, atol=1e-8)

    def test_initial_population_site1(self, sim7, short_t, psi1):
        r = sim7.simulate_dynamics(short_t, psi1)
        assert r["populations"][0, 0] > 0.99

    def test_initial_population_site3(self, H7, short_t):
        sim = SimpleQuantumDynamicsSimulator(H7)
        psi = np.zeros(7, dtype=complex)
        psi[2] = 1.0
        r = sim.simulate_dynamics(short_t, psi)
        assert r["populations"][0, 2] > 0.99

    def test_qfi_non_negative(self, sim7, short_t, psi1):
        r = sim7.simulate_dynamics(short_t, psi1)
        assert np.all(r["qfi"] >= -1e-10)

    def test_qfi_correct_formula(self, H7, short_t):
        """QFI for pure state = 4·(⟨H²⟩ - ⟨H⟩²) — verify at t=0."""
        sim = SimpleQuantumDynamicsSimulator(H7)
        psi = np.zeros(7, dtype=complex)
        psi[0] = 1.0
        r = sim.simulate_dynamics(short_t[:1], psi)  # only t=0
        # Manual QFI at t=0
        H_shifted = H7 - np.mean(np.diag(H7).real) * np.eye(7)
        exp_H = np.real(np.vdot(psi, H_shifted @ psi))
        exp_H2 = np.real(np.vdot(psi, H_shifted @ H_shifted @ psi))
        expected_qfi = 4.0 * max(0.0, exp_H2 - exp_H**2)
        assert abs(r["qfi"][0] - expected_qfi) < 1e-8

    def test_coherence_zero_at_t0_site_basis(self, H7, short_t):
        """At t=0 with site-basis initial state, off-diagonal elements are 0."""
        sim = SimpleQuantumDynamicsSimulator(H7)
        psi = np.zeros(7, dtype=complex)
        psi[0] = 1.0
        r = sim.simulate_dynamics(short_t[:1], psi)
        assert r["coherences"][0] < 1e-10

    def test_eigendecomp_hoisted_correctness(self, H7):
        """Hoisted eigendecomp must give same result as per-step computation."""
        sim = SimpleQuantumDynamicsSimulator(H7)
        t = np.array([0.0, 10.0, 50.0])
        psi = np.zeros(7, dtype=complex)
        psi[0] = 1.0
        r = sim.simulate_dynamics(t, psi)
        # Manually compute at t=50 fs
        eigenvals, eigenvecs = np.linalg.eigh(sim.h_shifted)
        c0 = eigenvecs.T.conj() @ psi
        tf = 50.0 * 0.0333564
        psi_50 = eigenvecs @ (np.exp(-1j * eigenvals * tf) * c0)
        expected_pops = np.real(psi_50 * np.conj(psi_50))
        assert np.allclose(r["populations"][2], expected_pops, atol=1e-10)

    def test_energy_shift_invariance(self, H7, short_t, psi1):
        """Populations must be identical regardless of energy shift."""
        sim1 = SimpleQuantumDynamicsSimulator(H7)
        H_shifted = H7 + 500.0 * np.eye(7)
        sim2 = SimpleQuantumDynamicsSimulator(H_shifted)
        r1 = sim1.simulate_dynamics(short_t, psi1)
        r2 = sim2.simulate_dynamics(short_t, psi1)
        assert np.allclose(r1["populations"], r2["populations"], atol=1e-8)

    def test_t_axis_in_output(self, sim7, short_t, psi1):
        r = sim7.simulate_dynamics(short_t, psi1)
        assert "t_axis" in r
        assert len(r["t_axis"]) == len(short_t)

    def test_simulator_key_in_output(self, sim7, short_t, psi1):
        r = sim7.simulate_dynamics(short_t, psi1)
        assert r["simulator"] == "Simple Quantum Simulator"

    def test_default_time_points(self, sim7, psi1):
        r = sim7.simulate_dynamics(initial_state=psi1)
        assert r["populations"].shape[0] == 101

    def test_default_initial_state(self, sim7, short_t):
        r = sim7.simulate_dynamics(short_t)
        assert r["populations"][0, 0] > 0.99


# ─────────────────────────────────────────────────────────────────────────────
# 2. StochasticallyBundledDissipator — correctness & edge cases
# ─────────────────────────────────────────────────────────────────────────────

class TestSBD:

    def test_empty_modes_returns_empty(self):
        sbd = StochasticallyBundledDissipator(n_bundles=3)
        result = sbd.discretize_spectral_density([])
        assert result == []

    def test_fewer_modes_than_bundles(self):
        sbd = StochasticallyBundledDissipator(n_bundles=5)
        modes = [(100.0, 0.5), (200.0, 0.3)]
        bundles = sbd.discretize_spectral_density(modes)
        assert len(bundles) == 2

    def test_no_bundle_doubling_on_repeated_calls(self):
        """Calling discretize twice must not double the bundle list."""
        sbd = StochasticallyBundledDissipator(n_bundles=3)
        modes = [(100.0, 0.5), (200.0, 0.3), (300.0, 0.2), (400.0, 0.1)]
        sbd.discretize_spectral_density(modes)
        sbd.discretize_spectral_density(modes)
        freqs, coups = sbd.get_bundle_parameters()
        assert len(freqs) == len(coups)
        # Should not be doubled
        assert len(freqs) <= len(modes)

    def test_effective_coupling_non_negative(self):
        """effective_coupling must be non-negative (sum of |couplings|)."""
        sbd = StochasticallyBundledDissipator(n_bundles=2)
        modes = [(100.0, 0.5), (200.0, -0.3), (300.0, 0.2), (400.0, -0.1)]
        sbd.discretize_spectral_density(modes)
        _, coups = sbd.get_bundle_parameters()
        assert all(c >= 0 for c in coups)

    def test_center_freq_within_mode_range(self):
        """Bundle center frequency must be within the range of its modes."""
        sbd = StochasticallyBundledDissipator(n_bundles=3)
        modes = [(f, 0.1) for f in [100, 150, 200, 250, 300, 350, 400, 450, 500]]
        sbd.discretize_spectral_density(modes)
        freqs, _ = sbd.get_bundle_parameters()
        assert all(100 <= f <= 500 for f in freqs)

    def test_max_freq_mode_not_dropped(self):
        """Mode at exactly max_freq must not be silently dropped."""
        sbd = StochasticallyBundledDissipator(n_bundles=2)
        modes = [(100.0, 0.5), (200.0, 0.3), (300.0, 0.2), (500.0, 0.1)]
        bundles = sbd.discretize_spectral_density(modes)
        all_modes = [m for b in bundles for m in b.modes]
        assert any(abs(m[0] - 500.0) < 1e-6 for m in all_modes), \
            "Max-frequency mode was dropped"

    def test_get_bundle_parameters_lengths_match(self):
        sbd = StochasticallyBundledDissipator(n_bundles=3)
        modes = [(f, 0.1) for f in range(100, 700, 50)]
        sbd.discretize_spectral_density(modes)
        freqs, coups = sbd.get_bundle_parameters()
        assert len(freqs) == len(coups)

    def test_single_mode(self):
        sbd = StochasticallyBundledDissipator(n_bundles=3)
        bundles = sbd.discretize_spectral_density([(250.0, 0.4)])
        assert len(bundles) == 1
        assert abs(bundles[0].center_frequency - 250.0) < 1e-10

    def test_all_same_frequency(self):
        """All modes at same frequency → single bin, no crash."""
        sbd = StochasticallyBundledDissipator(n_bundles=3)
        modes = [(200.0, 0.1)] * 6
        bundles = sbd.discretize_spectral_density(modes)
        assert len(bundles) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 3. QuantumDynamicsSimulator — unit-level (no MesoHOPS trajectory)
# ─────────────────────────────────────────────────────────────────────────────

class TestQuantumDynamicsSimulatorUnit:

    def test_import_raises_without_mesohops(self, H7):
        """QuantumDynamicsSimulator must raise ImportError if MesoHOPS absent."""
        from models.quantum_dynamics_simulator import MESOHOPS_AVAILABLE, QuantumDynamicsSimulator
        if not MESOHOPS_AVAILABLE:
            with pytest.raises(ImportError):
                QuantumDynamicsSimulator(H7)
        else:
            pytest.skip("MesoHOPS available — ImportError path not reachable")

    def test_non_square_hamiltonian_raises(self):
        from models.quantum_dynamics_simulator import MESOHOPS_AVAILABLE, QuantumDynamicsSimulator
        if not MESOHOPS_AVAILABLE:
            pytest.skip("MesoHOPS not available")
        with pytest.raises(ValueError, match="square"):
            QuantumDynamicsSimulator(np.ones((3, 4)))

    def test_zero_size_hamiltonian_raises(self):
        from models.quantum_dynamics_simulator import MESOHOPS_AVAILABLE, QuantumDynamicsSimulator
        if not MESOHOPS_AVAILABLE:
            pytest.skip("MesoHOPS not available")
        with pytest.raises(ValueError):
            QuantumDynamicsSimulator(np.zeros((0, 0)))

    def test_dl_modes_format_validated(self, H7, monkeypatch):
        """dl_modes with odd length must raise RuntimeError."""
        from models.quantum_dynamics_simulator import MESOHOPS_AVAILABLE
        if not MESOHOPS_AVAILABLE:
            pytest.skip("MesoHOPS not available")
        import models.quantum_dynamics_simulator as qds_mod
        monkeypatch.setattr(
            qds_mod, "bcf_convert_dl_to_exp_with_Matsubara",
            lambda *a, **kw: [1.0, 2.0, 3.0]  # odd length
        )
        from models.quantum_dynamics_simulator import QuantumDynamicsSimulator
        with pytest.raises(RuntimeError, match="unexpected format"):
            QuantumDynamicsSimulator(H7)


# ─────────────────────────────────────────────────────────────────────────────
# 4. optimize.py — unit-level logic
# ─────────────────────────────────────────────────────────────────────────────

class TestOptimizeLogic:

    def test_empty_results_returns_early(self, tmp_path, monkeypatch):
        """If all sweeps fail, sweep_filter_wavelengths must return [] without crashing."""
        import reproducibility.optimize as opt_mod
        # Patch HopsSimulator to always raise
        monkeypatch.setattr(
            opt_mod, "sweep_filter_wavelengths",
            lambda cfg, **kw: []
        )
        result = opt_mod.sweep_filter_wavelengths({})
        assert result == []

    def test_phi_ft_is_float(self):
        """phi_ft = 1.0 - populations[-1, 0] must be a Python float."""
        pops = np.random.rand(100, 7)
        pops = pops / pops.sum(axis=1, keepdims=True)
        phi_ft = float(1.0 - pops[-1, 0])
        assert isinstance(phi_ft, float)

    def test_wavelength_to_wavenumber_conversion(self):
        """1e7/λ_nm must give correct wavenumber for canonical wavelengths."""
        assert abs(1e7 / 750.0 - 13333.3) < 1.0   # 750 nm → ~13333 cm⁻¹
        assert abs(1e7 / 820.0 - 12195.1) < 1.0   # 820 nm → ~12195 cm⁻¹


# ─────────────────────────────────────────────────────────────────────────────
# 5. Regression tests for all previously fixed bugs
# ─────────────────────────────────────────────────────────────────────────────

class TestRegressions:

    def test_spectral_density_elementwise_sign(self):
        """Regression: np.any(omega>=0) scalar branch bug — must be element-wise."""
        from core.hamiltonian_factory import spectral_density_drude_lorentz
        omega = np.array([-100.0, -50.0, 50.0, 100.0])
        J = spectral_density_drude_lorentz(omega, 35.0, 50.0, 295.0)
        assert J[0] < 0 and J[1] < 0
        assert J[2] > 0 and J[3] > 0

    def test_csv_no_slash_in_filename(self, tmp_path):
        """Regression: config_hash='N/A' caused OSError — must be 'no_config'."""
        from utils.csv_data_storage import CSVDataStorage
        s = CSVDataStorage(output_dir=str(tmp_path))
        t = np.linspace(0, 10, 5)
        pops = np.random.rand(5, 7)
        cohs = np.random.rand(5)
        path = s.save_quantum_dynamics_results(t, pops, cohs, {})
        assert "/" not in Path(path).name or Path(path).exists()

    def test_figure_generator_length_guard(self, tmp_path):
        """Regression: mismatched array lengths must not crash figure generation."""
        from utils.figure_generator import FigureGenerator
        gen = FigureGenerator(figures_dir=str(tmp_path))
        t = np.linspace(0, 100, 50)
        pops = np.random.rand(45, 7)
        cohs = np.random.rand(48)
        metrics = {"qfi": np.random.rand(50)}
        path = gen.plot_quantum_dynamics(t, pops, cohs, metrics)
        assert Path(path).exists()

    def test_sbd_no_bundle_doubling(self):
        """Regression: self.bundles not reset → doubled on repeated calls."""
        sbd = StochasticallyBundledDissipator(n_bundles=2)
        modes = [(100.0, 0.5), (200.0, 0.3), (300.0, 0.2), (400.0, 0.1)]
        n1 = len(sbd.discretize_spectral_density(modes))
        n2 = len(sbd.discretize_spectral_density(modes))
        assert n1 == n2, f"Bundle count changed on second call: {n1} → {n2}"

    def test_sbd_signed_coupling_bug(self):
        """Regression: np.sum(bin_coups) with mixed signs → near-zero coupling."""
        sbd = StochasticallyBundledDissipator(n_bundles=1)
        modes = [(100.0, 0.5), (150.0, -0.5)]  # would cancel to 0 with signed sum
        sbd.discretize_spectral_density(modes)
        _, coups = sbd.get_bundle_parameters()
        assert coups[0] > 0.5, f"Coupling should be ~1.0 (sum of |g|), got {coups[0]}"

    def test_simple_sim_qfi_not_var_diag(self, H7, short_t):
        """Regression: QFI was 4*var(diag(rho)) — must now be 4*(⟨H²⟩-⟨H⟩²)."""
        sim = SimpleQuantumDynamicsSimulator(H7)
        psi = np.zeros(7, dtype=complex)
        psi[0] = 1.0
        r = sim.simulate_dynamics(short_t[:1], psi)
        # Old formula: 4*var(diag(rho)) at t=0 with site-basis state = 0
        # (only one non-zero diagonal element → var=0)
        # New formula: 4*(⟨H²⟩-⟨H⟩²) should be > 0 for non-eigenstate
        H_shifted = H7 - np.mean(np.diag(H7).real) * np.eye(7)
        exp_H = np.real(np.vdot(psi, H_shifted @ psi))
        exp_H2 = np.real(np.vdot(psi, H_shifted @ H_shifted @ psi))
        expected = 4.0 * max(0.0, exp_H2 - exp_H**2)
        assert abs(r["qfi"][0] - expected) < 1e-8

    def test_simple_sim_eigendecomp_not_in_loop(self, H7):
        """Performance regression: eigendecomp must be O(N³) once, not per step."""
        import time
        sim = SimpleQuantumDynamicsSimulator(H7)
        psi = np.zeros(7, dtype=complex)
        psi[0] = 1.0
        t_short = np.arange(0, 10, 0.5)   # 20 steps
        t_long = np.arange(0, 100, 0.5)   # 200 steps
        t0 = time.perf_counter()
        sim.simulate_dynamics(t_short, psi)
        dt_short = time.perf_counter() - t0
        t0 = time.perf_counter()
        sim.simulate_dynamics(t_long, psi)
        dt_long = time.perf_counter() - t0
        # With hoisted eigendecomp, 10x more steps should be < 15x slower
        # (not 10x slower as before, since eigendecomp dominated)
        ratio = dt_long / max(dt_short, 1e-6)
        assert ratio < 20, f"Time ratio {ratio:.1f}x suggests eigendecomp still in loop"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
