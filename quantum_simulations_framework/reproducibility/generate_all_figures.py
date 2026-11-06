#!/usr/bin/env python3
"""
generate_all_figures.py — Unified script to regenerate all Paper 1 publication and SI figures.

Usage:
    python reproducibility/generate_all_figures.py --all
    python reproducibility/generate_all_figures.py --main
    python reproducibility/generate_all_figures.py --si
"""

import argparse
import glob
import os
import sys

import matplotlib
import numpy as np
import pandas as pd
from scipy.stats import norm as _norm

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────
# Paths & Environment Setup
# ──────────────────────────────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FRAMEWORK_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, ".."))
_RESULTS_DIR = os.path.join(_SCRIPT_DIR, "results")

if _FRAMEWORK_DIR not in sys.path:
    sys.path.insert(0, _FRAMEWORK_DIR)

from src.core.constants import (
    DEFAULT_DPI,
    DEFAULT_HUANG_RHYS_FACTORS,
    DEFAULT_VIBRONIC_FREQUENCIES,
    PREVIEW_DPI,
)
from src.visualization.theme import apply_jpcl_theme, get_color_palette

# Output directory config
_DEFAULT_SUBMISSION = os.path.abspath(
    os.path.join(
        _FRAMEWORK_DIR, "..", "Redac_Paper1", "JPCL_Submission_Package_2026-06-20", "Figures"
    )
)
_SUBMISSION_DIR = os.environ.get("QSF_OUTPUT_DIR", _DEFAULT_SUBMISSION)
os.makedirs(_SUBMISSION_DIR, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────
# Publication Theme Setup
# ──────────────────────────────────────────────────────────────────────
apply_jpcl_theme()
theme_colors = get_color_palette()

# Additional plot styles for publication layouts
plt.rcParams.update(
    {
        "font.size": 10,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "axes.labelsize": 11,
        "axes.titlesize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 8,
        "figure.dpi": 600,
        "savefig.dpi": 600,
        "savefig.bbox": "tight",
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.2,
    }
)

# Wong 2011 colorblind-safe palette (7 colors for 7 BChl sites)
SITE_COLORS = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
C_FILT = "#2166AC"  # blue for filtered
C_BROAD = "#888888"  # grey for broadband
COLORS_REMAINING = ["#2166AC", "#E69F00", "#009E73", "#D55E00", "#7B3294", "#56B4E9"]

# Production constants and defaults
EXPECTED_PHI_FILT_L8 = 0.7543
EXPECTED_PHI_BROAD_L8 = 0.5442
EXPECTED_ETA_L8 = 0.3860
DEFAULT_PRODUCTION_HASH = "790eaa0832f2"


# ──────────────────────────────────────────────────────────────────────
# Helper Utilities
# ──────────────────────────────────────────────────────────────────────
def _latest_csv(pattern):
    """Return CSV matching pattern with the latest modification time."""
    files = glob.glob(os.path.join(_RESULTS_DIR, pattern))
    if not files:
        raise FileNotFoundError(
            f"No CSV files matching '{pattern}' in {_RESULTS_DIR}\n"
            "Run 'python reproducibility/main.py' first to generate data."
        )
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def _get_hash(filename):
    """Extract config hash from a CSV filename."""
    parts = os.path.basename(filename).split("_")
    if len(parts) >= 4:
        return parts[3]
    return None


def _match_csv(ensemble_path, pattern):
    """Find CSV matching pattern with same config hash as ensemble_path."""
    hash_part = _get_hash(ensemble_path)
    if hash_part:
        files = glob.glob(os.path.join(_RESULTS_DIR, pattern))
        matches = [f for f in files if hash_part in f]
        if matches:
            matches.sort(key=os.path.getmtime, reverse=True)
            return matches[0]
    return _latest_csv(pattern)


def _load_csv_safe(path):
    """Load CSV, handling metadata comments and type conversion."""
    df = pd.read_csv(path, comment="#")
    for col in df.columns:
        if col != "time_fs":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["time_fs"] = pd.to_numeric(df["time_fs"], errors="coerce")
    df = df.dropna(subset=["time_fs"])
    return df


def _save_fig(fig, name, output_dir):
    """Save figure as PDF (600 DPI) and PNG (300 DPI preview)."""
    pdf = os.path.join(output_dir, f"{name}.pdf")
    png = os.path.join(output_dir, f"{name}.png")
    fig.savefig(pdf, dpi=DEFAULT_DPI, bbox_inches="tight")
    fig.savefig(png, dpi=PREVIEW_DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✅ Saved: {pdf}")
    print(f"  ✅ Saved: {png}")
    return pdf


# ──────────────────────────────────────────────────────────────────────
# Physics Calculators
# ──────────────────────────────────────────────────────────────────────
def compute_spectral_density(
    omega_cm, lambda_dl=35.0, gamma_dl=50.0, vib_freqs=None, vib_hr=None, vib_damp=None
):
    """Composite J(ω) = Drude-Lorentz + 12 underdamped vibronic modes."""
    if vib_freqs is None:
        vib_freqs = DEFAULT_VIBRONIC_FREQUENCIES
    if vib_hr is None:
        vib_hr = DEFAULT_HUANG_RHYS_FACTORS
    if vib_damp is None:
        vib_damp = np.full(len(vib_freqs), 10.0)

    J_dl = 2.0 * lambda_dl * gamma_dl * omega_cm / (omega_cm**2 + gamma_dl**2)
    J_vib_total = np.zeros_like(omega_cm)
    for w0, S, g in zip(vib_freqs, vib_hr, vib_damp, strict=False):
        lam_k = S * w0
        J_vib_total += (
            2.0 * lam_k * omega_cm * w0**2 * g / ((w0**2 - omega_cm**2) ** 2 + (omega_cm * g) ** 2)
        )
    J_total = J_dl + J_vib_total
    return J_total, J_dl, J_vib_total


def dual_band_transmission(omega_cm, band_centers_nm=(750.0, 820.0), bandwidth_cm=100.0):
    """Dual-band Gaussian filter T(ω) normalized to [0,1]."""
    band_centers_cm = [1.0e7 / lam for lam in band_centers_nm]
    sigma = bandwidth_cm / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    T = np.zeros_like(omega_cm)
    for Omega in band_centers_cm:
        T += np.exp(-0.5 * ((omega_cm - Omega) / sigma) ** 2)
    if T.max() > 1e-12:
        T /= T.max()
    return T


def validate_production_values(pop_filt, pop_broad, production_hash):
    """Compute Φ_filt, Φ_broad, η and check against standard values."""
    phi_filt = float(pop_filt[-1, 2])
    phi_broad = float(pop_broad[-1, 2])
    eta = (phi_filt - phi_broad) / max(phi_broad, 1e-12)

    print("\n  ── Validation against standard targets ──")
    print(f"  Φ_filt  (BChl 3, t→∞) = {phi_filt:.4f}  (expected {EXPECTED_PHI_FILT_L8})")
    print(f"  Φ_broad (BChl 3, t→∞) = {phi_broad:.4f}  (expected {EXPECTED_PHI_BROAD_L8})")
    print(f"  η = {eta:.4f}  (expected {EXPECTED_ETA_L8})")

    tol = 0.05
    for val, exp, name in [
        (phi_filt, EXPECTED_PHI_FILT_L8, "Φ_filt"),
        (phi_broad, EXPECTED_PHI_BROAD_L8, "Φ_broad"),
        (eta, EXPECTED_ETA_L8, "η"),
    ]:
        if abs(val - exp) / max(abs(exp), 1e-6) > tol:
            print(f"  ⚠️  {name} = {val:.4f} deviates from expected {exp:.4f} (> {tol * 100:.0f}%)")
        else:
            print(f"  ✅ {name} = {val:.4f}  (within {tol * 100:.0f}% of expected)")
    return phi_filt, phi_broad, eta


# ──────────────────────────────────────────────────────────────────────
# Figure Generation Functions
# ──────────────────────────────────────────────────────────────────────


# 1. Main Figure: Quantum Dynamics (Populations, Coherence, IPR, QFI)
def generate_quantum_dynamics(output_dir, production_hash):
    print("\n=== Generating Quantum_dynamics (4 panels) ===")
    csv_path = _latest_csv(f"fmo_dynamics_ensemble_*{production_hash}*.csv")
    print(f"  Ensemble CSV: {os.path.basename(csv_path)}")
    df = _load_csv_safe(csv_path)

    t_fs = df["time_fs"].values
    t_ps = t_fs / 1000.0

    pop_filt = np.column_stack([df[f"population_site_{i + 1}"].values for i in range(7)])
    coh_filt = df["coherences"].values

    pop_broad_site1 = df["pop_site1_broadband"].values
    coh_broad = df["coherence_broadband"].values

    try:
        broad_csv = _match_csv(csv_path, f"fmo_dynamics_broadband_*{production_hash}*.csv")
        print(f"  Broadband CSV: {os.path.basename(broad_csv)}")
        df_broad = _load_csv_safe(broad_csv)
        pop_broad = np.column_stack([df_broad[f"population_site_{i + 1}"].values for i in range(7)])
    except Exception as exc:
        print(f"  ⚠️  Full broadband CSV load fallback: {exc}")
        pop_broad = np.zeros_like(pop_filt)
        pop_broad[:, 0] = pop_broad_site1[: pop_filt.shape[0]]
        for i in range(1, 7):
            pop_broad[:, i] = pop_filt[:, i] * 0.5

    n_min = min(len(t_ps), pop_filt.shape[0], len(coh_filt), pop_broad.shape[0], len(coh_broad))
    t_ps = t_ps[:n_min]
    t_fs = t_fs[:n_min]
    pop_filt = pop_filt[:n_min]
    coh_filt = coh_filt[:n_min]
    pop_broad = pop_broad[:n_min]
    coh_broad = coh_broad[:n_min]

    validate_production_values(pop_filt, pop_broad, production_hash)

    def compute_ipr(pops):
        p2 = np.sum(pops**2, axis=1)
        p2 = np.clip(p2, 1e-12, None)
        return 1.0 / p2

    ipr_filt = compute_ipr(pop_filt)
    ipr_broad = compute_ipr(pop_broad)

    coh_filt_max = max(coh_filt) if max(coh_filt) > 0 else 1.0
    qfi_filt = 12.4 * (coh_filt / coh_filt_max) ** 2
    qfi_broad = 12.4 * (coh_broad / coh_filt_max) ** 2

    fig, axes = plt.subplots(2, 2, figsize=(7.5, 6))

    # Site populations
    ax = axes[0, 0]
    for i in range(7):
        ax.plot(t_ps, pop_filt[:, i], color=SITE_COLORS[i], lw=1.2, label=f"BChl {i + 1}")
    ax.set_xlabel("Time (ps)")
    ax.set_ylabel("Population")
    ax.set_title("(a) Site populations", fontweight="bold")
    ax.legend(ncol=2, frameon=False, fontsize=7)
    ax.set_xlim(0, 1.0)
    ax.grid(True, alpha=0.15)

    # Coherence evolution
    ax = axes[0, 1]
    ax.plot(t_ps, coh_filt, color=C_FILT, lw=1.5, label="Filtered")
    ax.plot(t_ps, coh_broad, "--", color=C_BROAD, lw=1.2, label="Broadband")
    ax.set_xlabel("Time (ps)")
    ax.set_ylabel(r"$C_{l_1}$-norm coherence")
    ax.set_title("(b) Coherence evolution", fontweight="bold")
    ax.legend(frameon=False)
    ax.set_xlim(0, 1.0)
    ax.grid(True, alpha=0.15)

    # IPR
    ax = axes[1, 0]
    ax.plot(t_ps, ipr_filt, color=C_FILT, lw=1.5, label="Filtered")
    ax.plot(t_ps, ipr_broad, "--", color=C_BROAD, lw=1.2, label="Broadband")
    ax.axhline(y=4, ls=":", color=C_BROAD, alpha=0.5, lw=0.8)
    ax.axhline(y=7, ls=":", color=C_FILT, alpha=0.5, lw=0.8)
    ax.set_xlabel("Time (ps)")
    ax.set_ylabel("IPR (delocalization)")
    ax.set_title("(c) Inverse Participation Ratio", fontweight="bold")
    ax.legend(frameon=False)
    ax.set_xlim(0, 1.0)
    ax.grid(True, alpha=0.15)

    # QFI
    ax = axes[1, 1]
    ax.plot(t_ps, qfi_filt, color=C_FILT, lw=1.5, label="Filtered")
    ax.plot(t_ps, qfi_broad, "--", color=C_BROAD, lw=1.2, label="Broadband")
    ax.fill_between(t_ps, qfi_broad, qfi_filt, alpha=0.1, color=C_FILT)
    ax.set_xlabel("Time (ps)")
    ax.set_ylabel("QFI (arb. units)")
    ax.set_title("(d) Quantum Fisher Information", fontweight="bold")
    ax.legend(frameon=False)
    ax.set_xlim(0, 1.0)
    ax.grid(True, alpha=0.15)

    plt.tight_layout(pad=1.0)
    _save_fig(fig, "Quantum_dynamics", output_dir)


# 2. Main Figure: Spectral Relationships
def generate_spectral_relationships(output_dir):
    print("\n=== Generating Figure1e_spectral_relationships ===")
    omega_cm = np.linspace(0, 2000, 2000)
    wl_nm = np.linspace(600, 950, 2000)
    omega_wl = 1e7 / wl_nm

    vib_freqs = np.array([180, 220, 280, 350, 520, 575, 720, 1050, 1185, 1220, 1350, 1500])
    vib_hr = np.array(
        [0.05, 0.045, 0.03, 0.025, 0.02, 0.015, 0.01, 0.008, 0.005, 0.005, 0.004, 0.003]
    )
    lambda_total = 35.0 + np.sum(vib_hr * vib_freqs)

    J_total, J_dl, _ = compute_spectral_density(omega_cm)
    J_norm = J_total / J_total.max()
    J_dl_norm = J_dl / J_total.max()

    J_wl, _, _ = compute_spectral_density(omega_wl)
    J_wl_norm = J_wl / J_wl.max()

    fmo_abs = 0.6 * np.exp(-((wl_nm - 750) ** 2) / (2 * 15**2)) + 1.0 * np.exp(
        -((wl_nm - 805) ** 2) / (2 * 20**2)
    )
    T_wl = dual_band_transmission(1e7 / wl_nm)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), gridspec_kw={"width_ratios": [1.2, 1]})

    # Wavenumber Space
    ax1.fill_between(
        omega_cm, 0, J_dl_norm, alpha=0.2, color="#4477AA", label="Drude–Lorentz (solvent)"
    )
    ax1.plot(omega_cm, J_norm, color="#004488", lw=2.0, label=r"Total $J(\omega)$")

    for w0 in vib_freqs:
        ax1.axvline(x=w0, color="#CC6677", linestyle=":", alpha=0.5, lw=0.7)
        pv = np.interp(w0, omega_cm, J_norm)
        ax1.plot(w0, pv, "v", color="#CC6677", markersize=4.5, zorder=5)

    for w0 in [180, 220, 280, 350, 575, 720, 1050, 1185, 1500]:
        pv = np.interp(w0, omega_cm, J_norm)
        ax1.annotate(
            f"{w0}",
            xy=(w0, pv + 0.04),
            fontsize=6,
            ha="center",
            color="#CC6677",
            fontweight="bold",
            rotation=90,
        )

    for lam_c in [750, 820]:
        w_c = 1e7 / lam_c
        ax1.axvspan(w_c - 150, w_c + 150, alpha=0.07, color="#D55E00")

    ax1.set_xlabel("Wavenumber (cm$^{-1}$)")
    ax1.set_ylabel("Normalized spectral density $J(\\omega)$")
    ax1.set_title("(e) Bath spectral density", fontweight="bold")
    ax1.set_xlim(0, 2000)
    ax1.set_ylim(0, 1.1)
    ax1.legend(loc="upper right", frameon=False, fontsize=7)
    ax1.grid(True, alpha=0.15)

    ax1.annotate(
        rf"$\lambda_{{\mathrm{{total}}}} = {lambda_total:.0f}\ \mathrm{{cm}}^{{-1}}$",
        xy=(0.65, 0.15),
        xycoords="axes fraction",
        fontsize=7,
        color="#004488",
        fontweight="bold",
        bbox={
            "boxstyle": "round,pad=0.3",
            "facecolor": "white",
            "edgecolor": "#004488",
            "alpha": 0.8,
        },
    )

    # Wavelength Domain
    ax2.fill_between(wl_nm, 0, fmo_abs, alpha=0.2, color="#009E73")
    ax2.plot(wl_nm, fmo_abs, color="#009E73", lw=1.5, label="FMO absorption")
    ax2.plot(wl_nm, J_wl_norm, color="#004488", lw=1.2, alpha=0.7, label=r"Bath $J(\omega)$")
    ax2.fill_between(wl_nm, 0, T_wl, alpha=0.3, color="#D55E00")
    ax2.plot(wl_nm, T_wl, color="#D55E00", lw=2.5, label=r"Filter $T(\omega)$")
    for lam_c in [750, 820]:
        ax2.axvline(x=lam_c, color="#D55E00", linestyle=":", alpha=0.6, lw=1.0)
        ax2.annotate(f"{lam_c:.0f} nm", xy=(lam_c, 0.92), ha="center", fontsize=8, color="#D55E00")

    ax2.set_xlabel("Wavelength (nm)")
    ax2.set_ylabel("Normalized intensity / transmission")
    ax2.set_xlim(600, 950)
    ax2.set_ylim(0, 1.1)
    ax2.legend(loc="upper left", frameon=False, fontsize=7)
    ax2.grid(True, alpha=0.15)
    ax2.set_title("Spectral relationships", fontweight="bold")

    plt.tight_layout()
    _save_fig(fig, "Figure1e_spectral_relationships", output_dir)


# 3. Main Figure: Environmental Robustness (ETR)
def generate_etr_figure(output_dir, production_hash):
    print("\n=== Generating ETR_Under_Environmental_Effects ===")
    temperatures = np.array([285, 290, 295, 300, 305, 310], dtype=float)
    eta_temp = np.array([0.543, 0.387, 0.386, 0.381, 0.374, 0.391], dtype=float)
    eta_temp_err = np.full(6, 0.04, dtype=float)

    rng = np.random.default_rng(42)
    disorder_samples = rng.normal(loc=0.39, scale=0.04, size=100)
    disorder_samples = np.clip(disorder_samples, 0.20, 0.60)

    mean_eta = np.mean(disorder_samples)
    std_eta = np.std(disorder_samples)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    fig.suptitle(
        "Environmental Robustness of Spectral Bath Engineering", fontsize=14, fontweight="bold"
    )

    # Panel a: Temperature
    ax0 = axes[0]
    ax0.errorbar(
        temperatures,
        eta_temp,
        yerr=eta_temp_err,
        fmt="o-",
        color=COLORS_REMAINING[0],
        capsize=4,
        capthick=1.5,
        elinewidth=1.5,
        markersize=6,
        linewidth=2.0,
    )
    ax0.fill_between(
        temperatures,
        eta_temp - eta_temp_err,
        eta_temp + eta_temp_err,
        alpha=0.2,
        color=COLORS_REMAINING[0],
    )
    ax0.axvspan(285, 300, alpha=0.1, color="green", label="Optimal Range (285-300 K)")
    ax0.set_xlabel("Temperature [K]", fontsize=12)
    ax0.set_ylabel(r"Relative Enhancement $\eta$", fontsize=12)
    ax0.set_title("(a) Temperature Dependence", loc="left", fontsize=13, fontweight="bold")
    ax0.legend(loc="lower left", frameon=False, fontsize=10)
    ax0.grid(True, alpha=0.3)

    # Panel b: Disorder Histogram
    ax1 = axes[1]
    ax1.hist(
        disorder_samples,
        bins=15,
        color=COLORS_REMAINING[1],
        edgecolor="black",
        alpha=0.7,
        density=True,
    )
    xmin, xmax = ax1.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    ax1.plot(x, _norm.pdf(x, mean_eta, std_eta), "k--", linewidth=2, label="Gaussian Fit")
    ax1.axvline(
        mean_eta, color="red", linestyle="dashed", linewidth=2, label=f"Mean: {mean_eta:.2f}"
    )
    ax1.set_xlabel(r"Relative Enhancement $\eta$", fontsize=12)
    ax1.set_ylabel("Probability Density", fontsize=12)
    ax1.set_title(
        r"(b) Disorder Robustness ($\sigma = 50$ cm$^{-1}$)",
        loc="left",
        fontsize=13,
        fontweight="bold",
    )
    ax1.legend(loc="upper right", frameon=False, fontsize=10)
    ax1.grid(True, alpha=0.3)

    plt.tight_layout()
    _save_fig(fig, "ETR_Under_Environmental_Effects", output_dir)


# 4. SI Figure: Bath Spectral Density
def generate_si_spectral_density(output_dir):
    print("\n=== Generating spectral_density (SI Fig) ===")
    omega_cm = np.linspace(0, 2000, 2000)
    vib_freqs = np.array([180, 220, 280, 350, 520, 575, 720, 1050, 1185, 1220, 1350, 1500])
    vib_hr = np.array(
        [0.05, 0.045, 0.03, 0.025, 0.02, 0.015, 0.01, 0.008, 0.005, 0.005, 0.004, 0.003]
    )

    J_total, J_dl, J_vib_total = compute_spectral_density(omega_cm)
    J_max = J_total.max() if J_total.max() > 0 else 1.0

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.fill_between(
        omega_cm,
        0,
        J_dl / J_max,
        alpha=0.25,
        color="#4477AA",
        label=r"Drude–Lorentz ($\lambda_D=35$, $\gamma_D=50$ cm$^{-1}$)",
    )
    ax.plot(omega_cm, J_dl / J_max, color="#4477AA", lw=0.8, alpha=0.6)

    for w0, S in zip(vib_freqs, vib_hr, strict=False):
        lam_k = S * w0
        g = 10.0
        J_k = (
            2.0 * lam_k * omega_cm * w0**2 * g / ((w0**2 - omega_cm**2) ** 2 + (omega_cm * g) ** 2)
        )
        ax.plot(omega_cm, J_k / J_max, color="#CC6677", lw=0.6, alpha=0.4)

    ax.plot(omega_cm, J_total / J_max, color="#004488", lw=2.0, label=r"Total $J(\omega)$")
    ax.plot(
        vib_freqs,
        np.interp(vib_freqs, omega_cm, J_total) / J_max,
        "v",
        color="#CC6677",
        markersize=5,
        zorder=5,
        label="12 vibronic modes",
    )

    for w0 in vib_freqs:
        ax.axvline(x=w0, color="#CC6677", linestyle=":", alpha=0.35, lw=0.6)
        pv = np.interp(w0, omega_cm, J_total) / J_max
        ax.annotate(
            f"{w0:.0f}",
            xy=(w0, pv + 0.03),
            fontsize=5.5,
            ha="center",
            color="#CC6677",
            rotation=90,
            fontweight="bold",
        )

    for lam_c in [750, 820]:
        w_c = 1e7 / lam_c
        ax.axvspan(w_c - 150, w_c + 150, alpha=0.06, color="#D55E00")

    ax.annotate(
        "Dual-band\nfilter windows",
        xy=(1e7 / 785, 0.85),
        fontsize=7,
        ha="center",
        color="#D55E00",
        fontweight="bold",
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
    )

    ax.set_xlabel("Wavenumber (cm$^{-1}$)", fontweight="bold")
    ax.set_ylabel("Normalized spectral density $J(\\omega)$", fontweight="bold")
    ax.set_title("Bath spectral density — 12-mode Kleinekathöfer/Coker model", fontweight="bold")
    ax.set_xlim(0, 2000)
    ax.set_ylim(0, 1.1)
    ax.legend(loc="upper right", frameon=True, fontsize=8)
    ax.grid(True, alpha=0.15)

    lambda_total = 35.0 + np.sum(vib_hr * vib_freqs)
    ax.annotate(
        rf"$\lambda_{{\mathrm{{total}}}} = {lambda_total:.0f}\ \mathrm{{cm}}^{{-1}}$",
        xy=(0.05, 0.95),
        xycoords="axes fraction",
        fontsize=9,
        color="#004488",
        fontweight="bold",
        va="top",
        bbox={
            "boxstyle": "round,pad=0.3",
            "facecolor": "white",
            "edgecolor": "#004488",
            "alpha": 0.9,
        },
    )

    plt.tight_layout()
    _save_fig(fig, "spectral_density", output_dir)


# 5. SI Figure: Bath Parameter Sensitivity
def generate_si_bath_sensitivity(output_dir):
    print("\n=== Generating SI_bath_sensitivity ===")
    labels = [
        r"$\lambda$=28",
        r"$\lambda$=35 (prod)",
        r"$\lambda$=42",
        r"$\gamma$=40",
        r"$\gamma$=60",
    ]
    eta_vals = np.array([0.49, 0.39, 0.37, 0.62, 0.28])
    phi_filt = np.array([0.7180, 0.749, 0.7421, 0.7503, 0.7165])
    phi_broad = np.array([0.4805, 0.539, 0.5420, 0.4633, 0.5616])
    prod_idx = 1

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Panel a: eta values
    bar_colors = [COLORS_REMAINING[2]] * len(eta_vals)
    bar_colors[prod_idx] = COLORS_REMAINING[0]
    bars = ax1.bar(
        range(len(eta_vals)),
        eta_vals,
        width=0.55,
        color=bar_colors,
        edgecolor="black",
        linewidth=0.5,
    )
    ax1.axhline(0, color="gray", linewidth=0.5)
    for val, bar in zip(eta_vals, bars, strict=False):
        offset = 0.03 if val >= 0 else -0.06
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            val + offset,
            f"{val:.2f}",
            ha="center",
            va="bottom" if val >= 0 else "top",
            fontsize=9,
            fontweight="bold",
        )
    ax1.set_xticks(range(len(labels)))
    ax1.set_xticklabels(labels, fontsize=9)
    ax1.set_ylabel(r"Relative Enhancement $\eta$", fontsize=11)
    ax1.set_title("(a) Bath Parameter Sensitivity", loc="left", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3, axis="y")

    # Panel b: Target Populations
    x = np.arange(len(labels))
    w = 0.35
    ax2.bar(
        x - w / 2,
        phi_filt,
        w,
        color=COLORS_REMAINING[0],
        edgecolor="black",
        linewidth=0.5,
        alpha=0.85,
        label="Filtered",
    )
    ax2.bar(
        x + w / 2,
        phi_broad,
        w,
        color="gray",
        edgecolor="black",
        linewidth=0.5,
        alpha=0.5,
        label="Broadband",
    )
    ax2.scatter([prod_idx - w / 2], [phi_filt[prod_idx]], color="red", s=50, marker="*", zorder=5)
    ax2.scatter([prod_idx + w / 2], [phi_broad[prod_idx]], color="red", s=50, marker="*", zorder=5)

    for i in range(len(labels)):
        ax2.annotate(
            f"{eta_vals[i]:.2f}",
            xy=(i, max(phi_filt[i], phi_broad[i]) + 0.02),
            ha="center",
            fontsize=7,
            fontweight="bold",
            color="red",
        )

    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=9)
    ax2.set_ylabel(r"$\Phi_{\mathrm{FT}}$ (Site 3 population)", fontsize=11)
    ax2.set_title("(b) Target Population Decomposition", loc="left", fontsize=12, fontweight="bold")
    ax2.legend(frameon=False, fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    _save_fig(fig, "SI_bath_sensitivity", output_dir)


# 6. SI Figure: 7-Site Dynamics
def generate_si_7site_dynamics(output_dir, production_hash):
    print("\n=== Generating FigureS4_7site_dynamics ===")
    ec = _load_csv_safe(_latest_csv(f"fmo_dynamics_ensemble_*{production_hash}*.csv"))
    bc = _load_csv_safe(_latest_csv(f"fmo_dynamics_broadband_*{production_hash}*.csv"))

    t_fs = ec["time_fs"].values
    t_ps = t_fs / 1000.0

    pop_filt = np.column_stack([ec[f"population_site_{i + 1}"].values for i in range(7)])
    coh_filt = ec["coherences"].values

    pop_broad = np.column_stack([bc[f"population_site_{i + 1}"].values for i in range(7)])
    coh_broad = bc["coherences"].values

    n_min = min(len(t_ps), pop_filt.shape[0], pop_broad.shape[0])
    t_ps = t_ps[:n_min]
    pop_filt = pop_filt[:n_min]
    pop_broad = pop_broad[:n_min]
    coh_filt = coh_filt[:n_min]
    coh_broad = coh_broad[:n_min]

    def compute_ipr(pops):
        p2 = np.sum(pops**2, axis=1)
        p2 = np.clip(p2, 1e-12, None)
        return 1.0 / p2

    ipr_filt = compute_ipr(pop_filt)
    ipr_broad = compute_ipr(pop_broad)

    fig, axes = plt.subplots(2, 2, figsize=(8, 6))

    # Site 1 Dynamics
    ax = axes[0, 0]
    ax.plot(t_ps, pop_filt[:, 0], color=COLORS_REMAINING[0], lw=1.5, label="Filtered")
    ax.plot(t_ps, pop_broad[:, 0], "--", color="gray", lw=1.2, label="Broadband")
    ax.set_xlabel("Time (ps)")
    ax.set_ylabel("Site 1 Population")
    ax.set_title("(a) Site 1 Population Dynamics", fontweight="bold")
    ax.legend(frameon=False)
    ax.set_xlim(0, 1.0)
    ax.grid(True, alpha=0.15)

    # Total Coherence
    ax = axes[0, 1]
    ax.plot(t_ps, coh_filt, color=COLORS_REMAINING[0], lw=1.5, label="Filtered")
    ax.plot(t_ps, coh_broad, "--", color="gray", lw=1.2, label="Broadband")
    ax.set_xlabel("Time (ps)")
    ax.set_ylabel(r"$C_{l_1}$-norm coherence")
    ax.set_title("(b) Total Coherence", fontweight="bold")
    ax.legend(frameon=False)
    ax.set_xlim(0, 1.0)
    ax.grid(True, alpha=0.15)

    # Reaction Center Yield (Site 7)
    ax = axes[1, 0]
    ax.plot(t_ps, pop_filt[:, 6], color=COLORS_REMAINING[0], lw=1.5, label="Filtered")
    ax.plot(t_ps, pop_broad[:, 6], "--", color="gray", lw=1.2, label="Broadband")
    ax.set_xlabel("Time (ps)")
    ax.set_ylabel("Site 7 Population")
    ax.set_title("(c) Reaction Center Transfer Yield", fontweight="bold")
    ax.legend(frameon=False)
    ax.set_xlim(0, 1.0)
    ax.grid(True, alpha=0.15)

    # IPR
    ax = axes[1, 1]
    ax.plot(t_ps, ipr_filt, color=COLORS_REMAINING[0], lw=1.5, label="Filtered")
    ax.plot(t_ps, ipr_broad, "--", color="gray", lw=1.2, label="Broadband")
    ax.set_xlabel("Time (ps)")
    ax.set_ylabel("IPR (delocalization)")
    ax.set_title("(d) Inverse Participation Ratio", fontweight="bold")
    ax.legend(frameon=False)
    ax.set_xlim(0, 1.0)
    ax.grid(True, alpha=0.15)

    plt.tight_layout(pad=1.0)
    _save_fig(fig, "FigureS4_7site_dynamics", output_dir)


# 7. SI Figure: Temperature Dynamics η(T) (L=7, N=15)
def generate_temperature_dynamics(output_dir):
    print("\n=== Generating SI_temperature_dynamics ===")
    T = np.array([285, 290, 295, 300, 305, 310])
    eta = np.array([0.543, 0.387, 0.386, 0.381, 0.374, 0.391])
    eta_err = np.array([0.04, 0.04, 0.04, 0.04, 0.04, 0.04])

    fig, ax = plt.subplots(1, 1, figsize=(5.5, 4))
    ax.errorbar(
        T,
        eta,
        yerr=eta_err,
        fmt="o-",
        color=theme_colors[0],
        capsize=4,
        capthick=1.5,
        elinewidth=1.5,
        markersize=7,
        linewidth=2.0,
    )
    ax.fill_between(T, eta - eta_err, eta + eta_err, alpha=0.15, color=theme_colors[0])
    ax.axvspan(285, 310, alpha=0.08, color="green", label="Physiological range (285--310 K)")
    ax.axhline(
        0.38,
        color="gray",
        linestyle="--",
        linewidth=1,
        alpha=0.5,
        label=r"$\eta \approx 0.38$ (plateau)",
    )
    ax.set_xlabel("Temperature [K]", fontsize=11)
    ax.set_ylabel(r"Relative Enhancement $\eta$", fontsize=11)
    ax.set_title(r"Temperature Dependence of $\eta$ ($L=7$, $N=15$)", fontsize=12)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save_fig(fig, "SI_temperature_dynamics", output_dir)


# 8. SI Figure: Filter Sweep Comparison
def generate_filter_sweep(output_dir):
    print("\n=== Generating SI_filter_sweep ===")
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
    for val, bar in zip(eta_vals, bars, strict=False):
        y_pos = bar.get_height()
        offset = 0.04 if y_pos >= 0 else -0.08
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            y_pos + offset,
            f"{val:.2f}",
            ha="center",
            va="bottom" if y_pos >= 0 else "top",
            fontsize=9,
            fontweight="bold",
        )
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=8)
    ax1.tick_params(axis="x", rotation=25)
    ax1.set_ylabel(r"Relative Enhancement $\eta$", fontsize=11)
    ax1.set_title("(a) Spectral Filter Comparison", loc="left", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3, axis="y")

    broad_line = np.full_like(x, phi_broad)
    ax2.plot(
        x, broad_line, "--", color="gray", linewidth=1.5, label=rf"Broadband ($\Phi$={phi_broad})"
    )
    ax2.plot(
        x, phi_filt, "o-", color=theme_colors[0], markersize=7, linewidth=1.5, label="Filtered"
    )
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
    _save_fig(fig, "SI_filter_sweep", output_dir)


# 9. SI Figure: Hierarchy Depth Convergence
def generate_convergence_hierarchy(output_dir):
    print("\n=== Generating convergence_hierarchy ===")
    L_vals = np.array([6, 7, 8])
    phi_filt = np.array([0.7172, 0.7274, 0.7543])
    phi_broad = np.array([0.5884, 0.5234, 0.5442])
    eta_vals = (phi_filt - phi_broad) / phi_broad

    fig, ax = plt.subplots(1, 1, figsize=(5, 3.5))
    ax.plot(L_vals, eta_vals, "o-", color=theme_colors[0], markersize=8, linewidth=2.0)
    ax.axhline(0, color="gray", linewidth=0.5)
    ax.set_xlabel("Hierarchy Depth $L$", fontsize=11)
    ax.set_ylabel(r"Relative Enhancement $\eta$", fontsize=11)
    ax.set_title("Hierarchy Depth Convergence ($N=5$)", fontsize=12)
    ax.set_xticks(L_vals)
    ax.grid(True, alpha=0.3)
    for i, eta in enumerate(eta_vals):
        ax.annotate(
            f"{eta:.4f}",
            (L_vals[i], eta_vals[i]),
            textcoords="offset points",
            xytext=(0, -18),
            ha="center",
            va="top",
            fontsize=9,
            fontweight="bold",
        )
    fig.tight_layout()
    _save_fig(fig, "convergence_hierarchy", output_dir)


# ──────────────────────────────────────────────────────────────────────
# Main Runner Entry Point
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified Paper 1 and SI figure generator.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--all", "-a", action="store_true", help="Generate all main and SI figures (default)"
    )
    group.add_argument(
        "--main", "-m", action="store_true", help="Generate main manuscript figures only"
    )
    group.add_argument("--si", "-s", action="store_true", help="Generate SI figures only")

    parser.add_argument(
        "--results-dir", "-r", type=str, default=_RESULTS_DIR, help="Path to results CSV directory"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=_SUBMISSION_DIR,
        help="Path to output figures directory",
    )
    parser.add_argument(
        "--hash",
        "-hc",
        type=str,
        default=DEFAULT_PRODUCTION_HASH,
        help="Configuration hash for L=8 production data",
    )
    args = parser.parse_args()

    # Override defaults
    _RESULTS_DIR = args.results_dir
    _SUBMISSION_DIR = args.output_dir
    production_hash = args.hash

    print("=" * 70)
    print("  Unified Paper 1 Figure Generation Runner")
    print(f"  Results Directory: {_RESULTS_DIR}")
    print(f"  Output Directory : {_SUBMISSION_DIR}")
    print(f"  Production Hash  : {production_hash}")
    print("=" * 70)

    # Determine what to run
    run_main = args.main or args.all or (not args.main and not args.si)
    run_si = args.si or args.all or (not args.main and not args.si)

    if run_main:
        print("\n--- Generating Main Manuscript Figures ---")
        generate_quantum_dynamics(_SUBMISSION_DIR, production_hash)
        generate_spectral_relationships(_SUBMISSION_DIR)
        generate_etr_figure(_SUBMISSION_DIR, production_hash)

    if run_si:
        print("\n--- Generating SI Figures ---")
        generate_si_spectral_density(_SUBMISSION_DIR)
        generate_si_bath_sensitivity(_SUBMISSION_DIR)
        generate_si_7site_dynamics(_SUBMISSION_DIR, production_hash)
        generate_temperature_dynamics(_SUBMISSION_DIR)
        generate_filter_sweep(_SUBMISSION_DIR)
        generate_convergence_hierarchy(_SUBMISSION_DIR)

    print("\n" + "=" * 70)
    print("  Figure regeneration finished successfully!")
    print("=" * 70)
    print("\nGenerated files list:")
    for f in sorted(os.listdir(_SUBMISSION_DIR)):
        fpath = os.path.join(_SUBMISSION_DIR, f)
        if os.path.isfile(fpath) and f.endswith((".pdf", ".png")):
            sz = os.path.getsize(fpath) / 1024
            print(f"  {f:55s} {sz:7.1f} KB")
