"""Unit tests for GqasComplianceChecker module."""

from unittest.mock import MagicMock

import pytest

from src.iot_security.gqas_standard import GqasComplianceChecker


def _mock_config():
    return MagicMock()


class TestGqasComplianceChecker:
    def test_initial_state(self):
        gqas = GqasComplianceChecker(_mock_config())
        assert gqas._pillar_results == {}
        assert gqas._scores == {}

    def test_qkd_security_pass(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_qkd_security(qber=0.05, key_rate_hz=500.0)
        assert res["passed"]
        assert res["qber_ok"]
        assert res["key_rate_ok"]

    def test_qkd_security_fail_qber(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_qkd_security(qber=0.15, key_rate_hz=500.0)
        assert not res["passed"]
        assert not res["qber_ok"]

    def test_qkd_security_fail_rate(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_qkd_security(qber=0.05, key_rate_hz=50.0)
        assert not res["passed"]
        assert not res["key_rate_ok"]

    def test_data_sovereignty_pass(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_data_sovereignty(epsilon=2.0, ledger_intact=True)
        assert res["passed"]

    def test_data_sovereignty_fail_epsilon(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_data_sovereignty(epsilon=1.0, ledger_intact=True)
        assert not res["passed"]

    def test_data_sovereignty_fail_ledger(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_data_sovereignty(epsilon=3.0, ledger_intact=False)
        assert not res["passed"]

    def test_sensor_integrity_pass(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_sensor_integrity(sers_lod_nm=30.0, nv_calibrated=True)
        assert res["passed"]

    def test_sensor_integrity_fail_sers(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_sensor_integrity(sers_lod_nm=100.0, nv_calibrated=True)
        assert not res["passed"]

    def test_sensor_integrity_fail_nv(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_sensor_integrity(sers_lod_nm=30.0, nv_calibrated=False)
        assert not res["passed"]

    def test_quantum_fidelity_pass(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_quantum_fidelity(trace_ok=True, positivity_ok=True)
        assert res["passed"]

    def test_quantum_fidelity_fail(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_quantum_fidelity(trace_ok=False, positivity_ok=True)
        assert not res["passed"]

    def test_latency_pass(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_latency(end_to_end_latency_s=2.5)
        assert res["passed"]

    def test_latency_fail(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_latency(end_to_end_latency_s=10.0)
        assert not res["passed"]

    def test_sustainability_pass(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_sustainability(neb_co2_kg=15.0, payback_yr=4.5)
        assert res["passed"]

    def test_sustainability_fail_neb(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_sustainability(neb_co2_kg=-1.0, payback_yr=4.5)
        assert not res["passed"]

    def test_sustainability_fail_payback(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.check_sustainability(neb_co2_kg=15.0, payback_yr=12.0)
        assert not res["passed"]

    def test_full_audit_all_pass(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.full_audit(
            qber=0.05,
            key_rate_hz=500.0,
            epsilon=2.0,
            ledger_intact=True,
            sers_lod_nm=30.0,
            nv_calibrated=True,
            trace_ok=True,
            positivity_ok=True,
            end_to_end_latency_s=2.5,
            neb_co2_kg=15.0,
            payback_yr=4.5,
        )
        assert res["overall_pass"]
        assert res["pillars_passed"] == 6
        assert res["total_pillars"] == 6
        assert res["composite_score"] == pytest.approx(1.0)
        assert len(res["audit_id"]) == 12

    def test_full_audit_partial(self):
        gqas = GqasComplianceChecker(_mock_config())
        res = gqas.full_audit(
            qber=0.15,
            key_rate_hz=500.0,
            epsilon=1.0,
            ledger_intact=True,
            sers_lod_nm=30.0,
            nv_calibrated=True,
            trace_ok=True,
            positivity_ok=True,
            end_to_end_latency_s=2.5,
            neb_co2_kg=15.0,
            payback_yr=4.5,
        )
        assert not res["overall_pass"]
        assert res["pillars_passed"] < 6
        assert 0.0 < res["composite_score"] < 1.0

    def test_get_summary(self):
        gqas = GqasComplianceChecker(_mock_config())
        gqas.check_qkd_security(qber=0.05, key_rate_hz=500.0)
        summary = gqas.get_summary()
        assert "pillars_pass" in summary
        assert "scores" in summary
        assert summary["gqas_version"] == "1.0"
