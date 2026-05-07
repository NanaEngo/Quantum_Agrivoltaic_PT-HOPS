#!/usr/bin/env python
"""
Debug script for TestHopsSimulatorFallback::test_populations_key_present
Runs the test with logging every 5 seconds to track progress.
"""
import sys
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from core.hamiltonian_factory import create_fmo_hamiltonian
from core.hops_simulator import HopsSimulator

def run_test():
    logger.info("=" * 60)
    logger.info("Starting test_populations_key_present debug")
    logger.info("=" * 60)
    
    # Setup
    logger.info("[0s] Loading FMO Hamiltonian...")
    H, e = create_fmo_hamiltonian(include_reaction_center=False)
    logger.info(f"[{time.time():.1f}s] Hamiltonian shape: {H.shape}")
    
    logger.info("[0s] Creating HopsSimulator with use_mesohops=False...")
    sim = HopsSimulator(H, use_mesohops=False)
    logger.info(f"[{time.time():.1f}s] sim.use_mesohops: {sim.use_mesohops}")
    logger.info(f"[{time.time():.1f}s] sim.fallback_sim: {sim.fallback_sim}")
    
    # Time points
    logger.info("[0s] Creating time points...")
    short_time = np.arange(0, 50, 0.5)
    logger.info(f"[{time.time():.1f}s] short_time shape: {short_time.shape}")
    
    # Initial state
    logger.info("[0s] Creating initial state...")
    initial_state = np.zeros(H.shape[0], dtype=complex)
    initial_state[0] = 1.0
    logger.info(f"[{time.time():.1f}s] initial_state: {initial_state}")
    
    # Run simulation
    logger.info("[0s] Calling simulate_dynamics...")
    start = time.time()
    result = sim.simulate_dynamics(short_time, initial_state)
    elapsed = time.time() - start
    logger.info(f"[{elapsed:.1f}s] simulate_dynamics completed")
    
    # Check result
    logger.info("[0s] Checking result...")
    logger.info(f"[{time.time():.1f}s] result type: {type(result)}")
    logger.info(f"[{time.time():.1f}s] result keys: {list(result.keys())}")
    
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    logger.info("[0s] Result is dict ✓")
    
    assert "populations" in result, "Missing 'populations' key"
    logger.info("[0s] 'populations' key present ✓")
    
    pops = result["populations"]
    logger.info(f"[{time.time():.1f}s] populations shape: {pops.shape}")
    logger.info(f"[{time.time():.1f}s] populations[0,0]: {pops[0,0]}")
    
    logger.info("=" * 60)
    logger.info("TEST PASSED!")
    logger.info("=" * 60)

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        logger.error(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
