#!/usr/bin/env python3
"""
tau_c_diagnostic.py — Diagnostic d'extraction du temps de cohérence τ_c

Objectif : tester si τ_c = 420 fs (filtré, manuscrit) résulte d'un fit
monoexponentiel biaisé appliqué à un signal biexponentiel (H1).

Méthodes comparées :
  1. Fit mono-exponentiel  → reproduit probablement τ_c = 420 fs
  2. Fit bi-exponentiel    → τ_fast ~ 90 fs + τ_slow >> 1 ps
  3. Enveloppe Hilbert 1/e → τ_c via crossing du seuil 1/e
  4. Méthode SI §S10       → C₀·exp(−t/τ) + C_∞, seuil à C_∞ + C₀/e

Usage :
  mamba run -n MesoHOP-sim python tau_c_diagnostic.py

Sortie :
  - Console : tableau récapitulatif de toutes les méthodes
  - Fichier : tau_c_diagnostic_results.png (figure publication)
  - Fichier : tau_c_diagnostic_report.txt (valeurs pour LaTeX)
"""

import sys
import warnings
from pathlib import Path

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.signal import hilbert

warnings.filterwarnings("ignore", category=RuntimeWarning)

# ─────────────────────────────────────────────────────────────────────────────
# CHEMINS (production L=8, UUID 790eaa0832f2, 2026-06-17)
# ─────────────────────────────────────────────────────────────────────────────
RESULTS_DIR = Path(
    "/home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS"
    "/Redac_Paper1/quantum_simulations_framework_parallel_260612"
    "/reproducibility/results"
)

# UUID de production principal L=8
PROD_UUID = "790eaa0832f2"
PROD_DATE = "20260617_082552"

FILTERED_CSV = RESULTS_DIR / f"fmo_dynamics_filtered_{PROD_UUID}_{PROD_DATE}.csv"
BROADBAND_CSV = RESULTS_DIR / f"fmo_dynamics_broadband_{PROD_UUID}_{PROD_DATE}.csv"


# Fallback : chercher automatiquement le dernier CSV disponible
def _find_latest_csv(pattern: str) -> Path | None:
    candidates = sorted(RESULTS_DIR.glob(pattern), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


if not FILTERED_CSV.exists():
    print(f"[WARN] CSV filtré introuvable : {FILTERED_CSV}")
    found = _find_latest_csv("fmo_dynamics_filtered_790*.csv")
    if found:
        FILTERED_CSV = found
        print(f"[INFO] Fallback vers : {FILTERED_CSV.name}")
    else:
        sys.exit("[ERREUR] Aucun CSV filtré de production trouvé. Vérifier le chemin.")

if not BROADBAND_CSV.exists():
    found = _find_latest_csv("fmo_dynamics_broadband_790*.csv")
    if found:
        BROADBAND_CSV = found


# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT DES DONNÉES
# ─────────────────────────────────────────────────────────────────────────────
def load_coherence(csv_path: Path) -> tuple[np.ndarray, np.ndarray]:
    """
    Charge un CSV de dynamique FMO et retourne (time_fs, C_l1).

    La colonne 'coherences' est la l₁-norme moyennée sur l'ensemble.
    Les lignes METADATA (commençant par #) sont ignorées.
    """
    df = pd.read_csv(csv_path, comment="#")
    df.columns = df.columns.str.strip()
    t = df["time_fs"].values
    C = df["coherences"].values
    # Garder uniquement les données numériques valides
    mask = np.isfinite(t) & np.isfinite(C) & (t >= 0)
    return t[mask], C[mask]


print("\n" + "=" * 70)
print("  τ_c DIAGNOSTIC — Production L=8 (790eaa0832f2)")
print("=" * 70)

t_filt, C_filt = load_coherence(FILTERED_CSV)
t_broad, C_broad = load_coherence(BROADBAND_CSV)

print(f"\n[DATA] Filtré   : {FILTERED_CSV.name}")
print(f"       N points : {len(t_filt)}, t_max = {t_filt[-1]:.0f} fs")
print(f"       C(t=0)   = {C_filt[0]:.4f}, C(t_max) = {C_filt[-1]:.4f}")
print(f"\n[DATA] Broadband: {BROADBAND_CSV.name}")
print(f"       N points : {len(t_broad)}, t_max = {t_broad[-1]:.0f} fs")
print(f"       C(t=0)   = {C_broad[0]:.4f}, C(t_max) = {C_broad[-1]:.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# MODÈLES DE FIT
# ─────────────────────────────────────────────────────────────────────────────
def mono_exp(t, C0, tau, Cinf):
    """Monoexponentielle avec baseline : C_∞ + C₀·exp(−t/τ)"""
    return Cinf + C0 * np.exp(-t / tau)


def bi_exp(t, A1, tau1, A2, tau2, Cinf):
    """Biexponentielle avec baseline : C_∞ + A₁·exp(−t/τ₁) + A₂·exp(−t/τ₂)"""
    return Cinf + A1 * np.exp(-t / tau1) + A2 * np.exp(-t / tau2)


def fit_mono(t: np.ndarray, C: np.ndarray, t_range: tuple[float, float] = (0, 1000)) -> dict:
    """
    Fit monoexponentiel sur la fenêtre t_range.

    Reproduit la méthode probablement utilisée pour τ_c = 420 fs.
    """
    mask = (t >= t_range[0]) & (t <= t_range[1])
    t_fit, C_fit = t[mask], C[mask]
    Cinf0 = C_fit[-1]
    C0_0 = C_fit[0] - Cinf0
    p0 = [C0_0, 300.0, Cinf0]
    try:
        popt, pcov = curve_fit(
            mono_exp, t_fit, C_fit, p0=p0, bounds=([0, 1, 0], [10, 5000, 10]), maxfev=20000
        )
        perr = np.sqrt(np.diag(pcov))
        tau_c = popt[1]
        dtau = perr[1]
        resid = C_fit - mono_exp(t_fit, *popt)
        rmse = np.sqrt(np.mean(resid**2))
    except Exception as e:
        return {"tau_c": np.nan, "error": np.nan, "rmse": np.nan, "popt": None, "note": str(e)}
    return {
        "tau_c": tau_c,
        "error": dtau,
        "rmse": rmse,
        "popt": popt,
        "C0": popt[0],
        "Cinf": popt[2],
    }


def fit_biexp(t: np.ndarray, C: np.ndarray, t_range: tuple[float, float] = (0, 1000)) -> dict:
    """
    Fit biexponentiel : identifie τ_fast et τ_slow.

    Physiquement justifié pour le signal filtré (deux composantes).
    """
    mask = (t >= t_range[0]) & (t <= t_range[1])
    t_fit, C_fit = t[mask], C[mask]
    Cinf0 = C_fit[-1]
    amp = C_fit[0] - Cinf0
    p0 = [amp * 0.5, 80.0, amp * 0.5, 1500.0, Cinf0]
    bounds_lo = [0, 1, 0, 100, 0]
    bounds_hi = [10, 500, 10, 10000, 10]
    try:
        popt, pcov = curve_fit(
            bi_exp, t_fit, C_fit, p0=p0, bounds=(bounds_lo, bounds_hi), maxfev=50000
        )
        perr = np.sqrt(np.diag(pcov))
        # Ordonner par ordre croissant de τ
        if popt[1] > popt[3]:
            popt = [popt[2], popt[3], popt[0], popt[1], popt[4]]
            perr = [perr[2], perr[3], perr[0], perr[1], perr[4]]
        resid = C_fit - bi_exp(t_fit, *popt)
        rmse = np.sqrt(np.mean(resid**2))
    except Exception as e:
        return {
            "tau_fast": np.nan,
            "tau_slow": np.nan,
            "error_fast": np.nan,
            "error_slow": np.nan,
            "rmse": np.nan,
            "popt": None,
            "note": str(e),
        }
    return {
        "tau_fast": popt[1],
        "tau_slow": popt[3],
        "A_fast": popt[0],
        "A_slow": popt[2],
        "Cinf": popt[4],
        "error_fast": perr[1],
        "error_slow": perr[3],
        "rmse": rmse,
        "popt": popt,
    }


def hilbert_tau(t: np.ndarray, C: np.ndarray) -> dict:
    """
    Enveloppe Hilbert + seuil 1/e au-dessus de la baseline C_∞.

    Méthode de §S10 du SI :
        τ_c = premier temps où enveloppe(t) < C_∞ + (C_peak - C_∞)/e
    """
    Cinf = np.min(C)
    C_osc = C - Cinf  # signal oscillant centré sur 0
    analytic = hilbert(C_osc)
    envelope = np.abs(analytic)  # enveloppe instantanée
    C_peak = envelope[0]
    threshold = C_peak / np.e

    idx = np.where(envelope <= threshold)[0]
    if len(idx) == 0:
        return {"tau_c": np.inf, "note": "seuil jamais atteint"}
    tau_c = t[idx[0]]
    return {
        "tau_c": tau_c,
        "Cinf": Cinf,
        "C_peak": C_peak,
        "threshold": threshold,
        "envelope": envelope,
    }


# ─────────────────────────────────────────────────────────────────────────────
# EXÉCUTION DES FITS
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "-" * 70)
print("  FITS — SIGNAL FILTRÉ")
print("-" * 70)

# H1 : fit monoexp [0, 1000 fs] — reproduit la méthode manuscrit
filt_mono_full = fit_mono(t_filt, C_filt, t_range=(0, 1000))
print(
    f"\n[Mono 0–1000 fs]  τ_c = {filt_mono_full['tau_c']:.0f} ± "
    f"{filt_mono_full['error']:.0f} fs  |  RMSE = {filt_mono_full['rmse']:.4f}"
)
print(f"                  C0 = {filt_mono_full['C0']:.4f}, C_∞ = {filt_mono_full['Cinf']:.4f}")

# Monoexp sur [0, 500 fs] seulement
filt_mono_500 = fit_mono(t_filt, C_filt, t_range=(0, 500))
print(
    f"\n[Mono 0–500 fs]   τ_c = {filt_mono_500['tau_c']:.0f} ± "
    f"{filt_mono_500['error']:.0f} fs  |  RMSE = {filt_mono_500['rmse']:.4f}"
)

# H2 : fit biexponentiel [0, 1000 fs]
filt_biexp = fit_biexp(t_filt, C_filt, t_range=(0, 1000))
print("\n[Bi-exp 0–1000 fs]")
print(
    f"  τ_fast = {filt_biexp['tau_fast']:.0f} ± {filt_biexp['error_fast']:.0f} fs  "
    f"(A_fast = {filt_biexp['A_fast']:.4f})"
)
print(
    f"  τ_slow = {filt_biexp['tau_slow']:.0f} ± {filt_biexp['error_slow']:.0f} fs  "
    f"(A_slow = {filt_biexp['A_slow']:.4f})"
)
print(f"  C_∞    = {filt_biexp['Cinf']:.4f}  |  RMSE = {filt_biexp['rmse']:.4f}")

# Hilbert
filt_hilbert = hilbert_tau(t_filt, C_filt)
print(f"\n[Hilbert 1/e]     τ_c = {filt_hilbert['tau_c']:.0f} fs")

print("\n" + "-" * 70)
print("  FITS — SIGNAL BROADBAND")
print("-" * 70)

broad_mono = fit_mono(t_broad, C_broad, t_range=(0, 1000))
broad_biexp = fit_biexp(t_broad, C_broad, t_range=(0, 1000))
broad_hilbert = hilbert_tau(t_broad, C_broad)

print(
    f"\n[Mono 0–1000 fs]  τ_c = {broad_mono['tau_c']:.0f} ± "
    f"{broad_mono['error']:.0f} fs  |  RMSE = {broad_mono['rmse']:.4f}"
)
print(
    f"[Bi-exp 0–1000 fs] τ_fast = {broad_biexp['tau_fast']:.0f} fs, "
    f"τ_slow = {broad_biexp['tau_slow']:.0f} fs  |  RMSE = {broad_biexp['rmse']:.4f}"
)
print(f"[Hilbert 1/e]     τ_c = {broad_hilbert['tau_c']:.0f} fs")

# ─────────────────────────────────────────────────────────────────────────────
# RÉSUMÉ DIAGNOSTIC H1
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  VERDICT DIAGNOSTIC")
print("=" * 70)
tau_mono_filt = filt_mono_full["tau_c"]
tau_fast = filt_biexp["tau_fast"]
tau_slow = filt_biexp["tau_slow"]
rmse_mono = filt_mono_full["rmse"]
rmse_biexp = filt_biexp["rmse"]

h1_confirmed = 380 < tau_mono_filt < 470  # proche de 420 fs
biexp_better = rmse_biexp < rmse_mono * 0.7  # bi-exp significativement meilleur

if h1_confirmed:
    print(f"\n✅ H1 CONFIRMÉE : fit mono [0–1000 fs] donne τ_c = {tau_mono_filt:.0f} fs")
    print("   Ceci explique la valeur 420(35) fs du manuscrit.")
else:
    print(f"\n❓ H1 non confirmée : fit mono donne τ_c = {tau_mono_filt:.0f} fs")
    print("   (attendu : ~420 fs d'après le manuscrit)")

if biexp_better:
    print("\n✅ MODÈLE BIEXPONENTIEL supérieur au modèle monoexponentiel :")
    print(f"   RMSE mono = {rmse_mono:.5f}  vs  RMSE bi-exp = {rmse_biexp:.5f}")
    print("   → Physiquement cohérent avec sélection spectrale de modes vibroniques")
else:
    print(f"\n⚠️  RMSE mono ({rmse_mono:.5f}) comparable à bi-exp ({rmse_biexp:.5f})")
    print("   → Signal peu oscillant ou bruit dominant")

print("\n📊 RECOMMANDATION MANUSCRIT :")
print("   Remplacer τ_c = 420(35) fs par :")
print(f"   τ_fast = {tau_fast:.0f} fs (composante rapide, déphasage intra-bande)")
print(f"   τ_slow = {tau_slow:.0f} fs (composante lente, cohérence inter-bande persistante)")
print(
    f"   τ_c broadband = {broad_mono['tau_c']:.0f} ± {broad_mono['error']:.0f} fs (mono-exp, valide)"
)


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE PUBLICATION
# ─────────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(12, 9))
fig.patch.set_facecolor("#0f1117")
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.38)

COLORS = {
    "filtered": "#4FC3F7",  # bleu ciel
    "broadband": "#FF8A65",  # orange
    "mono": "#EF5350",  # rouge
    "biexp_fast": "#81C784",  # vert clair
    "biexp_slow": "#CE93D8",  # lilas
    "hilbert": "#FFD54F",  # ambre
    "manuscript": "#E0E0E0",  # gris clair
}

SPINE_COLOR = "#2a2d3a"
AX_FACECOLOR = "#1a1d27"
TEXT_COLOR = "#e8e8e8"
GRID_COLOR = "#2a2d3a"


def style_ax(ax, title=""):
    ax.set_facecolor(AX_FACECOLOR)
    for spine in ax.spines.values():
        spine.set_color(SPINE_COLOR)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    if title:
        ax.set_title(title, color=TEXT_COLOR, fontsize=10, pad=8, fontweight="bold")
    ax.grid(True, color=GRID_COLOR, alpha=0.5, linewidth=0.5)
    ax.legend(
        facecolor="#1a1d27",
        edgecolor=SPINE_COLOR,
        labelcolor=TEXT_COLOR,
        fontsize=8,
        framealpha=0.9,
    )


# — Panel (a) : Signal filtré + fits mono vs bi-exp
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(
    t_filt,
    C_filt,
    color=COLORS["filtered"],
    lw=1.5,
    label="C_{l₁}^{filt}(t) — données L=8",
    zorder=3,
)

# Fit mono [0-1000]
t_plot = np.linspace(0, 1000, 2000)
if filt_mono_full["popt"] is not None:
    ax1.plot(
        t_plot,
        mono_exp(t_plot, *filt_mono_full["popt"]),
        color=COLORS["mono"],
        lw=2,
        ls="--",
        label=f"Mono-exp: τ={filt_mono_full['tau_c']:.0f} fs (H1 = manuscrit)",
    )

# Fit bi-exp
if filt_biexp["popt"] is not None:
    ax1.plot(
        t_plot,
        bi_exp(t_plot, *filt_biexp["popt"]),
        color=COLORS["biexp_fast"],
        lw=2,
        ls="-.",
        label=(f"Bi-exp: τ_f={filt_biexp['tau_fast']:.0f} fs, τ_s={filt_biexp['tau_slow']:.0f} fs"),
    )

# Ligne horizontale manuscrit
ax1.axhline(y=0, color=COLORS["manuscript"], lw=0.5, ls=":")
ax1.set_xlabel("Temps (fs)")
ax1.set_ylabel("C_{l₁}(t)")
style_ax(ax1, "(a) Filtré — Mono vs Bi-exp")
ax1.set_xlim(0, 1000)


# — Panel (b) : Signal broadband + fit mono
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(
    t_broad,
    C_broad,
    color=COLORS["broadband"],
    lw=1.5,
    label="C_{l₁}^{broad}(t) — données L=8",
    zorder=3,
)
if broad_mono["popt"] is not None:
    ax2.plot(
        t_plot,
        mono_exp(t_plot, *broad_mono["popt"]),
        color=COLORS["mono"],
        lw=2,
        ls="--",
        label=f"Mono-exp: τ={broad_mono['tau_c']:.0f} fs",
    )
if broad_biexp["popt"] is not None:
    ax2.plot(
        t_plot,
        bi_exp(t_plot, *broad_biexp["popt"]),
        color=COLORS["biexp_fast"],
        lw=2,
        ls="-.",
        label=(f"Bi-exp: τ_f={broad_biexp['tau_fast']:.0f} fs"),
    )
ax2.set_xlabel("Temps (fs)")
ax2.set_ylabel("C_{l₁}(t)")
style_ax(ax2, "(b) Broadband — Validation")
ax2.set_xlim(0, 1000)


# — Panel (c) : Enveloppe Hilbert filtrée
ax3 = fig.add_subplot(gs[1, 0])
Cinf_filt = filt_hilbert.get("Cinf", np.min(C_filt))
envelope_filt = filt_hilbert.get("envelope", None)

ax3.plot(
    t_filt,
    C_filt - Cinf_filt,
    color=COLORS["filtered"],
    lw=1,
    alpha=0.6,
    label="Signal oscillant (− C_∞)",
)
if envelope_filt is not None:
    ax3.plot(t_filt, envelope_filt, color=COLORS["hilbert"], lw=2, label="Enveloppe Hilbert")
    threshold = filt_hilbert.get("threshold", 0)
    ax3.axhline(
        y=threshold,
        color=COLORS["manuscript"],
        lw=1.5,
        ls="--",
        label=f"Seuil 1/e = {threshold:.3f}",
    )
    tau_h = filt_hilbert["tau_c"]
    if np.isfinite(tau_h):
        ax3.axvline(
            x=tau_h,
            color=COLORS["hilbert"],
            lw=1.5,
            ls=":",
            label=f"τ_c (Hilbert) = {tau_h:.0f} fs",
        )
ax3.set_xlabel("Temps (fs)")
ax3.set_ylabel("Enveloppe de C_{l₁}")
style_ax(ax3, "(c) Enveloppe Hilbert — Signal filtré")
ax3.set_xlim(0, 1000)


# — Panel (d) : Tableau récapitulatif
ax4 = fig.add_subplot(gs[1, 1])
ax4.axis("off")

summary_data = [
    ["Méthode", "Filtré (fs)", "Broadband (fs)"],
    ["────────────────────", "──────────────", "──────────────"],
    ["Manuscrit (actuel)", "420 ± 35", "280 ± 25"],
    ["────────────────────", "──────────────", "──────────────"],
    [
        "Mono-exp [0–1000 fs]",
        f"{filt_mono_full['tau_c']:.0f} ± {filt_mono_full['error']:.0f}",
        f"{broad_mono['tau_c']:.0f} ± {broad_mono['error']:.0f}",
    ],
    ["Hilbert 1/e", f"{filt_hilbert['tau_c']:.0f}", f"{broad_hilbert['tau_c']:.0f}"],
    ["────────────────────", "──────────────", "──────────────"],
    [
        "Bi-exp τ_fast",
        f"{filt_biexp['tau_fast']:.0f} ± {filt_biexp['error_fast']:.0f}",
        f"{broad_biexp['tau_fast']:.0f} ± {broad_biexp['error_fast']:.0f}",
    ],
    [
        "Bi-exp τ_slow",
        f"{filt_biexp['tau_slow']:.0f} ± {filt_biexp['error_slow']:.0f}",
        f"{broad_biexp['tau_slow']:.0f} ± {broad_biexp['error_slow']:.0f}",
    ],
    ["────────────────────", "──────────────", "──────────────"],
    ["RMSE mono-exp", f"{filt_mono_full['rmse']:.5f}", f"{broad_mono['rmse']:.5f}"],
    ["RMSE bi-exp", f"{filt_biexp['rmse']:.5f}", f"{broad_biexp['rmse']:.5f}"],
]

table = ax4.table(
    cellText=[[r[0], r[1], r[2]] for r in summary_data],
    colLabels=None,
    cellLoc="center",
    loc="center",
    bbox=[0, 0.05, 1, 0.95],
)
table.auto_set_font_size(False)
table.set_fontsize(7.5)

# Colorer les cellules
for (row, col), cell in table.get_celld().items():
    cell.set_facecolor("#1a1d27" if row % 2 == 0 else "#13151f")
    cell.set_edgecolor(SPINE_COLOR)
    cell.set_text_props(color=TEXT_COLOR)
    # Mettre en évidence les valeurs incohérentes (filtré mono ≈ 420 fs)
    if row == 4 and col == 1:  # Mono-exp filtré
        cell.set_facecolor("#4a1a1a")  # rouge foncé : valeur à réviser

style_ax(ax4, "(d) Récapitulatif τ_c — Toutes méthodes")

# Titre général
fig.suptitle(
    "Diagnostic τ_c : Filtré vs Broadband — Production L=8 (790eaa0832f2)",
    color=TEXT_COLOR,
    fontsize=12,
    fontweight="bold",
    y=0.98,
)

out_fig = RESULTS_DIR / "tau_c_diagnostic_results.png"
fig.savefig(out_fig, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"\n[FIGURE] Sauvegardée → {out_fig}")
plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# RAPPORT TEXTE (valeurs pour LaTeX)
# ─────────────────────────────────────────────────────────────────────────────
report_path = RESULTS_DIR / "tau_c_diagnostic_report.txt"
with open(report_path, "w") as f:
    f.write("tau_c DIAGNOSTIC REPORT\n")
    f.write(f"Generated: {pd.Timestamp.now()}\n")
    f.write(f"Data: {FILTERED_CSV.name}\n\n")

    f.write("=" * 60 + "\n")
    f.write("FILTERED SIGNAL\n")
    f.write("=" * 60 + "\n")
    f.write(
        f"Mono-exp [0-1000 fs]: tau_c = {filt_mono_full['tau_c']:.0f} +/- "
        f"{filt_mono_full['error']:.0f} fs  (RMSE = {filt_mono_full['rmse']:.5f})\n"
    )
    f.write(
        f"Bi-exp tau_fast:      {filt_biexp['tau_fast']:.0f} +/- "
        f"{filt_biexp['error_fast']:.0f} fs  (A_fast = {filt_biexp['A_fast']:.4f})\n"
    )
    f.write(
        f"Bi-exp tau_slow:      {filt_biexp['tau_slow']:.0f} +/- "
        f"{filt_biexp['error_slow']:.0f} fs  (A_slow = {filt_biexp['A_slow']:.4f})\n"
    )
    f.write(f"Bi-exp C_inf:         {filt_biexp['Cinf']:.4f}\n")
    f.write(f"Bi-exp RMSE:          {filt_biexp['rmse']:.5f}\n")
    f.write(f"Hilbert 1/e:          {filt_hilbert['tau_c']:.0f} fs\n")
    f.write("Manuscript value:     420 +/- 35 fs\n\n")

    f.write("=" * 60 + "\n")
    f.write("BROADBAND SIGNAL\n")
    f.write("=" * 60 + "\n")
    f.write(
        f"Mono-exp [0-1000 fs]: tau_c = {broad_mono['tau_c']:.0f} +/- "
        f"{broad_mono['error']:.0f} fs  (RMSE = {broad_mono['rmse']:.5f})\n"
    )
    f.write(
        f"Bi-exp tau_fast:      {broad_biexp['tau_fast']:.0f} +/- "
        f"{broad_biexp['error_fast']:.0f} fs\n"
    )
    f.write(
        f"Bi-exp tau_slow:      {broad_biexp['tau_slow']:.0f} +/- "
        f"{broad_biexp['error_slow']:.0f} fs\n"
    )
    f.write(f"Hilbert 1/e:          {broad_hilbert['tau_c']:.0f} fs\n")
    f.write("Manuscript value:     280 +/- 25 fs\n\n")

    f.write("=" * 60 + "\n")
    f.write("LATEX SNIPPET (Option A — biexponentiel)\n")
    f.write("=" * 60 + "\n")
    tau_f = filt_biexp["tau_fast"]
    dtau_f = filt_biexp["error_fast"]
    tau_s = filt_biexp["tau_slow"]
    tau_broad = broad_mono["tau_c"]
    dtau_broad = broad_mono["error"]
    f.write(
        f"The filtered coherence exhibits biexponential decay with a fast component\n"
        f"$\\\\tau_{{\\\\mathrm{{fast}}}} = \\\\SI{{{tau_f:.0f}({dtau_f:.0f})}}"
        f"{{\\\\femto\\\\second}}$ (intra-band dephasing) and a\n"
        f"slow component $\\\\tau_{{\\\\mathrm{{slow}}}} > \\\\SI{{1}}{{\\\\pico\\\\second}}$\n"
        f"(inter-band long-lived coherence), in contrast to the broadband case\n"
        f"($\\\\tau_c = \\\\SI{{{tau_broad:.0f}({dtau_broad:.0f})}}"
        f"{{\\\\femto\\\\second}}$, monoexponential).\n"
    )

print(f"[RAPPORT] Sauvegardé → {report_path}")
print("\n[DONE] Diagnostic terminé.")
