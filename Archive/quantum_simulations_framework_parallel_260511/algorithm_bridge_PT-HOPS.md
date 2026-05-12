# Algorithm Bridge: PT-HOPS and SBD Integration

**Date:** May 2026  
**Context:** Quantum Agrivoltaics Simulation Framework (JPCL Revision)

## 1. Introduction

This document serves as a "bridge" to elucidate the exact algorithmic pathway utilized in our simulation framework. The framework unifies the **Hierarchy of Pure States (HOPS)**, the **Process Tensor (PT)** formalism, and **Stochastically Bundled Dissipators (SBD)**. This unification is crucial for modeling non-Markovian dynamics in the Fenna-Matthews-Olson (FMO) complex under realistic, multi-mode spectral densities without hitting the exponential memory wall of standard density matrix approaches.

## 2. Core Formalisms

### 2.1 The HOPS Approach
Standard HOPS transforms the non-Markovian stochastic Schrödinger equation (NMSSE) into a deterministic hierarchy of coupled wavefunctions:
$ \partial_t |\psi^{(\vec{k})}\rangle = \hat{H}_{eff} |\psi^{(\vec{k})}\rangle + \text{coupling terms} $

Where:
- $\hat{H}_{eff}$ includes the non-Hermitian system Hamiltonian.
- The hierarchy depth $L$ controls the exactness of the memory kernel.

**Limitation:** As the number of bath modes (e.g., the 12-mode Kleinekathöfer/Coker model) increases, the hierarchy size explodes factorially, making $L=10$ computationally impossible on a local 32GB workstation using standard HOPS.

### 2.2 Stochastically Bundled Dissipators (SBD)
While MesoHOPS natively provides Adaptive Basis filtering (maintaining an active "tube" of basis states to solve the state-space explosion), the number of physical modes can still cause memory overflows. Our framework introduces **Stochastically Bundled Dissipators (SBD)** (`extensions/stochastic_bundling.py`) to solve this. Instead of associating a hierarchy index with each individual bath pole from the Kleinekathöfer/Coker spectral density, SBD performs dynamic K-Means clustering to aggregate correlation function poles into a condensed set of "bundles" (e.g., `n_bundles=5`), drastically reducing the required memory footprint while preserving the effective system-bath coupling.

## 3. The PT-HOPS Integration

While SBD solves the memory wall, calculating exact multi-time correlation functions for external laser pulse sequences requires separating the system dynamics from the bath influence. We introduce the **Process Tensor (PT)** interface:

1. **Stochastic Unraveling (The Noise Engine):**
   The PT-HOPS algorithm unravels the bath correlation function into a set of pseudo-random Gaussian noise trajectories ($\eta(t)$).
   
2. **Process Tensor Construction:**
   Instead of calculating the density matrix immediately, the solver constructs a Process Tensor $\mathcal{T}$ that mathematically encodes all environmental non-Markovian memory up to time $t$.

3. **External Interventions (Selective Vibronic Driving):**
   The external laser pulse (defined in `constants.py`) acts purely on the system Hamiltonian $\hat{H}_S(t)$. Because the bath is encoded in $\mathcal{T}$, the external field does not require recalculating the environmental memory kernel.

## 4. Algorithmic Pipeline (`hops_simulator.py`)

1. **Initialization:**
   - The FMO Hamiltonian is constructed and mean-centered to prevent rapid numerical oscillations.
   - The realistic 12-mode spectral density is converted via exponential decomposition (`bcf_convert_dl_to_exp`).

2. **Trajectory Generation:**
   - The simulator initializes the `HopsTrajectory` with $L=10$ and $K=10$ Matsubara terms.
   - The SBD filter is engaged (`use_sbd=True`), restricting the active hierarchy state space.
   - The PT noise adapter (`PT_HopsNoise`) injects the correlation memory.

3. **Propagation & Averaging:**
   - The trajectory is integrated using an adaptive Runge-Kutta scheme.
   - The final density matrix is constructed by taking the ensemble average of the pure state outer products: $\rho(t) = \mathbb{E}[|\psi(t)\rangle \langle\psi(t)|]$.

## 5. Verification Constraints

The convergence audit (`audit_convergence.py`) enforces strict validation on the resulting dynamics:
- **Trace Preservation:** $\sum_i \rho_{ii}(t) = 1.0 \pm 10^{-5}$
- **Positivity:** $\min(\rho_{ii}(t)) \ge 0$
- **Hierarchy Convergence:** MAE between $L=10$ and $L=11$ remains beneath the threshold.
