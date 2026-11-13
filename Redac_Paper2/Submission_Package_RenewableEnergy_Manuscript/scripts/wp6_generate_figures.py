#!/usr/bin/env python3
"""
WP6: Generate 6 Publication-Grade Multi-Panel Figures for *Renewable Energy*
using ``scienceplots`` + ``seaborn`` at 600 DPI (PNG + vector PDF).

Reads verified outputs strictly from ``data/wp1..wp5`` without synthetic filler data.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scienceplots  # noqa: F401
import seaborn as sns

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FIG_DIR = BASE_DIR / "figures"

# Colorblind-safe Okabe-Ito scientific palette
PALETTE = sns.color_palette(["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#333333"])
CROP_LABELS = {
    "arabica_coffee": "Arabica Coffee (Foumbot)",
    "penja_white_pepper": "Penja White Pepper (Njombe)",
    "highland_tea": "Highland Tea (Djuttitsa)",
}
CROP_SHORT = {
    "arabica_coffee": "Coffee",
    "penja_white_pepper": "Penja Pepper",
    "highland_tea": "Tea",
}
CROP_COLORS = {
    "arabica_coffee": PALETTE[0],
    "penja_white_pepper": PALETTE[1],
    "highland_tea": PALETTE[2],
}


def setup_style() -> None:
    """Configure scienceplots + seaborn styling for clean journal typography."""
    plt.style.use(["science", "no-latex"])
    sns.set_context("paper", font_scale=1.05)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.labelsize": 10.5,
        "axes.titlesize": 11.0,
        "axes.titleweight": "bold",
        "xtick.labelsize": 9.2,
        "ytick.labelsize": 9.2,
        "legend.fontsize": 8.5,
        "figure.dpi": 150,
        "savefig.dpi": 600,
        "axes.grid": True,
        "grid.alpha": 0.28,
        "grid.linestyle": "--",
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def save_fig(fig: plt.Figure, stem: str) -> None:
    """Save figure cleanly in both vector PDF and 600 DPI PNG."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(FIG_DIR / f"{stem}.{ext}", bbox_inches="tight", dpi=600)
    plt.close(fig)


def plot_fig1_optical_pareto() -> None:
    """Fig 1: ST-OPV LUE Pareto Front, Spectral Transmittance & ePAR / R:FR Diagnostics."""
    df_tmm = pd.read_csv(DATA_DIR / "wp2" / "tmm_pareto_opv.csv")
    tmm_npz = np.load(DATA_DIR / "wp2" / "tmm_spectral_library.npz")
    wl = tmm_npz["wavelength_nm"]
    am15 = tmm_npz["am15_w_m2_nm"]
    apts = tmm_npz["design_apt_par"]
    t_beam = tmm_npz["T_beam"]
    t_diff = tmm_npz["T_diff"]

    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.3))

    # (a) LUE = PCE * APT Pareto frontier
    ax = axes[0]
    ap_grid = np.linspace(0.10, 0.62, 120)
    iso_pos = {2.5: 43.2, 3.5: 48.0, 4.5: 53.5}
    for lue_iso in (2.5, 3.5, 4.5):
        pce_iso = (lue_iso / 100.0) / ap_grid * 100.0
        mask = pce_iso <= 16.8
        ax.plot(ap_grid[mask] * 100.0, pce_iso[mask], ls=":", lw=1.0, color="#777777", alpha=0.8)
        ap_lbl = iso_pos[lue_iso]
        pce_lbl = (lue_iso / 100.0) / (ap_lbl / 100.0) * 100.0
        ax.text(
            ap_lbl,
            pce_lbl + 0.18,
            f"LUE={lue_iso:.1f}%",
            fontsize=7.3,
            color="#444444",
            ha="center",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.75),
        )

    non_par = df_tmm[df_tmm["is_pareto_all"] == 0]
    par = df_tmm[df_tmm["is_pareto_all"] == 1].sort_values("apt_par")
    ax.scatter(non_par["apt_par"] * 100.0, non_par["pce_pct"], s=20, color="#B0B8C0", alpha=0.65, label="Sub-optimal TMM stacks (n=96)")
    ax.plot(par["apt_par"] * 100.0, par["pce_pct"], "o-", color=PALETTE[0], ms=4.5, lw=1.8, label="LUE Pareto front (n=24)")
    focal_apts = [19.9, 35.0, 44.1, 52.1]
    for fa in focal_apts:
        sub = par.iloc[(par["apt_par"] * 100.0 - fa).abs().argsort()[:1]]
        ax.scatter(sub["apt_par"] * 100.0, sub["pce_pct"], s=65, color=PALETTE[1], edgecolor="black", zorder=5)
    ax.scatter([], [], s=65, color=PALETTE[1], edgecolor="black", label="Focal WP3/WP5 stacks")
    ax.set_xlabel("Average Photosynthetic Transmittance, APT (%)")
    ax.set_ylabel("Power Conversion Efficiency, PCE (%)")
    ax.set_title("(a) Coupled TMM PCE(APT) Pareto Front")
    ax.set_xlim(12, 60)
    ax.set_ylim(5.5, 16.5)
    ax.legend(loc="lower left", frameon=True, framealpha=0.92, fontsize=7.6)

    # (b) Spectral transmittance beam vs diffuse for APT ~35%, 44.1%, 52.1%
    ax = axes[1]
    ax.axvspan(400, 700, color="#E8F5E9", alpha=0.55, label="PAR (400–700 nm)")
    ax.axvspan(700, 750, color="#FFF3E0", alpha=0.65, label="ePAR Far-Red (700–750 nm)")
    am15_norm = am15 / np.max(am15) * 0.90
    ax.fill_between(wl, 0, am15_norm, color="#D8DEE9", alpha=0.45, label="AM1.5G norm.")

    target_apts = [(0.350, "APT 35.0%", PALETTE[0]), (0.441, "APT 44.1% (focal)", PALETTE[1]), (0.521, "APT 52.1%", PALETTE[2])]
    for tgt, lbl, col in target_apts:
        idx = int(np.argmin(np.abs(apts - tgt)))
        ax.plot(wl, t_beam[idx, 0, :] * 100.0, lw=1.8, color=col, label=f"{lbl} (0°)")
        ax.plot(wl, t_diff[idx, :] * 100.0, lw=1.2, ls="--", color=col, alpha=0.85)
    ax.set_xlim(320, 1050)
    ax.set_ylim(0, 88)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Transmittance $T_{\\mathrm{OPV}}(\\lambda)$ (%)")
    ax.set_title("(b) Spectral Shaping: Direct vs. Diffuse Sky")
    ax.legend(loc="upper right", ncol=2, fontsize=6.9, frameon=True, framealpha=0.93, columnspacing=0.8)

    # (c) ePAR/PAR and R:FR shift across Pareto stacks
    ax = axes[2]
    ax2 = ax.twinx()
    ax2.spines["top"].set_visible(False)
    l1 = ax.plot(par["apt_par"] * 100.0, par["epar_ratio"] / par["apt_par"], "o-", color=PALETTE[0], lw=1.8, ms=4, label="ePAR / PAR ratio")
    l2 = ax2.plot(par["apt_par"] * 100.0, par["r_fr_relative_change"] * 100.0, "s--", color=PALETTE[1], lw=1.7, ms=4, label="$\\Delta$(R:FR) vs. AM1.5G (%)")
    ax.axhline(1.0, color=PALETTE[0], ls=":", lw=0.9, alpha=0.6)
    ax2.axhline(0.0, color=PALETTE[1], ls=":", lw=0.9, alpha=0.6)
    ax.set_ylim(0.922, 1.016)
    ax2.set_ylim(-2.5, 40.0)
    ax.set_xlabel("Average Photosynthetic Transmittance, APT (%)")
    ax.set_ylabel("ePAR / PAR Transmittance Ratio", color=PALETTE[0])
    ax2.set_ylabel("Photomorphogenic R:FR Shift (%)", color=PALETTE[1])
    ax.set_title("(c) Sub-Canopy Biological Spectral Ratios")
    lines = l1 + l2
    labels = [ln.get_label() for ln in lines]
    ax.legend(lines, labels, loc="upper left", frameon=True, framealpha=0.92, fontsize=7.6)

    fig.tight_layout()
    save_fig(fig, "Fig1_Optical_Pareto_Spectral_TMM")


def plot_fig2_quantum_bound() -> None:
    """Fig 2: MesoHOPS v1.8.0 Benchmark, NESS |Delta_eta| Bound & Biological Attenuation."""
    with open(DATA_DIR / "wp2" / "mesohops_hpc_benchmark.json", "r", encoding="utf-8") as fh:
        mh = json.load(fh)["results"]
    df_q = pd.read_csv(DATA_DIR / "wp2" / "quantum_ness_spectra_matrix.csv")
    df_wp3 = pd.read_csv(DATA_DIR / "wp3" / "wp3_crop_microclimate_scenarios.csv")

    fig, axes = plt.subplots(1, 3, figsize=(14.4, 4.3))

    # (a) MesoHOPS v1.8.0 vs Modified Redfield/Pauli terminal Chl a population
    ax = axes[0]
    k_dl = "H3_MMSIC_MD_2025_full_DL_K1"
    k_vb = "H3_MMSIC_MD_2025_full_DL_K1_Vib340"
    t_dl = np.array(mh[k_dl]["t_axis_fs_sample"]) / 1000.0
    ax.plot(t_dl, mh[k_dl]["p_terminal_hops_sample"], lw=2.0, color=PALETTE[0], label=f"MesoHOPS H3 DL (MAE={mh[k_dl]['terminal_mae_0_tmax']:.3f})")
    ax.plot(t_dl, mh[k_dl]["p_terminal_pauli_sample"], lw=1.4, ls="--", color=PALETTE[0], alpha=0.85, label="Secular/Pauli H3 DL")
    t_vb = np.array(mh[k_vb]["t_axis_fs_sample"]) / 1000.0
    ax.plot(t_vb, mh[k_vb]["p_terminal_hops_sample"], lw=2.0, color=PALETTE[1], label=f"MesoHOPS H3 Vib340 (MAE={mh[k_vb]['terminal_mae_0_tmax']:.3f})")
    ax.plot(t_vb, mh[k_vb]["p_terminal_pauli_sample"], lw=1.4, ls=":", color=PALETTE[1], alpha=0.85, label="Secular/Pauli H3 Vib340")
    ax.set_xlabel("Relaxation Time (ps)")
    ax.set_ylabel("Terminal Chl a610–a612 Population")
    ax.set_title("(a) 14-Site LHCII Kinetics Benchmark (N=48)")
    ax.legend(loc="lower right", fontsize=7.5, frameon=True, framealpha=0.92)

    # (b) NESS |Delta_eta| across H1, H2, H3 & OPF spectra (beam vs diffuse)
    ax = axes[1]
    sub_q = df_q[df_q["spectrum"].str.startswith("STOPV_")].copy()
    sub_q["abs_deta_ppm"] = sub_q["delta_eta_vs_am15g"].abs() * 1e6
    sub_q["Ham"] = sub_q["hamiltonian"].map({
        "H1_Novoderezhkin2005_diag_PDA": "H1 (Novo. 2005)",
        "H2_Muh2010_diag_PDA": "H2 (Müh 2010)",
        "H3_MMSIC_MD_2025_full": "H3 (MMSIC 2025)",
    })
    sub_q["Regime"] = sub_q["regime"].map({
        "open_RC_no_NPQ": "Open RC (no NPQ)",
        "NPQ_1.5ns1": "Quenched (NPQ 1.5 ns$^{-1}$)",
    })
    sns.boxplot(data=sub_q, x="Ham", y="abs_deta_ppm", hue="Regime", ax=ax, palette=[PALETTE[0], PALETTE[3]], width=0.55)
    ax.axhline(33.7, color="#D55E00", ls="--", lw=1.1, label="Upper bound (33.7 ppm)")
    ax.set_ylim(0, 41.0)
    ax.set_xlabel("LHCII Exciton Hamiltonian")
    ax.set_ylabel("CW NESS $|\\Delta\\eta_{\\mathrm{ET}}|$ (ppm, $\\times 10^{-6}$)")
    ax.set_title("(b) Incoherent Sunlight EET Perturbation")
    ax.legend(loc="upper right", fontsize=7.4, frameon=True, framealpha=0.93)

    # (c) Scale attenuation: |Delta_eta_NESS| vs |Delta Y_quantum| vs |Delta Y_classical|
    ax = axes[2]
    comp_rows = []
    for crop in ("arabica_coffee", "penja_white_pepper", "highland_tea"):
        row = df_wp3[(df_wp3["crop"] == crop) & (df_wp3["scenario_id"] == "S3_OPV_APT44_GCR65")].iloc[0]
        classical_mag = max(abs(row["lever_par_pi_pct"]), abs(row["lever_therm_pct"]) + abs(row["lever_vpd_h2o_pct"]))
        quantum_y_mag = max(abs(row["eta_ness_ratio"] - 1.0) * 100.0, 1e-4)
        comp_rows.append({"Crop": CROP_SHORT[crop], "Mechanism": "Classical Microclimate / PAR (%)", "Magnitude_pct": classical_mag})
        comp_rows.append({"Crop": CROP_SHORT[crop], "Mechanism": "Spectral ePAR / R:FR (%)", "Magnitude_pct": abs(row["lever_spec_q_pct"])})
        comp_rows.append({"Crop": CROP_SHORT[crop], "Mechanism": "CW Quantum $|\\Delta\\eta_{\\mathrm{NESS}}|$ (%)", "Magnitude_pct": quantum_y_mag})
    df_comp = pd.DataFrame(comp_rows)
    sns.barplot(data=df_comp, x="Crop", y="Magnitude_pct", hue="Mechanism", ax=ax, palette=[PALETTE[0], PALETTE[4], PALETTE[1]])
    ax.set_yscale("log")
    ax.set_ylim(1e-4, 320.0)
    ax.set_xlabel("")
    ax.set_ylabel("Annual Crop Sensitivity Magnitude (%)")
    ax.set_title("(c) Micro-to-Canopy Scale Separation (Log)")
    ax.legend(loc="upper right", fontsize=7.2, frameon=True, framealpha=0.94)

    fig.tight_layout()
    save_fig(fig, "Fig2_Quantum_NESS_Bound_Benchmark")


def plot_fig3_microclimate_seasonal() -> None:
    """Fig 3: Leaf Cooling, Dry-vs-Monsoon Yield Inversion & ET Partitioning."""
    df_wp3 = pd.read_csv(DATA_DIR / "wp3" / "wp3_crop_microclimate_scenarios.csv")
    fig, axes = plt.subplots(1, 3, figsize=(14.4, 4.4))

    # (a) Dry-season leaf cooling dT_leaf & excess PV heating dT_pv across focal scenarios
    ax = axes[0]
    scen_pick = ["S1_agroforestry_shade", "S2_cSi_GCR40", "S3_OPV_APT44_GCR65"]
    scen_labels = {"S1_agroforestry_shade": "S1 Agroforestry", "S2_cSi_GCR40": "S2 c-Si GCR40", "S3_OPV_APT44_GCR65": "S3 OPV APT44"}
    sub_a = df_wp3[df_wp3["scenario_id"].isin(scen_pick)].copy()
    sub_a["Scenario"] = sub_a["scenario_id"].map(scen_labels)
    sub_a["Crop"] = sub_a["crop"].map(CROP_SHORT)
    sns.barplot(data=sub_a, x="Crop", y="dt_leaf_dry_day_c", hue="Scenario", ax=ax, palette=[PALETTE[2], PALETTE[6], PALETTE[1]])
    ax.axhline(0.0, color="black", lw=0.8)
    ax.set_ylim(-3.35, 0.10)
    ax.set_xlabel("")
    ax.set_ylabel("Dry-Season Daytime $\\Delta T_{\\mathrm{leaf}}$ (°C)")
    ax.set_title("(a) Canopy Leaf Cooling vs. Open Sun $S_0$")
    ax.legend(loc="lower center", ncol=2, fontsize=7.4, frameon=True, framealpha=0.93)

    # (b) Dry vs Wet yield inversion curve across Effective Shade (%) for Highland Tea & Coffee & Pepper
    ax = axes[1]
    for crop in ("arabica_coffee", "penja_white_pepper", "highland_tea"):
        sub_c = df_wp3[(df_wp3["crop"] == crop) & (df_wp3["technology"].isin(["ST_OPV_PM6Y6", "cSi_Opaque_AV"])) & (df_wp3["irrigated"] == 0)].sort_values("effective_shade_pct")
        ax.plot(sub_c["effective_shade_pct"], sub_c["delta_y_dry_pct"], ls="--", lw=1.4, color=CROP_COLORS[crop], alpha=0.8)
        ax.plot(sub_c["effective_shade_pct"], sub_c["delta_y_total_pct"], "o-", ms=3.2, lw=1.8, color=CROP_COLORS[crop], label=f"{CROP_SHORT[crop]} (Annual)")
        ax.plot(sub_c["effective_shade_pct"], sub_c["delta_y_wet_pct"], ls=":", lw=1.3, color=CROP_COLORS[crop], alpha=0.8)
    ax.axhline(0.0, color="black", lw=0.9)
    ax.text(46.0, 21.5, "Dry season (dashed): +9 to +30%", fontsize=7.4, color="#333333", ha="center", bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.82))
    ax.text(35.0, -30.5, "Monsoon (dotted): PAR deficit", fontsize=7.4, color="#333333", ha="center", bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.82))
    ax.set_xlabel("Effective Canopy Shading Factor (%)")
    ax.set_ylabel("Yield Anomaly $\\Delta Y$ vs. Open $S_0$ (%)")
    ax.set_title("(b) Dry-Season Rescue vs. Monsoon Light Deficit")
    ax.set_xlim(10, 72)
    ax.set_ylim(-42, 42)
    ax.legend(loc="upper left", fontsize=7.5, frameon=True, framealpha=0.93)

    # (c) Radiative vs Aerodynamic ET partitioning & WUE gain for S3_OPV_APT44_GCR65
    ax = axes[2]
    sub_c = df_wp3[df_wp3["scenario_id"] == "S3_OPV_APT44_GCR65"].copy()
    crops_ord = ["arabica_coffee", "penja_white_pepper", "highland_tea"]
    x = np.arange(len(crops_ord))
    rad_vals = [float(sub_c[sub_c["crop"] == c]["delta_et_rad_mm"].iloc[0]) for c in crops_ord]
    aero_vals = [float(sub_c[sub_c["crop"] == c]["delta_et_aero_mm"].iloc[0]) for c in crops_ord]
    wue_vals = [float(sub_c[sub_c["crop"] == c]["delta_wue_pct"].iloc[0]) for c in crops_ord]

    w = 0.34
    ax.bar(x - w / 2, rad_vals, width=w, color=PALETTE[0], label="$\\Delta ET_{\\mathrm{rad}}$ (mm/yr)")
    ax.bar(x + w / 2, aero_vals, width=w, color=PALETTE[4], label="$\\Delta ET_{\\mathrm{aero}}$ (mm/yr)")
    ax.axhline(0.0, color="black", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([CROP_SHORT[c] for c in crops_ord])
    ax.set_ylim(-118, 34)
    ax.set_ylabel("Annual Transpiration Shift (mm/yr)")
    ax.set_title("(c) Penman–Monteith $\\Delta ET_c$ & $\\Delta\\mathrm{WUE}$")
    ax_r = ax.twinx()
    ax_r.spines["top"].set_visible(False)
    l_wue = ax_r.plot(x, wue_vals, "D-", color=PALETTE[2], ms=6, lw=1.8, label="$\\Delta$WUE (%)")
    ax_r.set_ylabel("Water-Use Efficiency Gain $\\Delta$WUE (%)", color=PALETTE[2])
    ax_r.set_ylim(0, 18.5)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax_r.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="lower right", fontsize=7.4, frameon=True, framealpha=0.93)

    fig.tight_layout()
    save_fig(fig, "Fig3_Microclimate_Cooling_Dry_Wet_Regimes")


def plot_fig4_shapley_and_agro_phase() -> None:
    """Fig 4: Exact 4-Lever Shapley Attribution & 2D Dimensionless Agronomic Phase Diagram."""
    df_wp3 = pd.read_csv(DATA_DIR / "wp3" / "wp3_crop_microclimate_scenarios.csv")
    phase = np.load(DATA_DIR / "wp5" / "wp5_phase_maps.npz")
    with open(DATA_DIR / "wp5" / "wp5_validation_summary.json", "r", encoding="utf-8") as fh:
        be_sum = json.load(fh)["break_even_t80_by_crop"]

    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.0), gridspec_kw={"width_ratios": [1.08, 1.0]})

    # (a) Stacked/grouped 4-lever Shapley causal attribution
    ax = axes[0]
    picks = [
        ("arabica_coffee", "S3_OPV_APT56_GCR50", "Coffee\nOPV APT56"),
        ("arabica_coffee", "S3_OPV_APT44_GCR65", "Coffee\nOPV APT44"),
        ("penja_white_pepper", "S3_OPV_APT52_GCR65", "Pepper\nOPV APT52"),
        ("penja_white_pepper", "S3_OPV_APT44_GCR65", "Pepper\nOPV APT44"),
        ("highland_tea", "S3_OPV_APT56_GCR50", "Tea\nOPV APT56"),
        ("highland_tea", "S3_OPV_APT44_GCR65", "Tea\nOPV APT44"),
    ]
    x = np.arange(len(picks))
    levs = {"PAR_PI": [], "therm": [], "VPD_H2O": [], "spec_Q": [], "net": []}
    for crop, sid, _ in picks:
        row = df_wp3[(df_wp3["crop"] == crop) & (df_wp3["scenario_id"] == sid)].iloc[0]
        levs["PAR_PI"].append(row["lever_par_pi_pct"])
        levs["therm"].append(row["lever_therm_pct"])
        levs["VPD_H2O"].append(row["lever_vpd_h2o_pct"])
        levs["spec_Q"].append(row["lever_spec_q_pct"])
        levs["net"].append(row["delta_y_total_pct"])

    # Diverging stacked bars
    pos_base = np.zeros(len(picks))
    neg_base = np.zeros(len(picks))
    lever_meta = [
        ("PAR_PI", "PAR / Photoinhibition", PALETTE[0]),
        ("therm", "Leaf Thermal Cooling ($\\Delta T_l$)", PALETTE[1]),
        ("VPD_H2O", "Stomatal VPD & Soil $H_2O$", PALETTE[2]),
        ("spec_Q", "ePAR / R:FR / Quantum $\\eta_{\\mathrm{NESS}}$", PALETTE[3]),
    ]
    for k, lbl, col in lever_meta:
        vals = np.array(levs[k])
        pos_v = np.maximum(vals, 0.0)
        neg_v = np.minimum(vals, 0.0)
        ax.bar(x, pos_v, bottom=pos_base, width=0.58, color=col, alpha=0.88, label=lbl)
        ax.bar(x, neg_v, bottom=neg_base, width=0.58, color=col, alpha=0.88)
        pos_base += pos_v
        neg_base += neg_v
    ax.plot(x, levs["net"], "ko-", lw=1.4, ms=5.5, label="Net $\\Delta Y_{\\mathrm{annual}}$ (%)")
    ax.axhline(0.0, color="black", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([p[2] for p in picks], fontsize=8.5)
    ax.set_ylim(-24.0, 34.5)
    ax.set_ylabel("Yield Attribution $\\Delta Y$ (% vs. Open $S_0$)")
    ax.set_title("(a) Exact Four-Lever Shapley Causal Attribution")
    ax.legend(loc="upper left", ncol=2, fontsize=7.0, frameon=True, framealpha=0.93, columnspacing=0.8)

    # (b) 2D Agronomic Regime Phase Map (PAR_peak / I_sat vs VPD_peak)
    ax = axes[1]
    par_g = phase["agro_par_ratio_grid"]
    vpd_g = phase["agro_vpd_peak_grid"]
    dy_g = phase["agro_delta_y_pct"].T  # shape (len(vpd), len(par)) for contourf(X=par, Y=vpd)
    cf = ax.contourf(par_g, vpd_g, dy_g, levels=np.linspace(-24, 24, 25), cmap="BrBG", extend="both")
    cs = ax.contour(par_g, vpd_g, dy_g, levels=[0.0], colors=["black"], linewidths=[2.0])
    txts = ax.clabel(cs, fmt={0.0: "Neutral ($\\Delta Y = 0\\%$)"}, fontsize=8.0, inline=True, manual=[(1.93, 2.15)])
    for t in txts:
        t.set_bbox(dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    ax.axvline(par_g.max(), color="#666666", ls=":", lw=1.0)
    cbar = fig.colorbar(cf, ax=ax, pad=0.02)
    cbar.set_label("Expected Shade Yield Shift $\\Delta Y$ (%)")

    # Plot Cameroon sites onto Phase Space with zero-overlap leader arrows
    site_offsets = {
        "arabica_coffee": (2.30, 3.60),
        "highland_tea": (2.36, 3.05),
        "penja_white_pepper": (1.42, 2.75),
    }
    for crop in ("arabica_coffee", "penja_white_pepper", "highland_tea"):
        px = be_sum[crop]["site_par_over_isat"]
        py = be_sum[crop]["site_dry_vpd_p95_kpa"]
        ox, oy = site_offsets[crop]
        ax.scatter(px, py, s=110, color=CROP_COLORS[crop], edgecolor="white", linewidth=1.6, zorder=6)
        ax.annotate(
            CROP_SHORT[crop],
            xy=(px, py),
            xytext=(ox, oy),
            fontsize=8.3,
            fontweight="bold",
            color="black",
            ha="center",
            va="center",
            arrowprops=dict(arrowstyle="-|>", color=CROP_COLORS[crop], lw=1.1, shrinkA=2, shrinkB=6),
            bbox=dict(boxstyle="round,pad=0.22", fc="white", ec=CROP_COLORS[crop], alpha=0.92),
            zorder=7,
        )
    ax.set_xlim(par_g.min(), 2.65)
    ax.set_ylim(vpd_g.min(), vpd_g.max())
    ax.set_xlabel("Dimensionless Solar Load ($\\mathrm{PAR}_{95} / I_{\\mathrm{sat}}$)")
    ax.set_ylabel("Dry-Season Peak Vapor Pressure Deficit $\\mathrm{VPD}_{95}$ (kPa)")
    ax.set_title("(b) Dimensionless Agronomic Regime Phase Map")

    fig.tight_layout()
    save_fig(fig, "Fig4_Four_Lever_Causal_Attribution_Phase")


def plot_fig5_tea_lca_breakeven() -> None:
    """Fig 5: Cooperative BESS Dispatch, Dual-FU ISO LCA & 2D Tech Break-Even Surface."""
    df_wp5 = pd.read_csv(DATA_DIR / "wp5" / "wp5_tea_lca_scenarios.csv")
    phase = np.load(DATA_DIR / "wp5" / "wp5_phase_maps.npz")

    fig, axes = plt.subplots(1, 3, figsize=(14.6, 4.5))

    # (a) 3-Way LFP BESS Trade-off on Highland Tea & Tri-Crop Comparison (S3_OPV_APT44_GCR65)
    ax = axes[0]
    sub_b = df_wp5[(df_wp5["scenario_id"] == "S3_OPV_APT44_GCR65") & (df_wp5["wp5_variant"] == "baseline_zero_credit")].copy()
    sub_b["Crop"] = sub_b["crop"].map(CROP_SHORT)
    sub_b["BESS"] = sub_b["bess_option"].map({
        "no_bess_daytime_only": "No BESS (Daytime)",
        "small_lfp_buffer_2h": "2h LFP Buffer",
        "overnight_withering_bess": "Overnight BESS",
    })
    sub_b["NPV_k"] = sub_b["npv_usd_ha"] / 1000.0
    sns.barplot(data=sub_b, x="Crop", y="NPV_k", hue="BESS", ax=ax, palette=[PALETTE[5], PALETTE[0], PALETTE[2]])
    tea_lsf = sub_b[sub_b["crop"] == "highland_tea"].set_index("bess_option")["load_solar_fraction_pct"]
    ax.text(2.0, 925, f"Tea LSF:\n{tea_lsf['no_bess_daytime_only']:.1f}%→{tea_lsf['overnight_withering_bess']:.1f}%", ha="center", fontsize=7.6, bbox=dict(fc="#F8F9FA", ec="#CCCCCC"))
    ax.set_xlabel("")
    ax.set_ylabel("20-Year NPV (kUSD/ha, Zero Credits)")
    ax.set_ylim(0, 1080)
    ax.set_title("(a) Cooperative BESS Dispatch Value (ST-OPV)")
    ax.legend(loc="upper left", fontsize=7.6, frameon=True, framealpha=0.93)

    # (b) Dual-FU LCA (gCO2e/kWh) across S2 c-Si, S3 5-yr OPV & S4 15/25-yr OPV
    ax = axes[1]
    lca_rows = []
    for crop in ("arabica_coffee", "penja_white_pepper", "highland_tea"):
        bess_ref = "overnight_withering_bess" if crop == "highland_tea" else "small_lfp_buffer_2h"
        for sid, var, lbl in [
            ("S3_OPV_APT44_GCR65", "baseline_zero_credit", "S3 OPV (T80=5 yr)"),
            ("S3_OPV_APT44_GCR65", "S4_OPV_encapsulated_T80_15yr", "S4 OPV (T80=15 yr)"),
            ("S3_OPV_APT44_GCR65", "S4_OPV_encapsulated_T80_25yr", "S4 OPV (T80=25 yr)"),
            ("S2_cSi_GCR40", "baseline_zero_credit", "S2 c-Si (25 yr)"),
        ]:
            match = df_wp5[(df_wp5["crop"] == crop) & (df_wp5["scenario_id"] == sid) & (df_wp5["wp5_variant"] == var) & (df_wp5["bess_option"] == bess_ref)]
            if len(match):
                lca_rows.append({"Crop": CROP_SHORT[crop], "System": lbl, "gCO2_kWh": float(match["lca_pv_intensity_gco2e_kwh"].iloc[0])})
    df_lca = pd.DataFrame(lca_rows)
    sns.barplot(data=df_lca, x="Crop", y="gCO2_kWh", hue="System", ax=ax, palette=[PALETTE[1], PALETTE[4], PALETTE[2], PALETTE[6]])
    ax.set_ylim(0, 42.0)
    ax.set_xlabel("")
    ax.set_ylabel("Embodied PV Carbon Intensity ($\\mathrm{gCO_2e/kWh}$)")
    ax.set_title("(b) Dual-FU ISO LCA: 5-yr Replacement Penalty")
    ax.legend(loc="upper left", fontsize=7.4, frameon=True, framealpha=0.93)

    # (c) 2D Tech Break-Even Surface (T80_opv, C_mod_OPV / C_BOS_cSi) for Penja White Pepper
    ax = axes[2]
    t80_g = phase["tech_t80_grid"]
    ratio_g = phase["tech_cost_ratio_grid"]
    dnpv_p = phase["penja_white_pepper_delta_npv_grid"].T / 1000.0  # shape (ratio, t80)
    dlca_p = phase["penja_white_pepper_delta_lca_grid"].T
    cf = ax.contourf(t80_g, ratio_g, dnpv_p, levels=np.linspace(-250, 150, 21), cmap="RdYlGn", extend="both")
    cs_npv = ax.contour(t80_g, ratio_g, dnpv_p, levels=[0.0], colors=["black"], linewidths=[2.0])
    t_npv = ax.clabel(cs_npv, fmt={0.0: "$\\Delta\\mathrm{NPV}=0$"}, fontsize=7.8, inline=True, manual=[(11.8, 0.24)])
    for t in t_npv:
        t.set_bbox(dict(boxstyle="round,pad=0.14", fc="white", ec="none", alpha=0.82))
    ax.contour(t80_g, ratio_g, dlca_p, levels=[0.0], colors=[PALETTE[0]], linestyles=["--"], linewidths=[2.0])
    ax.text(8.1, 0.50, "$\\Delta\\mathrm{LCA}=0$\n(7.4 yr)", fontsize=7.6, color=PALETTE[0], fontweight="bold", ha="left", va="center", bbox=dict(boxstyle="round,pad=0.20", fc="white", ec=PALETTE[0], alpha=0.90))
    # Mark baseline (T80=5, C_mod=35/55=0.636) and R2R target (T80=16.3, C_mod=15/55=0.273)
    ax.scatter([5.0], [35.0 / 55.0], s=75, color=PALETTE[1], edgecolor="black", zorder=6, label="Baseline ($T_{80}=5$ yr, \\$35/m$^2$)")
    ax.scatter([16.33], [15.0 / 55.0], s=95, marker="*", color=PALETTE[2], edgecolor="black", zorder=6, label="R2R Parity (\\$15/m$^2$, 16.3 yr)")
    cbar = fig.colorbar(cf, ax=ax, pad=0.02)
    cbar.set_label("$\\Delta\\mathrm{NPV}$ (ST-OPV $-$ c-Si, kUSD/ha)")
    ax.set_xlabel("ST-OPV Operational Lifetime $T_{80}$ (yr)")
    ax.set_ylabel("Module-to-BOS Cost Ratio ($C_{\\mathrm{mod}}^{\\mathrm{OPV}} / C_{\\mathrm{BOS}}^{\\mathrm{c-Si}}$)")
    ax.set_title("(c) Break-Even Frontier (Penja Pepper)")
    ax.legend(loc="upper right", fontsize=7.1, frameon=True, framealpha=0.93)

    fig.tight_layout()
    save_fig(fig, "Fig5_Dispatch_TEA_LCA_BreakEven")


def plot_fig6_sobol_policy() -> None:
    """Fig 6: N=10,000 Sobol Distributions, Variance Attribution & Policy/LER Sensitivities."""
    with open(DATA_DIR / "wp5" / "wp5_sobol_sensitivity.json", "r", encoding="utf-8") as fh:
        sob = json.load(fh)
    df_wp5 = pd.read_csv(DATA_DIR / "wp5" / "wp5_tea_lca_scenarios.csv")

    fig, axes = plt.subplots(1, 3, figsize=(14.6, 4.4))

    # (a) Probabilistic Delta NPV (OPV - c-Si) percentile bars & p05-p95 spread
    ax = axes[0]
    crops_ord = ["arabica_coffee", "penja_white_pepper", "highland_tea"]
    y_pos = np.arange(len(crops_ord))
    for idx, c in enumerate(crops_ord):
        st = sob[c]["delta_npv_opv_minus_csi_stats_usd_ha"]
        p05, p50, p95 = st["p05"] / 1000.0, st["p50"] / 1000.0, st["p95"] / 1000.0
        prob = st["prob_opv_beats_csi"] * 100.0
        ax.plot([p05, p95], [idx, idx], lw=6.0, color=CROP_COLORS[c], alpha=0.55)
        ax.scatter([p50], [idx], s=90, color=CROP_COLORS[c], edgecolor="black", zorder=5)
        ax.text(p95 + 16.0, idx, f"P(>c-Si)={prob:.1f}%", va="center", fontsize=8.2, fontweight="bold")
    ax.axvline(0.0, color="black", ls="--", lw=1.3)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([CROP_SHORT[c] for c in crops_ord])
    ax.set_xlim(-540, 395)
    ax.set_xlabel("$\\Delta\\mathrm{NPV}$ (ST-OPV $-$ c-Si, kUSD/ha) [p05–p50–p95]")
    ax.set_title("(a) $N=10\\,000$ QMC Comparative Parity")

    # (b) Ranked Total-Order Sobol S_Ti indices (including bounded quantum NESS lever)
    ax = axes[1]
    # All levers (including the quantum NESS lever) are read from the SAME output
    # (Delta NPV = NPV_OPV - NPV_cSi) so that indices are directly comparable.
    penja_diff = sob["penja_white_pepper"]["sobol_delta_npv_opv_vs_csi"]
    q_sti = penja_diff["eta_ness_shift_pct"]["S_Ti"]
    q_exp = int(np.floor(np.log10(q_sti))) if q_sti > 0 else -12
    q_man = q_sti / 10.0**q_exp if q_sti > 0 else 0.0
    driver_names = {
        "c_mod_opv_usd_m2": "OPV Module Cost ($C_{\\mathrm{mod}}$)",
        "t80_opv_yr": "OPV Lifetime ($T_{80}$)",
        "c_bos_si_usd_m2": "c-Si BOS Cost ($C_{\\mathrm{BOS}}^{\\mathrm{Si}}$)",
        "export_tariff_usd_kwh": "Grid Export Tariff",
        "wacc": "Discount Rate (WACC)",
        "c_bos_opv_usd_m2": "OPV Tensile BOS Cost",
        "eta_ness_shift_pct": "Quantum NESS ($\\Delta\\eta_{\\mathrm{NESS}}$)",
    }
    keys_show = ["c_mod_opv_usd_m2", "t80_opv_yr", "c_bos_si_usd_m2", "export_tariff_usd_kwh", "wacc", "c_bos_opv_usd_m2", "eta_ness_shift_pct"]
    df_s = pd.DataFrame([
        {
            "Parameter": driver_names[k],
            "S_i (1st-order)": penja_diff[k]["S_i"],
            "S_Ti (Total)": penja_diff[k]["S_Ti"],
        }
        for k in keys_show
    ])
    y_i = np.arange(len(df_s))
    ax.barh(y_i + 0.18, df_s["S_Ti (Total)"], height=0.34, color=PALETTE[0], label="Total-order $S_{Ti}$")
    ax.barh(y_i - 0.18, df_s["S_i (1st-order)"], height=0.34, color=PALETTE[5], label="First-order $S_i$")
    ax.text(0.015, y_i[-1], f"$S_{{Ti}} = {q_man:.1f} \\times 10^{{{q_exp}}}$ (bounded)", va="center", fontsize=8.0, color=PALETTE[1], fontweight="bold")
    ax.set_yticks(y_i)
    ax.set_yticklabels(df_s["Parameter"], fontsize=8.3)
    ax.invert_yaxis()
    ax.set_xlim(0.0, 0.42)
    ax.set_xlabel("Sobol index on $\\Delta$NPV (Penja pepper)")
    ax.set_title("(b) Classical Drivers vs. Quantum Bound")
    ax.legend(loc="lower right", fontsize=7.8, frameon=True, framealpha=0.93)

    # (c) S5 Policy & Financial Stress Scenarios across the 3 crops (NPV kUSD/ha)
    ax = axes[2]
    var_map = {
        "baseline_zero_credit": "Baseline (0 USD/t, 0%)",
        "S5_certified_crop_price": "PGI / Cert. Price",
        "S5_carbon25_policy": "Carbon (25 USD/tCO$_2$e)",
        "S5_subsidy40_policy": "CAPEX Subsidy 40%",
        "S5_wacc_6pct": "Low WACC (6%)",
        "S5_wacc_15pct": "High WACC (15%)",
        "S5_offgrid_no_export": "Off-Grid (No Export)",
    }
    sub_p = df_wp5[
        (df_wp5["scenario_id"] == "S3_OPV_APT44_GCR65")
        & (df_wp5["wp5_variant"].isin(var_map.keys()))
        & (
            ((df_wp5["crop"] == "highland_tea") & (df_wp5["bess_option"] == "overnight_withering_bess"))
            | ((df_wp5["crop"] != "highland_tea") & (df_wp5["bess_option"] == "small_lfp_buffer_2h"))
        )
    ].copy()
    sub_p["Policy Regime"] = sub_p["wp5_variant"].map(var_map)
    sub_p["Crop"] = sub_p["crop"].map(CROP_SHORT)
    sub_p["NPV_k"] = sub_p["npv_usd_ha"] / 1000.0
    sns.barplot(data=sub_p, y="Policy Regime", x="NPV_k", hue="Crop", ax=ax, palette=[CROP_COLORS["arabica_coffee"], CROP_COLORS["penja_white_pepper"], CROP_COLORS["highland_tea"]], order=list(var_map.values()))
    ax.axvline(0.0, color="black", lw=0.9)
    ax.set_xlim(-460, 1420)
    ax.set_ylabel("")
    ax.set_xlabel("20-Year System NPV (kUSD/ha)")
    ax.set_title("(c) Policy, Valuation & Off-Grid Stress Tests")
    ax.legend(loc="lower right", fontsize=7.6, frameon=True, framealpha=0.93)

    fig.tight_layout()
    save_fig(fig, "Fig6_Sobol_Uncertainty_LER_Policy")


def main() -> None:
    setup_style()
    plot_fig1_optical_pareto()
    plot_fig2_quantum_bound()
    plot_fig3_microclimate_seasonal()
    plot_fig4_shapley_and_agro_phase()
    plot_fig5_tea_lca_breakeven()
    plot_fig6_sobol_policy()
    print("✅ WP6: Generated all 6 high-resolution figures (PDF + 600 DPI PNG) in figures/")


if __name__ == "__main__":
    main()
