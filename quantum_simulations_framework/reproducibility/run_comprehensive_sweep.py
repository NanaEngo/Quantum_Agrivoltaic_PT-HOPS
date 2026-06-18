#!/usr/bin/env python3
"""
Comprehensive sweep orchestrator for JPCL revision.
Runs convergence tests (L, K, dt) and robustness tests (bath, temp, filter, chirp)
on the server with the corrected vibronic bath code.

Usage:
    python reproducibility/run_comprehensive_sweep.py [--n-traj N] [--dry-run]

Defaults:
    --n-traj 1 for convergence sweeps, 20 for robustness sweeps
"""

import os, sys, json, yaml, copy, subprocess, time, glob, argparse, shutil
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "server_production.yaml")
RESULTS_DIR = os.path.join(BASE_DIR, "reproducibility", "results")
MAIN_PY = os.path.join(BASE_DIR, "reproducibility", "main.py")

with open(CONFIG_PATH) as f:
    BASE_CFG = yaml.safe_load(f)

def run_sweep(label, cfg_mods, n_traj=1, parallel=True, dry_run=False):
    """Run a sweep with modified config."""
    cfg = copy.deepcopy(BASE_CFG)
    for k, v in cfg_mods.items():
        parts = k.split(".")
        d = cfg
        for p in parts[:-1]:
            d = d[p]
        d[parts[-1]] = v

    cfg["simulation"]["n_traj"] = n_traj
    if "n_traj_temp_sweep" in cfg["simulation"]:
        cfg["simulation"]["n_traj_temp_sweep"] = n_traj

    tmp_yaml = os.path.join(BASE_DIR, "config", f"_sweep_{label}.yaml")
    with open(tmp_yaml, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)

    cmd = [sys.executable, MAIN_PY, "--config", tmp_yaml, "--skip-audit"]
    if parallel:
        cmd.append("--parallel")

    if dry_run:
        print(f"[DRY-RUN] {label}: {' '.join(cmd)}")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = os.path.join(BASE_DIR, "reproducibility", f"sweep_{label}_{timestamp}.log")
    print(f"[{timestamp}] Starting {label}: n_traj={n_traj}, log={logfile}")
    sys.stdout.flush()

    with open(logfile, "w") as lf:
        proc = subprocess.run(cmd, cwd=BASE_DIR, stdout=lf, stderr=subprocess.STDOUT,
                              timeout=86400)  # 24h timeout per sweep

    if proc.returncode != 0:
        print(f"  ⚠ {label} returned code {proc.returncode}")
    else:
        print(f"  ✅ {label} completed")

    # Tag output CSVs
    for f in glob.glob(os.path.join(RESULTS_DIR, "fmo_dynamics_*.csv")):
        base = os.path.basename(f)
        tagged = base.replace(".csv", f"_{label}.csv")
        os.rename(f, os.path.join(RESULTS_DIR, tagged))
        print(f"  → Tagged: {tagged}")

    os.remove(tmp_yaml)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-traj-conv", type=int, default=1, help="Trajs per convergence test")
    parser.add_argument("--n-traj-robust", type=int, default=20, help="Trajs per robustness test")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-conv", action="store_true")
    parser.add_argument("--skip-robust", action="store_true")
    args = parser.parse_args()

    sweeps = []

    if not args.skip_conv:
        # 1. L-sweep (vibronic)
        for L in [6, 7, 9]:
            if L == 8:
                continue  # already done in production
            sweeps.append((f"L{L}", {"dynamics.L_max": L}, args.n_traj_conv))

        # 2. K-sweep
        for K in [1, 3]:
            sweeps.append((f"K{K}", {"dynamics.matsubara_truncation": K}, args.n_traj_conv))

        # 3. dt-sweep
        for dt in [0.1, 1.0, 2.0]:
            sweeps.append((f"dt{dt}", {"dynamics.time_step": dt}, args.n_traj_conv))

    if not args.skip_robust:
        # 4. Bath sensitivity: λ_D ± 20%
        lam_base = BASE_CFG["bath"]["reorganization_energy"]
        for lam in [lam_base * 0.8, lam_base * 1.2]:
            sweeps.append((f"lambda{lam:.0f}", {"bath.reorganization_energy": lam}, args.n_traj_robust))

        # 5. Bath sensitivity: γ_D ± 20%
        gam_base = BASE_CFG["bath"]["drude_cutoff"]
        for gam in [gam_base * 0.8, gam_base * 1.2]:
            sweeps.append((f"gamma{gam:.0f}", {"bath.drude_cutoff": gam}, args.n_traj_robust))

        # 6. Temperature sweep
        for T in [285, 290, 300, 305, 310]:
            sweeps.append((f"T{T}", {"bath.temperature": float(T)}, args.n_traj_robust))

        # 7. Filter center variation
        filters = {
            "filt770_820": ([770.0, 820.0],),
            "filt730_820": ([730.0, 820.0],),
            "filt750_800": ([750.0, 800.0],),
        }
        for fname, (centers,) in filters.items():
            sweeps.append((fname, {"spectral_filter.band_centers_nm": list(centers)}, args.n_traj_robust))

        # 8. Chirp test (emulated by varying filter bandwidth)
        for bw in [50.0, 200.0]:
            sweeps.append((f"bw{bw:.0f}", {"spectral_filter.bandwidth_cm": bw}, args.n_traj_robust))

        # 9. Single-band filters (negative controls)
        for nm in [700, 850]:
            sweeps.append((f"single{nm}", {
                "spectral_filter.band_centers_nm": [float(nm)],
                "spectral_filter.bandwidth_cm": 100.0
            }, args.n_traj_robust))

    total_trajs = sum(n for _, _, n in sweeps)
    print(f"=== Comprehensive Sweep Plan ===")
    print(f"  Total sweeps: {len(sweeps)}")
    print(f"  Total trajectories: {total_trajs} (filtered+broadband combined)")
    print()

    for i, (label, mods, n) in enumerate(sweeps):
        print(f"  [{i+1}/{len(sweeps)}] {label}: n_traj={n}")
        for k, v in mods.items():
            print(f"      {k} = {v}")

    if args.dry_run:
        print("\n[Dry run mode — no execution]")
        return

    print("\n=== Starting sweeps ===")
    for i, (label, mods, n) in enumerate(sweeps):
        run_sweep(label, mods, n_traj=n, parallel=True)
        print(f"  [{i+1}/{len(sweeps)}] Done — {label}")
        sys.stdout.flush()

    print("\n=== All sweeps completed ===")

if __name__ == "__main__":
    main()
