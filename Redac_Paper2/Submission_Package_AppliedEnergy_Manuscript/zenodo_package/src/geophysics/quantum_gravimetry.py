import numpy as np

from ..config_loader import ConfigModel
from ..logging_config import get_logger

logger = get_logger("gravimetry")

GRAVITY_ACCELERATION_MS2 = 9.80665
WATER_DENSITY_KG_M3 = 1000.0
GRAVITATIONAL_CONSTANT = 6.67430e-11
QG1_NOISE_FLOOR_NM_S2 = 10.0
QG1_SENSITIVITY_NM_S2_PER_HZ = 500.0
QG1_BASELINE_M = 1.0
QG1_MAX_RANGE_KM = 50.0
EARTH_GRAVITY_GRADIENT_E_PER_M = 3.0e-6
STANDARD_DEVIATION_E = 1.0
# Recharge footprint of the 500 m2 greenhouse module quoted in the SM.
DEFAULT_CATCHMENT_AREA_M2 = 500.0


def bouguer_delta_g_ms2(
    water_volume_m3: float,
    catchment_area_m2: float = DEFAULT_CATCHMENT_AREA_M2,
    height_above_source_m: float = 0.0,
) -> float:
    """Single Delta-g law for the whole module (finite circular water source).

    A recharge volume V spread over a footprint A is a disk of radius
    R = sqrt(A/pi) with areal mass density sigma = rho*V/A.  Sensing at
    height z above its plane gives

        Delta g(z) = 2*pi*G*sigma * [1 - z / sqrt(z^2 + R^2)].

    At z = 0 this is the Bouguer plate 2*pi*G*rho*V/A quoted in the SM:
    230 m3/yr over the 500 m2 footprint -> ~0.19 um/s2 (detectable), the
    same volume over a 3 ha recharge zone -> ~3.2 nm/s2 (below the
    10 nm/s2 single-instrument floor).  Everything else in this module
    (point-monitoring signal, vertical gradient, recharge estimate) uses
    this one law; the gradient is its z > 0 finite-extent correction.
    """
    area_m2 = max(float(catchment_area_m2), 1e-9)
    sigma_kg_m2 = float(water_volume_m3) * WATER_DENSITY_KG_M3 / area_m2
    z = max(float(height_above_source_m), 0.0)
    radius_m = float(np.sqrt(area_m2 / np.pi))
    attenuation = 1.0 - z / float(np.hypot(z, radius_m))
    return 2.0 * np.pi * GRAVITATIONAL_CONSTANT * sigma_kg_m2 * attenuation


class QuantumGravimeter:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.g_measured = GRAVITY_ACCELERATION_MS2
        self.gradient_measured = 0.0
        self.n_samples = 0

    def simulate_groundwater_signal(
        self,
        water_volume_m3: float,
        catchment_area_m2: float = DEFAULT_CATCHMENT_AREA_M2,
        surface_offset_m: float = 0.0,
    ) -> float:
        delta_g = bouguer_delta_g_ms2(water_volume_m3, catchment_area_m2, surface_offset_m)
        noise = np.random.normal(0.0, QG1_NOISE_FLOOR_NM_S2 * 1e-9)
        self.g_measured = GRAVITY_ACCELERATION_MS2 + delta_g + noise
        self.n_samples += 1
        logger.info(
            "Gravimeter Δg = %.2e m/s² (%.1f μGal) for %.1f m³ over %.0f m²",
            delta_g,
            delta_g * 1e8,
            water_volume_m3,
            catchment_area_m2,
        )
        return self.g_measured

    def simulate_gradient_survey(
        self,
        water_volume_m3: float,
        baseline_m: float = QG1_BASELINE_M,
        catchment_area_m2: float = DEFAULT_CATCHMENT_AREA_M2,
    ) -> float:
        dg_upper = bouguer_delta_g_ms2(water_volume_m3, catchment_area_m2, 0.0)
        dg_lower = bouguer_delta_g_ms2(water_volume_m3, catchment_area_m2, baseline_m)
        g_gradient = (dg_upper - dg_lower) / max(float(baseline_m), 1e-9)
        noise = np.random.normal(
            0.0,
            STANDARD_DEVIATION_E * 1e-9 * GRAVITY_ACCELERATION_MS2 / max(float(baseline_m), 1e-9),
        )
        self.gradient_measured = g_gradient + noise
        self.n_samples += 1
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
        """Annual recharge volume -> Bouguer plate anomaly over the footprint.

        Uses :func:`bouguer_delta_g_ms2` (the single module law) with
        ``irrigation_saving_m3`` an ANNUAL volume (m3/yr) and
        ``catchment_area_m2`` the recharge footprint.  Each gravimeter
        returns the anomaly plus the QG1 10 nm/s2 noise floor.
        """
        delta_g_per_gravimeter = []
        for _ in range(n_gravimeters):
            local_variation = irrigation_saving_m3 * np.random.uniform(0.8, 1.2)
            delta_g = bouguer_delta_g_ms2(local_variation, catchment_area_m2, 0.0)
            noise = np.random.normal(0.0, QG1_NOISE_FLOOR_NM_S2 * 1e-9)
            delta_g_per_gravimeter.append(delta_g + noise)
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
