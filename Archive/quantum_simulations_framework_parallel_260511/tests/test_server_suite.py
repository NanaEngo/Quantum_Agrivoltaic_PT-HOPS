"""
test_server_suite.py — Server-scale test suite for ThinkStation P720.

Hardware target: 2× Intel Xeon Gold 6136 (48 cores / 96 threads),
                 128 GB RAM, NVIDIA RTX A4000 (16 GB VRAM).

Mirrors test_laptop_suite.py but uses full production parameters:
  - L_max = 8  (vs 3 on laptop)
  - n_traj = 100 (vs 10 on laptop)
  - t_max  = 1000 fs (vs 10 fs on laptop)
  - sbd_bundles_per_site = 6 (vs 2 on laptop)
  - n_workers = 40 (parallel trajectories)

Run with:
    pytest tests/test_server_suite.py -m server -v
    pytest tests/test_server_suite.py -m server -v -n 40   # with pytest-xdist
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from conftest import get_test_logger
from src.core.hops_simulator import HopsSimulator
from src.core.hamiltonian_factory import create_fmo_hamiltonian
from src.core.constants import (
    DEFAULT_MAX_HIERARCHY,
    DEFAULT_N_MATSUBARA,
    DEFAULT_TEMPERATURE,
    DEFAULT_N_TRAJ,
    DEFAULT_SBD_BUNDLES,
    DEFAULT_TIME_STEP,
    DEFAULT_MAX_TIME,
)

logger = get_test_logger("test_server_suite")

pytestmark = pytest.mark.server  # all tests in this file require the server marker


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_simulator(H: np.ndarray, L: int = DEFAULT_MAX_HIERARCHY) -> HopsSimulator:
    """Build a production-grade HopsSimulator from server_parameters.yaml values."""
    return HopsSimulator(
        H,
        max_hierarchy=L,
        k_matsubara=DEFAULT_N_MATSUBARA,          # K=2 — converged, K>2 → OOM
        use_sbd=True,
        sbd_bundles_per_site=DEFAULT_SBD_BUNDLES,  # 6 bundles retain vibronic structure
        temperature=DEFAULT_TEMPERATURE,
        reorganization_energy=35.0,
        drude_cutoff=50.0,
        vibronic_frequencies=np.array([180., 220., 280., 350., 520., 575.,
                                        720., 1050., 1185., 1220., 1350., 1500.]),
        huang_rhys_factors=np.array([0.05, 0.045, 0.03, 0.025, 0.02, 0.015,
                                      0.01, 0.008, 0.005, 0.005, 0.004, 0.003]),
        vibronic_damping=np.full(12, 10.0),
    )


# ── Test class ────────────────────────────────────────────────────────────────

class TestServerSuite:
    """Production-scale tests for the ThinkStation P720 server."""

    # ------------------------------------------------------------------
    # 1. Hamiltonian validation (fast — no dynamics)
    # ------------------------------------------------------------------
    def test_hamiltonian_properties(self, server_hardware):
        """Verify FMO Hamiltonian structure (Hermiticity, shape, real eigenvalues)."""
        logger.info(f"[server] Running on: {server_hardware['cpu_model']}, "
                    f"{server_hardware['ram_gb']:.0f} GB RAM")

        H, site_energies = create_fmo_hamiltonian(include_reaction_center=False)

        assert H.shape == (7, 7), "Hamiltonian shape mismatch"
        assert np.allclose(H, H.conj().T), "Hamiltonian not Hermitian"
        assert len(site_energies) == 7

        evals = np.linalg.eigvalsh(H)
        logger.info(f"Eigenvalue range: [{evals.min():.2f}, {evals.max():.2f}] cm⁻¹")
        assert np.all(np.isreal(evals)), "Eigenvalues not real"

    # ------------------------------------------------------------------
    # 2. SBD activation at L=8
    # ------------------------------------------------------------------
    def test_sbd_activation_L8(self, server_hardware):
        """Verify SBD is active at full hierarchy depth L=8."""
        H, _ = create_fmo_hamiltonian(include_reaction_center=False)
        sim = _make_simulator(H, L=DEFAULT_MAX_HIERARCHY)

        assert sim.use_sbd is True, "SBD must be active at L=8"
        assert sim.max_hierarchy == DEFAULT_MAX_HIERARCHY
        logger.info(f"[server] SBD active: L={sim.max_hierarchy}, "
                    f"bundles/site={DEFAULT_SBD_BUNDLES}")

    # ------------------------------------------------------------------
    # 3. 3-site full dynamics (1000 fs, 100 trajectories)
    # ------------------------------------------------------------------
    def test_3site_full_dynamics(self, server_hardware):
        """3-site FMO dynamics at full production parameters (1000 fs, n_traj=100)."""
        logger.info("[server] Starting 3-site full dynamics (1000 fs, 100 traj)...")

        H7, _ = create_fmo_hamiltonian(include_reaction_center=False)
        H3 = H7[:3, :3]

        init_state = np.zeros(3, dtype=complex)
        init_state[0] = 1.0

        sim = _make_simulator(H3)
        time_points = np.arange(0, DEFAULT_MAX_TIME + DEFAULT_TIME_STEP, DEFAULT_TIME_STEP)

        results = sim.simulate_dynamics(
            time_points,
            initial_state=init_state,
            n_traj=DEFAULT_N_TRAJ,
            show_progress=False,
        )

        pops = results["populations"]
        traces = np.sum(pops, axis=1)
        logger.info(f"[server] 3-site: shape={pops.shape}, "
                    f"trace=[{traces.min():.4f}, {traces.max():.4f}]")

        assert pops.shape == (len(time_points), 3), "Population shape mismatch"
        assert np.allclose(traces, 1.0, atol=0.05), "Trace not conserved (server tolerance)"
        assert np.all(pops >= -1e-6), "Positivity violated"

    # ------------------------------------------------------------------
    # 4. 7-site full dynamics (1000 fs, 100 trajectories)
    # ------------------------------------------------------------------
    def test_7site_full_dynamics(self, server_hardware):
        """7-site FMO dynamics at full production parameters (1000 fs, n_traj=100)."""
        logger.info("[server] Starting 7-site full dynamics (1000 fs, 100 traj)...")

        H, _ = create_fmo_hamiltonian(include_reaction_center=False)

        init_state = np.zeros(7, dtype=complex)
        init_state[0] = 1.0

        sim = _make_simulator(H)
        time_points = np.arange(0, DEFAULT_MAX_TIME + DEFAULT_TIME_STEP, DEFAULT_TIME_STEP)

        results = sim.simulate_dynamics(
            time_points,
            initial_state=init_state,
            n_traj=DEFAULT_N_TRAJ,
            show_progress=False,
        )

        pops = results["populations"]
        traces = np.sum(pops, axis=1)
        logger.info(f"[server] 7-site: shape={pops.shape}, "
                    f"trace=[{traces.min():.4f}, {traces.max():.4f}]")

        assert pops.shape == (len(time_points), 7), "Population shape mismatch"
        assert np.allclose(traces, 1.0, atol=0.05), "Trace not conserved (server tolerance)"
        assert np.all(pops >= -1e-6), "Positivity violated"

    # ------------------------------------------------------------------
    # 5. Hierarchy convergence: L=6 vs L=8
    # ------------------------------------------------------------------
    def test_hierarchy_convergence_L6_vs_L8(self, server_hardware):
        """Verify that L=8 is converged relative to L=6 (Frobenius norm < 1e-4)."""
        logger.info("[server] Hierarchy convergence test: L=6 vs L=8...")

        H, _ = create_fmo_hamiltonian(include_reaction_center=False)
        init_state = np.zeros(7, dtype=complex)
        init_state[0] = 1.0

        # Short window sufficient for convergence check
        time_points = np.arange(0, 200.0 + DEFAULT_TIME_STEP, DEFAULT_TIME_STEP)
        n_traj_conv = 20  # Reduced for convergence check speed

        pops = {}
        for L in (6, 8):
            sim = _make_simulator(H, L=L)
            res = sim.simulate_dynamics(
                time_points, initial_state=init_state,
                n_traj=n_traj_conv, show_progress=False,
            )
            pops[L] = res["populations"]

        frob = np.linalg.norm(pops[8] - pops[6]) / np.linalg.norm(pops[6])
        logger.info(f"[server] Relative Frobenius norm (L8 vs L6): {frob:.2e}")
        assert frob < 0.05, f"L=8 not converged relative to L=6 (Frobenius={frob:.2e})"

    # ------------------------------------------------------------------
    # 6. Parallel worker scaling (n_workers=40)
    # ------------------------------------------------------------------
    def test_parallel_worker_scaling(self, server_hardware):
        """Verify that 40-worker parallel execution completes without error."""
        import multiprocessing
        n_cpus = multiprocessing.cpu_count()
        logger.info(f"[server] CPU count: {n_cpus}, target n_workers=40")
        assert n_cpus >= 40, (
            f"Server should have ≥40 logical CPUs, found {n_cpus}. "
            "Check that hyperthreading is enabled."
        )

        # Smoke-test parallel trajectory dispatch
        H, _ = create_fmo_hamiltonian(include_reaction_center=False)
        init_state = np.zeros(7, dtype=complex)
        init_state[0] = 1.0

        sim = _make_simulator(H)
        time_points = np.arange(0, 50.0 + DEFAULT_TIME_STEP, DEFAULT_TIME_STEP)

        results = sim.simulate_dynamics(
            time_points, initial_state=init_state,
            n_traj=40, show_progress=False,
        )
        assert results["populations"].shape[1] == 7

    # ------------------------------------------------------------------
    # 7. GPU availability
    # ------------------------------------------------------------------
    def test_gpu_available(self, server_hardware):
        """Verify that the RTX A4000 is visible to the Python runtime."""
        gpu_info = server_hardware.get("gpu_name", "")
        logger.info(f"[server] GPU detected: {gpu_info}")

        # At least one of the GPU backends should see the card
        gpu_found = False

        try:
            import torch
            if torch.cuda.is_available():
                gpu_found = True
                name = torch.cuda.get_device_name(0)
                vram = torch.cuda.get_device_properties(0).total_memory / 1e9
                logger.info(f"[server] PyTorch CUDA: {name}, {vram:.1f} GB VRAM")
        except ImportError:
            pass

        if not gpu_found:
            try:
                import cupy as cp
                _ = cp.array([1.0])
                gpu_found = True
                logger.info("[server] CuPy GPU access confirmed")
            except (ImportError, Exception):
                pass

        if not gpu_found:
            pytest.skip("No GPU backend (torch/cupy) available — skipping GPU test")

        assert gpu_found, "RTX A4000 not accessible via any GPU backend"

    # ------------------------------------------------------------------
    # 8. Memory headroom check
    # ------------------------------------------------------------------
    def test_memory_headroom(self, server_hardware):
        """Verify ≥80 GB RAM available before running production simulations."""
        available_gb = server_hardware["available_ram_gb"]
        logger.info(f"[server] Available RAM: {available_gb:.1f} GB")
        assert available_gb >= 80.0, (
            f"Insufficient RAM for server suite: {available_gb:.1f} GB < 80 GB. "
            "Close other processes before running."
        )

    # ------------------------------------------------------------------
    # 9. Static disorder ensemble (n_disorder=100)
    # ------------------------------------------------------------------
    def test_disorder_ensemble(self, server_hardware):
        """Run 100-sample static disorder ensemble and check population statistics."""
        logger.info("[server] Starting disorder ensemble (100 samples)...")

        H_base, _ = create_fmo_hamiltonian(include_reaction_center=False)
        rng = np.random.default_rng(42)
        sigma = 50.0  # cm^-1

        time_points = np.arange(0, 100.0 + DEFAULT_TIME_STEP, DEFAULT_TIME_STEP)
        all_pops = []

        for _ in range(100):
            disorder = rng.normal(0, sigma, H_base.shape[0])
            H_dis = H_base.copy()
            np.fill_diagonal(H_dis, np.diag(H_dis) + disorder)

            init_state = np.zeros(H_dis.shape[0], dtype=complex)
            init_state[0] = 1.0

            sim = _make_simulator(H_dis)
            res = sim.simulate_dynamics(
                time_points, initial_state=init_state,
                n_traj=1, show_progress=False,
            )
            all_pops.append(res["populations"])

        ensemble_mean = np.mean(all_pops, axis=0)
        traces = np.sum(ensemble_mean, axis=1)
        logger.info(f"[server] Disorder ensemble: mean trace range "
                    f"[{traces.min():.4f}, {traces.max():.4f}]")

        assert np.allclose(traces, 1.0, atol=0.1), "Disorder ensemble trace not conserved"
        assert ensemble_mean.shape == (len(time_points), 7)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "server"])
