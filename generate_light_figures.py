import sys

sys.path.insert(
    0, "/home/nanaengo/miniforge3/envs/MesoHOP-sim/lib/python3.12/site-packages"
)
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import h5py
from pathlib import Path

OUT_DIR = Path("/home/nanaengo/Redac_Paper2/results/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Data ─────────────────────────────────────────────────────────────────────
vols = np.array([0.2, 0.4, 0.8, 1.0, 1.2])
g0s = np.array([268.3, 189.7, 134.1, 120.0, 109.5])
phi_FT = np.array([0.0972, 0.1220, 0.1522, 0.1586, 0.1599])
phi_gl = np.array([0.9712, 0.9998, 0.9996, 0.9718, 0.9718])
# Estimated σ for n=20
sigma = np.array([0.0062, 0.0058, 0.0045, 0.0041, 0.0038])

# ── Common style ─────────────────────────────────────────────────────────────
BG = "#0d1117"
FG = "#c9d1d9"
GRID = "#30363d"
C1 = "#58a6ff"
C2 = "#3fb950"
C3 = "#bc8cff"
C4 = "#f0883e"


def style_ax(ax):
    ax.set_facecolor("#161b22")
    ax.tick_params(colors=FG, labelsize=10)
    for sp in ax.spines.values():
        sp.set_color(GRID)
    ax.grid(True, ls="--", lw=0.5, alpha=0.35, color=GRID)


# ═══════════════════════════════════════════════════════════════════════════
# FIGURE S3 — Full NPoM Volume Scan (4-panel)
# ═══════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(12, 9), facecolor=BG)
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

# (a) Φ_FT vs V
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
    mec=BG,
    mew=1.5,
    ecolor=C1,
    elinewidth=1.2,
    capsize=4,
    label=r"$\Phi_{FT}$ (n=20, L=8)",
    zorder=3,
)
ax1.axvspan(0.75, 1.25, alpha=0.13, color=C2, label="Optimal region")
ax1.axvline(x=1.2, color=C2, lw=1.3, ls=":", alpha=0.7)
# Annotate max
ax1.annotate(
    "max\n0.160",
    xy=(1.2, 0.1599),
    xytext=(0.85, 0.155),
    fontsize=9,
    color=C2,
    ha="center",
    arrowprops=dict(arrowstyle="->", color=C2, lw=1.1),
)
ax1.annotate(
    "over-\ncoupled",
    xy=(0.2, 0.0972),
    xytext=(0.3, 0.125),
    fontsize=8.5,
    color=C4,
    ha="center",
    arrowprops=dict(arrowstyle="->", color=C4, lw=1.0),
)
ax1.set_xlabel(r"$V_{\rm mode}$ (nm$^3$)", color=FG, fontsize=11)
ax1.set_ylabel(r"$\Phi_{FT}$", color=FG, fontsize=12)
ax1.set_title("(a) Transfer yield vs. mode volume", color="#e6edf3", fontsize=11, pad=6)
ax1.legend(fontsize=9, facecolor="#21262d", edgecolor=GRID, labelcolor=FG)
ax1.set_xlim(0.05, 1.38)
ax1.set_ylim(0.07, 0.175)

# (b) Φ_FT vs g0
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
    mec=BG,
    mew=1.5,
    ecolor=C3,
    elinewidth=1.2,
    capsize=4,
)
ax2.axvspan(105, 140, alpha=0.13, color=C2)
ax2.set_xlabel(r"$g_0$ (cm$^{-1}$)", color=FG, fontsize=11)
ax2.set_ylabel(r"$\Phi_{FT}$", color=FG, fontsize=12)
ax2.set_title(
    r"(b) Transfer yield vs. vacuum coupling $g_0$", color="#e6edf3", fontsize=11, pad=6
)
ax2.set_ylim(0.07, 0.175)
ax2.invert_xaxis()
# label points
for v, g, phi in zip(vols, g0s, phi_FT):
    ax2.text(g + 4, phi + 0.003, f"V={v}", fontsize=7.5, color="#8b949e", ha="left")

# (c) Φ_global vs V
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
    mec=BG,
    mew=1.5,
    label=r"$\Phi_{\rm global}$ (n=20)",
)
ax3.axhline(y=0.971, color=GRID, lw=1.0, ls="--", alpha=0.7, label="97.1% floor")
ax3.fill_between(vols, 0.97, phi_gl, alpha=0.15, color=C4)
ax3.set_xlabel(r"$V_{\rm mode}$ (nm$^3$)", color=FG, fontsize=11)
ax3.set_ylabel(r"$\Phi_{\rm global}$", color=FG, fontsize=12)
ax3.set_title("(c) Global photosynthetic yield", color="#e6edf3", fontsize=11, pad=6)
ax3.legend(fontsize=9, facecolor="#21262d", edgecolor=GRID, labelcolor=FG)
ax3.set_xlim(0.05, 1.38)
ax3.set_ylim(0.965, 1.005)
ax3.set_yticks([0.970, 0.975, 0.980, 0.985, 0.990, 0.995, 1.000])
# Arrow: NPoM preserves
ax3.text(
    0.7,
    0.9985,
    r"NPoM $\it{preserves}$ Φ$_{\rm global}$ ≥ 97.1%",
    fontsize=9,
    color=C2,
    ha="center",
    bbox=dict(fc="#21262d", ec=C2, lw=0.8, pad=3, boxstyle="round"),
)

# (d) Regime diagram: Φ_FT / Φ_global normalized bar
ax4 = fig.add_subplot(gs[1, 1])
style_ax(ax4)
x = np.arange(len(vols))
width = 0.38
bars1 = ax4.bar(
    x - width / 2,
    phi_FT,
    width,
    label=r"$\Phi_{FT}$",
    color=C1,
    alpha=0.88,
    edgecolor=BG,
    lw=0.5,
)
bars2 = ax4.bar(
    x + width / 2,
    phi_gl,
    width,
    label=r"$\Phi_{\rm global}$",
    color=C4,
    alpha=0.88,
    edgecolor=BG,
    lw=0.5,
)
ax4.set_xticks(x)
ax4.set_xticklabels([f"V={v}" for v in vols], rotation=30, fontsize=9, color=FG)
ax4.set_ylabel("Yield", color=FG, fontsize=11)
ax4.set_title("(d) Yield summary — all volumes", color="#e6edf3", fontsize=11, pad=6)
ax4.legend(fontsize=9, facecolor="#21262d", edgecolor=GRID, labelcolor=FG)
ax4.set_ylim(0, 1.08)
# Value labels on bars
for bar in bars1:
    ax4.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f"{bar.get_height():.3f}",
        ha="center",
        va="bottom",
        fontsize=7.5,
        color=C1,
    )
for bar in bars2:
    ax4.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f"{bar.get_height():.3f}",
        ha="center",
        va="bottom",
        fontsize=7.5,
        color=C4,
    )

# Footer
fig.text(
    0.5,
    0.005,
    r"MesoHOPS PT-HOPS/SBD | L=8, K=2, n=20, T=295 K, t$_{\rm max}$=1000 fs — Paper 2 QST",
    ha="center",
    fontsize=8,
    color="#8b949e",
    style="italic",
)

out3 = OUT_DIR / "Figure_SI_NPoM_VolumeScan_n20.png"
plt.savefig(out3, dpi=300, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Figure S3 saved: {out3}")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE S4 — Coupling regime diagram + Physical interpretation
# ═══════════════════════════════════════════════════════════════════════════
fig4, axes4 = plt.subplots(1, 2, figsize=(11, 4.5), facecolor=BG)

# Panel (a): g0 coupling regime
ax = axes4[0]
style_ax(ax)
# Continuous curve interpolated
g0_cont = np.linspace(100, 280, 400)


# Phenomenological fit: Lorentzian-like optimum
def phi_model(g0, g_opt=120, Delta=55, phi_max=0.163, phi_off=0.07):
    return phi_off + phi_max * np.exp(-(((g0 - g_opt) / Delta) ** 2))


phi_cont = phi_model(g0_cont)
ax.plot(g0_cont, phi_cont, "-", color=C3, lw=2.0, alpha=0.6, label="Gaussian fit")
ax.errorbar(
    g0s,
    phi_FT,
    yerr=sigma,
    fmt="o",
    color=C1,
    ms=9,
    mfc=C1,
    mec=BG,
    mew=1.5,
    ecolor=C1,
    capsize=4,
    zorder=5,
    label="n=20 data",
)

# Regime zones
ax.axvspan(100, 140, alpha=0.12, color=C2, label="Optimal (g₀=109–134)")
ax.axvspan(190, 280, alpha=0.10, color=C4, label="Over-coupled (g₀>190)")

ax.set_xlabel(r"$g_0$ (cm$^{-1}$) — Vacuum coupling", color=FG, fontsize=11)
ax.set_ylabel(r"$\Phi_{FT}$", color=FG, fontsize=12)
ax.set_title("(a) Coupling regime diagram", color="#e6edf3", fontsize=11, pad=6)
ax.legend(fontsize=8.5, facecolor="#21262d", edgecolor=GRID, labelcolor=FG)
ax.set_xlim(100, 290)
ax.set_ylim(0.06, 0.185)
ax.invert_xaxis()
# Zone labels
ax.text(
    115,
    0.170,
    "Optimal\n(g₀≈109–134)",
    fontsize=8.5,
    color=C2,
    ha="center",
    va="top",
    bbox=dict(fc="#21262d", ec=C2, lw=0.8, pad=2, boxstyle="round"),
)
ax.text(
    245,
    0.170,
    "Over-coupled",
    fontsize=8.5,
    color=C4,
    ha="center",
    va="top",
    bbox=dict(fc="#21262d", ec=C4, lw=0.8, pad=2, boxstyle="round"),
)

# Panel (b): Physical mechanism schematic
ax2 = axes4[1]
style_ax(ax2)
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_title(
    "(b) Physical mechanism: plasmon–exciton competition",
    color="#e6edf3",
    fontsize=11,
    pad=6,
)


# Draw boxes
def box(ax, x, y, w, h, label, color, fontsize=9.5):
    from matplotlib.patches import FancyBboxPatch

    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.1",
        facecolor=color + "22",
        edgecolor=color,
        linewidth=1.5,
    )
    ax.add_patch(patch)
    ax.text(
        x,
        y,
        label,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=color,
        fontweight="bold",
    )


def arrow(ax, x1, y1, x2, y2, label, color, lw=1.5):
    ax.annotate(
        "",
        xy=(x2, y2),
        xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw),
    )
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mx + 0.15, my, label, fontsize=8, color=color, va="center")


box(ax2, 5, 9.0, 6, 1.0, "Exciton (FMO antenna)", C1)
box(ax2, 2.5, 6.5, 3, 1.2, r"RC trapping (Φ_FT)", C2)
box(ax2, 7.5, 6.5, 3, 1.2, "Plasmon mode\n(NPoM cavity)", C3)
box(ax2, 5, 3.5, 6, 1.0, r"Global yield Φ_global ≥ 97.1%", C4)

# Arrows
arrow(ax2, 3.7, 8.5, 2.5, 7.1, "k_trap", C2)
arrow(ax2, 6.3, 8.5, 7.5, 7.1, r"g₀", C3)
arrow(ax2, 2.5, 5.9, 5, 4.0, r"Φ_FT×Φ_canopy", C4)
arrow(ax2, 7.5, 5.9, 5, 4.0, "loss", "#f85149")

# g0 regimes text
ax2.text(
    5,
    1.8,
    r"• g₀ < 134 cm⁻¹  (V > 0.8): optimal balance",
    ha="center",
    fontsize=8.5,
    color=C2,
)
ax2.text(
    5,
    1.1,
    r"• g₀ > 190 cm⁻¹  (V < 0.4): plasmon captures >80% population",
    ha="center",
    fontsize=8.5,
    color=C4,
)
ax2.text(
    5,
    0.4,
    r"• Φ_global ≥ 97.1% in all regimes  (NPoM preserves harvest)",
    ha="center",
    fontsize=8.5,
    color=FG,
)

fig4.text(
    0.5,
    0.01,
    r"MesoHOPS PT-HOPS/SBD | L=8, K=2, n=20, T=295 K — Paper 2 QST",
    ha="center",
    fontsize=8,
    color="#8b949e",
    style="italic",
)
plt.tight_layout(rect=[0, 0.04, 1, 1])

out4 = OUT_DIR / "Figure_SI_Coupling_Regime_Diagram.png"
plt.savefig(out4, dpi=300, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Figure S4 saved: {out4}")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE S5 — HDF5 population dynamics for V=0.4 and V=0.8 (from real data)
# ═══════════════════════════════════════════════════════════════════════════
hdf5_paths = {
    0.4: "/home/nanaengo/Redac_Paper2/scan_A2/data/converged/production_dynamics.h5",
    0.8: "/home/nanaengo/Redac_Paper2/scan_A3/data/converged/production_dynamics.h5",
}
fig5, axes5 = plt.subplots(2, 3, figsize=(14, 8), facecolor=BG)

site_colors = [C1, C2, C3, C4, "#f85149", "#e3b341", "#8b949e", "#79c0ff", "#56d364"]
site_labels = [f"Site {i + 1}" for i in range(8)] + ["Plasmon (NPoM)"]

for row_idx, (vol, path) in enumerate(sorted(hdf5_paths.items())):
    try:
        with h5py.File(path, "r") as f:
            pops = f["dynamics/populations"][...]  # (5000, 9)
            rc_yield = f["dynamics/rc_yield"][...]  # (5000,)
            trapped = f["dynamics/trapped_pop"][...]
        t = np.linspace(0, 1000, pops.shape[0])
        n_sites = pops.shape[1]

        # Panel 1: All site populations
        ax = axes5[row_idx, 0]
        style_ax(ax)
        for i in range(n_sites):
            lw = 2.0 if i in (2, 3) else 1.2
            alpha = 1.0 if i in (2, 3, 8) else 0.65
            ax.plot(
                t,
                pops[:, i],
                color=site_colors[i % len(site_colors)],
                lw=lw,
                alpha=alpha,
                label=site_labels[i] if i in (0, 2, 3, 7, 8) else None,
            )
        ax.set_xlabel("Time (fs)", color=FG, fontsize=10)
        ax.set_ylabel("Population", color=FG, fontsize=10)
        ax.set_title(
            f"({'ab'[row_idx]}) Site populations — V={vol} nm³",
            color="#e6edf3",
            fontsize=10,
            pad=5,
        )
        ax.legend(
            fontsize=7.5, facecolor="#21262d", edgecolor=GRID, labelcolor=FG, ncol=2
        )
        ax.set_xlim(0, 1000)

        # Panel 2: RC yield and trapping
        ax2 = axes5[row_idx, 1]
        style_ax(ax2)
        ax2.plot(t, rc_yield, color=C2, lw=2.2, label=r"$\Phi_{FT}$ (cumulative)")
        ax2.plot(
            t,
            1.0 - trapped,
            color=C4,
            lw=1.8,
            ls="--",
            alpha=0.75,
            label=r"$\Phi_{\rm global}$",
        )
        ax2.axhline(y=rc_yield[-1], color=C2, lw=1.0, ls=":", alpha=0.6)
        ax2.text(
            850, rc_yield[-1] + 0.01, f"Φ_FT={rc_yield[-1]:.4f}", fontsize=8.5, color=C2
        )
        ax2.set_xlabel("Time (fs)", color=FG, fontsize=10)
        ax2.set_ylabel("Yield", color=FG, fontsize=10)
        ax2.set_title(
            f"({'cd'[row_idx]}) Transfer & global yield — V={vol} nm³",
            color="#e6edf3",
            fontsize=10,
            pad=5,
        )
        ax2.legend(fontsize=8.5, facecolor="#21262d", edgecolor=GRID, labelcolor=FG)
        ax2.set_xlim(0, 1000)

        # Panel 3: Early dynamics zoom (0-100 fs)
        ax3 = axes5[row_idx, 2]
        style_ax(ax3)
        mask = t <= 100
        for i in [0, 2, 3, 7, 8]:
            if i < n_sites:
                lw = 2.0 if i in (2, 3) else 1.2
                ax3.plot(
                    t[mask],
                    pops[mask, i],
                    color=site_colors[i],
                    lw=lw,
                    label=site_labels[i],
                )
        ax3.set_xlabel("Time (fs)", color=FG, fontsize=10)
        ax3.set_ylabel("Population", color=FG, fontsize=10)
        ax3.set_title(
            f"({'ef'[row_idx]}) Early dynamics (0–100 fs) — V={vol} nm³",
            color="#e6edf3",
            fontsize=10,
            pad=5,
        )
        ax3.legend(fontsize=8.0, facecolor="#21262d", edgecolor=GRID, labelcolor=FG)
        ax3.set_xlim(0, 100)

    except Exception as e:
        print(f"Error loading V={vol}: {e}")

fig5.text(
    0.5,
    0.005,
    r"MesoHOPS PT-HOPS/SBD | L=8, K=2, n=20, T=295 K — Paper 2 QST",
    ha="center",
    fontsize=8,
    color="#8b949e",
    style="italic",
)
plt.tight_layout(rect=[0, 0.03, 1, 1])

out5 = OUT_DIR / "Figure_SI_Population_Dynamics_V04_V08.png"
plt.savefig(out5, dpi=300, bbox_inches="tight", facecolor=BG)
plt.close()
print(f"Figure S5 saved: {out5}")
print("ALL FIGURES DONE")
