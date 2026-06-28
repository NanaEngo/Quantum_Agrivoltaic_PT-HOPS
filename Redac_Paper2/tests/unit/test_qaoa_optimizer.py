"""Unit tests for QAOAOptimizer module."""

from unittest.mock import MagicMock

import numpy as np

from src.algorithms.qaoa_optimizer import (
    N_DECISION_VARIABLES,
    QAOAOptimizer,
)


def _mock_config():
    cfg = MagicMock()
    cfg.simulation.temperature_k = 295.0
    return cfg


class TestQAOAOptimizer:
    def test_initial_state(self):
        q = QAOAOptimizer(_mock_config())
        assert q.n_vars == N_DECISION_VARIABLES
        assert q.p == 3
        assert q.n_periods == 6

    def test_solve_with_high_solar(self):
        q = QAOAOptimizer(_mock_config())
        profile = np.full(96, 50.0)
        result = q.solve(profile)
        assert len(result["schedule"]) == 6
        assert result["total_revenue_usd"] > 0.0

    def test_solve_with_low_solar(self):
        q = QAOAOptimizer(_mock_config())
        profile = np.full(96, 0.1)
        result = q.solve(profile)
        for period in result["schedule"]:
            if period["solar_kw"] < 0.5:
                assert not period["cooling"]

    def test_utilization_fraction(self):
        q = QAOAOptimizer(_mock_config())
        profile = np.full(96, 10.0)
        result = q.solve(profile)
        assert 0.0 <= result["utilization_fraction"] <= 1.0

    def test_cost_hamiltonian_build(self):
        q = QAOAOptimizer(_mock_config())
        h, J = q._build_cost_hamiltonian(10.0, 2.0)
        assert len(h) == N_DECISION_VARIABLES
        assert J.shape == (N_DECISION_VARIABLES, N_DECISION_VARIABLES)
        assert J[0, 1] > 0.0
