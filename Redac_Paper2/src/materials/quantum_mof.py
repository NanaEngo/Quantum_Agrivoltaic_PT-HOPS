import numpy as np

from ..config_loader import ConfigModel
from ..logging_config import get_logger

logger = get_logger("quantum_mof")

MOF_DEFAULT_PORE_VOLUME_CM3_G = 0.8
MOF_DEFAULT_SURFACE_AREA_M2_G = 1500.0
MOF_PBS_ADSORPTION_CAPACITY_MG_G = 300.0
MOF_CQD_LOADING_MG_G = 50.0
MOF_LANGMUIR_B_EV = 0.12


class QuantumMofAdsorber:
    """
    Quantum Metal-Organic Framework (MOF) model for adsorptive removal of
    heavy metals and controlled release of CQD quantum dots.

    Uses a Langmuir isotherm for Pb²⁺ adsorption and a first-order kinetic
    release model for CQD payload delivery. The MOF acts both as a filtration
    membrane (Axe 11 — contaminant scrubbing) and as a precision
    agrochemical carrier (Axe 15 — quantum fertiliser).
    """

    def __init__(self, config: ConfigModel):
        self.config = config
        self.pore_volume_cm3_g = MOF_DEFAULT_PORE_VOLUME_CM3_G
        self.surface_area_m2_g = MOF_DEFAULT_SURFACE_AREA_M2_G
        self.pb_adsorption_capacity_mg_g = MOF_PBS_ADSORPTION_CAPACITY_MG_G
        self.cqd_loading_mg_g = MOF_CQD_LOADING_MG_G
        self.langmuir_b_ev = MOF_LANGMUIR_B_EV
        self._cumulative_adsorbed_mg = 0.0
        self._cumulative_released_cqd_mg = 0.0

    def langmuir_uptake(self, pb_concentration_ppm: float, mass_g: float) -> float:
        b_ppm = self.langmuir_b_ev / 0.02585
        uptake_mg_g = self.pb_adsorption_capacity_mg_g * (
            b_ppm * pb_concentration_ppm / (1.0 + b_ppm * pb_concentration_ppm)
        )
        total_mg = uptake_mg_g * mass_g
        self._cumulative_adsorbed_mg += total_mg
        logger.debug(
            "MOF Langmuir: [Pb²⁺]=%.1f ppm, mass=%.2f g → uptake=%.2f mg/g, total=%.2f mg",
            pb_concentration_ppm,
            mass_g,
            uptake_mg_g,
            total_mg,
        )
        return float(total_mg)

    def release_cqd(self, days: float, decay_constant: float = 0.02) -> float:
        released_mg = self.cqd_loading_mg_g * (1.0 - np.exp(-decay_constant * days))
        self._cumulative_released_cqd_mg += released_mg
        logger.info(
            "MOF CQD release: day=%.0f, released=%.2f mg/g, cumulative=%.2f mg",
            days,
            released_mg,
            self._cumulative_released_cqd_mg,
        )
        return float(released_mg)

    def breakthrough_time(self, flow_rate_m3_day: float, mass_g: float) -> float:
        max_pb_removed_g = self.pb_adsorption_capacity_mg_g * mass_g / 1000.0
        influent_pb_mg_l = 0.05
        removal_rate_g_day = influent_pb_mg_l * flow_rate_m3_day * 1000.0 / 1e6
        if removal_rate_g_day <= 0.0:
            return float("inf")
        bt_days = max_pb_removed_g / removal_rate_g_day
        logger.info(
            "MOF breakthrough: mass=%.0f g, capacity=%.1f g Pb²⁺, flow=%.3f m³/day → %.0f days",
            mass_g,
            max_pb_removed_g,
            flow_rate_m3_day,
            bt_days,
        )
        return float(bt_days)

    def get_cumulative_stats(self) -> dict:
        return {
            "total_pb_adsorbed_mg": float(self._cumulative_adsorbed_mg),
            "total_cqd_released_mg": float(self._cumulative_released_cqd_mg),
        }

    def reset(self):
        self._cumulative_adsorbed_mg = 0.0
        self._cumulative_released_cqd_mg = 0.0
