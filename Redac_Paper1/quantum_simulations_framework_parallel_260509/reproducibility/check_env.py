import sys
import importlib

def check_package(package_name):
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name} is available.")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT available.")
        return False

def main():
    print("--- MesoHOP-sim Environment Validation ---")
    packages = ["mesohops", "numpy", "h5py", "yaml", "matplotlib", "scipy"]
    all_ok = True
    for pkg in packages:
        if not check_package(pkg):
            all_ok = False
    
    if all_ok:
        print("\n🚀 Environment is READY for PT-HOPS/SBD simulation.")
        sys.exit(0)
    else:
        print("\n⚠️ Environment is INCOMPLETE. Please run: mamba run -n MesoHOP-sim python check_env.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
