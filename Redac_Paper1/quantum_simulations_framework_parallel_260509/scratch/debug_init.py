
import sys
import os
from pathlib import Path
import numpy as np

# Add the project directory to sys.path
sys.path.insert(0, "/home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/quantum_simulations_framework_parallel_260509")

try:
    from core.hops_simulator import HopsSimulator
    from core.hamiltonian_factory import create_fmo_hamiltonian
    
    H, _ = create_fmo_hamiltonian(include_reaction_center=False)
    print("Hamiltonian created.")
    
    simulator = HopsSimulator(H, temperature=295.0, use_mesohops=False)
    print("HopsSimulator initialized (use_mesohops=False).")
    
    simulator_mh = HopsSimulator(H, temperature=295.0, use_mesohops=True)
    print("HopsSimulator initialized (use_mesohops=True).")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
