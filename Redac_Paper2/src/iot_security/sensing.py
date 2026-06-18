from ..config_loader import ConfigModel

# GQD sensor detection constants
# Stern-Volmer quenching constant (ppm-1) for heavy metal (Pb2+) detection
STERM_VOLMER_CONSTANT = 0.05
# CdTe/ZnSe emission peak red-shift sensitivity (nm/ppb) for pesticide detection
PESTICIDE_REDSHIFT_SENSITIVITY = 0.1


class GqdSensorNetwork:
    """
    Simulates the fluorescent response of Graphene Quantum Dots (GQDs)
    and CdTe/ZnSe core-shell quantum dots for soil diagnostics (moisture, nutrients, contaminants).
    """

    def __init__(self, config: ConfigModel):
        self.config = config

    def simulate_telemetry(
        self, soil_moisture_pct: float, heavy_metal_pb_ppm: float, pesticide_ppb: float
    ) -> dict:
        """
        Simulates fluorescent intensity shifts and emission peak displacements (nm).
        Returns a multiplexed sensor dictionary.

        Input validation:
        - soil_moisture_pct clamped to [0.0, 100.0]
        - heavy_metal_pb_ppm clamped to >= 0.0
        - pesticide_ppb clamped to >= 0.0
        """
        # Clamp inputs to physically valid ranges
        soil_moisture_pct = max(0.0, min(soil_moisture_pct, 100.0))
        heavy_metal_pb_ppm = max(heavy_metal_pb_ppm, 0.0)
        pesticide_ppb = max(pesticide_ppb, 0.0)

        # Baseline fluorescence emission peak for GQDs (typically around 450 nm, blue)
        # and CdTe/ZnSe (typically around 620 nm, red)

        # 1. Soil moisture increases fluorescence intensity of hydrophilic GQDs
        gqd_intensity = 1.2 * soil_moisture_pct

        # 2. Heavy metals (Pb2+) quench GQD fluorescence (Stern-Volmer quenching)
        gqd_quenched_intensity = gqd_intensity / (1.0 + STERM_VOLMER_CONSTANT * heavy_metal_pb_ppm)

        # 3. Pesticides cause a red-shift in CdTe/ZnSe emission peaks due to surface ligand exchange
        red_shift_nm = PESTICIDE_REDSHIFT_SENSITIVITY * pesticide_ppb
        sensor_peak_nm = 620.0 + red_shift_nm

        return {
            "gqd_fluorescence_intensity": float(max(gqd_quenched_intensity, 0.0)),
            "core_shell_peak_wavelength_nm": float(sensor_peak_nm),
            "soil_moisture_status": "dry" if soil_moisture_pct < 20.0 else "optimum",
        }


class WaterStressClassifier:
    """
    A machine learning inspired classifier analyzing multi-spectral GQD sensor signals
    to trigger automated irrigation adjustments.
    """

    def __init__(self):
        pass

    def predict_stress_level(self, telemetry: dict) -> str:
        """
        Classifies water stress level based on GQD fluorescence intensity and status.
        Returns: 'NO_STRESS', 'MODERATE_STRESS', or 'SEVERE_STRESS'
        """
        intensity = telemetry["gqd_fluorescence_intensity"]
        status = telemetry["soil_moisture_status"]

        if status == "dry":
            if intensity < 10.0:
                return "SEVERE_STRESS"
            return "MODERATE_STRESS"

        if intensity > 40.0:
            return "NO_STRESS"

        return "MODERATE_STRESS"

    def get_irrigation_valve_command(self, stress_level: str) -> float:
        """
        Returns the required valve flow rate adjustment (liters/hour).
        """
        if stress_level == "SEVERE_STRESS":
            return 15.0
        elif stress_level == "MODERATE_STRESS":
            return 5.0
        return 0.0
