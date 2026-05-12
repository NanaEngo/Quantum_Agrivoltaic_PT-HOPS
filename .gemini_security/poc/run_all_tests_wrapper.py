import subprocess
import sys
import os

def run_all_tests():
    print("Attempting to run ALL tests in the tests/ directory with mamba run -n MesoHOP-sim...")
    
    # Path to the tests directory
    tests_dir = "/media/taamangtchu/MYDATA/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/quantum_simulations_framework_parallel_260509/tests/"
    
    # Run pytest on the whole directory
    command = [
        "mamba", "run", "-n", "MesoHOP-sim", 
        "pytest", tests_dir, "-v"
    ]
    
    try:
        # Execute the command
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        # Print summary
        print("--- STDOUT (Summary) ---")
        lines = result.stdout.splitlines()
        if len(lines) > 50:
            print("\n".join(lines[:20]))
            print("...")
            print("\n".join(lines[-30:]))
        else:
            print(result.stdout)
            
        print("--- STDERR ---")
        print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ ALL tests passed successfully.")
        else:
            print(f"\n❌ Some tests failed (Exit Code: {result.returncode}).")
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_all_tests()
