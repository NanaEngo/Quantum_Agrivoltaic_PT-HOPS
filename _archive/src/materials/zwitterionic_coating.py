from ..config_loader import ConfigModel
from ..logging_config import get_logger

logger = get_logger("zwitterionic")

COATING_INITIAL_THICKNESS_NM = 20.0
COATING_DEGRADATION_RATE_NM_PER_DAY = 0.3
COATING_CRITICAL_THICKNESS_NM = 5.0
COATING_REAPPLICATION_COST_USD = 20.0
COATING_MAX_LIFETIME_DAYS = 60.0
COATING_COHERENCE_PRESERVATION_FRACTION = 0.90


class ZwitterionicCoating:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.thickness_nm = COATING_INITIAL_THICKNESS_NM
        self.application_count = 0
        self._apply()

    def _apply(self):
        self.thickness_nm = COATING_INITIAL_THICKNESS_NM
        self.application_count += 1
        logger.info(
            "Zwitterionic coating applied (#%d): initial thickness = %.1f nm",
            self.application_count,
            self.thickness_nm,
        )

    def degrade(self, days: float = 1.0) -> float:
        self.thickness_nm = max(
            0.0,
            self.thickness_nm - COATING_DEGRADATION_RATE_NM_PER_DAY * days,
        )
        if self.thickness_nm <= COATING_CRITICAL_THICKNESS_NM:
            logger.warning(
                "Coating degraded to %.1f nm (critical=%.1f nm) — reapplication needed",
                self.thickness_nm,
                COATING_CRITICAL_THICKNESS_NM,
            )
        return self.thickness_nm

    @property
    def is_intact(self) -> bool:
        return self.thickness_nm > COATING_CRITICAL_THICKNESS_NM

    @property
    def coherence_retention(self) -> float:
        if self.thickness_nm <= 0.0:
            return 0.0
        effective = min(self.thickness_nm / COATING_INITIAL_THICKNESS_NM, 1.0)
        return effective * COATING_COHERENCE_PRESERVATION_FRACTION

    @property
    def remaining_lifetime_days(self) -> float:
        if self.thickness_nm <= 0.0:
            return 0.0
        return self.thickness_nm / COATING_DEGRADATION_RATE_NM_PER_DAY

    def get_sensor_correction_factor(self, raw_drift_rate: float) -> float:
        if self.is_intact:
            return raw_drift_rate * (1.0 - self.coherence_retention)
        return raw_drift_rate

    def get_annual_opex(self) -> float:
        n_applications = max(1, int(365.0 / COATING_MAX_LIFETIME_DAYS))
        return float(n_applications) * COATING_REAPPLICATION_COST_USD

    def simulate_annual_cycle(self) -> dict:
        days = 0
        total_cost = 0.0
        thickness_log = []
        while days < 365:
            self.degrade(1.0)
            if not self.is_intact:
                self._apply()
                total_cost += COATING_REAPPLICATION_COST_USD
            thickness_log.append(self.thickness_nm)
            days += 1
        return {
            "annual_reapplications": self.application_count,
            "annual_opex_usd": total_cost,
            "final_thickness_nm": self.thickness_nm,
            "avg_coherence_retention": sum(
                min(t / COATING_INITIAL_THICKNESS_NM, 1.0) * COATING_COHERENCE_PRESERVATION_FRACTION
                for t in thickness_log
            )
            / len(thickness_log)
            if thickness_log
            else 0.0,
        }
