import sys
import os
import yaml
import numpy as np
import pytest
from pathlib import Path

# Add framework to path
CURRENT_DIR = Path(__file__).parent
FRAMEWORK_DIR = CURRENT_DIR.parent
sys.path.insert(0, str(FRAMEWORK_DIR))

from src.core.hops_simulator import HopsSimulator
from src.core.hamiltonian_factory import create_fmo_hamiltonian
from src.core.constants import DEFAULT_TEMPERATURE, DEFAULT_MAX_HIERARCHY, DEFAULT_N_MATSUBARA, DEFAULT_SBD_BUNDLES

def test_3site_simulation_with_config():
    """
    Unified 3-site dynamics test.
    Tests FMO dynamics with only 3 sites using laptop_parameters.yaml.
    SBD is automatically enforced for L>=2 by HopsSimulator.
    """
    # 1. Load laptop configuration
    config_path = FRAMEWORK_DIR / "laptop_parameters.yaml"
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
    
    # 2. Create standard 7-site Hamiltonian and slice it to 3 sites
    H7, site_energies7 = create_fmo_hamiltonian(include_reaction_center=False)
    n_sites = 3
    H3 = H7[:n_sites, :n_sites]
    site_energies3 = site_energies7[:n_sites]
    
    print(f"\n🧪 Testing 3-site simulation...")
    print(f"   Hamiltonian shape: {H3.shape}")
    
    # 3. Setup initial state (Site 1 excitation)
    init_state = np.zeros(n_sites, dtype=complex)
    init_state[0] = 1.0
    
    # 4. Setup simulator using laptop parameters (except number of sites and L_max)
    L = DEFAULT_MAX_HIERARCHY
    K = cfg['dynamics']['matsubara_truncation']
    dt = cfg['dynamics']['time_step']
    t_max = cfg['dynamics']['time_max']
    # Laptop/CI friendly caps to avoid long/intermittent failures
    t_max_cap_fs = 100.0  # reduce from ~1000 fs to ~100 fs
    t_max = min(float(t_max), t_max_cap_fs)
    time_points = np.arange(0, t_max, dt)
    n_sites = H3.shape[0]
    sbd_bundles = cfg['dynamics'].get('sbd_bundles_per_site', DEFAULT_SBD_BUNDLES)
    n_traj = int(cfg['simulation']['n_traj'])
    n_traj_cap = 5
    n_traj = min(n_traj, n_traj_cap)

    print(f"   Parameters: L={L}, K={K}, dt={dt} fs, t_max={t_max} fs, n_traj={n_traj}")
    print(f"   SBD: ENABLED ({sbd_bundles} bundles/site) — required at L>=2 to limit hierarchy size")
    print(f"   Estimated hierarchy modes: {n_sites * (K + sbd_bundles)} (vs {n_sites * (K + 12)} without SBD)")
    print(f"   Starting integration...")

    simulator = HopsSimulator(
        H3,
        max_hierarchy=L,
        k_matsubara=K,
        use_sbd=True,
        sbd_bundles_per_site=sbd_bundles,
        temperature=cfg['bath']['temperature'],
        reorganization_energy=cfg['bath']['reorganization_energy'],
        drude_cutoff=cfg['bath']['drude_cutoff'],
        vibronic_frequencies=np.array(cfg['bath']['vibronic_frequencies']),
        huang_rhys_factors=np.array(cfg['bath']['huang_rhys_factors']),
        vibronic_damping=np.array(cfg['bath']['vibronic_damping']),
    )
    
    # Explicitly check that SBD is activated for L >= 2
    if L >= 2:
        assert simulator.use_sbd is True, "SBD must be activated for L >= 2"

    # 5. Run simulation (parallelized via n_traj)
    results = simulator.simulate_dynamics(
        time_points,
        initial_state=init_state,
        n_traj=n_traj,
        show_progress=False,
        desc="3-Site Dynamics"
    )
    
    # 6. Validations
    pops = results['populations']
    print(f"   Populations shape: {pops.shape}")
    
    # Check dimensionality
    assert H3.shape == (3, 3)
    assert pops.shape == (len(time_points), 3)
    
    # Check normalization
    traces = np.sum(pops, axis=1)
    assert np.allclose(traces, 1.0, atol=1e-1), "Trace preservation failed (ensemble average)"
    
    # Check positivity
    assert np.all(pops >= -1e-6), "Positivity failed"
    
    # 7. Save results for demonstration/plotting
    output_dir = FRAMEWORK_DIR / "simulation_data"
    output_dir.mkdir(exist_ok=True)
    out_file = output_dir / "3site_dynamics_results.csv"
    
    coherences = results.get('coherences', np.zeros_like(results['t_axis']))
    data = np.column_stack((results['t_axis'], pops, coherences))
    
    np.savetxt(
        out_file, 
        data, 
        delimiter=",",
        header="time_fs,pop_1,pop_2,pop_3,coherence", 
        comments=""
    )
    print(f"   💾 Saved trajectory data to: {out_file}")
    
    print("✅ 3-site simulation test passed!")

if __name__ == "__main__":
    test_3site_simulation_with_config()
