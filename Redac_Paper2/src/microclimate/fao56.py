import os
from functools import lru_cache
from types import SimpleNamespace

import numpy as np

from ..config_loader import ConfigModel, load_config
from ..constants import (
    FAO56_ABSOLUTE_ZERO_C,
    FAO56_NET_LONGWAVE_LOSS,
    FAO56_NET_SHORTWAVE_FRACTION,
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

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class GreenhouseEvapotranspiration:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.shading_factor = config.microclimate.greenhouse.shading_factor
        # Panel soiling is a PV property; it is kept for provenance but never
        # enters the crop energy balance (see calculate_evapotranspiration).
        self.soiling_factor = config.microclimate.greenhouse.soiling_factor
        self.crop_coef = config.microclimate.greenhouse.crop_coefficient

    def calculate_evapotranspiration(
        self,
        solar_flux_w_m2: float,
        temp_c: float,
        relative_humidity_pct: float,
        wind_speed_m_s: float,
        shading_factor: float = 0.0,
    ) -> float:
        """FAO-56 Penman-Monteith crop evapotranspiration (mm/day).

        Parameters
        ----------
        solar_flux_w_m2 : float
            24-h MEAN global horizontal irradiance (W/m2), not an instantaneous
            peak. Convert a peak with ``peak * PEAK_SUN_HOURS / 24``.
        temp_c : float
            Air temperature (deg C).
        relative_humidity_pct : float
            Relative humidity (%), clamped to [0, 100].
        wind_speed_m_s : float
            Wind speed (m/s) at the FAO-56 reference height. The aerodynamic
            term uses the standard FAO-56 wind expression with no empirical
            rescaling.
        shading_factor : float, optional
            Optional canopy-net-radiation attenuation for the shielded case
            (f_shade = GCR(1 - tau_AVT) = 0.41); net radiation is multiplied
            by (1 - shading_factor). Default 0.0 = open-field reference.

        Notes
        -----
        Net radiation is computed as ``0.77 * Rs - 1.9`` MJ/m2/day (clipped at
        zero). Panel soiling never enters the energy balance. Negative
        temperatures at or below absolute zero return 0.0.
        """
        if temp_c <= FAO56_ABSOLUTE_ZERO_C:
            return 0.0

        relative_humidity_pct = max(0.0, min(relative_humidity_pct, 100.0))

        daily_irradiance_mj = solar_flux_w_m2 * FAO56_W_TO_MJ_CONVERSION
        net_radiation = max(
            daily_irradiance_mj * FAO56_NET_SHORTWAVE_FRACTION - FAO56_NET_LONGWAVE_LOSS,
            0.0,
        )
        if shading_factor:
            net_radiation *= 1.0 - max(0.0, min(shading_factor, 1.0))

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
            + gamma * (FAO56_TEMP_NUMERATOR / (temp_c - FAO56_ABSOLUTE_ZERO_C)) * wind_term * vpd
        )
        denominator = delta + gamma * (1.0 + FAO56_WIND_TERM_COEFF * wind_term)

        et_reference = numerator / denominator
        et_crop = et_reference * self.crop_coef

        return float(max(et_crop, 0.0))


@lru_cache(maxsize=1)
def _reference_climate() -> GreenhouseEvapotranspiration:
    """Published reference greenhouse parameters from parameters.yaml (guarded)."""
    try:
        config = load_config(os.path.join(_PROJECT_ROOT, "parameters.yaml"))
        return GreenhouseEvapotranspiration(config)
    except Exception:
        # ponytail: parameters.yaml unreadable -> published reference values
        return GreenhouseEvapotranspiration(
            SimpleNamespace(
                microclimate=SimpleNamespace(
                    greenhouse=SimpleNamespace(
                        shading_factor=0.41,
                        soiling_factor=0.05,
                        crop_coefficient=0.85,
                    )
                )
            )
        )


def reference_conditions_et(
    temp_c: float = 25.0,
    rh: float = 60.0,
    wind: float = 2.0,
    mean_flux_w_m2: float = 240.0,
) -> dict:
    """Published open-field vs smart-shield FAO-56 pair (single source of truth).

    Reference conditions: T = 25 C, RH = 60 %, wind = 2.0 m/s, Kc from
    parameters.yaml, 24-h mean GHI 240 W/m2 (= 5.76 kWh/m2/day), canopy shading
    f_shade = 0.41 (GCR(1 - tau_AVT) = 0.55 * 0.75) applied to the shield only.

    Returns
    -------
    dict
        ``et_open`` / ``et_shield`` (mm/day), ``reduction_pct`` (%) and
        ``saving_l_per_m2_yr`` (L/m2/yr; 1 mm/day = 1 L/m2/day, x365 days).
    """
    climate = _reference_climate()
    et_open = climate.calculate_evapotranspiration(mean_flux_w_m2, temp_c, rh, wind)
    et_shield = climate.calculate_evapotranspiration(
        mean_flux_w_m2, temp_c, rh, wind, shading_factor=climate.shading_factor
    )
    saving_l_per_m2_yr = (et_open - et_shield) * 365.0
    reduction_pct = (et_open - et_shield) / et_open * 100.0 if et_open > 0.0 else 0.0
    return {
        "et_open": float(et_open),
        "et_shield": float(et_shield),
        "reduction_pct": float(reduction_pct),
        "saving_l_per_m2_yr": float(saving_l_per_m2_yr),
    }
