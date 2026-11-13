#!/usr/bin/env python3
"""WP1 Quantum Photobiology Extraction: Extract verified 14x14 LHCII Hamiltonians and bath spectral parameters."""

import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WP1 = ROOT / "data" / "wp1"

# Standard PDB numbering matching 1RWT.pdb Chain A and PMC11736799 Table 2/3
SITE_LABELS = [
    "b601", "a602", "a603", "a604", "b605", "b606", "b607",
    "b608", "b609", "a610", "a611", "a612", "a613", "a614",
]
PDB_IDS = [int(s[1:]) for s in SITE_LABELS]


def parse_number(s: str) -> float:
    return float(s.replace(",", "").replace("−", "-").replace("–", "-").strip())


def extract_pmc11736799_tables(xml_path: Path) -> dict:
    root = ET.parse(xml_path).getroot()
    site_energies = {"Novoderezhkin_2005": {}, "Muh_2010": {}, "Slama_2020": {}, "MMSIC_MD_2025": {}, "reorg_MD_cm1": {}, "std_MD_cm1": {}}
    mmsic_matrix_raw = {}

    for tw in root.findall(".//table-wrap"):
        lbl = "".join(tw.find("label").itertext()).strip() if tw.find("label") is not None else ""
        if lbl == "Table 2":
            for tr in tw.findall(".//tr"):
                cells = [" ".join("".join(c.itertext()).split()) for c in tr.findall("./td")]
                if len(cells) >= 7 and cells[0] in SITE_LABELS:
                    s = cells[0]
                    site_energies["Novoderezhkin_2005"][s] = parse_number(cells[1])
                    site_energies["Muh_2010"][s] = parse_number(cells[2])
                    site_energies["Slama_2020"][s] = parse_number(cells[3])
                    site_energies["MMSIC_MD_2025"][s] = parse_number(cells[4])
                    site_energies["std_MD_cm1"][s] = parse_number(cells[5])
                    site_energies["reorg_MD_cm1"][s] = parse_number(cells[6])
        elif lbl == "Table 3":
            col_headers = None
            for tr in tw.findall(".//tr"):
                cells = [" ".join("".join(c.itertext()).split()) for c in tr.findall("./th") + tr.findall("./td")]
                if cells and cells[0] == "Chl":
                    col_headers = cells[1:]
                elif col_headers and cells and cells[0] in SITE_LABELS:
                    row_site = cells[0]
                    mmsic_matrix_raw[row_site] = {col_headers[k]: parse_number(cells[k + 1]) for k in range(len(col_headers))}

    # Canonicalize 14x14 matrix in sorted PDB order (601..614)
    mmsic_mat = []
    for r in SITE_LABELS:
        mmsic_mat.append([mmsic_matrix_raw[r][c] for c in SITE_LABELS])

    return {"site_energies_cm1": site_energies, "mmsic_md_matrix_cm1": mmsic_mat}


def build_pda_coupling_matrix(dipoles_json: Path, mu2_a: float = 21.0, mu2_b: float = 14.7, screening_factor: float = 1.0 / 2.0) -> list[list[float]]:
    """Compute ideal point-dipole couplings in cm^-1 using 1RWT Mg-Mg geometry and Knox & Spring dipole strengths.
    V_mn = screening_factor * 5040 * mu_m * mu_n * kappa_mn / R_mn^3 (mu in Debye, R in Angstrom -> cm^-1).
    """
    with open(dipoles_json, "r", encoding="utf-8") as f:
        d = json.load(f)["1RWT_chainA"]
    sites = d["sites"]
    n = len(sites)
    # 1 e*A = 4.8032 D => (1 Debye)^2 / (4 pi eps0 * 1 A^3) in cm^-1 is 5034.12 cm^-1
    C_D2_A3_TO_CM1 = 5034.12
    mus = [math.sqrt(mu2_a) if s["species"] == "Chl_a" else math.sqrt(mu2_b) for s in sites]
    mat = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            r = d["mg_distance_angstrom"][i][j]
            k = d["orientational_factor_kappa"][i][j]
            v = screening_factor * C_D2_A3_TO_CM1 * mus[i] * mus[j] * k / (r ** 3)
            mat[i][j] = mat[j][i] = round(v, 3)
    return mat


def main() -> None:
    tdata = extract_pmc11736799_tables(WP1 / "PMC11736799.xml")
    pda_couplings = build_pda_coupling_matrix(WP1 / "lhcii_pdb_dipoles.json", mu2_a=21.0, mu2_b=14.7, screening_factor=0.65)
    # Validate symmetry of MMSIC-MD matrix
    m = tdata["mmsic_md_matrix_cm1"]
    max_asym = max(abs(m[i][j] - m[j][i]) for i in range(14) for j in range(14))
    print(f"MMSIC-MD 14x14 loaded, max asymmetry = {max_asym} cm^-1")

    # Compare strongest couplings: MMSIC-MD vs 1RWT PDA (f_screen=0.65 -> ~effective TrEsp/dielectric)
    idx = {s: i for i, s in enumerate(SITE_LABELS)}
    for a, b in [("a611", "a612"), ("a604", "b606"), ("a603", "b609"), ("a610", "b608"), ("a602", "b601"), ("a613", "a614")]:
        i, j = idx[a], idx[b]
        print(f"Pair {a}-{b}: MMSIC-MD J={m[i][j]:+.1f} cm^-1 | 1RWT PDA(f=0.65) J={pda_couplings[i][j]:+.1f} cm^-1")

    # Construct H1 (Novoderezhkin site energies + PDA couplings), H2 (Muh 2010 site energies + PDA couplings), and H3 (MMSIC-MD full ab-initio)
    def assemble(diag_dict: dict, off_mat: list[list[float]]) -> list[list[float]]:
        h = [[off_mat[i][j] for j in range(14)] for i in range(14)]
        for i, s in enumerate(SITE_LABELS):
            h[i][i] = diag_dict[s]
        return h

    out = {
        "site_order": SITE_LABELS,
        "pdb_ids": PDB_IDS,
        "sources": {
            "PMC11736799": "10.1021/acs.jctc.4c01214 (Table 2: Novoderezhkin 2005, Muh 2010, Slama 2020, MMSIC-MD 2025; Table 3: MMSIC-MD full 14x14)",
            "PMC12063655": "10.1126/sciadv.ads0327 (Eq. 2 Renger spectral density: S=0.65, s1=0.8, s2=0.5, omega1=0.5565 cm-1, omega2=1.936 cm-1, E_lambda=50.87 cm-1, R_c=5.0 A)",
            "PMC12199089": "10.1021/acsomega.4c11543 (Knox & Spring dipole strengths: Chl a = 21.0 D^2, Chl b = 14.7 D^2; Muh 611-612 = 99.0 cm-1, Duffy 611-612 = 131.4 cm-1)",
            "1RWT": "Liu et al. 2004 Nature PDB 1RWT Chain A (2.72 A)",
        },
        "site_energies_cm1": tdata["site_energies_cm1"],
        "dipole_strengths_D2": {"Chl_a": 21.0, "Chl_b": 14.7},
        "renger_spectral_density": {
            "S": 0.65,
            "s1": 0.8,
            "s2": 0.5,
            "omega1_cm1": 0.5565,
            "omega2_cm1": 1.936,
            "reorganization_energy_cm1": 50.87,
            "correlation_radius_angstrom": 5.0,
        },
        "hamiltonians_cm1": {
            "H1_Novoderezhkin2005_diag_PDA": assemble(tdata["site_energies_cm1"]["Novoderezhkin_2005"], pda_couplings),
            "H2_Muh2010_diag_PDA": assemble(tdata["site_energies_cm1"]["Muh_2010"], pda_couplings),
            "H3_MMSIC_MD_2025_full": m,
        },
    }
    out_path = WP1 / "lhcii_hamiltonians_14site.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
