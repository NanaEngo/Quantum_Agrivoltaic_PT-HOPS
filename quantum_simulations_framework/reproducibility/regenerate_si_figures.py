"""
Regenerate SI figures with complete Phase 2 data.
Usage: python regenerate_si_figures.py
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.visualization.theme import apply_jpcl_theme, get_color_palette
from src.core.constants import DEFAULT_DPI, PREVIEW_DPI

# Output directory — configurable via QSF_OUTPUT_DIR env var (for server deployment)
_DEFAULT_OUTPUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "Redac_Paper1", "JPCL_Submission_Package_2026-06-20", "Figures"
))
OUTPUT_DIR = os.environ.get("QSF_OUTPUT_DIR", _DEFAULT_OUTPUT)
os.makedirs(OUTPUT_DIR, exist_ok=True)

apply_jpcl_theme()
colors = get_color_palette()

def save_fig(fig, name):
    pdf = os.path.join(OUTPUT_DIR, f"{name}.pdf")
    png = os.path.join(OUTPUT_DIR, f"{name}.png")
    fig.savefig(pdf, dpi=DEFAULT_DPI, bbox_inches="tight")
    fig.savefig(png, dpi=PREVIEW_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {pdf}")
    return pdf

def generate_temperature_dynamics():
    """Figure S3: η(T) with full 6-point dataset."""
    T = np.array([285, 290, 295, 300, 305, 310])
    eta = np.array([0.543, 0.387, 0.386, 0.381, 0.374, 0.391])
    eta_err = np.array([0.04, 0.04, 0.04, 0.04, 0.04, 0.04])

    fig, ax = plt.subplots(1, 1, figsize=(5.5, 4))
    ax.errorbar(T, eta, yerr=eta_err, fmt="o-", color=colors[0],
                capsize=4, capthick=1.5, elinewidth=1.5, markersize=7,
                linewidth=2.0)
    ax.fill_between(T, eta - eta_err, eta + eta_err, alpha=0.15, color=colors[0])
    ax.axvspan(285, 310, alpha=0.08, color="green", label="Physiological range (285--310 K)")
    ax.axhline(0.38, color="gray", linestyle="--", linewidth=1, alpha=0.5,
               label=r"$\eta \approx 0.38$ (plateau)")
    ax.set_xlabel("Temperature [K]", fontsize=11)
    ax.set_ylabel(r"Relative Enhancement $\eta$", fontsize=11)
    ax.set_title(r"Temperature Dependence of $\eta$ ($L=7$, $N=15$)", fontsize=12)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    save_fig(fig, "SI_temperature_dynamics")


def generate_filter_sweep():
    """Figure S5: filter sweep with all 7 configurations + broadband reference."""
    labels = [
        "[770,820] nm\n100 cm$^{-1}$",
        "[730,820] nm\n100 cm$^{-1}$",
        "[750,800] nm\n100 cm$^{-1}$",
        "BW 50 cm$^{-1}$",
        "BW 200 cm$^{-1}$",
        "700 nm single",
        "850 nm single",
    ]
    phi_filt = np.array([0.7274, 0.7274, 0.0181, 0.7136, 0.7671, 0.0195, 0.0195])
    phi_broad = 0.4653
    eta_vals = (phi_filt - phi_broad) / phi_broad
    x = np.arange(len(labels))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    green = "#009E73"
    red = "#D55E00"
    bar_colors = [green] * len(eta_vals)
    bar_colors[2] = red
    bar_colors[5] = red
    bar_colors[6] = red

    bars = ax1.bar(x, eta_vals, width=0.55, color=bar_colors, edgecolor="black", linewidth=0.5)
    ax1.axhline(0, color="gray", linewidth=0.5)
    for val, bar in zip(eta_vals, bars):
        y_pos = bar.get_height()
        offset = 0.04 if y_pos >= 0 else -0.08
        ax1.text(bar.get_x() + bar.get_width()/2, y_pos + offset,
                 f"{val:.2f}", ha="center", va="bottom" if y_pos >= 0 else "top",
                 fontsize=9, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8)
    ax1.tick_params(axis="x", rotation=25)
    ax1.set_ylabel(r"Relative Enhancement $\eta$", fontsize=11)
    ax1.set_title("(a) Spectral Filter Comparison", loc="left", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3, axis="y")

    broad_line = np.full_like(x, phi_broad)
    ax2.plot(x, broad_line, "--", color="gray", linewidth=1.5,
             label=rf"Broadband ($\Phi$={phi_broad})")
    ax2.plot(x, phi_filt, "o-", color=colors[0], markersize=7, linewidth=1.5,
             label="Filtered", markerfacecolor=colors[0])
    for i in range(len(x)):
        ax2.vlines(i, phi_broad, phi_filt[i], color=bar_colors[i], linewidth=1.2, alpha=0.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8)
    ax2.tick_params(axis="x", rotation=25)
    ax2.set_ylabel(r"$\Phi_{\mathrm{FT}}$ (Site 3 population)", fontsize=11)
    ax2.set_title("(b) Target Population Comparison", loc="left", fontsize=12, fontweight="bold")
    ax2.legend(loc="lower right", frameon=False, fontsize=8)
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    save_fig(fig, "SI_filter_sweep")


def generate_convergence_hierarchy():
    """Figure S6: η(L) convergence with SBD=3 hierarchy depths."""
    L_vals = np.array([6, 7, 8])
    phi_filt = np.array([0.7172, 0.7274, 0.7543])
    phi_broad = np.array([0.5884, 0.5234, 0.5442])
    eta_vals = (phi_filt - phi_broad) / phi_broad

    fig, ax = plt.subplots(1, 1, figsize=(5, 3.5))
    ax.plot(L_vals, eta_vals, "o-", color=colors[0], markersize=8,
            linewidth=2.0, markerfacecolor=colors[0])
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.set_xlabel("Hierarchy Depth $L$", fontsize=11)
    ax.set_ylabel(r"Relative Enhancement $\eta$", fontsize=11)
    ax.set_title("Hierarchy Depth Convergence ($N=5$)", fontsize=12)
    ax.set_xticks(L_vals)
    ax.grid(True, alpha=0.3)
    for i, eta in enumerate(eta_vals):
        ax.annotate(f"{eta:.4f}", (L_vals[i], eta_vals[i]),
                    textcoords="offset points", xytext=(0, -18),
                    ha="center", va="top", fontsize=9, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, "convergence_hierarchy")


if __name__ == "__main__":
    print("Regenerating SI figures...")
    print(f"Output directory: {OUTPUT_DIR}")
    generate_temperature_dynamics()
    generate_filter_sweep()
    generate_convergence_hierarchy()
    print("Done.")
