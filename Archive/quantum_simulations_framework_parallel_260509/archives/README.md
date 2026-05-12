# 📁 Archives & Legacy Components (`archives/`)
> **Last updated:** 2026-05-11

This directory contains deprecated modules, experimental prototypes, and legacy scripts that have been removed from the active simulation framework to maintain repository hygiene and performance.

---

## 📂 Archived Categories

### 1. `obsolete/`
Code that has been completely superseded by newer, more efficient implementations (e.g., non-parallelized HOPS solvers).
- **Status:** Should not be used for any new simulations.

### 2. `experimental/`
Work-in-progress code and high-risk prototypes.
- **Status:** Use with caution; these modules may lack proper validation or unit tests.

### 3. `duplicates/` & `incomplete_tests/`
Consolidated logic and placeholder tests from previous development cycles.
- **Status:** Retained solely for historical reference during the JPCL revision process.

---

## 🛠️ Restoration Procedure

While these files are removed from the active path, they remain fully accessible via Git:

```bash
# To view a specific archived file
cat Redac_Paper1/quantum_simulations_framework_parallel_260509/archives/obsolete/<filename>

# To restore a file to the active directory
cp Redac_Paper1/quantum_simulations_framework_parallel_260509/archives/<path>/<filename> ./
```

---

## 📜 Maintenance Policy

- **Safety:** Archived files must not be imported by any active production script.
- **Cleanup:** Components in `obsolete/` will be evaluated for permanent removal following the successful publication of the JPCL manuscript.

