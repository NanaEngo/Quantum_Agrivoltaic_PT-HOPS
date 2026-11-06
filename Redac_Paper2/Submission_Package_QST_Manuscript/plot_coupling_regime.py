"""Regenerate Figure_SI_Coupling_Regime_Diagram.png (QST SI, Fig. SI coupling regime).

Panel (a): local forward transfer yield vs. vacuum coupling g0 with the three
physical regimes (over-coupled plasmonic trap / optimal / weak coupling),
from the canonical NPoM volume scan dataset (Table 2 & SI.tex).
Panel (b): schematic of the polariton--plasmon competition mechanism
(dressed-state hybridization, plasmon relaxation kappa vs. RC trapping).
"""

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Canonical 7-point NPoM volume scan (Table 2 & SI.tex; n=20 relaunch 20260924) ──
vols = np.array([0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4])
g0s = np.array([268.3, 189.7, 154.9, 134.1, 120.0, 109.5, 101.4])
phi_FT = np.array([0.0505, 0.0605, 0.0727, 0.0768, 0.0793, 0.0799, 0.0791])

BG = "#ffffff"
FG = "#000000"
GRID = "#e0e0e0"
C1 = "#1f77b4"
C2 = "#2ca02c"
C4 = "#ff7f0e"
CRED = "#d62728"


def style_ax(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=10)
    for sp in ax.spines.values():
        sp.set_color(FG)
    ax.grid(True, ls="--", lw=0.5, alpha=0.6, color=GRID)


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), facecolor=BG)

# ── (a) Phi_FT vs g0 with regime bands ───────────────────────────────────────
style_ax(ax1)
ax1.axvspan(220, 285, alpha=0.10, color=C4)
ax1.axvspan(98, 150, alpha=0.15, color=C2)
ax1.plot(g0s, phi_FT, "o-", color=C1, lw=2.0, ms=7, mfc=C1, mec=FG, mew=0.8, zorder=3)
ax1.axvline(x=109.5, color=C2, lw=1.2, ls=":", alpha=0.8)
ax1.annotate(
    "operating point\n$V=1.2~\\mathrm{nm}^3$\n(max $0.0799$)",
    xy=(109.5, 0.0799),
    xytext=(150, 0.058),
    fontsize=9,
    color=C2,
    ha="center",
    arrowprops={"arrowstyle": "->", "color": C2, "lw": 1.1},
)
ax1.annotate(
    "over-coupled\nplasmonic trap",
    xy=(268.3, 0.0505),
    xytext=(232, 0.040),
    fontsize=9,
    color=C4,
    ha="center",
    arrowprops={"arrowstyle": "->", "color": C4, "lw": 1.0},
)
ax1.text(120, 0.094, "optimal domain", fontsize=9.5, color=C2, ha="center", style="italic")
ax1.set_xlabel(r"$g_0$ (cm$^{-1}$)", color=FG, fontsize=11)
ax1.set_ylabel(r"$\Phi_{\rm FT}$", color=FG, fontsize=12)
ax1.set_title("(a) Yield vs. vacuum coupling", color=FG, fontsize=12, pad=6)
ax1.set_xlim(290, 95)  # inverted: strong coupling on the left
ax1.set_ylim(0.030, 0.100)

# ── (b) Schematic: polariton-plasmon competition ─────────────────────────────
style_ax(ax2)
ax2.grid(False)
# energy levels
xL, xP = 0.28, 0.72
y0, dL, dP = 0.62, 0.20, 0.14
for (x, y, lab, col) in [
    (xL, y0 + dL / 2, "lower\npolariton $|L\\rangle$", C1),
    (xP, y0 + dP / 2, "plasmon mode $|P\\rangle$", CRED),
]:
    ax2.hlines(y, x - 0.16, x + 0.16, color=col, lw=3)
    ax2.text(x, y + 0.055, lab, fontsize=10, color=col, ha="center")
# hybridization coupling arrow
ax2.annotate(
    "",
    xy=(xP - 0.17, y0 + dP / 2),
    xytext=(xL + 0.17, y0 + dL / 2),
    arrowprops={"arrowstyle": "<->", "color": "#555555", "lw": 1.6},
)
ax2.text(
    (xL + xP) / 2,
    y0 + 0.135,
    "dressed-state\nhybridization",
    fontsize=9.5,
    color="#555555",
    ha="center",
)
# decay arrows
ax2.annotate(
    "",
    xy=(xL, 0.30),
    xytext=(xL, y0 + dL / 2 - 0.01),
    arrowprops={"arrowstyle": "->", "color": FG, "lw": 2.0},
)
ax2.text(xL, 0.26, r"$\Gamma_{\rm RC}$ trapping", fontsize=10, color=FG, ha="center")
ax2.annotate(
    "",
    xy=(xP, 0.30),
    xytext=(xP, y0 + dP / 2 - 0.01),
    arrowprops={"arrowstyle": "->", "color": CRED, "lw": 2.0},
)
ax2.text(
    xP,
    0.26,
    r"$\kappa \approx 800~\mathrm{cm}^{-1}$" + "\nrelaxation ($Q \\approx 15$)",
    fontsize=10,
    color=CRED,
    ha="center",
)
# ground line
ax2.hlines(0.28, 0.08, 0.92, color=FG, lw=1.4)
ax2.text(0.5, 0.235, "excitation lost / trapped", fontsize=9, color=FG, ha="center", style="italic")
ax2.set_xlim(0.02, 0.98)
ax2.set_ylim(0.18, 1.02)
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_title("(b) Polariton-plasmon competition", color=FG, fontsize=12, pad=6)

fig.text(
    0.5,
    0.005,
    r"MesoHOPS PT-HOPS/SBD | L=8, K=2, T=295 K, t$_{\rm max}$=1000 fs — Paper 2 QST",
    ha="center",
    fontsize=9,
    color="#555555",
    style="italic",
)
fig.tight_layout(rect=(0, 0.03, 1, 1))

out = OUT_DIR / "Figure_SI_Coupling_Regime_Diagram.png"
fig.savefig(out, dpi=600, facecolor=BG)
plt.close(fig)
print(f"Coupling regime diagram regenerated: {out}")
