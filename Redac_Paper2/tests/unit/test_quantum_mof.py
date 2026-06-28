"""Unit tests for QuantumMofAdsorber module."""

from unittest.mock import MagicMock

import pytest

from src.materials.quantum_mof import QuantumMofAdsorber


def _mock_config():
    cfg = MagicMock()
    return cfg


class TestQuantumMofAdsorber:
    def test_initial_state(self):
        mof = QuantumMofAdsorber(_mock_config())
        assert mof.pore_volume_cm3_g == 0.8
        assert mof.surface_area_m2_g == 1500.0
        assert mof._cumulative_adsorbed_mg == 0.0
        assert mof._cumulative_released_cqd_mg == 0.0

    def test_langmuir_uptake_zero_pb(self):
        mof = QuantumMofAdsorber(_mock_config())
        total = mof.langmuir_uptake(pb_concentration_ppm=0.0, mass_g=100.0)
        assert total == pytest.approx(0.0, abs=1e-9)
        assert mof._cumulative_adsorbed_mg == 0.0

    def test_langmuir_uptake_finite(self):
        mof = QuantumMofAdsorber(_mock_config())
        total = mof.langmuir_uptake(pb_concentration_ppm=0.05, mass_g=500.0)
        assert total > 0.0
        assert mof._cumulative_adsorbed_mg > 0.0

    def test_langmuir_saturation(self):
        mof = QuantumMofAdsorber(_mock_config())
        total_low = mof.langmuir_uptake(pb_concentration_ppm=0.01, mass_g=1.0)
        total_high = mof.langmuir_uptake(pb_concentration_ppm=100.0, mass_g=1.0)
        assert total_high > total_low
        assert total_high <= 300.0

    def test_cqd_release_zero_days(self):
        mof = QuantumMofAdsorber(_mock_config())
        released = mof.release_cqd(days=0.0)
        assert released == pytest.approx(0.0, abs=1e-6)

    def test_cqd_release_saturates(self):
        mof = QuantumMofAdsorber(_mock_config())
        r1 = mof.release_cqd(days=1.0)
        r30 = mof.release_cqd(days=30.0)
        assert 0.0 < r1 < 50.0
        assert 0.0 < r30 < 50.0
        assert mof._cumulative_released_cqd_mg > 0.0

    def test_breakthrough_infinite_flow(self):
        mof = QuantumMofAdsorber(_mock_config())
        bt = mof.breakthrough_time(flow_rate_m3_day=0.0, mass_g=500.0)
        assert bt == float("inf")

    def test_breakthrough_finite(self):
        mof = QuantumMofAdsorber(_mock_config())
        bt = mof.breakthrough_time(flow_rate_m3_day=0.5, mass_g=500.0)
        assert bt > 100.0

    def test_reset(self):
        mof = QuantumMofAdsorber(_mock_config())
        mof.langmuir_uptake(pb_concentration_ppm=1.0, mass_g=10.0)
        mof.release_cqd(days=10.0)
        assert mof._cumulative_adsorbed_mg > 0.0
        assert mof._cumulative_released_cqd_mg > 0.0
        mof.reset()
        assert mof._cumulative_adsorbed_mg == 0.0
        assert mof._cumulative_released_cqd_mg == 0.0

    def test_get_cumulative_stats(self):
        mof = QuantumMofAdsorber(_mock_config())
        mof.langmuir_uptake(pb_concentration_ppm=0.05, mass_g=100.0)
        mof.release_cqd(days=30.0)
        stats = mof.get_cumulative_stats()
        assert "total_pb_adsorbed_mg" in stats
        assert "total_cqd_released_mg" in stats
        assert stats["total_pb_adsorbed_mg"] > 0.0
        assert stats["total_cqd_released_mg"] > 0.0
