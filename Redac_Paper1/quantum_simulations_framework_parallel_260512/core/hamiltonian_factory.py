"""
Hamiltonian Factory for Quantum Agrivoltaics.

This module provides automated generation of exciton-vibronic Hamiltonians for 
light-harvesting complexes. It primarily implements the Fenna-Matthews-Olsen (FMO) 
complex based on the Adolphs-Renger parameters. It also includes 
utilities for evaluating Drude-Lorentz spectral densities with full 
Bose-Einstein thermal statistics.
"""

import numpy as np

try:
    from src.core.constants import FMO_SITE_ENERGIES_7, FMO_SITE_ENERGIES_8, FMO_COUPLINGS, KB_CM_K
except ImportError:
    from .constants import FMO_SITE_ENERGIES_7, FMO_SITE_ENERGIES_8, FMO_COUPLINGS, KB_CM_K


def create_fmo_hamiltonian(include_reaction_center: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """
    Construct the excitonic Hamiltonian for the FMO complex.

    The Fenna-Matthews-Olsen (FMO) complex is modeled as an excitonic system 
    within the tight-binding approximation:
    
        H_sys = Σᵢ εᵢ |i⟩⟨i| + Σᵢⱼ Jᵢⱼ (|i⟩⟨j| + |j⟩⟨i|)

    Parameters
    ----------
    include_reaction_center : bool, optional
        Whether to include the 8th pigment (BChl 8) which couples to the 
        reaction center. If True, returns an 8x8 matrix; otherwise, returns 
        the standard 7x7 matrix. Default is False.

    Returns
    -------
    H : np.ndarray
        The system Hamiltonian matrix in cm⁻¹. Hermitian by construction.
    site_energies : np.ndarray
        The diagonal site energies εᵢ in cm⁻¹.

    Notes
    -----
    The parameters (site energies and couplings) are based on the 
    Adolphs & Renger (2006) structure-based model (DOI: 10.1529/biophysj.105.079483).
    Pigment 3 is typically the lowest energy site, serving as the 'sink' 
    towards the reaction center.
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
