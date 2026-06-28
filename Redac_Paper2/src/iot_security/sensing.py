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
from ..logging_config import get_logger

logger = get_logger("sensing")


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

        status = "dry" if soil_moisture_pct < SOIL_MOISTURE_DRY_THRESHOLD else "optimum"
        logger.info(
            "GQD telemetry: moisture=%.1f%%, Pb=%.2f ppm, pesticide=%.1f ppb → "
            "intensity=%.2f, peak=%.1f nm, status=%s",
            soil_moisture_pct,
            heavy_metal_pb_ppm,
            pesticide_ppb,
            gqd_quenched_intensity,
            GQD_CORE_SHELL_BASELINE_NM + red_shift_nm,
            status,
        )
        return {
            "gqd_fluorescence_intensity": float(max(gqd_quenched_intensity, 0.0)),
            "core_shell_peak_wavelength_nm": float(GQD_CORE_SHELL_BASELINE_NM + red_shift_nm),
            "soil_moisture_status": status,
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


class DynamicCalibrator:
    """
    V5: Corrects GQD sensor baseline drift due to biofouling, thermal cycling,
    and long-term field ageing.

    Uses an exponential moving average (EMA) of recent baseline readings to
    compute a multiplicative correction factor. This maintains measurement
    accuracy between scheduled cleaning cycles.
    """

    def __init__(
        self,
        ema_alpha: float = 0.1,
        drift_alarm_threshold: float = 0.20,
        k_sv_ref: float = 1.5e5,
        t_ref: float = 298.15,
    ):
        """
        Args:
            ema_alpha: EMA smoothing factor in [0, 1]. Smaller = slower adaptation.
            drift_alarm_threshold: Fractional drift (vs. initial baseline) that
                triggers a maintenance alert (default 20%).
        """
        if not 0.0 <= ema_alpha <= 1.0:
            raise ValueError(f"ema_alpha must be in [0, 1], got {ema_alpha}")
        self.ema_alpha = ema_alpha
        self.drift_alarm_threshold = drift_alarm_threshold
        self._baseline_ema: float | None = None
        self._reference_baseline: float | None = None
        self.k_sv_ref = k_sv_ref
        self.t_ref = t_ref

    def update(self, raw_baseline_reading: float) -> dict:
        """
        Update EMA with a new baseline measurement and return calibration state.

        Args:
            raw_baseline_reading: GQD fluorescence intensity measured on a
                reference (clean-water) sample to characterise current drift.

        Returns:
            dict with 'correction_factor', 'drift_fraction', 'alarm', 'ema_baseline'.
        """
        if self._baseline_ema is None:
            self._baseline_ema = raw_baseline_reading
            self._reference_baseline = raw_baseline_reading
        else:
            self._baseline_ema = (
                self.ema_alpha * raw_baseline_reading + (1.0 - self.ema_alpha) * self._baseline_ema
            )

        ref = self._reference_baseline if self._reference_baseline else 1.0
        drift_fraction = abs(self._baseline_ema - ref) / max(abs(ref), 1e-12)
        correction_factor = ref / max(self._baseline_ema, 1e-12)
        alarm = drift_fraction > self.drift_alarm_threshold
        if alarm:
            logger.warning(
                "DynamicCalibrator: drift=%.2f%% exceeds threshold %.2f%% — cleaning required",
                drift_fraction * 100,
                self.drift_alarm_threshold * 100,
            )
        logger.debug(
            "DynamicCalibrator: correction=%.4f, drift=%.4f, ema=%.4f",
            correction_factor,
            drift_fraction,
            self._baseline_ema,
        )

        return {
            "correction_factor": float(correction_factor),
            "drift_fraction": float(drift_fraction),
            "ema_baseline": float(self._baseline_ema),
            "alarm": bool(alarm),
            "alarm_message": "Panel cleaning required — sensor drift >20%" if alarm else None,
        }

    def apply_correction(self, raw_measurement: float) -> float:
        """Apply current EMA correction to a raw sensor measurement."""
        if self._baseline_ema is None or self._reference_baseline is None:
            return raw_measurement
        correction_factor = self._reference_baseline / max(self._baseline_ema, 1e-12)
        return float(raw_measurement * correction_factor)

    def get_calibrated_k_sv(self, temperature_k: float, salinity_ms_cm: float) -> float:
        """
        Ajuste la constante de Stern-Volmer pour contrer la dérive due à la température et au pH/salinité.
        """
        alpha_temp = -0.0035  # Dérive thermique
        beta_salinity = -0.012  # Dérive due à la salinité du sol (fouling)

        delta_t = temperature_k - self.t_ref
        k_sv_adj = self.k_sv_ref * (1.0 + alpha_temp * delta_t + beta_salinity * salinity_ms_cm)
        logger.debug(
            "Stern-Volmer calibrated: k_sv=%.1e (T=%.1f K, S=%.2f mS/cm)",
            max(k_sv_adj, 1e4),
            temperature_k,
            salinity_ms_cm,
        )
        return float(max(k_sv_adj, 1e4))
