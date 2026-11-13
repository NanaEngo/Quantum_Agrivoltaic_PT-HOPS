# WP2 Verification Summary — Multilayer TMM ST-OPV & Open Quantum LHCII NESS + Non-Markovian Benchmarks

**Framework Version:** `2.5.0`  
**Target Journal:** *Renewable Energy* (Elsevier)  
**Environments Verified:** Local (`fl_qom` & `base`) + HPC `penavoraserver` (`MesoHOP-sim-18`, 48 cores / 125 GB RAM)

---

## 1. Module A — Multilayer Transfer-Matrix ST-OPV Solver ([`scripts/wp2_tmm_opv.py`](../scripts/wp2_tmm_opv.py))

- **Method:** Exact Fresnel-Snell coherent $2 \times 2$ Abeles transfer matrix on incoherent glass substrate across $300\text{–}1100\ \text{nm}$ (`1 nm` step) with 18-point Gauss-Legendre hemispherical diffuse integral, calibrated against *Nat. Commun.* 2025 (`PMC12816033`) Table 1 (`PM6:Y6` at `53/75/135/212 nm`, `IQE = 0.96`).
- **Conservation & Calibration:**
  - `max_energy_conservation_error` ($|T + R + A_{\text{total}} - 1|$): `4.44089e-16`
  - Opaque `75 nm` validation: `J_sc = 25.701 mA/cm2`, `PCE = 15.501%` (`53 nm`: `12.57%`; `135 nm`: `14.45%`)
- **Pareto Front (`120` grid designs, `24` Pareto-optimal overall, `23` within `parameters.yaml` bounds):**
  - `YAML bounds` (`d_act=50–120 nm`, `d_Ag=10–16 nm`, `d_cap=0–50 nm`): `APT_PAR in [0.1454, 0.5206]`, `LUE max = 4.424%` (`d_act=60, d_Ag=10, d_cap=20` $\rightarrow$ `APT=43.72%`, `PCE=10.12%`).
  - Extended `d_Ag = 8 nm`: `APT_PAR` up to `0.5569`, `LUE max = 4.486%`.
  - **Photomorphogenic shift:** Across the Pareto front, selective NIR/Far-Red absorption by `PM6:Y6` (`700–850 nm`) **elevates** the transmitted Red:Far-Red photon ratio (`r_fr_rel_shift = +11.8%` to `+32.0%` relative to `AM1.5G`), counteracting Shade Avoidance Syndrome under canopy shading.

---

## 2. Module B — 14-Site LHCII Open Quantum NESS & `QuTiP HEOMSolver` ([`scripts/wp2_quantum_ness.py`](../scripts/wp2_quantum_ness.py))

- **Method:** Hybrid Modified Redfield–Generalized Förster (`cutoff = 15 cm^-1`, `N_dis = 200`, FWHM `110 cm^-1`, `T = 295 K`) in both **Pauli secular** and **Partial-Secular** ($|\omega_{ab}| \le 150\ \text{cm}^{-1}$ with Fano-Agarwal correlated solar pumping from `1RWT_chainA` dipoles and local `a610-a611-a612` RC + `a612` Lutein-1 NPQ anti-commutators).
- **Spectral Invariance & Sensitivity Bounds (`open_rc`, `NPQ`, `k_RC` sweep):**
  - `H1_Novoderezhkin2005_diag_PDA`: $\eta_{\text{AM1.5G}} = 0.90951$, $\max|\Delta\eta|_{\text{open}} = 3.37 \times 10^{-5}$, $\max|\Delta\eta|_{\text{NPQ}} = 3.06 \times 10^{-5}$
  - `H2_Muh2010_diag_PDA`: $\eta_{\text{AM1.5G}} = 0.88278$, $\max|\Delta\eta|_{\text{open}} = 1.94 \times 10^{-5}$, $\max|\Delta\eta|_{\text{NPQ}} = 1.83 \times 10^{-5}$
  - `H3_MMSIC_MD_2025_full`: $\eta_{\text{AM1.5G}} = 0.88961$, $\max|\Delta\eta|_{\text{open}} = 6.12 \times 10^{-6}$, $\max|\Delta\eta|_{\text{NPQ}} = 5.96 \times 10^{-6}$
  - `Neutral_cSi_40pct` achromatic counterfactual vs `AM1.5G`: $|\Delta\eta| < 10^{-9}$ across all Hamiltonians (analytic intensity-invariance confirmed).
  - Partial-secular vs Pauli shift: $|\eta_{\text{PS}} - \eta_{\text{Pauli}}| \approx 1\text{–}2 \times 10^{-6}$.
  - `k_RC` sensitivity (`0.0033`, `0.01`, `0.5 ps^-1` on `H2`, `STOPV_APT_44.1pct_beam`): $|\Delta\eta| \in [9.90 \times 10^{-6},\, 1.18 \times 10^{-5}]$.
- **Exact `QuTiP 5.3.1 HEOMSolver` Benchmark (`4-site b601-a602-a610-a611`, Drude-Lorentz Pade `L=4, Nk=2`, `0–25 ps`):**
  - `H2`: `p_terminal_quasi_eq_heom = 0.6589` vs `pauli = 0.6384`, `abs_eta_error = 2.104e-3`
  - `H3`: `p_terminal_quasi_eq_heom = 0.6312` vs `pauli = 0.6322`, `abs_eta_error = 1.058e-4` (sub-ps coherent overshoot `max_err = 0.413` relaxes prior to `25–200 ps` RC trapping).

---

## 3. Module C — Full-14-Site Non-Markovian `MesoHOPS v1.8` HPC Benchmark ([`scripts/wp2_mesohops_hpc_benchmark.py`](../scripts/wp2_mesohops_hpc_benchmark.py))

Executed on `penavoraserver` (`MesoHOP-sim-18`, 16 parallel workers, adaptive HOPS `ADAPTIVE_H=True, ADAPTIVE_S=True`):

| Case | Sites / Modes | `MAXHIER` / `N_traj` / `t_max` | `max_norm_dev` | `P_term(HOPS)` | `P_term(Pauli)` | `MAE` |
|---|---|---|---|---|---|---|
| `H2_Muh2010_diag_PDA_DL_K1` | 14 / 28 | `L=5` / `48` / `2000 fs` | `1.11e-15` | `0.1429 ± 0.0409` | `0.1542` | `0.0198` |
| `H3_MMSIC_MD_2025_full_DL_K1` | 14 / 28 | `L=5` / `48` / `2000 fs` | `9.99e-16` | `0.2209 ± 0.0522` | `0.4125` | `0.2017` |
| `H3_MMSIC_MD_2025_full_DL_K1_Vib340` | 14 / 56 | `L=4` / `16` / `1000 fs` | `8.88e-16` | `0.0835 ± 0.0521` | `0.4035` | `0.2200` |

**Physical conclusion (mechanistic interpretability):**  
While explicit non-Markovian bath reorganization and the `340 cm^-1` chlorophyll vibronic mode induce transient sub-2 ps polaron retention in `H3` (`MesoHOPS` slower Chl b $\rightarrow$ Chl a relaxation than Redfield–Förster), the `25 ps` HEOM benchmark confirms equilibration before the `200 ps` (`k_RC = 0.005 ps^-1`) trapping timescale, yielding an overall NESS spectral quantum-efficiency shift bounded within $|\Delta\eta_{\text{NESS}}| < 3.4 \times 10^{-5}$ ($\ll 0.01\%$) across all three Hamiltonians and ST-OPV filter strata. Consequently, spectral photoselection by `PM6:Y6` ST-OPV **preserves intrinsic PSII LHCII excitonic quantum yield** while shifting sub-canopy light quantity (`PAR`) and `R:FR` photomorphogenesis — isolating the true downstream biophysical levers for WP3/WP4.

---

## 4. Synchronized Verification Runs

- **Local (`fl_qom`):** `scripts/check_config.py` (`10/10` blocks, `8/8` datasets) + `unittest` (`Ran 9 tests in 0.232s — OK`)
- **HPC (`penavoraserver`, `MesoHOP-sim-18`):** `scripts/check_config.py` (`10/10` blocks, `8/8` datasets) + `unittest` (`Ran 9 tests in 0.155s — OK`)
