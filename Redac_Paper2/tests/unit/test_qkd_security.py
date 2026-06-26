import os

import pytest

from src.config_loader import load_config
from src.iot_security.qkd import Bb84Protocol, SecurityThresholdExceeded
from src.iot_security.sensing import (
    DynamicCalibrator,
    GqdSensorNetwork,
    WaterStressClassifier,
)


def test_gqd_sensor_and_classifier():
    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    sensors = GqdSensorNetwork(config)
    # Target: 15% moisture, 10.0 ppm Lead contamination, 5.0 ppb pesticide residues
    telemetry = sensors.simulate_telemetry(15.0, 10.0, 5.0)

    assert "gqd_fluorescence_intensity" in telemetry
    assert telemetry["core_shell_peak_wavelength_nm"] == 620.0 + 0.1 * 5.0
    assert telemetry["soil_moisture_status"] == "dry"

    classifier = WaterStressClassifier()
    stress = classifier.predict_stress_level(telemetry)
    assert stress in ["SEVERE_STRESS", "MODERATE_STRESS"]

    valve = classifier.get_irrigation_valve_command(stress)
    assert valve > 0.0


def test_gqd_sensor_edge_cases():
    """E-10: Bounds validation for sensor inputs."""
    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    sensors = GqdSensorNetwork(config)

    # Test moisture clamping (>100% clamped to 100%)
    telemetry_over = sensors.simulate_telemetry(200.0, 10.0, 5.0)
    assert telemetry_over["gqd_fluorescence_intensity"] >= 0.0

    # Test negative moisture clamped to 0%
    telemetry_neg = sensors.simulate_telemetry(-50.0, 10.0, 5.0)
    assert telemetry_neg["soil_moisture_status"] == "dry"

    # Test negative heavy metals clamped to 0
    telemetry_metal_neg = sensors.simulate_telemetry(50.0, -10.0, 5.0)
    assert telemetry_metal_neg["gqd_fluorescence_intensity"] >= 0.0

    # Test negative pesticides clamped to 0 (no red shift)
    telemetry_pest_neg = sensors.simulate_telemetry(50.0, 10.0, -5.0)
    assert telemetry_pest_neg["core_shell_peak_wavelength_nm"] == 620.0


def test_bb84_qkd_protocol():
    config_path = os.path.join(os.path.dirname(__file__), "../../parameters.yaml")
    config = load_config(config_path)

    # 1. Test Success scenario (low noise)
    qkd_success = Bb84Protocol(config)
    qkd_success.noise_rate = 0.02
    res_success = qkd_success.simulate_key_exchange(seed=101)

    assert res_success["qber"] <= 0.11
    assert res_success["status"] == "SUCCESS"
    assert res_success["channel_type"] == "fiber"  # V5: fiber channel
    assert len(res_success["key"]) == config.security.qkd.key_length_bits

    # 2. Test V5 Fail-safe: high noise MUST raise SecurityThresholdExceeded
    qkd_fail = Bb84Protocol(config)
    qkd_fail.noise_rate = 0.30
    with pytest.raises(SecurityThresholdExceeded) as exc_info:
        qkd_fail.simulate_key_exchange(seed=101)
    assert "Irrigation command relay halted" in str(exc_info.value)
    assert "fiber" in str(exc_info.value)  # channel type in message


def test_dynamic_calibrator():
    """V5: DynamicCalibrator corrects GQD sensor baseline drift via EMA."""
    cal = DynamicCalibrator(ema_alpha=0.1, drift_alarm_threshold=0.20)

    # Feed clean reference readings — no drift expected
    for _ in range(5):
        state = cal.update(1.0)
    assert state["drift_fraction"] == pytest.approx(0.0, abs=1e-6)
    assert not state["alarm"]
    assert state["correction_factor"] == pytest.approx(1.0, abs=1e-4)

    # Feed degraded readings (simulate biofouling: 30% drop)
    for _ in range(30):
        state = cal.update(0.70)
    assert state["drift_fraction"] > 0.20  # drift detected
    assert state["alarm"] is True
    assert "cleaning required" in (state["alarm_message"] or "")

    # apply_correction should bring a reading back toward reference
    corrected = cal.apply_correction(0.70)
    assert corrected > 0.70  # correction amplifies signal

    # Test Stern-Volmer thermal/salinity calibration
    k_sv_cal = cal.get_calibrated_k_sv(temperature_k=308.15, salinity_ms_cm=5.0)
    # Expected: 1.5e5 * (1.0 - 0.0035 * 10 - 0.012 * 5.0) = 1.5e5 * (1.0 - 0.035 - 0.06) = 1.5e5 * 0.905 = 135750.0
    assert k_sv_cal == pytest.approx(135750.0)

    # Floor limit test
    k_sv_floor = cal.get_calibrated_k_sv(temperature_k=400.0, salinity_ms_cm=100.0)
    assert k_sv_floor == 1e4
