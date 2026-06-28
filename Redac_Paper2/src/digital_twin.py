"""
Agrivoltaic Digital Twin (Axe 1) — Fuses quantum dynamics, microclimate,
IoT sensor telemetry, and LCA economics into a single stateful control loop.

The Digital Twin replaces the log-only heartbeat in the orchestrator with
actual cross-domain fusion: SERS anomalies trigger urgency flags, GQD sensor
data adjusts microclimate inputs, and QKD status gates irrigation commands.
"""

from __future__ import annotations

import numpy as np

from .config_loader import ConfigModel
from .lca.neb import NetEcologicalBenefit
from .logging_config import get_logger
from .microclimate.fao56 import GreenhouseEvapotranspiration
from .quantum_interface.diagnostics import SersDiagnostics

logger = get_logger("digital_twin")


class DigitalTwin:
    """Stateful agrivoltaic digital twin that fuses all five domains."""

    def __init__(self, config: ConfigModel) -> None:
        self.config = config
        self.sers = SersDiagnostics(config)
        self.climate = GreenhouseEvapotranspiration(config)
        self.lca = NetEcologicalBenefit(config)

        # Fusion state
        self._tick_count: int = 0
        self._last_anomaly_score: float = 0.0
        self._last_urgency: str = "NORMAL"
        self._last_phi_ft_global: float = 0.0
        self._ops_log: list[dict] = []
        logger.info(
            "DigitalTwin initialized: security_gate=%s", config.digital_twin.security_gate_qkd
        )

    # ── Public API ────────────────────────────────────────────────────────

    def tick(
        self,
        solar_flux: float,
        dm_array: np.ndarray | None = None,
        sers_readout: dict | None = None,
        anomaly_result: dict | None = None,
        sensor_telemetry: dict | None = None,
        qkd_status: dict | None = None,
    ) -> dict:
        """Run one fusion cycle and return consolidated state.

        Parameters
        ----------
        solar_flux : float
            Current solar irradiance (W/m²).
        dm_array : np.ndarray, optional
            Density matrices from quantum solver (T × N × N, complex).
        sers_readout : dict, optional
            SERS Raman spectrum from SersDiagnostics.
        anomaly_result : dict, optional
            QML anomaly detection output (predicted_stress, anomaly_score, ...).
        sensor_telemetry : dict, optional
            GQD sensor readings (gqd_fluorescence_intensity, soil_moisture_status, ...).
        qkd_status : dict, optional
            BB84 QKD status (qber, key, status).

        Returns
        -------
        dict
            Consolidated state with keys: tick, urgency, phi_ft_global,
            et_rate_mm_day, water_saved_liters, power_soiled_kwh,
            neb_co2_kg, anomaly_score, security_gate, calibration_correction,
            sensor_drift.
        """
        # 1. Calibration update from sensor drift
        cal_correction, sensor_drift = self._update_calibration(sensor_telemetry)

        # 2. Cross-domain feedback: SERS anomaly → urgency
        urgency = self._compute_update_urgency(anomaly_result)

        # 3. Cross-domain feedback: GQD telemetry → adjusted climate inputs
        adj_temp, adj_rh = self._fuse_climate_inputs(sensor_telemetry)

        # 4. Cross-domain feedback: QKD security gate
        irrigation_safe = self._check_security_gate(qkd_status)

        # 5. Soiling + global canopy yield
        days_since_cleaning = getattr(
            self.config.microclimate.greenhouse, "days_since_cleaning", 30
        )
        daily_decay_rate = self.config.physics.soiling_decay_rate_per_day
        power_ideal = solar_flux * self.config.lca.pv_efficiency * self.config.lca.pv_fill_factor
        power_soiled = SersDiagnostics.calculate_opv_power_with_soiling(
            power_ideal=power_ideal,
            days_since_cleaning=days_since_cleaning,
            daily_decay_rate=daily_decay_rate,
        )

        phi_ft_npom = 0.08  # default NPoM yield when no DM provided
        if dm_array is not None and dm_array.size > 0:
            from .constants import MAX_TRAPPING_YIELD, TRAPPING_SITES

            gamma_rc = self.config.quantum.fmo.coupling_reaction_center
            dt_fs = self.config.quantum.solver.time_step_fs
            trapped_pop = np.sum(dm_array[:, TRAPPING_SITES, TRAPPING_SITES].real, axis=1)
            phi_ft_npom = min(2.0 * gamma_rc * np.sum(trapped_pop) * dt_fs, MAX_TRAPPING_YIELD)

        phi_ft_global = self.sers.calculate_global_canopy_yield(
            phi_ft_npom=phi_ft_npom,
            phi_ft_passive=0.98,
            sentinel_ratio=self.config.physics.sensing_sentinel_ratio,
        )

        # 6. FAO-56 evapotranspiration with fused climate inputs
        from .constants import WIND_SPEED_GREENHOUSE_FACTOR

        wind_greenhouse = (
            self.config.microclimate.default_wind_speed_m_s * WIND_SPEED_GREENHOUSE_FACTOR
        )
        et_rate = self.climate.calculate_evapotranspiration(
            solar_flux_w_m2=solar_flux,
            temp_c=adj_temp,
            relative_humidity_pct=adj_rh,
            wind_speed_m_s=wind_greenhouse,
        )
        baseline_water_mm = self.config.microclimate.baseline_water_mm
        water_saved = max(0.0, baseline_water_mm - et_rate) * 1000.0  # L/m²

        # 7. LCA
        neb = self.lca.calculate_scenario_neb(
            scenario="A",
            excitonic_yield=phi_ft_global,
            water_saved_liters=water_saved,
            power_generated_kwh=power_soiled,
            crop_biomass_kg=self.config.lca.reference_biomass_kg,
        )

        # 8. Build state
        anomaly_score = 0.0
        predicted_stress = 0.0
        if anomaly_result:
            anomaly_score = anomaly_result.get("anomaly_score", 0.0)
            predicted_stress = anomaly_result.get("predicted_stress", 0.0)

        state = {
            "tick": self._tick_count,
            "urgency": urgency,
            "phi_ft_global": float(phi_ft_global),
            "phi_ft_npom": float(phi_ft_npom),
            "et_rate_mm_day": float(et_rate),
            "water_saved_liters": float(water_saved),
            "power_soiled_kwh": float(power_soiled),
            "neb_co2_kg": float(neb["net_benefit_co2_kg"]),
            "neb_biomass_kg": float(neb["effective_biomass_kg"]),
            "anomaly_score": float(anomaly_score),
            "predicted_stress": float(predicted_stress),
            "security_gate": irrigation_safe,
            "calibration_correction": float(cal_correction),
            "sensor_drift": float(sensor_drift),
            "solar_flux": float(solar_flux),
            "adj_temp_c": float(adj_temp),
            "adj_rh_pct": float(adj_rh),
        }

        self._tick_count += 1
        self._last_anomaly_score = anomaly_score
        self._last_urgency = urgency
        self._last_phi_ft_global = phi_ft_global
        self._ops_log.append(state)

        logger.info(
            "Tick %d: urgency=%s, phi_ft=%.4f, ET=%.2f mm/day, water_saved=%.1f L, "
            "security=%s, cal=%.4f, drift=%.4f",
            self._tick_count,
            urgency,
            phi_ft_global,
            et_rate,
            water_saved,
            irrigation_safe,
            cal_correction,
            sensor_drift,
        )
        return state

    def get_state_summary(self) -> dict:
        """Return the most recent fused state (or empty dict if no ticks)."""
        if not self._ops_log:
            return {}
        return self._ops_log[-1].copy()

    def get_ops_log(self) -> list[dict]:
        """Return full tick history."""
        return list(self._ops_log)

    # ── Internal cross-domain feedback ────────────────────────────────────

    def _compute_update_urgency(self, anomaly_result: dict | None) -> str:
        """SERS anomaly score → update frequency urgency level.

        HIGH: anomaly_score > 2.0 → request immediate quantum re-propagation
        MEDIUM: anomaly_score > 1.0 → request next-cycle update
        NORMAL: otherwise → standard 60s cadence
        """
        if not anomaly_result:
            return "NORMAL"
        score = anomaly_result.get("anomaly_score", 0.0)
        high_thresh = self.config.digital_twin.urgency_high_threshold
        medium_thresh = self.config.digital_twin.urgency_medium_threshold
        if score > high_thresh:
            logger.warning("Urgency HIGH: anomaly_score=%.4f > %.4f", score, high_thresh)
            return "HIGH"
        if score > medium_thresh:
            logger.info("Urgency MEDIUM: anomaly_score=%.4f > %.4f", score, medium_thresh)
            return "MEDIUM"
        return "NORMAL"

    def _fuse_climate_inputs(self, sensor_telemetry: dict | None) -> tuple[float, float]:
        """GQD sensor data → adjusted temperature and humidity for FAO-56.

        When soil moisture is 'dry', the greenhouse microclimate is slightly
        warmer and drier (evaporative cooling deficit). When sensor telemetry
        is unavailable, the config defaults are returned unchanged.
        """
        base_temp = self.config.microclimate.default_temp_c
        base_rh = self.config.microclimate.default_rh_pct

        if sensor_telemetry is None:
            return base_temp, base_rh

        soil_status = sensor_telemetry.get("soil_moisture_status", "optimum")
        if soil_status == "dry":
            # Dry soil → reduced evaporative cooling → +1.5°C, -5% RH
            return base_temp + 1.5, max(base_rh - 5.0, 10.0)

        return base_temp, base_rh

    def _check_security_gate(self, qkd_status: dict | None) -> bool:
        """QKD security check: returns False if quantum channel is compromised.

        When QBER exceeds the Shor-Preskill threshold, the digital twin
        disables automated irrigation commands to prevent adversarial
        manipulation of water allocation.
        """
        if not self.config.digital_twin.security_gate_qkd:
            return True
        if qkd_status is None:
            return True
        return qkd_status.get("status", "SECURE") == "SECURE"

    def _update_calibration(self, sensor_telemetry: dict | None) -> tuple[float, float]:
        """Update DynamicCalibrator EMA and return (correction_factor, drift)."""
        if sensor_telemetry is None:
            return 1.0, 0.0
        baseline = sensor_telemetry.get("baseline_reading")
        if baseline is None:
            return 1.0, 0.0
        from .iot_security.sensing import DynamicCalibrator

        if not hasattr(self, "_calibrator"):
            self._calibrator = DynamicCalibrator()
        result = self._calibrator.update(float(baseline))
        return result["correction_factor"], result["drift_fraction"]
