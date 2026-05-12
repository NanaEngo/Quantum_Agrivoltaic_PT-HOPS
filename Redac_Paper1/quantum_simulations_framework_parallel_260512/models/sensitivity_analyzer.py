"""
Sensitivity Analysis and Uncertainty Quantification.

This module provides the SensitivityAnalyzer class, designed to evaluate the 
robustness of agrivoltaic performance metrics under parameter variation. 
It supports local sensitivity analysis (varying one parameter at a time) 
and Monte Carlo simulations for global uncertainty quantification, facilitating 
the identification of critical design bottlenecks in quantum-enhanced systems.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.typing import NDArray

# Import required classes
try:
    from src.core.hops_simulator import HopsSimulator
except ImportError:
    try:
        from quantum_simulations_framework.core.hops_simulator import HopsSimulator
    except ImportError:
        try:
            import os
            import sys

            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from src.core.hops_simulator import HopsSimulator
        except ImportError:
            HopsSimulator = None

try:
    from agrivoltaic_coupling_model import AgrivoltaicCouplingModel
except ImportError:
    AgrivoltaicCouplingModel = None

logger = logging.getLogger(__name__)


class SensitivityAnalyzer:
    """
    Orchestrator for sensitivity and uncertainty analysis in agrivoltaic systems.

    This class provides a high-level interface for probing the response of 
    quantum dynamics (coherence, population transfer) and agrivoltaic 
    performance (PCE, ETR) to fluctuations in environmental or physical 
    parameters.

    Parameters
    ----------
    quantum_simulator : Any
        An instance of HopsSimulator or a compatible quantum dynamics solver.
    agrivoltaic_model : Any
        An instance of AgrivoltaicCouplingModel or a compatible model.

    Attributes
    ----------
    quantum_simulator : Any
        The active quantum simulator instance.
    agrivoltaic_model : Any
        The active agrivoltaic model instance.
    param_ranges : Dict[str, Tuple[float, float]]
        Definition of the search space for each sensitivity parameter, 
        mapping parameter names to (min, max) tuples.
    """

    def __init__(self, quantum_simulator, agrivoltaic_model):
        """Initialize the sensitivity analyzer."""
        self.quantum_simulator = quantum_simulator
        self.agrivoltaic_model = agrivoltaic_model
        
        # Use constants for default ranges
        from src.core.constants import (
            DEFAULT_TEMPERATURE, 
            DEFAULT_DEPHASING_RATE,
            SENSITIVITY_TEMP_OFFSET,
            SENSITIVITY_DEPHASING_FACTORS,
            SENSITIVITY_CENTER_RANGE,
            SENSITIVITY_WIDTH_RANGE,
            SENSITIVITY_DUST_RANGE,
        )
        self.param_ranges = {
            "temperature": (
                DEFAULT_TEMPERATURE + SENSITIVITY_TEMP_OFFSET[0], 
                DEFAULT_TEMPERATURE + SENSITIVITY_TEMP_OFFSET[1]
            ),
            "dephasing_rate": (
                DEFAULT_DEPHASING_RATE * SENSITIVITY_DEPHASING_FACTORS[0], 
                DEFAULT_DEPHASING_RATE * SENSITIVITY_DEPHASING_FACTORS[1]
            ),
            "transmission_center": SENSITIVITY_CENTER_RANGE,
            "transmission_width": SENSITIVITY_WIDTH_RANGE,
            "dust_thickness": SENSITIVITY_DUST_RANGE,
        }
        logger.info("SensitivityAnalyzer initialized")

    def local_sensitivity_analysis(
        self, base_params: Dict[str, float], param_name: str, n_points: int = 20
    ) -> Tuple[NDArray, NDArray, NDArray, NDArray]:
        """
        Perform local sensitivity analysis by varying one parameter.
        """
        param_range = self.param_ranges.get(param_name, (0, 1))
        param_values = np.linspace(param_range[0], param_range[1], n_points)
        pce_values, etr_values, coherence_values = [], [], []
        
        from src.core.constants import (
            DEFAULT_TEMPERATURE, 
            DEFAULT_DEPHASING_RATE,
            AUDIT_TIME_WINDOW,
            SENSITIVITY_POINTS_DEFAULT
        )

        for val in param_values:
            current_params = base_params.copy()
            current_params[param_name] = val

            if param_name in ["temperature", "dephasing_rate"]:
                if HopsSimulator is not None:
                    sim = HopsSimulator(
                        self.quantum_simulator.hamiltonian,
                        temperature=current_params.get("temperature", DEFAULT_TEMPERATURE),
                        dephasing_rate=current_params.get("dephasing_rate", DEFAULT_DEPHASING_RATE),
                    )
                    # Use a short representative time window
                    time_points = np.linspace(0, AUDIT_TIME_WINDOW, SENSITIVITY_POINTS_DEFAULT)
                    result = sim.simulate_dynamics(time_points=time_points)
                    # Extract coherences from result
                    cohers = result.get("coherences", np.array([0]))
                    coherence_values.append(np.mean(cohers))
                else:
                    coherence_values.append(0.0)

                # Calculate PCE and ETR
                if self.agrivoltaic_model is not None:
                    # Use dynamic transmission calculation
                    trans = self.agrivoltaic_model.calculate_spectral_transmission()
                    pce_values.append(self.agrivoltaic_model.calculate_opv_efficiency(trans))
                    etr_values.append(self.agrivoltaic_model.calculate_psu_efficiency(trans))
                else:
                    pce_values.append(0.0)
                    etr_values.append(0.0)

            elif param_name == "dust_thickness":
                if hasattr(self.agrivoltaic_model, "update_environmental_conditions"):
                    self.agrivoltaic_model.update_environmental_conditions(dust_thickness=val)
                if self.agrivoltaic_model is not None:
                    trans = self.agrivoltaic_model.calculate_spectral_transmission()
                    pce_values.append(self.agrivoltaic_model.calculate_opv_efficiency(trans))
                    etr_values.append(self.agrivoltaic_model.calculate_psu_efficiency(trans))
                else:
                    pce_values.append(0.0)
                    etr_values.append(0.0)
                coherence_values.append(0.0)
            else:
                pce_values.append(0.0)
                etr_values.append(0.0)
                coherence_values.append(0.0)

        return (
            param_values,
            np.array(pce_values),
            np.array(etr_values),
            np.array(coherence_values),
        )

    def monte_carlo_uncertainty(
        self, n_samples: int = 100, param_uncertainties: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Perform Monte Carlo uncertainty quantification.
        """
        if param_uncertainties is None:
            param_uncertainties = dict.fromkeys(self.param_ranges.keys(), 0.1)

        pce_samples, etr_samples = [], []
        base_params = {key: (val[0] + val[1]) / 2 for key, val in self.param_ranges.items()}

        for _ in range(n_samples):
            sampled_params = {}
            for key, base_val in base_params.items():
                uncertainty = param_uncertainties.get(key, 0.1)
                sampled_value = np.random.normal(base_val, base_val * uncertainty)
                sampled_params[key] = np.clip(
                    sampled_value, self.param_ranges[key][0], self.param_ranges[key][1]
                )

            # Calculate PCE and ETR with sampled parameters
            if self.agrivoltaic_model is not None:
                trans = self.agrivoltaic_model.calculate_spectral_transmission()
                pce_samples.append(self.agrivoltaic_model.calculate_opv_efficiency(trans))
                etr_samples.append(self.agrivoltaic_model.calculate_psu_efficiency(trans))

        pce_samples = np.array(pce_samples)
        etr_samples = np.array(etr_samples)

        return {
            "pce": {
                "mean": np.mean(pce_samples),
                "std": np.std(pce_samples),
                "ci_95": (np.percentile(pce_samples, 2.5), np.percentile(pce_samples, 97.5)),
                "samples": pce_samples,
            },
            "etr": {
                "mean": np.mean(etr_samples),
                "std": np.std(etr_samples),
                "ci_95": (np.percentile(etr_samples, 2.5), np.percentile(etr_samples, 97.5)),
                "samples": etr_samples,
            },
        }

    def comprehensive_sensitivity_report(self, n_points: int = 10) -> Dict[str, Dict[str, Any]]:
        """
        Generate comprehensive sensitivity report for all parameters.
        """
        report = {}
        base_params = {key: (val[0] + val[1]) / 2 for key, val in self.param_ranges.items()}

        param_names = list(self.param_ranges.keys())

        for param_name in param_names:
            param_vals, pce_vals, etr_vals, coh_vals = self.local_sensitivity_analysis(
                base_params, param_name, n_points
            )

            report[param_name] = {
                "param_values": param_vals,
                "pce_values": pce_vals,
                "etr_values": etr_vals,
                "coherence_values": coh_vals,
                "pce_sensitivity": (
                    (pce_vals.max() - pce_vals.min()) / pce_vals.mean()
                    if pce_vals.mean() > 0
                    else 0
                ),
                "etr_sensitivity": (
                    (etr_vals.max() - etr_vals.min()) / etr_vals.mean()
                    if etr_vals.mean() > 0
                    else 0
                ),
            }

        logger.info("Comprehensive sensitivity report generated")
        return report

    def save_sensitivity_results_to_csv(
        self,
        report: Dict[str, Any],
        filename_prefix: str = "sensitivity_analysis",
        output_dir: str = "../simulation_data/",
    ) -> str:
        """
        Save sensitivity analysis results to CSV.
        """
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        rows = []
        for param_name, data in report.items():
            for i, (param_val, pce_val, etr_val, coh_val) in enumerate(
                zip(
                    data["param_values"],
                    data["pce_values"],
                    data["etr_values"],
                    data["coherence_values"],
                    strict=False,
                )
            ):
                rows.append(
                    {
                        "parameter": param_name,
                        "param_value": param_val,
                        "pce": pce_val,
                        "etr": etr_val,
                        "coherence": coh_val,
                        "pce_sensitivity": data["pce_sensitivity"] if i == 0 else None,
                        "etr_sensitivity": data["etr_sensitivity"] if i == 0 else None,
                    }
                )

        df = pd.DataFrame(rows)
        filename = f"{filename_prefix}_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        df.to_csv(filepath, index=False, float_format="%.6e")

        logger.info(f"Sensitivity analysis results saved to {filepath}")
        return filepath

    def plot_sensitivity_results(
        self,
        report: Dict[str, Any],
        filename_prefix: str = "sensitivity_analysis",
        figures_dir: str = "../Graphics/",
    ) -> str:
        """
        Plot sensitivity analysis results.
        """
        os.makedirs(figures_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        n_params = len(report)
        n_cols = 2
        n_rows = (n_params + 1) // 2

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, 4 * n_rows))
        if n_params == 1:
            axes = np.array([axes])
        axes = axes.flatten()

        fig.suptitle("Sensitivity Analysis Results", fontsize=16, fontweight="bold")

        for idx, (param_name, data) in enumerate(report.items()):
            ax = axes[idx]
            ax2 = ax.twinx()

            ax.plot(
                data["param_values"], data["pce_values"], "b-", marker="o", label="PCE", linewidth=2
            )
            ax2.plot(
                data["param_values"], data["etr_values"], "r-", marker="s", label="ETR", linewidth=2
            )

            ax.set_xlabel(param_name.replace("_", " ").title(), fontsize=10)
            ax.set_ylabel("PCE", color="b", fontsize=10)
            ax2.set_ylabel("ETR", color="r", fontsize=10)
            ax.tick_params(axis="y", labelcolor="b")
            ax2.tick_params(axis="y", labelcolor="r")
            ax.grid(alpha=0.3)

            sens_text = (
                f"PCE Sens: {data['pce_sensitivity']:.3f}\nETR Sens: {data['etr_sensitivity']:.3f}"
            )
            ax.text(
                0.02,
                0.98,
                sens_text,
                transform=ax.transAxes,
                fontsize=8,
                verticalalignment="top",
                bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5},
            )

        for idx in range(n_params, len(axes)):
            axes[idx].axis("off")

        plt.tight_layout()

        filename = f"{filename_prefix}_{timestamp}.pdf"
        filepath = os.path.join(figures_dir, filename)
        plt.savefig(filepath, dpi=600, bbox_inches="tight") # JPCL 600 DPI

        png_filename = f"{filename_prefix}_{timestamp}.png"
        png_filepath = os.path.join(figures_dir, png_filename)
        plt.savefig(png_filepath, dpi=300, bbox_inches="tight")

        plt.close()

        logger.info(f"Sensitivity plots saved to {filepath}")
        return filepath


if __name__ == "__main__":
    # Example usage
    logger.info("SensitivityAnalyzer module - example usage")

    class DummySimulator:
        def __init__(self):
            self.hamiltonian = np.eye(7)

    class DummyModel:
        def calculate_spectral_transmission(self, params=None):
            return np.ones(100) * 0.5

        def calculate_opv_efficiency(self, transmission):
            return 0.15

        def calculate_psu_efficiency(self, transmission):
            return 0.8

    dummy_sim = DummySimulator()
    dummy_model = DummyModel()

    analyzer = SensitivityAnalyzer(dummy_sim, dummy_model)

    mc_results = analyzer.monte_carlo_uncertainty(n_samples=50)
    print(f"PCE mean: {mc_results['pce']['mean']:.3f}")
    print(f"ETR mean: {mc_results['etr']['mean']:.3f}")
