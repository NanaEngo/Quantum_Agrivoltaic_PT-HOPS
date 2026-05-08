#!/usr/bin/env python
"""
Benchmark script for parallel/GPU performance testing.
Tests CPU parallel vs GPU batch processing.
"""

import sys
import os
import time
import numpy as np
from pathlib import Path

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.hamiltonian_factory import create_fmo_hamiltonian
from models.simple_quantum_dynamics_simulator import SimpleQuantumDynamicsSimulator
from utils.parallel_utils import parallel_trajectory_simulation

# Try GPU imports
try:
    from core.gpu_dynamics import GPUQuantumDynamics, JAX_AVAILABLE
except ImportError:
    JAX_AVAILABLE = False

print("="*80)
print("PARALLEL/GPU PERFORMANCE BENCHMARK")
print("="*80)
print()

# Setup
H = create_fmo_hamiltonian(include_reaction_center=False)
n_sites = H.shape[0]
time_points = np.linspace(0, 1000, 201)  # 5 fs step
n_traj_list = [1, 10, 50, 100]

print(f"System: {n_sites}-site FMO complex")
print(f"Time grid: {len(time_points)} points (0-1000 fs)")
print(f"Trajectories: {n_traj_list}")
print()

# Benchmark 1: Single-threaded CPU
print("-"*80)
print("BENCHMARK 1: Single-threaded CPU")
print("-"*80)

sim = SimpleQuantumDynamicsSimulator(H, temperature=295.0)
initial_state = np.zeros(n_sites, dtype=np.complex128)
initial_state[0] = 1.0

for n_traj in n_traj_list:
    start = time.time()
    for i in range(n_traj):
        result = sim.simulate_dynamics(time_points=time_points, initial_state=initial_state)
    elapsed = time.time() - start
    print(f"  {n_traj:3d} trajectories: {elapsed:6.2f} s ({elapsed/n_traj:.3f} s/traj)")

print()

# Benchmark 2: CPU Parallel (40 workers)
print("-"*80)
print("BENCHMARK 2: CPU Parallel (40 workers)")
print("-"*80)

def simulate_single(seed):
    np.random.seed(seed)
    return sim.simulate_dynamics(time_points=time_points, initial_state=initial_state)

for n_traj in n_traj_list:
    if n_traj == 1:
        print(f"  {n_traj:3d} trajectories: (skipped - no parallelization benefit)")
        continue
    
    start = time.time()
    results = parallel_trajectory_simulation(
        list(range(n_traj)),
        simulate_single,
        n_workers=min(40, n_traj)
    )
    elapsed = time.time() - start
    speedup = (n_traj * 0.8) / elapsed  # Estimate based on single-thread time
    print(f"  {n_traj:3d} trajectories: {elapsed:6.2f} s ({elapsed/n_traj:.3f} s/traj, ~{speedup:.1f}× speedup)")

print()

# Benchmark 3: GPU Batch (if available)
if JAX_AVAILABLE:
    print("-"*80)
    print("BENCHMARK 3: GPU Batch (JAX)")
    print("-"*80)
    
    gpu_sim = GPUQuantumDynamics(H, temperature=295.0, use_gpu=True)
    
    for n_traj in n_traj_list:
        # Create batch of initial states
        initial_states = np.zeros((n_traj, n_sites, n_sites), dtype=np.complex128)
        initial_states[:, 0, 0] = 1.0
        
        # Warmup (JIT compilation)
        if n_traj == n_traj_list[0]:
            print("  (JIT compilation warmup...)")
            _ = gpu_sim.simulate_batch_trajectories(initial_states[:2], time_points[:10], method='rk4')
        
        start = time.time()
        trajectories = gpu_sim.simulate_batch_trajectories(initial_states, time_points, method='rk4')
        elapsed = time.time() - start
        speedup = (n_traj * 0.8) / elapsed
        print(f"  {n_traj:3d} trajectories: {elapsed:6.2f} s ({elapsed/n_traj:.3f} s/traj, ~{speedup:.1f}× speedup)")
    
    print()
else:
    print("-"*80)
    print("BENCHMARK 3: GPU Batch (JAX)")
    print("-"*80)
    print("  JAX not available - GPU benchmark skipped")
    print()

print("="*80)
print("BENCHMARK COMPLETE")
print("="*80)
print()
print("Recommendations:")
print("  - For n_traj < 10: Use single-threaded CPU")
print("  - For 10 ≤ n_traj < 50: Use CPU parallel (40 workers)")
print("  - For n_traj ≥ 50: Use GPU batch (if available)")
print()
