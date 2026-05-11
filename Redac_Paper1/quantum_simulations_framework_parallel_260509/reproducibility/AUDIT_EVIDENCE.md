# Audit Evidence Mapping — 2026-05-10

This document provides evidence-backed verification of all audit claims by mapping them to specific code locations.

## ✅ Verified Claims (with Code Evidence)

### 1. Config Governance with Production Mandates
**Claim:** Production runs enforce L≥8, K≥2 constraints.

**Evidence:**
- **File:** `reproducibility/main.py`
- **Function:** `load_and_validate_config()`
- **Lines:** L≥8 check, K≥2 check
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

### 3. Audit Suite Implementation
**Claim:** Audit suite consists of 5 explicit audit functions.

**Evidence:**
- **File:** `reproducibility/audit_convergence.py`
- **Functions:**
  1. `run_convergence_audit()` — Hierarchy depth sweep (L-convergence)
  2. `run_time_step_audit()` — Time step convergence (dt-convergence)
  3. `run_detailed_balance_audit()` — Boltzmann distribution convergence
  4. `run_hermiticity_audit()` — Hermiticity preservation
  5. `run_markovian_limit_audit()` — Markovian limit behavior

**Status:** ✅ VERIFIED (5 functions, not "12 tests" as previously claimed)

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

### B. "12-Test Convergence Suite"
**Status:** PARTIALLY INCORRECT
- **Finding:** Only 5 audit functions are implemented, not 12
- **Correction:** Update documentation to reflect actual 5-function suite
- **Note:** The "12 tests" label in `main.py` Step 2 is a placeholder; actual count is 5

---

### C. Type-Hint Coverage & LOC Metrics
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

### Priority 2: Monolithic Class Remediation
- **File:** `models/quantum_dynamics_simulator.py`
- **Issue:** Large class with 500+ LOC
- **Refactoring Strategy:**
  - Extract module-level worker functions for joblib picklability
  - Separate bath correlation function decomposition into helper functions
  - Preserve interface compatibility (no caller changes needed)
- **Status:** ✅ PARTIALLY IMPLEMENTED (workers extracted; full decomposition pending)

---

### Priority 3: Import Path Standardization
- **Status:** PENDING
- **Action:** Audit all `from core.X` vs `from ..core.X` imports
- **Target Files:** All modules in `models/`, `extensions/`, `utils/`

---

### Priority 4: Audit Documentation Update
- **File:** `_bmad-output/audit/Comprehensive_Codebase_Audit_260510.md`
- **Change:** Rewritten to restrict claims to evidenced code
- **Status:** ✅ COMPLETED

---

## 📊 Traceability & Determinism Guarantees

### Git Commit Tracking
- **Implementation:** Add `git_commit_sha` to output metadata
- **Location:** `utils/csv_data_storage.py` metadata section
- **Status:** PENDING

---

### RNG Seeding
- **Implementation:** All random sampling uses seeded RNG (seed=42)
- **Evidence:**
  - `_run_temperature_sweep()` uses explicit seed
  - `_build_disorder_samples()` uses `rng_seed=42`
- **Status:** ✅ VERIFIED

---

## 🎯 Next Steps

1. **Complete monolithic class refactoring** — Extract analysis service from QuantumDynamicsSimulator
2. **Standardize import paths** — Audit and fix all relative/absolute import inconsistencies
3. **Add Git commit tracking** — Implement in CSVDataStorage metadata
4. **Audit bath construction** — Verify spectral density implementation in `models/`
5. **Update "12-test" label** — Correct to "5-audit" in main.py Step 2

---

**Audit Date:** 2026-05-10  
**Auditor:** Comprehensive Codebase Audit Tool  
**Status:** Evidence-Backed, Partial Refactoring Complete
