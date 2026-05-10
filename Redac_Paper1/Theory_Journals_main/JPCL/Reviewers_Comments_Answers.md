# Consolidated Response to Reviewers
**Manuscript ID:** jz-2026-00994t
**Title:** "Quantum-coherent spectral engineering: non-Markovian dynamics in photosynthetic energy transfer under engineered photon baths"

This document consolidates our point-by-point responses to the reviewers' comments, removing redundancies and ensuring consistency across all explanations, adhering to the latest project parameters.

---

## Reviewer 1

**Comment 1.1:** *The authors claim to employ the Process Tensor Hierarchy of Pure States (PT-HOPS), yet the acknowledgment and data availability sections explicitly reference the MesoHOPS library. These are not identical methods. Could the authors provide a more detailed and self-contained account of the precise algorithm used...?*

**Draft Answer:** 
We have clarified the relationship between the formalism and the software in the Methods section. PT-HOPS (Process Tensor Hierarchy of Pure States) is the theoretical non-perturbative formalism we use to handle non-Markovian memory without exponential scaling. MesoHOPS (v1.6) is the specific open-source software library utilized for the implementation. We highlight that our implementation leverages the Stochastically Bundled Dissipators (SBD) approach within MesoHOPS to achieve size-invariant scaling $O(1)$, making it computationally tractable for complex systems.

**Comment 1.2:** *The paper's defining claim—"spectral bath engineering"—is fundamentally misleading. The observed differences in dynamics are the trivially expected consequence of preparing different initial states.*

**Draft Answer:** 
We agree with the reviewer's point that our laser pulse is treated classically and does not alter the electromagnetic vacuum density of states. Following Reviewer 2's suggestion, we have updated our terminology throughout the manuscript to **"quantum control via selective vibronic excitation"** instead of "bath engineering." However, to clarify that this is more than just a trivial initial state preparation, we expanded the theoretical section to explain our two-stage mechanism: (1) Selective vibronic driving prepares polaron-dressed states. (2) In the polaron frame, the resonant vibronic modes shift into the "system", reducing the residual reorganization energy ($\lambda_{res}$) by 25%. This actively slows the rate of decoherence during the subsequent transport phase.

**Comment 1.3:** *Figure 1 is insufficiently detailed... axis labels and tick marks for panels (a)–(d) are either missing or illegible—the x-axis numbering and units cannot be discerned.*

**Draft Answer:** 
We have completely overhauled Figure 1 to meet JPCL standards (600 DPI). All panels now feature clearly labeled axes with explicit units ("Time [fs]"). We have also increased font sizes and ensured all tick marks and labels are fully legible.

**Comment 1.4:** *Figure 2(a): physically unmotivated temperature profile. The x-axis... is labeled "Time (days)" and spans 0 to 350, apparently representing a seasonal temperature cycle. This presentation is puzzling and physically irrelevant...*

**Draft Answer:** 
We recognize the confusion caused by mixing macroscopic agricultural timescales with femtosecond quantum dynamics. We have replaced the seasonal "Time (days)" cycle with physically motivated static temperature sweeps (ranging from cryogenic up to physiological temperatures at 295 K). This correctly decouples the microscopic ultrafast quantum dynamics from the macroscopic environmental factors.

**Comment 1.5:** *The paper contains directly contradictory specifications for key numerical parameters. The main text states L=10 with K=4... SI Table S1 lists L=6, K=6. Furthermore, SI Test 1 reports 0.9% deviation... while Table S4 lists 1.2%.*

**Draft Answer:** 
We sincerely apologize for these typographical and reporting inconsistencies, which were remnants of early parameter convergence sweeps. We have now strictly synchronized all truncation parameters across the manuscript, SI, and our codebase. All final production benchmarks strictly use a Hierarchy Depth of **$L=8$** and **$K=2$** Matsubara terms, with a time step of $\Delta t = 1.0$ fs. We have added a physically-motivated justification for the $K=2$ truncation in SI Section S2.3, noting that at room temperature, the dynamics are dominated by explicit vibronic modes rather than high-order Matsubara corrections, with a Mean Absolute Error (MAE) of $3.42 \times 10^{-5}$ compared to $K=3$.

---

## Reviewer 2

**Comment 2.1:** *The term of 'bath-engineering' is misleading... a proper description of the study will be ‘quantum control of light-harvesting energy transfer via initial excitation’.*

**Draft Answer:** 
We thank the reviewer for providing this precise terminology. As noted in our response to Reviewer 1, we have updated the abstract and manuscript text to use "quantum control via selective vibronic excitation" and removed references to "bath engineering".

**Comment 2.2:** *Vibronic coherence in light-harvesting energy transfer has been explored extensively by Graham Fleming... Greg Scholes... In these studies, vibronic resonance is identified as a possible mechanism for efficient energy transfer...*

**Draft Answer:** 
We appreciate the pointer to these foundational works. We have added the suggested references (Fleming 2015, Scholes 2015) to our bibliography and explicitly cited them in the Introduction and Discussion sections to acknowledge prior identification of vibronic resonance as a key mechanism for efficient transfer.

**Comment 2.3:** *Is the spectral density used in Eq. (3) based on a realistic modelling of FMO? Several groups including David Coker and Ulrich Kleinekathöfer have carried out detailed numerical modelling...*

**Draft Answer:** 
Yes, we have clarified our discussion of the spectral density to emphasize its biological realism. The $J(\omega)$ employed is based on the robust **12-mode Kleinekathöfer/Coker model**. It explicitly includes a continuous, overdamped Drude-Lorentz component ($\lambda_D = 35$ cm$^{-1}$, $\gamma_D = 50$ cm$^{-1}$) at 295 K to model the protein-solvent medium fluctuations, in addition to the specific vibronic resonances.

**Comment 2.4:** *The authors refer to environment-assisted quantum transport (ENAQT) extensively... In the context of the current study, can the vibronic coupling or laser excitation be optimized?*

**Draft Answer:** 
We have cited the ENAQT literature (Wu et al. 2010). In the revised text, we discuss how our selective laser excitation can be co-optimized with environmental factors to navigate the parameter space toward maximal energy transfer efficiency, conceptually extending the ENAQT framework.

**Comment 2.5:** *FMO serves as a linker between the base-plate and reaction center in the green bacteria and is not directly exposed to sunlight. Thus, the proposed coherent excitation may be relevant in laser control experiments but not in the biological setting.*

**Draft Answer:** 
We entirely agree. We have revised the text to clarify that the proposed coherent excitation scheme is highly relevant for ultrafast laser control experiments (e.g., using 2DES with pulse shaping) and artificial bio-inspired light-harvesting architectures (such as our agrivoltaic concept), rather than asserting that this precise coherent excitation occurs natively in the biological setting.

---

## Reviewer 3

**Comment 3.1:** *...omits important information regarding key features of the suggested process... the functional form of the time-dependent field amplitude and its timing relative to photoexcitation are not given.*

**Draft Answer:** 
In the revised Theoretical Framework and SI Section S1.1, we have now explicitly defined the laser pulse. The temporal envelope is defined as a Gaussian $E(t) = E_0 \exp(-t^2/2\sigma_t^2)$ with a Full Width at Half Maximum (FWHM) duration of 50 fs, centered exactly at $t = 0$.

**Comment 3.2:** *...cannot identify the coherence enhancement... in Figure 1, where each panel shows a single noisy line (not a comparison) without time units...*

**Draft Answer:** 
We have fundamentally redesigned Figure 1. Time units ("Time [fs]") are now explicitly included on all x-axes. Instead of separate lines, we now **overlay** the "Broadband" (reference) and "Filtered" results in the same panel using distinct line styles (solid vs. dashed) for direct comparison. We also included an inset plotting the difference to visually highlight the reported 20–50% enhancement in coherence lifetime.

**Comment 3.3:** *...model spectral density employed... which has four peaks, is not representative of the true spectral density of bacteriochlorophyll molecules... Huang-Rhys factors used... are quite small...*

**Draft Answer:** 
We clarify in the revised text that our simulations actually utilize a more comprehensive **12-mode model** based on the Kleinekathöfer/Coker parameters, not just 4 isolated peaks. Importantly, as detailed in our response to Reviewer 2, this spectral density includes the requisite overdamped Drude-Lorentz component ($\lambda_D = 35$ cm$^{-1}$, $\gamma_D = 50$ cm$^{-1}$) representing the low-frequency solvent/protein medium, ensuring standard biological realism.

**Comment 3.4:** *...unclear to me whether the simulation results are exact, as claimed. The method employed involves many adjustable/truncation parameters.*

**Draft Answer:** 
We have elevated the visibility of our rigorous "12-test validation suite" (SI Section S3). We clarify that the HOPS method is **"formally exact"** because it rigorously converges to the exact solution of the stochastic Schrödinger equation as hierarchy depth ($L$) and Matsubara terms ($K$) increase. Using our now globally synchronized production parameters ($L=8, K=2$), our dedicated `audit_convergence.py` confirms trace preservation and positivity, mathematically validating the accuracy of the integration.
