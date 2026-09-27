FMO_NSITES = 8
N_DIM_DRESSED = FMO_NSITES + 1
PLASMON_INDEX = FMO_NSITES

FMO_SITE_ENERGIES_CM = [280, 420, 0, 110, 270, 500, 310, 200]

FMO_COUPLINGS_CM: dict[tuple[int, int], float] = {
    (0, 1): -87.7,
    (0, 2): 5.5,
    (0, 3): -5.9,
    (0, 4): 6.7,
    (0, 5): -13.7,
    (0, 6): -9.9,
    (0, 7): 21.0,
    (1, 2): 30.0,
    (1, 3): 8.2,
    (1, 4): 0.7,
    (1, 5): 11.8,
    (1, 6): 4.3,
    (1, 7): -4.2,
    (2, 3): -53.5,
    (2, 4): -2.2,
    (2, 5): -9.6,
    (2, 6): 6.0,
    (2, 7): 0.6,
    (3, 4): -70.7,
    (3, 5): -17.0,
    (3, 6): -63.3,
    (3, 7): -1.3,
    (4, 5): 81.1,
    (4, 6): -1.3,
    (4, 7): 1.5,
    (5, 6): 39.7,
    (5, 7): -7.9,
    (6, 7): 12.0,
}

TRAPPING_SITES = [2, 3]

NPoM_MAX_PLASMON_COUPLING_CM = 1000.0
NPoM_REFERENCE_MODE_VOLUME_NM3 = 1.0
NPoM_REFERENCE_COUPLING_CM = 120.0
NPoM_VOLUME_GUARDRAIL_THRESHOLD = 1e-6

SERS_ENHANCEMENT_FACTOR = 100.0
SERS_VIBRONIC_SITES_180 = [2, 3]
SERS_VIBRONIC_SITES_740 = [0, 1]

FAO56_SAT_VAPOR_COEFF = 0.6108
FAO56_PSYCHROMETRIC_CONSTANT = 0.066
FAO56_VAPOR_SLOPE_NUM = 4098.0
FAO56_VAPOR_TEMP_OFFSET = 237.3

LCA_MAX_PHYSICAL_YIELD = 0.95
# Carbon intensity of water pumping: 0.298 kg CO2e per m³ (= per 1000 L)
LCA_WATER_PUMPING_CARBON_FACTOR = 0.000298  # per LITER
LCA_FOOTPRINT_A = 8.5
LCA_FOOTPRINT_B = 5.0
LCA_FOOTPRINT_C = 0.0

QKD_QBER_THRESHOLD = 0.11
QKD_SAMPLE_DIVISOR = 4
# SI S6: parameter estimation discloses >= 128 bits at N = 256 (f_sample >= 0.5)
QKD_MIN_SAMPLE_SIZE = 128
QKD_MAX_SAMPLE_SIZE = 128

GQD_STERN_VOLMER_CONSTANT = 0.05
GQD_PESTICIDE_REDSHIFT_SENSITIVITY = 0.1
GQD_MOISTURE_SENSITIVITY = 1.2
GQD_CORE_SHELL_BASELINE_NM = 620.0
SOIL_MOISTURE_DRY_THRESHOLD = 20.0
STRESS_SEVERE_THRESHOLD = 10.0
STRESS_NONE_THRESHOLD = 40.0
IRRIGATION_SEVERE_VALVE = 15.0
IRRIGATION_MODERATE_VALVE = 5.0

# Solver
K_MATSUBARA = 2
SOLVER_DETERMINISTIC_SEED = 0

# QA/QC
FLOQUET_EVAL_TIME_PS = 1.0
FLOQUET_SITES = [0, 5]
MAX_TRAPPING_YIELD = 0.98  # Physical maximum (FMO baseline Φ_FT = 0.98)
# Φ_FT = Γ_RC × ∫(P3+P4)dt with NO prefactor (canon 2026-09-23; Γ_RC = 0.15 fs⁻¹
# effective, i.e. τ_trap ≈ 6.7 fs in the dressed-model units).
BASELINE_TRANSMISSION = 0.8
# Optical limiting of the 750/820 nm passbands: T = T0 / (1 + I / I_sat).
# The picocavity saturates under strong drive (NOT optomechanically induced
# transparency): at I = 1000 W/m2, T = T0 / 2.25 = 0.444 T0 (44 %).
OMIT_I_SAT_W_M2 = 800.0
# eV -> cm^-1 conversion (CODATA/IAU: 1 eV = 8065.54429 cm^-1)
EV_TO_CM1 = 8065.54429
PLASMON_COUPLING_SITES = [0, 5]

# Irrigation / Greenhouse
# 1 mm of water standing over 1 m2 = 1 L/m2 (mm -> L/m2 is x1, NOT x1000).
MM_TO_LITER_PER_M2 = 1.0
FAO56_ABSOLUTE_ZERO_C = -273.15

# Stability audit bounds
TRACE_UPPER_BOUND = 1.0001
TRACE_LOWER_BOUND = -1e-5
POSITIVITY_TOLERANCE = -1e-5

# FAO-56 Penman-Monteith coefficients
# Argument of the ET model is the 24-h MEAN global horizontal irradiance (W/m2).
FAO56_W_TO_MJ_CONVERSION = 0.0864
FAO56_VAPOR_SLOPE_EMP = 17.27
# Standard FAO-56 aerodynamic wind term (u2, m/s): no empirical rescaling.
FAO56_WIND_COEFF = 1.0
# Net radiation: Rn = 0.77 * Rs - 1.9 (MJ/m2/day; FAO-56 default albedo 0.23,
# net longwave loss 1.9 MJ/m2/day). Panel soiling/canopy shading are NOT part
# of this broadband energy balance.
FAO56_NET_SHORTWAVE_FRACTION = 0.77
FAO56_NET_LONGWAVE_LOSS = 1.9  # MJ/m2/day
FAO56_RADIATION_FACTOR = 0.408
FAO56_TEMP_NUMERATOR = 900.0
FAO56_WIND_TERM_COEFF = 0.34

# Instantaneous peak -> 24-h mean irradiance conversion for the ET path:
#     daily_mean_W_m2 = peak_W_m2 * PEAK_SUN_HOURS / 24
# equivalent full-load hours: daily_kWh_m2 = (peak_W/1000) * PEAK_SUN_HOURS,
# calibrated so the 600 W/m2 reference irradiance integrates to 5.76 kWh/m2/day
# (site solar-resource assumption for the Western Highlands) = 240 W/m2 daily mean. Hence 9.6 = 5.76 / 0.6, and the published
# 4.505 / 3.246 mm/day pair (open / shield) is reproduced from a 600 W/m2 peak.
PEAK_SUN_HOURS = 9.6

# Conversion factors
G_TO_KG = 1000.0

# Quantum fertiliser biostimulation (Axe 15)
QUANTUM_FERTILIZER_BOOST = 1.08

# CLI defaults
DEFAULT_SOLAR_FLUX_W_M2 = 950.0

# QKD
QKD_SIFTING_OVERHEAD = 4

# SERS diagnostic
SERS_MODE_1145_CM = 1145
