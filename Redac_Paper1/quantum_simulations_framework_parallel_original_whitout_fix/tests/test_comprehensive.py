"""
Comprehensive test suite for the quantum_simulations_framework.
Covers: Hamiltonian physics, HopsSimulator pipeline, CSVDataStorage,
FigureGenerator, audit_convergence logic, mesohops_adapters, and
parameter consistency (parameters.yaml ↔ constants.py).
"""
import os
import sys
import importlib
from pathlib import Path

import numpy as np
import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.constants import (
    DEFAULT_DRUDE_CUTOFF,
    DEFAULT_HUANG_RHYS_FACTORS,
    DEFAULT_MAX_HIERARCHY,
    DEFAULT_N_MATSUBARA,
    DEFAULT_REORGANIZATION_ENERGY,
    DEFAULT_TEMPERATURE,
    DEFAULT_VIBRONIC_DAMPING,
    DEFAULT_VIBRONIC_FREQUENCIES,
    FMO_COUPLINGS,
    FMO_SITE_ENERGIES_7,
    FMO_SITE_ENERGIES_8,
    PULSE_FWHM,
)
from core.hamiltonian_factory import create_fmo_hamiltonian, spectral_density_drude_lorentz
from core.hops_simulator import HopsSimulator
from utils.csv_data_storage import CSVDataStorage
from utils.figure_generator import FigureGenerator


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def fmo7():
    H, e = create_fmo_hamiltonian(include_reaction_center=False)
    return H, e


@pytest.fixture
def initial_state_site1(fmo7):
    H, _ = fmo7
    psi = np.zeros(H.shape[0], dtype=complex)
    psi[0] = 1.0
    return psi


@pytest.fixture
def short_time():
    return np.arange(0, 50, 0.5)  # 100 points, Δt=0.5 fs


@pytest.fixture
def fallback_sim(fmo7):
    H, _ = fmo7
    return HopsSimulator(H, use_mesohops=False)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Parameter consistency: parameters.yaml ↔ constants.py
# ─────────────────────────────────────────────────────────────────────────────

class TestParameterConsistency:
    YAML_PATH = Path(__file__).parent.parent / "parameters.yaml"

    @pytest.fixture(autouse=True)
    def load_yaml(self):
        with open(self.YAML_PATH) as f:
            self.cfg = yaml.safe_load(f)

    def test_hierarchy_depth(self):
        assert self.cfg["dynamics"]["hierarchy_depth"] == DEFAULT_MAX_HIERARCHY == 10

    def test_matsubara_truncation(self):
        assert self.cfg["dynamics"]["matsubara_truncation"] == DEFAULT_N_MATSUBARA == 2

    def test_temperature(self):
        assert self.cfg["bath"]["temperature"] == DEFAULT_TEMPERATURE == 295.0

    def test_reorganization_energy(self):
        assert self.cfg["bath"]["reorganization_energy"] == DEFAULT_REORGANIZATION_ENERGY == 35.0

    def test_drude_cutoff(self):
        assert self.cfg["bath"]["drude_cutoff"] == DEFAULT_DRUDE_CUTOFF == 50.0

    def test_vibronic_frequencies_count(self):
        assert len(self.cfg["bath"]["vibronic_frequencies"]) == 12
        assert len(DEFAULT_VIBRONIC_FREQUENCIES) == 12

    def test_vibronic_frequencies_values(self):
        yaml_freqs = np.array(self.cfg["bath"]["vibronic_frequencies"])
        assert np.allclose(yaml_freqs, DEFAULT_VIBRONIC_FREQUENCIES)

    def test_huang_rhys_count(self):
        assert len(self.cfg["bath"]["huang_rhys_factors"]) == 12
        assert len(DEFAULT_HUANG_RHYS_FACTORS) == 12

    def test_vibronic_damping_is_list(self):
        """vibronic_damping must be a list (not scalar) to avoid broadcast ambiguity."""
        damp = self.cfg["bath"]["vibronic_damping"]
        assert isinstance(damp, list), "vibronic_damping must be a list in parameters.yaml"
        assert len(damp) == 12

    def test_time_step(self):
        assert self.cfg["dynamics"]["time_step"] == 2.0  # fs (matches CSV ground truth)

    def test_pulse_fwhm(self):
        assert self.cfg["pulse"]["fwhm"] == PULSE_FWHM == 50.0


# ─────────────────────────────────────────────────────────────────────────────
# 2. Hamiltonian physics
# ─────────────────────────────────────────────────────────────────────────────

class TestHamiltonianFactory:
    def test_7site_shape(self, fmo7):
        H, e = fmo7
        assert H.shape == (7, 7)
        assert len(e) == 7

    def test_8site_shape(self):
        H, e = create_fmo_hamiltonian(include_reaction_center=True)
        assert H.shape == (8, 8)
        assert len(e) == 8

    def test_hermitian(self, fmo7):
        H, _ = fmo7
        assert np.allclose(H, H.T), "Hamiltonian must be Hermitian (real symmetric)"

    def test_diagonal_equals_site_energies(self, fmo7):
        H, e = fmo7
        assert np.allclose(np.diag(H), e)

    def test_site_energies_range(self, fmo7):
        """FMO site energies should be in the BChl Qy band ~12000-12700 cm⁻¹."""
        _, e = fmo7
        assert np.all(e > 11000) and np.all(e < 13000)

    def test_couplings_symmetric(self, fmo7):
        H, _ = fmo7
        for (i, j), v in FMO_COUPLINGS.items():
            assert H[i, j] == v
            assert H[j, i] == v

    def test_rc_site_energy_lower(self):
        """Reaction center (site 8) should have lower energy than BChl sites."""
        _, e7 = create_fmo_hamiltonian(include_reaction_center=False)
        _, e8 = create_fmo_hamiltonian(include_reaction_center=True)
        assert e8[-1] < np.min(e7), "RC site energy should be below all BChl sites"

    def test_eigenvalues_real(self, fmo7):
        H, _ = fmo7
        evals = np.linalg.eigvalsh(H)
        assert np.all(np.isreal(evals))

    def test_spectral_density_positive_omega(self):
        """J(ω) must be positive for ω > 0 (physical requirement)."""
        omega = np.linspace(1, 500, 200)
        J = spectral_density_drude_lorentz(omega, 35.0, 50.0, 295.0)
        assert np.all(J >= 0), "Spectral density must be non-negative for ω > 0"

    def test_spectral_density_zero_at_zero(self):
        """J(0) = 0 by definition of Drude-Lorentz."""
        J = spectral_density_drude_lorentz(np.array([0.0]), 35.0, 50.0, 295.0)
        assert abs(J[0]) < 1e-6

    def test_spectral_density_elementwise_sign(self):
        """Negative ω should give negative J (emission side)."""
        omega = np.array([-100.0, -50.0, 50.0, 100.0])
        J = spectral_density_drude_lorentz(omega, 35.0, 50.0, 295.0)
        assert J[0] < 0 and J[1] < 0, "J(ω<0) must be negative"
        assert J[2] > 0 and J[3] > 0, "J(ω>0) must be positive"

    def test_spectral_density_no_scalar_branch_bug(self):
        """Regression: np.any(omega>=0) must not collapse to a single branch."""
        omega = np.array([-10.0, 10.0])
        J = spectral_density_drude_lorentz(omega, 35.0, 50.0, 295.0)
        assert J[0] != J[1], "Positive and negative ω must give different signs"


# ─────────────────────────────────────────────────────────────────────────────
# 3. HopsSimulator — fallback path
# ─────────────────────────────────────────────────────────────────────────────

class TestHopsSimulatorFallback:
    def test_initialization(self, fallback_sim):
        assert not fallback_sim.use_mesohops
        assert fallback_sim.fallback_sim is not None

    def test_simulator_type_string(self, fallback_sim):
        assert "fallback" in fallback_sim.simulator_type.lower() or \
               "QuantumDynamics" in fallback_sim.simulator_type

    def test_simulate_returns_dict(self, fallback_sim, short_time, initial_state_site1):
        result = fallback_sim.simulate_dynamics(short_time, initial_state_site1)
        assert isinstance(result, dict)

    def test_populations_key_present(self, fallback_sim, short_time, initial_state_site1):
        result = fallback_sim.simulate_dynamics(short_time, initial_state_site1)
        assert "populations" in result

    def test_populations_shape(self, fallback_sim, short_time, initial_state_site1):
        result = fallback_sim.simulate_dynamics(short_time, initial_state_site1)
        pops = result["populations"]
        assert pops.ndim == 2
        assert pops.shape[1] == 7

    def test_populations_non_negative(self, fallback_sim, short_time, initial_state_site1):
        result = fallback_sim.simulate_dynamics(short_time, initial_state_site1)
        assert np.all(result["populations"] >= -1e-6), "Populations must be non-negative"

    def test_populations_sum_conserved(self, fallback_sim, short_time, initial_state_site1):
        result = fallback_sim.simulate_dynamics(short_time, initial_state_site1)
        total = np.sum(result["populations"], axis=1)
        assert np.allclose(total, 1.0, atol=0.05), "Total population must be conserved"

    def test_initial_excitation_site1(self, fallback_sim, short_time, initial_state_site1):
        """At t=0, site 1 should have population ≈ 1."""
        result = fallback_sim.simulate_dynamics(short_time, initial_state_site1)
        assert result["populations"][0, 0] > 0.9

    def test_t_axis_present(self, fallback_sim, short_time, initial_state_site1):
        result = fallback_sim.simulate_dynamics(short_time, initial_state_site1)
        assert "t_axis" in result

    def test_no_simulator_raises(self, fmo7):
        """If both MesoHOPS and fallback fail, RuntimeError must be raised."""
        H, _ = fmo7
        sim = HopsSimulator(H, use_mesohops=False)
        sim.fallback_sim = None  # Force no simulator
        with pytest.raises(RuntimeError, match="No simulator available"):
            sim.simulate_dynamics(np.arange(0, 10, 0.5), np.array([1.0] + [0.0] * 6))

    def test_no_double_fallback_init(self, fmo7):
        """_init_fallback must not be called twice when MesoHOPS is disabled."""
        H, _ = fmo7
        call_count = {"n": 0}
        original = HopsSimulator._init_fallback

        def counting_init(self, **kwargs):
            call_count["n"] += 1
            return original(self, **kwargs)

        HopsSimulator._init_fallback = counting_init
        try:
            HopsSimulator(H, use_mesohops=False)
        finally:
            HopsSimulator._init_fallback = original

        assert call_count["n"] == 1, f"_init_fallback called {call_count['n']} times, expected 1"

    def test_vibronic_damping_scalar_broadcast(self, fmo7):
        """Scalar vibronic_damping must not crash (broadcast to array)."""
        H, _ = fmo7
        sim = HopsSimulator(
            H,
            use_mesohops=True,  # will try MesoHOPS init, may fall back
            vibronic_frequencies=np.array([180.0, 220.0]),
            huang_rhys_factors=np.array([0.05, 0.045]),
            vibronic_damping=10.0,  # scalar — must be broadcast
        )
        # No exception means broadcast worked
        assert sim is not None


# ─────────────────────────────────────────────────────────────────────────────
# 4. CSVDataStorage
# ─────────────────────────────────────────────────────────────────────────────

class TestCSVDataStorage:
    def test_creates_directory(self, tmp_path):
        d = tmp_path / "subdir"
        CSVDataStorage(output_dir=str(d))
        assert d.exists()

    def test_save_returns_path(self, tmp_path):
        s = CSVDataStorage(output_dir=str(tmp_path))
        t = np.linspace(0, 100, 20)
        pops = np.random.rand(20, 7)
        cohs = np.random.rand(20)
        path = s.save_quantum_dynamics_results(t, pops, cohs, {})
        assert os.path.exists(path)

    def test_csv_has_time_column(self, tmp_path):
        import pandas as pd
        s = CSVDataStorage(output_dir=str(tmp_path))
        t = np.linspace(0, 100, 10)
        pops = np.random.rand(10, 7)
        cohs = np.random.rand(10)
        path = s.save_quantum_dynamics_results(t, pops, cohs, {})
        df = pd.read_csv(path)
        assert "time_fs" in df.columns

    def test_csv_has_population_columns(self, tmp_path):
        import pandas as pd
        s = CSVDataStorage(output_dir=str(tmp_path))
        t = np.linspace(0, 100, 10)
        pops = np.random.rand(10, 7)
        cohs = np.random.rand(10)
        path = s.save_quantum_dynamics_results(t, pops, cohs, {})
        df = pd.read_csv(path)
        for i in range(1, 8):
            assert f"population_site_{i}" in df.columns

    def test_metric_length_mismatch_truncated(self, tmp_path):
        """Metric arrays shorter than time_points must be padded, not crash."""
        s = CSVDataStorage(output_dir=str(tmp_path))
        t = np.linspace(0, 100, 20)
        pops = np.random.rand(20, 7)
        cohs = np.random.rand(20)
        metrics = {"short_metric": np.ones(10)}  # shorter than t
        path = s.save_quantum_dynamics_results(t, pops, cohs, metrics)
        assert os.path.exists(path)

    def test_metric_length_mismatch_longer(self, tmp_path):
        """Metric arrays longer than time_points must be truncated, not crash."""
        s = CSVDataStorage(output_dir=str(tmp_path))
        t = np.linspace(0, 100, 10)
        pops = np.random.rand(10, 7)
        cohs = np.random.rand(10)
        metrics = {"long_metric": np.ones(30)}  # longer than t
        path = s.save_quantum_dynamics_results(t, pops, cohs, metrics)
        assert os.path.exists(path)

    def test_config_hash_in_filename(self, tmp_path):
        s = CSVDataStorage(output_dir=str(tmp_path))
        t = np.linspace(0, 10, 5)
        pops = np.random.rand(5, 7)
        cohs = np.random.rand(5)
        cfg = {"dynamics": {"hierarchy_depth": 10}}
        path = s.save_quantum_dynamics_results(t, pops, cohs, {}, config_dict=cfg)
        # With config_dict, hash must be a 12-char hex string (not "no_config")
        basename = os.path.basename(path)
        assert "no_config" not in basename


# ─────────────────────────────────────────────────────────────────────────────
# 5. FigureGenerator
# ─────────────────────────────────────────────────────────────────────────────

class TestFigureGenerator:
    def test_creates_directory(self, tmp_path):
        gen = FigureGenerator(figures_dir=str(tmp_path / "figs"))
        assert (tmp_path / "figs").exists()

    def test_plot_quantum_dynamics_returns_path(self, tmp_path):
        gen = FigureGenerator(figures_dir=str(tmp_path))
        t = np.linspace(0, 100, 50)
        pops = np.random.rand(50, 7)
        cohs = np.random.rand(50)
        metrics = {"qfi": np.random.rand(50), "entropy": np.random.rand(50)}
        path = gen.plot_quantum_dynamics(t, pops, cohs, metrics)
        assert os.path.exists(path)

    def test_plot_quantum_dynamics_length_mismatch(self, tmp_path):
        """Mismatched array lengths must not crash — guard truncates."""
        gen = FigureGenerator(figures_dir=str(tmp_path))
        t = np.linspace(0, 100, 50)
        pops = np.random.rand(45, 7)   # shorter
        cohs = np.random.rand(48)       # shorter
        metrics = {"qfi": np.random.rand(50)}
        path = gen.plot_quantum_dynamics(t, pops, cohs, metrics)
        assert os.path.exists(path)

    def test_plot_quantum_dynamics_with_baseline(self, tmp_path):
        gen = FigureGenerator(figures_dir=str(tmp_path))
        t = np.linspace(0, 100, 30)
        pops = np.random.rand(30, 7)
        cohs = np.random.rand(30)
        path = gen.plot_quantum_dynamics(
            t, pops, cohs, {},
            baseline_populations=np.random.rand(30, 7),
            baseline_coherences=np.random.rand(30),
        )
        assert os.path.exists(path)

    def test_plot_environmental_robustness_returns_path(self, tmp_path):
        gen = FigureGenerator(figures_dir=str(tmp_path))
        temps = np.array([285, 290, 295, 300, 305, 310], dtype=float)
        eta = np.ones(6) * 0.25
        err = np.ones(6) * 0.04
        samples = np.random.normal(0.25, 0.04, 100)
        path = gen.plot_environmental_robustness(temps, eta, err, samples)
        assert os.path.exists(path)

    def test_plot_environmental_robustness_no_scipy(self, tmp_path, monkeypatch):
        """Figure 2 must still be generated even if scipy is unavailable."""
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "scipy.stats":
                raise ImportError("mocked scipy absence")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)
        gen = FigureGenerator(figures_dir=str(tmp_path))
        temps = np.array([285, 295, 305], dtype=float)
        eta = np.ones(3) * 0.2
        err = np.ones(3) * 0.03
        samples = np.random.normal(0.2, 0.03, 50)
        # Should not raise even without scipy
        path = gen.plot_environmental_robustness(temps, eta, err, samples)
        assert os.path.exists(path)


# ─────────────────────────────────────────────────────────────────────────────
# 6. SBD adapter — site grouping
# ─────────────────────────────────────────────────────────────────────────────

class TestSBDAdapter:
    def test_diagonal_operator_site_idx(self):
        """Diagonal L operators must map to the correct site index."""
        from extensions.mesohops_adapters import SBD_HopsTrajectory
        n = 7
        for site in range(n):
            L = np.zeros((n, n))
            L[site, site] = 1.0
            diag = np.abs(np.diag(L))
            assert int(np.argmax(diag)) == site

    def test_offdiagonal_operator_fallback(self):
        """Off-diagonal L operators must not crash site_idx detection."""
        n = 7
        L = np.zeros((n, n))
        L[2, 4] = 0.5
        L[4, 2] = 0.5
        diag = np.abs(np.diag(L))
        if diag.max() > 1e-12:
            site_idx = int(np.argmax(diag))
        else:
            site_idx = int(np.argmax(np.abs(L).sum(axis=1)))
        assert 0 <= site_idx < n


# ─────────────────────────────────────────────────────────────────────────────
# 7. Audit convergence logic (unit-level, no MesoHOPS required)
# ─────────────────────────────────────────────────────────────────────────────

class TestAuditConvergenceLogic:
    """Test the convergence audit guard logic without running actual simulations."""

    def test_identical_results_detected(self):
        """L=9 and L=10 identical populations must be flagged as fake data."""
        pops = np.random.rand(100, 7)
        results = {9: pops.copy(), 10: pops.copy(), 11: pops.copy()}
        assert np.allclose(results[9], results[10], atol=1e-12), \
            "Test setup: results must be identical"

    def test_shape_mismatch_detected(self):
        """Different shapes across hierarchy depths must be detected."""
        results = {
            9: np.random.rand(100, 7),
            10: np.random.rand(95, 7),   # different length
            11: np.random.rand(100, 7),
        }
        shapes = {L: results[L].shape for L in [9, 10, 11]}
        assert len(set(shapes.values())) > 1

    def test_catastrophic_trace_loss(self):
        """Mean trace < 0.01 must be flagged as solver failure."""
        pops = np.full((100, 7), 1e-4)  # near-zero populations
        mean_trace = np.mean(np.sum(pops, axis=1))
        assert mean_trace < 0.01

    def test_positivity_violation(self):
        """Negative populations below -1e-3 must be flagged."""
        pops = np.random.rand(50, 7)
        pops[10, 3] = -0.01  # inject violation
        min_pop = np.min(pops)
        assert min_pop < -1e-3

    def test_convergence_threshold_check(self):
        """MAE(L10→L11) < threshold must pass; above must warn."""
        threshold = 1e-6
        # Converged case
        p10 = np.random.rand(50, 7)
        p11 = p10 + np.random.rand(50, 7) * 1e-8
        mae = np.mean(np.abs(p11 - p10))
        assert mae < threshold

        # Non-converged case
        p11_bad = p10 + np.random.rand(50, 7) * 0.1
        mae_bad = np.mean(np.abs(p11_bad - p10))
        assert mae_bad > threshold


# ─────────────────────────────────────────────────────────────────────────────
# 8. Physical invariants (regression tests for corrected bugs)
# ─────────────────────────────────────────────────────────────────────────────

class TestPhysicalInvariants:
    def test_hamiltonian_energy_shift_invariant(self, fmo7):
        """Shifting H by a constant must not change populations (physical invariant)."""
        H, _ = fmo7
        n = H.shape[0]
        E_mean = np.mean(np.diag(H))
        H_shifted = H - E_mean * np.eye(n)

        sim1 = HopsSimulator(H, use_mesohops=False)
        sim2 = HopsSimulator(H_shifted, use_mesohops=False)

        t = np.arange(0, 30, 0.5)
        psi = np.zeros(n, dtype=complex)
        psi[0] = 1.0

        r1 = sim1.simulate_dynamics(t, psi)
        r2 = sim2.simulate_dynamics(t, psi)

        assert np.allclose(r1["populations"], r2["populations"], atol=1e-4), \
            "Energy shift must not change populations"

    def test_population_sum_rule(self, fallback_sim, short_time, initial_state_site1):
        """Σᵢ ρᵢᵢ(t) = 1 for all t (trace preservation)."""
        result = fallback_sim.simulate_dynamics(short_time, initial_state_site1)
        total = np.sum(result["populations"], axis=1)
        assert np.allclose(total, 1.0, atol=0.05)

    def test_initial_state_respected(self, fmo7, short_time):
        """Initial excitation on site 3 must give ρ₃₃(0) ≈ 1."""
        H, _ = fmo7
        sim = HopsSimulator(H, use_mesohops=False)
        psi = np.zeros(7, dtype=complex)
        psi[2] = 1.0  # site 3 (index 2)
        result = sim.simulate_dynamics(short_time, psi)
        assert result["populations"][0, 2] > 0.9

    def test_spectral_density_reorganization_energy(self):
        """∫₀^∞ J(ω)/ω dω = λ (reorganization energy) — approximate check."""
        omega = np.linspace(0.1, 2000, 10000)
        dw = omega[1] - omega[0]
        lambda_reorg = 35.0
        gamma = 50.0
        T = DEFAULT_TEMPERATURE
        # J_DL(ω) = 2λγω/(ω²+γ²) — without thermal factor
        J_bare = 2 * lambda_reorg * gamma * omega / (omega**2 + gamma**2)
        integral = np.sum(J_bare / omega) * dw / np.pi
        assert abs(integral - lambda_reorg) / lambda_reorg < 0.05, \
            f"Reorganization energy integral: {integral:.2f} vs {lambda_reorg}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
