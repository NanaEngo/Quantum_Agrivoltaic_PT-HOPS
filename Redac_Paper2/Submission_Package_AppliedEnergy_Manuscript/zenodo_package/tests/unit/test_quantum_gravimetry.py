"""Unit tests for QuantumGravimeter module."""

from unittest.mock import MagicMock

from src.geophysics.quantum_gravimetry import (
    GRAVITY_ACCELERATION_MS2,
    QuantumGravimeter,
    bouguer_delta_g_ms2,
)


def _mock_config():
    cfg = MagicMock()
    cfg.simulation.temperature_k = 295.0
    return cfg


class TestBouguerLaw:
    def test_single_law_matches_sm_footprint(self):
        # SM: 230 m3/yr over the 500 m2 footprint -> ~0.2 um/s2
        dg_footprint = bouguer_delta_g_ms2(230.0, 500.0)
        assert 1.5e-7 < dg_footprint < 2.5e-7

    def test_single_law_matches_sm_3ha(self):
        # SM: same volume over a 3 ha recharge zone -> ~3.2 nm/s2
        dg_3ha = bouguer_delta_g_ms2(230.0, 30000.0)
        assert 2.5e-9 < dg_3ha < 4.0e-9

    def test_law_is_monotonic_in_volume(self):
        assert bouguer_delta_g_ms2(1000.0, 500.0) > bouguer_delta_g_ms2(100.0, 500.0)


class TestQuantumGravimeter:
    def test_initial_state(self):
        g = QuantumGravimeter(_mock_config())
        assert g.n_samples == 0

    def test_groundwater_signal_detectable(self):
        g = QuantumGravimeter(_mock_config())
        g_meas = g.simulate_groundwater_signal(650.0, catchment_area_m2=500.0)
        assert g_meas > GRAVITY_ACCELERATION_MS2
        assert g.n_samples == 1

    def test_larger_volume_gives_larger_signal(self):
        g = QuantumGravimeter(_mock_config())
        g1 = g.simulate_groundwater_signal(100.0)
        g2 = g.simulate_groundwater_signal(1000.0)
        assert g2 > g1

    def test_gradient_survey(self):
        g = QuantumGravimeter(_mock_config())
        grad = g.simulate_gradient_survey(650.0, baseline_m=1.0)
        assert grad > 0.0

    def test_aquifer_recharge_estimate(self):
        g = QuantumGravimeter(_mock_config())
        result = g.estimate_aquifer_recharge(650.0, n_gravimeters=3)
        assert result["n_gravimeters"] == 3
        assert "detectable" in result
        assert result["estimated_recharge_m3"] == 650.0

    def test_get_status(self):
        g = QuantumGravimeter(_mock_config())
        status = g.get_status()
        assert "g_measured_ms2" in status
        assert "n_samples" in status
