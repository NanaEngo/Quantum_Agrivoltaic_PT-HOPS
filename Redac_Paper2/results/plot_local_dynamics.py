import os

import h5py
import matplotlib.pyplot as plt
import numpy as np


def generate_si_population_dynamics():
    output_dir = "figures"
    os.makedirs(output_dir, exist_ok=True)

    files = [
        (" (a)  $V = 0.2$ nm$^3$ ($g_0 = 268.3$ cm$^{-1}$)", "V0.2_data.h5"),
        (" (b)  $V = 0.4$ nm$^3$ ($g_0 = 189.7$ cm$^{-1}$)", "V0.4_data.h5"),
        (" (c)  $V = 0.6$ nm$^3$ ($g_0 = 154.9$ cm$^{-1}$)", "V0.6_data.h5"),
        (" (d)  $V = 0.8$ nm$^3$ ($g_0 = 134.1$ cm$^{-1}$)", "V0.8_data.h5"),
        (" (e)  $V = 1.2$ nm$^3$ ($g_0 = 109.5$ cm$^{-1}$)", "V1.2_data.h5"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(15, 9), sharey=True, sharex=True)
    fig.patch.set_facecolor("#ffffff")

    axes_flat = axes.flatten()

    # 5000 steps * 0.5 fs = 2500 fs = 2.5 ps
    time = np.linspace(0, 2500, 5000)

    lines_for_legend = []
    labels_for_legend = []

    colors_fmo = plt.cm.plasma(np.linspace(0.1, 0.85, 7))

    for idx, (label, filename) in enumerate(files):
        ax = axes_flat[idx]
        if not os.path.exists(filename):
            print(f"File {filename} not found, skipping...")
            ax.set_title(f"{label} (Data Pending)", fontsize=13, fontweight="bold")
            continue

        with h5py.File(filename, "r") as f:
            pops = f["dynamics/populations"][:]

        # Plot 7 FMO sites
        for i in range(7):
            (line,) = ax.plot(
                time,
                pops[:, i],
                color=colors_fmo[i],
                alpha=0.85,
                linewidth=1.5,
                label=f"FMO Site {i + 1}",
            )
            if idx == 0 and len(lines_for_legend) < 7:
                lines_for_legend.append(line)
                labels_for_legend.append(f"FMO Site {i + 1}")

        # Reaction Center & NPoM
        (line_rc,) = ax.plot(
            time, pops[:, 7], label="Reaction Center (RC)", color="black", linewidth=2.2
        )
        (line_npom,) = ax.plot(
            time,
            pops[:, 8],
            label="NPoM Plasmon Mode",
            color="#d62728",
            linestyle="--",
            linewidth=2.2,
        )

        if idx == 0:
            lines_for_legend.append(line_rc)
            labels_for_legend.append("Reaction Center (RC)")
            lines_for_legend.append(line_npom)
            labels_for_legend.append("NPoM Plasmon Mode")

        ax.set_title(label, fontsize=13, fontweight="bold", pad=8)
        ax.set_xlim(0, 2000)
        ax.set_ylim(0, 1.05)
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.set_facecolor("#ffffff")

        if idx >= 3:
            ax.set_xlabel("Time (fs)", fontsize=12, fontweight="bold")
        if idx in [0, 3]:
            ax.set_ylabel("Population", fontsize=12, fontweight="bold")

    # 6th panel (1,2) -> Legend & Summary Box
    ax_leg = axes_flat[5]
    ax_leg.axis("off")
    ax_leg.legend(
        lines_for_legend,
        labels_for_legend,
        loc="center",
        fontsize=11,
        frameon=True,
        facecolor="#f8f9fa",
        edgecolor="#cccccc",
        title="Quantum Dynamics States",
        title_fontsize=12,
    )

    plt.tight_layout()
    out_path = os.path.join(output_dir, "Figure_SI_Population_Dynamics_Local.png")
    plt.savefig(out_path, dpi=600, bbox_inches="tight", facecolor="#ffffff")
    print(f"Figure saved in 2-row layout: {out_path}")


if __name__ == "__main__":
    generate_si_population_dynamics()
