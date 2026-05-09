"""
Hamiltonian Factory for Quantum Agrivoltaics.

This module provides functions to create system Hamiltonians, specifically the
Fenna-Matthews-Olsen (FMO) complex, and helper functions for spectral densities.
All FMO parameters are read from constants.py — the single source of truth.
"""

import numpy as np

try:
    from core.constants import FMO_SITE_ENERGIES_7, FMO_SITE_ENERGIES_8, FMO_COUPLINGS, KB_CM_K
except ImportError:
    from .constants import FMO_SITE_ENERGIES_7, FMO_SITE_ENERGIES_8, FMO_COUPLINGS, KB_CM_K


def create_fmo_hamiltonian(include_reaction_center=False):
    """
    Create the FMO Hamiltonian matrix based on standard parameters from the literature.

    Mathematical Framework:
    The Fenna-Matthews-Olsen (FMO) complex is modeled as an excitonic system
    with the Hamiltonian:

    H_FMO = Σᵢ εᵢ |i⟩⟨i| + Σᵢⱼ Jᵢⱼ |i⟩⟨j|

    Parameters:
    include_reaction_center (bool): Whether to include the reaction center state

    Returns:
    H (2D array): Hamiltonian matrix in units of cm^-1
    site_energies (1D array): Site energies in cm^-1
    """
    site_energies = FMO_SITE_ENERGIES_8 if include_reaction_center else FMO_SITE_ENERGIES_7
    n_sites = len(site_energies)
    H = np.zeros((n_sites, n_sites))
    np.fill_diagonal(H, site_energies)

    for (i, j), value in FMO_COUPLINGS.items():
        if i < n_sites and j < n_sites:
            H[i, j] = value
            H[j, i] = value  # Ensure Hermitian

    return H, site_energies


def spectral_density_drude_lorentz(omega, lambda_reorg, gamma, temperature):
    """Calculate Drude-Lorentz spectral density."""
    kT = KB_CM_K * temperature
    J = 2 * lambda_reorg * gamma * omega / (omega**2 + gamma**2)
    n_th = 1.0 / (np.exp(np.maximum(np.abs(omega), 1e-10) / kT) - 1)
    # Element-wise: emission side (omega<0) uses n_th-1, absorption side uses 1+n_th
    J *= np.where(omega >= 0, 1.0 + n_th, n_th - 1.0)
    return J
