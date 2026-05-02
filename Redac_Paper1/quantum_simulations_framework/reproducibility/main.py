"""
main.py — Single-entry reproducibility pipeline for JPCL revision.
Usage: mamba run -n MesoHOP-sim python reproducibility/main.py
"""
import os
import sys
import logging
import yaml
from datetime import datetime

# Ensure framework is importable regardless of CWD
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_FRAMEWORK_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, '..'))
sys.path.insert(0, _FRAMEWORK_DIR)
sys.path.insert(0, _SCRIPT_DIR)  # so audit_convergence is importable

_LOG_DIR = os.path.join(_SCRIPT_DIR, 'logs')
os.makedirs(_LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(_LOG_DIR, f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_and_validate_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'parameters.yaml'))
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)

    L = cfg['dynamics']['hierarchy_depth']
    K = cfg['dynamics']['matsubara_truncation']
    if L < 10:
        raise ValueError(f"hierarchy_depth={L} < 10. JPCL revision requires L=10.")
    if K < 10:
        raise ValueError(f"matsubara_truncation={K} < 10. JPCL revision requires K=10.")

    logger.info(f"Config validated: L={L}, K={K}, T={cfg['bath']['temperature']}K")
    return cfg


def check_environment():
    try:
        import mesohops
        version = getattr(mesohops, '__version__', 'unknown')
        print(f"  ✅ MesoHOPS {version} available")
        logger.info(f"MesoHOPS {version} available")
        return True
    except ImportError:
        print("  ❌ MesoHOPS NOT found. Run: mamba run -n MesoHOP-sim python reproducibility/main.py")
        logger.error("MesoHOPS not available")
        return False


def run_convergence_audit():
    print("\n[Step 2] Running convergence audit (L=9,10,11)...")
    from audit_convergence import run_convergence_audit as _audit
    _audit()


def generate_figures(cfg):
    print("\n[Step 3] Generating publication figures...")
    try:
        from utils.figure_generator import FigureGenerator
        jpcl_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', 'Theory_Journals', 'JPCL'
        ))
        gen = FigureGenerator(figures_dir=jpcl_dir)
        logger.info(f"Figures will be saved to {jpcl_dir}")
        print(f"  ✅ Figure generator ready → {jpcl_dir}")
        print("  ℹ️  Run individual figure scripts or call gen.plot_* methods with converged data.")
    except Exception as e:
        print(f"  ⚠️  Figure generator error: {e}")
        logger.warning(f"Figure generator: {e}")


def main():
    print("=" * 60)
    print("  Quantum Agrivoltaic PT-HOPS — JPCL Reproducibility Pipeline")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: Validate config
    print("\n[Step 1] Loading and validating parameters.yaml...")
    try:
        cfg = load_and_validate_config()
        L = cfg['dynamics']['hierarchy_depth']
        K = cfg['dynamics']['matsubara_truncation']
        print(f"  ✅ L={L}, K={K}, T={cfg['bath']['temperature']}K — all mandates satisfied")
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        sys.exit(1)

    # Step 1b: Check environment
    print("\n[Step 1b] Checking MesoHOPS environment...")
    mesohops_ok = check_environment()
    if not mesohops_ok:
        print("\n⚠️  Cannot run simulations without MesoHOPS. Exiting.")
        sys.exit(1)

    # Step 2: Convergence audit
    run_convergence_audit()

    # Step 3: Figure generation
    generate_figures(cfg)

    print("\n" + "=" * 60)
    print("  Pipeline complete. Check logs/ for execution details.")
    print("=" * 60)


if __name__ == "__main__":
    main()
