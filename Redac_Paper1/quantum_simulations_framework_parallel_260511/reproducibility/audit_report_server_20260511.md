# Server Reproducibility Audit Report — 2026-05-11

**Target:** `Redac_Paper1/quantum_simulations_framework_parallel_260511/reproducibility` (server tests)

**Date generated:** 2026-05-11

---

## 1) Scope & what was audited

This report audits:
1. The **server-side reproducibility pipeline code paths** that are used for:
   - convergence auditing (Step 2)
   - full FMO production simulations (Step 3)
   - figure generation (Step 4)
2. The **server-side reproducibility artifacts** present in:
   - `reproducibility/results/`
   - (where applicable) `reproducibility/logs/`
3. It then performs a **comparison** against the existing **laptop test execution report(s)**:
   - `Redac_Paper1/docs/test_execution_report_20260511.md`
   - `Redac_Paper1/docs/test_report_after_10_01am.md`

> Note: The “server” audit here is based on inspecting the **server reproducibility pipeline implementation** and the **server results artifacts** that exist in the repository; the explicit server-side test report markdown referenced in the task was not found by repo search.

---

## 2) Server pipeline design checks (code evidence)

### 2.1 Config governance: production mandates only for canonical `parameters.yaml`
- `reproducibility/main.py` enforces:
  - `L_max >= 8`
  - `matsubara_truncation >= 2`
- Enforcement is gated by:
  - `is_production = os.path.basename(config_path) == 'parameters.yaml'`

**Implication:** exploratory runs with non-canonical configs are not forced into the production constraints, while server production-like runs using the canonical file are validated.

---

### 2.2 Convergence auditing: solver fallback detection + fatal exit
- `reproducibility/audit_convergence.py`
- Fallback detector:
  - checks `sim_data.get('simulator') == 'SimpleQuantumDynamicsSimulator'`
- Fatal exit:
  - `sys.exit(1)` with message indicating “SILENT FALLBACK DETECTED. Audit is invalid.”

**Implication:** the audit is designed to fail fast if the framework returns a non-hierarchy solver.

---

### 2.3 Convergence audit suite implementation: 5 explicit audit functions
`reproducibility/audit_convergence.py` contains:
1. `run_convergence_audit()` — hierarchy-depth sweep
2. `run_time_step_audit()` — dt-convergence
3. `run_detailed_balance_audit()` — Boltzmann convergence
4. `run_hermiticity_audit()` — hermiticity/realness proxy
5. `run_markovian_limit_audit()` — Markovian-limit proxy

**Implication:** the audit suite count is **5**, even though `reproducibility/main.py` prints “12 tests…” (see §5.2 for mismatch details).

---

### 2.4 Stochastic Bundling Dynamics (SBD) enabled for audits
- `run_convergence_audit()` initializes `HopsSimulator(... use_sbd=True ...)`
- Similar SBD enabling exists in the Matsubara K-audit section.

**Implication:** the server convergence audit is consistent with the stated SI Table S2 computation assumption (“SBD active”).

---

### 2.5 Excitation filtering: dual-band transmission + exciton projection
- `reproducibility/main.py`
  - `_dual_band_transmission()` implements dual-band Gaussian filter(s) and normalizes max to 1.
  - `_build_initial_state_for_label()` constructs:
    - `E_in(ω)` (Gaussian pulse spectral envelope)
    - `E_eff(ω) = T(ω) * E_in(ω)`
    - spectral weights proportional to `|E_eff|^2`
    - initial state from exciton eigenvectors with weights.

**Implication:** the server pipeline’s “filtered” excitation is explicitly physics-constructed rather than stubbed.

---

### 2.6 Operational logging: flushing after every record
- `reproducibility/main.py`
  - `_FlushingStreamHandler.emit()` flushes immediately
  - `_FlushingFileHandler.emit()` flushes immediately

**Implication:** better observability for long server cluster jobs.

---

## 3) Server-side artifacts present (evidence from `reproducibility/results/`)

The repository contains many precomputed CSV artifacts under:
- `reproducibility/results/convergence_audit_*.csv`
- `reproducibility/results/fmo_dynamics_*.csv`

Representative filenames include:
- Convergence:
  - `convergence_audit_1012c2967159_20260511_094053.csv`
  - `convergence_audit_L8_1012c2967159_20260511_085938.csv`
  - `convergence_audit_K2_1012c2967159_20260511_092643.csv`
  - `convergence_audit_L6_1012c2967159_20260511_084134.csv`
- Production dynamics:
  - `fmo_dynamics_filtered_2d6bf169d04e_20260510_125633.csv`
  - `fmo_dynamics_broadband_2d6bf169d04e_20260510_125633.csv`
  - `fmo_dynamics_ensemble_85ed4115d72b_20260510_001120.csv`

**Implication:** server-side computations appear to have been executed across multiple config hashes and dates, including runs producing both filtered and broadband dynamics.

---

## 4) What the server tests appear to validate (inferred from implementation)

Given the server pipeline, the effective validation includes:
- **Hierarchy convergence**: hierarchy depth sweep at fixed time window
- **K/Matsubara truncation convergence**: K-terms sweep around configured value
- **Trace and positivity checks** (within `run_convergence_audit()`)
- **dt convergence**
- **Detailed balance** (Boltzmann target at long times)
- **Realness proxy** for populations (hermiticity audit)
- **Markovian monotonic decay proxy**

Additionally, full production runs then feed figure generation (Quantum dynamics, spectral relationships, environmental robustness).

---

## 5) Issues / inconsistencies discovered in the server code

### 5.1 Documentation/test-count mismatch
- `reproducibility/main.py` prints:
  - `"[Step 2] Running full validation suite (12 tests)..."`
- But `reproducibility/audit_convergence.py` implements **5** explicit audit functions.
- Separately, the overall “validation suite” may be conflating “audit functions” with “unit tests in tests/”.

**Implication:** server run messaging can be misleading for human readers/reviewers.

---

### 5.2 “Hermiticity audit” is a proxy, not a strict rho-H hermiticity test
In `run_hermiticity_audit()`:
- It checks:
  - max imaginary part of `data['populations']`
- But it does not compute `rho - rho†` hermiticity explicitly.

**Implication:** audit is adequate as a sanity check but may not fully satisfy a strict “hermiticity preservation” criterion at the density-matrix level.

---

## 6) Comparison with laptop test reports (docs)

### 6.1 Laptop report highlights
From `Redac_Paper1/docs/test_execution_report_20260511.md`:
- Test session started **10:01:27**, ended **11:56:30**
- Summary:
  - **24/25 tests passed** (96%)
  - **Failed test:** `test_quantum_dynamics_simulator` in `test_models_dynamics.py`

From `Redac_Paper1/docs/test_report_after_10_01am.md`:
- Mentions recurring FAILED integration-layer expectations (config validation / environment checks / full pipeline flow)
- Also repeatedly calls out `test_quantum_dynamics_simulator` as FAILED
- Also notes intermittent laptop-suite memory estimation behavior

---

### 6.2 Agreement between server code audit and laptop failure report
**Agreement:**
- The laptop failures highlight a problem in `test_quantum_dynamics_simulator`.
- The server audit (code inspection) shows that the convergence audit is guarded against silent fallback:
  - it explicitly fails if a non-hierarchy “SimpleQuantumDynamicsSimulator” is used.

**Interpretation:**
- Both sides suggest that **solver selection / correct simulator backend execution** is a critical fragility point.
- If laptop tests fail in `test_quantum_dynamics_simulator`, it likely corresponds to a backend path mismatch, return-structure mismatch, or strict assertion expecting a specific simulator mode.

---

### 6.3 Differences (what server code suggests vs laptop symptoms)
- The server pipeline’s explicit fallback detection is designed to prevent “fake data” from passing.
- Laptop report shows failing assertions but does not show the root cause.

**Implication:**
- Laptop failures may occur even though the server pipeline is designed to be safe; either:
  1. the laptop tests are asserting stricter semantics than the server pipeline’s convergence proxies, or
  2. laptop tests exercise a different simulator class/path than what server pipeline uses.

---

## 7) Server audit conclusion

1. The server reproducibility framework contains **strong internal safeguards** for convergence audit validity:
   - fallback detection with fatal exit
   - hierarchy depth and K-term sweeps with step-by-step saving
   - trace/positivity sanity checks
2. Excitation physics construction (dual-band filtering + exciton projection) is implemented directly in code.
3. The server pipeline contains at least one **human-facing mismatch** in “test count” messaging.
4. Laptop reports show a persistent failure in `test_quantum_dynamics_simulator`, consistent with backend-path fragility (solver/mode selection or expected output structure).

---

## 8) End-of-report: explicit additions requested

### 8.1 “Add the end of that report”
This report ends with the server audit conclusions and comparison summary (§7).

### 8.2 Comparison summary with laptop tests
- Laptop: 24/25 passed, **fail** in `test_quantum_dynamics_simulator`.
- Server code: explicitly detects solver fallback and enforces validity during convergence audit.
- Combined interpretation: the remaining reliability risk is centered around **correct simulator backend/mode selection and matching test expectations**.

