"""Publication-quality figure generator for Paper 2 (Nature Energy).

Produces 3-panel figures matching the manuscript caption descriptions:
  Figure 1: 3 panels — (a) Energy level diagram, (b) Population dynamics, (c) RC yield
  Figure 2: 3 panels — (a) Floquet Stark, (b) OMIT, (c) SERS spectrum
  Figure 3: 3 panels — (a) ET comparison, (b) NEB comparison, (c) Cooperative payback
"""

from __future__ import annotations

import os

import h5py
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from ..config_loader import ConfigModel, load_config
from ..logging_config import get_logger

logger = get_logger("plot_utils")

# ── Colour palette ─────────────────────────────────────────────────────────
COLORS = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728", "#9467bd", "#8c564b"]

# ── FMO constants (imported from src/constants.py to avoid duplication) ────
from ..constants import (
    FMO_COUPLINGS_CM,
    FMO_NSITES,
    FMO_SITE_ENERGIES_CM,
    N_DIM_DRESSED,
    PLASMON_COUPLING_SITES,
    NPoM_REFERENCE_COUPLING_CM,
    NPoM_REFERENCE_MODE_VOLUME_NM3,
)

MODE_VOLUME_NM3 = 0.8  # Default production mode volume


def _compute_dressed_eigenvalues() -> np.ndarray:
    """Build the 9×9 dressed Hamiltonian and return real eigenvalues (cm⁻¹)."""
    H = np.zeros((N_DIM_DRESSED, N_DIM_DRESSED), dtype=float)
    for i in range(FMO_NSITES):
        H[i, i] = FMO_SITE_ENERGIES_CM[i]
    for (i, j), val in FMO_COUPLINGS_CM.items():
        H[i, j] = val
        H[j, i] = val
    g0 = NPoM_REFERENCE_COUPLING_CM * np.sqrt(NPoM_REFERENCE_MODE_VOLUME_NM3 / MODE_VOLUME_NM3)
    H[FMO_NSITES, FMO_NSITES] = 12500.0
    for site in PLASMON_COUPLING_SITES:
        H[site, FMO_NSITES] = g0
        H[FMO_NSITES, site] = g0
    return np.linalg.eigvalsh(H)


class Paper2FigureGenerator:
    """Generates publication-quality 3-panel figures for Paper 2."""

    def __init__(
        self, output_dir: str = "./Graphics", config: ConfigModel | str | None = None
    ) -> None:
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        if config is None:
            # Try to auto-locate parameters.yaml relative to this source file
            src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            project_root = os.path.dirname(src_dir)
            config_path = os.path.join(project_root, "parameters.yaml")
            try:
                self.config = load_config(config_path)
            except Exception as e:
                logger.warning("Could not auto-load parameters.yaml: %s", e)
                self.config = None
        elif isinstance(config, str):
            try:
                self.config = load_config(config)
            except Exception as e:
                logger.warning("Could not load config from %s: %s", config, e)
                self.config = None
        else:
            self.config = config

    def _compute_cooperative_payback(self) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
        """Compute cooperative payback curves using the internal configuration."""
        if not self.config:
            return None

        cfg = self.config
        capex = cfg.lca.default_capex
        annual_revenue = cfg.lca.default_annual_revenue
        annual_opex = cfg.lca.default_annual_opex
        training_opex = cfg.lca.cooperative.annual_training_opex_usd
        cleaning_opex = cfg.lca.cooperative.annual_cleaning_opex_usd
        total_opex = annual_opex + training_opex + cleaning_opex

        subsidy_rates = np.linspace(0, 0.5, 51)
        coop_sizes = [1, 3, 5, 10]

        payback_matrix = np.zeros((len(coop_sizes), len(subsidy_rates)))
        for i, n_coop in enumerate(coop_sizes):
            for j, s in enumerate(subsidy_rates):
                net_capex = capex * (1.0 - s) / n_coop
                net_cashflow = (annual_revenue - total_opex) / n_coop
                payback_matrix[i, j] = net_capex / net_cashflow if net_cashflow > 0 else np.inf

        return subsidy_rates, np.array(coop_sizes), payback_matrix

    # ── Figure 1: Quantum Dynamics (3 panels) ──────────────────────────────

    def plot_figure_1_quantum_dynamics(self, h5_file_path: str) -> str:
        """3-panel figure: (a) Energy level diagram, (b) Population dynamics, (c) RC yield."""
        if not os.path.exists(h5_file_path):
            raise FileNotFoundError(f"HDF5 dataset {h5_file_path} not found.")

        with h5py.File(h5_file_path, "r") as f:
            populations = f["dynamics/populations"][:]
            rc_yield = f["dynamics/rc_yield"][:]
            dt_fs = f["dynamics"].attrs.get("time_step_fs", 0.2)

        n_steps = len(populations)
        time_pts = np.arange(n_steps) * dt_fs

        fig, (ax1, ax2, ax3) = plt.subplots(
            1, 3, figsize=(16, 5), gridspec_kw={"width_ratios": [1, 2, 2]}
        )

        # Panel (a): Energy level diagram
        eigvals = _compute_dressed_eigenvalues()
        for i, ev in enumerate(eigvals):
            ax1.hlines(y=i, xmin=0, xmax=1, linewidth=2.5, color=COLORS[i % len(COLORS)])
            ax1.text(1.02, i, f"  {ev:.0f} cm⁻¹", va="center", fontsize=7)
        ax1.axhspan(-0.5, FMO_NSITES - 0.5, alpha=0.08, color="#4C72B0", label="FMO sites")
        ax1.axhspan(
            FMO_NSITES - 0.5, N_DIM_DRESSED - 0.5, alpha=0.08, color="#DD8452", label="Plasmon mode"
        )
        ax1.set_ylim(-0.5, N_DIM_DRESSED - 0.5)
        ax1.set_xlim(0, 1.3)
        ax1.set_yticks([])
        ax1.set_xticks([])
        ax1.set_title("(a) Dressed Hamiltonian", loc="left", fontweight="bold")
        ax1.legend(frameon=False, fontsize=8, loc="lower right")

        # Panel (b): Population dynamics
        n_sites = populations.shape[1]
        for i in range(n_sites):
            label = f"Site {i + 1}" if i < FMO_NSITES else "Plasmon"
            ax2.plot(
                time_pts,
                populations[:, i],
                label=label,
                linewidth=1.8,
                color=COLORS[i % len(COLORS)],
            )
        ax2.set_xlabel("Time (fs)", fontweight="bold")
        ax2.set_ylabel("Population Probability", fontweight="bold")
        ax2.set_title("(b) Excitonic Energy Transfer", loc="left", fontweight="bold")
        ax2.grid(True, alpha=0.3)
        ax2.legend(ncol=2, frameon=False, fontsize=8)

        # Panel (c): RC Trapping Yield
        ax3.plot(time_pts, rc_yield, color="#d62728", linewidth=2.5, label=r"$\Phi_{\rm FT}$")
        final_yield = float(rc_yield[-1])
        ax3.axhline(y=final_yield, color="#d62728", linestyle="--", alpha=0.5)
        ax3.annotate(
            f"$\\Phi_{{\\rm FT}} = {final_yield:.4f}$",
            xy=(time_pts[-1] * 0.65, final_yield * 1.08),
            fontsize=10,
            fontweight="bold",
            color="#d62728",
        )
        ax3.set_xlabel("Time (fs)", fontweight="bold")
        ax3.set_ylabel("Trapping Yield", fontweight="bold")
        ax3.set_title("(c) Reaction Center Energy Capture", loc="left", fontweight="bold")
        ax3.grid(True, alpha=0.3)
        ax3.legend(frameon=False)

        plt.tight_layout()
        out_path = os.path.join(self.output_dir, "Figure1_Quantum_Dynamics.png")
        plt.savefig(out_path, dpi=600, bbox_inches="tight")
        plt.close()
        logger.info("Figure 1 saved: %s (%d steps, dt=%.1f fs)", out_path, n_steps, dt_fs)
        return out_path

    # ── Figure 2: SERS Readout (3 panels) ──────────────────────────────────

    def plot_figure_2_sers_readout(self, raman_spectrum: dict) -> str:
        """3-panel figure: (a) Floquet Stark, (b) OMIT, (c) SERS spectrum."""
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))

        # Panel (a): Floquet Stark detuning
        flux = np.linspace(0, 1200, 200)
        V0 = 0.05
        I_threshold = 800.0
        V_eff = V0 / (1.0 + np.exp(-(flux - I_threshold) / 30.0))
        V_eff -= V_eff[0]
        ax1.plot(flux, V_eff, color="#4C72B0", linewidth=2.5)
        ax1.axvline(
            x=I_threshold,
            color="gray",
            linestyle="--",
            alpha=0.5,
            label=f"Threshold ({I_threshold} W/m²)",
        )
        ax1.fill_between(flux, 0, V_eff, alpha=0.15, color="#4C72B0")
        ax1.set_xlabel("Solar Flux (W/m²)", fontweight="bold")
        ax1.set_ylabel("Stark Detuning (eV)", fontweight="bold")
        ax1.set_title("(a) Floquet Stark Detuning", loc="left", fontweight="bold")
        ax1.grid(True, alpha=0.3)
        ax1.legend(frameon=False, fontsize=8)

        # Panel (b): OMIT transmission
        T0 = 1.0
        I_sat = 800.0
        T_omit = T0 / (1.0 + flux / I_sat)
        ax2.plot(flux, T_omit, color="#DD8452", linewidth=2.5)
        ax2.axhline(y=1.0, color="gray", linestyle=":", alpha=0.4)
        ax2.axvline(x=I_sat, color="gray", linestyle="--", alpha=0.5, label=f"I_sat ({I_sat} W/m²)")
        ax2.fill_between(flux, 0, T_omit, alpha=0.15, color="#DD8452")
        ax2.set_xlabel("Solar Flux (W/m²)", fontweight="bold")
        ax2.set_ylabel("Normalised Transmission T/T₀", fontweight="bold")
        ax2.set_title("(b) OMIT Modulation", loc="left", fontweight="bold")
        ax2.grid(True, alpha=0.3)
        ax2.legend(frameon=False, fontsize=8)

        # Panel (c): SERS spectrum
        mode_labels = [
            "180 cm⁻¹\n(Franck-Condon)",
            "740 cm⁻¹\n(Ring def.)",
            "1145 cm⁻¹\n(C-C stretch)",
            "1435 cm⁻¹\n(2,4,5-T)",
            "CQD Pb²⁺\n(Fluor.)",
        ]
        keys = ["180_cm", "740_cm", "1145_cm", "1435_cm", "cqd_pb2"]
        intensities = [raman_spectrum.get(k, 0.0) for k in keys]
        bar_colors = ["#4C72B0", "#4C72B0", "#4C72B0", "#DD8452", "#937860"]
        bars = ax3.bar(
            mode_labels, intensities, color=bar_colors, edgecolor="black", width=0.55, alpha=0.85
        )

        max_int = max(intensities) if intensities else 1.0
        y_off = max_int * 0.03
        for bar_i, val in zip(bars, intensities, strict=False):
            if val < 0.001:
                ax3.annotate(
                    f"{val:.4f}",
                    xy=(bar_i.get_x() + bar_i.get_width() / 2, val + 0.0001),
                    xytext=(0, 35),
                    textcoords="offset points",
                    ha="center",
                    fontweight="bold",
                    fontsize=7,
                    arrowprops={"arrowstyle": "->", "color": "gray", "lw": 0.6},
                )
            else:
                ax3.text(
                    bar_i.get_x() + bar_i.get_width() / 2,
                    val + y_off,
                    f"{val:.3f}",
                    ha="center",
                    fontweight="bold",
                    fontsize=8,
                )

        ax3.annotate(
            "LOD = 1 nM",
            xy=(3, intensities[3]),
            fontsize=7,
            color="#DD8452",
            fontweight="bold",
            xytext=(30, 8),
            textcoords="offset points",
            ha="center",
            arrowprops={"arrowstyle": "->", "color": "#DD8452", "lw": 0.6},
        )
        ax3.annotate(
            "LOD = 31.8 nM",
            xy=(4, intensities[4]),
            fontsize=7,
            color="#937860",
            fontweight="bold",
            xytext=(-30, 8),
            textcoords="offset points",
            ha="center",
            arrowprops={"arrowstyle": "->", "color": "#937860", "lw": 0.6},
        )

        legend_elements = [
            Patch(facecolor="#4C72B0", label="Canonical BChl $a$"),
            Patch(facecolor="#DD8452", label="2,4,5-T (SERS)"),
            Patch(facecolor="#937860", label="Pb$^{2+}$ CQD (fluor.)"),
        ]
        ax3.legend(handles=legend_elements, loc="upper right", frameon=False, fontsize=7)
        ax3.set_ylabel("Intensity / Response (a.u.)", fontweight="bold")
        ax3.set_title("(c) In Situ SERS Diagnostics", loc="left", fontweight="bold")
        ax3.grid(axis="y", alpha=0.3)
        for label in ax3.get_xticklabels():
            label.set_fontsize(7)

        plt.tight_layout()
        out_path = os.path.join(self.output_dir, "Figure2_SERS_Readout.png")
        plt.savefig(out_path, dpi=600, bbox_inches="tight")
        plt.close()
        logger.info(
            "Figure 2 saved: %s (peaks: %s)",
            out_path,
            {k: f"{v:.4f}" for k, v in raman_spectrum.items() if k != "stress_markers"},
        )
        return out_path

    # ── Figure 3: LCA / NEB Comparison (3 panels) ──────────────────────────

    def plot_figure_3_lca_neb(
        self,
        scenario_a: dict,
        scenario_b: dict,
        scenario_c: dict,
        *,
        et_open_field: float = 4.5,
        et_smart_shield: float = 3.2,
        subsidy_rates: np.ndarray | None = None,
        payback_matrix: np.ndarray | None = None,
        coop_sizes: np.ndarray | None = None,
    ) -> str:
        """3-panel figure: (a) Water savings, (b) NEB comparison, (c) Cooperative payback."""
        fig, (ax1, ax2, ax3) = plt.subplots(
            1, 3, figsize=(16, 5), gridspec_kw={"width_ratios": [1, 1.6, 1.6]}
        )

        # Panel (a): Water savings (ET comparison)
        et_labels = ["Open Field", "OPV Smart\nShield"]
        et_values = [et_open_field, et_smart_shield]
        et_colors = ["#d62728", "#2ca02c"]
        bars_et = ax1.bar(
            et_labels, et_values, color=et_colors, edgecolor="black", width=0.45, alpha=0.85
        )
        for bar_i, val in zip(bars_et, et_values, strict=False):
            ax1.text(
                bar_i.get_x() + bar_i.get_width() / 2,
                val + 0.1,
                f"{val:.1f} mm/day",
                ha="center",
                fontweight="bold",
                fontsize=9,
                color=bar_i.get_facecolor(),
            )
        reduction = (et_open_field - et_smart_shield) / et_open_field * 100
        ax1.annotate(
            f"-{reduction:.0f}%",
            xy=(0.5, (et_open_field + et_smart_shield) / 2),
            fontsize=11,
            fontweight="bold",
            color="#2ca02c",
            ha="center",
            xytext=(0.5, et_open_field + 0.3),
            xycoords="data",
            textcoords="data",
            arrowprops={"arrowstyle": "<->", "color": "#2ca02c", "lw": 1.5},
        )
        ax1.set_ylabel("Evapotranspiration ET$_c$ (mm/day)", fontweight="bold")
        ax1.set_title("(a) Water Savings", loc="left", fontweight="bold")
        ax1.grid(axis="y", alpha=0.3)

        # Panel (b): NEB comparison (twin-axis)
        scenarios = [
            "Scenario A\n(Quantum OPV)",
            "Scenario B\n(Static PV)",
            "Scenario C\n(Open Field)",
        ]
        carbon_avoided = [
            scenario_a["net_benefit_co2_kg"],
            scenario_b["net_benefit_co2_kg"],
            scenario_c["net_benefit_co2_kg"],
        ]
        biomass = [
            scenario_a["effective_biomass_kg"],
            scenario_b["effective_biomass_kg"],
            scenario_c["effective_biomass_kg"],
        ]
        x = np.arange(len(scenarios))
        width = 0.35
        ax2b = ax2.twinx()
        ax2.bar(
            x - width / 2,
            carbon_avoided,
            width,
            label="Carbon Avoided (kg CO$_2$e)",
            color=COLORS[0],
            alpha=0.85,
        )
        ax2b.bar(
            x + width / 2, biomass, width, label="Crop Biomass (kg)", color=COLORS[1], alpha=0.85
        )
        for i, val in enumerate(carbon_avoided):
            ax2.text(
                i - width / 2,
                val + max(carbon_avoided) * 0.02,
                f"{val:.1f}",
                ha="center",
                fontweight="bold",
                fontsize=8,
                color=COLORS[0],
            )
        for i, val in enumerate(biomass):
            ax2b.text(
                i + width / 2,
                val + max(biomass) * 0.02,
                f"{val:.2f}",
                ha="center",
                fontweight="bold",
                fontsize=8,
                color=COLORS[1],
            )
        ax2.set_ylabel(
            "Avoided Emissions (kg CO$_2$e / m$^2$ yr)", color=COLORS[0], fontweight="bold"
        )
        ax2.tick_params(axis="y", labelcolor=COLORS[0])
        ax2b.set_ylabel("Crop Biomass (kg / m$^2$ yr)", color=COLORS[1], fontweight="bold")
        ax2b.tick_params(axis="y", labelcolor=COLORS[1])
        ax2.set_xticks(x)
        ax2.set_xticklabels(scenarios, fontweight="bold")
        ax2.set_title("(b) NEB Scenario Comparison", loc="left", fontweight="bold")
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2b.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper right", frameon=False, fontsize=8)

        # Panel (c): Cooperative payback
        if subsidy_rates is None or payback_matrix is None or coop_sizes is None:
            curves = self._compute_cooperative_payback()
            if curves is not None:
                subsidy_rates, coop_sizes, payback_matrix = curves

        if subsidy_rates is not None and payback_matrix is not None and coop_sizes is not None:
            coop_colors = ["#d62728", "#ff7f0e", "#2ca02c", "#4C72B0"]
            for i, n_coop in enumerate(coop_sizes):
                ax3.plot(
                    subsidy_rates * 100,
                    payback_matrix[i, :],
                    label=f"{n_coop} member{'s' if n_coop > 1 else ''}",
                    color=coop_colors[i % len(coop_colors)],
                    linewidth=2.0,
                )
            ref_subsidy = 30.0
            ref_coop = 5
            if ref_coop in list(coop_sizes):
                ref_idx = list(coop_sizes).index(ref_coop)
                ref_payback = np.interp(
                    ref_subsidy, subsidy_rates * 100, payback_matrix[ref_idx, :]
                )
                ax3.plot(ref_subsidy, ref_payback, "o", color="#2ca02c", markersize=8, zorder=5)
                ax3.annotate(
                    f"5 members, 30%\\n= {ref_payback:.2f} yr",
                    xy=(ref_subsidy, ref_payback),
                    xytext=(ref_subsidy + 8, ref_payback + 0.8),
                    fontsize=8,
                    fontweight="bold",
                    color="#2ca02c",
                    arrowprops={"arrowstyle": "->", "color": "#2ca02c", "lw": 0.8},
                )
            ax3.legend(frameon=False, fontsize=8)
        else:
            # Fallback: simple payback bar chart
            for sc, label, color in [
                (scenario_a, "A", COLORS[0]),
                (scenario_b, "B", COLORS[1]),
                (scenario_c, "C", COLORS[2]),
            ]:
                payback = sc.get("payback_yr", 0.0)
                ax3.bar(label, payback, color=color, alpha=0.85, edgecolor="black")

        ax3.set_xlabel(
            "Blended-Finance Subsidy Rate (%)" if subsidy_rates is not None else "Scenario",
            fontweight="bold",
        )
        ax3.set_ylabel("Payback Period (yr)", fontweight="bold")
        ax3.set_title("(c) Cooperative Payback", loc="left", fontweight="bold")
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()
        out_path = os.path.join(self.output_dir, "Figure3_LCA_NEB_Comparison.png")
        plt.savefig(out_path, dpi=600, bbox_inches="tight")
        plt.close()
        logger.info("Figure 3 saved: %s", out_path)
        return out_path
