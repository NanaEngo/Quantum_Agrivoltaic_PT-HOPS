"""Unit tests for the Agrivoltaic Digital Twin (Axe 1)."""

import numpy as np
import pytest

from src.config_loader import ConfigModel, load_config
from src.digital_twin import DigitalTwin


@pytest.fixture(scope="module")
def dt_config(config_path: str) -> ConfigModel:
    """Load config for Digital Twin tests (module-scoped for speed)."""
    return load_config(config_path)


@pytest.fixture
def dt(dt_config: ConfigModel) -> DigitalTwin:
    """Fresh DigitalTwin instance per test."""
    return DigitalTwin(dt_config)


class TestTick:
    def test_returns_all_keys(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        state = dt.tick(solar_flux=default_solar_flux)
        required = [
            "tick",
            "urgency",
            "phi_ft_global",
            "et_rate_mm_day",
            "water_saved_liters",
            "power_soiled_kwh",
            "neb_co2_kg",
            "anomaly_score",
            "security_gate",
            "calibration_correction",
            "sensor_drift",
            "solar_flux",
            "adj_temp_c",
            "adj_rh_pct",
        ]
        for key in required:
            assert key in state, f"Missing key: {key}"

    def test_tick_increments(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        s1 = dt.tick(solar_flux=default_solar_flux)
        s2 = dt.tick(solar_flux=default_solar_flux)
        assert s1["tick"] == 0
        assert s2["tick"] == 1

    def test_power_soiled_positive(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        state = dt.tick(solar_flux=default_solar_flux)
        assert state["power_soiled_kwh"] > 0.0

    def test_phi_ft_global_in_range(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        state = dt.tick(solar_flux=default_solar_flux)
        assert 0.0 <= state["phi_ft_global"] <= 1.0

    def test_with_dm_array(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        """Tick with a synthetic 9×9 density matrix array."""
        n_sites = 9
        n_steps = 10
        dm_array = np.zeros((n_steps, n_sites, n_sites), dtype=complex)
        for t in range(n_steps):
            dm_array[t, 0, 0] = 0.5
            dm_array[t, 2, 2] = 0.3
            dm_array[t, 3, 3] = 0.2
        state = dt.tick(solar_flux=default_solar_flux, dm_array=dm_array)
        assert state["phi_ft_npom"] > 0.0


class TestUrgency:
    def test_urgency_normal(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        anomaly = {"anomaly_score": 0.5, "predicted_stress": 0.1}
        state = dt.tick(solar_flux=default_solar_flux, anomaly_result=anomaly)
        assert state["urgency"] == "NORMAL"

    def test_urgency_medium(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        anomaly = {"anomaly_score": 1.5, "predicted_stress": 0.4}
        state = dt.tick(solar_flux=default_solar_flux, anomaly_result=anomaly)
        assert state["urgency"] == "MEDIUM"

    def test_urgency_high(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        anomaly = {"anomaly_score": 3.0, "predicted_stress": 0.8}
        state = dt.tick(solar_flux=default_solar_flux, anomaly_result=anomaly)
        assert state["urgency"] == "HIGH"


class TestSecurityGate:
    def test_security_gate_pass_no_qkd(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        state = dt.tick(solar_flux=default_solar_flux)
        assert state["security_gate"] is True

    def test_security_gate_pass_secure(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        qkd = {"status": "SECURE", "qber": 0.03}
        state = dt.tick(solar_flux=default_solar_flux, qkd_status=qkd)
        assert state["security_gate"] is True

    def test_security_gate_block(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        qkd = {"status": "COMPROMISED", "qber": 0.15}
        state = dt.tick(solar_flux=default_solar_flux, qkd_status=qkd)
        assert state["security_gate"] is False


class TestCalibration:
    def test_calibration_no_sensor(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        state = dt.tick(solar_flux=default_solar_flux)
        assert state["calibration_correction"] == 1.0
        assert state["sensor_drift"] == 0.0

    def test_calibration_with_sensor(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        sensor = {"baseline_reading": 0.9, "soil_moisture_status": "optimum"}
        state = dt.tick(solar_flux=default_solar_flux, sensor_telemetry=sensor)
        assert state["calibration_correction"] > 0.0


class TestClimateFusion:
    def test_climate_no_sensor(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        state = dt.tick(solar_flux=default_solar_flux)
        assert state["adj_temp_c"] == 25.0
        assert state["adj_rh_pct"] == 60.0

    def test_climate_dry_soil(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        sensor = {"soil_moisture_status": "dry", "baseline_reading": 1.0}
        state = dt.tick(solar_flux=default_solar_flux, sensor_telemetry=sensor)
        assert state["adj_temp_c"] == 26.5  # +1.5°C
        assert state["adj_rh_pct"] == 55.0  # -5%


class TestOpsLog:
    def test_ops_log_grows(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        dt.tick(solar_flux=default_solar_flux)
        dt.tick(solar_flux=default_solar_flux)
        assert len(dt.get_ops_log()) == 2

    def test_get_state_summary(self, dt: DigitalTwin, default_solar_flux: float) -> None:
        assert dt.get_state_summary() == {}
        dt.tick(solar_flux=default_solar_flux)
        summary = dt.get_state_summary()
        assert "tick" in summary
        assert summary["tick"] == 0
