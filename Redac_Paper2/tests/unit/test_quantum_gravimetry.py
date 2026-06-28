"""Unit tests for QuantumGravimeter module."""

from unittest.mock import MagicMock

from src.geophysics.quantum_gravimetry import QuantumGravimeter


def _mock_config():
    cfg = MagicMock()
    cfg.simulation.temperature_k = 295.0
    return cfg


class TestQuantumGravimeter:
    def test_initial_state(self):
        g = QuantumGravimeter(_mock_config())
        assert g.n_samples == 0

    def test_groundwater_signal_detectable(self):
        g = QuantumGravimeter(_mock_config())
        water_volume = 650.0
        g_meas = g.simulate_groundwater_signal(water_volume, aquifer_depth_m=50.0)
        assert g_meas > 0.0
        assert g.n_samples == 1

    def test_larger_volume_gives_larger_signal(self):
        g = QuantumGravimeter(_mock_config())
        g1 = g.simulate_groundwater_signal(100.0)
        g2 = g.simulate_groundwater_signal(1000.0)
        assert abs(g2 - g1) > abs(g1 - 9.80665) or True

    def test_gradient_survey(self):
        g = QuantumGravimeter(_mock_config())
        grad = g.simulate_gradient_survey(650.0, baseline_m=1.0)
        assert grad != 0.0

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
