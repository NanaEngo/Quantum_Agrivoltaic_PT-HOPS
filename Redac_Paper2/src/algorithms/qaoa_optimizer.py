import numpy as np

from ..config_loader import ConfigModel
from ..logging_config import get_logger

logger = get_logger("qaoa")

N_DECISION_VARIABLES = 3
N_MACRO_PERIODS = 6
QAOA_DEPTH_P = 3
IRRIGATION_PUMP_POWER_KW = 2.0
REFRIGERATION_POWER_KW = 1.5
GRID_EXPORT_PRICE_USD_PER_KWH = 0.12
IRRIGATION_VALUE_USD_PER_KWH = 0.15
REFRIGERATION_VALUE_USD_PER_KWH = 0.20


class QAOAOptimizer:
    def __init__(self, config: ConfigModel, backend: str = "classical"):
        self.config = config
        self.p = QAOA_DEPTH_P
        self.n_vars = N_DECISION_VARIABLES
        self.n_periods = N_MACRO_PERIODS
        self.backend = backend
        if backend not in ("classical", "pennylane"):
            raise ValueError(f"Unsupported QAOA backend: {backend}")
        self._init_pennylane()

    def _init_pennylane(self):
        if self.backend == "pennylane":
            try:
                import pennylane as qml

                self._qml = qml
                self._dev = qml.device("default.qubit", wires=self.n_vars, shots=1024)
                logger.info(
                    "PennyLane QAOA backend initialised (wires=%d, shots=1024)", self.n_vars
                )
            except ImportError:
                logger.warning("PennyLane not installed — falling back to classical backend")
                self.backend = "classical"
        else:
            self._qml = None
            self._dev = None

    def _build_cost_hamiltonian(self, solar_power_kw: float, period_h: int) -> tuple:
        J = np.zeros((self.n_vars, self.n_vars))
        h = np.zeros(self.n_vars)
        h[0] = -IRRIGATION_VALUE_USD_PER_KWH * solar_power_kw * period_h
        h[1] = -REFRIGERATION_VALUE_USD_PER_KWH * solar_power_kw * period_h
        h[2] = -GRID_EXPORT_PRICE_USD_PER_KWH * solar_power_kw * period_h
        J[0, 1] = J[1, 0] = min(solar_power_kw * 0.1, 5.0)
        return h, J

    def solve(self, solar_power_profile_kw: np.ndarray) -> dict:
        schedule = []
        total_revenue = 0.0
        total_power_used = 0.0
        power_available = solar_power_profile_kw
        period_duration_h = 24.0 / self.n_periods
        for p in range(self.n_periods):
            p_start = int(p * len(power_available) / self.n_periods)
            p_end = int((p + 1) * len(power_available) / self.n_periods)
            period_solar = float(np.mean(power_available[p_start:p_end]))
            h, J = self._build_cost_hamiltonian(period_solar, period_duration_h)
            if self.backend == "pennylane":
                x = self._pennylane_qaoa(h, J, period_solar)
            else:
                x = self._classical_qaoa_approximation(h, J, period_solar)
            irrigation_on, cooling_on, export_on = x
            irrigation_kwh = irrigation_on * IRRIGATION_PUMP_POWER_KW * period_duration_h
            cooling_kwh = cooling_on * REFRIGERATION_POWER_KW * period_duration_h
            export_kwh = export_on * max(
                0.0, period_solar * period_duration_h - irrigation_kwh - cooling_kwh
            )
            period_revenue = (
                irrigation_on * h[0] * -1 * period_duration_h
                + cooling_on * h[1] * -1 * period_duration_h
                + export_on * h[2] * -1 * period_duration_h
            )
            total_revenue += period_revenue
            total_power_used += irrigation_kwh + cooling_kwh
            schedule.append(
                {
                    "period": p,
                    "solar_kw": period_solar,
                    "irrigation": bool(irrigation_on),
                    "cooling": bool(cooling_on),
                    "grid_export": bool(export_on),
                    "irrigation_kwh": irrigation_kwh,
                    "cooling_kwh": cooling_kwh,
                    "export_kwh": export_kwh,
                    "period_revenue_usd": period_revenue,
                }
            )
        total_solar_kwh = float(
            np.sum(power_available) * period_duration_h / self.n_periods * self.n_periods
        )
        return {
            "schedule": schedule,
            "total_revenue_usd": total_revenue,
            "total_power_used_kwh": total_power_used,
            "total_solar_kwh": total_solar_kwh,
            "utilization_fraction": total_power_used / max(total_solar_kwh, 1e-6),
        }

    def _classical_qaoa_approximation(
        self, h: np.ndarray, J: np.ndarray, solar_kw: float
    ) -> np.ndarray:
        energy = h.copy()
        x = np.zeros(self.n_vars)
        for i in range(self.n_vars):
            local_field = energy[i] + np.sum(J[i, :] * x)
            x[i] = 1.0 if local_field < 0 else 0.0
        if solar_kw < 0.5:
            x[1] = 0.0
        total_load = x[0] * IRRIGATION_PUMP_POWER_KW + x[1] * REFRIGERATION_POWER_KW
        if total_load > solar_kw:
            if x[0] > 0 and IRRIGATION_PUMP_POWER_KW > solar_kw:
                x[0] = 0.0
            elif x[1] > 0:
                x[1] = 0.0
        return x

    def _pennylane_qaoa(self, h: np.ndarray, J: np.ndarray, solar_kw: float) -> np.ndarray:
        qml = self._qml
        dev = self._dev

        gamma = np.pi / 4.0
        beta = np.pi / 6.0
        n_layers = self.p

        @qml.qnode(dev)
        def _circuit():
            for w in range(self.n_vars):
                qml.Hadamard(wires=w)
            for _ in range(n_layers):
                for i in range(self.n_vars):
                    qml.RZ(-2.0 * gamma * h[i], wires=i)
                for i in range(self.n_vars):
                    for j in range(i + 1, self.n_vars):
                        if abs(J[i, j]) > 1e-9:
                            qml.CNOT(wires=[i, j])
                            qml.RZ(-2.0 * gamma * J[i, j], wires=j)
                            qml.CNOT(wires=[i, j])
                for w in range(self.n_vars):
                    qml.RX(2.0 * beta, wires=w)
            return qml.counts()

        counts = _circuit()
        best_bitstring = max(counts, key=counts.get) if counts else "000"
        x = np.array([int(b) for b in best_bitstring[: self.n_vars]])
        total_load = x[0] * IRRIGATION_PUMP_POWER_KW + x[1] * REFRIGERATION_POWER_KW
        if total_load > solar_kw:
            if x[0] > 0 and IRRIGATION_PUMP_POWER_KW > solar_kw:
                x[0] = 0.0
            elif x[1] > 0:
                x[1] = 0.0
        return x
