# Patch: Correct Audit Count in main.py

## Issue
Line in `reproducibility/main.py` function `run_convergence_audit()`:
```python
print("\\n[Step 2] Running full validation suite (12 tests)...")
```

Should be:
```python
print("\\n[Step 2] Running full validation suite (5 audits)...")
```

## Rationale
The audit suite consists of exactly 5 audit functions:
1. run_convergence_audit() - Hierarchy depth convergence
2. run_time_step_audit() - Time step convergence
3. run_detailed_balance_audit() - Boltzmann distribution convergence
4. run_hermiticity_audit() - Hermiticity preservation
5. run_markovian_limit_audit() - Markovian limit behavior

The "12 tests" label was a placeholder and does not match the actual implementation.

## Application
Replace line ~180 in reproducibility/main.py:
```
OLD: print("\\n[Step 2] Running full validation suite (12 tests)...")
NEW: print("\\n[Step 2] Running full validation suite (5 audits)...")
```

## Status
PENDING - Requires manual edit due to JSON escaping issues in fsReplace tool.
