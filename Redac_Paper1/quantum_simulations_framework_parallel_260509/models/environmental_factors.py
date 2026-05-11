"""
Environmental Impact Modeling for Agrivoltaic Systems.

This module provides the EnvironmentalFactors class, which models the influence 
of external conditions (temperature, humidity, dust, and wind) on the 
performance of hybrid OPV-PSU systems. It implements phenomenological models 
to adjust energy conversion efficiencies and electron transport rates based 
on varying climate profiles.
"""

import logging
import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.core.constants import (
    ENVIRONMENTAL_DUST_SAT_FACTOR,
    ENVIRONMENTAL_HUMIDITY_OPT,
    ENVIRONMENTAL_T_REF,
    DEFAULT_DUST_RATE,
    DEFAULT_DUST_SATURATION,
    TEMP_COEFF_OPV,
    TEMP_COEFF_PSU,
    HUMIDITY_COEFF,
    WIND_SPEED_FACTOR,
    ENVIRONMENTAL_PRECIP_PROB,
    ENVIRONMENTAL_PRECIP_CLEAN_FACTOR
)

logger = logging.getLogger(__name__)


class EnvironmentalFactors:
    """
    Environmental impact simulator for agrivoltaic performance metrics.

    This class provides a suite of models to quantify how environmental 
    stressors degrade the performance of organic photovoltaics and 
    photosynthetic units. It supports both time-dependent degradation 
    (dust accumulation) and state-dependent efficiency scaling (temperature 
    and humidity).

    Mathematical Framework
    ----------------------
    1. Dust accumulation: Saturation-limited growth with reset events:
       d(t) = d_sat * (1 - exp(-k * t))

    2. Temperature scaling: Linear efficiency degradation:
       η(T) = η_ref * [1 - α * (T - T_ref)]

    3. Humidity scaling: Optimization-centered parabolic/linear scaling:
       η_h = η_0 * (1 - β * |h - h_opt|)
    """

    def __init__(self):
        """Initialize environmental factors with default parameters."""
        # Environmental parameters
        self.dust_accumulation_rate = DEFAULT_DUST_RATE  # Units per day
        self.dust_saturation_thickness = DEFAULT_DUST_SATURATION  # Max dust thickness
        self.temperature_coefficient_opv = TEMP_COEFF_OPV  # % / K for OPV efficiency
        self.temperature_coefficient_psu = TEMP_COEFF_PSU  # % / K for PSU efficiency
        self.humidity_coefficient = HUMIDITY_COEFF  # Effect of humidity on performance
        self.wind_speed_factor = WIND_SPEED_FACTOR  # Factor for dust removal
        logger.debug("EnvironmentalFactors initialized with default parameters")

    def dust_accumulation_model(self, time_days, initial_dust=0.1, weather_conditions="normal"):
        """
        Model dust accumulation over time with weather effects.

        Mathematical Framework:
        Dust accumulation is modeled as a saturating process with different
        accumulation rates based on weather conditions:

        d(t) = d_sat * (1 - exp(-k * t))

        where d_sat is the saturation dust thickness, k is the accumulation rate
        constant, and t is time. Precipitation events reset dust accumulation.

        Parameters
        ----------
        time_days : np.ndarray
            Time points in days
        initial_dust : float
            Initial dust thickness
        weather_conditions : str
            Weather type ('arid', 'normal', 'humid', 'dusty')

        Returns
        -------
        np.ndarray
            Dust thickness over time
        """
        # Adjust accumulation rate based on weather
        if weather_conditions == "arid":
            k = self.dust_accumulation_rate * 1.5
        elif weather_conditions == "dusty":
            k = self.dust_accumulation_rate * 2.0
        elif weather_conditions == "humid":
            k = self.dust_accumulation_rate * 0.5
        else:  # normal
            k = self.dust_accumulation_rate

        # Simulate some random precipitation events that reset dust
        dust_thickness = np.zeros_like(time_days, dtype=float)
        current_dust = initial_dust

        for i, _t in enumerate(time_days):
            # Apply accumulation
            current_dust = min(
                self.dust_saturation_thickness,
                current_dust + k * (1 - current_dust / self.dust_saturation_thickness),
            )

            # Random precipitation event (5% chance per day)
            if np.random.random() < ENVIRONMENTAL_PRECIP_PROB:
                current_dust *= ENVIRONMENTAL_PRECIP_CLEAN_FACTOR  # Reduce dust by 70%

            dust_thickness[i] = current_dust

        return dust_thickness

    def temperature_effects_model(self, temperatures, base_efficiency, efficiency_type="opv"):
        r"""
        Model temperature effects on system efficiency.

        Mathematical Framework:
        Temperature effects on efficiency follow a linear model:

        \eta(T) = \eta_ref * [1 - \alpha * (T - T_ref)]

        where \eta_ref is the reference efficiency at T_ref, \alpha is the
        temperature coefficient, and T is the operating temperature.

        Parameters
        ----------
        temperatures : np.ndarray
            Temperature values in Kelvin
        base_efficiency : float
            Reference efficiency at reference temperature
        efficiency_type : str
            Type of efficiency ('opv', 'psu')

        Returns
        -------
        np.ndarray
            Temperature-adjusted efficiency
        """
        # Reference temperature (STC = 298.15K)
        T_ref = ENVIRONMENTAL_T_REF

        # Select temperature coefficient based on system type
        if efficiency_type == "opv":
            alpha = self.temperature_coefficient_opv
        else:  # psu
            alpha = self.temperature_coefficient_psu

        # Calculate efficiency with temperature correction
        efficiency = base_efficiency * (1 - alpha * (temperatures - T_ref))

        # Ensure efficiency remains positive
        efficiency = np.clip(efficiency, 0, base_efficiency)

        return efficiency

    def humidity_effects_model(self, humidity_values, base_efficiency):
        r"""
        Model humidity effects on system efficiency.

        Mathematical Framework:
        Humidity effects can be complex, but are often approximated as:

        \eta_h = \eta_0 * (1 - \beta * |h - h_opt|)

        where h is relative humidity, h_opt is optimal humidity, and \beta is
        the humidity sensitivity coefficient.

        Parameters
        ----------
        humidity_values : np.ndarray
            Relative humidity values (0-1)
        base_efficiency : float
            Base efficiency without humidity effects

        Returns
        -------
        np.ndarray
            Humidity-adjusted efficiency
        """
        # Optimal humidity (e.g., 45%)
        optimal_humidity = ENVIRONMENTAL_HUMIDITY_OPT

        # Calculate deviation from optimal humidity
        humidity_deviation = np.abs(humidity_values - optimal_humidity)

        # Apply humidity effects
        efficiency = base_efficiency * (1 - self.humidity_coefficient * humidity_deviation)

        # Ensure efficiency remains positive
        efficiency = np.clip(efficiency, 0, base_efficiency)

        return efficiency

    def wind_effects_model(self, wind_speeds, dust_thickness):
        """
        Model wind effects on dust removal and heat dissipation.

        Mathematical Framework:
        Wind affects dust accumulation through removal rate and influences
        heat dissipation. The dust removal rate is modeled as:

        dr/dt = -k_wind * v * d

        where v is wind speed and k_wind is the removal rate constant.

        Parameters
        ----------
        wind_speeds : np.ndarray
            Wind speeds in m/s
        dust_thickness : np.ndarray
            Current dust thickness

        Returns
        -------
        np.ndarray
            Dust thickness after wind effects
        """
        # Apply wind dust removal
        removal_factor = np.exp(-self.wind_speed_factor * wind_speeds)
        adjusted_dust = dust_thickness * removal_factor

        return adjusted_dust

    def combined_environmental_effects(
        self,
        time_days,
        temperatures,
        humidity_values,
        wind_speeds,
        base_pce,
        base_etr,
        weather_conditions="normal",
    ):
        r"""
        Combine all environmental effects into a comprehensive model.

        Mathematical Framework:
        The combined environmental effect is approximated as a product of
        individual effects:

        \eta_combined = \eta_base * \eta_dust * \eta_temp * \eta_humidity * \eta_wind

        This assumes that the environmental effects are approximately
        independent and multiplicative.

        Parameters
        ----------
        time_days : np.ndarray
            Time points in days
        temperatures : np.ndarray
            Temperature values in Kelvin
        humidity_values : np.ndarray
            Relative humidity values (0-1)
        wind_speeds : np.ndarray
            Wind speeds in m/s
        base_pce : float
            Base PCE without environmental effects
        base_etr : float
            Base ETR without environmental effects
        weather_conditions : str
            Weather type ('arid', 'normal', 'humid', 'dusty')

        Returns
        -------
        tuple
            (pce_env, etr_env, dust_profile) - Adjusted PCE, ETR, and dust profile
        """
        # Calculate dust accumulation
        dust_profile = self.dust_accumulation_model(
            time_days, weather_conditions=weather_conditions
        )

        # Apply wind effects to dust
        dust_profile = self.wind_effects_model(wind_speeds, dust_profile)

        # Calculate temperature effects
        pce_temp = self.temperature_effects_model(temperatures, base_pce, "opv")
        etr_temp = self.temperature_effects_model(temperatures, base_etr, "psu")

        # Calculate humidity effects
        pce_humidity = self.humidity_effects_model(humidity_values, base_pce)
        etr_humidity = self.humidity_effects_model(humidity_values, base_etr)

        # Combine all effects
        # For simplicity, using average dust effect across wavelengths
        dust_factor = 1 - (dust_profile / self.dust_saturation_thickness) * ENVIRONMENTAL_DUST_SAT_FACTOR

        pce_env = base_pce * dust_factor * (pce_temp / base_pce) * (pce_humidity / base_pce)
        etr_env = base_etr * dust_factor * (etr_temp / base_etr) * (etr_humidity / base_etr)

        return pce_env, etr_env, dust_profile

    def save_environmental_data_to_csv(
        self,
        time_days: np.ndarray,
        temperatures: np.ndarray,
        humidity_values: np.ndarray,
        wind_speeds: np.ndarray,
        pce_env: np.ndarray,
        etr_env: np.ndarray,
        dust_profile: np.ndarray,
        filename_prefix: str = "environmental_effects",
        output_dir: str = "../simulation_data/",
    ) -> str:
        """
        Save environmental effects data to CSV.

        Parameters
        ----------
        time_days : np.ndarray
            Time points in days
        temperatures : np.ndarray
            Temperature values in Kelvin
        humidity_values : np.ndarray
            Relative humidity values (0-1)
        wind_speeds : np.ndarray
            Wind speeds in m/s
        pce_env : np.ndarray
            PCE with environmental effects
        etr_env : np.ndarray
            ETR with environmental effects
        dust_profile : np.ndarray
            Dust thickness over time
        filename_prefix : str
            Prefix for output filename
        output_dir : str
            Directory to save CSV file

        Returns
        -------
        str
            Path to saved CSV file
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        df = pd.DataFrame(
            {
                "time_days": time_days,
                "temperature_k": temperatures,
                "humidity": humidity_values,
                "wind_speed_m_s": wind_speeds,
                "dust_thickness": dust_profile,
                "pce_with_environment": pce_env,
                "etr_with_environment": etr_env,
            }
        )

        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False, float_format="%.6e")

        logger.info(f"Environmental data saved to {filepath}")
        return filepath

    def plot_environmental_effects(
        self,
        temperatures: np.ndarray,
        humidity_values: np.ndarray,
        wind_speeds: np.ndarray,
        pce_temp: np.ndarray,
        etr_temp: np.ndarray,
        pce_humidity: np.ndarray,
        etr_humidity: np.ndarray,
        filename_prefix: str = "environmental_effects_static",
        figures_dir: str = "../Graphics/",
    ) -> str:
        """
        Plot environmental effects as static parameter sweeps to ensure physical relevance
        to ultrafast dynamics, replacing the physically unmotivated 365-day seasonal cycle.

        Parameters
        ----------
        temperatures : np.ndarray
            Temperature values in Kelvin
        humidity_values : np.ndarray
            Relative humidity values (0-1)
        wind_speeds : np.ndarray
            Wind speeds in m/s
        pce_temp, etr_temp, pce_humidity, etr_humidity: np.ndarray
            Sweep results for plotting
        filename_prefix : str
            Prefix for output filename
        figures_dir : str
            Directory to save figures
        """
        os.makedirs(figures_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle("Environmental Effects on Exciton Transport", fontsize=16, fontweight="bold")

        # (a) Temperature Profile
        ax1 = axes[0]
        ax1.plot(temperatures, etr_temp * 100, "r-", linewidth=2, label="ETR")
        ax1.plot(temperatures, pce_temp * 100, "b--", linewidth=2, label="PCE")
        ax1.set_xlabel("Temperature [K]", fontsize=12)
        ax1.set_ylabel("Efficiency [%]", fontsize=12)
        ax1.set_title("(a) Temperature Profile", fontsize=14, fontweight="bold")
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # (b) Humidity Profile
        ax2 = axes[1]
        ax2.plot(humidity_values * 100, etr_humidity * 100, "g-", linewidth=2, label="ETR")
        ax2.plot(humidity_values * 100, pce_humidity * 100, "b--", linewidth=2, label="PCE")
        ax2.set_xlabel("Relative Humidity [%]", fontsize=12)
        ax2.set_ylabel("Efficiency [%]", fontsize=12)
        ax2.set_title("(b) Humidity Profile", fontsize=14, fontweight="bold")
        ax2.grid(True, alpha=0.3)
        ax2.legend()

        plt.tight_layout()

        filename = f"{filename_prefix}_{timestamp}.pdf"
        filepath = os.path.join(figures_dir, filename)
        plt.savefig(filepath, dpi=600, bbox_inches="tight")
        plt.close()

        logger.info(f"Environmental parameter sweeps saved to {filepath}")
        return filepath
