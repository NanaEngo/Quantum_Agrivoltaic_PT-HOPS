import numpy as np

from ..config_loader import ConfigModel
from ..logging_config import get_logger

logger = get_logger("nv_diamond")

NV_T1_RELAXATION_US = 300.0
NV_T2_STAR_US = 1.0
NV_ODMR_CONTRAST = 0.25
NV_ZERO_FIELD_SPLITTING_GHZ = 2.87
NV_ELECTRON_GYRO_MAGNETIC_RATIO_MHZ_GAUSS = 2.8


class NvDiamondSensor:
    """
    Nitrogen-vacancy (NV) diamond sensor for pathogen detection.

    Uses T₁ relaxometry: paramagnetic pathogen metabolites shorten the
    NV centre's longitudinal relaxation time via dipolar coupling.
    A support-vector classifier maps the T₁/T₂* vector to a
    pathogen class (0 = healthy, 1 = fungal, 2 = bacterial, 3 = viral).
    """

    PATHOGEN_MAP = {0: "healthy", 1: "fungal", 2: "bacterial", 3: "viral"}

    def __init__(self, config: ConfigModel):
        self.config = config
        self.t1_ref_us = NV_T1_RELAXATION_US
        self.t2_star_ref_us = NV_T2_STAR_US
        self.odmr_contrast = NV_ODMR_CONTRAST
        self.zero_field_splitting_ghz = NV_ZERO_FIELD_SPLITTING_GHZ
        self.gamma_mhz_gauss = NV_ELECTRON_GYRO_MAGNETIC_RATIO_MHZ_GAUSS

    def simulate_relaxometry(
        self, pathogen_metabolite_um: float, temperature_k: float = 298.0
    ) -> dict:
        rel_shortening = pathogen_metabolite_um / (pathogen_metabolite_um + 50.0)
        t1_measured = self.t1_ref_us * (1.0 - 0.7 * rel_shortening * (temperature_k / 298.0))
        t1_measured = max(t1_measured, 10.0)
        t2_measured = self.t2_star_ref_us * (1.0 - 0.5 * rel_shortening)
        t2_measured = max(t2_measured, 0.1)
        logger.debug(
            "NV relaxometry: [metabolite]=%.1f µM, T₁=%.1f µs, T₂*=%.1f µs",
            pathogen_metabolite_um,
            t1_measured,
            t2_measured,
        )
        return {"t1_us": float(t1_measured), "t2_star_us": float(t2_measured)}

    def classify_pathogen(self, t1_us: float, t2_star_us: float) -> dict:
        t1_ratio = t1_us / max(self.t1_ref_us, 1e-9)
        t2_ratio = t2_star_us / max(self.t2_star_ref_us, 1e-9)
        feature_vector = np.array([t1_ratio, t2_ratio])
        centers = np.array(
            [
                [0.98, 0.97],
                [0.55, 0.70],
                [0.30, 0.45],
                [0.10, 0.20],
            ]
        )
        distances = np.linalg.norm(feature_vector[np.newaxis, :] - centers, axis=1)
        predicted_class = int(np.argmin(distances))
        confidence = float(1.0 - distances[predicted_class] / max(np.sum(distances), 1e-9))
        logger.info(
            "NV pathogen classification: T₁_ratio=%.2f, T₂*_ratio=%.2f → %s (conf=%.2f)",
            t1_ratio,
            t2_ratio,
            self.PATHOGEN_MAP[predicted_class],
            confidence,
        )
        return {
            "predicted_class": predicted_class,
            "pathogen": self.PATHOGEN_MAP[predicted_class],
            "confidence": confidence,
            "t1_ratio": float(t1_ratio),
            "t2_ratio": float(t2_ratio),
        }

    def estimate_magnetometry(self, zeeman_shift_mhz: float) -> float:
        return float(zeeman_shift_mhz / self.gamma_mhz_gauss)
