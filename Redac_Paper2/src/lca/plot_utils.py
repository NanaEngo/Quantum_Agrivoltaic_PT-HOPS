import os

import h5py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


class Paper2FigureGenerator:
    """
    Generates publication-quality figures for the Quantum Agrivoltaics Paper 2.
    Conforms to Q1 journal formatting standards (600 DPI, tailored color schemes).
    """

    def __init__(self, output_dir: str = "./Graphics"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        # Harmonious Nature Energy styling color palette
        self.colors = ["#1f77b4", "#2ca02c", "#ff7f0e", "#d62728", "#9467bd", "#8c564b"]

    def plot_figure_1_quantum_dynamics(self, h5_file_path: str) -> str:
        """
        Produces Figure 1: Coupled Bio-Organic Polaritonic Interface Dynamics
        - Panel (a): Exciton population transport across the 8 sites + plasmon mode.
        - Panel (b): Trapping yield build-up in the Reaction Center.
        """
        if not os.path.exists(h5_file_path):
            raise FileNotFoundError(f"HDF5 dataset {h5_file_path} not found.")

        with h5py.File(h5_file_path, "r") as f:
            populations = f["dynamics/populations"][:]
            rc_yield = f["dynamics/rc_yield"][:]
            dt_fs = f["dynamics"].attrs.get("time_step_fs", 0.2)

        time_points = np.arange(len(populations)) * dt_fs

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Panel a: Exciton Populations
        for i in range(populations.shape[1]):
            ax1.plot(
                time_points,
                populations[:, i],
                label=f"Site {i + 1}",
                linewidth=1.8,
                color=self.colors[i % len(self.colors)],
            )
        ax1.set_xlabel("Time (fs)", fontweight="bold")
        ax1.set_ylabel("Population Probability", fontweight="bold")
        ax1.set_title("(a) Excitonic Energy Transfer", loc="left", fontweight="bold")
        ax1.grid(True, alpha=0.3)
        ax1.legend(ncol=2, frameon=False)

        # Panel b: Reaction Center Trapping Yield
        ax2.plot(
            time_points,
            rc_yield,
            color="#d62728",
            linewidth=2.5,
            label=r"RC Yield $\Phi_{FT}$",
        )
        ax2.set_xlabel("Time (fs)", fontweight="bold")
        ax2.set_ylabel("Trapping Yield", fontweight="bold")
        ax2.set_title("(b) Reaction Center Energy Capture", loc="left", fontweight="bold")
        ax2.grid(True, alpha=0.3)
        ax2.legend(frameon=False)

        plt.tight_layout()
        out_path = os.path.join(self.output_dir, "Figure1_Quantum_Dynamics.png")
        plt.savefig(out_path, dpi=600)
        plt.close()
        return out_path

    def plot_figure_2_sers_readout(self, raman_spectrum: dict) -> str:
        """
        Produces Figure 2: SERS Diagnostics with Agricultural Target Signatures.
        Bar chart showing 5 signatures: 3 canonical BChl a modes +
        2 agricultural targets (1435 cm-1 2,4,5-T and CdTe/ZnSe CQD Pb2+).
        """
        # ── Mode labels (descriptive) ────────────────────────────────────────
        mode_labels = [
            "180 cm⁻¹\n(Franck-Condon)",
            "740 cm⁻¹\n(Ring def.)",
            "1145 cm⁻¹\n(C-C stretch)",
            "1435 cm⁻¹\n(2,4,5-T pest.)",
            "CQD Pb²⁺\n(Fluor. quench)",
        ]
        keys = ["180_cm", "740_cm", "1145_cm", "1435_cm", "cqd_pb2"]
        intensities = [raman_spectrum.get(k, 0.0) for k in keys]

        # ── Color scheme ────────────────────────────────────────────────────
        # Canonical BChl a modes: steel blue
        # Agricultural target (Raman): terracotta
        # Agricultural target (fluorescence): slate brown
        bar_colors = ["#4C72B0", "#4C72B0", "#4C72B0", "#DD8452", "#937860"]

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(
            mode_labels,
            intensities,
            color=bar_colors,
            edgecolor="black",
            width=0.55,
            alpha=0.85,
        )

        # ── Value annotations on bars ────────────────────────────────────────
        max_int = max(intensities) if intensities else 1.0
        y_offset = max_int * 0.03

        for bar_i, val in zip(bars, intensities, strict=False):
            if val < 0.001:
                # Tiny bar (180 cm-1): annotate with arrow + magnified value
                label = f"{val:.4f}"
                ax.annotate(
                    label,
                    xy=(bar_i.get_x() + bar_i.get_width() / 2, val + 0.0001),
                    xytext=(0, 40),
                    textcoords="offset points",
                    ha="center",
                    fontweight="bold",
                    fontsize=8,
                    arrowprops={"arrowstyle": "->", "color": "gray", "lw": 0.8},
                )
            else:
                ax.text(
                    bar_i.get_x() + bar_i.get_width() / 2,
                    val + y_offset,
                    f"{val:.3f}" if val < 100 else f"{val:.1f}",
                    ha="center",
                    fontweight="bold",
                    fontsize=9,
                )

        # ── LOD annotations for agricultural targets ─────────────────────────
        ax.annotate(
            "LOD = 1 nM",
            xy=(3, intensities[3]),
            fontsize=8,
            color="#DD8452",
            fontweight="bold",
            xytext=(35, 10),
            textcoords="offset points",
            ha="center",
            arrowprops={"arrowstyle": "->", "color": "#DD8452", "lw": 0.8},
        )
        ax.annotate(
            "LOD = 31.8 nM",
            xy=(4, intensities[4]),
            fontsize=8,
            color="#937860",
            fontweight="bold",
            xytext=(-35, 10),
            textcoords="offset points",
            ha="center",
            arrowprops={"arrowstyle": "->", "color": "#937860", "lw": 0.8},
        )

        # ── Legend ───────────────────────────────────────────────────────────
        legend_elements = [
            Patch(facecolor="#4C72B0", label="Canonical BChl $a$ modes"),
            Patch(facecolor="#DD8452", label="2,4,5-T pesticide (SERS)"),
            Patch(facecolor="#937860", label="Pb$^{2+}$ CQD (fluorescence)"),
        ]
        ax.legend(handles=legend_elements, loc="upper right", frameon=False, fontsize=9)

        # ── Labels and grid ──────────────────────────────────────────────────
        ax.set_ylabel(
            "Raman Intensity / Fluorescence Response (a.u.)",
            fontweight="bold",
        )
        ax.set_title(
            "In Situ SERS Diagnostics with Agricultural Target Signatures",
            fontweight="bold",
            pad=15,
        )
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        out_path = os.path.join(self.output_dir, "Figure2_SERS_Readout.png")
        plt.savefig(out_path, dpi=600)
        plt.close()
        return out_path

    def plot_figure_3_lca_neb(self, scenario_a: dict, scenario_b: dict, scenario_c: dict) -> str:
        """
        Produces Figure 3: WEF Nexus Net Ecological Benefit (NEB) Comparison
        Compares Scenarios A, B, and C across Net Carbon Avoided and Effective Biomass.
        """
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

        fig, ax1 = plt.subplots(figsize=(8, 5))

        # Twin axes to plot two different metrics together
        ax2 = ax1.twinx()

        ax1.bar(
            x - width / 2,
            carbon_avoided,
            width,
            label="Net Carbon Avoided (kg CO2e)",
            color="#1f77b4",
            alpha=0.85,
        )
        ax2.bar(
            x + width / 2,
            biomass,
            width,
            label="Effective Crop Biomass (kg)",
            color="#2ca02c",
            alpha=0.85,
        )

        ax1.set_ylabel("Avoided Emissions (kg CO2e / m2 yr)", color="#1f77b4", fontweight="bold")
        ax1.tick_params(axis="y", labelcolor="#1f77b4")
        ax2.set_ylabel(
            "Effective Crop Biomass Harvested (kg / m2 yr)",
            color="#2ca02c",
            fontweight="bold",
        )
        ax2.tick_params(axis="y", labelcolor="#2ca02c")

        ax1.set_xticks(x)
        ax1.set_xticklabels(scenarios, fontweight="bold")
        ax1.set_title("WEF Nexus Life Cycle Assessment Comparison", fontweight="bold", pad=15)

        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", frameon=False)

        plt.tight_layout()
        out_path = os.path.join(self.output_dir, "Figure3_LCA_NEB_Comparison.png")
        plt.savefig(out_path, dpi=600)
        plt.close()
        return out_path
