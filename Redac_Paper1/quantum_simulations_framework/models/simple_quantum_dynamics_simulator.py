"""
Simple quantum dynamics simulator for educational purposes.
This provides a minimal fallback that doesn't require MesoHOPS.
"""

import logging

import numpy as np

logger = logging.getLogger(__name__)


class SimpleQuantumDynamicsSimulator:
    """
    A simple quantum dynamics simulator that doesn't require MesoHOPS.

    This uses a basic Schrodinger equation solver to simulate quantum dynamics.
    It's not as accurate as the MesoHOPS implementation but serves as a fallback.
    """

    def __init__(self, hamiltonian, temperature=295):
        self.hamiltonian = np.array(hamiltonian, dtype=complex)
        self.temperature = temperature
        self.n_sites = self.hamiltonian.shape[0]

        # Shift Hamiltonian to improve numerical stability
        self.energy_shift = np.mean(np.diag(self.hamiltonian).real)
        self.h_shifted = self.hamiltonian - self.energy_shift * np.eye(self.n_sites)

        logger.info(f"Simple quantum simulator initialized with {self.n_sites} sites")

    def simulate_dynamics(self, time_points=None, initial_state=None, dt=0.1):
        """
        Simulate quantum dynamics using the time-dependent Schrödinger equation.
        iħ d/dt |ψ⟩ = H |ψ⟩  →  |ψ(t)⟩ = exp(-iHt) |ψ(0)⟩
        Note: pure-state propagation — entropy is always 0 (no bath).
        """
        if time_points is None:
            time_points = np.linspace(0, 100, 101)
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
            time_factor = t * 0.0333564
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
