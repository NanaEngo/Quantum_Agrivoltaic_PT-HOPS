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


def create_fmo_hamiltonian(include_reaction_center: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """
    Create FMO complex Hamiltonian matrix.

    The Fenna-Matthews-Olsen (FMO) complex is modeled as an excitonic system
    with the Hamiltonian H = Σᵢ εᵢ |i⟩⟨i| + Σᵢⱼ Jᵢⱼ |i⟩⟨j|.

    Parameters
    ----------
    include_reaction_center : bool
        If True, use 8-site model (includes reaction center pigment).
        If False, use the standard 7-site model.

    Returns
    -------
    H : np.ndarray
        Hamiltonian matrix (n_sites × n_sites) in cm⁻¹. Hermitian by construction.
    site_energies : np.ndarray
        Site energies array (n_sites,) in cm⁻¹.
    """
    site_energies = FMO_SITE_ENERGIES_8 if include_reaction_center else FMO_SITE_ENERGIES_7
    n_sites = len(site_energies)

    # Use np.diag for clean diagonal initialization (server best practice)
    H = np.diag(site_energies.copy())

    for (i, j), coupling in FMO_COUPLINGS.items():
        if i < n_sites and j < n_sites:
            H[i, j] = coupling
            H[j, i] = coupling  # Hermitian symmetry

    return H, site_energies


def spectral_density_drude_lorentz(
    omega: np.ndarray,
    lambda_reorg: float,
    gamma: float,
    temperature: float,
) -> np.ndarray:
    """
    Compute the symmetrised Drude-Lorentz spectral density J(ω).

    Parameters
    ----------
    omega : np.ndarray
        Frequency array in cm⁻¹ (may include negative values for emission).
    lambda_reorg : float
        Reorganisation energy λ_D in cm⁻¹ (canonical value: 35 cm⁻¹).
    gamma : float
        Bath relaxation rate γ_D in cm⁻¹ (canonical value: 50 cm⁻¹).
    temperature : float
        Temperature in Kelvin (canonical value: 295 K).

    Returns
    -------
    J : np.ndarray
        Symmetrised spectral density evaluated at each frequency in ``omega``.
    """
    kT = KB_CM_K * temperature
    J = 2.0 * lambda_reorg * gamma * omega / (omega**2 + gamma**2)
    # Bose-Einstein occupancy (regularised to avoid division-by-zero at ω=0)
    n_th = 1.0 / (np.exp(np.maximum(np.abs(omega), 1e-10) / kT) - 1.0)
    # Detailed balance: absorption (+ω) → (1 + n_th), emission (−ω) → n_th − 1
    J *= np.where(omega >= 0, 1.0 + n_th, n_th - 1.0)
    return J
