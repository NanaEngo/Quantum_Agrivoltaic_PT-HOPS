"""
Simple quantum dynamics simulator for educational purposes.
This provides a minimal fallback that doesn't require MesoHOPS.
"""

import logging
from typing import Any, Dict, Optional

import numpy as np
import scipy.linalg as la
from src.core.constants import (
    DEFAULT_MAX_TIME,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIME_POINTS,
    TIME_PHASE_CONVERSION,
)

logger = logging.getLogger(__name__)


class SimpleQuantumDynamicsSimulator:
    """
    A simple quantum dynamics simulator that doesn't require MesoHOPS.

    This uses a basic Schrodinger equation solver to simulate closed quantum 
    dynamics (unitary evolution). It is not as accurate as the MesoHOPS 
    implementation for open quantum systems, but serves as a fast, exact fallback
    for isolated systems without a bath.

    Parameters
    ----------
    hamiltonian : np.ndarray
        The system Hamiltonian matrix in cm^-1. Must be square.
    temperature : float, optional
        System temperature in Kelvin, by default DEFAULT_TEMPERATURE.
        Note: Temperature has no effect on closed-system dynamics but is 
        kept for API compatibility.
    """

    def __init__(self, hamiltonian, temperature=DEFAULT_TEMPERATURE):
        self.hamiltonian = np.array(hamiltonian, dtype=complex)
        if self.hamiltonian.ndim != 2 or self.hamiltonian.shape[0] != self.hamiltonian.shape[1]:
            raise ValueError(f"Hamiltonian must be square, got shape {self.hamiltonian.shape}")
        self.n_sites = self.hamiltonian.shape[0]
        if self.n_sites == 0:
            raise ValueError("Hamiltonian must have at least 1 site")
        self.temperature = temperature

        # Shift Hamiltonian to improve numerical stability
        self.energy_shift = np.mean(np.diag(self.hamiltonian).real)
        self.h_shifted = self.hamiltonian - self.energy_shift * np.eye(self.n_sites)

        logger.info(f"Simple quantum simulator initialized with {self.n_sites} sites")

    def simulate_dynamics(
        self,
        time_points: Optional[np.ndarray] = None,
        initial_state: Optional[np.ndarray] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Simulate quantum dynamics using the time-dependent Schrödinger equation.

        Integrates the equation iħ d/dt |ψ⟩ = H |ψ⟩ analytically via matrix
        exponentiation: |ψ(t)⟩ = exp(-iHt) |ψ(0)⟩.
        Note: Because this is pure-state propagation, entropy is always 0 
        (no environmental decoherence).

        Parameters
        ----------
        time_points : np.ndarray, optional
            Array of time points in femtoseconds to evaluate the state at.
            If None, defaults to a linear space from 0 to DEFAULT_MAX_TIME.
        initial_state : np.ndarray, optional
            The initial quantum state vector |ψ(0)⟩.
            If None, defaults to an excitation localized on the first site.
        **kwargs : Any
            Additional keyword arguments (ignored, kept for API compatibility).

        Returns
        -------
        dict[str, Any]
            Dictionary containing the simulation results:
            - 't_axis' : The time points evaluated.
            - 'populations' : The site populations over time.
            - 'coherences' : L1 norm of the coherences.
            - 'qfi' : Quantum Fisher Information.
            - 'entropy' : Von Neumann entropy (always 0 here).
            - and other metric arrays (zeros/ones for pure states).
        """
        if time_points is None:
            time_points = np.linspace(0, DEFAULT_MAX_TIME, DEFAULT_TIME_POINTS)
        time_points = np.asarray(time_points)
        if time_points.ndim != 1:
            raise ValueError(f"time_points must be 1-D, got shape {time_points.shape}")

        if initial_state is None:
            initial_state = np.zeros(self.n_sites, dtype=complex)
            initial_state[0] = 1.0
        initial_state = np.array(initial_state, dtype=complex).flatten()
        if initial_state.shape[0] != self.n_sites:
            raise ValueError(
                f"initial_state length {initial_state.shape[0]} != n_sites {self.n_sites}"
            )

        n_times = len(time_points)
        populations = np.zeros((n_times, self.n_sites))
        coherences = np.zeros(n_times)
        qfi_values = np.zeros(n_times)
        entropy_values = np.zeros(n_times)  # always 0 for pure-state propagation

        # Hoist eigendecomposition — O(N³) once instead of O(N³·T)
        eigenvals, eigenvecs = np.linalg.eigh(self.h_shifted)
        # Precompute projection of initial state onto eigenbasis
        c0 = eigenvecs.T.conj() @ initial_state  # shape (n_sites,)

        for i, t in enumerate(time_points):
            # time_factor: (cm⁻¹)·fs → dimensionless via ħ=1/(2πc) in cm⁻¹·fs units
            time_factor = t * TIME_PHASE_CONVERSION
            exp_evals = np.exp(-1j * eigenvals * time_factor)
            psi_t = eigenvecs @ (exp_evals * c0)
            rho_t = np.outer(psi_t, psi_t.conj())
            populations[i, :] = np.real(np.diag(rho_t))
            # Coherence: L1 norm of off-diagonal elements (vectorised)
            coherences[i] = float(np.sum(np.abs(rho_t)) - np.sum(np.abs(np.diag(rho_t))))
            # QFI for pure state: 4·Var_ψ(H) = 4(⟨H²⟩-⟨H⟩²)
            H_psi = self.h_shifted @ psi_t
            exp_H = np.real(np.vdot(psi_t, H_psi))
            exp_H2 = np.real(np.vdot(psi_t, self.h_shifted @ H_psi))
            qfi_values[i] = 4.0 * max(0.0, exp_H2 - exp_H ** 2)
            # entropy_values[i] = 0 always for pure state — left as zeros

        return {
            "t_axis": time_points,
            "populations": populations,
            "coherences": coherences,
            "qfi": qfi_values,
            "entropy": entropy_values,
            "bipartite_ent": np.zeros(n_times),
            "multipartite_ent": np.zeros(n_times),
            "pairwise_concurrence": np.zeros(n_times),
            "discord": np.zeros(n_times),
            "fidelity": np.ones(n_times),
            "mandel_q": np.zeros(n_times),
            "simulator": "Simple Quantum Simulator",
        }
