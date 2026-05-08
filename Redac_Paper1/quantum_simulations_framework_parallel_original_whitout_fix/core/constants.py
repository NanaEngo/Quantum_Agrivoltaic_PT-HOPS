"""
Physical and simulation constants for quantum agrivoltaic simulations.

This module contains all magic numbers and physical constants used throughout
the quantum agrivoltaics simulation framework.
"""

from typing import Final

import numpy as np

# =============================================================================
# PHYSICAL CONSTANTS
# =============================================================================

# Temperature
DEFAULT_TEMPERATURE: Final[float] = 295.0  # Kelvin (room temperature)
MIN_TEMPERATURE: Final[float] = 0.0  # Kelvin (absolute zero)
MAX_TEMPERATURE: Final[float] = 1000.0  # Kelvin (upper limit for simulations)

# Energy conversion
CM_TO_EV: Final[float] = 1.23984e-4  # cm^-1 to eV conversion factor
EV_TO_CM: Final[float] = 1.0 / CM_TO_EV  # eV to cm^-1 conversion factor
KB_CM_K: Final[float] = 0.695  # Boltzmann constant in cm^-1/K

# Time
DEFAULT_TIME_POINTS: Final[int] = 501   # 0–1000 fs at step=2 fs → linspace(0,1000,501)
DEFAULT_TIME_STEP: Final[float] = 2.0   # femtoseconds
DEFAULT_MAX_TIME: Final[float] = 1000.0  # femtoseconds

# =============================================================================
# MESOHOPS SIMULATION PARAMETERS
# =============================================================================

DEFAULT_MAX_HIERARCHY: Final[int] = 10  # L=10 mandate (JPCL revision)
DEFAULT_N_MATSUBARA: Final[int] = 2   # K=2: converged at T=295 K (ν₁≈1300 cm⁻¹ >> γ_D=50 cm⁻¹)

# =============================================================================
# FMO COMPLEX PARAMETERS
# =============================================================================

# Standard FMO site energies (cm^-1) - Adolphs & Renger 2006
# Reference: DOI: 10.1529/biophysj.105.079483
FMO_SITE_ENERGIES_7: Final[np.ndarray] = np.array([12410, 12530, 12210, 12320, 12480, 12630, 12440])

FMO_SITE_ENERGIES_8: Final[np.ndarray] = np.array(
    [12410, 12530, 12210, 12320, 12480, 12630, 12440, 11700]  # Last is RC
)

# FMO coupling parameters (cm^-1) - Adolphs & Renger 2006
FMO_COUPLINGS: Final[dict] = {
    (0, 1): -87.7,
    (0, 2): 5.5,
    (0, 3): -5.9,
    (0, 4): 6.7,
    (0, 5): -13.7,
    (0, 6): -9.9,
    (1, 2): 30.8,
    (1, 3): 8.2,
    (1, 4): 0.7,
    (1, 5): 11.8,
    (1, 6): 4.3,
    (2, 3): -53.5,
    (2, 4): -2.2,
    (2, 5): -9.6,
    (2, 6): 6.0,
    (3, 4): -70.7,
    (3, 5): -17.0,
    (3, 6): -63.3,
    (4, 5): 81.1,
    (4, 6): -1.3,
    (5, 6): 39.7,
}

# =============================================================================
# SPECTRAL DENSITY PARAMETERS (Kleinekathöfer/Coker Realistic Model)
# =============================================================================

# Drude-Lorentz (Solvent/Protein) parameters
DEFAULT_REORGANIZATION_ENERGY: Final[float] = 35.0  # cm^-1
DEFAULT_DRUDE_CUTOFF: Final[float] = 50.0  # cm^-1

# High-Fidelity Vibronic mode parameters (48-mode simplification per Coker 2013)
# Dominant frequencies (cm^-1) and corresponding Huang-Rhys factors
DEFAULT_VIBRONIC_FREQUENCIES: Final[np.ndarray] = np.array([
    180.0, 220.0, 280.0, 350.0, 520.0, 575.0, 720.0, 1050.0, 1185.0, 1220.0, 1350.0, 1500.0
])
DEFAULT_HUANG_RHYS_FACTORS: Final[np.ndarray] = np.array([
    0.05, 0.045, 0.03, 0.025, 0.02, 0.015, 0.01, 0.008, 0.005, 0.005, 0.004, 0.003
])
DEFAULT_VIBRONIC_DAMPING: Final[np.ndarray] = np.array([10.0] * 12)  # cm^-1

# =============================================================================
# AGRIVOLTAIC SYSTEM PARAMETERS
# =============================================================================

DEFAULT_N_OPV_SITES: Final[int] = 4
DEFAULT_N_PSU_SITES: Final[int] = 7

# Default performance metrics
DEFAULT_PCE: Final[float] = 0.15  # Power conversion efficiency (15%)
DEFAULT_ETR: Final[float] = 0.25  # Electron transport rate

# =============================================================================
# LASER PULSE SPECIFICATIONS (Reviewer 3 Compliance)
# =============================================================================

PULSE_TYPE: Final[str] = "Gaussian"  # Options: Gaussian, Lorentzian
PULSE_FWHM: Final[float] = 50.0  # fs
PULSE_RELATIVE_DELAY: Final[float] = 0.0  # fs (delay from photoexcitation)
PULSE_CENTRAL_FREQ: Final[float] = 12500.0  # cm^-1 (BChl Qy band)
PULSE_PHASE: Final[float] = 0.0  # radians
PULSE_AMPLITUDE: Final[float] = 0.05  # arbitrary amplitude units

# =============================================================================
# OPTIMIZATION PARAMETERS
# =============================================================================

DEFAULT_POPSIZE: Final[int] = 15
DEFAULT_MAXITER: Final[int] = 100
DEFAULT_WORKERS: Final[int] = -1  # Use all available cores

# =============================================================================
# FILE PATHS
# =============================================================================

DEFAULT_FIGURES_DIR: Final[str] = "../Graphics/"
DEFAULT_DATA_DIR: Final[str] = "../simulation_data/"
DEFAULT_DATA_OUTPUT_DIR: Final[str] = "./data_output/"

# =============================================================================
# NUMERICAL PRECISION
# =============================================================================

MINIMAL_OMEGA: Final[float] = 1e-10  # Minimum frequency to avoid division by zero
CONVERGENCE_TOLERANCE: Final[float] = 1e-6
MAX_ITERATIONS: Final[int] = 10000
