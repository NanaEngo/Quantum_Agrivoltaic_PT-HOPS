import hashlib
import json

from ..config_loader import ConfigModel
from ..logging_config import get_logger

logger = get_logger("gqas")

GQAS_VERSION = "1.0"
GQAS_MIN_QKD_QBER = 0.11
GQAS_MIN_QKD_KEY_RATE_HZ = 100.0
GQAS_MIN_DIFFERENTIAL_PRIVACY_EPSILON = 2.0
GQAS_MIN_SERS_LOD_NM = 50.0
GQAS_MIN_TRACE_FIDELITY = 0.95
GQAS_MAX_LATENCY_S = 5.0


class GqasComplianceChecker:
    """
    Global Quantum Agriculture Standard (GQAS) compliance checker.

    Defines a voluntary certification framework for quantum-enabled
    agrivoltaic installations. Six pillars:
    1. QKD security — minimum QBER and key rate
    2. Data sovereignty — differential privacy, immutable provenance
    3. Sensor integrity — SERS LOD threshold, NV diamond calibration
    4. Quantum fidelity — density-matrix trace, positivity
    5. Latency — end-to-end IoT-to-decision latency
    6. Sustainability — net ecological benefit minimum
    """

    def __init__(self, config: ConfigModel):
        self.config = config
        self._pillar_results: dict[str, bool] = {}
        self._scores: dict[str, float] = {}

    def check_qkd_security(self, qber: float, key_rate_hz: float) -> dict:
        ok_qber = qber <= GQAS_MIN_QKD_QBER
        ok_rate = key_rate_hz >= GQAS_MIN_QKD_KEY_RATE_HZ
        passed = ok_qber and ok_rate
        self._pillar_results["qkd_security"] = passed
        self._scores["qkd_security"] = 1.0 if passed else 0.0
        logger.info(
            "GQAS QKD: QBER=%.3f (%s), rate=%.1f Hz (%s) → %s",
            qber,
            "PASS" if ok_qber else "FAIL",
            key_rate_hz,
            "PASS" if ok_rate else "FAIL",
            "PASS" if passed else "FAIL",
        )
        return {"passed": passed, "qber_ok": ok_qber, "key_rate_ok": ok_rate}

    def check_data_sovereignty(self, epsilon: float, ledger_intact: bool) -> dict:
        ok_dp = epsilon >= GQAS_MIN_DIFFERENTIAL_PRIVACY_EPSILON
        passed = ok_dp and ledger_intact
        self._pillar_results["data_sovereignty"] = passed
        self._scores["data_sovereignty"] = 1.0 if passed else 0.0
        logger.info(
            "GQAS Data Sovereignty: ε=%.1f (%s), ledger=%s → %s",
            epsilon,
            "PASS" if ok_dp else "FAIL",
            ledger_intact,
            "PASS" if passed else "FAIL",
        )
        return {"passed": passed, "epsilon_ok": ok_dp, "ledger_intact": ledger_intact}

    def check_sensor_integrity(self, sers_lod_nm: float, nv_calibrated: bool) -> dict:
        ok_sers = sers_lod_nm <= GQAS_MIN_SERS_LOD_NM
        passed = ok_sers and nv_calibrated
        self._pillar_results["sensor_integrity"] = passed
        self._scores["sensor_integrity"] = 1.0 if passed else 0.0
        logger.info(
            "GQAS Sensor: SERS LOD=%.1f nM (%s), NV cal=%s → %s",
            sers_lod_nm,
            "PASS" if ok_sers else "FAIL",
            nv_calibrated,
            "PASS" if passed else "FAIL",
        )
        return {"passed": passed, "sers_ok": ok_sers, "nv_calibrated": nv_calibrated}

    def check_quantum_fidelity(self, trace_ok: bool, positivity_ok: bool) -> dict:
        passed = trace_ok and positivity_ok
        self._pillar_results["quantum_fidelity"] = passed
        self._scores["quantum_fidelity"] = 1.0 if passed else 0.0
        return {"passed": passed, "trace_ok": trace_ok, "positivity_ok": positivity_ok}

    def check_latency(self, end_to_end_latency_s: float) -> dict:
        passed = end_to_end_latency_s <= GQAS_MAX_LATENCY_S
        self._pillar_results["latency"] = passed
        self._scores["latency"] = 1.0 if passed else 0.0
        return {
            "passed": passed,
            "latency_s": end_to_end_latency_s,
            "max_latency_s": GQAS_MAX_LATENCY_S,
        }

    def check_sustainability(self, neb_co2_kg: float, payback_yr: float) -> dict:
        passed = neb_co2_kg > 0.0 and payback_yr < 10.0
        self._pillar_results["sustainability"] = passed
        self._scores["sustainability"] = 1.0 if passed else 0.0
        return {"passed": passed, "neb_co2_kg": neb_co2_kg, "payback_yr": payback_yr}

    def full_audit(
        self,
        qber: float,
        key_rate_hz: float,
        epsilon: float,
        ledger_intact: bool,
        sers_lod_nm: float,
        nv_calibrated: bool,
        trace_ok: bool,
        positivity_ok: bool,
        end_to_end_latency_s: float,
        neb_co2_kg: float,
        payback_yr: float,
    ) -> dict:
        results = {}
        results["qkd_security"] = self.check_qkd_security(qber, key_rate_hz)
        results["data_sovereignty"] = self.check_data_sovereignty(epsilon, ledger_intact)
        results["sensor_integrity"] = self.check_sensor_integrity(sers_lod_nm, nv_calibrated)
        results["quantum_fidelity"] = self.check_quantum_fidelity(trace_ok, positivity_ok)
        results["latency"] = self.check_latency(end_to_end_latency_s)
        results["sustainability"] = self.check_sustainability(neb_co2_kg, payback_yr)
        pillars_passed = sum(1 for r in results.values() if r["passed"])
        total_pillars = len(results)
        overall_pass = pillars_passed >= total_pillars
        composite_score = pillars_passed / total_pillars
        audit_id = hashlib.sha256(json.dumps(results, sort_keys=True).encode()).hexdigest()[:12]
        logger.info(
            "GQAS full audit: %d/%d pillars passed → %s (score=%.2f, id=%s)",
            pillars_passed,
            total_pillars,
            "PASS" if overall_pass else "PARTIAL",
            composite_score,
            audit_id,
        )
        return {
            "pillars": results,
            "overall_pass": overall_pass,
            "composite_score": float(composite_score),
            "pillars_passed": pillars_passed,
            "total_pillars": total_pillars,
            "audit_id": audit_id,
            "gqas_version": GQAS_VERSION,
        }

    def get_summary(self) -> dict:
        return {
            "pillars_pass": self._pillar_results,
            "scores": self._scores,
            "gqas_version": GQAS_VERSION,
        }
