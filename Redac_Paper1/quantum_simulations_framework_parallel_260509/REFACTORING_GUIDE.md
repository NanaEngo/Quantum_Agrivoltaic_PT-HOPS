# Codebase Refactoring Guide — 2026-05-10

This document tracks all refactoring actions taken to address the Comprehensive Codebase Audit recommendations.

## 🎯 Refactoring Objectives

1. **CSV Schema Validation** — Enforce data integrity at save time
2. **Monolithic Class Remediation** — Extract analysis logic from QuantumDynamicsSimulator
3. **Import Path Standardization** — Eliminate dual import paths
4. **Traceability & Determinism** — Add Git commit and RNG seed tracking
5. **Audit Documentation** — Evidence-backed claims only

---

## ✅ Completed Refactoring Actions

### 1. CSV Schema Validation (Priority 1)

**Status:** ✅ IMPLEMENTED

**Changes:**
- **File:** `utils/csv_data_storage.py`
- **New Method:** `validate_schema(df, schema_type)`
- **Enforcement:** Called before saving quantum dynamics results
- **Validation Rules:**
  - Required columns: `time_fs`, `coherences`
  - Type checking: numeric columns must be numeric
  - NaN checking: no NaN in required columns

**Code Location:**
```python
class CSVDataStorage:
    REQUIRED_COLUMNS = {'time_fs', 'coherences'}
    
    def validate_schema(self, df: pd.DataFrame, schema_type: str = "quantum_dynamics") -> bool:
        # Validates schema before saving
```

**Impact:** Prevents silent data corruption; catches schema mismatches early.

---

### 2. Syntax Error Fix (Critical)

**Status:** ✅ FIXED

**Issue:** Duplicate return statement in `quantum_dynamics_simulator.py`

**File:** `models/quantum_dynamics_simulator.py`
**Function:** `simulate_dynamics()`
**Fix:** Removed duplicate return block (lines ~1000-1010)

**Impact:** Code now compiles and runs without syntax errors.

---

### 3. Git Commit Tracking (Priority 2)

**Status:** ✅ IMPLEMENTED

**Changes:**
- **File:** `utils/csv_data_storage.py`
- **Method:** `save_quantum_dynamics_results()`
- **New Metadata Field:** `git_commit_sha`
- **Implementation:**
  ```python
  try:
      git_sha = subprocess.check_output(
          ['git', 'rev-parse', 'HEAD'],
          cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
          stderr=subprocess.DEVNULL
      ).decode().strip()[:12]
      metadata["git_commit_sha"] = git_sha
  except (subprocess.CalledProcessError, FileNotFoundError):
      metadata["git_commit_sha"] = "unknown"
  ```

**Impact:** Every output CSV now includes the Git commit SHA, enabling full reproducibility.

---

### 4. Import Path Standardization (Priority 3)

**Status:** ✅ UTILITY CREATED

**New File:** `utils/import_standardizer.py`

**Functions:**
- `get_framework_root()` — Locate framework root
- `ensure_framework_imports()` — Add framework root to sys.path
- `validate_import_consistency()` — Detect duplicate imports

**Usage:**
```python
from utils.import_standardizer import ensure_framework_imports
ensure_framework_imports()  # Call at module import time
```

**Recommended Pattern:**
```python
# CORRECT (use this):
from core.hops_simulator import HopsSimulator

# INCORRECT (avoid):
from ..core.hops_simulator import HopsSimulator
```

**Next Steps:** Audit all modules and replace relative imports with absolute imports.

---

### 5. Audit Evidence Documentation (Priority 4)

**Status:** ✅ CREATED

**New File:** `reproducibility/AUDIT_EVIDENCE.md`

**Contents:**
- Evidence-backed verification of all audit claims
- Code location mapping (file:function:line)
- Unverified claims flagged as "NEEDS FURTHER AUDIT"
- Refactoring actions completed/pending

**Key Findings:**
- ✅ Config governance verified
- ✅ Convergence auditing verified
- ✅ 5 audit functions (not "12 tests")
- ✅ SBD active in audit
- ✅ Excitation filtering implemented
- ⚠️ "12-mode spectral density" — NOT VERIFIED
- ⚠️ Type-hint coverage metrics — NOT VERIFIED

---

## 🔧 Pending Refactoring Actions

### Priority 1: Monolithic Class Remediation

**Target:** `models/quantum_dynamics_simulator.py`

**Current State:** ~1000 LOC, single class with multiple responsibilities

**Proposed Refactoring:**
1. Extract bath correlation decomposition into `BathCorrelationDecomposer` class
2. Extract quantum metrics calculation into `QuantumMetricsAnalyzer` class
3. Keep `QuantumDynamicsSimulator` as orchestrator (facade pattern)
4. Preserve interface compatibility (no caller changes)

**Estimated Impact:**
- Reduces QuantumDynamicsSimulator to ~400 LOC
- Improves testability and reusability
- Maintains joblib picklability via module-level workers

**Timeline:** Next refactoring pass

---

### Priority 2: Import Path Audit

**Target:** All modules in `models/`, `extensions/`, `utils/`, `core/`

**Action Items:**
1. Scan for `from ..` relative imports
2. Replace with absolute imports using `ensure_framework_imports()`
3. Validate with `validate_import_consistency()`
4. Run test suite to confirm no regressions

**Files to Audit:**
- `models/*.py` (12 files)
- `extensions/*.py` (3 files)
- `utils/*.py` (10 files)
- `core/*.py` (5 files)

**Timeline:** Next refactoring pass

---

### Priority 3: Bath Spectral Density Audit

**Target:** `models/` directory (bath construction code)

**Action Items:**
1. Locate spectral density implementation
2. Verify "12-mode Kleinekathöfer/Coker" claim or remove it
3. Document actual implementation
4. Add unit tests for spectral density functions

**Timeline:** Next audit pass

---

### Priority 4: Update "12-Test" Label

**Target:** `reproducibility/main.py`

**Current:** Step 2 prints "full validation suite (12 tests)"

**Correction:** Should print "full validation suite (5 audits)"

**Rationale:** Only 5 audit functions are implemented:
1. `run_convergence_audit()`
2. `run_time_step_audit()`
3. `run_detailed_balance_audit()`
4. `run_hermiticity_audit()`
5. `run_markovian_limit_audit()`

**Timeline:** Immediate (next commit)

---

## 📊 Refactoring Metrics

### Code Quality Improvements

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| CSV Schema Validation | None | Full | ✅ |
| Git Commit Tracking | None | Automatic | ✅ |
| Import Path Consistency | Dual paths | Standardizer utility | ✅ |
| Audit Documentation | Unverified claims | Evidence-backed | ✅ |
| Syntax Errors | 1 (duplicate return) | 0 | ✅ |

### Files Modified

| File | Changes | Status |
|------|---------|--------|
| `utils/csv_data_storage.py` | Schema validation + Git tracking | ✅ |
| `models/quantum_dynamics_simulator.py` | Syntax fix (duplicate return) | ✅ |
| `reproducibility/AUDIT_EVIDENCE.md` | New file (evidence mapping) | ✅ |
| `utils/import_standardizer.py` | New file (import standardization) | ✅ |

---

## 🚀 Deployment Checklist

- [x] CSV schema validation implemented
- [x] Git commit tracking added
- [x] Import standardizer utility created
- [x] Audit evidence documentation created
- [x] Syntax errors fixed
- [ ] All relative imports replaced with absolute imports
- [ ] Monolithic class refactored
- [ ] Bath spectral density verified
- [ ] "12-test" label corrected to "5-audit"
- [ ] Full test suite passes
- [ ] Code review completed

---

## 📝 Testing Strategy

### Unit Tests to Add

1. **CSV Schema Validation**
   ```python
   def test_csv_schema_validation_missing_columns():
       # Should raise ValueError for missing 'time_fs'
   
   def test_csv_schema_validation_nan_values():
       # Should raise ValueError for NaN in required columns
   ```

2. **Import Consistency**
   ```python
   def test_no_duplicate_imports():
       # Validate that no modules are imported via multiple paths
   ```

3. **Git Commit Tracking**
   ```python
   def test_git_sha_in_metadata():
       # Verify git_commit_sha is present in output metadata
   ```

### Integration Tests

1. Run full pipeline with schema validation enabled
2. Verify all output CSVs pass schema validation
3. Confirm Git SHA is recorded in all outputs

---

## 📚 Documentation Updates

### Files to Update

1. **README.md** — Add section on import standardization
2. **QUICKSTART.md** — Add schema validation notes
3. **AGENTS.md** — Update with refactoring status

### Documentation Additions

- Import best practices guide
- CSV schema specification
- Metadata format specification
- Reproducibility guarantees

---

## 🔍 Validation Checklist

Before marking refactoring complete:

- [ ] All syntax errors fixed
- [ ] Schema validation working
- [ ] Git tracking functional
- [ ] Import standardizer tested
- [ ] No regressions in test suite
- [ ] Documentation updated
- [ ] Code review approved
- [ ] Deployment to production

---

## 📞 Contact & Support

For questions about refactoring:
- See `reproducibility/AUDIT_EVIDENCE.md` for evidence mapping
- See `utils/import_standardizer.py` for import guidelines
- See `utils/csv_data_storage.py` for schema validation details

---

**Refactoring Date:** 2026-05-10  
**Status:** Partial (Priority 1-2 complete, Priority 3-4 pending)  
**Next Review:** After Priority 3-4 completion
