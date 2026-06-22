from ..config_loader import ConfigModel
from ..constants import (
    GQD_CORE_SHELL_BASELINE_NM,
    GQD_MOISTURE_SENSITIVITY,
    GQD_PESTICIDE_REDSHIFT_SENSITIVITY,
    GQD_STERN_VOLMER_CONSTANT,
    IRRIGATION_MODERATE_VALVE,
    IRRIGATION_SEVERE_VALVE,
    SOIL_MOISTURE_DRY_THRESHOLD,
    STRESS_NONE_THRESHOLD,
    STRESS_SEVERE_THRESHOLD,
)


class GqdSensorNetwork:
    def __init__(self, config: ConfigModel):
        self.config = config

    def simulate_telemetry(
        self, soil_moisture_pct: float, heavy_metal_pb_ppm: float, pesticide_ppb: float
    ) -> dict:
        soil_moisture_pct = max(0.0, min(soil_moisture_pct, 100.0))
        heavy_metal_pb_ppm = max(heavy_metal_pb_ppm, 0.0)
        pesticide_ppb = max(pesticide_ppb, 0.0)

        gqd_intensity = GQD_MOISTURE_SENSITIVITY * soil_moisture_pct
        gqd_quenched_intensity = gqd_intensity / (
            1.0 + GQD_STERN_VOLMER_CONSTANT * heavy_metal_pb_ppm
        )
        red_shift_nm = GQD_PESTICIDE_REDSHIFT_SENSITIVITY * pesticide_ppb

        return {
            "gqd_fluorescence_intensity": float(max(gqd_quenched_intensity, 0.0)),
            "core_shell_peak_wavelength_nm": float(GQD_CORE_SHELL_BASELINE_NM + red_shift_nm),
            "soil_moisture_status": "dry"
            if soil_moisture_pct < SOIL_MOISTURE_DRY_THRESHOLD
            else "optimum",
        }


class WaterStressClassifier:
    def __init__(self):
        pass

    def predict_stress_level(self, telemetry: dict) -> str:
        intensity = telemetry["gqd_fluorescence_intensity"]
        status = telemetry["soil_moisture_status"]
        if status == "dry":
            return "SEVERE_STRESS" if intensity < STRESS_SEVERE_THRESHOLD else "MODERATE_STRESS"
        return "NO_STRESS" if intensity > STRESS_NONE_THRESHOLD else "MODERATE_STRESS"

    def get_irrigation_valve_command(self, stress_level: str) -> float:
        if stress_level == "SEVERE_STRESS":
            return IRRIGATION_SEVERE_VALVE
        elif stress_level == "MODERATE_STRESS":
            return IRRIGATION_MODERATE_VALVE
        return 0.0
