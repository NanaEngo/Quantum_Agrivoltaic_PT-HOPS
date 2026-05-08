import os
import sys
import numpy as np

# Add framework to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from core.hops_simulator import HopsSimulator, MESOHOPS_AVAILABLE
    from core.hamiltonian_factory import create_fmo_hamiltonian
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_hops():
    if not MESOHOPS_AVAILABLE:
        print("❌ MesoHOPS not available")
        return

    print("🚀 Starting small HOPS test (L=2, 3 sites)...")
    
    # 3-site Hamiltonian
    H = np.array([
        [12410, -87.7, 5.5],
        [-87.7, 12530, 30.8],
        [5.5, 30.8, 12210]
    ], dtype=complex)
    
    init_state = np.zeros(3, dtype=complex)
    init_state[0] = 1.0
    
    time_points = np.linspace(0, 100, 11)
    
    try:
        sim = HopsSimulator(
            H,
            max_hierarchy=2,
            k_matsubara=1,
            reorganization_energy=35.0,
            drude_cutoff=50.0,
            use_sbd=False
        )
        
        print(f"Simulator type: {sim.simulator_type}")
        results = sim.simulate_dynamics(time_points, initial_state=init_state)
        
        print("✅ Simulation successful!")
        print(f"Final populations: {results['populations'][-1]}")
        print(f"Final trace: {np.sum(results['populations'][-1]):.4f}")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hops()
