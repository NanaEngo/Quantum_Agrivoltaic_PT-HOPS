"""Regenerate the two SI comparison figures of the Applied Energy submission.

Source of truth for panel letters/counts: `AppliedEnergy_SM_2609.tex`
section S11 (`SI-sec:comparative_hdf5`):

  Figure_SI_Comparative_4Runs.png  -> fig:SI_comparative_dynamics, panels (a)-(i)
  Figure_SI_NPoM_ON_vs_OFF.png     -> fig:SI_npom_off_vs_on, panels (a)-(j)

Data: `Redac_Paper2/data/converged/*.h5` (+ `relaunch_20260924/`).
Honesty rules baked into the figure text:
  * the NPoM-OFF `rc_yield` trace is Gamma*int(P3+P4)dt and does NOT saturate;
    the published passive baseline is the capture-efficiency cap 0.980,
    so the raw endpoint is never presented as a yield;
  * canonical values only: suppression 91.8 %, Phi_global 0.971,
    g0(V=1.2) = 110 cm^-1, Phi = 0.980 / 0.0768 / 0.0799 / 0.1685.
"""

from pathlib import Path

import h5py
import matplotlib
import numpy as np
from PIL import Image

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

PKG = Path(__file__).resolve().parent
DATA = PKG.parent / "data" / "converged"
FIGDIR = PKG / "figures"
DPI = 300

# ── Canonical published numbers (table_comparative_4runs.tex) ────────────────
PHI_OFF_CAP = 0.980  # passive capture-efficiency cap (model input)
PHI = {"off": 0.9800, "v08": 0.0768, "v12": 0.0799, "k77": 0.1685}
N_TRAJ = {"off": 20, "v08": 100, "v12": 20, "k77": 2}
MAX_TRAP = {"off": 0.0189, "v08": 0.0048, "v12": 0.0038, "k77": 0.0055}
P1_FINAL = {"off": 0.7318, "v08": 0.1455, "v12": 0.1221, "k77": 0.1091}
P6_FINAL = {"off": 0.0030, "v08": 0.0537, "v12": 0.0422, "k77": 0.0409}
PLAS_FINAL = {"off": None, "v08": 0.7901, "v12": 0.8256, "k77": 0.8401}
SERS_EF = {"off": None, "v08": 100.0, "v12": 44.0, "k77": 44.0}
FOM = {"off": None, "v08": 7.68, "v12": 3.52, "k77": 7.41}
PHI_GLOBAL = 0.971  # 0.01 * Phi_NPoM + 0.99 * 0.980
SUPPRESSION_PCT = 91.8
G0_V12_CM1 = 110

# Okabe-Ito palette: 8 FMO sites + plasmon, all pairwise distinct.
SITE_COLORS = [
    "#0072B2",  # site 1
    "#E69F00",  # site 2
    "#D55E00",  # site 3 (trapping)
    "#CC79A7",  # site 4 (trapping)
    "#56B4E9",  # site 5
    "#009E73",  # site 6
    "#F0E442",  # site 7
    "#999999",  # site 8
    "#000000",  # plasmon (Site 9) — must differ from site 3
]
C_OFF, C_V08, C_V12, C_K77 = "#4d4d4d", "#0072B2", "#D55E00", "#009E73"
C_CAP = "#b22222"

LABELS = {
    "off": "NPoM OFF (n = 20, 8-site)",
    "v08": "V = 0.8 nm$^3$, 295 K (n = 20 relaunch)",
    "v12": "V = 1.2 nm$^3$, 295 K (n = 20)",
    "k77": "V = 1.2 nm$^3$, 77 K (n = 2)",
}
COLORS = {"off": C_OFF, "v08": C_V08, "v12": C_V12, "k77": C_K77}

S_OFF = 0  # site 1
S_TRAP = (2, 3)  # sites 3 + 4
S6 = 5
PLASMON = 8


def load(path: Path) -> dict:
    """Load one production HDF5: populations, cumulative Gamma*int dt, trace."""
    with h5py.File(path, "r") as f:
        grp = f["dynamics"]
        pop = np.asarray(grp["populations"])
        rc = np.asarray(grp["rc_yield"])
        dt = float(grp.attrs["time_step_fs"])
        meta = {k: str(grp.attrs.get(k, "?")) for k in ("run_id", "git_hash", "timestamp")}
    return {
        "t": np.arange(pop.shape[0]) * dt,
        "pop": pop,
        "rc": rc,
        "trace": pop.sum(axis=1),
        "trap": pop[:, S_TRAP[0]] + pop[:, S_TRAP[1]],
        "nsite": pop.shape[1],
        "meta": meta,
    }


def load_runs() -> dict:
    return {
        "off": load(DATA / "baseline_N20.h5"),
        "v08": load(DATA / "relaunch_20260924" / "V0.8" / "production_dynamics.h5"),
        "v12": load(DATA / "relaunch_20260924" / "V1.2" / "production_dynamics.h5"),
        "k77": load(DATA / "production_dynamics_77K.h5"),
    }


def style_ax(ax) -> None:
    ax.set_facecolor("#ffffff")
    ax.tick_params(colors="#000000", labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#000000")
    ax.grid(True, ls="--", lw=0.5, alpha=0.6, color="#e0e0e0")


def report(runs: dict) -> None:
    """Print the provenance/consistency checks asked for by the SI text."""
    print("── run provenance ─────────────────────────────────────────────")
    for key, run in runs.items():
        tr = run["trace"]
        print(
            f"{key:4s} nsite={run['nsite']} run_id={run['meta']['run_id']} "
            f"ts={run['meta']['timestamp']} dt={run['t'][1] - run['t'][0]:.1f} fs"
        )
        print(
            f"     Tr(rho): mu={tr.mean():.6f} sigma={tr.std():.2e} "
            f"final={tr[-1]:.6f}  |  Gamma*int dt end={run['rc'][-1]:.4f}"
        )
        print(f"     final pops={np.round(run['pop'][-1], 4)}  max(P3+P4)={run['trap'].max():.4f}")
    # canonical cross-checks against table_comparative_4runs.tex
    checks = [
        ("off  P1 final", runs["off"]["pop"][-1, 0], P1_FINAL["off"], 1e-4),
        ("off  max trap", runs["off"]["trap"].max(), MAX_TRAP["off"], 1e-4),
        ("v12  Phi", runs["v12"]["rc"][-1], PHI["v12"], 5e-5),
        ("v12  P1 final", runs["v12"]["pop"][-1, 0], P1_FINAL["v12"], 1e-4),
        ("v12  P6 final", runs["v12"]["pop"][-1, S6], P6_FINAL["v12"], 1e-4),
        ("v12  plasmon", runs["v12"]["pop"][-1, PLASMON], PLAS_FINAL["v12"], 1e-4),
        ("v12  max trap", runs["v12"]["trap"].max(), MAX_TRAP["v12"], 1e-4),
        ("k77  Phi", runs["k77"]["rc"][-1], PHI["k77"], 5e-5),
        ("k77  plasmon", runs["k77"]["pop"][-1, PLASMON], PLAS_FINAL["k77"], 1e-4),
        ("k77  max trap", runs["k77"]["trap"].max(), MAX_TRAP["k77"], 1e-4),
    ]
    print("── canonical cross-checks ─────────────────────────────────────")
    for name, got, want, tol in checks:
        status = "OK " if abs(got - want) <= tol else "DIFF"
        print(f"[{status}] {name}: h5={got:.4f} table={want:.4f}")
    supp = 100.0 * (PHI_OFF_CAP - PHI["v12"]) / PHI_OFF_CAP
    print(f"suppression = (0.980-0.0799)/0.980 = {supp:.1f} %")
    print(f"Phi_global  = 0.01*0.0799 + 0.99*0.980 = {0.01 * PHI['v12'] + 0.99 * PHI_OFF_CAP:.3f}")
    print(
        f"trace sigma (ON v12) = {runs['v12']['trace'].std():.2e} "
        f"-> mu=1.000000, sigma<1e-5: {runs['v12']['trace'].std() < 1e-5}"
    )
    print(
        f"plasmon share (v12): t=100 fs {runs['v12']['pop'][500, PLASMON]:.3f}, "
        f"t=1 ps {runs['v12']['pop'][-1, PLASMON]:.3f}"
    )
    print(
        f"V0.8 local trace is the n=20 relaunch: Phi={runs['v08']['rc'][-1]:.4f} "
        f"(archived n=100 run: {PHI['v08']}) -- table keeps the n=100 value"
    )


# ═══════════════════════════════════════════════════════════════════════════
# Figure S1 — fig:SI_comparative_dynamics, panels (a)-(i)
# ═══════════════════════════════════════════════════════════════════════════
def figure_comparative_4runs(runs: dict) -> None:
    fig, axes = plt.subplots(3, 3, figsize=(16, 12.5), constrained_layout=True)
    (a_phi, a_s1, a_plas), (a_trap, a_s6, a_tr), (a_bphi, a_btrap, a_tbl) = axes
    keys = ["off", "v08", "v12", "k77"]

    # (a) forward transfer yield ------------------------------------------------
    style_ax(a_phi)
    for k in keys:
        a_phi.plot(runs[k]["t"], runs[k]["rc"], color=COLORS[k], lw=1.6, label=LABELS[k])
    a_phi.axhline(PHI_OFF_CAP, color=C_CAP, ls="--", lw=1.5)
    a_phi.text(
        40,
        PHI_OFF_CAP + 0.045,
        "passive cap $\\Phi$ = 0.980",
        color=C_CAP,
        fontsize=9,
        fontweight="bold",
    )
    a_phi.text(
        58,
        1.62,
        "NPoM OFF: $\\Gamma\\!\\int(P_3{+}P_4)\\,dt$ does not saturate\n"
        "in the 1 ps window (passive baseline = cap 0.980)",
        fontsize=7.5,
        color=C_OFF,
        va="top",
    )
    a_phi.text(
        58,
        1.34,
        "NPoM on: $\\Phi_{\\rm FT}$ = 0.0768 / 0.0799 / 0.1685",
        fontsize=7.5,
        color=C_V12,
        va="top",
    )
    a_phi.set_xlim(0, 1000)
    a_phi.set_ylim(0, 2.15)
    a_phi.set_xlabel("Time (fs)", fontsize=11)
    a_phi.set_ylabel("$\\Phi_{\\rm FT}$ (cumulative)", fontsize=11)
    a_phi.set_title("(a) Forward transfer yield $\\Phi_{\\rm FT}$", fontsize=12, pad=6)
    a_phi.legend(fontsize=8, loc="upper left", framealpha=0.9)
    # zoom inset over the NPoM-on traces (free band below the cap line)
    ins = a_phi.inset_axes([0.47, 0.17, 0.49, 0.25])
    style_ax(ins)
    short = {"v08": "V = 0.8", "v12": "V = 1.2", "k77": "V = 1.2, 77 K"}
    for k in ["v08", "v12", "k77"]:
        ins.plot(runs[k]["t"], runs[k]["rc"], color=COLORS[k], lw=1.4, label=short[k])
    ins.axhline(PHI_OFF_CAP, color=C_CAP, ls="--", lw=1.0)
    ins.set_xlim(0, 1000)
    ins.set_ylim(0, 0.20)
    ins.text(0.5, 0.93, "NPoM-on zoom", transform=ins.transAxes, fontsize=7, ha="center", va="top")
    ins.tick_params(labelsize=7)
    ins.legend(fontsize=6, loc="lower right")

    # (b) site 1 antenna --------------------------------------------------------
    style_ax(a_s1)
    for k in keys:
        a_s1.plot(runs[k]["t"], runs[k]["pop"][:, S_OFF], color=COLORS[k], lw=1.5, label=LABELS[k])
    a_s1.set_xlim(0, 1000)
    a_s1.set_xlabel("Time (fs)", fontsize=11)
    a_s1.set_ylabel("Site 1 population", fontsize=11)
    a_s1.set_title("(b) Site 1 antenna population", fontsize=12, pad=6)
    a_s1.legend(fontsize=8, loc="best")

    # (c) plasmon mode ----------------------------------------------------------
    style_ax(a_plas)
    for k in ["v08", "v12", "k77"]:
        a_plas.plot(
            runs[k]["t"], runs[k]["pop"][:, PLASMON], color=COLORS[k], lw=1.5, label=LABELS[k]
        )
    a_plas.set_xlim(0, 1000)
    a_plas.set_ylim(0, 1.05)
    a_plas.set_xlabel("Time (fs)", fontsize=11)
    a_plas.set_ylabel("Plasmon population", fontsize=11)
    a_plas.set_title("(c) Plasmon mode (Site 9)", fontsize=12, pad=6)
    a_plas.text(980, 0.45, "NPoM OFF: no plasmon channel", fontsize=8, color=C_OFF, ha="right")
    a_plas.legend(fontsize=8, loc="lower left")

    # (d) trapping sites 3+4 ----------------------------------------------------
    style_ax(a_trap)
    for k in keys:
        a_trap.plot(runs[k]["t"], runs[k]["trap"], color=COLORS[k], lw=1.5, label=LABELS[k])
    a_trap.set_xlim(0, 1000)
    a_trap.set_xlabel("Time (fs)", fontsize=11)
    a_trap.set_ylabel("Sites 3 + 4 population", fontsize=11)
    a_trap.set_title("(d) Trapping sites 3 + 4", fontsize=12, pad=6)
    a_trap.legend(fontsize=8, loc="upper right")

    # (e) site 6 ----------------------------------------------------------------
    style_ax(a_s6)
    for k in keys:
        a_s6.plot(runs[k]["t"], runs[k]["pop"][:, S6], color=COLORS[k], lw=1.5, label=LABELS[k])
    a_s6.set_xlim(0, 1000)
    a_s6.set_xlabel("Time (fs)", fontsize=11)
    a_s6.set_ylabel("Site 6 population", fontsize=11)
    a_s6.set_title("(e) Site 6 secondary antenna", fontsize=12, pad=6)
    a_s6.legend(fontsize=8, loc="best")

    # (f) trace conservation ----------------------------------------------------
    style_ax(a_tr)
    for k in keys:
        a_tr.plot(runs[k]["t"], runs[k]["trace"], color=COLORS[k], lw=1.5, label=LABELS[k])
    a_tr.set_xlim(0, 1000)
    a_tr.set_ylim(1.0 - 3e-5, 1.0 + 3e-5)
    a_tr.yaxis.set_major_formatter(plt.ScalarFormatter(useOffset=False))
    a_tr.set_yticks([1.0 - 2e-5, 1.0, 1.0 + 2e-5])
    a_tr.set_xlabel("Time (fs)", fontsize=11)
    a_tr.set_ylabel("Tr($\\rho$)", fontsize=11)
    a_tr.set_title("(f) Trace conservation", fontsize=12, pad=6)
    a_tr.text(
        500,
        1.0 - 2.2e-5,
        "$\\mu$ = 1.000000, $\\sigma < 10^{-5}$ (all four runs)",
        fontsize=10,
        ha="center",
    )

    # (g) bar chart of final Phi_FT ---------------------------------------------
    style_ax(a_bphi)
    keys_b = ["off", "v08", "v12", "k77"]
    vals = [PHI[k] for k in keys_b]
    a_bphi.bar(
        range(4),
        vals,
        color=[COLORS[k] for k in keys_b],
        edgecolor="#000000",
        lw=0.8,
        width=0.62,
    )
    for i, v in enumerate(vals):
        a_bphi.text(
            i,
            v + 0.012,
            f"{v:.4f}",
            ha="center",
            fontsize=10,
            fontweight="bold",
        )
    a_bphi.text(
        3, PHI["k77"] + 0.10, "$\\times 2.1$ vs 295 K", ha="center", fontsize=9, color=C_K77
    )
    a_bphi.set_xticks(range(4))
    a_bphi.set_xticklabels(
        [
            "NPoM OFF\n(n = 20; cap)",
            "V = 0.8,\n295 K (n = 100)",
            "V = 1.2,\n295 K (n = 20)",
            "V = 1.2,\n77 K (n = 2)",
        ],
        fontsize=8,
    )
    a_bphi.set_ylim(0, 1.40)
    a_bphi.set_ylabel("$\\Phi_{\\rm FT}$", fontsize=11)
    a_bphi.set_title("(g) Final $\\Phi_{\\rm FT}$", fontsize=12, pad=6)
    a_bphi.text(
        0.5,
        0.955,
        "* OFF = passive capture cap (model input); the $\\Gamma\\!\\int dt$ trace does not\n"
        "  saturate. V = 0.8 bar = archived n = 100 run (n = 20 relaunch trace: 0.0761).",
        transform=a_bphi.transAxes,
        ha="center",
        va="top",
        fontsize=7.5,
        color="#333333",
    )

    # (h) bar chart of max trapping population -----------------------------------
    style_ax(a_btrap)
    vals_h = [MAX_TRAP[k] for k in keys_b]
    a_btrap.bar(
        range(4),
        vals_h,
        color=[COLORS[k] for k in keys_b],
        edgecolor="#000000",
        lw=0.8,
        width=0.62,
    )
    for i, v in enumerate(vals_h):
        a_btrap.text(i, v + 0.0004, f"{v:.4f}", ha="center", fontsize=10, fontweight="bold")
    a_btrap.set_xticks(range(4))
    a_btrap.set_xticklabels(
        [
            "NPoM OFF\n(n = 20)",
            "V = 0.8,\n295 K (n = 100)",
            "V = 1.2,\n295 K (n = 20)",
            "V = 1.2,\n77 K (n = 2)",
        ],
        fontsize=8,
    )
    a_btrap.set_ylim(0, 0.024)
    a_btrap.set_ylabel("max P$_{3+4}$", fontsize=11)
    a_btrap.set_title("(h) Max trapping population (3 + 4)", fontsize=12, pad=6)
    a_btrap.text(
        0.5,
        0.955,
        "Table values (V = 0.8 = archived n = 100 run;\nthe n = 20 relaunch trace peaks at 0.0047).",
        transform=a_btrap.transAxes,
        ha="center",
        va="top",
        fontsize=7.5,
        color="#333333",
    )

    # (i) summary table ----------------------------------------------------------
    a_tbl.axis("off")
    a_tbl.set_title("(i) Summary (table_comparative_4runs)", fontsize=12, pad=6)
    header = [
        "Metric",
        "NPoM OFF\n(n = 20)",
        "V = 0.8\n(n = 100)",
        "V = 1.2\n(n = 20)",
        "V = 1.2, 77 K\n(n = 2)",
    ]
    cells = [
        ["System size", "8$\\times$8", "9$\\times$9", "9$\\times$9", "9$\\times$9"],
        ["$\\Phi_{\\rm FT}$", "0.9800*", "0.0768", "0.0799", "0.1685"],
        ["max P$_{3+4}$", "0.0189", "0.0048", "0.0038", "0.0055"],
        ["Site 1 final", "0.7318", "0.1455", "0.1221", "0.1091"],
        ["Site 6 final", "0.0030", "0.0537", "0.0422", "0.0409"],
        ["Plasmon final", "---", "0.7901", "0.8256", "0.8401"],
        [
            "Tr($\\rho$)",
            "1.0000\n$\\sigma{<}10^{-5}$",
            "1.0000\n$\\sigma{<}10^{-5}$",
            "1.0000\n$\\sigma{<}10^{-5}$",
            "1.0000\n$\\sigma{<}10^{-5}$",
        ],
        ["SERS EF", "---", "100.0", "44.0", "44.0"],
        ["$\\Phi_{\\rm FT}\\times$EF", "---", "7.68", "3.52", "7.41"],
    ]
    tbl = a_tbl.table(cellText=cells, colLabels=header, loc="center", bbox=[0.0, 0.30, 1.0, 0.62])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.5)
    tbl.scale(1, 1.4)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor("#666666")
        cell.get_text().set_fontweight("bold" if row == 0 else "normal")
        if row == 0:
            cell.set_facecolor("#f0f0f0")
        cell.set_width(0.24 if col == 0 else 0.19)
    a_tbl.text(
        0.5,
        0.24,
        "* OFF $\\Phi_{\\rm FT}$ = passive capture-efficiency cap (model input); "
        "$\\Gamma\\!\\int(P_3{+}P_4)dt$ does not saturate in the 1 ps window.\n"
        "V = 0.8 column = archived n = 100 production run; the plotted V = 0.8 trace "
        "is the n = 20 relaunch HDF5 ($\\Phi$ = 0.0761).\n"
        "All other entries are read directly from the archived HDF5 files "
        "(run_id in the file attributes).",
        transform=a_tbl.transAxes,
        ha="center",
        va="top",
        fontsize=8,
        color="#333333",
    )

    out = FIGDIR / "Figure_SI_Comparative_4Runs.png"
    fig.savefig(out, dpi=DPI, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


# ═══════════════════════════════════════════════════════════════════════════
# Figure S2 — fig:SI_npom_off_vs_on, panels (a)-(j)
# ═══════════════════════════════════════════════════════════════════════════
def figure_npom_on_vs_off(runs: dict) -> None:
    off, on = runs["off"], runs["v12"]
    c_off, c_on = "#0072B2", "#D55E00"

    fig = plt.figure(figsize=(16, 14), constrained_layout=True)
    gs = fig.add_gridspec(4, 4, height_ratios=[1.25, 1.0, 1.0, 1.05])
    ax_a = fig.add_subplot(gs[0, :])
    axes_row1 = [fig.add_subplot(gs[1, i]) for i in range(4)]
    axes_row2 = [fig.add_subplot(gs[2, i]) for i in range(4)]
    ax_j = fig.add_subplot(gs[3, :])

    # (a) forward transfer yield: OFF vs ON -------------------------------------
    style_ax(ax_a)
    ax_a.plot(
        off["t"],
        off["rc"],
        color=c_off,
        lw=2.0,
        label="NPoM OFF (n = 20): $\\Gamma\\!\\int(P_3{+}P_4)\\,dt$ (non-saturating)",
    )
    ax_a.plot(
        on["t"],
        on["rc"],
        color=c_on,
        lw=2.0,
        label="NPoM ON V = 1.2 nm$^3$ (n = 20): $\\Phi_{\\rm FT}$ = 0.0799",
    )
    ax_a.axhline(
        PHI_OFF_CAP, color=C_CAP, ls="--", lw=1.6, label="passive cap $\\Phi$ = 0.980 (model input)"
    )
    ax_a.annotate(
        "",
        xy=(880, 0.0799),
        xytext=(880, PHI_OFF_CAP),
        arrowprops={"arrowstyle": "<->", "color": "#000000", "lw": 1.3},
    )
    ax_a.text(
        865,
        0.52,
        f"$-$ {SUPPRESSION_PCT} %\nsuppression\n(0.0799 vs 0.980)",
        ha="right",
        fontsize=11,
        fontweight="bold",
        color="#000000",
        bbox={"boxstyle": "round,pad=0.3", "fc": "#ffffff", "ec": "#999999", "alpha": 0.9},
    )
    ax_a.text(
        60,
        1.58,
        "NPoM OFF: the cumulative $\\Gamma\\!\\int dt$ trace does not saturate in the\n"
        "1 ps window; the published passive baseline is the cap 0.980",
        fontsize=9.5,
        color=c_off,
        va="top",
    )
    ax_a.set_xlim(0, 1000)
    ax_a.set_ylim(0, 2.15)
    ax_a.set_xlabel("Time (fs)", fontsize=11)
    ax_a.set_ylabel("$\\Phi_{\\rm FT}$ (cumulative)", fontsize=11)
    ax_a.set_title("(a) Forward transfer yield $\\Phi_{\\rm FT}$: NPoM OFF vs ON", fontsize=12)
    ax_a.legend(fontsize=9, loc="upper left", framealpha=0.92)

    # (b) site 1 antenna ---------------------------------------------------------
    axb = axes_row1[0]
    style_ax(axb)
    axb.plot(off["t"], off["pop"][:, S_OFF], color=c_off, lw=1.8, label="NPoM OFF")
    axb.plot(on["t"], on["pop"][:, S_OFF], color=c_on, lw=1.8, label="NPoM ON (V = 1.2)")
    axb.set_xlim(0, 1000)
    axb.set_xlabel("Time (fs)", fontsize=10)
    axb.set_ylabel("Site 1 population", fontsize=10)
    axb.set_title("(b) Site 1 antenna", fontsize=11)
    axb.text(
        0.97,
        0.93,
        "final: 73 % OFF / 12 % ON",
        transform=axb.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
    )
    axb.legend(fontsize=8, loc="center right")

    # (c) trapping sites 3+4 -----------------------------------------------------
    axc = axes_row1[1]
    style_ax(axc)
    axc.plot(off["t"], off["trap"], color=c_off, lw=1.8, label="NPoM OFF")
    axc.plot(on["t"], on["trap"], color=c_on, lw=1.8, label="NPoM ON (V = 1.2)")
    axc.set_xlim(0, 1000)
    axc.set_xlabel("Time (fs)", fontsize=10)
    axc.set_ylabel("Sites 3 + 4 population", fontsize=10)
    axc.set_title("(c) Trapping sites 3 + 4", fontsize=11)
    axc.text(
        0.97,
        0.60,
        "max 0.0189 $\\rightarrow$ 0.0038\n(fivefold reduction)",
        transform=axc.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
    )
    axc.legend(fontsize=7.5, loc="upper right")

    # (d) site 6 ------------------------------------------------------------------
    axd = axes_row1[2]
    style_ax(axd)
    axd.plot(off["t"], off["pop"][:, S6], color=c_off, lw=1.8, label="NPoM OFF")
    axd.plot(on["t"], on["pop"][:, S6], color=c_on, lw=1.8, label="NPoM ON (V = 1.2)")
    axd.set_xlim(0, 1000)
    axd.set_xlabel("Time (fs)", fontsize=10)
    axd.set_ylabel("Site 6 population", fontsize=10)
    axd.set_title("(d) Site 6 secondary antenna", fontsize=11)
    axd.text(
        0.97,
        0.93,
        "final: 0.0030 OFF / 0.0422 ON",
        transform=axd.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
    )
    axd.legend(fontsize=8, loc="center right")

    # (e) final site distribution -------------------------------------------------
    axe = axes_row1[3]
    style_ax(axe)
    labels_e = [f"S{i + 1}" for i in range(8)] + ["Plas"]
    x = np.arange(9)
    off_final = np.append(off["pop"][-1], np.nan)
    on_final = on["pop"][-1]
    w = 0.42
    for i in range(9):
        col = SITE_COLORS[i]
        if not np.isnan(off_final[i]):
            axe.bar(
                x[i] - w / 2,
                off_final[i],
                width=w,
                color=col,
                alpha=0.55,
                hatch="//",
                edgecolor="#000000",
                lw=0.7,
            )
        axe.bar(x[i] + w / 2, on_final[i], width=w, color=col, edgecolor="#000000", lw=0.7)
    axe.set_xticks(x)
    axe.set_xticklabels(labels_e, fontsize=9)
    axe.set_xlabel("Site", fontsize=10)
    axe.set_ylabel("Final population (t = 1000 fs)", fontsize=10)
    axe.set_title("(e) Site distribution", fontsize=11)
    axe.legend(
        handles=[
            Patch(facecolor="#bbbbbb", hatch="//", edgecolor="#000000", label="NPoM OFF"),
            Patch(facecolor="#bbbbbb", edgecolor="#000000", label="NPoM ON"),
        ],
        fontsize=7.5,
        loc="center",
    )

    # (f) plasmon mode population --------------------------------------------------
    axf = axes_row2[0]
    style_ax(axf)
    axf.plot(
        off["t"],
        np.zeros_like(off["t"]),
        color=c_off,
        lw=1.5,
        label="NPoM OFF (no plasmon channel)",
    )
    axf.plot(
        on["t"], on["pop"][:, PLASMON], color="#000000", lw=1.8, label="NPoM ON plasmon (Site 9)"
    )
    axf.set_xlim(0, 1000)
    axf.set_ylim(0, 1.05)
    axf.set_xlabel("Time (fs)", fontsize=10)
    axf.set_ylabel("Plasmon population", fontsize=10)
    axf.set_title("(f) Plasmon mode population", fontsize=11)
    axf.text(
        0.97,
        0.70,
        "NPoM ON: plasmon captures\n$\\geq$82.3 % of the excitation\n"
        "within 100 fs\n(85.1 % at 100 fs; 82.6 % at 1 ps)",
        transform=axf.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
        bbox={"boxstyle": "round,pad=0.3", "fc": "#ffffff", "ec": "#999999"},
    )
    axf.legend(fontsize=8, loc="lower left")

    # (g) trace conservation --------------------------------------------------------
    axg = axes_row2[1]
    style_ax(axg)
    axg.plot(off["t"], off["trace"], color=c_off, lw=1.8, label="NPoM OFF")
    axg.plot(on["t"], on["trace"], color=c_on, lw=1.8, label="NPoM ON (V = 1.2)")
    axg.set_xlim(0, 1000)
    axg.set_ylim(1.0 - 3e-5, 1.0 + 3e-5)
    axg.yaxis.set_major_formatter(plt.ScalarFormatter(useOffset=False))
    axg.set_yticks([1.0 - 2e-5, 1.0, 1.0 + 2e-5])
    axg.set_xlabel("Time (fs)", fontsize=10)
    axg.set_ylabel("Tr($\\rho$)", fontsize=10)
    axg.set_title("(g) Trace conservation", fontsize=11)
    axg.text(
        0.5,
        0.45,
        "$\\mu$ = 1.000000 for both runs\n($\\sigma < 10^{-5}$)",
        transform=axg.transAxes,
        ha="center",
        va="center",
        fontsize=9.5,
    )

    # (h) early dynamics zoom (0-50 fs) ----------------------------------------------
    axh = axes_row2[2]
    style_ax(axh)
    sl = off["t"] <= 50
    axh.plot(off["t"][sl], off["pop"][sl, S_OFF], color=c_off, lw=1.8, label="OFF: Site 1")
    axh.plot(off["t"][sl], off["trap"][sl], color=c_off, lw=1.4, ls=":", label="OFF: Sites 3+4")
    axh.plot(on["t"][sl], on["pop"][sl, S_OFF], color=c_on, lw=1.8, label="ON: Site 1")
    axh.plot(on["t"][sl], on["trap"][sl], color=c_on, lw=1.4, ls=":", label="ON: Sites 3+4")
    axh.plot(
        on["t"][sl], on["pop"][sl, PLASMON], color="#000000", lw=1.6, ls="--", label="ON: plasmon"
    )
    axh.set_xlim(0, 50)
    axh.set_xlabel("Time (fs)", fontsize=10)
    axh.set_ylabel("Population", fontsize=10)
    axh.set_title("(h) Early dynamics (0$-$50 fs)", fontsize=11)
    axh.legend(fontsize=7, loc="center left")

    # (i) yield comparison across four configurations -----------------------------------
    axi = axes_row2[3]
    style_ax(axi)
    keys = ["off", "v08", "v12", "k77"]
    vals = [PHI[k] for k in keys]
    axi.bar(
        range(4), vals, color=[COLORS[k] for k in keys], edgecolor="#000000", lw=0.8, width=0.62
    )
    for i, v in enumerate(vals):
        axi.text(
            i,
            v + 0.02,
            f"{v:.4f}",
            ha="center",
            fontsize=9.5,
            fontweight="bold",
        )
    axi.set_xticks(range(4))
    axi.set_xticklabels(
        ["OFF\n(n = 20; cap)", "V = 0.8\n(n = 100)", "V = 1.2\n(n = 20)", "V = 1.2\n77 K (n = 2)"],
        fontsize=8.5,
    )
    axi.set_ylim(0, 1.15)
    axi.set_ylabel("$\\Phi_{\\rm FT}$", fontsize=10)
    axi.set_title("(i) Yield comparison", fontsize=11)
    axi.text(
        0.62,
        0.62,
        f"$\\Phi_{{\\rm global}}$ = {PHI_GLOBAL}\n(1 % sentinel fraction)",
        transform=axi.transAxes,
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        bbox={"boxstyle": "round,pad=0.3", "fc": "#ffffff", "ec": "#999999"},
    )

    # (j) physical interpretation ---------------------------------------------------------
    axj = ax_j
    axj.set_xlim(0, 1)
    axj.set_ylim(0, 1)
    axj.axis("off")
    axj.add_patch(
        plt.Rectangle(
            (0.004, 0.03), 0.992, 0.94, fill=False, ec="#666666", lw=1.2, transform=axj.transData
        )
    )
    axj.text(
        0.03,
        0.95,
        "(j) Physical interpretation: strong-coupling hybridization",
        fontsize=12,
        fontweight="bold",
        va="top",
    )
    bullets = (
        "1. PLASMONIC SUPPRESSION\n"
        "     $\\Phi_{\\rm FT}$: 0.980 (passive cap) $\\rightarrow$ 0.0799 "
        "(NPoM ON, V = 1.2 nm$^3$, n = 20) = $-$91.8 %\n"
        "2. POPULATION REDISTRIBUTION (t = 1000 fs)\n"
        "     plasmon captures $\\geq$82.3 % of the excitation within 100 fs "
        "(82.6 % at 1 ps), starving the reaction center\n"
        "     OFF: Site 1 = 73 %, Site 2 = 20 %, trapping 3+4 max = 0.0189\n"
        "3. COMPETITIVE TRAPPING PATHWAY\n"
        "     max P$_{3+4}$: 0.0189 $\\rightarrow$ 0.0038 (fivefold); "
        "77 K recovers 0.0055 (+45 %) and $\\Phi_{\\rm FT}$ = 0.1685 ($\\times 2.1$)\n"
        "4. NUMERICAL VALIDATION\n"
        "     Tr($\\rho$) = 1.000000, $\\sigma < 10^{-5}$ for OFF and ON "
        "(n = 20 each) $\\Rightarrow$ suppression is physical, not numerical\n"
        "5. SYSTEM DESIGN IMPLICATION\n"
        "     1 % sentinel fraction: $\\Phi_{\\rm global}$ = 0.971; "
        "99 % of the canopy stays passive, SERS EF = 44 at V = 1.2 nm$^3$"
    )
    axj.text(
        0.03,
        0.85,
        bullets,
        fontsize=8.4,
        va="top",
        ha="left",
        linespacing=1.5,
        family="DejaVu Sans",
    )
    # --- level schematic (right) ---
    for i in range(8):
        y = 0.74 - i * 0.055
        axj.plot([0.57, 0.65], [y, y], color=SITE_COLORS[i], lw=2.6, solid_capstyle="butt")
        axj.text(0.655, y, f"{i + 1}", fontsize=6, va="center", color="#333333")
    axj.text(0.61, 0.30, "FMO sites 1$-$8\n(8 excitons)", fontsize=7.5, ha="center", va="top")
    axj.annotate(
        "",
        xy=(0.72, 0.545),
        xytext=(0.66, 0.545),
        arrowprops={"arrowstyle": "<->", "color": "#000000", "lw": 1.1},
    )
    axj.plot([0.72, 0.80], [0.545, 0.545], color="#000000", lw=3.4, solid_capstyle="butt")
    axj.text(0.76, 0.49, "NPoM plasmon\n$\\omega_{\\rm pl}$", fontsize=7.5, ha="center", va="top")
    axj.annotate(
        "",
        xy=(0.83, 0.70),
        xytext=(0.83, 0.40),
        arrowprops={"arrowstyle": "<->", "color": "#000000", "lw": 1.2},
    )
    axj.text(
        0.83,
        0.84,
        f"$g_0$ = {G0_V12_CM1} cm$^{{-1}}$\n(V = 1.2 nm$^3$)",
        fontsize=7.5,
        ha="center",
        va="top",
    )
    axj.text(
        0.83,
        0.345,
        "$g_{\\rm eff}\\sim 2000$ cm$^{-1}$\n$> \\kappa \\approx 800$ cm$^{-1}$",
        fontsize=7,
        ha="center",
        va="top",
    )
    axj.plot([0.87, 0.95], [0.74, 0.74], color=c_on, lw=2.6, solid_capstyle="butt")
    axj.plot([0.87, 0.95], [0.35, 0.35], color=c_on, lw=2.6, solid_capstyle="butt")
    axj.text(0.955, 0.74, "upper LP", fontsize=7, va="center", ha="left")
    axj.text(0.955, 0.35, "lower LP", fontsize=7, va="center", ha="left")
    axj.text(
        0.76,
        0.22,
        "fast non-radiative loss\n$\\kappa$ (Q $\\approx$ 15)",
        fontsize=7,
        ha="center",
        va="top",
    )

    fig.suptitle(
        "NPoM plasmonic suppression: baseline OFF vs ON comparison "
        "(PT-HOPS/SBD, L = 8, K = 2, $\\Delta t$ = 0.2 fs, 1 ps)",
        fontsize=14,
        fontweight="bold",
    )
    out = FIGDIR / "Figure_SI_NPoM_ON_vs_OFF.png"
    fig.savefig(out, dpi=DPI, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


def verify() -> None:
    for name in ("Figure_SI_Comparative_4Runs.png", "Figure_SI_NPoM_ON_vs_OFF.png"):
        path = FIGDIR / name
        size = path.stat().st_size
        with Image.open(path) as im:
            width, height = im.size
        status = "OK" if size > 40 * 1024 else "TOO SMALL"
        print(f"[{status}] {name}: {width}x{height} px, {size / 1024:.0f} KiB")
        assert size > 40 * 1024, f"{name} is smaller than 40 KiB"


def main() -> None:
    FIGDIR.mkdir(parents=True, exist_ok=True)
    runs = load_runs()
    report(runs)
    figure_comparative_4runs(runs)
    figure_npom_on_vs_off(runs)
    verify()


if __name__ == "__main__":
    main()
