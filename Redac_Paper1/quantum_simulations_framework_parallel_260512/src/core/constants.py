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
LIGHT_SPEED_CMS: Final[float] = 2.99792458e10  # cm/s

# =============================================================================
# HIERARCHY / SBD PARAMETERS
# =============================================================================
DEFAULT_SBD_BUNDLES: Final[int] = 6  # SBD bundles per site (SI mandate: all production runs use SBD)

# Dephasing rate (used by sensitivity_analyzer)
DEFAULT_DEPHASING_RATE: Final[float] = 0.01  # cm^-1/fs (phenomenological dephasing)

# Number of trajectories
DEFAULT_N_TRAJ: Final[int] = 100  # ensemble trajectories (parameters.yaml: n_traj=100)

# Markovian limit test: high Drude cutoff to approach Markovian regime
MARKOVIAN_DRUDE_CUTOFF: Final[float] = 500.0  # cm^-1 (gamma >> J → Markovian)

# FFT noise buffer for MesoHOPS trajectory stability
FFT_NOISE_BUFFER_FS: Final[float] = 50.0  # fs buffer added to TLEN for FFT_FILTER stability

# Static disorder standard deviation (parameters.yaml: disorder_sigma_cm)
DEFAULT_DISORDER_SIGMA: Final[float] = 50.0  # cm^-1 (Gaussian diagonal disorder)

# Time
DEFAULT_TIME_POINTS: Final[int] = 501   # 0–1000 fs at step=2 fs → linspace(0,1000,501)
DEFAULT_TIME_STEP: Final[float] = 1.0   # femtoseconds (1.0 fs recommended for stability with 12-mode bath)
DEFAULT_MAX_TIME: Final[float] = 1000.0  # femtoseconds
DEFAULT_TIME_LONG: Final[float] = 5000.0 # femtoseconds for thermalization checks

# Frequency to phase conversion (2*pi*c where c is in cm/fs)
# c = 2.99792458e10 cm/s = 0.0299792458 cm/fs
# 2*pi*c = 0.188365156
FREQ_TO_PHASE: Final[float] = 0.188365156

# =============================================================================
# MESOHOPS SIMULATION PARAMETERS
# =============================================================================

DEFAULT_MAX_HIERARCHY: Final[int] = 8  # Capped at L=8 to prevent OOM on 128GB nodes
DEFAULT_N_MATSUBARA: Final[int] = 2   # K=2: converged at T=295 K (ν₁≈1300 cm⁻¹ >> γ_D=50 cm⁻¹)

# Ensemble parameters
DEFAULT_N_TRAJ_SWEEP: Final[int] = 10
DEFAULT_N_DISORDER: Final[int] = 100

# =============================================================================
# SPECTRAL FILTER DEFAULTS (Eq. 3 in Manuscript)
# =============================================================================

FILTER_BAND_CENTERS_NM: Final[list] = [750.0, 820.0]
FILTER_BANDWIDTH_CM: Final[float] = 100.0
FILTER_WEIGHTS: Final[list] = [1.0, 1.0]

# =============================================================================
# MESOHOPS INTEGRATOR SPECIFICATIONS
# =============================================================================

MESOHOPS_SEED: Final[int] = 42
MESOHOPS_EARLY_STEPS: Final[int] = 5
MESOHOPS_INCHWORM_CAP: Final[int] = 5

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
DEFAULT_VIBRONIC_DAMPING_VAL: Final[float] = 10.0

# =============================================================================
# AGRIVOLTAIC SYSTEM PARAMETERS
# =============================================================================

DEFAULT_N_OPV_SITES: Final[int] = 4
DEFAULT_N_PSU_SITES: Final[int] = 7

# Default performance metrics
DEFAULT_PCE: Final[float] = 0.15  # Power conversion efficiency (15%)
DEFAULT_ETR: Final[float] = 0.25  # Electron transport rate
DEFAULT_FILL_FACTOR_OPV: Final[float] = 0.75
DEFAULT_CONVERSION_FACTOR_OPV: Final[float] = 0.05
PCE_MAX_LIMIT: Final[float] = 0.25

# Photo-efficiency Thresholds
PSU_BLUE_MIN: Final[float] = 400.0
PSU_BLUE_MAX: Final[float] = 500.0
PSU_RED_MIN: Final[float] = 600.0
PSU_RED_MAX: Final[float] = 700.0
PSU_GREEN_MIN: Final[float] = 500.0
PSU_GREEN_MAX: Final[float] = 600.0

# ETR Calculation Thresholds
ETR_BASE: Final[float] = 0.85
ETR_SCALE: Final[float] = 0.1
ETR_SAT_PAR: Final[float] = 10.0
ETR_MIN: Final[float] = 0.05
ETR_MAX: Final[float] = 0.98
DEFAULT_OPV_VOLTAGE: Final[float] = 0.85 # Volts

# Solar Spectrum Limits
SOLAR_LAMBDA_MIN: Final[float] = 300.0  # nm
SOLAR_LAMBDA_MAX: Final[float] = 1100.0 # nm
SOLAR_TOTAL_IRRADIANCE: Final[float] = 100.0 # mW/cm^2 (AM1.5G)

# Environmental Reference Values
ENVIRONMENTAL_T_REF: Final[float] = 298.15  # Kelvin (25°C STC)
ENVIRONMENTAL_HUMIDITY_OPT: Final[float] = 0.45  # Optimal relative humidity
ENVIRONMENTAL_DUST_SAT_FACTOR: Final[float] = 0.3  # Max efficiency loss from dust saturation

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
MEMORY_FRACTION_LIMIT: Final[float] = 0.66  # Use at most 2/3 of available RAM
BASE_TRAJ_MEMORY_GB: Final[float] = 6.0  # Reference memory for L=8, K=2 production
MIN_TRAJ_MEMORY_GB: Final[float] = 0.5   # Minimum floor for memory estimation
MAX_N_JOBS: Final[int] = 1               # Hard cap: 54 GB/traj × n_jobs must fit in 128 GB RAM

# =============================================================================
# FILE PATHS
# =============================================================================

DEFAULT_FIGURES_DIR: Final[str] = "../Graphics/"
DEFAULT_DATA_DIR: Final[str] = "../simulation_data/"
DEFAULT_DATA_OUTPUT_DIR: Final[str] = "./data_output/"
DEFAULT_SYSTEM_LIFETIME: Final[int] = 25  # Years

# =============================================================================
# VISUALIZATION PARAMETERS
# =============================================================================

DEFAULT_DPI: Final[int] = 600  # High-resolution for JPCL publication
PREVIEW_DPI: Final[int] = 300  # Standard preview resolution

# =============================================================================
# ECO-DESIGN & SUSTAINABILITY THRESHOLDS
# =============================================================================

BDE_THRESHOLD_ECO: Final[float] = 300.0  # kJ/mol (Bond Dissociation Energy threshold)
OPV_ACTIVE_REGION_MIN: Final[float] = 300.0  # nm
OPV_ACTIVE_REGION_MAX: Final[float] = 700.0  # nm

# Eco-design targets
TARGET_BIODEGRADABILITY: Final[float] = 0.8
TARGET_LC50: Final[float] = 400.0
DEFAULT_MOLECULAR_WEIGHT: Final[float] = 500.0
DEFAULT_LC50: Final[float] = 500.0

# Reactivity descriptor reference values
REF_CHEMICAL_POTENTIAL: Final[float] = -4.0
REF_CHEMICAL_HARDNESS: Final[float] = 2.5
REF_ELECTROPHILICITY: Final[float] = 4.0
REF_FUKUI_NUC: Final[float] = 0.3
REF_FUKUI_ELEC: Final[float] = 0.2

# 2DES Spectroscopy constants
SPECTROSCOPY_LINEWIDTH_SCALE: Final[float] = 1.5
SPECTROSCOPY_CROSS_PEAK_AMP: Final[float] = 0.3

# Simulation sweep parameters
DEFAULT_TEMP_SWEEP: Final[tuple] = (285.0, 290.0, 295.0, 300.0, 305.0, 310.0)

# Biodegradability Index (B-index) weights
BINDEX_WEIGHT_NUC: Final[float] = 350.0
BINDEX_WEIGHT_ELEC: Final[float] = 300.0
BINDEX_WEIGHT_REACT: Final[float] = 2.0
BINDEX_WEIGHT_SIZE: Final[float] = 0.6
BINDEX_SIZE_DECAY: Final[float] = 2000.0

# Biodegradability Analyzer weights
BIO_WEIGHT_NUC: Final[float] = 0.3
BIO_WEIGHT_ELEC: Final[float] = 0.2
BIO_WEIGHT_DUAL: Final[float] = 0.2
BIO_WEIGHT_SOFTNESS: Final[float] = 0.15
BIO_WEIGHT_MAX_FUKUI: Final[float] = 0.15
BIO_SOFTNESS_SCALE: Final[float] = 10.0
BIO_MAX_FUKUI_SCALE: Final[float] = 5.0

# =============================================================================
# NUMERICAL PRECISION
# =============================================================================

MINIMAL_OMEGA: Final[float] = 1e-10  # Minimum frequency to avoid division by zero
CONVERGENCE_TOLERANCE: Final[float] = 1e-6
MAX_ITERATIONS: Final[int] = 10000
DEFAULT_SPECTRAL_RESOLUTION: Final[int] = 256
DEFAULT_W_BUFFER: Final[float] = 400.0
T_DECAY_DIAGONAL: Final[float] = 800.0  # fs (Reviewer 2 requested realistic broadening)
T_DECAY_CROSS: Final[float] = 450.0     # fs
GAUSSIAN_TBW_FS: Final[float] = 14700.0  # Gaussian Time-Bandwidth constant (cm^-1 * fs)
# Thresholds for validation
MAE_THRESHOLD: Final[float] = 1e-2
MAE_THRESHOLD_LOOSE: Final[float] = 0.05
TRACE_THRESHOLD: Final[float] = 0.5   # Threshold for single-trajectory trace preservation
POPS_REAL_THRESHOLD: Final[float] = 1e-12

# =============================================================================
# ENVIRONMENTAL COEFFICIENTS
# =============================================================================

# =============================================================================
# VALIDATION & AUDIT PARAMETERS
# =============================================================================

AUDIT_TIME_WINDOW: Final[float] = 100.0  # fs for convergence audit
DEFAULT_AUDIT_RESOLUTION: Final[int] = 201

# Sensitivity Analysis Parameters
SENSITIVITY_TEMP_OFFSET: Final[tuple] = (-20.0, 25.0)
SENSITIVITY_DEPHASING_FACTORS: Final[tuple] = (0.25, 2.5)
SENSITIVITY_CENTER_RANGE: Final[tuple] = (400.0, 700.0)
SENSITIVITY_WIDTH_RANGE: Final[tuple] = (20.0, 150.0)
SENSITIVITY_DUST_RANGE: Final[tuple] = (0.0, 5.0)
SENSITIVITY_POINTS_DEFAULT: Final[int] = 20

# =============================================================================
# ENVIRONMENTAL DYNAMICS THRESHOLDS
# =============================================================================

DEFAULT_DUST_RATE: Final[float] = 0.02
DEFAULT_DUST_SATURATION: Final[float] = 5.0
ENVIRONMENTAL_PRECIP_PROB: Final[float] = 0.05
ENVIRONMENTAL_PRECIP_CLEAN_FACTOR: Final[float] = 0.3 # Reduce dust to 30%
TEMP_COEFF_OPV: Final[float] = 0.004
TEMP_COEFF_PSU: Final[float] = 0.002
HUMIDITY_COEFF: Final[float] = 0.001
WIND_SPEED_FACTOR: Final[float] = 0.01

# Physics conversion
TIME_PHASE_CONVERSION: Final[float] = 0.0333564  # ps/cm (1/c) used in fallback simulator

# =============================================================================
# TECHNO-ECONOMIC & LCA PARAMETERS
# =============================================================================

# Spectral Optimization constants
OPV_MAX_EFFICIENCY: Final[float] = 0.20
OPV_UTILIZATION_FACTOR: Final[float] = 0.85
PSU_MAX_EFFICIENCY: Final[float] = 0.95
PSU_UTILIZATION_FACTOR: Final[float] = 0.92
PSU_MIN_EFFICIENCY: Final[float] = 0.05
FILTER_WIDTH_MIN: Final[float] = 5.0
FILTER_WIDTH_MAX: Final[float] = 100.0
SIMPLE_TRANS_PSU_FAVOR: Final[float] = 0.3
SIMPLE_TRANS_OPV_FAVOR: Final[float] = 0.4

# Agrivoltaic Coupling constants
DEFAULT_OPV_BANDGAP: Final[float] = 1.9
DEFAULT_OPV_ABSORPTION: Final[float] = 1.0
DEFAULT_N_OPV_SITES: Final[int] = 4
DEFAULT_OPV_SITE_ENERGIES: Final[tuple] = (1.9, 1.85, 1.95, 1.8)
DEFAULT_OPV_COUPLING_STRENGTH: Final[float] = 0.08
AGRI_SPECTRAL_COUPLING_STRENGTH: Final[float] = 0.03
PSU_BROADENING_EV: Final[float] = 0.03
HBAR_EV_FS: Final[float] = 0.6582119569  # hbar in eV*fs
OPV_RESPONSE_DECAY_WIDTH: Final[float] = 400.0
PSU_NIR_DECAY_RATE: Final[float] = 0.015
PSU_NIR_AMP: Final[float] = 0.35

# Economic parameters
DEFAULT_DISCOUNT_RATE: Final[float] = 0.05
# Note: DEFAULT_SYSTEM_LIFETIME is already defined above as 25
DEFAULT_ELECTRICITY_PRICE: Final[float] = 0.12  # $/kWh
DEFAULT_CROP_PRICE_KG: Final[float] = 1.50      # $/kg
DEFAULT_BASE_CROP_YIELD: Final[float] = 8000.0  # kg/ha
DEFAULT_CAPEX_KW: Final[float] = 1200.0         # $/kW
DEFAULT_OPEX_KW_YR: Final[float] = 15.0         # $/kW/yr
SOLAR_IRRADIANCE_ANNUAL: Final[float] = 1700.0  # kWh/m2/yr
SHADING_BOOST_FACTOR: Final[float] = 1.1        # Yield boost for water retention
HECTARE_TO_M2: Final[float] = 10000.0

# LCA parameters
LCA_MANUFACTURING_ENERGY_BASE: Final[float] = 1500.0  # MJ/m2
LCA_CARBON_INTENSITY_MFG: Final[float] = 0.05        # kg CO2eq/MJ
LCA_CARBON_INTENSITY_GRID: Final[float] = 0.5         # kg CO2eq/kWh
LCA_TOXICITY_FACTOR: Final[float] = 0.1
LCA_RESOURCE_DEPLETION_FACTOR: Final[float] = 0.05
LCA_MAINTENANCE_FACTOR: Final[float] = 0.02
LCA_CLEANING_FACTOR: Final[float] = 0.01
LCA_RECYCLING_RATE: Final[float] = 0.8
LCA_LANDFILL_IMPACT: Final[float] = 0.5
LCA_RECYCLING_ENERGY_FACTOR: Final[float] = 0.3
LCA_CARBON_CREDIT_RECYCLE: Final[float] = 2.0        # kg CO2eq/kg
MJ_TO_KWH: Final[float] = 0.2778
KWH_TO_MJ: Final[float] = 3.6

# Reference values for Silicon PV
SILICON_PV_CARBON: Final[float] = 40.0               # gCO2eq/kWh
SILICON_PV_EPBT: Final[float] = 2.0                  # years

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================
CPU_COUNT_FRACTION: Final[float] = 0.66
