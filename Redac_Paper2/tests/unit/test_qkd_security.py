import os
from Redac_Paper2.src.config_loader import load_config
from Redac_Paper2.src.iot_security.sensing import (
    GqdSensorNetwork,
    WaterStressClassifier,
)
from Redac_Paper2.src.iot_security.qkd import Bb84Protocol


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
    assert len(res_success["key"]) == config.security.qkd.key_length_bits

    # 2. Test Failure scenario (high noise)
    qkd_fail = Bb84Protocol(config)
    qkd_fail.noise_rate = 0.30
    res_fail = qkd_fail.simulate_key_exchange(seed=101)

    assert res_fail["status"] == "FAILED_HI_NOISE_OR_EAVESDROP"
    assert res_fail["key"] is None
