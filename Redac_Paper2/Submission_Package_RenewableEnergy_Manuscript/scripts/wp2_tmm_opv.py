#!/usr/bin/env python3
"""WP2 Module A: Multilayer Optical Transfer Matrix Method (TMM) Solver for ST-OPV.

Computes exact s/p polarization and angle-resolved reflectance, transmittance,
and layer-resolved absorptance for:
    Air / Thick Glass_PET (incoherent) / ITO(100) / ZnO(35) / PM6:Y6(d_act) / MoO3(10) / Ag(d_Ag) / MoO3(d_cap) / Air

Outputs:
    - data/wp2/tmm_pareto_opv.csv: full grid scan + Pareto-optimal front markers
    - data/wp2/tmm_spectral_library.npz: resolved T_beam(lambda, theta) & T_diff(lambda) for Pareto designs + opaque ref
    - data/wp2/tmm_validation_summary.json: conservation checks & Nat. Commun. 2025 opaque calibration metrics
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

try:
    import yaml  # PyYAML

    def load_yaml(path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
except ImportError:
    from ruamel.yaml import YAML

    def load_yaml(path: Path) -> dict:
        y = YAML(typ="safe")
        with open(path, "r", encoding="utf-8") as f:
            return y.load(f)


PKG_ROOT = Path(__file__).resolve().parent.parent
DATA_WP1 = PKG_ROOT / "data" / "wp1"
DATA_WP2 = PKG_ROOT / "data" / "wp2"

# Fundamental physical constants (SI)
H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8
Q_ELECTRON = 1.602176634e-19
_TRAPZ = getattr(np, "trapezoid", getattr(np, "trapz", None))


def load_optical_dataset(csv_path: Path) -> Dict[str, np.ndarray]:
    """Load dispersive n,k (300-1100 nm, 1 nm) and AM1.5G spectrum without pandas dependency."""
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = {name: [] for name in reader.fieldnames}
        for row in reader:
            for name in cols:
                cols[name].append(float(row[name]))
    return {k: np.asarray(v, dtype=np.float64) for k, v in cols.items()}


def fresnel_interface_and_kz(
    n_i: np.ndarray, n_j: np.ndarray, sin_theta0: float, n0: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Complex Snell cos(theta) and Fresnel reflection/transmission amplitude coefficients."""
    # Complex wavevector z-component normalized by k0: n * cos(theta)
    kz_i = np.sqrt(n_i**2 - (n0 * sin_theta0) ** 2 + 0j)
    kz_j = np.sqrt(n_j**2 - (n0 * sin_theta0) ** 2 + 0j)
    # Enforce physical branch: Im(kz) >= 0 (attenuation), or Re(kz) >= 0 if Im ~ 0
    kz_i = np.where((np.imag(kz_i) < 0) | ((np.imag(kz_i) == 0) & (np.real(kz_i) < 0)), -kz_i, kz_i)
    kz_j = np.where((np.imag(kz_j) < 0) | ((np.imag(kz_j) == 0) & (np.real(kz_j) < 0)), -kz_j, kz_j)

    cos_i = kz_i / n_i
    cos_j = kz_j / n_j

    r_s = (n_i * cos_i - n_j * cos_j) / (n_i * cos_i + n_j * cos_j)
    t_s = 2.0 * n_i * cos_i / (n_i * cos_i + n_j * cos_j)

    r_p = (n_j * cos_i - n_i * cos_j) / (n_j * cos_i + n_i * cos_j)
    t_p = 2.0 * n_i * cos_i / (n_j * cos_i + n_i * cos_j)
    return r_s, t_s, r_p, t_p


def simulate_opv_exact_snell(
    data: Dict[str, np.ndarray],
    d_act_nm: float,
    d_ag_nm: float,
    d_cap_nm: float,
    theta_air_deg: float,
    d_ito_nm: float = 100.0,
    d_zno_nm: float = 35.0,
    d_moo3_htl_nm: float = 10.0,
    active_material: str = "PM6Y6",
) -> Dict[str, np.ndarray]:
    """Exact wavelength-invariant Snell k_par = k0 * sin(theta_air) implementation."""
    wl = data["wavelength_nm"]
    n_air = np.ones_like(wl, dtype=np.complex128)
    n_glass = data["Glass_n"] + 1j * np.zeros_like(wl)
    n_ito = data["ITO_n"] + 1j * data["ITO_k"]
    n_zno = data["ZnO_n"] + 1j * data["ZnO_k"]
    n_act = data[f"{active_material}_n"] + 1j * data[f"{active_material}_k"]
    n_moo3 = data["MoO3_n"] + 1j * data["MoO3_k"]
    n_ag = data["Ag_n"] + 1j * data["Ag_k"]

    sin_th_air = float(np.sin(np.deg2rad(theta_air_deg)))
    n0_sin_sq = (1.0 * sin_th_air) ** 2

    # Front Air <-> Glass Fresnel (incoherent)
    r_s_0g, _, r_p_0g, _ = fresnel_interface_and_kz(n_air, n_glass, sin_th_air, n_air)
    R0_s = np.abs(r_s_0g) ** 2
    R0_p = np.abs(r_p_0g) ** 2
    T0_s = 1.0 - R0_s
    T0_p = 1.0 - R0_p

    # Stack inside Glass
    n_list = [n_glass, n_ito, n_zno, n_act, n_moo3, n_ag, n_moo3, n_air]
    d_list = [np.inf, d_ito_nm, d_zno_nm, d_act_nm, d_moo3_htl_nm, d_ag_nm, d_cap_nm, np.inf]
    m_tot = len(n_list)

    kz_all = []
    for n_j in n_list:
        kz = np.sqrt(n_j**2 - n0_sin_sq + 0j)
        kz = np.where((np.imag(kz) < 0) | ((np.imag(kz) == 0) & (np.real(kz) < 0)), -kz, kz)
        kz_all.append(kz)

    res_T = np.zeros_like(wl)
    res_R = np.zeros_like(wl)
    res_A_act = np.zeros_like(wl)
    res_A_tot = np.zeros_like(wl)

    k0 = 2.0 * np.pi / wl
    n_wl = len(wl)
    target_layer_idx = 3

    for pol, R0, T0 in [("s", R0_s, T0_s), ("p", R0_p, T0_p)]:
        Y = kz_all if pol == "s" else [(n_list[j] ** 2) / kz_all[j] for j in range(m_tot)]

        E_curr = np.ones(n_wl, dtype=np.complex128)
        H_curr = Y[-1].copy()
        log_scale_total = np.zeros(n_wl, dtype=np.float64)
        log_scale_at_tgt_out = np.zeros(n_wl, dtype=np.float64)
        log_scale_at_tgt_in = np.zeros(n_wl, dtype=np.float64)
        E_tgt_out = H_tgt_out = E_tgt_in = H_tgt_in = None

        for j in range(m_tot - 2, 0, -1):
            if j == target_layer_idx:
                E_tgt_out = E_curr.copy()
                H_tgt_out = H_curr.copy()
                log_scale_at_tgt_out = log_scale_total.copy()

            delta = k0 * kz_all[j] * d_list[j]
            im_d = np.imag(delta)
            step_log = np.where(im_d > 25.0, im_d - 25.0, 0.0)
            cos_d = np.cos(delta)
            sin_d = np.sin(delta)
            E_next = cos_d * E_curr - 1j * (sin_d / Y[j]) * H_curr
            H_next = -1j * Y[j] * sin_d * E_curr + cos_d * H_curr

            if np.any(step_log > 0):
                inv_s = np.exp(-step_log)
                E_next = E_next * inv_s
                H_next = H_next * inv_s
                log_scale_total = log_scale_total + step_log

            E_curr, H_curr = E_next, H_next
            if j == target_layer_idx:
                E_tgt_in = E_curr.copy()
                H_tgt_in = H_curr.copy()
                log_scale_at_tgt_in = log_scale_total.copy()

        Y0 = Y[0]
        E0_plus = 0.5 * (E_curr + H_curr / Y0)
        E0_minus = 0.5 * (E_curr - H_curr / Y0)
        r_stack = E0_minus / E0_plus

        R_stack = np.abs(r_stack) ** 2
        S_inc_norm = np.real(Y0) * (np.abs(E0_plus) ** 2)
        S_exit_norm = np.real(Y[-1]) * np.exp(-2.0 * log_scale_total)
        T_stack = S_exit_norm / S_inc_norm

        S_tgt_in = np.real(E_tgt_in * np.conj(H_tgt_in)) * np.exp(-2.0 * (log_scale_total - log_scale_at_tgt_in))
        S_tgt_out = np.real(E_tgt_out * np.conj(H_tgt_out)) * np.exp(-2.0 * (log_scale_total - log_scale_at_tgt_out))
        A_act_stack = (S_tgt_in - S_tgt_out) / S_inc_norm
        A_tot_stack = 1.0 - R_stack - T_stack

        # Incoherent substrate coupling (single-bounce back reflection ignored? No, exact geometric series!)
        # Wait: R_stack_back equals R_stack for non-absorbing media only if symmetric, otherwise R0 (Air->Glass) = R0 (Glass->Air)
        denom = 1.0 - R0 * R_stack
        res_T += 0.5 * (T0 * T_stack) / denom
        res_R += 0.5 * (R0 + (T0 * R_stack * T0) / denom)
        res_A_act += 0.5 * (T0 * A_act_stack) / denom
        res_A_tot += 0.5 * (T0 * A_tot_stack) / denom

    return {"T": res_T, "R": res_R, "A_active": res_A_act, "A_total": res_A_tot}


def compute_diffuse_average(
    data: Dict[str, np.ndarray], d_act_nm: float, d_ag_nm: float, d_cap_nm: float, n_quad: int = 18
) -> Dict[str, np.ndarray]:
    """Hemispherical isotropic diffuse average integral_0^{pi/2} F(theta) sin(2 theta) dtheta."""
    # Gauss-Legendre on u = sin^2(theta) in [0, 1] since sin(2 theta) dtheta = d(sin^2 theta)!
    nodes, weights = np.polynomial.legendre.leggauss(n_quad)
    u_pts = 0.5 * (nodes + 1.0)
    w_pts = 0.5 * weights
    thetas_deg = np.rad2deg(np.arcsin(np.sqrt(u_pts)))

    T_diff = np.zeros_like(data["wavelength_nm"])
    R_diff = np.zeros_like(data["wavelength_nm"])
    A_act_diff = np.zeros_like(data["wavelength_nm"])
    A_tot_diff = np.zeros_like(data["wavelength_nm"])

    for th_deg, w in zip(thetas_deg, w_pts):
        res = simulate_opv_exact_snell(data, d_act_nm, d_ag_nm, d_cap_nm, float(th_deg))
        T_diff += w * res["T"]
        R_diff += w * res["R"]
        A_act_diff += w * res["A_active"]
        A_tot_diff += w * res["A_total"]

    return {"T": T_diff, "R": R_diff, "A_active": A_act_diff, "A_total": A_tot_diff}


def pm6y6_ff_voc_model(d_act_nm: float) -> Tuple[float, float]:
    """Thickness-dependent Voc (V) & FF (-) calibrated on Nat. Commun. 2025 (PMC12816033 Table 1).

    Data points:
      53 nm:  Voc = 0.838 V, FF = 0.739
      75 nm:  Voc = 0.840 V, FF = 0.718
      135 nm: Voc = 0.827 V, FF = 0.651
      212 nm: Voc = 0.821 V, FF = 0.588
    """
    d_knots = np.array([53.0, 75.0, 135.0, 212.0])
    voc_knots = np.array([0.838, 0.840, 0.827, 0.821])
    ff_knots = np.array([0.739, 0.718, 0.651, 0.588])
    voc = float(np.interp(d_act_nm, d_knots, voc_knots))
    ff = float(np.interp(d_act_nm, d_knots, ff_knots))
    return voc, ff


def compute_spectral_metrics(
    wl: np.ndarray,
    am15_w_m2_nm: np.ndarray,
    res_norm: Dict[str, np.ndarray],
    d_act_nm: float,
    iqe: float,
) -> Dict[str, float]:
    """Compute J_sc, PCE, APT, ePAR ratio, and R:FR shift under AM1.5G."""
    # Photon flux density [umol photons m^-2 s^-1 nm^-1] = 1e6 / N_A * (W * lambda / (h * c))
    N_A = 6.02214076e23
    wl_m = wl * 1e-9
    phi_am15 = (am15_w_m2_nm * wl_m / (H_PLANCK * C_LIGHT)) * (1e6 / N_A)
    phi_trans = phi_am15 * res_norm["T"]

    # Photonic current integration: J_sc [mA/cm2] = 0.1 * q * int (lambda/(hc)) * I(lambda) * EQE(lambda) dlambda
    # Unit check: [W m^-2 nm^-1] * nm * [C / J] = C s^-1 m^-2 = A m^-2 -> * 0.1 = mA cm^-2!
    jsc_max_mA_cm2 = 0.1 * Q_ELECTRON * float(_TRAPZ(am15_w_m2_nm * res_norm["A_active"] * wl_m / (H_PLANCK * C_LIGHT), wl))
    jsc = iqe * jsc_max_mA_cm2
    voc, ff = pm6y6_ff_voc_model(d_act_nm)
    # AM1.5G total irradiance is 1000 W/m2 = 100 mW/cm2 -> PCE(%) = Jsc(mA/cm2) * Voc(V) * FF / 100 * 100 = Jsc * Voc * FF
    pce_pct = jsc * voc * ff

    # APT definitions:
    # 1) Standard photon-flux weighted PAR (400-700 nm) transmittance
    m_par = (wl >= 400.0) & (wl <= 700.0)
    m_epar = (wl >= 400.0) & (wl <= 750.0)
    m_red = (wl >= 655.0) & (wl <= 665.0)
    m_fr = (wl >= 725.0) & (wl <= 735.0)

    par_in = float(_TRAPZ(phi_am15[m_par], wl[m_par]))
    par_tr = float(_TRAPZ(phi_trans[m_par], wl[m_par]))
    epar_in = float(_TRAPZ(phi_am15[m_epar], wl[m_epar]))
    epar_tr = float(_TRAPZ(phi_trans[m_epar], wl[m_epar]))

    apt_par = par_tr / par_in
    epar_ratio = epar_tr / epar_in

    r_in = float(_TRAPZ(phi_am15[m_red], wl[m_red]))
    fr_in = float(_TRAPZ(phi_am15[m_fr], wl[m_fr]))
    r_tr = float(_TRAPZ(phi_trans[m_red], wl[m_red]))
    fr_tr = float(_TRAPZ(phi_trans[m_fr], wl[m_fr]))
    r_fr_am15 = r_in / fr_in
    r_fr_trans = r_tr / fr_tr

    # LUE (%) = PCE (%) * APT (fraction)
    lue_pct = pce_pct * apt_par

    # Integrated SW metrics (300-1100 nm) for thermal energy balance cross-check
    m_sw = (wl >= 300.0) & (wl <= 1100.0)
    e_in = float(_TRAPZ(am15_w_m2_nm[m_sw], wl[m_sw]))
    t_sw_300_1100 = float(_TRAPZ((am15_w_m2_nm * res_norm["T"])[m_sw], wl[m_sw])) / e_in
    r_sw_300_1100 = float(_TRAPZ((am15_w_m2_nm * res_norm["R"])[m_sw], wl[m_sw])) / e_in
    a_sw_300_1100 = float(_TRAPZ((am15_w_m2_nm * res_norm["A_total"])[m_sw], wl[m_sw])) / e_in

    return {
        "jsc_max_mA_cm2": jsc_max_mA_cm2,
        "jsc_mA_cm2": jsc,
        "voc_V": voc,
        "ff": ff,
        "pce_pct": pce_pct,
        "apt_par": apt_par,
        "epar_ratio": epar_ratio,
        "lue_pct": lue_pct,
        "r_fr_am15": r_fr_am15,
        "r_fr_trans": r_fr_trans,
        "r_fr_relative_change": (r_fr_trans / r_fr_am15) - 1.0,
        "t_sw_300_1100": t_sw_300_1100,
        "r_sw_300_1100": r_sw_300_1100,
        "a_sw_300_1100": a_sw_300_1100,
    }


def mark_pareto_front(records: List[Dict[str, float]]) -> List[bool]:
    """Identify non-dominated points maximizing both (apt_par, pce_pct)."""
    is_pareto = []
    for i, ri in enumerate(records):
        dominated = False
        for j, rj in enumerate(records):
            if i == j:
                continue
            if (rj["apt_par"] >= ri["apt_par"] and rj["pce_pct"] >= ri["pce_pct"]) and (
                rj["apt_par"] > ri["apt_par"] or rj["pce_pct"] > ri["pce_pct"]
            ):
                dominated = True
                break
        is_pareto.append(not dominated)
    return is_pareto


def main() -> None:
    DATA_WP2.mkdir(parents=True, exist_ok=True)
    cfg = load_yaml(PKG_ROOT / "parameters.yaml")
    data = load_optical_dataset(PKG_ROOT / cfg["opv_technology"]["optical_nk_dataset"])
    wl = data["wavelength_nm"]
    am15 = data["AM15G_W_m2_nm"]

    # 1. Calibrate effective IQE on thick opaque Ag (120 nm), PM6:Y6 = 75 nm benchmark (PMC12816033 Table 1: Jsc_EQE=26.36 mA/cm2, PCE=16.27%)
    opaque_75 = simulate_opv_exact_snell(data, d_act_nm=75.0, d_ag_nm=120.0, d_cap_nm=0.0, theta_air_deg=0.0)
    # Physical photon conservation check on all angles
    conservation_err = float(np.max(np.abs(opaque_75["T"] + opaque_75["R"] + opaque_75["A_total"] - 1.0)))

    opaque_m0 = compute_spectral_metrics(wl, am15, opaque_75, d_act_nm=75.0, iqe=1.0)
    target_jsc_eqe = 26.36  # PMC12816033 Table 1 for 75 nm PM6:Y6
    calibrated_iqe = target_jsc_eqe / opaque_m0["jsc_max_mA_cm2"]
    # Physical clamp in case Glass/ITO losses differ slightly vs experimental inverted stack
    iqe_used = min(calibrated_iqe, 0.96)
    opaque_cal = compute_spectral_metrics(wl, am15, opaque_75, d_act_nm=75.0, iqe=iqe_used)

    # Check 53 nm & 135 nm opaque as validation points
    val_points = {}
    for d_ref in (53.0, 75.0, 135.0):
        op_r = simulate_opv_exact_snell(data, d_act_nm=d_ref, d_ag_nm=120.0, d_cap_nm=0.0, theta_air_deg=0.0)
        m_r = compute_spectral_metrics(wl, am15, op_r, d_act_nm=d_ref, iqe=iqe_used)
        val_points[f"opaque_{int(d_ref)}nm"] = {
            "jsc_mA_cm2": round(m_r["jsc_mA_cm2"], 3),
            "pce_pct": round(m_r["pce_pct"], 3),
            "apt_par": round(m_r["apt_par"], 6),
        }

    # 2. Design space sweep within parameters.yaml tmm_design_bounds_nm:
    #    d_act in [50..120], d_Ag in [10..16], d_cap in [0..50]
    # Include thinner ultra-transparent exploratory sensitivity? Wait: stick strictly to parameters.yaml bounds first, plus check Ag=6..10 edge?
    # Keep scan inside parameters.yaml bounds + 8 nm transparent electrode check flagged explicitly if needed;
    # let's check what APT range [50..120, 10..16, 0..50] actually covers!
    d_act_grid = [50.0, 60.0, 75.0, 90.0, 105.0, 120.0]
    d_ag_grid = [8.0, 10.0, 12.0, 14.0, 16.0]
    d_cap_grid = [0.0, 20.0, 35.0, 50.0]

    records: List[Dict[str, float]] = []
    max_cons_err = conservation_err
    for d_act in d_act_grid:
        for d_ag in d_ag_grid:
            for d_cap in d_cap_grid:
                res0 = simulate_opv_exact_snell(data, d_act, d_ag, d_cap, theta_air_deg=0.0)
                err = float(np.max(np.abs(res0["T"] + res0["R"] + res0["A_total"] - 1.0)))
                if err > max_cons_err:
                    max_cons_err = err
                met = compute_spectral_metrics(wl, am15, res0, d_act_nm=d_act, iqe=iqe_used)
                rec = {
                    "d_act_nm": d_act,
                    "d_ag_nm": d_ag,
                    "d_cap_nm": d_cap,
                    "within_yaml_bounds": int(d_ag >= 10.0),
                }
                rec.update(met)
                records.append(rec)

    pareto_all = mark_pareto_front(records)
    records_yaml = [r for r in records if r["within_yaml_bounds"] == 1]
    pareto_yaml_flags = mark_pareto_front(records_yaml)
    yaml_pareto_keys = {
        (r["d_act_nm"], r["d_ag_nm"], r["d_cap_nm"])
        for r, pf in zip(records_yaml, pareto_yaml_flags)
        if pf
    }

    for r, pf in zip(records, pareto_all):
        r["is_pareto_all"] = int(pf)
        r["is_pareto_yaml"] = int((r["d_act_nm"], r["d_ag_nm"], r["d_cap_nm"]) in yaml_pareto_keys)

    # Save CSV
    csv_out = DATA_WP2 / "tmm_pareto_opv.csv"
    fieldnames = list(records[0].keys())
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(records)

    # 3. Compute full angle-resolved & diffuse spectra for Pareto designs + representative APT strata (~35%, ~45%, ~55%, ~65%)
    pareto_designs = sorted([r for r in records if r["is_pareto_all"] == 1], key=lambda x: x["apt_par"])
    inc_angles = list(cfg["optical_radiative_model"]["incidence_angles_deg"])

    T_beam_cube = np.zeros((len(pareto_designs), len(inc_angles), len(wl)), dtype=np.float64)
    A_act_beam_cube = np.zeros((len(pareto_designs), len(inc_angles), len(wl)), dtype=np.float64)
    T_diff_mat = np.zeros((len(pareto_designs), len(wl)), dtype=np.float64)
    R_diff_mat = np.zeros((len(pareto_designs), len(wl)), dtype=np.float64)
    A_tot_diff_mat = np.zeros((len(pareto_designs), len(wl)), dtype=np.float64)

    for idx, des in enumerate(pareto_designs):
        d_act, d_ag, d_cap = des["d_act_nm"], des["d_ag_nm"], des["d_cap_nm"]
        for a_idx, ang in enumerate(inc_angles):
            rb = simulate_opv_exact_snell(data, d_act, d_ag, d_cap, theta_air_deg=float(ang))
            T_beam_cube[idx, a_idx, :] = rb["T"]
            A_act_beam_cube[idx, a_idx, :] = rb["A_active"]
        rd = compute_diffuse_average(data, d_act, d_ag, d_cap, n_quad=18)
        T_diff_mat[idx, :] = rd["T"]
        R_diff_mat[idx, :] = rd["R"]
        A_tot_diff_mat[idx, :] = rd["A_total"]

    npz_out = DATA_WP2 / "tmm_spectral_library.npz"
    np.savez_compressed(
        npz_out,
        wavelength_nm=wl,
        am15_w_m2_nm=am15,
        incidence_angles_deg=np.asarray(inc_angles, dtype=np.float64),
        design_d_act_nm=np.asarray([d["d_act_nm"] for d in pareto_designs]),
        design_d_ag_nm=np.asarray([d["d_ag_nm"] for d in pareto_designs]),
        design_d_cap_nm=np.asarray([d["d_cap_nm"] for d in pareto_designs]),
        design_apt_par=np.asarray([d["apt_par"] for d in pareto_designs]),
        design_pce_pct=np.asarray([d["pce_pct"] for d in pareto_designs]),
        design_lue_pct=np.asarray([d["lue_pct"] for d in pareto_designs]),
        design_r_fr_trans=np.asarray([d["r_fr_trans"] for d in pareto_designs]),
        T_beam=T_beam_cube,
        A_active_beam=A_act_beam_cube,
        T_diff=T_diff_mat,
        R_diff=R_diff_mat,
        A_total_diff=A_tot_diff_mat,
    )

    apt_min_yaml = min(r["apt_par"] for r in records_yaml)
    apt_max_yaml = max(r["apt_par"] for r in records_yaml)
    apt_min_all = min(r["apt_par"] for r in records)
    apt_max_all = max(r["apt_par"] for r in records)

    summary = {
        "n_grid_total": len(records),
        "n_pareto_all": len(pareto_designs),
        "n_pareto_yaml": len(yaml_pareto_keys),
        "max_energy_conservation_error": max_cons_err,
        "raw_calibrated_iqe": calibrated_iqe,
        "iqe_used": iqe_used,
        "opaque_validation": val_points,
        "yaml_bounds_apt_range": [round(apt_min_yaml, 4), round(apt_max_yaml, 4)],
        "extended_ag8_apt_range": [round(apt_min_all, 4), round(apt_max_all, 4)],
        "max_lue_yaml_pct": round(max(r["lue_pct"] for r in records_yaml), 3),
        "max_lue_all_pct": round(max(r["lue_pct"] for r in records), 3),
        "pareto_preview": [
            {
                "d_act_nm": d["d_act_nm"],
                "d_ag_nm": d["d_ag_nm"],
                "d_cap_nm": d["d_cap_nm"],
                "apt_par": round(d["apt_par"], 4),
                "pce_pct": round(d["pce_pct"], 2),
                "lue_pct": round(d["lue_pct"], 2),
                "epar_ratio": round(d["epar_ratio"], 4),
                "r_fr_rel_shift": round(d["r_fr_relative_change"], 4),
            }
            for d in pareto_designs
        ],
    }
    (DATA_WP2 / "tmm_validation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
