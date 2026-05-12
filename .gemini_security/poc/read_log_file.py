import os

log_file = "/media/taamangtchu/MYDATA/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/logs/tests_20260512_064614.log"

if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        print(f"--- LOG CONTENT: {os.path.basename(log_file)} ---")
        print(f.read())
else:
    print(f"Error: Log file not found at {log_file}")
