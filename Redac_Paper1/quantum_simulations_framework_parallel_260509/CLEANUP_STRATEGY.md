# Codebase Cleanup & Archival Strategy — 2026-05-10

## Executive Summary

The codebase contains **obsolete, duplicate, and experimental code** that should be archived to improve clarity and maintainability. This document outlines a systematic cleanup strategy.

---

## 🗑️ Obsolete Code Inventory

### Tier 1: Clearly Obsolete (Archive Immediately)

| File/Directory | Status | Reason | Action |
|---|---|---|---|
| `quantum_coherence_agrivoltaics_mesohops_complete.py` | ❌ OBSOLETE | Monolithic script, superseded by modular pipeline | Archive |
| `refactor.py` | ❌ OBSOLETE | Old refactoring script | Archive |
| `refactor_script.py` | ❌ OBSOLETE | Duplicate refactoring script | Archive |
| `scratch/` | ❌ OBSOLETE | Experimental/debug code | Archive |
| `orca_work/` | ❌ UNCLEAR | Empty or experimental | Archive |
| `simulations/` | ⚠️ UNCLEAR | Unclear purpose, minimal content | Review |

---

### Tier 2: Duplicate/Redundant (Consolidate)

| File | Duplicate Of | Action |
|---|---|---|
| `utils/generate_figures.py` | `utils/figure_generator.py` | Consolidate into one |
| `reproducibility/main_parallel.py` | `reproducibility/main.py` | Merge into main.py |
| `reproducibility/optimize.py` | Unclear purpose | Review and archive if obsolete |

---

### Tier 3: Experimental/Incomplete (Archive)

| File/Directory | Status | Action |
|---|---|---|
| `Colab/` | Experimental notebooks | Archive (keep one canonical) |
| `test_comprehensive.py` | Placeholder (0 tests) | Archive or complete |
| `test_jpcl_resubmission_suite.py` | Placeholder (0 tests) | Archive or complete |
| `test_physics_validation.py` | Placeholder (0 tests) | Archive or complete |
| `test_second_pass.py` | Placeholder (0 tests) | Archive or complete |
| `test_svd_mpo.py` | Placeholder (0 tests) | Archive or complete |

---

### Tier 4: Utility Scripts (Organize)

| File | Purpose | Action |
|---|---|---|
| `check_env.py` | Environment checking | Move to `scripts/setup/` |
| `run_cluster.sh` | Cluster submission | Move to `scripts/cluster/` |
| `run_temp_sweep_cluster.sh` | Cluster temperature sweep | Move to `scripts/cluster/` |
| `patch_notebook_standardization.py` | Notebook utilities | Move to `scripts/maintenance/` |
| `sync_ipynb.py` | Notebook sync | Move to `scripts/maintenance/` |

---

## 📦 Proposed Archive Structure

```
archives/
├── obsolete/
│   ├── quantum_coherence_agrivoltaics_mesohops_complete.py
│   ├── refactor.py
│   ├── refactor_script.py
│   └── README_OBSOLETE.md
├── experimental/
│   ├── scratch/
│   ├── orca_work/
│   ├── simulations/
│   └── README_EXPERIMENTAL.md
├── notebooks/
│   ├── colab/
│   │   ├── quantum_agrivoltaic_colab_launcher.ipynb
│   │   ├── quantum_agrivoltaic_colab_launcher2.ipynb
│   │   └── quantum_coherence_agrivoltaics_mesohops_complete.ipynb
│   └── README_NOTEBOOKS.md
├── duplicates/
│   ├── generate_figures.py (old version)
│   ├── main_parallel.py (merged into main.py)
│   └── README_DUPLICATES.md
└── incomplete_tests/
    ├── test_comprehensive.py
    ├── test_jpcl_resubmission_suite.py
    ├── test_physics_validation.py
    ├── test_second_pass.py
    ├── test_svd_mpo.py
    └── README_INCOMPLETE_TESTS.md
```

---

## 🔄 Cleanup Workflow

### Step 1: Create Archives Directory
```bash
mkdir -p archives/{obsolete,experimental,notebooks,duplicates,incomplete_tests}
```

### Step 2: Archive Obsolete Code
```bash
# Move monolithic script
mv quantum_coherence_agrivoltaics_mesohops_complete.py archives/obsolete/

# Move refactoring scripts
mv refactor.py archives/obsolete/
mv refactor_script.py archives/obsolete/

# Move experimental directories
mv scratch/ archives/experimental/
mv orca_work/ archives/experimental/
mv simulations/ archives/experimental/
```

### Step 3: Archive Notebooks
```bash
# Move Colab notebooks
mv Colab/ archives/notebooks/colab/
```

### Step 4: Archive Incomplete Tests
```bash
# Move placeholder test files
mv tests/test_comprehensive.py archives/incomplete_tests/
mv tests/test_jpcl_resubmission_suite.py archives/incomplete_tests/
mv tests/test_physics_validation.py archives/incomplete_tests/
mv tests/test_second_pass.py archives/incomplete_tests/
mv tests/test_svd_mpo.py archives/incomplete_tests/
```

### Step 5: Consolidate Duplicates
```bash
# Keep figure_generator.py, archive generate_figures.py
mv utils/generate_figures.py archives/duplicates/

# Merge main_parallel.py into main.py, then archive
# (See consolidation details below)
mv reproducibility/main_parallel.py archives/duplicates/
```

### Step 6: Organize Utility Scripts
```bash
mkdir -p scripts/{setup,cluster,maintenance}

# Setup scripts
mv reproducibility/check_env.py scripts/setup/

# Cluster scripts
mv run_cluster.sh scripts/cluster/
mv reproducibility/run_temp_sweep_cluster.sh scripts/cluster/

# Maintenance scripts
mv utils/patch_notebook_standardization.py scripts/maintenance/
mv utils/sync_ipynb.py scripts/maintenance/
```

---

## 🔗 Consolidation Details

### 1. Figure Generation Consolidation

**Current State:**
- `utils/figure_generator.py` — Main figure generator
- `utils/generate_figures.py` — Duplicate/variant

**Action:**
```python
# In utils/figure_generator.py, add:
# - All functions from generate_figures.py
# - Consolidate duplicate logic
# - Keep single canonical implementation

# Archive old version:
mv utils/generate_figures.py archives/duplicates/
```

**Update Imports:**
```python
# Before:
from utils.generate_figures import plot_dynamics

# After:
from utils.figure_generator import plot_dynamics
```

---

### 2. Main Pipeline Consolidation

**Current State:**
- `reproducibility/main.py` — Production pipeline
- `reproducibility/main_parallel.py` — Parallel variant

**Action:**
```python
# In reproducibility/main.py, add:
# - Parallel execution logic from main_parallel.py
# - Keep --parallel flag to enable parallel mode
# - Consolidate configuration handling

# Archive old version:
mv reproducibility/main_parallel.py archives/duplicates/
```

**Update Entry Point:**
```bash
# Before:
python reproducibility/main_parallel.py --parallel

# After:
python reproducibility/main.py --parallel
```

---

### 3. Optimize.py Review

**Current State:**
- `reproducibility/optimize.py` — Unclear purpose

**Action:**
```bash
# Review content:
cat reproducibility/optimize.py

# If obsolete:
mv reproducibility/optimize.py archives/obsolete/

# If useful:
mv reproducibility/optimize.py pipelines/optimization/
```

---

## 📝 Archive Documentation

### README_OBSOLETE.md
```markdown
# Obsolete Code Archive

This directory contains code that is no longer used in the active codebase.

## Contents

- `quantum_coherence_agrivoltaics_mesohops_complete.py` — Monolithic script
  - **Reason:** Superseded by modular pipeline in `reproducibility/main.py`
  - **Date Archived:** 2026-05-10
  - **Replacement:** Use `reproducibility/main.py` instead

- `refactor.py`, `refactor_script.py` — Old refactoring scripts
  - **Reason:** Superseded by new refactoring tools
  - **Date Archived:** 2026-05-10
  - **Replacement:** Use new refactoring utilities

## How to Restore

If you need to restore any of these files:

```bash
git checkout HEAD -- archives/obsolete/<filename>
```

## Notes

- These files are kept for historical reference
- Do not use in production
- Consider deleting after 6 months if not needed
```

### README_EXPERIMENTAL.md
```markdown
# Experimental Code Archive

This directory contains experimental and work-in-progress code.

## Contents

- `scratch/` — Debug and experimental scripts
- `orca_work/` — ORCA integration experiments
- `simulations/` — Simulation experiments

## Status

These are not part of the active codebase and may not work.

## How to Use

If you want to revive any experimental code:

1. Review the code carefully
2. Test thoroughly
3. Move to appropriate location in `src/`
4. Update imports and dependencies
5. Add to test suite

## Notes

- Use at your own risk
- May have outdated dependencies
- Consider refactoring before use
```

### README_INCOMPLETE_TESTS.md
```markdown
# Incomplete Test Files

This directory contains test files that are placeholders or incomplete.

## Contents

- `test_comprehensive.py` — Placeholder (0 tests)
- `test_jpcl_resubmission_suite.py` — Placeholder (0 tests)
- `test_physics_validation.py` — Placeholder (0 tests)
- `test_second_pass.py` — Placeholder (0 tests)
- `test_svd_mpo.py` — Placeholder (0 tests)

## Status

These files exist but contain no actual test functions.

## How to Complete

To complete any of these test files:

1. Move back to `tests/`
2. Implement test functions
3. Ensure all tests pass
4. Add to CI/CD pipeline

## Notes

- These are not run by pytest
- Do not rely on these for coverage
- Consider completing or deleting
```

---

## 🧹 Cleanup Checklist

### Phase 1: Preparation
- [ ] Create `archives/` directory structure
- [ ] Create README files for each archive subdirectory
- [ ] Review all files to be archived
- [ ] Get team approval for cleanup

### Phase 2: Archival
- [ ] Archive obsolete code
- [ ] Archive experimental code
- [ ] Archive notebooks
- [ ] Archive incomplete tests
- [ ] Archive duplicate files

### Phase 3: Consolidation
- [ ] Consolidate figure generation
- [ ] Consolidate main pipeline
- [ ] Review and archive optimize.py
- [ ] Update all imports

### Phase 4: Organization
- [ ] Create `scripts/` directory structure
- [ ] Move utility scripts to appropriate locations
- [ ] Update all references to moved scripts
- [ ] Update documentation

### Phase 5: Verification
- [ ] Run full test suite
- [ ] Verify all imports work
- [ ] Check that no code is broken
- [ ] Update CI/CD configuration

### Phase 6: Documentation
- [ ] Update README.md
- [ ] Update QUICKSTART.md
- [ ] Create CLEANUP_SUMMARY.md
- [ ] Update CONTRIBUTING.md

---

## 📊 Impact Analysis

### Before Cleanup
```
Total Files: ~150
Obsolete: ~15
Duplicate: ~5
Experimental: ~10
Incomplete: ~5
Organized: ~110
```

### After Cleanup
```
Active Codebase: ~110 files
Archives: ~35 files
Clarity: Significantly improved
Maintainability: Significantly improved
```

---

## 🔐 Safety Measures

### Git History Preservation
```bash
# All archived files remain in Git history
# Can be restored with:
git checkout HEAD -- archives/obsolete/<filename>

# Or view history:
git log --follow -- <filename>
```

### Backup Strategy
```bash
# Create backup before cleanup:
git tag -a cleanup-backup-2026-05-10 -m "Backup before cleanup"

# Can restore entire state if needed:
git checkout cleanup-backup-2026-05-10
```

### Gradual Rollout
1. Create archives directory
2. Move files one category at a time
3. Test after each move
4. Verify no breakage
5. Commit changes incrementally

---

## 📋 Files to Keep (Active Codebase)

### Core Modules
- ✅ `core/` — All files
- ✅ `extensions/` — All files
- ✅ `models/` — All files (to be reorganized)
- ✅ `utils/` — All files (to be reorganized)

### Reproducibility
- ✅ `reproducibility/main.py` — Keep (consolidate main_parallel.py into it)
- ✅ `reproducibility/audit_convergence.py` — Keep
- ✅ `reproducibility/run_temp_sweep_only.py` — Keep

### Tests
- ✅ `tests/` — Keep active tests (archive incomplete ones)
- ✅ `tests/conftest.py` — Keep

### Configuration
- ✅ `parameters.yaml` — Keep
- ✅ `laptop_parameters.yaml` — Keep
- ✅ `parallel_config.yaml` — Keep
- ✅ `pytest.ini` — Keep

### Data
- ✅ `data/` — Keep
- ✅ `data_input/` — Keep

### Documentation
- ✅ `README.md` — Keep (update)
- ✅ `QUICKSTART.md` — Keep (update)
- ✅ All `.md` files in root — Keep (organize)

---

## 🚀 Implementation Timeline

### Week 1: Preparation
- [ ] Create archive structure
- [ ] Review all files
- [ ] Get team approval
- [ ] Create backup tag

### Week 2: Archival
- [ ] Archive obsolete code
- [ ] Archive experimental code
- [ ] Archive incomplete tests
- [ ] Verify no breakage

### Week 3: Consolidation
- [ ] Consolidate duplicates
- [ ] Update imports
- [ ] Run full test suite
- [ ] Verify functionality

### Week 4: Organization
- [ ] Move utility scripts
- [ ] Update documentation
- [ ] Final verification
- [ ] Deploy changes

---

## ✨ Expected Benefits

### Clarity
- ✅ Reduced confusion about which code is active
- ✅ Clear distinction between production and experimental
- ✅ Easier to find relevant code

### Maintainability
- ✅ Fewer files to maintain
- ✅ Clearer code organization
- ✅ Easier onboarding for new developers

### Performance
- ✅ Faster IDE indexing
- ✅ Faster search operations
- ✅ Reduced cognitive load

### Quality
- ✅ Fewer duplicate implementations
- ✅ Single source of truth for each function
- ✅ Easier to maintain consistency

---

## 📝 Cleanup Summary Document

After cleanup, create `CLEANUP_SUMMARY.md`:

```markdown
# Codebase Cleanup Summary — 2026-05-10

## Changes Made

### Archived Files
- Moved 15 obsolete files to `archives/obsolete/`
- Moved 10 experimental files to `archives/experimental/`
- Moved 5 incomplete tests to `archives/incomplete_tests/`
- Moved 3 Colab notebooks to `archives/notebooks/`

### Consolidated Files
- Merged `generate_figures.py` into `figure_generator.py`
- Merged `main_parallel.py` into `main.py`
- Reviewed and archived `optimize.py`

### Organized Files
- Created `scripts/` directory structure
- Moved utility scripts to appropriate locations
- Updated all references

## Impact

- **Active Codebase:** 110 files (down from 150)
- **Clarity:** Significantly improved
- **Maintainability:** Significantly improved
- **Test Coverage:** Unchanged (31 active tests)

## Next Steps

1. Review restructuring proposal
2. Plan module reorganization
3. Implement new directory structure
4. Migrate code to new locations
```

---

## 🎯 Conclusion

This cleanup strategy will:

1. **Remove clutter** — Archive obsolete and experimental code
2. **Eliminate duplication** — Consolidate duplicate implementations
3. **Improve clarity** — Clear distinction between active and archived code
4. **Enhance maintainability** — Easier to find and modify code
5. **Preserve history** — All code remains in Git history

**Estimated Effort:** 1-2 weeks  
**Risk Level:** Low (all changes reversible via Git)  
**Expected ROI:** High (improved clarity and maintainability)

---

**Cleanup & Archival Strategy — 2026-05-10**  
**Status:** Ready for implementation  
**Next Step:** Create archives directory and begin archival process
