"""
Quantum Dynamics Simulator using MesoHOPS for Agrivoltaic Systems.

This module implements non-Markovian quantum dynamics simulations using the
MesoHOPS (Mesoscale Hierarchy of Pure States) framework for simulating
energy transfer in photosynthetic systems and quantum-enhanced agrivoltaics.
"""

from models.quantum_analysis import QuantumAnalysisSuite
import logging
import os
from datetime import datetime
from typing import Any, Dict

import numpy as np
import scipy.linalg as la
from scipy.sparse import csc_matrix
import multiprocessing
try:
    from joblib import Parallel, delayed
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

from core.constants import (
        DEFAULT_MAX_HIERARCHY, DEFAULT_N_MATSUBARA, DEFAULT_TEMPERATURE,
        DEFAULT_REORGANIZATION_ENERGY, DEFAULT_DRUDE_CUTOFF,
        DEFAULT_N_TRAJ, DEFAULT_MAX_TIME, MEMORY_FRACTION_LIMIT, 
        BASE_TRAJ_MEMORY_GB, MIN_TRAJ_MEMORY_GB,
    )

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

logger = logging.getLogger(__name__)


def _qds_run_single_traj(
    seed_val: int,
    gw_sysbath: list,
    l_hier: list,
    l_noise1: list,
    param_noise1: list,
    H_shifted: "np.ndarray",
    n_sites: int,
    max_hier: int,
    gamma_dl: float,
    t_max: float,
    dt_save: float,
    psi_0: "np.ndarray",
) -> tuple:
    """
    Module-level picklable worker for QuantumDynamicsSimulator parallel ensemble.

    All state is passed explicitly so joblib can serialize this function
    and send it to worker processes without encountering closure errors.

    Parameters
    ----------
    seed_val : int
        Random seed for the stochastic noise generation.
    gw_sysbath : list
        List of [g, w] bath correlation parameters for all sites.
    l_hier : list
        List of hierarchy operator matrices (L_ops) for each mode.
    l_noise1 : list
        List of noise operator matrices.
    param_noise1 : list
        List of noise parameters corresponding to the noise operators.
    H_shifted : np.ndarray
        Zero-shifted Hamiltonian matrix to improve numerical stability.
    n_sites : int
        Number of sites in the system (e.g., 7 or 8 for FMO).
    max_hier : int
        Maximum depth of the MesoHOPS hierarchy (L_max).
    gamma_dl : float
        Drude-Lorentz cutoff frequency in cm^-1, used to determine the noise buffer length.
    t_max : float
        Total simulation time in femtoseconds.
    dt_save : float
        Time step interval for data saving.
    psi_0 : np.ndarray
        Initial quantum state vector.

    Returns
    -------
    tuple
        (psi_traj_local, t_ax_local) containing the trajectory state history and the time axis.
        Returns (None, None) if the trajectory integration fails.
    """
    try:
        from mesohops.trajectory.hops_trajectory import HopsTrajectory

        def _alpha_noise1(t_axis, g, w):
            return g * np.exp(-w * t_axis)

        system_param = {
            "HAMILTONIAN": H_shifted,
            "GW_SYSBATH": gw_sysbath,
            "L_HIER": l_hier,
            "L_NOISE1": l_noise1,
            "ALPHA_NOISE1": _alpha_noise1,
            "PARAM_NOISE1": param_noise1,
        }
        eom_param = {"EQUATION_OF_MOTION": "NORMALIZED NONLINEAR"}
        noise_param = {
            "SEED": seed_val,
            "MODEL": "FFT_FILTER",
            "TLEN": t_max + max(100.0, 5.0 / gamma_dl),
            "TAU": dt_save,
        }
        hierarchy_param = {"MAXHIER": max_hier}
        integration_param = {
            "INTEGRATOR": "RUNGE_KUTTA",
            "INCHWORM_CAP": 5,
            "STATIC_BASIS": None,
        }
        hops_local = HopsTrajectory(
            system_param=system_param,
            eom_param=eom_param,
            noise_param=noise_param,
            hierarchy_param=hierarchy_param,
            integration_param=integration_param,
        )
        hops_local.initialize(psi_0.copy())
        hops_local.propagate(t_max, dt_save)
        psi_traj_local = np.array(hops_local.storage.data["psi_traj"])[:, :n_sites]
        t_ax_local = np.array(hops_local.storage.data["t_axis"])
        return psi_traj_local, t_ax_local
    except Exception as exc:
        import traceback
        print(f"QDS trajectory seed {seed_val} failed: {exc}\n{traceback.format_exc()}")
        return None, None


try:
    import mesohops.eom.hops_eom as _eom_mod
    from mesohops.trajectory.hops_trajectory import HopsTrajectory
    from mesohops.util.bath_corr_functions import (
        bcf_convert_dl_to_exp,
    )
    # MesoHOPS v1.6 renaming / reorganization support
    try:
        from mesohops.util.bath_corr_functions import bcf_convert_sdl_to_exp as bcf_convert_dl_ud_to_exp
    except ImportError:
        try:
            from mesohops.util.bath_corr_functions import bcf_convert_dl_ud_to_exp
        except ImportError:
            # Fallback for older versions where it might be missing or named differently
            bcf_convert_dl_ud_to_exp = None

    # Check for Matsubara version specifically if needed
    try:
        from mesohops.util.bath_corr_functions import bcf_convert_dl_to_exp_with_Matsubara
    except ImportError:
        bcf_convert_dl_to_exp_with_Matsubara = bcf_convert_dl_to_exp

    MESOHOPS_AVAILABLE = True
except ImportError:
    MESOHOPS_AVAILABLE = False
    _eom_mod = None
    bcf_convert_dl_to_exp = None
    bcf_convert_dl_ud_to_exp = None
    bcf_convert_dl_to_exp_with_Matsubara = None


def _bcf_dl_to_exp_pairs(lam: float, gamma: float, T: float, k: int) -> list:
    """
    Robustly convert Drude-Lorentz bath parameters to exponential pairs (g, w).

    Probes the installed MesoHOPS API signature to handle version differences,
    specifically detecting support for Matsubara corrections (v1.6+).

    Parameters
    ----------
    lam : float
        Reorganization energy lambda in cm^-1.
    gamma : float
        Drude-Lorentz cutoff frequency in cm^-1.
    T : float
        Temperature in Kelvin.
    k : int
        Number of Matsubara terms to include.

    Returns
    -------
    list
        A flat list of [g0, w0, g1, w1, ...] representing the complex exponential
        decomposition parameters of the bath correlation function.
    """
    import inspect
    
    if bcf_convert_dl_to_exp is None:
        raise ImportError("MesoHOPS bath conversion functions not available")
        
    try:
        # Priority 1: Modern MesoHOPS (v1.6+) with explicit Matsubara function
        if bcf_convert_dl_to_exp_with_Matsubara is not None:
            dl_modes = bcf_convert_dl_to_exp_with_Matsubara(lam, gamma, T, k)
        else:
            raise AttributeError("bcf_convert_dl_to_exp_with_Matsubara not available")
    except (ImportError, AttributeError, TypeError):
        # Priority 2: Probe signature of bcf_convert_dl_to_exp
        sig = inspect.signature(bcf_convert_dl_to_exp)
        params = sig.parameters
        
        if 'n_matsubara' in params:
            # Keyword form (~v1.5)
            dl_modes = bcf_convert_dl_to_exp(lam, gamma, T, n_matsubara=k)
        elif len(params) >= 4:
            # Positional form (~v1.4)
            dl_modes = bcf_convert_dl_to_exp(lam, gamma, T, k)
        else:
            # 3-arg form (<=v1.3) — low-temp corrections not available
            dl_modes = bcf_convert_dl_to_exp(lam, gamma, T)
    
    # Validate output format: must be flat list [g0, w0, g1, w1, ...]
    if not isinstance(dl_modes, (list, np.ndarray)) or len(dl_modes) % 2 != 0:
        raise RuntimeError(f"MesoHOPS bath conversion returned unexpected format: {type(dl_modes)}")
        
    return dl_modes


# FIX H-5: apply the EOM_DICT_TYPES patch once at module import time, not on
# every QuantumDynamicsSimulator instantiation. Mutating a global MesoHOPS dict
# inside __init__ runs 100× in a trajectory loop and is a side-effect that can
# interfere with other MesoHOPS users in the same process.
_EOM_PATCHED = False

def _patch_eom_dict_types():
    """Extend MesoHOPS EOM_DICT_TYPES with adHOPS keys (v1.6.0 compatibility)."""
    global _EOM_PATCHED
    if _EOM_PATCHED or _eom_mod is None:
        return
    if "ADAPTIVE_H" not in _eom_mod.EOM_DICT_TYPES:
        _eom_mod.EOM_DICT_TYPES["ADAPTIVE_H"] = [bool]
        _eom_mod.EOM_DICT_TYPES["ADAPTIVE_S"] = [bool]
        _eom_mod.EOM_DICT_TYPES["UPDATE_STEP"] = [float, bool, type(None)]
        _eom_mod.EOM_DICT_TYPES["F_DISCARD"] = [float, int]
        logger.debug("EOM_DICT_TYPES patched for adHOPS support (MesoHOPS v1.6.0)")
    _EOM_PATCHED = True

_patch_eom_dict_types()


class QuantumDynamicsSimulator:
    """
    Non-Markovian quantum dynamics for the FMO complex using MesoHOPS.

    This class implements the adaptive Hierarchy of Pure States (adHOPS) method
    with low-temperature Matsubara corrections (PT-HOPS) via the MesoHOPS
    library (Varvelo et al. 2021, Citty et al. 2024). It provides numerically
    exact, non-Markovian open quantum system dynamics for the FMO complex
    coupled to a structured phonon bath characterized by a Drude-Lorentz
    spectral density with optional underdamped vibronic modes.

    The simulation proceeds by:
    1. Decomposing the bath correlation function into exponential modes
       using Matsubara frequency corrections for accuracy at
       finite temperature.
    2. Running N_traj stochastic HOPS trajectories, each driven by
       independent coloured noise samples.
    3. Ensemble-averaging the density matrix:
       rho(t) = (1/N) sum_k |psi_k(t)><psi_k(t)|
    4. Computing quantum metrics (QFI, coherence, entropy, entanglement)
       from the ensemble-averaged rho(t).

    Parameters
    ----------
    hamiltonian : np.ndarray
        System Hamiltonian in cm^-1 (7x7 for FMO).
    temperature : float
        Bath temperature in K (default: 295).
    lambda_reorg : float
        Drude-Lorentz reorganization energy in cm^-1 (default: 35).
    gamma_dl : float
        Drude-Lorentz cutoff frequency in cm^-1 (default: 50).
    k_matsubara : int
        Number of Matsubara modes (default: 0, sufficient for 295K).
    max_hier : int
        Maximum hierarchy depth (default: 6).
    n_traj : int
        Number of stochastic trajectories for ensemble averaging (default: 50).
    vibronic_modes : list of dict, optional
        Underdamped vibronic modes, each with keys 'omega', 'lambda', 'gamma'.
        Example: [{'omega': 150, 'lambda': 0.05*150, 'gamma': 10}, ...]

    References
    ----------
    Varvelo et al., "MesoHOPS: Size-invariant scaling HOPS", PCCP (2021).
    Citty et al., "adHOPS: adaptive HOPS", J. Chem. Phys. (2024).
    Adolphs & Renger, Biophys. J. 91, 2778–2797 (2006).
    """

    def __init__(
        self,
        hamiltonian,
        temperature=DEFAULT_TEMPERATURE,
        lambda_reorg=DEFAULT_REORGANIZATION_ENERGY,
        gamma_dl=DEFAULT_DRUDE_CUTOFF,
        k_matsubara=DEFAULT_N_MATSUBARA,
        max_hier=DEFAULT_MAX_HIERARCHY,
        n_traj=DEFAULT_N_TRAJ,   # Aligned with parameters.yaml n_traj=100
        vibronic_modes=None,
    ):

        if not MESOHOPS_AVAILABLE:
            raise ImportError(
                "MesoHOPS is required but not available. Please install it: pip install mesohops"
            )

        self.H_raw = np.array(hamiltonian, dtype=complex)
        if self.H_raw.ndim != 2 or self.H_raw.shape[0] != self.H_raw.shape[1]:
            raise ValueError(f"Hamiltonian must be square, got shape {self.H_raw.shape}")
        self.n_sites = self.H_raw.shape[0]
        if self.n_sites == 0:
            raise ValueError("Hamiltonian must have at least 1 site")
        self.temperature = temperature
        self.analyzer = QuantumAnalysisSuite()
        self.lambda_reorg = lambda_reorg
        self.gamma_dl = gamma_dl
        self.k_matsubara = k_matsubara
        self.max_hier = max_hier
        self.n_traj = n_traj
        # FIX M-3: 'vibronic_modes or []' raises ValueError for empty np.ndarray.
        # Use explicit None check instead.
        self.vibronic_modes = vibronic_modes if vibronic_modes is not None else []

        # Zero-shift Hamiltonian to improve numerical stability
        self.E_shift = np.mean(np.diag(self.H_raw).real)
        self.H = self.H_raw - self.E_shift * np.eye(self.n_sites, dtype=complex)

        # ── Bath correlation function decomposition ──────────────────
        # Drude-Lorentz spectral density (high-temperature limit).
        # k_matsubara=0: High-temperature approximation (standard for 295K)
        # FIX H-6: Use version-agnostic helper to build dl_modes
        dl_modes = _bcf_dl_to_exp_pairs(
            lambda_reorg, gamma_dl, temperature, k_matsubara
        )
        # Validate output format: must be flat [g0, w0, g1, w1, ...]
        if not isinstance(dl_modes, (list, np.ndarray)) or len(dl_modes) % 2 != 0:
            raise RuntimeError(
                f"bcf_convert_dl_to_exp_with_Matsubara returned unexpected format: "
                f"type={type(dl_modes)}, len={len(dl_modes) if hasattr(dl_modes, '__len__') else 'N/A'}"
            )
        self.n_modes_dl = len(dl_modes) // 2

        # Optional: underdamped vibronic modes via bcf_convert_dl_ud_to_exp
        # Returns flat [g0, w0, g1, w1, ...] for the two complex conjugate poles
        vib_mode_list = []
        for vm in self.vibronic_modes:
            try:
                if bcf_convert_dl_ud_to_exp is not None:
                    ud_modes = bcf_convert_dl_ud_to_exp(
                        vm["lambda"], vm["gamma"], vm["omega"], temperature
                    )
                    # Support both [g, w] (legacy) and [g1, w1, g2, w2] (modern)
                    for k in range(0, len(ud_modes), 2):
                        vib_mode_list.append((ud_modes[k], ud_modes[k + 1]))
                else:
                    # Basic high-temperature fallback: single pole approximation
                    # g = lambda * omega * (coth(beta*omega/2) + 1), w = gamma + i*omega
                    # Here we just use a simplified version:
                    vib_mode_list.append((vm["lambda"], vm["gamma"] + 1j * vm["omega"]))
            except KeyError as e:
                raise ValueError(
                    f"Vibronic mode dict missing key {e}. "
                    "Required keys: 'lambda', 'gamma', 'omega'."
                ) from e
        self.n_modes_vib = len(vib_mode_list)

        # Total modes per site
        self.n_modes_per_site = self.n_modes_dl + self.n_modes_vib

        # ── Build system-bath coupling lists ─────────────────────────
        # Each site couples to its own independent bath
        self._L_ops = []
        for i in range(self.n_sites):
            L = np.zeros((self.n_sites, self.n_sites), dtype=complex)
            L[i, i] = 1.0
            # Use dense matrices to avoid indexing issues in some MesoHOPS versions
            self._L_ops.append(L)

        self.gw_sysbath = []
        self.l_hier = []
        self.l_noise1 = []
        self.param_noise1 = []

        for site_idx in range(self.n_sites):
            # Drude-Lorentz + Matsubara modes
            for k in range(0, len(dl_modes), 2):
                g, w = dl_modes[k], dl_modes[k + 1]
                self.gw_sysbath.append([g, w])
                self.l_hier.append(self._L_ops[site_idx])
                self.l_noise1.append(self._L_ops[site_idx])
                self.param_noise1.append([g, w])

            # Underdamped vibronic modes
            for g_vib, w_vib in vib_mode_list:
                self.gw_sysbath.append([g_vib, w_vib])
                self.l_hier.append(self._L_ops[site_idx])
                self.l_noise1.append(self._L_ops[site_idx])
                self.param_noise1.append([g_vib, w_vib])

        logger.info(
            f"Bath decomposition: {self.n_modes_dl} DL modes "
            f"+ {self.n_modes_vib} vibronic modes per site "
            f"= {self.n_modes_per_site * self.n_sites} total hierarchy modes"
        )

    @staticmethod
    def _alpha_noise1(t_axis, g, w):
        """Single-mode bath correlation function: alpha(t) = g * exp(-w*t)."""
        return g * np.exp(-w * t_axis)

    def _build_hops_trajectory(self, seed, t_max, dt_save=2.0):
        """
        Build and return an initialized HopsTrajectory object.

        Parameters
        ----------
        seed : int
            Random seed for the stochastic noise.
        t_max : float
            Total simulation time in fs.
        dt_save : float
            Time interval between saved points in fs.

        Returns
        -------
        hops : HopsTrajectory
            Initialized HOPS trajectory object.
        """
        system_param = {
            "HAMILTONIAN": self.H,
            "GW_SYSBATH": self.gw_sysbath,
            "L_HIER": self.l_hier,
            "L_NOISE1": self.l_noise1,
            "ALPHA_NOISE1": self._alpha_noise1,
            "PARAM_NOISE1": self.param_noise1,
        }

        eom_param = {"EQUATION_OF_MOTION": "NORMALIZED NONLINEAR"}
        noise_param = {
            "SEED": seed,
            "MODEL": "FFT_FILTER",
            "TLEN": t_max + max(100.0, 5.0 / self.gamma_dl),  # buffer ≥ bath correlation time
            "TAU": dt_save,  # noise sampling interval = integration timestep
        }
        hierarchy_param = {"MAXHIER": self.max_hier}
        integration_param = {
            "INTEGRATOR": "RUNGE_KUTTA",
            "INCHWORM_CAP": 5,
            "STATIC_BASIS": None,
        }

        hops = HopsTrajectory(
            system_param=system_param,
            eom_param=eom_param,
            noise_param=noise_param,
            hierarchy_param=hierarchy_param,
            integration_param=integration_param,
        )
        return hops

    def _get_memory_estimate(self) -> float:
        """
        Dynamically estimate memory per trajectory based on hierarchy depth (L)
        and Matsubara terms (K). 
        
        Reference: L=8, K=2 -> BASE_TRAJ_MEMORY_GB.

        Returns
        -------
        float
            Estimated memory requirement in GB.
        """
        l_ref = 8.0
        k_ref = 2.0
        
        # Quadratic scaling with L
        l_factor = (self.max_hier / l_ref) ** 2
        # Linear scaling with K (minimum factor 0.5 to avoid under-estimation)
        k_factor = max(0.5, (self.k_matsubara / k_ref))
        
        estimate = BASE_TRAJ_MEMORY_GB * l_factor * k_factor
        
        # Apply platform-specific safety buffer if RAM is low
        if HAS_PSUTIL:
            total_ram_gb = psutil.virtual_memory().total / (1024**3)
            if total_ram_gb < 16.0:
                estimate *= 1.5  # 50% more conservative on low-RAM systems
                
        return max(MIN_TRAJ_MEMORY_GB, estimate)

    def simulate_dynamics(self, initial_state=None, time_points=None, dt_save=2.0, seeds=None, **kwargs):
        """
        Run ensemble-averaged non-Markovian dynamics via MesoHOPS.

        Runs n_traj independent HOPS trajectories and constructs the
        ensemble-averaged density matrix at each time point:
            rho(t) = (1/N) sum_k |psi_k(t)><psi_k(t)|

        Parameters
        ----------
        initial_state : np.ndarray, optional
            Initial pure state vector (default: excitation on site 1).
        time_points : np.ndarray, optional
            Desired output time points in fs (used to set t_max).
            Note: actual time grid is determined by dt_save.
        dt_save : float
            Noise discretization / save interval in fs (default: 0.5).
        seeds : list of int, optional
            Random seeds for each trajectory (default: range(n_traj)).

        Returns
        -------
        results : dict
            Dictionary containing:
            - 't_axis': Time points in fs.
            - 'density_matrices': list of np.ndarray
            - 'populations': np.ndarray (n_times, n_sites)
            - 'coherences': np.ndarray (n_times,)
            - 'qfi': np.ndarray (n_times,)
            - 'entropy': np.ndarray (n_times,)
            - 'purity': np.ndarray (n_times,)
            - 'linear_entropy': np.ndarray (n_times,)
            - 'bipartite_ent': np.ndarray (n_times,)
            - 'multipartite_ent': np.ndarray (n_times,)
            - 'pairwise_concurrence': np.ndarray (n_times,)
            - 'discord': np.ndarray (n_times,)
            - 'fidelity': np.ndarray (n_times,)
            - 'mandel_q': np.ndarray (n_times,)
        """
        import warnings

        warnings.filterwarnings("ignore", category=RuntimeWarning)

        n_sites = self.n_sites
        n_traj = self.n_traj

        # Determine simulation time
        if time_points is not None:
            t_max = float(np.max(time_points))
        else:
            t_max = DEFAULT_MAX_TIME  # default: 1000 fs per parameters.yaml

        # Initial state
        if initial_state is None:
            psi_0 = np.zeros(n_sites, dtype=complex)
            psi_0[0] = 1.0  # Excitation on site 1 (BChl 1)
        else:
            psi_0 = np.array(initial_state, dtype=complex).flatten()
            assert psi_0.shape[0] == n_sites

        # Seeds
        if seeds is None:
            seeds = list(range(n_traj))

        # ── Run ensemble of trajectories (Parallelized) ─────────────────────
        # Calculate memory-aware n_jobs
        cpu_count = multiprocessing.cpu_count()
        if HAS_PSUTIL:
            mem_avail_gb = psutil.virtual_memory().available / (1024**3)
            mem_limit_gb = mem_avail_gb * MEMORY_FRACTION_LIMIT
            # Dynamic estimate based on L and K
            traj_mem_gb = self._get_memory_estimate()
            n_mem_jobs = max(1, int(mem_limit_gb / traj_mem_gb))
            n_jobs = min(n_mem_jobs, cpu_count)
            logger.info(f"Memory-aware n_jobs: {n_jobs} (Avail: {mem_avail_gb:.1f}GB, Limit: {mem_limit_gb:.1f}GB, Est/Traj: {traj_mem_gb:.1f}GB)")
        else:
            n_jobs = max(1, int(cpu_count * 0.5))
            logger.warning(f"psutil not available; using conservative n_jobs: {n_jobs}")

        logger.info(
            f"  Running {n_traj} HOPS trajectories in parallel (n_jobs={n_jobs}, "
            f"{t_max:.0f} fs, dt={dt_save} fs, MAXHIER={self.max_hier})..."
        )

        # Build picklable argument dict for module-level worker
        worker_kwargs = dict(
            gw_sysbath=self.gw_sysbath,
            l_hier=self.l_hier,
            l_noise1=self.l_noise1,
            param_noise1=self.param_noise1,
            H_shifted=self.H,
            n_sites=n_sites,
            max_hier=self.max_hier,
            gamma_dl=self.gamma_dl,
            t_max=t_max,
            dt_save=dt_save,
            psi_0=psi_0,
        )

        all_psi_trajs = []
        t_axis = None

        if HAS_JOBLIB and n_jobs > 1:
            # Parallel execution using the module-level picklable worker
            results_parallel = Parallel(n_jobs=n_jobs)(
                delayed(_qds_run_single_traj)(s, **worker_kwargs) for s in seeds
            )
            for psi_traj, t_ax_k in results_parallel:
                if psi_traj is not None and not np.any(np.isnan(psi_traj)):
                    if t_axis is None:
                        t_axis = t_ax_k
                    elif len(t_ax_k) < len(t_axis):
                        t_axis = t_ax_k
                    all_psi_trajs.append(psi_traj)
        else:
            # Sequential fallback
            for seed in seeds:
                psi_traj, t_ax_k = _qds_run_single_traj(seed, **worker_kwargs)
                if psi_traj is not None and not np.any(np.isnan(psi_traj)):
                    if t_axis is None:
                        t_axis = t_ax_k
                    elif len(t_ax_k) < len(t_axis):
                        t_axis = t_ax_k
                    all_psi_trajs.append(psi_traj)
                    
        # Consistent truncation
        if t_axis is not None:
            n_t = len(t_axis)
            all_psi_trajs = [p[:n_t] for p in all_psi_trajs]

        n_valid = len(all_psi_trajs)
        if n_valid == 0:
            raise RuntimeError(
                "All HOPS trajectories failed. Try increasing MAXHIER or decreasing dt_save."
            )

        logger.info(f"  Ensemble: {n_valid}/{n_traj} valid trajectories")

        # ── Ensemble-average density matrix ──────────────────────────
        n_times = len(t_axis)
        density_matrices = []
        populations = np.zeros((n_times, n_sites))
        coherences = np.zeros(n_times)
        qfi_values = np.zeros(n_times)
        entropy_values = np.zeros(n_times)
        ipr_values = np.zeros(n_times)
        bipartite_ent_values = np.zeros(n_times)
        multipartite_ent_values = np.zeros(n_times)
        pairwise_concurrence_values = np.zeros(n_times)
        discord_values = np.zeros(n_times)
        fidelity_values = np.zeros(n_times)
        mandel_q_values = np.zeros(n_times)

        for i in range(n_times):
            # Construct density matrix: rho = (1/N) sum_k |psi_k><psi_k|
            rho = np.zeros((n_sites, n_sites), dtype=complex)
            for psi_traj in all_psi_trajs:
                psi = psi_traj[i]
                rho += np.outer(psi, np.conj(psi))
            rho /= n_valid

            # Normalize trace to 1 (should be close already)
            tr = np.trace(rho).real
            if tr > 1e-10:
                rho /= tr

            density_matrices.append(rho)
            populations[i, :] = np.real(np.diag(rho))
            coherences[i] = self.analyzer.calculate_coherence_measure(rho)

            # IPR = 1 / Σ_n ρ_nn²  (manuscript Fig. 1c)
            diag_sq = np.sum(np.real(np.diag(rho)) ** 2)
            ipr_values[i] = 1.0 / diag_sq if diag_sq > 1e-12 else 1.0

            try:
                qfi_values[i] = self.analyzer.calculate_qfi(rho, self.H_raw)
            except (np.linalg.LinAlgError, ValueError, TypeError) as e:
                logger.debug(f"QFI calculation failed at t={i}: {e}")
                qfi_values[i] = 0.0

            try:
                entropy_values[i] = self.analyzer.calculate_entropy_von_neumann(rho)
            except (np.linalg.LinAlgError, ValueError, TypeError) as e:
                logger.debug(f"Entropy calculation failed at t={i}: {e}")
                entropy_values[i] = 0.0

            try:
                bipartite_ent_values[i] = self.analyzer.calculate_bipartite_entanglement(rho)
            except (np.linalg.LinAlgError, ValueError, TypeError) as e:
                logger.debug(f"Bipartite entanglement calc failed at t={i}: {e}")
                bipartite_ent_values[i] = 0.0

            try:
                multipartite_ent_values[i] = self.analyzer.calculate_multipartite_entanglement(rho)
            except (np.linalg.LinAlgError, ValueError, TypeError) as e:
                logger.debug(f"Multipartite entanglement calc failed at t={i}: {e}")
                multipartite_ent_values[i] = 0.0

            try:
                pairwise_concurrence_values[i] = self.analyzer.calculate_pairwise_concurrence(rho)
            except (np.linalg.LinAlgError, ValueError, TypeError) as e:
                logger.debug(f"Pairwise concurrence calc failed at t={i}: {e}")
                pairwise_concurrence_values[i] = 0.0

            try:
                discord_values[i] = self.analyzer.calculate_quantum_discord(rho)
            except (np.linalg.LinAlgError, ValueError, TypeError) as e:
                logger.debug(f"Quantum discord calc failed at t={i}: {e}")
                discord_values[i] = 0.0

            try:
                # Fidelity relative to initial state
                rho_0 = density_matrices[0]
                fidelity_values[i] = self.analyzer.calculate_fidelity(rho, rho_0)
            except (np.linalg.LinAlgError, ValueError, TypeError) as e:
                logger.debug(f"Fidelity calc failed at t={i}: {e}")
                fidelity_values[i] = 1.0 if i == 0 else 0.0

            try:
                # Mandel Q requires vibrational occupations - using population weighted average as dummy
                mandel_q_values[i] = self.analyzer.calculate_mandel_q_parameter(populations[i])
            except (ValueError, TypeError) as e:
                logger.debug(f"Mandel Q calc failed at t={i}: {e}")
                mandel_q_values[i] = 0.0

        return {
            "t_axis": t_axis,
            "density_matrices": density_matrices,
            "populations": populations,
            "coherences": coherences,
            "qfi": qfi_values,
            "entropy": entropy_values,
            "ipr": ipr_values,
            "bipartite_ent": bipartite_ent_values,
            "multipartite_ent": multipartite_ent_values,
            "pairwise_concurrence": pairwise_concurrence_values,
            "discord": discord_values,
            "fidelity": fidelity_values,
            "mandel_q": mandel_q_values,
            "simulator": "QuantumDynamicsSimulator (MesoHOPS)",
        }


def spectral_density_drude_lorentz(omega, lambda_reorg, gamma):
    """
    Drude-Lorentz spectral density.

    J(omega) = (2 * lambda_reorg * gamma * omega) / (omega^2 + gamma^2)

    Parameters
    ----------
    omega : array-like
        Angular frequency in cm^-1
    lambda_reorg : float
        Reorganization energy in cm^-1
    gamma : float
        Cutoff frequency in cm^-1

    Returns
    -------
    J : array-like
        Spectral density values
    """
    omega = np.asarray(omega)
    J = (2 * lambda_reorg * gamma * omega) / (omega**2 + gamma**2)
    # Avoid division by zero at omega=0
    J[omega == 0] = 0
    return J


def spectral_density_vibronic(omega, omega_mode, lambda_mode, gamma_mode):
    """
    Underdamped vibronic mode spectral density (Shifted Drude-Lorentz).

    J(omega) = (2 * lambda_mode * omega_mode * gamma_mode * omega) /
               ((omega^2 - omega_mode^2)^2 + omega^2 * gamma_mode^2)

    Parameters
    ----------
    omega : array-like
        Angular frequency in cm^-1
    omega_mode : float
        Vibronic mode frequency in cm^-1
    lambda_mode : float
        Reorganization energy of the mode in cm^-1
    gamma_mode : float
        Damping rate in cm^-1

    Returns
    -------
    J : array-like
        Spectral density values
    """
    omega = np.asarray(omega)
    numerator = 2 * lambda_mode * omega_mode * gamma_mode * omega
    denominator = (omega**2 - omega_mode**2) ** 2 + omega**2 * gamma_mode**2
    J = numerator / denominator
    # Avoid division by zero at omega=0
    J[omega == 0] = 0
    return J


def spectral_density_total(omega, lambda_reorg, gamma, vibronic_modes=None):
    """
    Total spectral density combining Drude-Lorentz and vibronic modes.

    Parameters
    ----------
    omega : array-like
        Angular frequency in cm^-1
    lambda_reorg : float
        Reorganization energy for Drude-Lorentz component in cm^-1
    gamma : float
        Cutoff frequency for Drude-Lorentz component in cm^-1
    vibronic_modes : list of dict, optional
        List of vibronic modes, each with keys 'omega', 'lambda', 'gamma'

    Returns
    -------
    J : array-like
        Total spectral density values
    """
    omega = np.asarray(omega)

    # Drude-Lorentz component
    J_total = spectral_density_drude_lorentz(omega, lambda_reorg, gamma)

    # Add vibronic modes if provided
    if vibronic_modes:
        for mode in vibronic_modes:
            J_vib = spectral_density_vibronic(omega, mode["omega"], mode["lambda"], mode["gamma"])
            J_total += J_vib

    return J_total


def save_quantum_dynamics_results(
    results: Dict[str, Any],
    filename_prefix: str = "quantum_dynamics",
    output_dir: str = "../simulation_data/",
) -> str:
    """
    Save quantum dynamics simulation results to CSV.

    Parameters
    ----------
    results : dict
        Results from simulate_dynamics method
    filename_prefix : str
        Prefix for output filename
    output_dir : str
        Directory to save CSV file

    Returns
    -------
    str
        Path to saved CSV file
    """
    import pandas as pd

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Extract data from results
    t_axis = results.get("t_axis", [])
    populations = results.get("populations", np.array([]))
    coherences = results.get("coherences", np.array([]))
    qfi = results.get("qfi", np.array([]))
    entropy = results.get("entropy", np.array([]))
    bipartite_ent = results.get("bipartite_ent", np.array([]))
    multipartite_ent = results.get("multipartite_ent", np.array([]))
    pairwise_concurrence = results.get("pairwise_concurrence", np.array([]))
    discord = results.get("discord", np.array([]))
    fidelity = results.get("fidelity", np.array([]))
    mandel_q = results.get("mandel_q", np.array([]))

    # Create DataFrame
    data = {"time_fs": t_axis}

    # Add populations for each site
    if len(populations) > 0 and len(populations[0]) > 0:
        n_sites = len(populations[0])
        for i in range(n_sites):
            data[f"population_site_{i + 1}"] = [p[i] for p in populations]

    # Add quantum metrics
    if len(coherences) > 0:
        data["coherences"] = coherences
    if len(qfi) > 0:
        data["qfi"] = qfi
    if len(entropy) > 0:
        data["entropy"] = entropy
    if len(bipartite_ent) > 0:
        data["bipartite_ent"] = bipartite_ent
    if len(multipartite_ent) > 0:
        data["multipartite_ent"] = multipartite_ent
    if len(pairwise_concurrence) > 0:
        data["pairwise_concurrence"] = pairwise_concurrence
    if len(discord) > 0:
        data["discord"] = discord
    if len(fidelity) > 0:
        data["fidelity"] = fidelity
    if len(mandel_q) > 0:
        data["mandel_q"] = mandel_q

    df = pd.DataFrame(data)
    filename = f"{filename_prefix}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    df.to_csv(filepath, index=False)

    logger.info(f"Quantum dynamics results saved to {filepath}")
    return filepath


def plot_quantum_dynamics_results(
    results: Dict[str, Any],
    filename_prefix: str = "quantum_dynamics",
    figures_dir: str = "../Graphics/",
) -> str:
    """
    Plot quantum dynamics simulation results.

    Parameters
    ----------
    results : dict
        Results from simulate_dynamics method
    filename_prefix : str
        Prefix for output filename
    figures_dir : str
        Directory to save figures

    Returns
    -------
    str
        Path to saved figure
    """
    import matplotlib.pyplot as plt

    os.makedirs(figures_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    t_axis = results.get("t_axis", [])
    populations = results.get("populations", np.array([]))
    coherences = results.get("coherences", np.array([]))
    qfi = results.get("qfi", np.array([]))
    entropy = results.get("entropy", np.array([]))

    # Create figure with subplots
    n_metrics = sum(x.size > 0 for x in [coherences, qfi, entropy])
    n_plots = max(2, n_metrics + 1)  # At least populations and one metric

    n_cols = 2
    n_rows = (n_plots + 1) // 2

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
    fig.suptitle("Quantum Dynamics Simulation Results", fontsize=16, fontweight="bold")

    # Handle single row case
    if n_rows == 1:
        axes = [axes] if n_cols == 1 else axes
    elif n_rows == 1 and n_cols > 1:
        axes = axes
    else:
        axes = axes.flatten() if n_plots > 1 else [axes]

    # Plot populations
    if len(populations) > 0 and len(populations[0]) > 0:
        ax_idx = 0
        ax = axes[ax_idx]
        n_sites = len(populations[0])
        for i in range(min(n_sites, 7)):  # Limit to first 7 sites for readability
            ax.plot(t_axis, [p[i] for p in populations], label=f"Site {i + 1}", linewidth=1.5)
        ax.set_xlabel("Time (fs)")
        ax.set_ylabel("Population")
        ax.set_title("Site Populations vs Time")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    else:
        ax_idx = -1

    # Plot quantum metrics
    metrics_to_plot = [
        (coherences, "Coherence", "coherences"),
        (qfi, "QFI", "qfi"),
        (entropy, "Entropy", "entropy"),
    ]

    for metric_values, metric_label, _metric_key in metrics_to_plot:
        if len(metric_values) > 0:
            ax_idx += 1
            if ax_idx < len(axes):
                ax = axes[ax_idx]
                ax.plot(t_axis, metric_values, linewidth=2)
                ax.set_xlabel("Time (fs)")
                ax.set_ylabel(metric_label)
                ax.set_title(f"{metric_label} Evolution")
                ax.grid(True, alpha=0.3)

    # Remove unused subplots
    for idx in range(ax_idx + 1, len(axes)):
        fig.delaxes(axes[idx])

    plt.tight_layout()

    filename = f"{filename_prefix}_{timestamp}.pdf"
    filepath = os.path.join(figures_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches="tight")

    png_filename = f"{filename_prefix}_{timestamp}.png"
    png_filepath = os.path.join(figures_dir, png_filename)
    plt.savefig(png_filepath, dpi=150, bbox_inches="tight")

    plt.close()

    logger.info(f"Quantum dynamics plots saved to {filepath}")
    return filepath