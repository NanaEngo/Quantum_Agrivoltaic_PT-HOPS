# Archives and legacy components (`archives/`)

> **Last updated:** 2026-11-14

Deprecated modules, prototypes and legacy scripts removed from the active framework path to keep
the importable tree small. Nothing here is imported by a production script.

---

## Contents

### 1. `obsolete/`
Superseded implementations (for example the non-parallelised HOPS solvers). Do not use for new runs.

### 2. `experimental/`
Work-in-progress prototypes and scratch checks (`experimental/scratch/`, `experimental/simulations/`).
May lack validation.

### 3. `notebooks/`
Colab notebooks kept for provenance (launcher variants, the MesoHOPS coherence notebook).

---

## Access and restoration

These files live at their current paths and are also recoverable from git history. The older
`Redac_Paper1/quantum_simulations_framework_parallel_2605xx/` trees they once belonged to are gone —
the whole parallel-era codebase was moved to the repository-level `_archive/` on 2026-11-06, and the
JPCL revision that used it is published.

```bash
# Inspect an archived file in place
sed -n '1,40p' quantum_simulations_framework/archives/experimental/scratch/check_mesohops.py

# See what a file looked like before it was archived
git log --oneline -- quantum_simulations_framework/archives/
git show <commit>:<old/path/to/file>

# Restore one file into the active tree (then fix imports and run the tests)
git show <commit>:<old/path/to/file> > quantum_simulations_framework/src/<target>.py
```

---

## Policy

- Archived files must not be imported by active code. If one is needed, restore it, adapt it, and
  cover it with a test before relying on it.
- `obsolete/` is a candidate for permanent deletion now that the JPCL manuscript is published; it is
  kept only because removal is not required for reproducibility of the published figures.
