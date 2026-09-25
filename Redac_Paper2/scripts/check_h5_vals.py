#!/usr/bin/env python3
"""Extrait les grandeurs canoniques d'un HDF5 de production (cote HPC, h5py).

Usage : python check_h5_vals.py <file.h5>
Sortie (1 ligne) : rc_yield=...,sum_trapped_pop=...,n_frames=...,t_max_fs=...
Canon 2026-09-23 : Phi_FT = Gamma_RC * sum(trapped_pop) * dt, SANS prefacteur 2.
"""
import sys

import h5py
import numpy as np


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_h5_vals.py <file.h5>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    try:
        with h5py.File(path, "r") as f:
            dy = f["dynamics"]
            ry = float(dy["rc_yield"][-1])
            tp = float(np.asarray(dy["trapped_pop"][...]).sum())
            nf = int(dy["rc_yield"].shape[0])
            tmax = float(dy["time"][-1]) if "time" in dy else float("nan")
    except Exception as exc:  # noqa: BLE001 — on veut le message, pas un crash
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        f"rc_yield={ry:.6f},sum_trapped_pop={tp:.4f},"
        f"n_frames={nf},t_max_fs={tmax:.1f}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
