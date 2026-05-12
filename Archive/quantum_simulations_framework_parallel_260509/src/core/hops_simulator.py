"""
HopsSimulator: Unified quantum dynamics simulator with MesoHOPS integration.

This module provides the HopsSimulator class which uses MesoHOPS as the default
simulation engine with automatic fallback to QuantumDynamicsSimulator.
"""

import sys
from typing import Any, Dict, Optional

import numpy as np
import scipy.sparse as sp
from numpy.typing import NDArray
import multiprocessing
try:
    from joblib import Parallel, delayed
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

try:
    from tqdm.auto import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# Import MesoHOPS modules
try:
    from mesohops.basis.hops_basis import HopsBasis
    from mesohops.basis.hops_system import HopsSystem
    from mesohops.trajectory.hops_trajectory import HopsTrajectory
    try:
        from mesohops.eom.hops_eom import HopsEOM
    except ImportError:
        HopsEOM = None

    MESOHOPS_AVAILABLE = True
except ImportError:
    MESOHOPS_AVAILABLE = False
    HopsSystem = None
    HopsBasis = None
    HopsTrajectory = None
    HopsEOM = None

# Import our custom PT-HOPS and SBD Extensions (absolute import)
try:
    from src.extensions.mesohops_adapters import PT_HopsNoise, SBD_HopsTrajectory
except ImportError:
    try:
        from ..extensions.mesohops_adapters import PT_HopsNoise, SBD_HopsTrajectory
    except ImportError:
        SBD_HopsTrajectory = None
        PT_HopsNoise = None

# Import fallback simulators from models package (absolute import)
try:
    from models import QuantumDynamicsSimulator, SimpleQuantumDynamicsSimulator
except ImportError:
    try:
        from ..models import QuantumDynamicsSimulator, SimpleQuantumDynamicsSimulator
    except ImportError:
        QuantumDynamicsSimulator = None
        SimpleQuantumDynamicsSimulator = None

try:
    from src.core.constants import (
        DEFAULT_DRUDE_CUTOFF,
        DEFAULT_HUANG_RHYS_FACTORS,
        DEFAULT_MAX_HIERARCHY,
        DEFAULT_N_MATSUBARA,
        DEFAULT_REORGANIZATION_ENERGY,
        DEFAULT_TEMPERATURE,
        DEFAULT_VIBRONIC_DAMPING,
        DEFAULT_VIBRONIC_FREQUENCIES,
        DEFAULT_SBD_BUNDLES,
        DEFAULT_N_TRAJ,
        FFT_NOISE_BUFFER_FS,
        PULSE_CENTRAL_FREQ,
        PULSE_FWHM,
        PULSE_RELATIVE_DELAY,
        PULSE_TYPE,
        PULSE_AMPLITUDE,
        MEMORY_FRACTION_LIMIT,
        MESOHOPS_SEED,
        MESOHOPS_EARLY_STEPS,
        MESOHOPS_INCHWORM_CAP,
        DEFAULT_MAX_TIME,
        DEFAULT_TIME_STEP,
        BASE_TRAJ_MEMORY_GB,
        MIN_TRAJ_MEMORY_GB,
    )
except ImportError:
    from .constants import (
        DEFAULT_DRUDE_CUTOFF,
        DEFAULT_HUANG_RHYS_FACTORS,
        DEFAULT_MAX_HIERARCHY,
        DEFAULT_N_MATSUBARA,
        DEFAULT_REORGANIZATION_ENERGY,
        DEFAULT_TEMPERATURE,
        DEFAULT_VIBRONIC_DAMPING,
        DEFAULT_VIBRONIC_FREQUENCIES,
        DEFAULT_SBD_BUNDLES,
        DEFAULT_N_TRAJ,
        FFT_NOISE_BUFFER_FS,
        PULSE_CENTRAL_FREQ,
        PULSE_FWHM,
        PULSE_RELATIVE_DELAY,
        PULSE_TYPE,
        PULSE_AMPLITUDE,
        MEMORY_FRACTION_LIMIT,
        MESOHOPS_SEED,
        MESOHOPS_EARLY_STEPS,
        MESOHOPS_INCHWORM_CAP,
        DEFAULT_MAX_TIME,
        DEFAULT_TIME_STEP,
        BASE_TRAJ_MEMORY_GB,
        MIN_TRAJ_MEMORY_GB,
    )

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    from utils.logging_config import get_logger
except ImportError:
    from ..utils.logging_config import get_logger


def get_mesohops_version() -> Optional[str]:
    """Return the installed MesoHOPS version or None if not available."""
    try:
        import mesohops

        return getattr(mesohops, "__version__", None)
    except (ImportError, ModuleNotFoundError):
        return None


logger = get_logger(__name__)


def _run_single_traj_worker(
    seed: int,
    TrajectoryClass: Any,
    traj_kwargs: Dict[str, Any],
    use_pt_hops: bool,
    pt_hops_noise_class: Any,
    system_param: Dict[str, Any],
    initial_state: NDArray[np.complex128],
    t_max: float,
    dt_save: float,
    time_points: NDArray[np.float64],
) -> Optional[Dict[str, Any]]:
    """
    Standalone worker function for parallel trajectory execution.

    This function must be picklable to run in a separate process via joblib.
    It initializes the trajectory, prepares the PT-HOPS noise (if applicable),
    and propagates the trajectory up to t_max.

    Parameters
    ----------
    seed : int
        Random seed for the specific trajectory's noise realization.
    TrajectoryClass : type
        The class object used to instantiate the trajectory (e.g., SBD_HopsTrajectory).
    traj_kwargs : dict[str, Any]
        Arguments dictionary to pass to the TrajectoryClass constructor.
    use_pt_hops : bool
        Flag indicating if PT-HOPS (Process Tensor HOPS) noise generation should be used.
    pt_hops_noise_class : type
        The class object for PT-HOPS noise generation (e.g., PT_HopsNoise).
    system_param : dict[str, Any]
        System parameters including noise basis details required for PT-HOPS.
    initial_state : NDArray[np.complex128]
        Initial wave function/state vector.
    t_max : float
        Maximum simulation time.
    dt_save : float
        Time interval for saving state data during propagation.
    time_points : NDArray[np.float64]
        Array of explicit time points at which noise is evaluated.

    Returns
    -------
    dict[str, Any] or None
        Dictionary containing trajectory state ('psi_traj'), time axis ('t_axis'), and
        site populations ('pop_site'). Returns None if execution fails.
    """
    try:
        # Deep copy of params to avoid process collisions
        import copy

        local_traj_kwargs = copy.deepcopy(traj_kwargs)
        local_traj_kwargs["noise_param"]["SEED"] = seed

        trajectory = TrajectoryClass(**local_traj_kwargs)

        if use_pt_hops and pt_hops_noise_class is not None:
            pt_noise = pt_hops_noise_class(
                local_traj_kwargs["noise_param"], system_param["PARAM_NOISE1"]
            )
            if hasattr(trajectory, "noise"):
                trajectory.noise = pt_noise
            pt_noise._prepare_noise(system_param["L_NOISE1"], time_points=time_points)

        trajectory.initialize(initial_state.copy())
        trajectory.propagate(t_max, dt_save)

        return {
            "psi_traj": np.array(trajectory.storage.data["psi_traj"]),
            "t_axis": np.array(trajectory.storage.data["t_axis"]),
            "pop_site": np.array(trajectory.storage.data.get("pop_site", [])),
        }
    except Exception as e:
        import traceback

        # We use print here as logger might not be fully configured in worker processes
        print(f"Parallel trajectory {seed} failed: {e}\n{traceback.format_exc()}")
        return None


class HopsSimulator:
    """
    Unified simulator that uses MesoHOPS by default with fallback.

    This class provides a consistent interface for quantum dynamics simulations,
    automatically using MesoHOPS when available and falling back to the custom
    QuantumDynamicsSimulator when needed.

    Parameters
    ----------
    hamiltonian : NDArray[np.float64]
        System Hamiltonian matrix in cm⁻¹. Must be square and Hermitian.
    temperature : float, optional
        Temperature in Kelvin (default: 295.0)
    use_mesohops : bool, optional
        Whether to use MesoHOPS if available (default: True)
    max_hierarchy : int, optional
        Maximum hierarchy level for MesoHOPS (default: 10)
    **kwargs : dict
        Additional arguments passed to underlying simulator

    Notes
    -----
    Energy shift: the Hamiltonian is internally zero-shifted by subtracting the
    mean diagonal energy before passing it to MesoHOPS:

        H_shifted = H - mean(diag(H)) · I

    For the FMO complex this removes ~12 400 cm⁻¹ from all site energies,
    preventing rapid oscillations exp(-iHt/ℏ) that cause numerical overflow in
    the integrator. All physical observables (populations, coherences, QFI) are
    invariant to this uniform energy shift.

    Attributes
    ----------
    hamiltonian : NDArray[np.float64]
        The system Hamiltonian (unshifted, as provided by the caller)
    temperature : float
        Simulation temperature
    use_mesohops : bool
        Whether MesoHOPS is being used
    system : Optional[HopsSystem]
        MesoHOPS system object (if initialized)
    fallback_sim : Optional[QuantumDynamicsSimulator]
        Fallback simulator (if initialized)

    Examples
    --------
    >>> import numpy as np
    >>> from src.core.hops_simulator import HopsSimulator
    >>> hamiltonian = np.array([[1, 0.5], [0.5, 1]])
    >>> simulator = HopsSimulator(hamiltonian, temperature=DEFAULT_TEMPERATURE)
    >>> time_points = np.linspace(0, 100, 100)
    >>> results = simulator.simulate_dynamics(time_points)
    """

    def __init__(
        self,
        hamiltonian: NDArray[np.float64],
        temperature: float = DEFAULT_TEMPERATURE,
        use_mesohops: bool = True,
        max_hierarchy: int = DEFAULT_MAX_HIERARCHY,
        k_matsubara: int = DEFAULT_N_MATSUBARA,
        **kwargs: Any,
    ):
        """Initialize the simulator."""
        self.hamiltonian = hamiltonian
        self.temperature = temperature
        self.max_hierarchy = max_hierarchy
        self.k_matsubara = k_matsubara
        self.use_mesohops = MESOHOPS_AVAILABLE and use_mesohops
        self.use_pt_hops = kwargs.pop("use_pt_hops", False)
        # SI mandate: all production runs use SBD (see SI Section S1, Table S1).
        # Override with use_sbd=False only for exact-reference unit tests.
        self.use_sbd = kwargs.pop("use_sbd", True)
        
        # Enforce SBD from L>=2 whenever the number of sites, even for tests
        if self.max_hierarchy >= 2:
            self.use_sbd = True
            
        self.n_traj = kwargs.pop("n_traj", kwargs.get("n_trajectories", DEFAULT_N_TRAJ))
        self.sbd_bundles_per_site = kwargs.get("sbd_bundles_per_site", 2)
        self.system = None
        self.fallback_sim: Optional[Any] = None

        # D-4 FIX: validate Hermiticity before any simulation work.
        # A non-Hermitian Hamiltonian produces complex eigenvalues and unphysical
        # dynamics that are hard to diagnose downstream. Catch it here.
        H = np.asarray(hamiltonian)
        if H.ndim == 2 and H.shape[0] == H.shape[1]:
            max_asymmetry = np.max(np.abs(H - H.conj().T))
            if max_asymmetry > 1e-8:
                raise ValueError(
                    f"Hamiltonian is not Hermitian: max|H - H†| = {max_asymmetry:.2e}. "
                    "Check units and construction (should be in cm⁻¹, symmetric couplings)."
                )

        logger.debug(
            f"Initializing HopsSimulator (MesoHOPS available: {MESOHOPS_AVAILABLE}, "
            f"use_mesohops: {use_mesohops})"
        )

        if self.use_mesohops:
            self._init_mesohops(**kwargs)

        # Always initialize fallback so it is available if MesoHOPS fails mid-run.
        # _init_mesohops may have already set fallback_sim (on init failure path);
        # skip re-initialization in that case.
        if self.fallback_sim is None:
            self._init_fallback(**kwargs)

    def _get_memory_estimate(self) -> float:
        """
        Dynamically estimate memory per trajectory based on hierarchy depth (L)
        and Matsubara terms (K).

        The scaling relies on heuristics: memory scales quadratically with max hierarchy
        depth and linearly with the number of Matsubara terms. Safety buffers are applied 
        to prevent system out-of-memory (OOM) errors.

        Returns
        -------
        float
            Estimated memory requirement per trajectory in gigabytes (GB).
        """
        l_ref = 8.0
        k_ref = 2.0
        
        # Quadratic scaling with L (approximate growth of hierarchy states)
        l_factor = (self.max_hierarchy / l_ref) ** 2
        # Linear scaling with K (minimum factor 0.5 to avoid under-estimation)
        k_factor = max(0.5, self.k_matsubara / k_ref)
        
        estimate = BASE_TRAJ_MEMORY_GB * l_factor * k_factor
        
        # Apply platform-specific safety buffer if RAM is low
        if HAS_PSUTIL:
            total_ram_gb = psutil.virtual_memory().total / (1024**3)
            if total_ram_gb < 16.0:
                estimate *= 1.5  # 50% more conservative on low-RAM systems
                
        return max(MIN_TRAJ_MEMORY_GB, estimate)

    @staticmethod
    def _alpha_noise1(t_axis: NDArray[np.float64], g: complex, w: complex) -> NDArray[np.complex128]:
        """
        Single-mode exponential bath correlation function.

        Evaluates the exponential form alpha(t) = g * exp(-w*t) used for noise generation
        in the HOPS framework.

        Parameters
        ----------
        t_axis : NDArray[np.float64]
            Time points to evaluate the correlation function over.
        g : complex
            Pre-exponential factor (coupling strength parameter).
        w : complex
            Exponential decay rate (frequency parameter).

        Returns
        -------
        NDArray[np.complex128]
            The evaluated bath correlation function over the given time axis.
        """
        return g * np.exp(-w * t_axis)

    @staticmethod
    def _bcf_dl_to_exp_pairs(lam: float, gamma: float, T: float, k: int) -> list:
        """
        Robustly convert Drude-Lorentz bath parameters to exponential pairs (g, w).

        Since MesoHOPS API signatures vary across versions, this function uses reflection 
        to detect the installed version and route the parameters to the correct parsing logic.

        Parameters
        ----------
        lam : float
            Reorganization energy lambda.
        gamma : float
            Drude-Lorentz cutoff frequency/damping rate.
        T : float
            Temperature in Kelvin.
        k : int
            Number of Matsubara terms to include in the approximation.

        Returns
        -------
        list
            A list of tuples or dictionaries representing the (g, w) exponential 
            decomposition pairs for the Drude-Lorentz spectral density.
        """
        import inspect
        from mesohops.util.bath_corr_functions import bcf_convert_dl_to_exp
        
        try:
            from mesohops.util.bath_corr_functions import bcf_convert_dl_to_exp_with_Matsubara
            # Priority 1: Modern MesoHOPS (v1.6+) with explicit Matsubara function
            dl_modes = bcf_convert_dl_to_exp_with_Matsubara(lam, gamma, T, k)
        except (ImportError, AttributeError):
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
            
        return [[dl_modes[i], dl_modes[i+1]] for i in range(0, len(dl_modes), 2)]

    def _init_mesohops(self, **kwargs: Any) -> None:
        """Initialize MesoHOPS simulator with proper system parameters."""
        try:
            # Prepare system parameters for MesoHOPS - correct API format
            n_sites = self.hamiltonian.shape[0]

            # Get bath parameters from kwargs or use defaults
            lambda_reorg = kwargs.get("reorganization_energy", DEFAULT_REORGANIZATION_ENERGY)
            gamma_cutoff = kwargs.get("drude_cutoff", DEFAULT_DRUDE_CUTOFF)

            # Define system-bath coupling operators (Lindblad operators)
            # MesoHOPS requires sparse matrices for efficiency and compatibility
            L_ops = []
            for i in range(n_sites):
                L_op = np.zeros((n_sites, n_sites), dtype=complex)
                L_op[i, i] = 1.0  # Diagonal operator for site i
                L_ops.append(sp.csc_matrix(L_op))

            # Shift Hamiltonian to center energies around 0.
            E_mean = np.mean(np.diag(self.hamiltonian).real)
            H_shifted = self.hamiltonian - E_mean * np.eye(n_sites, dtype=complex)

            # Build GW_SYSBATH as a flat list of (g, w) tuples — one entry per mode per site.
            gw_sysbath = []
            l_hier_flat = []
            l_noise_flat = []
            param_noise_flat = []

            # 1. Drude-Lorentz modes (one per site)
            # FIX H-6: Use version-agnostic helper to build dl_pairs
            dl_pairs = self._bcf_dl_to_exp_pairs(
                lambda_reorg, gamma_cutoff, self.temperature, self.k_matsubara
            )

            for i in range(n_sites):
                for g, w in dl_pairs:
                    gw_sysbath.append([g, w])
                    l_hier_flat.append(L_ops[i])
                    l_noise_flat.append(L_ops[i])
                    param_noise_flat.append([g, w])

            # 2. Vibronic modes (one per mode per site)
            vib_freqs = kwargs.get("vibronic_frequencies", DEFAULT_VIBRONIC_FREQUENCIES)
            vib_hr = kwargs.get("huang_rhys_factors", DEFAULT_HUANG_RHYS_FACTORS)
            vib_damping_raw = kwargs.get("vibronic_damping", DEFAULT_VIBRONIC_DAMPING)
            
            if np.isscalar(vib_damping_raw):
                vib_damping = np.full(len(vib_freqs), float(vib_damping_raw))
            else:
                vib_damping = np.asarray(vib_damping_raw, dtype=float)

            # Attempt to load the underdamped BCF converter; fall back to
            # single-mode Lorentzian representation if unavailable.
            _ud_bcf = None
            for _fname in ('bcf_convert_sdl_to_exp', 'bcf_convert_dl_ud_to_exp'):
                try:
                    import importlib
                    _mod = importlib.import_module('mesohops.util.bath_corr_functions')
                    _ud_bcf = getattr(_mod, _fname, None)
                    if _ud_bcf is not None:
                        break
                except ImportError:
                    pass

            n_vib_added = 0
            for freq, hr, damp in zip(vib_freqs, vib_hr, vib_damping, strict=False):
                lambda_vib = hr * freq
                if _ud_bcf is not None:
                    try:
                        ud_modes = _ud_bcf(lambda_vib, damp, freq, self.temperature)
                        ud_pairs = [[ud_modes[i], ud_modes[i+1]] for i in range(0, len(ud_modes), 2)]
                    except Exception as _e:
                        logger.warning(f"ud_bcf failed for freq={freq}: {_e} — using single-mode fallback")
                        ud_pairs = [[lambda_vib, freq + 1j * damp]]
                else:
                    # Single-mode Lorentzian: g=λ_vib, w=ω_k + iγ_k
                    ud_pairs = [[lambda_vib, freq + 1j * damp]]
                for g, w in ud_pairs:
                    for i in range(n_sites):
                        gw_sysbath.append([g, w])
                        l_hier_flat.append(L_ops[i])
                        l_noise_flat.append(L_ops[i])
                        param_noise_flat.append([g, w])
                n_vib_added += len(ud_pairs)

            # 3. System parameters dictionary — MesoHOPS format
            self.system_param = {
                "HAMILTONIAN": H_shifted,
                "GW_SYSBATH": gw_sysbath,
                "L_HIER": l_hier_flat,
                "L_NOISE1": l_noise_flat,
                "ALPHA_NOISE1": self._alpha_noise1,
                "PARAM_NOISE1": param_noise_flat,
                "PULSE_PARAMS": {
                    "type": kwargs.get("pulse_type", PULSE_TYPE),
                    "fwhm": kwargs.get("pulse_fwhm", PULSE_FWHM),
                    "delay": kwargs.get("pulse_delay", PULSE_RELATIVE_DELAY),
                    "center_freq": kwargs.get("pulse_center_freq", PULSE_CENTRAL_FREQ),
                    "amplitude": kwargs.get("pulse_amplitude", 0.05),
                }
            }
            logger.info(
                f"MesoHOPS system_param built: {len(gw_sysbath)} hierarchy modes "
                f"({len(dl_pairs)} DL + {n_vib_added} vibronic pairs × {n_sites} sites)"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize MesoHOPS: {e}")
            logger.info("Falling back to fallback chain...")
            self.use_mesohops = False
            self._init_fallback(**kwargs)

    def _init_fallback(self, **kwargs: Any) -> None:
        """Initialize fallback simulator with proper priority.

        Issue-3 fix: the vibronic bath is specified via three separate arrays
        (vibronic_frequencies, huang_rhys_factors, vibronic_damping) in the
        HopsSimulator API.  QuantumDynamicsSimulator expects a single
        ``vibronic_modes`` list of dicts {'omega', 'lambda', 'gamma'}.
        We build that list here so the fallback uses the same 12-mode bath
        that the primary MesoHOPS path uses.
        """
        # Build vibronic_modes list from the three-array representation used by
        # HopsSimulator's public API (vibronic_frequencies / huang_rhys_factors /
        # vibronic_damping) so the fallback simulator sees the correct bath.
        vib_freqs   = np.asarray(kwargs.get("vibronic_frequencies", DEFAULT_VIBRONIC_FREQUENCIES), dtype=float)
        vib_hr      = np.asarray(kwargs.get("huang_rhys_factors",   DEFAULT_HUANG_RHYS_FACTORS),   dtype=float)
        vib_damping = np.asarray(kwargs.get("vibronic_damping",     DEFAULT_VIBRONIC_DAMPING),     dtype=float)

        # Pad shorter arrays to the longest so zip is safe
        n_modes = max(len(vib_freqs), len(vib_hr), len(vib_damping))
        if n_modes > 0:
            if len(vib_freqs)   < n_modes: vib_freqs   = np.pad(vib_freqs,   (0, n_modes - len(vib_freqs)))
            if len(vib_hr)      < n_modes: vib_hr      = np.pad(vib_hr,      (0, n_modes - len(vib_hr)))
            if len(vib_damping) < n_modes: vib_damping = np.pad(vib_damping, (0, n_modes - len(vib_damping)))

        vibronic_modes = [
            {"omega": float(omega), "lambda": float(hr) * float(omega), "gamma": float(gamma)}
            for omega, hr, gamma in zip(vib_freqs, vib_hr, vib_damping)
            if float(omega) > 0.0
        ]

        # Priority 1: Full QuantumDynamicsSimulator (requires MesoHOPS but has more robust init)
        if QuantumDynamicsSimulator is not None:
            try:
                qds_kwargs = {
                    "temperature":    self.temperature,
                    "lambda_reorg":   kwargs.get("reorganization_energy", DEFAULT_REORGANIZATION_ENERGY),
                    "gamma_dl":       kwargs.get("drude_cutoff",          DEFAULT_DRUDE_CUTOFF),
                    "max_hier":       self.max_hierarchy,
                    "k_matsubara":    self.k_matsubara,
                    "n_traj":         self.n_traj,
                    "vibronic_modes": vibronic_modes if vibronic_modes else None,
                }

                self.fallback_sim = QuantumDynamicsSimulator(self.hamiltonian, **qds_kwargs)
                logger.info(
                    f"QuantumDynamicsSimulator (HOPS-based) initialized as fallback "
                    f"({len(vibronic_modes)} vibronic modes)"
                )
                return
            except Exception as e:
                logger.warning(f"Failed to initialize QuantumDynamicsSimulator fallback: {e}")

        # Priority 2: SimpleQuantumDynamicsSimulator (no MesoHOPS required, but less accurate)
        if SimpleQuantumDynamicsSimulator is not None:
            try:
                self.fallback_sim = SimpleQuantumDynamicsSimulator(
                    self.hamiltonian, temperature=self.temperature
                )
                logger.info("SimpleQuantumDynamicsSimulator (Schrödinger-based) initialized as fallback")
                return
            except Exception as e:
                logger.error(f"Failed to initialize SimpleQuantumDynamicsSimulator fallback: {e}")

        logger.error("Failed to initialize any fallback simulator")
        self.fallback_sim = None

    def simulate_dynamics(
        self,
        time_points: NDArray[np.float64],
        initial_state: Optional[NDArray[np.float64]] = None,
        strict_mode: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Simulate quantum dynamics.

        Uses MesoHOPS if available, otherwise falls back to custom simulator.

        Parameters
        ----------
        time_points : NDArray[np.float64]
            Array of time points for simulation
        initial_state : Optional[NDArray[np.float64]]
            Initial quantum state (default: None)
        **kwargs : dict
            Additional simulation parameters

        Returns
        -------
        Dict[str, Any]
            Simulation results containing populations, coherences, and other metrics

        Raises
        ------
        RuntimeError
            If no simulator is available
        """
        logger.info(f"Starting dynamics simulation for {len(time_points)} time points")

        if self.use_mesohops and hasattr(self, "system_param") and self.system_param is not None:
            try:
                logger.debug("Attempting MesoHOPS simulation")
                return self._simulate_with_mesohops(time_points, initial_state, **kwargs)
            except (RuntimeError, ModuleNotFoundError) as e:
                if strict_mode:
                    logger.error(f"MesoHOPS simulation failed in strict_mode: {e}")
                    raise
                logger.error(f"MesoHOPS simulation failed mid-run, falling back to SimpleQuantumDynamicsSimulator: {e}")
                logger.info("Falling back to custom simulator...")

        # Fallback to custom simulator
        if self.fallback_sim is not None:
            logger.warning("Using fallback simulator. Results will not show L-dependence.")
            # Strip HopsSimulator-only kwargs that the fallback doesn't understand
            _HOPS_ONLY = {"n_traj", "show_progress", "desc", "seed", "strict_mode"}
            fallback_kwargs = {k: v for k, v in kwargs.items() if k not in _HOPS_ONLY}
            try:
                result = self.fallback_sim.simulate_dynamics(
                    time_points=time_points, initial_state=initial_state, **fallback_kwargs
                )
                # Issue-5 fix: inject n_traj_used so main.py can safely access it
                # regardless of which fallback path was taken.
                result.setdefault("n_traj_used", self.n_traj)
                return result
            except Exception as e2:
                if strict_mode:
                    logger.error(f"Primary fallback failed in strict_mode: {e2}")
                    raise
                logger.error(f"Primary fallback also failed: {e2}. Trying SimpleQuantumDynamicsSimulator.")
                if SimpleQuantumDynamicsSimulator is not None:
                    simple = SimpleQuantumDynamicsSimulator(self.hamiltonian, temperature=self.temperature)
                    return simple.simulate_dynamics(time_points=time_points, initial_state=initial_state)
        elif SimpleQuantumDynamicsSimulator is not None:
            logger.warning("No fallback_sim set; using SimpleQuantumDynamicsSimulator directly.")
            simple = SimpleQuantumDynamicsSimulator(self.hamiltonian, temperature=self.temperature)
            return simple.simulate_dynamics(time_points=time_points, initial_state=initial_state)
        else:
            raise RuntimeError("No simulator available")

    def _simulate_with_mesohops(
        self,
        time_points: NDArray[np.float64],
        initial_state: Optional[NDArray[np.float64]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Internal method to run MesoHOPS simulation with proper quantum dynamics.

        Mathematical Framework:
        Uses the Hierarchy of Pure States (HOPS) method to solve the
        stochastic Schrödinger equation for non-Markovian open quantum systems:

        |ψ(t)⟩ = |ψ(0)⟩ + ∫₀ᵗ dt' [Ĥ_eff(t') + noise terms] |ψ(t')⟩

        where Ĥ_eff includes the system Hamiltonian and system-bath interactions.
        """
        # Import required MesoHOPS classes
        if HopsTrajectory is None:
            raise RuntimeError("MesoHOPS not available for simulation")

        try:
            # Get simulation parameters
            max_hierarchy = kwargs.get("max_hierarchy", self.max_hierarchy)
            k_matsubara = kwargs.get("k_matsubara", self.k_matsubara)

            # Set up hierarchy parameters — L is the truncation depth.
            # TERMINATOR=True applies the Markovian terminator at the boundary,
            # which reduces memory by ~50% with negligible accuracy loss.
            # STATIC_BASIS with triangular filter cuts the active hierarchy
            # from O(modes^L) to O(modes*L) — essential for 77-mode systems.
            # STATIC_FILTERS "Triangular" expects params = [boolean_by_mode, kmax_2]
            # boolean_by_mode: list of bools, length n_hmodes (which modes to filter)
            # kmax_2: int, max individual mode depth (set equal to MAXHIER = no extra cut)
            n_hmodes = len(self.system_param["GW_SYSBATH"])
            hierarchy_param = {
                "MAXHIER": max_hierarchy,
                "TERMINATOR": True,
                "STATIC_FILTERS": [["Triangular", [[True] * n_hmodes, max_hierarchy]]],
            }

            # Set up EOM parameters - use NORMALIZED NONLINEAR for better numerical stability
            eom_param = {
                "EQUATION_OF_MOTION": "NORMALIZED NONLINEAR",
                "TIME_DEPENDENCE": False,
            }

            # Set up noise parameters based on test examples
            t_max = float(np.max(time_points)) if len(time_points) > 0 else DEFAULT_MAX_TIME
            # Use explicit dt if provided to handle arbitrary time grids safely
            dt_save = kwargs.get("dt", float(time_points[1] - time_points[0]) if len(time_points) > 1 else DEFAULT_TIME_STEP)

            noise_param = {
                "SEED": kwargs.get("seed", MESOHOPS_SEED),
                "MODEL": "FFT_FILTER",
                "TLEN": float(t_max + FFT_NOISE_BUFFER_FS),  # must be float
                "TAU": float(dt_save * 0.5),                 # must be float
            }

            # Set up integrator parameters based on test examples
            integrator_param = {
                "INTEGRATOR": "RUNGE_KUTTA",
                "EARLY_ADAPTIVE_INTEGRATOR": "INCH_WORM",
                "EARLY_INTEGRATOR_STEPS": MESOHOPS_EARLY_STEPS,
                "INCHWORM_CAP": MESOHOPS_INCHWORM_CAP,
                "STATIC_BASIS": None,
            }

            # Select Trajectory Engine
            TrajectoryClass = HopsTrajectory
            traj_kwargs = {
                "system_param": self.system_param,
                "eom_param": eom_param,
                "noise_param": noise_param,
                "hierarchy_param": hierarchy_param,
                "integration_param": integrator_param,
            }

            if self.use_sbd and SBD_HopsTrajectory is not None:
                TrajectoryClass = SBD_HopsTrajectory
                traj_kwargs["n_bundles_per_site"] = kwargs.get("sbd_bundles_per_site", self.sbd_bundles_per_site)
                logger.info("Engaging SBD_HopsTrajectory for compressed environmental simulation.")
            elif self.use_pt_hops and PT_HopsNoise is not None:
                logger.info("Engaging PT_HopsNoise for Process Tensor dynamics.")
                # We will handle PT-HOPS by overriding the noise component after trajectory init
                pass

            # ── Run ensemble of trajectories (Parallelized) ─────────────────────
            # Ensemble size: use kwarg, then self.n_traj, then fallback to 1
            n_traj = kwargs.get("n_traj", self.n_traj if hasattr(self, "n_traj") else 1)
            cpu_count = multiprocessing.cpu_count()

            # Memory-aware parallelization (User mandate: max 2/3 of available RAM)
            if HAS_PSUTIL:
                mem_avail_gb = psutil.virtual_memory().available / (1024**3)
                mem_limit_gb = mem_avail_gb * MEMORY_FRACTION_LIMIT
                # Dynamic estimate based on L and K
                traj_mem_gb = self._get_memory_estimate()
                n_mem_jobs = max(1, int(mem_limit_gb / traj_mem_gb))
                n_jobs = min(n_mem_jobs, cpu_count)
                logger.info(
                    f"Memory-aware n_jobs: {n_jobs} (Avail: {mem_avail_gb:.1f}GB, Limit: {mem_limit_gb:.1f}GB, Est/Traj: {traj_mem_gb:.1f}GB)"
                )
            else:
                n_jobs = max(1, int(cpu_count * 0.5)) if n_traj > 1 else 1
                logger.warning(f"psutil not available; using conservative n_jobs: {n_jobs}")

            if n_traj == 1:
                n_jobs = 1

            # Determine seeds
            seeds = kwargs.get("seeds", list(range(n_traj)))

            # Prepare arguments for the picklable worker
            worker_args = {
                "TrajectoryClass": TrajectoryClass,
                "traj_kwargs": traj_kwargs,
                "use_pt_hops": self.use_pt_hops,
                "pt_hops_noise_class": PT_HopsNoise,
                "system_param": self.system_param,
                "initial_state": initial_state,
                "t_max": t_max,
                "dt_save": dt_save,
                "time_points": time_points,
            }

            if HAS_JOBLIB and n_jobs > 1:
                logger.info(f"Running ensemble of {n_traj} trajectories on {n_jobs} cores...")

                # Setup tqdm progress bar
                iterable = seeds
                if HAS_TQDM and kwargs.get("show_progress", True):
                    desc = kwargs.get("desc", "Trajectories")
                    iterable = tqdm(seeds, desc=desc, unit="traj", leave=False)

                traj_results = Parallel(n_jobs=n_jobs)(
                    delayed(_run_single_traj_worker)(s, **worker_args) for s in iterable
                )
            else:
                traj_results = [
                    _run_single_traj_worker(s, **worker_args) for s in seeds
                ]

            # Filter failed trajectories
            traj_results = [r for r in traj_results if r is not None]
            if not traj_results:
                raise RuntimeError("All parallel trajectories failed.")

            # Ensemble averaging
            t_axis = traj_results[0]["t_axis"]
            n_times = len(t_axis)
            n_sites = self.hamiltonian.shape[0]
            n_valid = len(traj_results)
            
            # Construct averaged rho(t)
            # We use the physical subspace (first n_sites)
            density_matrices = []
            populations = np.zeros((n_times, n_sites))
            coherences = np.zeros(n_times)
            
            for i in range(n_times):
                rho = np.zeros((n_sites, n_sites), dtype=complex)
                for res in traj_results:
                    psi = res["psi_traj"][i, :n_sites]
                    rho += np.outer(psi, np.conj(psi))
                rho /= n_valid
                
                # Trace normalization
                tr = np.trace(rho).real
                if tr > 1e-10:
                    rho /= tr
                
                density_matrices.append(rho)
                populations[i, :] = np.real(np.diag(rho))
                coherences[i] = float(np.sum(np.abs(rho)) - np.sum(np.abs(np.diag(rho))))

            # Calculate other metrics (QFI, IPR, Entropy)
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

            logger.info(f"Ensemble averaged over {n_valid} trajectories completed.")

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
            }

        except (
            RuntimeError,
            AttributeError,
            ValueError,
            TypeError,
            OSError,
            np.linalg.LinAlgError,
        ) as e:
            import traceback

            traceback.print_exc()
            logger.error(f"MesoHOPS simulation failed: {e}")
            raise RuntimeError(f"MesoHOPS simulation failed: {e}") from e

    def _calculate_von_neumann_entropy(self, rho: NDArray[np.float64]) -> float:
        """Calculate the von Neumann entropy: -Tr[rho * log(rho)]."""
        # Get eigenvalues of the density matrix
        eigenvals = np.linalg.eigvals(rho)
        # Take real part and ensure non-negative
        eigenvals = np.real(eigenvals)
        eigenvals = np.clip(eigenvals, 1e-12, None)
        # Calculate entropy: -Σ λᵢ log(λᵢ)
        entropy = -np.sum(eigenvals * np.log(eigenvals))
        return float(entropy)

    def _calculate_qfi(self, rho: NDArray[np.float64], H: NDArray[np.float64]) -> float:
        """
        Calculate the Quantum Fisher Information for parameter estimation.

        QFI = 2 * Σᵢ Σⱼ (λᵢ - λⱼ)² / (λᵢ + λⱼ) * |⟨i|H|j⟩|²
        where λᵢ are eigenvalues and |i⟩ are eigenvectors of rho.
        """
        try:
            eigenvals, eigenvecs = np.linalg.eigh(rho)
            eigenvals = np.real(eigenvals)

            # Calculate QFI
            qfi = 0.0
            n = len(eigenvals)
            for i in range(n):
                for j in range(n):
                    denom = eigenvals[i] + eigenvals[j]
                    if denom > 1e-12:
                        Hij = np.abs(np.vdot(eigenvecs[:, i], H @ eigenvecs[:, j])) ** 2
                        qfi += 2.0 * (eigenvals[i] - eigenvals[j]) ** 2 / denom * Hij

            return float(qfi)
        except (np.linalg.LinAlgError, ValueError):
            return 0.0

    def create_basis(self) -> Optional[HopsBasis]:
        """
        Create MesoHOPS basis for the Hamiltonian.

        Returns
        -------
        Optional[HopsBasis]
            MesoHOPS basis object or None if not available
        """
        if not MESOHOPS_AVAILABLE or HopsBasis is None:
            logger.warning("MesoHOPS not available for basis creation")
            return None

        try:
            system_dict = {
                "hamiltonian": self.hamiltonian,
                "temperature": self.temperature,
                "n_site": self.hamiltonian.shape[0],
                "n_exciton": 1,
            }
            basis = HopsBasis(system_dict, self.max_hierarchy)
            logger.debug("MesoHOPS basis created successfully")
            return basis
        except (RuntimeError, ValueError, TypeError) as e:
            logger.error(f"Failed to create MesoHOPS basis: {e}")
            return None

    def create_trajectory(self, basis: HopsBasis) -> Optional[HopsTrajectory]:
        """
        Create MesoHOPS trajectory for quantum dynamics.

        Parameters
        ----------
        basis : HopsBasis
            MesoHOPS basis object

        Returns
        -------
        Optional[HopsTrajectory]
            MesoHOPS trajectory object or None if not available
        """
        if not MESOHOPS_AVAILABLE or HopsTrajectory is None:
            logger.warning("MesoHOPS not available for trajectory creation")
            return None

        try:
            trajectory = HopsTrajectory(
                basis, temperature=self.temperature, max_hier=self.max_hierarchy
            )
            logger.debug("MesoHOPS trajectory created successfully")
            return trajectory
        except (RuntimeError, ValueError, TypeError) as e:
            logger.error(f"Failed to create MesoHOPS trajectory: {e}")
            return None

    @property
    def is_using_mesohops(self) -> bool:
        """Check if MesoHOPS is being used."""
        return self.use_mesohops and hasattr(self, "system_param") and self.system_param is not None

    @property
    def simulator_type(self) -> str:
        """Get the type of simulator being used."""
        if self.is_using_mesohops:
            base = "MesoHOPS"
            exts = []
            if self.use_pt_hops:
                exts.append("PT")
            if self.use_sbd:
                exts.append("SBD")
            return f"{base} ({' + '.join(exts)})" if exts else base
        elif self.fallback_sim is not None:
            return "QuantumDynamicsSimulator (fallback)"
        else:
            return "None (not initialized)"
