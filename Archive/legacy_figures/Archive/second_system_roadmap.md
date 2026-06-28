# Roadmap: Adding a Second System for Generalizability

## Motivation

Referees may object that the spectral bath engineering mechanism is specific to the FMO complex. Demonstrating the same effect in a second system—even a minimal model—proves universality and significantly increases the probability of acceptance (~55–65% → ~70–75%).

---

## Option A: 3-Site Toy Model ⭐ Recommended

### System Description

A minimal excitonic trimer with tunable parameters designed to isolate the spectral bath engineering mechanism from system-specific features of FMO.

### Hamiltonian

$$H_S = \sum_{n=1}^{3} \varepsilon_n |n\rangle\langle n| + \sum_{n \neq m} J_{nm} |n\rangle\langle m|$$

| Parameter | Value | Rationale |
|---|---|---|
| $\varepsilon_1$ | 0 cm⁻¹ | Reference energy |
| $\varepsilon_2$ | 150 cm⁻¹ | Gap ≈ underdamped mode frequency |
| $\varepsilon_3$ | −50 cm⁻¹ | Reaction center (sink) |
| $J_{12}$ | −80 cm⁻¹ | Strong coupling (FMO-like) |
| $J_{13}$ | 5 cm⁻¹ | Weak direct coupling |
| $J_{23}$ | −50 cm⁻¹ | Intermediate coupling |

### Spectral Density

Drude–Lorentz + one underdamped mode:

$$J(\omega) = \frac{2\lambda\gamma\omega}{\omega^2 + \gamma^2} + \frac{2\lambda_v\omega_v^2\gamma_v\omega}{(\omega^2 - \omega_v^2)^2 + \omega^2\gamma_v^2}$$

| Parameter | Value |
|---|---|
| $\lambda$ (reorganization) | 35 cm⁻¹ |
| $\gamma$ (Drude cutoff) | 50 cm⁻¹ |
| $\omega_v$ (vibronic mode) | 180 cm⁻¹ |
| $\lambda_v$ (vibronic coupling) | 15 cm⁻¹ |
| $\gamma_v$ (vibronic damping) | 10 cm⁻¹ |
| $T$ | 295 K |

### Filter Design

Dual-band filter targeting $\varepsilon_1 + \omega_v$ and $\varepsilon_2$:
- Band 1: center at equivalent wavelength of $\varepsilon_1 + \omega_v$
- Band 2: center at equivalent wavelength of $\varepsilon_2$
- FWHM: 20 nm equivalent

### Expected Results

- Coherence extension: ~30–40%
- ETE enhancement: ~15–20%
- Off-resonant filter control: $\eta < 0.05$ (negative control)

### Computational Cost

- ~2 hours on AMD Ryzen 5 (3 sites × L=6 × K=3, 100 disorder realizations)

### Manuscript Integration

- **Results section:** New subsection "Generalizability: Three-site model" (~1 paragraph + 1 table)
- **SI:** New section with parameters and convergence tests
- **Conclusion:** Update to reference the generality demonstration

### Effort: ~1 day

---

## Option B: LH2 B850 Ring

### System Description

The 18-bacteriochlorophyll B850 ring of the LH2 complex from *Rhodopseudomonas acidophila*. The most-studied light-harvesting complex after FMO.

### Hamiltonian

- 18 BChl sites with C₉ symmetry
- Parameters from Novoderezhkin & van Grondelle (2010)
- Nearest-neighbor couplings: $J \approx$ 300 cm⁻¹ (strong)
- Next-nearest: $J \approx$ −50 cm⁻¹

### Spectral Density

- Drude–Lorentz: $\lambda = 220$ cm⁻¹, $\gamma^{-1} = 50$ fs
- Underdamped mode at ~750 cm⁻¹ (C=C stretch)

### Filter Design

- B850 absorption band centered at ~850 nm
- Dual-band: ~840 nm and ~870 nm targeting upper and lower exciton bands
- FWHM: 15 nm

### Computational Cost

- ~24 hours per trajectory (18 sites)
- 100 disorder realizations: ~100 days single-core, ~10 days with 12 threads
- Reduced validation suite: ~1 week total

### Manuscript Integration

- Major new subsection in Results
- Significant SI section (parameters, convergence, disorder)
- May push paper beyond JPCL 5-page limit → consider as follow-up paper

### Effort: ~1–2 weeks

---

## Option C: Organic PV Donor–Acceptor Dimer

### System Description

A 2-site donor–acceptor model representing a generic organic photovoltaic heterojunction (e.g., P3HT:PCBM-like).

### Hamiltonian

| Parameter | Value | Source |
|---|---|---|
| $\varepsilon_D$ (donor) | 0 cm⁻¹ | Reference |
| $\varepsilon_A$ (acceptor) | −1500 cm⁻¹ | Typical LUMO offset |
| $J_{DA}$ | 200 cm⁻¹ | Charge-transfer coupling |

### Spectral Density

- Higher reorganization: $\lambda = 200$ cm⁻¹
- Underdamped C=C stretch: $\omega_v = 1400$ cm⁻¹, $\lambda_v = 50$ cm⁻¹
- Temperature: 300 K

### Filter Design

- Absorption in UV-vis range (~500–600 nm)
- Filter targeting donor S₁ + C=C stretch resonance

### Computational Cost

- 2 sites → very fast (~30 min per trajectory)
- 100 realizations: ~50 hours

### Manuscript Integration

- Brief new subsection in Results (~1 paragraph)
- Short SI section
- Strong narrative: "bridges biological and artificial systems"

### Risks

- Less established Hamiltonian parameters
- Reviewers may question whether a 2-site model captures OPV physics

### Effort: ~3 days

---

## Recommendation

**Option A (3-site model)** is optimal for JPCL because:

1. Fits within the 5-page limit
2. Cleanly isolates the mechanism from FMO-specific details
3. Compute time is negligible
4. Provides the negative control (off-resonant filter → no enhancement) that reviewers will want
5. Option B (LH2) is better suited as a standalone follow-up paper
