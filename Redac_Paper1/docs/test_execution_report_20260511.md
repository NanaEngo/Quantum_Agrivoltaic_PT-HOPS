# Test Execution Report - May 11, 2026

**Report Generated**: 2026-05-11  
**Time Range**: After 10:01 AM  
**Data Sources**: Test logs and CSV files from `/reproducibility/logs/` and `/reproducibility/results/`

## Test Execution Summary

**Test Session: 2026-05-11 (Started: 10:01:27, Ended: 11:56:30)**

### Test Results Overview
- **Total Tests Run**: 25+ individual test cases
- **Pass Rate**: 24/25 tests passed (96% success rate)
- **Failed Test**: `test_quantum_dynamics_simulator` in `test_models_dynamics.py`

### Key Test Categories Executed

#### 1. Core Functionality Tests
- Constants validation (Temperature: 295.0 K) ✅
- Hamiltonian factory (FMO 7×7 matrix, Hermitian check passed) ✅
- HopsSimulator initialization (L=8, K=2 configuration) ✅

#### 2. Site Dynamics Tests
- **3-Site Minimal**: Population shape (5, 3), trace preserved [1.0000, 1.0000] ✅
- **7-Site Minimal**: Population shape (5, 7), trace preserved [1.0000, 1.0000] ✅

#### 3. Hamiltonian Properties
- Hermitian matrix validation ✅
- Eigenvalue analysis: Real values, range [12180.7, 12680.6] cm⁻¹ ✅

#### 4. Environmental Factors
- **Temperature Sweep Efficiency**:
  - OPV: [0.15, 0.15, 0.15, 0.1489, 0.1459, 0.1429]
  - PSU: [0.15, 0.15, 0.15, 0.1494, 0.1479, 0.1464]
- **Dust Saturation**: Max dust = 1.4762 (within limit 5.0) ✅
- **Combined Effects**:
  - PCE: [0.1479, 0.1418, 0.1357]
  - ETR: [0.2474, 0.2422, 0.2371]

#### 5. Stochastically Bundled Dissipators (SBD)
- Activation tests for L=2,3,4: All enabled ✅
- Memory estimation: Simulator initialized successfully ✅

#### 6. Integration Pipeline
- Configuration loading (L=8, K=2) ✅
- Validation failure test (L=4 rejected) ✅
- Environment checks (MesoHOPS present/absent) ✅
- Full pipeline flow: Audit, simulation, figures all called ✅

#### 7. Agrivoltaic Coupling Model
- 28 total sites (4 OPV + 7 PSU) ✅
- Spectral optimizer: Optimal PCE = 0.2000 ✅

#### 8. Analysis Models
- **LCA**: EPBT = 1.63 yr, CF = 35.55 gCO2/kWh
- **Techno-economic**: NPV = $5.7M, LCOE = $0.0694/kWh
- **Eco-design**: B-index = 112.85, Sustainability = 1.000
- **Biodegradability**: Score = 0.2902

#### 9. Spectroscopy
- 2DES spectrum generation: Shape (256, 256) ✅
- Figure saved: `spectroscopy_2des_20260511_115629.pdf`

#### 10. Utilities
- CSV data storage: 11 rows, 10 columns ✅
- Figure generator: DPI validation (600/300) ✅
- Logging configuration: Test logger created ✅

## Data Files Generated

### Convergence Audit Data
**File**: `convergence_audit_1012c2967159_20260511_112037.csv`
- **Time Range**: 0-24 fs
- **Data Points**: 49 time steps
- **Columns**: time_fs, populations (7 sites), coherences, L6/L7 comparisons
- **Key Observations**:
  - Initial state: Site 1 = 1.000, others = 0.000
  - Population transfer dynamics show coherent energy migration
  - Coherence values increase from 0 to ~1.13 over 24 fs
  - L6/L7 convergence comparison columns included

### FMO Dynamics Broadband Data
**File**: `fmo_dynamics_broadband_1012c2967159_20260511_114753.csv`
- **Format**: Time series with site populations and coherences
- **Metadata**: Config SHA256: 1012c2967159, JPCL Resubmission v1.3
- **Initial Distribution**: Sites [0.267, 0.036, 0.046, 0.040, 0.133, 0.008, 0.471]
- **Coherence**: Initial value ~4.106

## Critical Issues Identified

### ❌ Failed Test: Quantum Dynamics Simulator
- **Location**: `test_models_dynamics.py::test_quantum_dynamics_simulator`
- **Status**: FAILED
- **Impact**: Core quantum simulation functionality may be compromised
- **Recommendation**: Investigate failure cause and fix before production use

## Performance Metrics
- **Test Duration**: ~1 hour 55 minutes (10:01 to 11:56)
- **Data Generation**: Multiple CSV files with convergence and dynamics data
- **Figure Generation**: 2DES spectroscopy plots created successfully
- **Memory Usage**: Within acceptable limits for L=8, K=2 simulations

## Recommendations
1. **Immediate**: Debug and fix the `test_quantum_dynamics_simulator` failure
2. **Data Validation**: Verify convergence audit results against expected physical behavior
3. **Performance**: Monitor memory usage in production runs with full disorder ensembles
4. **Documentation**: Update test logs with failure root cause analysis

## Conclusion
The test suite demonstrates robust functionality across most components, with the quantum dynamics simulator being the primary concern requiring immediate attention. All environmental factors, agrivoltaic coupling, and analysis models are functioning correctly.</content>
<parameter name="filePath">/home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/quantum_simulations_framework_parallel_260509/reproducibility/results/test_execution_report_20260511.md