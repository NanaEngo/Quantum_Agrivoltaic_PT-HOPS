"""
HopsSimulator: Unified quantum dynamics simulator with MesoHOPS integration.

This module provides the HopsSimulator class which uses MesoHOPS as the default
simulation engine with automatic fallback to QuantumDynamicsSimulator.
"""

import sys
from typing import Any, Dict, Optional

import numpy as np
from numpy.typing import NDArray

# Import MesoHOPS modules
try:
    from mesohops.basis.hops_basis import HopsBasis
    from mesohops.basis.hops_system import HopsSystem
    from mesohops.trajectory.hops_trajectory import HopsTrajectory

    MESOHOPS_AVAILABLE = True
except ImportError:
    MESOHOPS_AVAILABLE = False
    HopsSystem = None
    HopsBasis = None
    HopsTrajectory = None

# Import our custom PT-HOPS and SBD Extensions (absolute import)
try:
    from extensions.mesohops_adapters import PT_HopsNoise, SBD_HopsTrajectory
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
    from core.constants import (
        DEFAULT_DRUDE_CUTOFF,
        DEFAULT_HUANG_RHYS_FACTORS,
        DEFAULT_MAX_HIERARCHY,
        DEFAULT_N_MATSUBARA,
        DEFAULT_REORGANIZATION_ENERGY,
        DEFAULT_TEMPERATURE,
        DEFAULT_VIBRONIC_DAMPING,
        DEFAULT_VIBRONIC_FREQUENCIES,
        PULSE_CENTRAL_FREQ,
        PULSE_FWHM,
        PULSE_RELATIVE_DELAY,
        PULSE_TYPE,
        PULSE_AMPLITUDE,
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
        PULSE_CENTRAL_FREQ,
        PULSE_FWHM,
        PULSE_RELATIVE_DELAY,
        PULSE_TYPE,
        PULSE_AMPLITUDE,
    )

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


class HopsSimulator:
    """
    Unified simulator that uses MesoHOPS by default with fallback.

    This class provides a consistent interface for quantum dynamics simulations,
    automatically using MesoHOPS when available and falling back to the custom
    QuantumDynamicsSimulator when needed.

    Parameters
    ----------
    hamiltonian : NDArray[np.float64]
        System Hamiltonian matrix
    temperature : float, optional
        Temperature in Kelvin (default: 295.0)
    use_mesohops : bool, optional
        Whether to use MesoHOPS if available (default: True)
    max_hierarchy : int, optional
        Maximum hierarchy level for MesoHOPS (default: 10)
    **kwargs : dict
        Additional arguments passed to underlying simulator

    Attributes
    ----------
    hamiltonian : NDArray[np.float64]
        The system Hamiltonian
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
    >>> from core.hops_simulator import HopsSimulator
    >>> hamiltonian = np.array([[1, 0.5], [0.5, 1]])
    >>> simulator = HopsSimulator(hamiltonian, temperature=295)
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
        self.use_sbd = kwargs.pop("use_sbd", False)
        self.sbd_bundles_per_site = kwargs.pop("sbd_bundles_per_site", 2)
        self.system = None
        self.fallback_sim: Optional[Any] = None

        logger.debug(
            f"Initializing HopsSimulator (MesoHOPS available: {MESOHOPS_AVAILABLE}, "
            f"use_mesohops: {use_mesohops})"
        )

        if self.use_mesohops:
            self._init_mesohops(**kwargs)

        # Initialize fallback only if MesoHOPS was not requested or failed without
        # already initializing a fallback inside _init_mesohops
        if not self.use_mesohops and self.fallback_sim is None:
            self._init_fallback(**kwargs)

    def _init_mesohops(self, **kwargs: Any) -> None:
        """Initialize MesoHOPS simulator with proper system parameters."""
        try:
            # Prepare system parameters for MesoHOPS - correct API format
            n_sites = self.hamiltonian.shape[0]

            # Get bath parameters from kwargs or use defaults
            lambda_reorg = kwargs.get("reorganization_energy", DEFAULT_REORGANIZATION_ENERGY)
            gamma_cutoff = kwargs.get("drude_cutoff", DEFAULT_DRUDE_CUTOFF)

            # Define system-bath coupling operators (Lindblad operators)
            # MesoHOPS uses dense arrays for L operators based on test examples
            L_hier = []
            L_noise = []
            for i in range(n_sites):
                L_op = np.zeros((n_sites, n_sites), dtype=np.float64)
                L_op[i, i] = 1.0  # Diagonal operator for site i
                L_hier.append(L_op)
                L_noise.append(L_op)

            # Shift Hamiltonian to center energies around 0.
            # Large absolute energies (like ~12000 cm^-1 for FMO) cause rapid oscillations
            # exp(-i H t / hbar) which numerical integrators struggle with, causing overflows.
            # Physical observables (populations) are invariant to uniform energy shifts.
            E_mean = np.mean(np.diag(self.hamiltonian))
            H_shifted = self.hamiltonian - E_mean * np.eye(n_sites)

            # Build GW_SYSBATH as a flat list of (g, w) tuples — one entry per mode per site.
            # MesoHOPS requires: GW_SYSBATH[k] = (g_k, w_k), L_HIER[k] = coupling op for mode k.
            gw_sysbath = []   # flat list of (g, w) tuples
            l_hier_flat = []  # coupling operator for each mode
            l_noise_flat = []

            # 1. Drude-Lorentz modes (one per site)
            try:
                from mesohops.util.bath_corr_functions import bcf_convert_dl_to_exp
                # pass k_matsubara to enable PT-HOPS/low-temp corrections
                dl_modes = bcf_convert_dl_to_exp(
                    lambda_reorg, gamma_cutoff, self.temperature, n_matsubara=self.k_matsubara
                )
                # dl_modes = [g0, w0, g1, w1, ...] — pairs of (g, w)
                dl_pairs = [(dl_modes[i], dl_modes[i+1]) for i in range(0, len(dl_modes), 2)]
            except (ImportError, AttributeError, TypeError) as e:
                # Try legacy name if modern name fails
                try:
                    from mesohops.util.bath_corr_functions import bcf_convert_dl_to_exp_with_Matsubara
                    dl_modes = bcf_convert_dl_to_exp_with_Matsubara(
                        lambda_reorg, gamma_cutoff, self.temperature, self.k_matsubara
                    )
                    dl_pairs = [(dl_modes[i], dl_modes[i+1]) for i in range(0, len(dl_modes), 2)]
                except Exception:
                    raise RuntimeError(
                        f"MesoHOPS bath conversion failed — cannot build valid GW_SYSBATH: {e}"
                    ) from e

            for i in range(n_sites):
                for g, w in dl_pairs:
                    gw_sysbath.append((g, w))
                    l_hier_flat.append(L_hier[i])
                    l_noise_flat.append(L_noise[i])

            # 2. Vibronic modes (one per mode per site)
            vib_freqs = kwargs.get("vibronic_frequencies", DEFAULT_VIBRONIC_FREQUENCIES)
            vib_hr = kwargs.get("huang_rhys_factors", DEFAULT_HUANG_RHYS_FACTORS)
            vib_damping_raw = kwargs.get("vibronic_damping", DEFAULT_VIBRONIC_DAMPING)
            # Normalize: scalar → broadcast to array matching vib_freqs length
            if np.isscalar(vib_damping_raw):
                vib_damping = np.full(len(vib_freqs), float(vib_damping_raw))
            else:
                vib_damping = np.asarray(vib_damping_raw, dtype=float)

            # Use bcf_convert_sdl_to_exp for underdamped vibronic modes.
            # Each mode returns [g1, w1, g2, w2] — two complex conjugate pairs.
            try:
                try:
                    from mesohops.util.bath_corr_functions import bcf_convert_sdl_to_exp as bcf_convert_dl_ud_to_exp
                except ImportError:
                    from mesohops.util.bath_corr_functions import bcf_convert_dl_ud_to_exp
                use_ud_bcf = True
            except ImportError:
                use_ud_bcf = False

            n_vib_added = 0
            for freq, hr, damp in zip(vib_freqs, vib_hr, vib_damping, strict=False):
                lambda_vib = hr * freq
                if use_ud_bcf:
                    ud_modes = bcf_convert_dl_ud_to_exp(lambda_vib, damp, freq, self.temperature)
                    ud_pairs = [(ud_modes[i], ud_modes[i+1]) for i in range(0, len(ud_modes), 2)]
                else:
                    ud_pairs = [(lambda_vib, freq + 1j * damp)]
                for g, w in ud_pairs:
                    for i in range(n_sites):
                        gw_sysbath.append((g, w))
                        l_hier_flat.append(L_hier[i])
                        l_noise_flat.append(L_noise[i])
                n_vib_added += len(ud_pairs)

            # 3. System parameters dictionary — MesoHOPS format
            from mesohops.trajectory.exp_noise import bcf_exp

            self.system_param = {
                "HAMILTONIAN": H_shifted,
                "GW_SYSBATH": gw_sysbath,
                "L_HIER": l_hier_flat,
                "L_NOISE1": l_noise_flat,
                "ALPHA_NOISE1": bcf_exp,
                "PARAM_NOISE1": gw_sysbath,
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
        except (ImportError, AttributeError, RuntimeError, ValueError) as e:
            logger.warning(f"Failed to initialize MesoHOPS: {e}")
            logger.info("Falling back to QuantumDynamicsSimulator")
            self.use_mesohops = False
            self._init_fallback(**kwargs)

    def _init_fallback(self, **kwargs: Any) -> None:
        """Initialize fallback simulator."""
        # First try the simple simulator as it doesn't require MesoHOPS
        if SimpleQuantumDynamicsSimulator is not None:
            try:
                self.fallback_sim = SimpleQuantumDynamicsSimulator(
                    self.hamiltonian, temperature=self.temperature
                )
                logger.info("SimpleQuantumDynamicsSimulator initialized successfully")
                return
            except (ImportError, RuntimeError, ValueError) as e:
                logger.error(f"Failed to initialize SimpleQuantumDynamicsSimulator: {e}")

        # Then try the full QuantumDynamicsSimulator (this may fail if MesoHOPS is not available)
        if QuantumDynamicsSimulator is not None:
            try:
                # Filter kwargs to only pass parameters that QuantumDynamicsSimulator accepts
                qds_kwargs = {}
                valid_params = {
                    "temperature",
                    "lambda_reorg",
                    "gamma_dl",
                    "k_matsubara",
                    "max_hier",
                    "n_traj",
                    "vibronic_modes",
                }

                for key, value in kwargs.items():
                    if key in valid_params:
                        qds_kwargs[key] = value

                # Use default values if not provided
                qds_kwargs.setdefault("temperature", self.temperature)
                qds_kwargs.setdefault(
                    "lambda_reorg",
                    kwargs.get("reorganization_energy", DEFAULT_REORGANIZATION_ENERGY),
                )
                qds_kwargs.setdefault("gamma_dl", kwargs.get("drude_cutoff", DEFAULT_DRUDE_CUTOFF))
                qds_kwargs.setdefault("max_hier", self.max_hierarchy)
                qds_kwargs.setdefault("k_matsubara", self.k_matsubara)
                qds_kwargs.setdefault("n_traj", 10)

                self.fallback_sim = QuantumDynamicsSimulator(self.hamiltonian, **qds_kwargs)
                logger.info("QuantumDynamicsSimulator initialized successfully")
                return
            except (ImportError, RuntimeError, ValueError) as e:
                logger.warning(f"Failed to initialize QuantumDynamicsSimulator: {e}")

        # If both fail, log error
        logger.error("Failed to initialize any fallback simulator")
        self.fallback_sim = None

    def simulate_dynamics(
        self,
        time_points: NDArray[np.float64],
        initial_state: Optional[NDArray[np.float64]] = None,
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
                logger.error(f"MesoHOPS simulation failed mid-run, falling back to SimpleQuantumDynamicsSimulator: {e}")
                logger.info("Falling back to custom simulator...")

        # Fallback to custom simulator
        if self.fallback_sim is not None:
            logger.warning("Using fallback simulator. Results will not show L-dependence.")
            # Remove aggressive filtering so fallback receives all physics params
            fallback_kwargs = dict(kwargs)
            # Use keyword args to avoid arg-order mismatch between fallback implementations
            return self.fallback_sim.simulate_dynamics(
                time_points=time_points, initial_state=initial_state, **fallback_kwargs
            )
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

            # Set up hierarchy parameters — L is the truncation depth
            # Note: K_MATSUBARA is handled via bcf_convert_dl_to_exp_with_Matsubara
            # in the bath decomposition, not as a hierarchy parameter in this MesoHOPS version
            hierarchy_param = {
                "MAXHIER": max_hierarchy,
                "TERMINATOR": False,
                "STATIC_FILTERS": [],
            }

            # Set up EOM parameters - use LINEAR for simplicity
            eom_param = {
                "EQUATION_OF_MOTION": "LINEAR",
                "TIME_DEPENDENCE": False,
            }

            # Set up noise parameters based on test examples
            t_max = float(np.max(time_points)) if len(time_points) > 0 else 500.0
            # Use explicit dt if provided to handle arbitrary time grids safely
            dt_save = kwargs.get("dt", float(time_points[1] - time_points[0]) if len(time_points) > 1 else 0.5)

            noise_param = {
                "SEED": kwargs.get("seed", 42),
                "MODEL": "FFT_FILTER",
                "TLEN": t_max + 100.0,  # Add buffer
                "TAU": dt_save,
            }

            # Set up integrator parameters based on test examples
            integrator_param = {
                "INTEGRATOR": "RUNGE_KUTTA",
                "EARLY_ADAPTIVE_INTEGRATOR": "INCH_WORM",
                "EARLY_INTEGRATOR_STEPS": 5,
                "INCHWORM_CAP": 5,
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

            # Create HOPS trajectory with all parameters
            trajectory = TrajectoryClass(**traj_kwargs)

            # If PT-HOPS, inject our custom noise adapter
            if self.use_pt_hops and PT_HopsNoise is not None:
                pt_noise = PT_HopsNoise(noise_param, self.system_param["PARAM_NOISE1"])
                # Some mesohops versions use .noise, others .noise_engine
                if hasattr(trajectory, "noise"):
                    trajectory.noise = pt_noise
                # Prepare the Process Tensor on the trajectory's time grid (use safe access)
                try:
                    pt_noise._prepare_noise(self.system_param["L_NOISE1"], time_points=time_points)
                except AttributeError:
                    logger.warning(
                        "PT_HopsNoise._prepare_noise not available in this adapter version"
                    )

            # Set initial state
            if initial_state is None:
                raise ValueError("initial_state must be explicitly provided. Defaulting to site 0 is physically unsafe for arbitrary Hamiltonians.")

            trajectory.initialize(initial_state.copy())

            # Propagate the system — tau is the internal integration timestep
            trajectory.propagate(t_max, dt_save)

            # Extract results from trajectory
            t_axis = np.array(trajectory.storage.data["t_axis"])

            # MesoHOPS stores the full hierarchy state vector in psi_traj.
            # The physical (system) subspace occupies the first n_sites components
            # of the zeroth hierarchy layer, which is always the leading block.
            # We use 'pop_site' if available (direct population output), otherwise
            # fall back to extracting from psi_traj.
            n_times = len(t_axis)
            n_sites = self.hamiltonian.shape[0]

            storage_data = trajectory.storage.data
            if "pop_site" in storage_data:
                # Preferred: direct population output from MesoHOPS storage
                populations = np.real(np.array(storage_data["pop_site"]))  # shape (T, n_sites)
                if populations.ndim == 1:
                    populations = populations.reshape(-1, 1)
            else:
                # Fallback: extract physical subspace from psi_traj
                psi_traj = np.array(storage_data["psi_traj"])
                populations = np.zeros((n_times, n_sites))
                for i in range(n_times):
                    psi = psi_traj[i, :n_sites]
                    populations[i, :] = np.real(psi * np.conj(psi))

            # Calculate coherences from populations (or psi_traj if available)
            coherences = np.zeros(n_times)
            if "psi_traj" in storage_data:
                psi_traj = np.array(storage_data["psi_traj"])
                for i in range(n_times):
                    psi = psi_traj[i, :n_sites]
                    rho = np.outer(psi, np.conj(psi))
                    coherences[i] = float(np.sum(np.abs(rho)) - np.sum(np.abs(np.diag(rho))))

            # Calculate other quantum metrics
            qfi_values = np.zeros(n_times)
            entropy_values = np.zeros(n_times)

            psi_traj_arr = np.array(storage_data["psi_traj"]) if "psi_traj" in storage_data else None
            for i in range(n_times):
                if psi_traj_arr is not None:
                    psi = psi_traj_arr[i, :n_sites]
                    rho = np.outer(psi, np.conj(psi))
                else:
                    # Build rho from populations (diagonal only — coherences lost)
                    rho = np.diag(populations[i, :].astype(complex))
                # Normalize
                trace_rho = np.trace(rho).real
                if trace_rho > 1e-10:
                    rho = rho / trace_rho
                entropy_values[i] = self._calculate_von_neumann_entropy(rho)
                try:
                    qfi_values[i] = self._calculate_qfi(rho, self.hamiltonian)
                except (np.linalg.LinAlgError, ValueError):
                    qfi_values[i] = 0.0

            logger.debug("MesoHOPS simulation completed successfully")

            return {
                "t_axis": t_axis,
                "populations": populations,
                "coherences": coherences,
                "qfi": qfi_values,
                "entropy": entropy_values,
                "simulator": "MesoHOPS",
                "n_traj_used": 1,  # Single trajectory
                "max_hierarchy_used": max_hierarchy,
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
