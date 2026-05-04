#!/usr/bin/env python3
"""
check_env.py — Environment validation for MesoHOPS simulations.

Checks all required packages and verifies the MesoHOPS API is functional
(correct import paths for bcf_exp and bcf_convert_dl_to_exp).
"""

import sys
import importlib


def check_package(name: str) -> bool:
    try:
        importlib.import_module(name)
        print(f"  ✅ {name}")
        return True
    except ImportError:
        print(f"  ❌ {name} — NOT available")
        return False


def check_mesohops_api() -> bool:
    """Verify the specific MesoHOPS functions used by HopsSimulator."""
    ok = True
    checks = [
        ("mesohops.trajectory.hops_trajectory", "HopsTrajectory"),
        ("mesohops.trajectory.exp_noise", "bcf_exp"),
        ("mesohops.util.bath_corr_functions", "bcf_convert_dl_to_exp"),
    ]
    for module, attr in checks:
        try:
            mod = importlib.import_module(module)
            getattr(mod, attr)
            print(f"  ✅ {module}.{attr}")
        except (ImportError, AttributeError) as e:
            print(f"  ❌ {module}.{attr} — {e}")
            ok = False
    return ok


def main() -> None:
    print("─── MesoHOP-sim Environment Validation ───")
    print("\nCore packages:")
    packages = ["mesohops", "numpy", "scipy", "h5py", "yaml", "matplotlib", "numba"]
    all_ok = all(check_package(p) for p in packages)

    print("\nMesoHOPS API (corrected import paths):")
    api_ok = check_mesohops_api()

    print()
    if all_ok and api_ok:
        print("🚀 Environment is READY for PT-HOPS simulation.")
        sys.exit(0)
    else:
        print("⚠️  Environment is INCOMPLETE. Check missing items above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
