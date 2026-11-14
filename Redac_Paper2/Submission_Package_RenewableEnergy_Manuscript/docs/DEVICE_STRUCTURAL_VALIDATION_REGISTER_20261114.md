# Device and structural external-validation register (M9)

**Status:** mitigation record and acceptance criteria. **No independent measurement or local
tender exists.** Nothing here is a validation result.
**Prepared:** 2026-11-14 · **Package:** `Redac_Paper2/Submission_Package_RenewableEnergy_Manuscript/`

M9 (as written in the mitigation plan) requires "independent optical/device checks for the modelled
PM6:Y6 stack and local wind/load/contractor evidence for elevated structures, louvers, replacement,
and maintenance", while keeping "laboratory stack validation distinct from field durability and
agronomic validation". Two of those three things cannot be produced here. What can be produced is a
register that says exactly what would count as validation, what the model predicts the check should
find, and how far the modelled results move inside credible fabrication and load tolerance —
so the check, when it happens, is a comparison against a number rather than an impression.

---

## Part A — Optical/device

### A.1 What is already validated, and what is not

| Item | Status | Evidence |
|---|---|---|
| Transfer-matrix engine conserves photons | Verified numerically | `max|R+T+A_tot−1| = 4.44×10⁻¹⁶` over the 120-stack library and over 4000 tolerance draws (`data/wp2/wp2_device_tolerance.json`) |
| Engine reproduces an **opaque** PM6:Y6 reference cell | Reproduced to within the IQE calibration | modelled 25.701 mA/cm², 15.501 % vs measured 26.36 mA/cm², 16.27 % (`data/wp2/tmm_validation_summary.json`); the 0.96 IQE clamp, not the optics, absorbs the residual |
| Engine reproduces the **semi-transparent** focal stack | **Not validated** | no measured APT/PCE/transmittance for this stack exists in the package |
| Outdoor spectral performance under Cameroon humidity/UV | **Not validated** | no outdoor measurement; ISOS-type weathering absent |
| Angular response | Modelled only | `sec:sm_angular`, computed here |

The single most important honesty point: the opaque-cell reproduction calibrates an effective IQE;
it does not validate the semi-transparent stack, whose transmittance is the quantity the agronomic
argument actually depends on.

### A.2 Acceptance criteria a laboratory check must meet

Derived from the tolerance audit (`scripts/wp2b_device_tolerance_audit.py`, 4000 draws, active layer
±5 %, Ag ±1 nm, capping ±2 nm, 1σ):

| Quantity | Modelled nominal | Modelled p05–p95 | Criterion for "consistent with the model" |
|---|---|---|---|
| APT (400–700 nm, AM1.5G) | 44.12 % | 40.30–47.75 % | measured APT within ±2.3 pp of 44.1 % |
| PCE (AM1.5G, aperture) | 9.93 % | 9.18–10.61 % | measured PCE within ±0.44 pp |
| LUE = PCE × APT | 4.38 % | 4.24–4.43 % | measured LUE within ±0.06 pp (1.3 %) |
| Beam APT at 60° | 33.07 % | — | angular protocol declared; measured normal-incidence value is not comparable to diffuse-weighted results |

The asymmetry in that table is the substantive finding: APT and PCE trade off under thickness error,
so **LUE is nearly fabrication-invariant while APT is not**. A laboratory result that reproduces
LUE but not APT is therefore consistent with the model, whereas one that reproduces APT but shifts
LUE by more than ~2 % is not.

### A.3 Required laboratory deliverables (to be appended when obtained)

1. Measured transmittance spectrum 300–1100 nm, beam at 0°/30°/60° and hemispherical, with the
   integrating-sphere geometry stated.
2. J–V under AM1.5G with a calibrated reference cell, aperture area, and stabilisation protocol;
   PCE uncertainty budget including spectral mismatch factor.
3. Layer thicknesses by ellipsometry or cross-section, so the measured stack can be compared with
   the modelled one at the same (d_act, d_Ag, d_cap).
4. Scaled-up module (≥ 10 × 10 cm) result, since the model assumes an aperture-uniform stack.
5. Durability evidence (ISOS-L-2 or equivalent) if any lifetime claim is to be retained; the
   manuscript's T80 = 5 yr baseline must otherwise remain an assumption, which is how it is labelled.

---

## Part B — Structural and wind load

### B.1 What the shipped data can and cannot say

`scripts/wp1_wind_load_screening.py` reads the 2023 ERA5 hourly series and reports:

| Site | mean (m/s) | p99 (m/s) | max (m/s) | q at record max (Pa) | hours > 10 m/s |
|---|---|---|---|---|---|
| Foumbot (coffee) | 1.53 | 3.87 | 5.42 | 18.3 | 0 |
| Njombe-Penja (pepper) | 1.18 | 2.94 | 4.58 | 13.1 | 0 |
| Djuttitsa (tea) | 1.89 | 5.31 | 7.03 | 30.9 | 0 |

These are hourly 10 m means. Candidate basic velocities of 20–32 m/s correspond to dynamic
pressures of 250–640 Pa, i.e. 8–50× the record maximum dynamic pressure. **The 2023 record
therefore bounds ordinary operating wind only and cannot support a design load**, and the package
asserts no design pressure. What the model does carry is the structural cost line
`C_BOS^c-Si ∈ [35, 85] USD/m²`, a Sobol parameter whose total-order index on comparative NPV parity
is 0.150–0.170 — so the economics brackets the structural class but the class itself is unvalidated.

### B.2 Required local inputs (fixed list)

1. National-annex basic velocity `v_b,0` for each site, with the map edition cited.
2. Terrain category and roughness length for each plot; orography factor `c_o` where slope exceeds
   the code threshold.
3. Altitude correction and the exposure/season factors the annex requires.
4. Wind tunnel or CFD evidence for the specific canopy/windbreak geometry if a reduced-pressure
   shelter factor is to be claimed. None is claimed in the manuscript.
5. Supplier certificates: module mechanical-load rating (IEC 61215/61730), mounting system
   structural calculation, and fastener/soil-anchor specification.
6. At least two independent contractor quotations for the elevated structure, the louver
   mechanism, module replacement access, and periodic maintenance, per site.

### B.3 Sensitivity already covered

| Perturbation | Effect in the package | Where |
|---|---|---|
| c-Si steel BOS cost 35–85 USD/m² | S_Ti = 0.150–0.170 on ΔNPV; ranking unchanged | `tab:sobol_dual`, `tab:sobol_convergence` |
| Louver actuation capital headroom | zero headroom where grid monetization anchors bankability | `tab:sm_monsoon_louver` |
| Seasonal open-louver operation | annual PV generation loss 38.0–40.1 %; NPV −$350k to −$784k | `tab:sm_monsoon_louver` |
| Replacement cost | carried in replacement annuity at 25 USD/m², T80 sweep 3–25 yr | `sec:methods_tea` |

### B.4 The objection this register does **not** answer

A reviewer may reasonably say that a structure whose wind class is unvalidated makes every NPV
above it provisional. That objection is correct in kind, and the manuscript's response is scoping
rather than evidence: NPV is reported as a modelled operating case per installed-array hectare, not
as a bankable forecast, and the no-export and 50 %-acceptance cases already show the headline
collapsing to −$380k and −$282k for the two daytime-load crops. Structural cost is one of the
twelve Sobol parameters and does not change the technology ranking, but it would change the absolute
numbers, and no claim in the paper depends on the absolute level being right.

---

## Statement of what has and has not been done

**Done here:** an executed fabrication-tolerance and angular-acceptance audit of the focal stack
(`data/wp2/wp2_device_tolerance.json`), an executed site wind screening
(`data/wp1/wind_load_screening.json`), explicit acceptance criteria, and a fixed list of the local
evidence that would close the item.

**Not done, and not claimed:** any independent optical measurement, any outdoor durability
measurement, any structural calculation to a national annex, any contractor quotation, any
installation, and any field campaign. M9 remains **open** in its substance; it is now specified
rather than merely deferred.
