---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: [
  'Redac_Paper2/_bmad-output/planning-artifacts/prd.md',
  'Redac_Paper2/_bmad-output/planning-artifacts/architecture.md',
  'Redac_Paper2/project_ideas.md',
  'Redac_Paper2/_bmad-output/brainstorming/brainstorming-session-2026-06-16-0750.md'
]
status: 'complete'
completedAt: '2026-06-16'
---

# Quantum Agrivoltaic PT-HOPS Paper 2 - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for the Paper 2 project, decomposing the requirements from the PRD and Architecture into implementable developer stories.

## Requirements Inventory

### Functional Requirements

FR1: Modélisation FMO à 8 sites de BChl a + puits de capture irréversible pour le Centre Réactionnel ($H_{trap} = -i \Gamma_{RC}$) avec métrique $\Phi_{FT}$ intégrée.
FR2: Architecture polaritonique NPoM ($V < 1 \text{ nm}^3$) avec barrière de graphène et diagnostics SERS moléculaires in situ non destructifs.
FR3: Dynamique non-markovienne PT-HOPS/SBD + commutateurs d'auto-protection (désaccord Stark de Floquet et OMIT).
FR4: Modèle microclimatique FAO-56 Penman-Monteith de bouclier thermique (Smart Shield) réduisant l'évapotranspiration.
FR5: Évaluation LCA avec unité fonctionnelle combinée ($\text{kWh} \cdot \text{kg}_{\text{crop}} / \text{m}^2 \cdot \text{yr}$) et calcul du NEB (Net Ecological Benefit).
FR6: Réseau IoT de capteurs quantiques à points quantiques (GQDs/CQDs) détectant l'eau, les métaux lourds et nutriments + algorithme ML d'irrigation.
FR7: Atténuation de la "fracture quantique" par des subventions échelonnées et des coopératives agricoles pour petits exploitants.
FR8: Sécurisation de la télémétrie IoT par protocole de cryptographie quantique QKD BB84.

### NonFunctional Requirements

NFR1: Préservation de la trace quantique et positivité des populations sous dynamics non-markovienne.
NFR2: Audit de convergence automatique (L-audit et K-audit) avant validation des trajectoires de production.
NFR3: Latence et consommation énergétique réduites du chiffrement QKD BB84 sur les nœuds IoT ruraux.
NFR4: Protection contre les divergences numériques (NaN/Inf) sous couplages plasmoniques extrêmes.
NFR5: Analyse d'amortissement CAPEX et évaluation de viabilité économique à long terme.

### Additional Requirements

AR1: Schéma de validation Pydantic pour `parameters.yaml` à l'initialisation.
AR2: Sérialisation HDF5 avec arborescence normalisée (`/dynamics/populations`, `/dynamics/rc_yield`, `/metadata/parameters`).
AR3: Structure modulaire Custom Monorepo Python (`src/quantum_interface`, `src/microclimate`, `src/lca`, `src/iot_security`).
AR4: Règle stricte de conversion d'indexation (indices physiques FMO 1-8 vers indices Python 0-7).
AR5: Tests unitaires isolés dans `tests/unit/` sous framework `pytest`.

### UX Design Requirements

Aucun (Règles intégrées dans les visualisations du thème et l'intégrité de la télémétrie).

### FR Coverage Map

- **FR1 (8-Site FMO & RC Trap)**: Epic 2 - Microscopic Quantum Dynamics Solver
- **FR2 (NPoM Interface & SERS)**: Epic 2 - Microscopic Quantum Dynamics Solver
- **FR3 (PT-HOPS/SBD & NPQ Switch)**: Epic 2 - Microscopic Quantum Dynamics Solver
- **FR4 (Serres PM Microclimate)**: Epic 3 - Crop Microclimate & Macroscopic LCA Engine
- **FR5 (Functional Unit & NEB)**: Epic 3 - Crop Microclimate & Macroscopic LCA Engine
- **FR6 (GQD Sensors & ML Irrigation)**: Epic 4 - Precision IoT Sensing & QKD Security
- **FR7 (Socio-Economic & Cooperatives)**: Epic 3 - Crop Microclimate & Macroscopic LCA Engine
- **FR8 (QKD BB84 Cybersecurity)**: Epic 4 - Precision IoT Sensing & QKD Security

## Epic List

### Epic 1: Project Initialization & Environment Setup
Initialize the custom monorepo Python structure, define validation schemas using Pydantic for parameters, and setup the testing infrastructure.
**FRs covered:** AR1, AR3, AR5

### Epic 2: Microscopic Quantum Dynamics Solver
Implement the 8-site Hamiltonian wrapper with reaction center trapping, time-dependent Floquet Stark driving, OMIT optomecanics, and non-destructive SERS diagnostics.
**FRs covered:** FR1, FR2, FR3, NFR1, NFR2, NFR4, AR2, AR4

### Epic 3: Crop Microclimate & Macroscopic LCA Engine
Implement the FAO-56 Penman-Monteith greenhouse evapotranspiration calculator, the combined LCA functional unit, NEB, and the socioeconomic cooperative amortization model.
**FRs covered:** FR4, FR5, FR7, NFR5

### Epic 4: Precision IoT Sensing & QKD Security
Develop the fluorescent GQD multi-target detection model, ML automated irrigation logic, and simulated BB84 QKD protocol secure telemetry channel.
**FRs covered:** FR6, FR8, NFR3

---

## Epic 1: Project Initialization & Environment Setup

### Story 1.1: Repository Structure Setup
As a quantum agrivoltaics researcher,
I want to initialize the custom monorepo directory structure and configure pytest,
So that the codebase remains modular, clean, and testable from day one.

**Acceptance Criteria:**
* **Given** the repository root directory `Redac_Paper2`
* **When** I run directory checks
* **Then** the packages `src/quantum_interface`, `src/microclimate`, `src/lca`, `src/iot_security`, `tests/unit`, and `data/converged` must contain initial dummy modules/classes and `__init__.py` files.
* **And** running `pytest` from the root directory must pass successfully.

### Story 1.2: Configuration Validation with Pydantic
As a simulation developer,
I want to define a strict physical and agronomical parameter validation schema using Pydantic to parse parameters.yaml,
So that invalid model constants or types are detected before simulation run.

**Acceptance Criteria:**
* **Given** a `parameters.yaml` file containing simulation inputs (FMO site energies, plasmonic volume, FAO-56 crop coefficients)
* **When** the schema validation script loads the file
* **Then** Pydantic must enforce data types, presence of required keys, and boundary conditions (e.g., $V_{\text{mode}} > 0$).
* **And** any invalid value must raise a validation error and abort configuration loading.

---

## Epic 2: Microscopic Quantum Dynamics Solver

### Story 2.1: 8-Site FMO Hamiltonian & RC Trap
As a quantum physicist,
I want to implement the 8-site Hamiltonian model of the FMO complex with an anti-Hermitian trapping term on sites 3 and 4 representing the reaction center,
So that I can calculate the forward transfer yield $\Phi_{FT}$.

**Acceptance Criteria:**
* **Given** an 8-site FMO site energy structure parameterized from the configuration loader
* **When** propagating dynamics using a non-Hermitian reaction center sink term $H_{trap} = -i \Gamma_{RC} \sum_{j \in \{3,4\}} |j\rangle\langle j|$
* **Then** the total population of the FMO complex must decay over time as excitation gets captured.
* **And** the transfer yield metric $\Phi_{FT} = 2 \Gamma_{RC} \int_0^{t_{max}} \sum_{j \in \{3,4\}} P_j(t) dt$ must converge to a value between 0.0 and 1.0.

### Story 2.2: NPoM Picocavity & Strong Coupling Dynamics
As a nanophysicist,
I want to couple the 8-site FMO transitions and the OPV excitons to a localized surface plasmon mode within a sub-nanometer NPoM picocavity with a graphene monolayer barrier,
So that I can model strong coherent coupling at 295 K.

**Acceptance Criteria:**
* **Given** a NPoM mode volume parameter $V_{\text{mode}}$
* **When** $V_{\text{mode}} \to 0$ in the coupling calculations
* **Then** the system must cap the coupling constant $g_0$ using a high-value guardrail to avoid numerical divergence.
* **And** the Hamiltonian construction must explicitly set Dexter-type charge transfer terms to zero to model the shielding effect of the graphene barrier.

### Story 2.3: Floquet Stark Detuning & OMIT Auto-Protection Switch
As a control systems modeler,
I want to implement a dynamic Stark detuning driving term using Floquet theory and an OMIT transmission switch,
So that FMO is shielded from exciton overload under high solar flux.

**Acceptance Criteria:**
* **Given** an incoming solar flux that exceeds the photo-protection threshold
* **When** the time-dependent driving field $V(t) \cos(\omega t)$ shifts excitonic levels out of resonance
* **Then** energy transfer to the FMO complex must drop (Stark detuning).
* **And** at zero solar flux (night mode), the time-dependent terms must gracefully drop to zero without division-by-zero errors.

### Story 2.4: SERS Molecular Optomechanical Diagnostics
As a quantum measurement theorist,
I want to model the Surface-Enhanced Raman Scattering (SERS) signal using molecular cavity optomechanics,
So that I can calculate the in situ non-destructive diagnostic readouts.

**Acceptance Criteria:**
* **Given** the calculated density matrix $\rho(t)$ of the 8-site FMO complex
* **When** calling the SERS diagnostic module
* **Then** the script must return a simulated Raman intensity spectrum that varies characteristically depending on the population of specific BChl a sites.

### Story 2.5: Numerical Stability Audit & HDF5 Serialization
As a scientific data engineer,
I want to audit trajectory trace preservation, run convergence checks, and serialize trajectory populations to a standardized HDF5 output format,
So that raw simulation datasets are verified for physical correctness and cleanly stored.

**Acceptance Criteria:**
* **Given** a finished non-Markovian PT-HOPS/SBD simulation trajectory
* **When** performing the automated audit (checks on trace preservation and positive semi-definiteness)
* **Then** any physical violation must trigger a log entry in `solver_errors.log`.
* **And** the output files must be saved in `data/converged/` using the HDF5 group path structure `/dynamics/populations`, `/dynamics/rc_yield`, and `/metadata/parameters`.

---

## Epic 3: Crop Microclimate & Macroscopic LCA Engine

### Story 3.1: FAO-56 Serres PM Evapotranspiration Calculator
As an agricultural modeler,
I want to implement the FAO-56 Penman-Monteith crop evapotranspiration model parameterized for shaded greenhouse environments,
So that I can calculate the water saving index and crop temperature relief.

**Acceptance Criteria:**
* **Given** weather input variables (solar irradiance, temperature, relative humidity, wind speed)
* **When** calculating crop evapotranspiration $ET_c$ under an OPV selective filter
* **Then** the net radiation $R_n$ must be adjusted according to the selective spectral transmission (blocking NIR/UV).
* **And** the crop water use must show a quantified reduction compared to the open-field control.

### Story 3.2: Combined Functional Unit & NEB Aggregator
As a lifecycle assessment analyst,
I want to compute the Net Ecological Benefit (NEB) using a combined functional unit ($\text{kWh} \cdot \text{kg}_{\text{crop}} / \text{m}^2 \cdot \text{yr}$),
So that I can compare quantum agrivoltaics against static systems and open agricultural land.

**Acceptance Criteria:**
* **Given** microscopic simulation results (excitonic yield $\Phi_{FT}$) and mesoscopic irrigation savings
* **When** scaling these parameters into Scenario A (Quantum OPV), Scenario B (static shading), and Scenario C (open field)
* **Then** the NEB aggregator must compute net displaced carbon, biomass production, and water savings.
* **And** the microscopic efficiency $\Phi_{FT}$ must act as a direct scaling multiplier for the crop light harvesting term.

### Story 3.3: Quantum Divide & Socioeconomic Amortization Analysis
As a socioeconomic researcher,
I want to evaluate CAPEX amortization and cooperative ownership models for agrivoltaics,
So that I can formulate policy recommendation criteria that mitigate the technology access gap (Quantum Divide) for smallholders.

**Acceptance Criteria:**
* **Given** capital expenditure (CAPEX) inputs for sub-nanometer plasmonic OPV systems
* **When** simulating payback period under cooperative cost-sharing and carbon-linked tiered subsidies
* **Then** the socioeconomic module must calculate the return on investment (ROI).
* **And** under the optimal cooperative scenario, the CAPEX amortization time must be less than 7 years.

---

## Epic 4: Precision IoT Sensing & QKD Security

### Story 4.1: Fluorescent Graphene Quantum Dot (GQD) Sensor Network
As an agricultural sensor engineer,
I want to model the fluorescence response of a soil-embedded network of GQDs and CdTe/ZnSe core-shell quantum dots,
So that I can simulate multi-target detection of water content, nutrient deficiencies, and contaminants.

**Acceptance Criteria:**
* **Given** physical inputs representing soil water content, heavy metals ($Pb^{2+}$), and pesticide residues
* **When** evaluating the fluorescent intensity shift and emission wavelength changes of the GQD model
* **Then** the sensor simulator must output a multiplexed telemetry data signature.
* **And** the detection limits for heavy metals and pesticides must comply with standard literature thresholds.

### Story 4.2: Machine Learning Automated Irrigation Controller
As a smart farming algorithm developer,
I want to implement a machine learning classifier to process multi-spectral GQD sensor signals,
So that I can trigger automated irrigation commands upon early detection of plant water stress.

**Acceptance Criteria:**
* **Given** a simulated stream of time-series multiplexed GQD telemetry data
* **When** the classifier analyzes the spectral features
* **Then** it must predict the crop water stress level before visible physiological damage occurs.
* **And** the model must trigger automated irrigation valve signals to adjust water supply dynamically.

### Story 4.3: Lightweight BB84 QKD Cryptography Module
As an IoT cybersecurity developer,
I want to simulate a lightweight BB84 QKD protocol including polarization state exchange, sifting, and error correction,
So that the IoT sensor telemetry transmission is protected against interception.

**Acceptance Criteria:**
* **Given** a noisy quantum communication channel between the agricultural IoT node and the cloud server
* **When** executing the BB84 simulation protocol to establish a symmetric key
* **Then** the system must calculate the Quantum Bit Error Rate (QBER) and abort key generation if QBER exceeds 11%.
* **And** if the key generation fails, the system must trigger a fail-safe offline irrigation routine.
* **And** the runtime overhead of the simulation must be optimized to run within constraints of resource-limited IoT node models.
