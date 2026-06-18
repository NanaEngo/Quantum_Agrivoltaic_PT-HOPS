import numpy as np
from ..config_loader import ConfigModel

# FAO-56 Penman-Monteith physical constants
# Saturation vapor pressure coefficient (kPa) at 0°C (Magnus formula)
SAT_VAPOR_COEFF = 0.6108
# Psychrometric constant (kPa/°C) at standard atmospheric pressure
PSYCHROMETRIC_CONSTANT = 0.066
# Slope of saturation vapor pressure curve numerator
VAPOR_SLOPE_NUM = 4098.0
# Temperature conversion offset for vapor pressure calculation (Celsius to Kelvin)
VAPOR_TEMP_OFFSET = 237.3


class GreenhouseEvapotranspiration:
    """
    Implements the FAO-56 Penman-Monteith crop evapotranspiration model (ET_c)
    parameterized for shaded greenhouse environments under spectrally selective OPV filters.
    """

    def __init__(self, config: ConfigModel):
        self.config = config
        self.shading_factor = config.microclimate.greenhouse.shading_factor
        self.crop_coef = config.microclimate.greenhouse.crop_coefficient

    def calculate_evapotranspiration(
        self,
        solar_flux_w_m2: float,
        temp_c: float,
        relative_humidity_pct: float,
        wind_speed_m_s: float,
    ) -> float:
        """
        Calculates ET_c (mm/day) under greenhouse conditions with selective shading.
        Formula based on FAO-56 Penman-Monteith equation simplified for greenhouse:
        Rn (net radiation) is attenuated by the OPV shading factor.

        Edge case guards:
        - temp_c <= -273.15 causes division by zero in VPD calculation -> returns 0.0
        - Non-physical relative humidity (>100%) is clamped down.
        """
        # Guard: absolute zero — no vapor pressure possible, ET = 0
        if temp_c <= -273.15:
            return 0.0

        # Guard: clamp humidity to physical range
        relative_humidity_pct = max(0.0, min(relative_humidity_pct, 100.0))

        # 1. Net radiation (Rn) calculation. Convert solar flux (W/m2) to MJ/m2/day
        solar_mj = solar_flux_w_m2 * 0.0864
        # Apply selective OPV shading
        net_radiation = solar_mj * (1.0 - self.shading_factor)

        # 2. Vapor pressure deficit (VPD)
        e_s = SAT_VAPOR_COEFF * np.exp((17.27 * temp_c) / (temp_c + VAPOR_TEMP_OFFSET))  # kPa
        e_a = e_s * (relative_humidity_pct / 100.0)
        vpd = e_s - e_a

        # 3. Psychrometric constant (gamma) and slope of vapor pressure curve (Delta)
        gamma = PSYCHROMETRIC_CONSTANT  # kPa/°C
        delta = (VAPOR_SLOPE_NUM * e_s) / ((temp_c + VAPOR_TEMP_OFFSET) ** 2)

        # 4. FAO-56 Penman-Monteith Equation adapted for greenhouse conditions
        # (Reduced aerodynamic term due to greenhouse barrier, wind speed is attenuated)
        wind_term = 0.1 * wind_speed_m_s
        numerator = (
            0.408 * delta * net_radiation
            + gamma * (900.0 / (temp_c + 273.0)) * wind_term * vpd
        )
        denominator = delta + gamma * (1.0 + 0.34 * wind_term)

        et_reference = numerator / denominator
        et_crop = et_reference * self.crop_coef

        return float(max(et_crop, 0.0))
