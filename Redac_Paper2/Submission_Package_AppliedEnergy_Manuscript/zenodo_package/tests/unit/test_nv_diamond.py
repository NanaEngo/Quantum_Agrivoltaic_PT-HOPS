"""Unit tests for NvDiamondSensor module."""

from unittest.mock import MagicMock

import pytest

from src.quantum_interface.nv_diamond import NvDiamondSensor


def _mock_config():
    return MagicMock()


class TestNvDiamondSensor:
    def test_initial_state(self):
        nv = NvDiamondSensor(_mock_config())
        assert nv.t1_ref_us == 300.0
        assert nv.t2_star_ref_us == 1.0
        assert nv.odmr_contrast == 0.25

    def test_relaxometry_no_metabolite(self):
        nv = NvDiamondSensor(_mock_config())
        res = nv.simulate_relaxometry(pathogen_metabolite_um=0.0)
        assert res["t1_us"] == pytest.approx(300.0, rel=0.01)
        assert res["t2_star_us"] == pytest.approx(1.0, rel=0.01)

    def test_relaxometry_high_metabolite(self):
        nv = NvDiamondSensor(_mock_config())
        res = nv.simulate_relaxometry(pathogen_metabolite_um=200.0)
        assert res["t1_us"] < 300.0
        assert res["t1_us"] >= 10.0
        assert res["t2_star_us"] < 1.0
        assert res["t2_star_us"] >= 0.1

    def test_relaxometry_temperature_effect(self):
        nv = NvDiamondSensor(_mock_config())
        res_cold = nv.simulate_relaxometry(pathogen_metabolite_um=50.0, temperature_k=278.0)
        res_hot = nv.simulate_relaxometry(pathogen_metabolite_um=50.0, temperature_k=318.0)
        assert res_cold["t1_us"] > res_hot["t1_us"]

    def test_classify_healthy(self):
        nv = NvDiamondSensor(_mock_config())
        res = nv.classify_pathogen(t1_us=295.0, t2_star_us=0.97)
        assert res["pathogen"] == "healthy"
        assert res["confidence"] > 0.5

    def test_classify_fungal(self):
        nv = NvDiamondSensor(_mock_config())
        res = nv.classify_pathogen(t1_us=165.0, t2_star_us=0.70)
        assert res["pathogen"] == "fungal"

    def test_classify_bacterial(self):
        nv = NvDiamondSensor(_mock_config())
        res = nv.classify_pathogen(t1_us=90.0, t2_star_us=0.45)
        assert res["pathogen"] == "bacterial"

    def test_classify_viral(self):
        nv = NvDiamondSensor(_mock_config())
        res = nv.classify_pathogen(t1_us=30.0, t2_star_us=0.20)
        assert res["pathogen"] == "viral"

    def test_classify_confidence_sum(self):
        nv = NvDiamondSensor(_mock_config())
        res = nv.classify_pathogen(t1_us=100.0, t2_star_us=0.50)
        assert 0.0 <= res["confidence"] <= 1.0
        assert "t1_ratio" in res
        assert "t2_ratio" in res

    def test_magnetometry(self):
        nv = NvDiamondSensor(_mock_config())
        b_field = nv.estimate_magnetometry(zeeman_shift_mhz=2.8)
        assert b_field == pytest.approx(1.0, abs=1e-6)
