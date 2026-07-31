import matplotlib
import numpy as np

matplotlib.use("Agg")
from pathlib import Path

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

OUT_DIR = Path(
    "/home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper2/Submission_Package_QST_Manuscript/Figures"
)
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Authentic 6-point NPoM Volume Scan Dataset (Table 2 & SI.tex) ───────────────
vols = np.array([0.2, 0.4, 0.6, 0.8, 1.0, 1.2])  # V_mode (nm^3)
g0s = np.array([268.3, 189.7, 154.9, 134.1, 120.0, 109.5])  # Vacuum coupling g0 (cm^-1)
phi_FT = np.array(
    [0.097, 0.183, 0.146, 0.148, 0.159, 0.160]
)  # Local transfer yield \Phi_{FT}^{NPoM}
sigma = np.array([0.0062, 0.0058, 0.0051, 0.0045, 0.0041, 0.0038])  # Standard error (n=20)

# Exact physical area-weighted canopy yield formula:
# \Phi_{global} = 0.01 * \Phi_{FT}^{NPoM} + 0.99 * 0.980
phi_gl = 0.01 * phi_FT + 0.99 * 0.980

# ── Common style (LIGHT THEME for QST Publication Standards) ─────────────────
BG = "#ffffff"
FG = "#000000"
GRID = "#e0e0e0"
C1 = "#1f77b4"
C2 = "#2ca02c"
C3 = "#9467bd"
C4 = "#ff7f0e"


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=10)
    for sp in ax.spines.values():
        sp.set_color(FG)
    ax.grid(True, ls="--", lw=0.5, alpha=0.6, color=GRID)


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE S3 — Authentic 6-Point NPoM Volume Scan (4-panel)
# ═══════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(12, 9), facecolor=BG)
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

# (a) \Phi_FT vs V
ax1 = fig.add_subplot(gs[0, 0])
style_ax(ax1)
ax1.errorbar(
    vols,
    phi_FT,
    yerr=sigma,
    fmt="o-",
    color=C1,
    lw=2.2,
    ms=8,
    mfc=C1,
    mec=FG,
    mew=1.0,
    ecolor=C1,
    elinewidth=1.2,
    capsize=4,
    label=r"$\Phi_{FT}$ (n=20, L=8)",
    zorder=3,
)
ax1.axvspan(0.75, 1.25, alpha=0.15, color=C2, label="Optimal region")
ax1.axvline(x=1.2, color=C2, lw=1.3, ls=":", alpha=0.7)

# Annotations
ax1.annotate(
    "max\n0.160",
    xy=(1.2, 0.160),
    xytext=(1.05, 0.130),
    fontsize=9,
    color=C2,
    ha="center",
    arrowprops={"arrowstyle": "->", "color": C2, "lw": 1.1},
)
ax1.annotate(
    "transient\npeak 0.183",
    xy=(0.4, 0.183),
    xytext=(0.53, 0.198),
    fontsize=8.5,
    color=C1,
    ha="center",
    arrowprops={"arrowstyle": "->", "color": C1, "lw": 1.0},
)
ax1.annotate(
    "over-\ncoupled",
    xy=(0.2, 0.097),
    xytext=(0.18, 0.128),
    fontsize=8.5,
    color=C4,
    ha="center",
    arrowprops={"arrowstyle": "->", "color": C4, "lw": 1.0},
)
ax1.set_xlabel(r"$V_{\rm mode}$ (nm$^3$)", color=FG, fontsize=11)
ax1.set_ylabel(r"$\Phi_{FT}$", color=FG, fontsize=12)
ax1.set_title("(a) Transfer yield vs. mode volume", color=FG, fontsize=12, pad=6)
ax1.legend(fontsize=9, facecolor=BG, edgecolor=FG, labelcolor=FG, loc="lower right")
ax1.set_xlim(0.05, 1.38)
ax1.set_ylim(0.07, 0.220)

# (b) \Phi_FT vs g0
ax2 = fig.add_subplot(gs[0, 1])
style_ax(ax2)
ax2.errorbar(
    g0s,
    phi_FT,
    yerr=sigma,
    fmt="o-",
    color=C3,
    lw=2.2,
    ms=8,
    mfc=C3,
    mec=FG,
    mew=1.0,
    ecolor=C3,
    elinewidth=1.2,
    capsize=4,
)
ax2.axvspan(105, 140, alpha=0.15, color=C2)
ax2.set_xlabel(r"$g_0$ (cm$^{-1}$)", color=FG, fontsize=11)
ax2.set_ylabel(r"$\Phi_{FT}$", color=FG, fontsize=12)
ax2.set_title(r"(b) Transfer yield vs. vacuum coupling $g_0$", color=FG, fontsize=12, pad=6)
ax2.set_ylim(0.07, 0.220)
ax2.invert_xaxis()
# label points
for v, g, phi in zip(vols, g0s, phi_FT, strict=False):
    ax2.text(g + 4, phi + 0.004, f"V={v}", fontsize=7.5, color="#555555", ha="left")

# (c) \Phi_global vs V
ax3 = fig.add_subplot(gs[1, 0])
style_ax(ax3)
ax3.plot(
    vols,
    phi_gl,
    "s-",
    color=C4,
    lw=2.2,
    ms=8,
    mfc=C4,
    mec=FG,
    mew=1.0,
    label=r"$\Phi_{\rm global} = 0.01\Phi_{FT} + 0.99(0.980)$",
)
ax3.axhline(y=0.9702, color="#555555", lw=1.2, ls="--", alpha=0.8, label="97.02% canopy floor")
ax3.axhline(y=0.9802, color="#d62728", lw=1.0, ls=":", alpha=0.7, label="Upper bound (0.9802)")
ax3.fill_between(vols, 0.9702, phi_gl, alpha=0.15, color=C4)
ax3.set_xlabel(r"$V_{\rm mode}$ (nm$^3$)", color=FG, fontsize=11)
ax3.set_ylabel(r"$\Phi_{\rm global}$", color=FG, fontsize=12)
ax3.set_title("(c) Global photosynthetic yield", color=FG, fontsize=12, pad=6)
ax3.legend(fontsize=9, facecolor=BG, edgecolor=FG, labelcolor=FG, loc="upper right")
ax3.set_xlim(0.05, 1.38)
ax3.set_ylim(0.968, 0.982)
ax3.set_yticks([0.970, 0.972, 0.974, 0.976, 0.978, 0.980, 0.982])

# (d) Yield summary bar chart for all 6 sampled volumes
ax4 = fig.add_subplot(gs[1, 1])
style_ax(ax4)
x = np.arange(len(vols))
width = 0.38
bars1 = ax4.bar(
    x - width / 2, phi_FT, width, label=r"$\Phi_{FT}$", color=C1, alpha=0.88, edgecolor=FG, lw=0.8
)
bars2 = ax4.bar(
    x + width / 2,
    phi_gl,
    width,
    label=r"$\Phi_{\rm global}$",
    color=C4,
    alpha=0.88,
    edgecolor=FG,
    lw=0.8,
)
ax4.set_xticks(x)
ax4.set_xticklabels([f"V={v}" for v in vols], rotation=30, fontsize=9.5, color=FG)
ax4.set_ylabel("Yield", color=FG, fontsize=11)
ax4.set_title("(d) Yield summary — all 6 volumes", color=FG, fontsize=12, pad=6)
ax4.legend(fontsize=9.5, facecolor=BG, edgecolor=FG, labelcolor=FG)
ax4.set_ylim(0, 1.08)
# Value labels on bars
for bar in bars1:
    ax4.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f"{bar.get_height():.3f}",
        ha="center",
        va="bottom",
        fontsize=8,
        color="#105080",
    )
for bar in bars2:
    ax4.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f"{bar.get_height():.3f}",
        ha="center",
        va="bottom",
        fontsize=8,
        color="#a04000",
    )

# Footer
fig.text(
    0.5,
    0.005,
    r"MesoHOPS PT-HOPS/SBD | L=8, K=2, n=20, T=295 K, t$_{\rm max}$=1000 fs — Paper 2 QST",
    ha="center",
    fontsize=9,
    color="#555555",
    style="italic",
)

out3 = OUT_DIR / "Figure_SI_NPoM_VolumeScan_n20.png"
plt.savefig(out3, dpi=600, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Figure S3 successfully regenerated: {out3}")
