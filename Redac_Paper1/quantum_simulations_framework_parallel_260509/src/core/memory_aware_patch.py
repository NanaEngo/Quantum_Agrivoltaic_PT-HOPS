"""
Integration patch for HopsSimulator to use MemoryAwareJobScheduler.

This module patches the _simulate_with_mesohops method to use batch-wise
execution instead of launching all trajectories at once.

Changes:
1. Memory validation before starting simulation
2. Batch-wise trajectory execution to prevent joblib queue explosion
3. Explicit garbage collection between batches
4. Enhanced logging for memory tracking
"""

import gc
import logging
from typing import Dict, Any, List, Optional
import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)


def apply_memory_aware_patching():
    """
    Apply memory-aware patching to HopsSimulator._simulate_with_mesohops.

    This patches the method to use MemoryAwareJobScheduler and batch-wise
    execution instead of launching all trajectories at once.

    This should be called early in the module initialization, before any
    HopsSimulator instances are created.
    """
    try:
        from src.core.hops_simulator import HopsSimulator
        from src.core.memory_manager import MemoryAwareJobScheduler
    except ImportError:
        try:
            from .hops_simulator import HopsSimulator
            from .memory_manager import MemoryAwareJobScheduler
        except ImportError:
            logger.error("Failed to import HopsSimulator or MemoryAwareJobScheduler")
            return

    # Store original method
    original_simulate = HopsSimulator._simulate_with_mesohops

    def _simulate_with_mesohops_patched(
        self,
        time_points: NDArray[np.float64],
        initial_state: Optional[NDArray[np.float64]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Patched version with memory-aware batch execution.

        Replaces the original method which launched all trajectories at once
        with a batch-wise approach that:
        1. Validates memory feasibility
        2. Executes trajectories in batches
        3. Frees memory between batches
        4. Collects results from all batches
        """
        from joblib import Parallel, delayed
        from tqdm.auto import tqdm

        if not hasattr(self, "system_param") or self.system_param is None:
            raise RuntimeError("MesoHOPS not available for simulation")

        # ===== Step 1: Memory Validation =====
        logger.info("Starting memory-aware MesoHOPS simulation")

        n_traj = kwargs.get("n_traj", self.n_traj if hasattr(self, "n_traj") else 1)

        scheduler = MemoryAwareJobScheduler(
            L_max=kwargs.get("max_hierarchy", self.max_hierarchy),
            K_max=kwargs.get("k_matsubara", self.k_matsubara),
            total_trajectories=n_traj,
        )

        try:
            sched_info = scheduler.validate_and_adapt()
        except ValueError as e:
            logger.error(f"Memory validation failed: {e}")
            raise

        n_jobs = sched_info["n_jobs"]
        batch_size = sched_info["batch_size"]
        n_batches = sched_info["n_batches"]

        scheduler.print_report()

        # ===== Step 2: Prepare common worker parameters =====
        from src.core.hops_simulator import _run_single_traj_worker

        t_max = float(np.max(time_points)) if len(time_points) > 0 else 1000.0
        dt_save = kwargs.get(
            "dt", float(time_points[1] - time_points[0]) if len(time_points) > 1 else 1.0
        )

        # Import necessary parameters
        try:
            from src.core.constants import (
                MESOHOPS_SEED,
                FFT_NOISE_BUFFER_FS,
                MESOHOPS_EARLY_STEPS,
                MESOHOPS_INCHWORM_CAP,
            )
        except ImportError:
            from .constants import (
                MESOHOPS_SEED,
                FFT_NOISE_BUFFER_FS,
                MESOHOPS_EARLY_STEPS,
                MESOHOPS_INCHWORM_CAP,
            )

        noise_param = {
            "SEED": kwargs.get("seed", MESOHOPS_SEED),
            "MODEL": "FFT_FILTER",
            "TLEN": float(t_max + FFT_NOISE_BUFFER_FS),
            "TAU": float(dt_save * 0.5),
        }

        integrator_param = {
            "INTEGRATOR": "RUNGE_KUTTA",
            "EARLY_ADAPTIVE_INTEGRATOR": "INCH_WORM",
            "EARLY_INTEGRATOR_STEPS": MESOHOPS_EARLY_STEPS,
            "INCHWORM_CAP": MESOHOPS_INCHWORM_CAP,
            "STATIC_BASIS": None,
        }

        # Determine trajectory class
        try:
            from src.extensions.mesohops_adapters import SBD_HopsTrajectory
        except ImportError:
            try:
                from ..extensions.mesohops_adapters import SBD_HopsTrajectory
            except ImportError:
                SBD_HopsTrajectory = None

        try:
            from mesohops.trajectory.hops_trajectory import HopsTrajectory
        except ImportError:
            HopsTrajectory = None

        TrajectoryClass = HopsTrajectory
        if self.use_sbd and SBD_HopsTrajectory is not None:
            TrajectoryClass = SBD_HopsTrajectory
            logger.info("Using SBD_HopsTrajectory for simulation")

        # Build traj_kwargs (shared across all batches)
        eom_param = {
            "EQUATION_OF_MOTION": "NORMALIZED NONLINEAR",
            "TIME_DEPENDENCE": False,
        }

        n_hmodes = len(self.system_param["GW_SYSBATH"])
        max_hierarchy = kwargs.get("max_hierarchy", self.max_hierarchy)
        hierarchy_param = {
            "MAXHIER": max_hierarchy,
            "TERMINATOR": True,
            "STATIC_FILTERS": [["Triangular", [[True] * n_hmodes, max_hierarchy]]],
        }

        traj_kwargs = {
            "system_param": self.system_param,
            "eom_param": eom_param,
            "noise_param": noise_param,
            "hierarchy_param": hierarchy_param,
            "integration_param": integrator_param,
        }

        if self.use_sbd and SBD_HopsTrajectory is not None:
            traj_kwargs["n_bundles_per_site"] = kwargs.get(
                "sbd_bundles_per_site", self.sbd_bundles_per_site
            )

        worker_args = {
            "TrajectoryClass": TrajectoryClass,
            "traj_kwargs": traj_kwargs,
            "use_pt_hops": self.use_pt_hops,
            "pt_hops_noise_class": None,  # TODO: handle PT-HOPS if needed
            "system_param": self.system_param,
            "initial_state": initial_state,
            "t_max": t_max,
            "dt_save": dt_save,
            "time_points": time_points,
        }

        # ===== Step 3: Batch-wise execution =====
        logger.info(
            f"Starting batch-wise trajectory execution: {n_batches} batch(es), "
            f"{batch_size} traj/batch, {n_jobs} workers/batch"
        )

        all_results = []

        for batch_idx in range(n_batches):
            start_seed = batch_idx * batch_size
            end_seed = min(start_seed + batch_size, n_traj)
            batch_seeds = list(range(start_seed, end_seed))

            logger.info(
                f"Executing batch {batch_idx + 1}/{n_batches}: "
                f"seeds {start_seed}–{end_seed - 1} ({len(batch_seeds)} traj)"
            )

            # Create iterable with progress bar if available
            iterable = batch_seeds
            if kwargs.get("show_progress", True):
                try:
                    desc = f"{kwargs.get('desc', 'Trajectories')} (batch {batch_idx+1}/{n_batches})"
                    iterable = tqdm(batch_seeds, desc=desc, unit="traj", leave=False)
                except Exception:
                    pass

            # Run batch
            try:
                batch_results = Parallel(n_jobs=n_jobs)(
                    delayed(_run_single_traj_worker)(s, **worker_args) for s in iterable
                )
            except Exception as e:
                logger.error(f"Batch {batch_idx + 1} failed: {e}")
                raise

            # Filter successful results
            valid_results = [r for r in batch_results if r is not None]
            all_results.extend(valid_results)

            logger.info(
                f"Batch {batch_idx + 1} complete: {len(valid_results)}/{len(batch_seeds)} "
                f"trajectories succeeded"
            )

            # Memory cleanup between batches
            if batch_idx < n_batches - 1:
                logger.debug("Freeing memory between batches...")
                gc.collect()

        # ===== Step 4: Ensemble averaging (from original) =====
        if not all_results:
            raise RuntimeError("All parallel trajectories failed.")

        t_axis = all_results[0]["t_axis"]
        n_times = len(t_axis)
        n_sites = self.hamiltonian.shape[0]
        n_valid = len(all_results)

        logger.info(f"Ensemble averaging over {n_valid} trajectories...")

        density_matrices = []
        populations = np.zeros((n_times, n_sites))
        coherences = np.zeros(n_times)

        for i in range(n_times):
            rho = np.zeros((n_sites, n_sites), dtype=complex)
            for res in all_results:
                psi = res["psi_traj"][i, :n_sites]
                rho += np.outer(psi, np.conj(psi))
            rho /= n_valid

            tr = np.trace(rho).real
            if tr > 1e-10:
                rho /= tr

            density_matrices.append(rho)
            populations[i, :] = np.real(np.diag(rho))
            coherences[i] = float(np.sum(np.abs(rho)) - np.sum(np.abs(np.diag(rho))))

        # Calculate QFI, entropy, IPR
        qfi_values = np.zeros(n_times)
        entropy_values = np.zeros(n_times)
        ipr_values = np.zeros(n_times)

        for i in range(n_times):
            rho = density_matrices[i]
            entropy_values[i] = self._calculate_von_neumann_entropy(rho)
            try:
                qfi_values[i] = self._calculate_qfi(rho, self.hamiltonian)
            except (np.linalg.LinAlgError, ValueError):
                qfi_values[i] = 0.0
            diag_sq = np.sum(np.real(np.diag(rho)) ** 2)
            ipr_values[i] = 1.0 / diag_sq if diag_sq > 1e-12 else 1.0

        logger.info("Simulation complete.")

        return {
            "t_axis": t_axis,
            "populations": populations,
            "coherences": coherences,
            "density_matrices": density_matrices,
            "qfi": qfi_values,
            "entropy": entropy_values,
            "ipr": ipr_values,
            "simulator": "MesoHOPS-Parallel",
            "n_traj_used": n_valid,
            "max_hierarchy_used": kwargs.get("max_hierarchy", self.max_hierarchy),
            "scheduler_info": sched_info,
        }

    # Replace the method
    HopsSimulator._simulate_with_mesohops = _simulate_with_mesohops_patched
    logger.info("Memory-aware patching applied to HopsSimulator")
