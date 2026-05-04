"""
hops_simulator.py — Corrected HopsSimulator with verified MesoHOPS API.

Key fixes vs original:
  1. bcf_exp imported from mesohops.trajectory.exp_noise (correct location)
  2. bcf_convert_dl_to_exp from mesohops.util.bath_corr_functions (correct name)
  3. PULSE_PARAMS removed from system_param (not a valid MesoHOPS key)
  4. storage accessed via hops.storage['psi_traj'] dict-style (not .data attribute)
  5. storage_param={'psi_traj': True, 't_axis': True} passed to HopsTrajectory
  6. gw_sysbath built as list of [g, w] pairs (not tuples) matching quickstart
  7. Markovian correction mode added per quickstart example
"""

import sys
from typing import Any, Dict, Optional

import numpy as np
import scipy.sparse as sp
from numpy.typing import NDArray

# ── MesoHOPS imports ──────────────────────────────────────────────────────────
try:
    from mesohops.trajectory.hops_trajectory import HopsTrajectory
    # bcf_exp lives in mesohops.trajectory.exp_noise
    from mesohops.trajectory.exp_noise import bcf_exp
    # Bath conversion lives in mesohops.util.bath_corr_functions
    from mesohops.util.bath_corr_functions import bcf_convert_dl_to_exp
    try:
        from mesohops.util.bath_corr_functions import bcf_convert_dl_ud_to_exp
        _HAS_UD = True
    except ImportError:
        _HAS_UD = False
    MESOHOPS_AVAILABLE = True
except ImportError:
    HopsTrajectory = None
    bcf_exp = None
    bcf_convert_dl_to_exp = None
    _HAS_UD = False
    MESOHOPS_AVAILABLE = False

# ── Fallback simulator ────────────────────────────────────────────────────────
try:
    from models.simple_quantum_dynamics_simulator import SimpleQuantumDynamicsSimulator
except ImportError:
    try:
        from ..models.simple_quantum_dynamics_simulator import SimpleQuantumDynamicsSimulator
    except ImportError:
        SimpleQuantumDynamicsSimulator = None

# ── Defaults ──────────────────────────────────────────────────────────────────
DEFAULT_TEMPERATURE = 295.0        # K
DEFAULT_REORGANIZATION_ENERGY = 35.0  # cm^-1
DEFAULT_DRUDE_CUTOFF = 50.0        # cm^-1
DEFAULT_MAX_HIERARCHY = 10
DEFAULT_N_MATSUBARA = 0            # 0 = no Matsubara correction (fast)
DEFAULT_MARKOVIAN_CUTOFF = 500.0   # cm^-1  (imaginary correction mode)


class HopsSimulator:
    """
    Unified quantum dynamics simulator backed by MesoHOPS.

    Parameters
    ----------
    hamiltonian : ndarray, shape (N, N)
        System Hamiltonian in cm^-1.
    temperature : float
        Temperature in Kelvin.
    use_mesohops : bool
        Use MesoHOPS when available (default True).
    max_hierarchy : int
        Hierarchy truncation depth MAXHIER.
    k_matsubara : int
        Number of Matsubara modes (0 = none).
    reorganization_energy : float
        Bath reorganisation energy λ in cm^-1.
    drude_cutoff : float
        Drude-Lorentz cutoff γ in cm^-1.
    """

    def __init__(
        self,
        hamiltonian: NDArray,
        temperature: float = DEFAULT_TEMPERATURE,
        use_mesohops: bool = True,
        max_hierarchy: int = DEFAULT_MAX_HIERARCHY,
        k_matsubara: int = DEFAULT_N_MATSUBARA,
        reorganization_energy: float = DEFAULT_REORGANIZATION_ENERGY,
        drude_cutoff: float = DEFAULT_DRUDE_CUTOFF,
        **kwargs: Any,
    ):
        self.hamiltonian = np.array(hamiltonian, dtype=np.complex128)
        self.temperature = temperature
        self.max_hierarchy = max_hierarchy
        self.k_matsubara = k_matsubara
        self.reorganization_energy = reorganization_energy
        self.drude_cutoff = drude_cutoff
        self.use_pt_hops = kwargs.pop("use_pt_hops", False)
        self.use_sbd = kwargs.pop("use_sbd", False)
        self._system_param: Optional[Dict] = None
        self._fallback: Optional[Any] = None

        self.use_mesohops = MESOHOPS_AVAILABLE and use_mesohops
        if self.use_mesohops:
            self._build_system_param(**kwargs)
        if not self.use_mesohops:
            self._init_fallback()

    # ── System parameter construction ─────────────────────────────────────────

    def _build_system_param(self, **kwargs: Any) -> None:
        """Build the system_param dict in the format MesoHOPS expects."""
        n = self.hamiltonian.shape[0]

        # Shift Hamiltonian to avoid large absolute energies (numerical stability)
        E_mean = np.mean(np.diag(self.hamiltonian).real)
        H = self.hamiltonian - E_mean * np.eye(n, dtype=np.complex128)

        # Bath correlation function: Drude-Lorentz exponential decomposition
        # bcf_convert_dl_to_exp(lambda_dl, gamma_dl, temp, k_matsubara=0)
        # Returns a flat list: [g0, w0, g1, w1, ...]
        gw_flat = bcf_convert_dl_to_exp(
            self.reorganization_energy,
            self.drude_cutoff,
            self.temperature,
            self.k_matsubara,
        )
        # Pair up into [[g0, w0], [g1, w1], ...]
        dl_pairs = [[gw_flat[i], gw_flat[i + 1]] for i in range(0, len(gw_flat), 2)]

        # Build L-operators (site-projection operators)
        lop_list = []
        for i in range(n):
            L = np.zeros((n, n), dtype=np.float64)
            L[i, i] = 1.0
            lop_list.append(sp.coo_matrix(L))

        # Build GW_SYSBATH and L_HIER / L_NOISE1 (one entry per mode per site)
        gw_sysbath: list = []
        l_hier: list = []
        l_noise: list = []

        for i in range(n):
            for g, w in dl_pairs:
                gw_sysbath.append([g, w])
                l_hier.append(lop_list[i])
                l_noise.append(lop_list[i])
            # Markovian correction: cancels Im(g_0) at t=0
            g0, _ = dl_pairs[0]
            gw_sysbath.append([-1j * np.imag(g0), DEFAULT_MARKOVIAN_CUTOFF])
            l_hier.append(lop_list[i])
            l_noise.append(lop_list[i])

        # Optional underdamped vibronic modes
        vib_freqs = kwargs.get("vibronic_frequencies", np.array([]))
        vib_hr = kwargs.get("huang_rhys_factors", np.array([]))
        vib_damp = kwargs.get("vibronic_damping", np.array([]))
        if _HAS_UD and len(vib_freqs):
            from mesohops.util.bath_corr_functions import bcf_convert_dl_ud_to_exp
            for freq, hr, damp in zip(vib_freqs, vib_hr, vib_damp):
                lam_vib = hr * freq
                ud_flat = bcf_convert_dl_ud_to_exp(lam_vib, damp, freq, self.temperature)
                ud_pairs = [[ud_flat[i], ud_flat[i + 1]] for i in range(0, len(ud_flat), 2)]
                for i in range(n):
                    for g, w in ud_pairs:
                        gw_sysbath.append([g, w])
                        l_hier.append(lop_list[i])
                        l_noise.append(lop_list[i])

        # NOTE: PULSE_PARAMS is NOT a valid MesoHOPS system_param key — omitted.
        self._system_param = {
            "HAMILTONIAN": H,
            "GW_SYSBATH": gw_sysbath,
            "L_HIER": l_hier,
            "L_NOISE1": l_noise,
            "ALPHA_NOISE1": bcf_exp,       # from mesohops.trajectory.exp_noise
            "PARAM_NOISE1": gw_sysbath,
        }

    # ── Fallback ──────────────────────────────────────────────────────────────

    def _init_fallback(self) -> None:
        if SimpleQuantumDynamicsSimulator is not None:
            try:
                self._fallback = SimpleQuantumDynamicsSimulator(
                    self.hamiltonian, temperature=self.temperature
                )
                return
            except Exception:
                pass
        self._fallback = None

    # ── Public API ────────────────────────────────────────────────────────────

    def simulate_dynamics(
        self,
        time_points: NDArray,
        initial_state: Optional[NDArray] = None,
        seed: int = 0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Run quantum dynamics simulation.

        Parameters
        ----------
        time_points : ndarray
            Time grid in fs.
        initial_state : ndarray, optional
            Initial wavefunction (complex, length N). Defaults to site-0 excitation.
        seed : int
            RNG seed for noise trajectory.

        Returns
        -------
        dict with keys: t_axis, populations, coherences, simulator
        """
        n = self.hamiltonian.shape[0]
        if initial_state is None:
            initial_state = np.zeros(n, dtype=complex)
            initial_state[0] = 1.0

        if self.use_mesohops and self._system_param is not None:
            try:
                return self._run_mesohops(time_points, initial_state, seed=seed, **kwargs)
            except Exception as e:
                print(f"[HopsSimulator] MesoHOPS failed ({e}), using fallback.")

        if self._fallback is not None:
            return self._fallback.simulate_dynamics(
                time_points=time_points, initial_state=initial_state
            )
        raise RuntimeError("No simulator available.")

    def _run_mesohops(
        self,
        time_points: NDArray,
        initial_state: NDArray,
        seed: int = 0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Run a single MesoHOPS trajectory and return populations."""
        t_max = float(np.max(time_points))
        dt = float(time_points[1] - time_points[0]) if len(time_points) > 1 else 1.0

        # MesoHOPS constraint: tau_step = tau * integrator_step (0.5) must be an
        # integer multiple of noise TAU, and tau >= TAU.
        # Simplest valid choice: TAU = dt * 0.5  →  tau_step = dt*0.5 = 1×TAU.
        tau = dt
        noise_tau = dt * 0.5   # tau_step = tau * 0.5 = 1 × noise_tau ✓
        noise_param = {
            "SEED": seed,
            "MODEL": "FFT_FILTER",
            "TLEN": t_max + 2.0 * self.drude_cutoff,  # buffer ≥ reorganisation time
            "TAU": noise_tau,
        }
        eom_param = {"EQUATION_OF_MOTION": "NORMALIZED NONLINEAR"}
        hierarchy_param = {"MAXHIER": self.max_hierarchy}
        integration_param = {"INTEGRATOR": "RUNGE_KUTTA"}
        # Request storage of wavefunction and time axis
        storage_param = {"psi_traj": True, "t_axis": True}

        hops = HopsTrajectory(
            self._system_param,
            noise_param=noise_param,
            eom_param=eom_param,
            hierarchy_param=hierarchy_param,
            integration_param=integration_param,
            storage_param=storage_param,
        )

        psi_0 = np.array(initial_state, dtype=complex)
        psi_0 = psi_0 / np.linalg.norm(psi_0)
        hops.initialize(psi_0)
        # t_step = tau (1× multiple of TAU — always valid)
        hops.propagate(t_max, tau)

        # Access storage via dict-style indexing (hops.storage['key'])
        psi_traj = np.array(hops.storage["psi_traj"])   # shape (T, N)
        t_axis = np.array(hops.storage["t_axis"], dtype=float)

        n = self.hamiltonian.shape[0]
        populations = np.abs(psi_traj[:, :n]) ** 2
        # Coherence: L1 norm of off-diagonal density matrix elements
        coherences = np.array([
            sum(abs(psi_traj[t, i] * np.conj(psi_traj[t, j]))
                for i in range(n) for j in range(n) if i != j)
            for t in range(len(t_axis))
        ])

        return {
            "t_axis": t_axis,
            "populations": populations,
            "coherences": coherences,
            "simulator": "MesoHOPS",
        }

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def is_using_mesohops(self) -> bool:
        return self.use_mesohops and self._system_param is not None

    @property
    def simulator_type(self) -> str:
        if self.is_using_mesohops:
            tags = []
            if self.use_pt_hops:
                tags.append("PT")
            if self.use_sbd:
                tags.append("SBD")
            return "MesoHOPS" + (f" ({'+'.join(tags)})" if tags else "")
        return "Fallback" if self._fallback else "None"
