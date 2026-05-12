import subprocess
import sys
import os

def run_mamba_tests():
    print("Attempting to run tests with mamba run -n MesoHOP-sim...")
    
    # Path to the test file
    test_file = "/media/taamangtchu/MYDATA/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/quantum_simulations_framework_parallel_260509/tests/test_laptop_suite.py"
    
    # The command requested by the user
    command = [
        "mamba", "run", "-n", "MesoHOP-sim", 
        "pytest", test_file, "-v", "-s"
    ]
    
    try:
        # Execute the command
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        # Print output
        print("--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        
        if result.returncode == 0:
            print("Tests completed successfully within the mamba environment.")
        else:
            print(f"Tests failed with return code {result.returncode}.")
            
    except FileNotFoundError:
        print("Error: 'mamba' command not found in the environment path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_mamba_tests()
