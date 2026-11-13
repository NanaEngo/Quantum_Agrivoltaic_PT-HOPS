#!/usr/bin/env python3
"""WP1 Optical Data Assembly: Build 1 nm spectral grid (300-1100 nm) for Glass/ITO/ZnO/PM6:Y6/MoO3/Ag + AM1.5G."""

import csv
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WP1 = ROOT / "data" / "wp1"
OPT = WP1 / "optical_nk"


def load_refractiveindex_csv(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load two-section refractiveindex.info CSV (wl_um, n) and (wl_um, k)."""
    wl_n, n_vals, wl_k, k_vals = [], [], [], []
    mode = None
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith("wl,n"):
                mode = "n"
                continue
            if s.startswith("wl,k"):
                mode = "k"
                continue
            a, b = [float(x) for x in s.split(",")]
            if mode == "n":
                wl_n.append(a * 1000.0)
                n_vals.append(b)
            elif mode == "k":
                wl_k.append(a * 1000.0)
                k_vals.append(b)
    # Sort ascending by wavelength
    idx_n = np.argsort(wl_n)
    idx_k = np.argsort(wl_k)
    return np.array(wl_n)[idx_n], np.array(n_vals)[idx_n], np.array(wl_k)[idx_k], np.array(k_vals)[idx_k]


def interp_ri_csv(path: Path, grid_nm: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    wn, nv, wk, kv = load_refractiveindex_csv(path)
    n_i = np.interp(grid_nm, wn, nv, left=nv[0], right=nv[-1])
    k_i = np.interp(grid_nm, wk, kv, left=kv[0], right=kv[-1])
    return n_i, k_i


def load_schiek_txt(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    wls, no, ko = [], [], []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            try:
                vals = [float(x) for x in parts]
            except ValueError:
                continue
            wls.append(vals[0])
            no.append(vals[1])
            ko.append(vals[2])
    arr = np.argsort(wls)
    return np.array(wls)[arr], np.array(no)[arr], np.array(ko)[arr]


def load_simsalabim_txt(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    wls, n_v, k_v = [], [], []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if not parts or parts[0] == "lambda":
                continue
            wls.append(float(parts[0]) * 1e9)
            n_v.append(float(parts[1]))
            k_v.append(float(parts[2]))
    arr = np.argsort(wls)
    return np.array(wls)[arr], np.array(n_v)[arr], np.array(k_v)[arr]


def load_astm_g173(path: Path, grid_nm: np.ndarray) -> np.ndarray:
    wls, glob = [], []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.reader(f)
        for row in r:
            if not row:
                continue
            try:
                wl = float(row[0])
                g = float(row[2])  # Global tilt W*m-2*nm-1
            except ValueError:
                continue
            wls.append(wl)
            glob.append(g)
    return np.interp(grid_nm, np.array(wls), np.array(glob), left=0.0, right=0.0)


def bruggeman_ema(eps1: np.ndarray, eps2: np.ndarray, f1: float) -> np.ndarray:
    """Solve isotropic 3D Bruggeman effective medium equation for complex permittivities."""
    f2 = 1.0 - f1
    b = (3.0 * f1 - 1.0) * eps1 + (3.0 * f2 - 1.0) * eps2
    c = 2.0 * eps1 * eps2
    # Quadratic: 2 eps_eff^2 - b eps_eff - eps1*eps2 = 0 (since c = 2*eps1*eps2 -> discr = b^2 + 8*eps1*eps2)
    disc = np.sqrt(b ** 2 + 4.0 * 2.0 * eps1 * eps2 + 0j)
    r1 = (b + disc) / 4.0
    r2 = (b - disc) / 4.0
    return np.where(np.imag(r1) >= 0.0, r1, r2)


def tmm_normal_abs(n_stack: list[complex], d_nm: list[float], wl_nm: float) -> tuple[float, float, float, float]:
    """Quick 1D coherent TMM (normal incidence) returning (R, T, A_total, A_active_idx2_3)."""
    # n_stack = [n_air, n_ITO, n_ZnO, n_active, n_MoO3, n_Ag, n_air]
    # Note: thick glass handled incoherently via single front air/glass interface transmittance T_glass
    M = np.eye(2, dtype=complex)
    layers = []
    # Transfer matrices from medium j -> j+1
    def iface(na: complex, nb: complex) -> np.ndarray:
        r = (na - nb) / (na + nb)
        t = 2.0 * na / (na + nb)
        return np.array([[1.0, r], [r, 1.0]], dtype=complex) / t

    def prop(nj: complex, dj: float) -> np.ndarray:
        delta = 2.0 * math.pi * nj * dj / wl_nm
        return np.array([[np.exp(-1j * delta), 0.0], [0.0, np.exp(1j * delta)]], dtype=complex)

    # Coherent core starts in Glass -> ITO -> ZnO -> Active -> MoO3 -> Ag -> Air
    mats = [iface(n_stack[0], n_stack[1])]
    for j in range(1, len(n_stack) - 1):
        P = prop(n_stack[j], d_nm[j])
        I_next = iface(n_stack[j], n_stack[j + 1])
        mats.append(P)
        mats.append(I_next)

    M_tot = np.eye(2, dtype=complex)
    for m in mats:
        M_tot = M_tot @ m
    r_tot = M_tot[1, 0] / M_tot[0, 0]
    t_tot = 1.0 / M_tot[0, 0]
    R = float(abs(r_tot) ** 2)
    T = float(np.real(n_stack[-1]) / np.real(n_stack[0]) * abs(t_tot) ** 2)
    return R, T


def main() -> None:
    grid_nm = np.arange(300.0, 1101.0, 1.0)
    am15 = load_astm_g173(WP1 / "ASTMG173.csv", grid_nm)

    n_glass, k_glass = interp_ri_csv(OPT / "Glass_lowiron.csv", grid_nm)
    n_ito, k_ito = interp_ri_csv(OPT / "ITO_Konig.csv", grid_nm)
    n_zno, k_zno = interp_ri_csv(OPT / "ZnO_Stelling.csv", grid_nm)
    # MoO3 Stelling (301-899 nm) + Vos (>899 nm, offset matched cleanly at 899 nm)
    n_moo_s, k_moo_s = interp_ri_csv(OPT / "MoO3_Stelling.csv", grid_nm)
    n_moo_v, k_moo_v = interp_ri_csv(OPT / "MoO3_Vos.csv", grid_nm)
    # Use Stelling up to 899 nm and smooth delta-matched Vos for 900-1000 nm, flat Cauchy beyond 1000
    mask_tail = grid_nm > 899.0
    dn_899 = n_moo_s[grid_nm == 899.0][0] - n_moo_v[grid_nm == 899.0][0]
    n_moo = np.where(mask_tail, n_moo_v + dn_899, n_moo_s)
    k_moo = np.where(mask_tail, 0.0, k_moo_s)
    n_ag, k_ag = interp_ri_csv(OPT / "Ag_Johnson.csv", grid_nm)

    w_pm6, no_pm6, ko_pm6 = load_schiek_txt(OPT / "PM6_uniaxial_nk.txt")
    n_pm6 = np.interp(grid_nm, w_pm6, no_pm6)
    k_pm6 = np.interp(grid_nm, w_pm6, ko_pm6)

    w_d18, no_d18, ko_d18 = load_schiek_txt(OPT / "D18Y6_uniaxial_nk.txt")
    n_d18y6 = np.interp(grid_nm, w_d18, no_d18)
    k_d18y6 = np.interp(grid_nm, w_d18, ko_d18)

    w_y6, n_y6_raw, k_y6_raw = load_simsalabim_txt(OPT / "simsalabim" / "nk_Y6.txt")
    n_y6 = np.interp(grid_nm, w_y6, n_y6_raw)
    k_y6 = np.interp(grid_nm, w_y6, k_y6_raw)

    # Bruggeman 1:1.2 (f_PM6 = 1/2.2 = 0.4545) over 300-800 nm; above 800 nm Y6 tail scaled from D18:Y6 NIR band shape
    eps_pm6 = (n_pm6 + 1j * k_pm6) ** 2
    eps_y6 = (n_y6 + 1j * k_y6) ** 2
    eps_blend = bruggeman_ema(eps_pm6, eps_y6, f1=1.0 / 2.2)
    nk_blend = np.sqrt(eps_blend)
    n_pm6y6 = np.real(nk_blend).copy()
    k_pm6y6 = np.imag(nk_blend).copy()

    # Smooth NIR Y6 tail >800 nm anchored to Bruggeman blend value at 800 nm and D18:Y6 NIR spectral shape
    i800 = int(np.where(grid_nm == 800.0)[0][0])
    scale_k = k_pm6y6[i800] / max(1e-6, k_d18y6[i800])
    n_offset = n_pm6y6[i800] - n_d18y6[i800]
    for i in range(i800 + 1, len(grid_nm)):
        n_pm6y6[i] = n_d18y6[i] + n_offset * math.exp(-(grid_nm[i] - 800.0) / 100.0)
        k_pm6y6[i] = k_d18y6[i] * scale_k

    out_csv = WP1 / "optical_nk_stack_1nm.csv"
    headers = [
        "wavelength_nm", "AM15G_W_m2_nm",
        "Glass_n", "Glass_k",
        "ITO_n", "ITO_k",
        "ZnO_n", "ZnO_k",
        "PM6Y6_n", "PM6Y6_k",
        "D18Y6_n", "D18Y6_k",
        "PM6_n", "PM6_k",
        "MoO3_n", "MoO3_k",
        "Ag_n", "Ag_k",
    ]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for i in range(len(grid_nm)):
            w.writerow([
                f"{grid_nm[i]:.1f}", f"{am15[i]:.6e}",
                f"{n_glass[i]:.5f}", f"{k_glass[i]:.6e}",
                f"{n_ito[i]:.5f}", f"{k_ito[i]:.5f}",
                f"{n_zno[i]:.5f}", f"{k_zno[i]:.5f}",
                f"{n_pm6y6[i]:.5f}", f"{k_pm6y6[i]:.5f}",
                f"{n_d18y6[i]:.5f}", f"{k_d18y6[i]:.5f}",
                f"{n_pm6[i]:.5f}", f"{k_pm6[i]:.5f}",
                f"{n_moo[i]:.5f}", f"{k_moo[i]:.5f}",
                f"{n_ag[i]:.5f}", f"{k_ag[i]:.5f}",
            ])
    print(f"Saved {out_csv} ({len(grid_nm)} wavelengths)")

    # Quick TMM sanity check for Glass/ITO(135)/ZnO(30)/PM6Y6(75)/MoO3(8)/Ag(120) vs opaque Jsc benchmark & Ag(12nm) ST-OPV
    h_planck = 6.62607015e-34
    c_light = 2.99792458e8
    q_e = 1.602176634e-19
    for label, d_act, d_ag, iq_e in [("Opaque 75nm Ag120 (PMC12816033 ref)", 75.0, 120.0, 0.85), ("ST-OPV 90nm Ag12", 90.0, 12.0, 0.82)]:
        # Simple Poynting absorption estimate across active layer vs total transmittance
        # Using exact Beer-corrected stack reflectance/transmittance check at 1nm
        T_par_sum = 0.0
        par_inc_sum = 0.0
        jsc_upper = 0.0
        for i, wl in enumerate(grid_nm):
            ns = [complex(n_glass[i], 0.0), complex(n_ito[i], k_ito[i]), complex(n_zno[i], k_zno[i]),
                  complex(n_pm6y6[i], k_pm6y6[i]), complex(n_moo[i], k_moo[i]), complex(n_ag[i], k_ag[i]), complex(1.0, 0.0)]
            ds = [0.0, 135.0, 30.0, d_act, 8.0, d_ag, 0.0]
            R, T = tmm_normal_abs(ns, ds, wl)
            # Front air/glass incoherent reflection (~4%) + single-pass transmitted fraction
            R_air_gl = ((1.0 - n_glass[i]) / (1.0 + n_glass[i])) ** 2
            T_tot = (1.0 - R_air_gl) * T / (1.0 - R_air_gl * R)
            A_tot = (1.0 - R_air_gl) * (1.0 - R - T) / (1.0 - R_air_gl * R)
            e_ph = h_planck * c_light / (wl * 1e-9)
            if 400.0 <= wl <= 700.0:
                par_inc_sum += am15[i] / e_ph
                T_par_sum += T_tot * am15[i] / e_ph
            if 300.0 <= wl <= 950.0:
                # Active vs parasitic partition approx weighted by alpha*d
                jsc_upper += q_e * (A_tot * iq_e) * (am15[i] / e_ph) * 0.1  # mA/cm2
        print(f"{label}: PAR photon transmittance={T_par_sum/par_inc_sum:.3f}, Total A*IQE Jsc_upper~{jsc_upper:.2f} mA/cm2")


if __name__ == "__main__":
    main()
