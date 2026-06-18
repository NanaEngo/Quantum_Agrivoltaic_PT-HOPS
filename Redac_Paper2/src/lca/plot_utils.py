import os
import matplotlib.pyplot as plt
import numpy as np
import h5py


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

        time_points = np.arange(len(populations)) * 5.0  # 5 fs step size

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Panel a: Exciton Populations
        for i in range(populations.shape[1]):
            ax1.plot(
                time_points,
                populations[:, i],
                label=f"Site {i+1}",
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
        ax2.set_title(
            "(b) Reaction Center Energy Capture", loc="left", fontweight="bold"
        )
        ax2.grid(True, alpha=0.3)
        ax2.legend(frameon=False)

        plt.tight_layout()
        out_path = os.path.join(self.output_dir, "Figure1_Quantum_Dynamics.png")
        plt.savefig(out_path, dpi=600)
        plt.close()
        return out_path

    def plot_figure_2_sers_readout(self, raman_spectrum: dict) -> str:
        """
        Produces Figure 2: Non-Destructive SERS Molecular Optomechanical Signature
        Plots characteristic Raman peak intensities corresponding to key FMO vibrational modes.
        """
        fig, ax = plt.subplots(figsize=(6, 4.5))

        modes = list(raman_spectrum.keys())
        intensities = list(raman_spectrum.values())

        ax.bar(
            modes,
            intensities,
            color=self.colors[1],
            edgecolor="black",
            width=0.4,
            alpha=0.85,
        )
        ax.set_ylabel("Raman Intensity (a.u.)", fontweight="bold")
        ax.set_xlabel("Vibrational Mode Signature", fontweight="bold")
        ax.set_title(
            "In Situ Optomechanical SERS Diagnostic", fontweight="bold", pad=15
        )
        ax.grid(axis="y", alpha=0.3)

        # Label values on top of bars
        for i, val in enumerate(intensities):
            ax.text(
                i,
                val + max(intensities) * 0.02,
                f"{val:.4f}",
                ha="center",
                fontweight="bold",
            )

        plt.tight_layout()
        out_path = os.path.join(self.output_dir, "Figure2_SERS_Readout.png")
        plt.savefig(out_path, dpi=600)
        plt.close()
        return out_path

    def plot_figure_3_lca_neb(
        self, scenario_a: dict, scenario_b: dict, scenario_c: dict
    ) -> str:
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

        ax1.set_ylabel(
            "Avoided Emissions (kg CO2e / m2 yr)", color="#1f77b4", fontweight="bold"
        )
        ax1.tick_params(axis="y", labelcolor="#1f77b4")
        ax2.set_ylabel(
            "Effective Crop Biomass Harvested (kg / m2 yr)",
            color="#2ca02c",
            fontweight="bold",
        )
        ax2.tick_params(axis="y", labelcolor="#2ca02c")

        ax1.set_xticks(x)
        ax1.set_xticklabels(scenarios, fontweight="bold")
        ax1.set_title(
            "WEF Nexus Life Cycle Assessment Comparison", fontweight="bold", pad=15
        )

        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", frameon=False)

        plt.tight_layout()
        out_path = os.path.join(self.output_dir, "Figure3_LCA_NEB_Comparison.png")
        plt.savefig(out_path, dpi=600)
        plt.close()
        return out_path
