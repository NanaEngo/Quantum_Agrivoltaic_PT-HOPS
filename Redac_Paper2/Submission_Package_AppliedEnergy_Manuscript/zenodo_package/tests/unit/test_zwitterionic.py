"""Unit tests for ZwitterionicCoating module."""

from unittest.mock import MagicMock

from src.materials.zwitterionic_coating import (
    COATING_CRITICAL_THICKNESS_NM,
    COATING_INITIAL_THICKNESS_NM,
    ZwitterionicCoating,
)


def _mock_config():
    cfg = MagicMock()
    cfg.simulation.temperature_k = 295.0
    cfg.physics.soiling_decay_rate_per_day = 0.005
    return cfg


class TestZwitterionicCoating:
    def test_initial_thickness(self):
        coating = ZwitterionicCoating(_mock_config())
        assert coating.thickness_nm == COATING_INITIAL_THICKNESS_NM
        assert coating.is_intact
        assert coating.application_count == 1

    def test_degradation_over_time(self):
        coating = ZwitterionicCoating(_mock_config())
        coating.degrade(10.0)
        expected = COATING_INITIAL_THICKNESS_NM - 10.0 * 0.3
        assert abs(coating.thickness_nm - expected) < 1e-6

    def test_coating_failure_at_critical_thickness(self):
        coating = ZwitterionicCoating(_mock_config())
        days_to_fail = (COATING_INITIAL_THICKNESS_NM - COATING_CRITICAL_THICKNESS_NM) / 0.3
        coating.degrade(days_to_fail + 1)
        assert not coating.is_intact

    def test_coherence_retention_at_full_thickness(self):
        coating = ZwitterionicCoating(_mock_config())
        assert coating.coherence_retention == 0.90

    def test_coherence_retention_at_zero_thickness(self):
        coating = ZwitterionicCoating(_mock_config())
        coating.thickness_nm = 0.0
        assert coating.coherence_retention == 0.0

    def test_remaining_lifetime(self):
        coating = ZwitterionicCoating(_mock_config())
        expected_days = COATING_INITIAL_THICKNESS_NM / 0.3
        assert abs(coating.remaining_lifetime_days - expected_days) < 1e-6

    def test_sensor_correction_factor_intact(self):
        coating = ZwitterionicCoating(_mock_config())
        corrected = coating.get_sensor_correction_factor(0.012)
        assert corrected < 0.012

    def test_sensor_correction_factor_degraded(self):
        coating = ZwitterionicCoating(_mock_config())
        coating.thickness_nm = 0.0
        corrected = coating.get_sensor_correction_factor(0.012)
        assert corrected == 0.012

    def test_reapplication_on_degradation(self):
        coating = ZwitterionicCoating(_mock_config())
        coating.degrade(100.0)
        assert not coating.is_intact
        coating._apply()
        assert coating.is_intact
        assert coating.application_count == 2

    def test_annual_cycle(self):
        coating = ZwitterionicCoating(_mock_config())
        result = coating.simulate_annual_cycle()
        assert result["annual_reapplications"] >= 6
        assert result["annual_opex_usd"] >= 120.0
