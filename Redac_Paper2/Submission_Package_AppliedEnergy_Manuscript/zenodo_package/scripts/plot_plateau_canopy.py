"""Head figure for the AE main: local quenching vs. global canopy stability.

Panel (a): forward transfer yield across the validated n=20 NPoM mode-volume
scan (relaunch 20260924 HDF5, Table tab:npom_volume_scan), against the
NPoM-off baseline --- the >90% local transport quenching.
Panel (b): area-weighted global canopy trapping yield for the 1% sentinel
fraction --- flat at 0.971 across the entire scan: the design-relevant outcome.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Validated n=20 canon (relaunch 20260924; tab:npom_volume_scan) ───────────
vols = np.array([0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4])
phi_FT = np.array([0.0505, 0.0605, 0.0727, 0.0768, 0.0793, 0.0799, 0.0791])
phi_off = 0.98  # pristine FMO baseline (NPoM off)
alpha = 0.01  # sentinel fraction
phi_gl = alpha * phi_FT + (1 - alpha) * phi_off

BG = "#ffffff"
FG = "#000000"
GRID = "#e0e0e0"
C1 = "#1f77b4"
C4 = "#ff7f0e"
CRED = "#d62728"


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=10)
    for sp in ax.spines.values():
        sp.set_color(FG)
    ax.grid(True, ls="--", lw=0.5, alpha=0.6, color=GRID)


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.4), facecolor=BG)

# ── (a) Local quenching: the 12x gulf against the NPoM-off baseline ──────────
style_ax(ax1)
ax1.axhline(phi_off, color=CRED, lw=1.4, ls="--")
ax1.text(0.66, phi_off - 0.055, "NPoM-off baseline (0.98)", color=CRED, fontsize=9)
ax1.plot(vols, phi_FT, "o-", color=C1, lw=2.2, ms=7, mfc=C1, mec=FG, mew=0.9, zorder=3)
ax1.annotate(
    "max 0.0799\nat V=1.2 nm$^3$",
    xy=(1.2, 0.0799),
    xytext=(0.78, 0.24),
    fontsize=9,
    color=C1,
    ha="center",
    arrowprops={"arrowstyle": "->", "color": C1, "lw": 1.0},
)
ax1.set_xlabel(r"$V_{\rm mode}$ (nm$^3$)", color=FG, fontsize=11)
ax1.set_ylabel(r"$\Phi_{\rm FT}$ (local)", color=FG, fontsize=12)
ax1.set_title("(a) Local: >90% transport quenching", color=FG, fontsize=12, pad=6)
ax1.set_xlim(0.05, 1.5)
ax1.set_ylim(0.0, 1.06)

# ── (b) Global plateau: flat at 97.1% across the scan ────────────────────────
style_ax(ax2)
ax2.plot(vols, phi_gl, "s-", color=C4, lw=2.2, ms=7, mfc=C4, mec=FG, mew=0.9, zorder=3)
ax2.axhline(0.971, color="#555555", lw=1.0, ls=":")
ax2.fill_between(vols, 0.971, 1.0, alpha=0.08, color="#555555")
ax2.text(
    0.75,
    0.984,
    "NPoM integration cost: 0.9 pt\n(shortfall vs. ideal: 2.9 pts)",
    fontsize=9,
    color="#555555",
    ha="center",
)
ax2.set_xlabel(r"$V_{\rm mode}$ (nm$^3$)", color=FG, fontsize=11)
ax2.set_ylabel(r"$\Phi_{\rm FT}^{\rm global}$", color=FG, fontsize=12)
ax2.set_title("(b) Global: flat at 97.1% across the scan", color=FG, fontsize=12, pad=6)
ax2.set_xlim(0.05, 1.5)
ax2.set_ylim(0.955, 1.005)
ax2.set_yticks([0.96, 0.97, 0.98, 0.99, 1.00])

fig.text(
    0.5,
    0.005,
    r"MesoHOPS PT-HOPS/SBD | L=8, K=2, T=295 K, t$_{\rm max}$=1000 fs, $n$=20",
    ha="center",
    fontsize=9,
    color="#555555",
    style="italic",
)
fig.tight_layout(rect=(0, 0.03, 1, 1))

out = OUT_DIR / "Figure_Plateau_Canopy.png"
fig.savefig(out, dpi=600, facecolor=BG)
plt.close(fig)
print(f"Plateau figure regenerated: {out}")
