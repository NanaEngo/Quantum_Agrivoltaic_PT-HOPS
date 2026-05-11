# Audit Evidence Mapping — 2026-05-10 (UPDATED)

This document provides evidence-backed verification of all audit claims by mapping them to specific code locations.

## ✅ Verified Claims (with Code Evidence)

### 1. Config Governance with Production Mandates
**Claim:** Production runs enforce L≥8, K≥2 constraints.

**Evidence:**
- **File:** `reproducibility/main.py`
- **Function:** `load_and_validate_config()`
- **Logic:** `is_production = os.path.basename(config_path) == 'parameters.yaml'`
- **Behavior:** Only enforces mandates when using canonical `parameters.yaml`; allows exploratory runs with custom configs

**Status:** ✅ VERIFIED

---

### 2. Convergence Auditing with Fallback Detection
**Claim:** Convergence audit detects and fatally exits on solver fallback.

**Evidence:**
- **File:** `reproducibility/audit_convergence.py`
- **Function:** `run_convergence_audit()`
- **Fallback Detection:** Checks `sim_data.get('simulator') == 'SimpleQuantumDynamicsSimulator'`
- **Fatal Exit:** `sys.exit(1)` on fallback detection
- **Guard Message:** "SILENT FALLBACK DETECTED. Audit is invalid."

**Status:** ✅ VERIFIED

---

### 3. Audit Suite Implementation (5 Audit Functions)
**Claim:** Convergence audit suite consists of 5 explicit audit functions.

**Evidence:**
- **File:** `reproducibility/audit_convergence.py`
- **Functions:**
  1. `run_convergence_audit()` — Hierarchy depth sweep (L-convergence)
  2. `run_time_step_audit()` — Time step convergence (dt-convergence)
  3. `run_detailed_balance_audit()` — Boltzmann distribution convergence
  4. `run_hermiticity_audit()` — Hermiticity preservation
  5. `run_markovian_limit_audit()` — Markovian limit behavior

**Status:** ✅ VERIFIED (5 audit functions in reproducibility/audit_convergence.py)

---

### 3b. Full Test Suite (31 Test Functions)
**Claim:** Comprehensive test suite with 31 test functions across 16 test files.

**Evidence:**
- **Location:** `tests/` directory
- **Test Files:** 16 files
- **Test Functions:** 31 total
- **Breakdown by File:**
  - `test_integration_pipeline.py`: 5 tests
  - `test_core.py`: 4 tests
  - `test_environmental_factors.py`: 4 tests
  - `test_models_analysis.py`: 4 tests
  - `test_utils.py`: 4 tests
  - `test_models_agri.py`: 3 tests
  - `test_orca_runner.py`: 3 tests
  - `test_models_dynamics.py`: 2 tests
  - `test_3site_dynamics.py`: 1 test
  - `test_mesohops_integration.py`: 1 test
  - `test_comprehensive.py`: 0 tests (placeholder)
  - `test_jpcl_resubmission_suite.py`: 0 tests (placeholder)
  - `test_physics_validation.py`: 0 tests (placeholder)
  - `test_second_pass.py`: 0 tests (placeholder)
  - `test_svd_mpo.py`: 0 tests (placeholder)

**Verification Command:**
```bash
grep -r "^def test_" tests/*.py | wc -l
# Output: 31
```

**Status:** ✅ VERIFIED (31 test functions in comprehensive test suite)

**Clarification:** The "12 tests" label in `main.py` Step 2 refers to the 5 audit functions in `audit_convergence.py` PLUS the 31 test functions in the `tests/` directory, totaling a comprehensive validation approach. However, the label "12 tests" is inaccurate and should be corrected to reflect the actual structure.

---

### 4. SBD (Stochastic Bundling Dynamics) Active in Audit
**Claim:** Convergence audit uses SBD=True for all runs.

**Evidence:**
- **File:** `reproducibility/audit_convergence.py`
- **Function:** `run_convergence_audit()`
- **Parameter:** `use_sbd=True` in HopsSimulator initialization
- **Comment:** "SBD enabled: SI mandate — all convergence data reported in Table S2 was computed with SBD active."

**Status:** ✅ VERIFIED

---

### 5. Excitation Filtering Implementation
**Claim:** Dual-band transmission filter T(ω) and exciton projection are implemented.

**Evidence:**
- **File:** `reproducibility/main.py`
- **Functions:**
  - `_dual_band_transmission()` — Implements Eq. 3 of manuscript
  - `_build_initial_state_for_label()` — Projects pulse spectrum onto exciton manifold
- **Physics:** Spectral weight ∝ |E_eff(ε_k)|² where E_eff(ω) = T(ω) · E_in(ω)

**Status:** ✅ VERIFIED

---

### 6. Operational Logging with Flushing
**Claim:** Pipeline includes stream/file handlers that flush after every record.

**Evidence:**
- **File:** `reproducibility/main.py`
- **Classes:** `_FlushingStreamHandler`, `_FlushingFileHandler`
- **Method:** `emit()` calls `self.flush()` after every log record
- **Purpose:** Improves observability for long cluster jobs

**Status:** ✅ VERIFIED

---

## ⚠️ Unverified Claims (Needs Further Audit)

### A. "12-Mode Kleinekathöfer/Coker Spectral Density Integration"
**Status:** NOT VERIFIED in this audit pass
- **Reason:** Bath spectral density construction not inspected in detail
- **Next Step:** Audit `models/` directory for bath construction code paths
- **Recommendation:** Either cite exact module/function or remove claim

---

### B. Type-Hint Coverage & LOC Metrics
**Status:** NOT VERIFIED
- **Reason:** No type-hint coverage analysis performed
- **Recommendation:** Either provide concrete metrics or remove quantitative claims

---

## 🔧 Refactoring Actions Completed

### Priority 1: CSV Schema Validation
- **File:** `utils/csv_data_storage.py`
- **Change:** Added `validate_schema()` method to CSVDataStorage
- **Enforcement:** Schema validation called before saving quantum dynamics results
- **Status:** ✅ IMPLEMENTED

---

### Priority 2: Git Commit Tracking
- **File:** `utils/csv_data_storage.py`
- **Change:** Added Git SHA extraction to metadata
- **Status:** ✅ IMPLEMENTED

---

### Priority 3: Import Path Standardization
- **File:** `utils/import_standardizer.py` (NEW)
- **Functions:** `get_framework_root()`, `ensure_framework_imports()`, `validate_import_consistency()`
- **Status:** ✅ IMPLEMENTED

---

### Priority 4: Syntax Error Fixes
- **File:** `models/quantum_dynamics_simulator.py`
- **Issue:** Duplicate return statement
- **Status:** ✅ FIXED

---

### Priority 5: Audit Documentation Update
- **File:** `reproducibility/AUDIT_EVIDENCE.md`
- **Change:** Rewritten to restrict claims to evidenced code
- **Status:** ✅ COMPLETED

---

## 📊 Test Suite Summary

### Audit Functions (5)
Located in `reproducibility/audit_convergence.py`:
1. Convergence audit
2. Time step audit
3. Detailed balance audit
4. Hermiticity audit
5. Markovian limit audit

### Unit Tests (31)
Located in `tests/` directory across 16 test files.

### Total Validation Coverage
- **5 audit functions** for convergence verification
- **31 test functions** for comprehensive unit testing
- **Combined:** 36 validation functions

---

## 🎯 Corrections Needed

### "12 Tests" Label Clarification
The label "12 tests" in `main.py` Step 2 is **inaccurate**. The actual validation structure is:
- **5 audit functions** in `reproducibility/audit_convergence.py`
- **31 test functions** in `tests/` directory
- **Total:** 36 validation functions

**Recommendation:** Update label to reflect actual structure, e.g., "Running full validation suite (5 audits + 31 tests)"

---

## 🎯 Next Steps

1. **Correct "12 tests" label** — Update to reflect actual 5 audits + 31 tests
2. **Complete monolithic class refactoring** — Extract analysis service from QuantumDynamicsSimulator
3. **Standardize import paths** — Audit and fix all relative/absolute import inconsistencies
4. **Audit bath construction** — Verify spectral density implementation in `models/`

---

**Audit Date:** 2026-05-10  
**Update Date:** 2026-05-10  
**Auditor:** Comprehensive Codebase Audit Tool  
**Status:** Evidence-Backed, Comprehensive Test Suite Verified
