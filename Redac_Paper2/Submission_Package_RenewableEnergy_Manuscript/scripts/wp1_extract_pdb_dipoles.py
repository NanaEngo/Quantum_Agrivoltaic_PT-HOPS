#!/usr/bin/env python3
"""WP1 Structural Extraction: Extract 14-site LHCII Mg centers and Qy (NB -> ND) dipole vectors from 1RWT.pdb and 2BHW.pdb."""

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WP1 = ROOT / "data" / "wp1"


def parse_chain_chls(pdb_path: Path, chain_id: str = "A") -> dict:
    """Parse MG, NB, ND coordinates for all CLA/CHL residues in a chain."""
    chls = {}
    with open(pdb_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.startswith(("ATOM  ", "HETATM")):
                continue
            altloc = line[16].strip()
            if altloc not in ("", "A"):
                continue
            res = line[17:20].strip()
            chain = line[21].strip()
            if res not in ("CLA", "CHL") or chain != chain_id:
                continue
            resseq = int(line[22:26].strip())
            atom = line[12:16].strip()
            if atom not in ("MG", "NB", "ND"):
                continue
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            entry = chls.setdefault(resseq, {"resname": res, "atoms": {}})
            entry["atoms"][atom] = (x, y, z)
    return dict(sorted(chls.items()))


def norm_vec(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[list[float], float]:
    """Return unit vector from a to b and Euclidean norm."""
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    r = math.sqrt(dx * dx + dy * dy + dz * dz)
    if r == 0.0:
        raise ValueError("Zero vector norm")
    return [dx / r, dy / r, dz / r], r


def dot(u: list[float], v: list[float]) -> float:
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def process_pdb(pdb_filename: str, chain_id: str = "A") -> dict:
    pdb_path = WP1 / pdb_filename
    chls = parse_chain_chls(pdb_path, chain_id=chain_id)
    if len(chls) != 14:
        raise RuntimeError(f"Expected 14 chlorophylls in {pdb_filename} chain {chain_id}, found {len(chls)}")

    sites = []
    for resseq, info in chls.items():
        atoms = info["atoms"]
        if not all(k in atoms for k in ("MG", "NB", "ND")):
            raise RuntimeError(f"Missing MG/NB/ND in {pdb_filename} site {resseq}")
        mu_hat, nb_nd_dist = norm_vec(atoms["NB"], atoms["ND"])
        species = "Chl_a" if info["resname"] == "CLA" else "Chl_b"
        sites.append({
            "pdb_id": resseq,
            "resname": info["resname"],
            "species": species,
            "mg_angstrom": list(atoms["MG"]),
            "qy_unit_vec_nb_to_nd": [round(x, 6) for x in mu_hat],
            "nb_nd_span_angstrom": round(nb_nd_dist, 4),
        })

    n = len(sites)
    dist_matrix = [[0.0] * n for _ in range(n)]
    kappa_matrix = [[0.0] * n for _ in range(n)]
    dipole_alignment = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            r_hat, r_ij = norm_vec(tuple(sites[i]["mg_angstrom"]), tuple(sites[j]["mg_angstrom"]))
            ui = sites[i]["qy_unit_vec_nb_to_nd"]
            uj = sites[j]["qy_unit_vec_nb_to_nd"]
            cos_ij = dot(ui, uj)
            kappa = cos_ij - 3.0 * dot(ui, r_hat) * dot(uj, r_hat)
            dist_matrix[i][j] = dist_matrix[j][i] = round(r_ij, 4)
            kappa_matrix[i][j] = kappa_matrix[j][i] = round(kappa, 6)
            dipole_alignment[i][j] = dipole_alignment[j][i] = round(cos_ij, 6)

    return {
        "source_pdb": pdb_filename,
        "chain": chain_id,
        "site_order_pdb_ids": [s["pdb_id"] for s in sites],
        "sites": sites,
        "mg_distance_angstrom": dist_matrix,
        "orientational_factor_kappa": kappa_matrix,
        "dipole_dot_cos": dipole_alignment,
    }


def main() -> None:
    out_1rwt = process_pdb("1RWT.pdb", "A")
    out_2bhw = process_pdb("2BHW.pdb", "A")
    out_path = WP1 / "lhcii_pdb_dipoles.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"1RWT_chainA": out_1rwt, "2BHW_chainA": out_2bhw}, f, indent=2)
    print(f"Saved {out_path}")
    # Print summary key nearest-neighbor pairs (610-611-612, 601-608-609, 602-603, 613-614)
    ids = out_1rwt["site_order_pdb_ids"]
    idx = {pid: k for k, pid in enumerate(ids)}
    for a, b in [(610, 611), (611, 612), (610, 612), (602, 603), (601, 608), (608, 609), (606, 607), (613, 614)]:
        i, j = idx[a], idx[b]
        print(f"1RWT {a}-{b}: R_Mg={out_1rwt['mg_distance_angstrom'][i][j]:.2f} A, kappa={out_1rwt['orientational_factor_kappa'][i][j]:+.3f}, cos={out_1rwt['dipole_dot_cos'][i][j]:+.3f}")


if __name__ == "__main__":
    main()
