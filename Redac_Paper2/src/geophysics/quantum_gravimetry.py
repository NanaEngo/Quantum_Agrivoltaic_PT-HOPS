import numpy as np

from ..config_loader import ConfigModel
from ..logging_config import get_logger

logger = get_logger("gravimetry")

GRAVITY_ACCELERATION_MS2 = 9.80665
QG1_NOISE_FLOOR_NM_S2 = 10.0
QG1_SENSITIVITY_NM_S2_PER_HZ = 500.0
QG1_BASELINE_M = 1.0
QG1_MAX_RANGE_KM = 50.0
EARTH_GRAVITY_GRADIENT_E_PER_M = 3.0e-6
STANDARD_DEVIATION_E = 1.0


class QuantumGravimeter:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.g_measured = GRAVITY_ACCELERATION_MS2
        self.gradient_measured = 0.0
        self.n_samples = 0

    def simulate_groundwater_signal(
        self,
        water_volume_m3: float,
        aquifer_depth_m: float = 50.0,
        soil_porosity: float = 0.35,
    ) -> float:
        bulk_density_water_kg_m3 = 1000.0
        mass_change_kg = water_volume_m3 * bulk_density_water_kg_m3
        effective_depth = aquifer_depth_m * (1.0 - soil_porosity) + aquifer_depth_m * soil_porosity
        delta_g = 2.0 * 6.67430e-11 * mass_change_kg / (effective_depth**2)
        noise = np.random.normal(0.0, QG1_NOISE_FLOOR_NM_S2 * 1e-9)
        self.g_measured = GRAVITY_ACCELERATION_MS2 + delta_g + noise
        self.n_samples += 1
        logger.info(
            "Gravimeter Δg = %.2e m/s² (%.1f μGal) for %.1f m³ at depth %.0f m",
            delta_g,
            delta_g * 1e8,
            water_volume_m3,
            aquifer_depth_m,
        )
        return self.g_measured

    def simulate_gradient_survey(
        self,
        water_volume_m3: float,
        baseline_m: float = QG1_BASELINE_M,
    ) -> float:
        delta_g_upper = self.simulate_groundwater_signal(water_volume_m3, aquifer_depth_m=50.0)
        delta_g_lower = self.simulate_groundwater_signal(
            water_volume_m3, aquifer_depth_m=50.0 + baseline_m
        )
        g_gradient = (delta_g_upper - delta_g_lower) / baseline_m
        noise = np.random.normal(
            0.0, STANDARD_DEVIATION_E * 1e-9 * GRAVITY_ACCELERATION_MS2 / baseline_m
        )
        self.gradient_measured = g_gradient + noise
        logger.info(
            "Gravity gradient G_zz = %.2e 1/s² (%.1f E) for V=%.1f m³, baseline=%.1f m",
            self.gradient_measured,
            self.gradient_measured * 1e9,
            water_volume_m3,
            baseline_m,
        )
        return self.gradient_measured

    def estimate_aquifer_recharge(
        self,
        irrigation_saving_m3: float,
        catchment_area_m2: float = 1e6,
        n_gravimeters: int = 3,
    ) -> dict:
        delta_g_per_gravimeter = []
        for _ in range(n_gravimeters):
            local_variation = irrigation_saving_m3 * np.random.uniform(0.8, 1.2)
            dg = self.simulate_groundwater_signal(local_variation)
            delta_g_per_gravimeter.append(dg)
        mean_dg = float(np.mean(delta_g_per_gravimeter))
        std_dg = float(np.std(delta_g_per_gravimeter))
        logger.info(
            "Aquifer recharge estimate: Δg = %.2e ± %.2e m/s² (%d gravimeters)",
            mean_dg,
            std_dg,
            n_gravimeters,
        )
        return {
            "mean_delta_g_ms2": mean_dg,
            "std_delta_g_ms2": std_dg,
            "n_gravimeters": n_gravimeters,
            "estimated_recharge_m3": irrigation_saving_m3,
            "detectable": abs(mean_dg) > (QG1_NOISE_FLOOR_NM_S2 * 1e-9),
            "signal_to_noise": abs(mean_dg) / max(std_dg, 1e-12),
        }

    def get_status(self) -> dict:
        return {
            "g_measured_ms2": self.g_measured,
            "gradient_measured_1_s2": self.gradient_measured,
            "gradient_measured_E": self.gradient_measured * 1e9,
            "n_samples": self.n_samples,
        }
