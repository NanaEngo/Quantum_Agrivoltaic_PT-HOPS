import numpy as np

from ..config_loader import ConfigModel
from ..constants import (
    FAO56_ABSOLUTE_ZERO_C,
    FAO56_PSYCHROMETRIC_CONSTANT,
    FAO56_RADIATION_FACTOR,
    FAO56_SAT_VAPOR_COEFF,
    FAO56_TEMP_NUMERATOR,
    FAO56_VAPOR_SLOPE_EMP,
    FAO56_VAPOR_SLOPE_NUM,
    FAO56_VAPOR_TEMP_OFFSET,
    FAO56_W_TO_MJ_CONVERSION,
    FAO56_WIND_COEFF,
    FAO56_WIND_TERM_COEFF,
)


class GreenhouseEvapotranspiration:
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
        if temp_c <= FAO56_ABSOLUTE_ZERO_C:
            return 0.0

        relative_humidity_pct = max(0.0, min(relative_humidity_pct, 100.0))

        solar_mj = solar_flux_w_m2 * FAO56_W_TO_MJ_CONVERSION
        net_radiation = solar_mj * (1.0 - self.shading_factor)

        e_s = FAO56_SAT_VAPOR_COEFF * np.exp(
            (FAO56_VAPOR_SLOPE_EMP * temp_c) / (temp_c + FAO56_VAPOR_TEMP_OFFSET)
        )
        e_a = e_s * (relative_humidity_pct / 100.0)
        vpd = e_s - e_a

        gamma = FAO56_PSYCHROMETRIC_CONSTANT
        delta = (FAO56_VAPOR_SLOPE_NUM * e_s) / ((temp_c + FAO56_VAPOR_TEMP_OFFSET) ** 2)

        wind_term = FAO56_WIND_COEFF * wind_speed_m_s
        numerator = (
            FAO56_RADIATION_FACTOR * delta * net_radiation
            + gamma * (FAO56_TEMP_NUMERATOR / (temp_c + 273.0)) * wind_term * vpd
        )
        denominator = delta + gamma * (1.0 + FAO56_WIND_TERM_COEFF * wind_term)

        et_reference = numerator / denominator
        et_crop = et_reference * self.crop_coef

        return float(max(et_crop, 0.0))
