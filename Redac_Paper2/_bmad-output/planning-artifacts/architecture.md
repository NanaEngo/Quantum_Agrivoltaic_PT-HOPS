---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments: [
  'Redac_Paper2/_bmad-output/planning-artifacts/prd.md',
  'Redac_Paper2/project_ideas.md',
  'Redac_Paper2/_bmad-output/brainstorming/brainstorming-session-2026-06-16-0750.md'
]
workflowType: 'architecture'
project_name: 'Quantum_Agrivoltaic_PT-HOPS_Paper2'
user_name: 'Taamangtchu'
date: '2026-06-16'
status: 'complete'
completedAt: '2026-06-16'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
L'architecture doit lier de manière cohérente la physique microscopique (simulateur quantique d'interface OPV-FMO à 8 sites avec piège RC, désaccord Stark de Floquet et modulation OMIT sous PT-HOPS/SBD) et l'ingénierie macroscopique (LCA multi-échelle avec unité fonctionnelle combinée, modèle microclimatique de serre Smart Shield FAO-56, réseau IoT de capteurs quantiques à GQDs avec automatisation par IA, et sécurité par cryptographie QKD).

**Non-Functional Requirements:**
- **Stabilité Numérique & Convergence :** Préservation de la trace et audit de convergence pour les propagations non-markoviennes à 295 K.
- **Sécurité et Intégrité des Données :** Transmission chiffrée de la télémétrie IoT via QKD sans impact rédhibitoire sur la latence des nœuds ruraux.
- **Accessibilité Socio-Économique :** Analyse d'amortissement CAPEX et modèles de coopératives pour atténuer la "fracture quantique".

**Scale & Complexity:**
- Primary domain : Simulation Quantique Multi-échelle, Analyse de Cycle de Vie (LCA) et IoT sécurisé.
- Complexity level : Élevé (Interdisciplinarité combinant physique quantique ouverte, agronomie, cryptographie et analyse environnementale).
- Estimated architectural components : 5 (Quantum Dynamics Solver, SERS/Optomechanics Diagnostics, Crop Microclimate & LCA Evaluator, GQD-AI Precision Irrigation, QKD Cryptography IoT Module).

### Technical Constraints & Dependencies
- Conda env `MesoHOP-sim` (Python 3.12+, MesoHOPS v1.7.0).
- Modèle FAO-56 Penman-Monteith standardisé pour le microclimat de la serre.
- Protocoles QKD légers pour les architectures de capteurs IoT à ressources limitées.

### Cross-Cutting Concerns Identified
- **Passage d'Échelles (Micro-to-Macro Mapping) :** Comment convertir mathématiquement l'efficacité de transfert quantique ($\Phi_{FT}$) simulée en gains de biomasse ($\text{kg}_{\text{crop}}$) dans le modèle microclimatique et la LCA.
- **Intégrité de la Télémétrie terrain-vers-cloud :** Gestion de la latence induite par le traitement local de l'IA de stress hydrique et le chiffrement QKD.

---

## Starter Template Evaluation

### Primary Technology Domain

Le projet relève du domaine des **Sciences Numériques Appliquées & Génie des Procédés Durables (Python Monorepo)**. Il nécessite un couplage fort entre des solveurs quantiques en temps réel (MesoHOPS en Python) et des modules d'analyse macroscopique (LCA, agronomie, cryptographie IoT).

### Starter Options Considered

1. **Custom Monorepo (Recommandé) :** Création d'une architecture modulaire Python sur mesure, héritant de l'environnement Conda `MesoHOP-sim` éprouvé dans le papier 1, mais structurée avec de nouvelles frontières étanches pour chaque discipline.
2. **Snakemake / Workflow Engine :** Utilisation d'un orchestrateur de flux de données scientifique. Bien qu'excellent pour la reproductibilité, il ajoute une surcouche de complexité inutile pour un pipeline linéaire.

### Selected Starter: Custom Research Monorepo (Python 3.12+)

**Rationale for Selection:**
L'utilisation d'une structure Custom Monorepo garantit une intégration transparente avec MesoHOPS v1.7.0 et le gestionnaire de paramètres centralisé (`parameters.yaml`), tout en permettant de modulariser proprement les nouveaux axes de recherche (SERS, LCA microclimatique, QKD et IA).

**Initialization Command:**
```bash
# Initialisation de la structure de répertoires locale sous Redac_Paper2
mkdir -p src/{quantum_interface,microclimate,lca,iot_security} tests/ data/converged logs/
touch parameters.yaml src/quantum_interface/solver.py src/microclimate/fao56.py src/lca/neb.py src/iot_security/qkd.py
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
- Python 3.12+ (exécuté dans l'environnement Conda `MesoHOP-sim`).
- Rigueur de typage (Type Hints) et docstrings de style NumPy pour tous les nouveaux modules.

**Testing Framework:**
- `pytest` pour les tests unitaires physiques (stabilité numérique) et cryptographiques.

**Code Organization:**
- Découpage strict en quatre packages sous `src/` :
  - `quantum_interface/` : Solveur 8 sites, désaccord Stark de Floquet, NPoM, OMIT et diagnostics SERS.
  - `microclimate/` : Modélisation FAO-56 Penman-Monteith.
  - `lca/` : Calcul du Bénéfice Écologique Net (NEB) et de l'unité fonctionnelle hybride.
  - `iot_security/` : Télémétrie ML et distribution de clés QKD.
- `parameters.yaml` à la racine comme unique source de vérité (Single Source of Truth).

---

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- **Data Architecture (HDF5 & YAML) :** Validation rigoureuse du schéma `parameters.yaml` avant initialisation. Sortie des propagations quantiques au format HDF5 (`.h5` avec `h5py` v3.11+) pour stocker les matrices de densité $\rho(t)$ à 8 sites et l'accumulation dans le piège RC.
- **Modèle Quantique (MesoHOPS & Floquet Stark) :** Formalisation de l'hamiltonien à 8 sites et du désaccord Stark de Floquet comme un terme dépendant du temps dans le solveur enveloppe.
- **Réseau IoT Chiffré par QKD :** Modélisation en Python du protocole BB84 pour la génération de clés chiffrées protégeant la transmission de télémétrie.

**Important Decisions (Shape Architecture):**
- **Calcul de $\Phi_{FT}$ :** Intégration temporelle exacte via quadrature de Simpson des populations des sites 3 et 4 dans le piège RC.
- **Modèle Microclimatique FAO-56 :** Implémentation de l'équation de Penman-Monteith sous forme de module Python stateless (`src/microclimate/fao56.py`) alimenté par les coefficients de transmission calculés de l'OPV.

### Data Architecture
- **Format de Sortie :** HDF5 avec groupes structurés par scénario (ex: `/scenario_a/dynamics`).
- **Data Validation :** Utilisation de Pydantic pour valider à la fois les paramètres physiques de la simulation et les variables d'entrée de la LCA.

### Authentication & Security
- **Sécurisation IoT :** Simulation du protocole de cryptographie quantique BB84 (échange de bits polarisés, réconciliation de clés et amplification de confidentialité) pour authentifier les capteurs quantiques à GQDs.

### API & Communication Patterns
- **Interfaces Python :** Communication interne entre les packages via des APIs fortement typées. `lca/neb.py` fait office d'orchestrateur de haut niveau, appelant séquentiellement le module quantique, le module microclimatique et le module de sécurité pour calculer le bénéfice écologique net (NEB).

### Infrastructure & Deployment
- **Environnement d'exécution :** Isolation totale dans l'environnement Conda `MesoHOP-sim`. Validation sur serveur requérant l'allocation de ressources via le planificateur de mémoire (scheduler) développé dans le papier 1 pour éviter les OOM.

---

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
- **Accès aux constantes physiques :** Risque de codage en dur de variables (ex. les couplages de Franck-Condon ou la constante $\Gamma_{RC}$) au lieu de passer par le validateur YAML.
- **Indexation des sites FMO (1-indexed vs 0-indexed) :** Le formalisme physique utilise l'indexation 1-8 pour les BChl a. Le code Python MesoHOPS doit convertir cela rigoureusement en indices 0-7, sans ambiguïté dans les boucles de calcul.
- **Structure interne des HDF5 :** Des agents différents pourraient nommer les groupes HDF5 différemment.

### Naming Patterns

**Code Naming Conventions:**
- Variables et fonctions : `snake_case` (ex: `calculate_reaction_center_yield()`).
- Classes : `CamelCase` (ex: `FmoSolverWrapper`).
- Fichiers source : `snake_case` (ex: `fao56_calculator.py`).

**HDF5 Node Paths (Standardization) :**
- Données dynamiques de population : `/dynamics/populations` (matrice `[time_steps, 8_sites]`).
- Rendement cumulé du piège RC : `/dynamics/rc_yield` (vecteur `[time_steps]`).
- Métadonnées et paramètres de la simulation : `/metadata/parameters` (dictionnaire sérialisé).

### Structure Patterns

**Project Organization:**
- Tous les tests unitaires doivent résider dans le répertoire `tests/` de la racine du projet (pas de co-localisation des tests dans le dossier source).
- L'orchestrateur de haut niveau `neb.py` doit être le seul point d'entrée pour la compilation des résultats de la LCA.

### Process Patterns

**Enforcement Guidelines (Règles obligatoires pour les agents) :**
- **Zéro valeur physique en dur :** Tous les paramètres physiques du système (température, couplages, taux de piégeage, etc.) doivent impérativement être extraits de l'objet de configuration YAML validé par Pydantic.
- **Gestion des NaN/Inf :** Le solveur et l'intégrateur de la LCA doivent inclure des protections explicites contre les instabilités numériques (ex. NaN causés par des pas de temps mal adaptés sous Floquet), avec journalisation automatique dans `logs/solver_errors.log`.
- **Règle de conversion d'indexation :** Tout commentaire ou variable manipulant l'indice d'un site FMO doit spécifier s'il s'agit du modèle physique (site 1-8) ou de l'indice de l'implémentation (index 0-7).

### Graph of Thoughts & Edge Cases Enhancements

**Graph of Thoughts (Interconnexion Micro-Macro) :**
- **Liaison Quantique-Agronomique :** Le rendement quantique microscopique $\Phi_{FT}$ (calculé par le solveur FMO 8 sites) doit servir de facteur d'échelle multiplicatif direct pour l'efficacité de conversion lumineuse dans le calcul du gain de biomasse végétale ($\text{kg}_{\text{crop}}$).
- **Boucle de rétroaction Stark/Floquet :** La fréquence de désaccord dynamique Stark de Floquet $\omega(t)$ induite par l'OPV doit modifier dynamiquement le coefficient d'absorption spectrale de la canopée sous-jacente dans le calcul de l'évapotranspiration $ET_c(t)$ de Penman-Monteith.
- **Dépendance Télémétrie-Sécurité :** Le taux de génération de clés QKD $R_{key}(t)$ régit la fréquence d'actualisation des décisions de l'IA d'irrigation. Si $R_{key}$ chute sous un seuil, le système doit basculer sur un mode d'irrigation locale "hors ligne" (fail-safe).

**Boundary & Edge Case Sweep (Cas Limites) :**
- **Cas limite $g_0 \to \infty$ (Volume de mode $V \to 0$ dans les picocavités) :** Imposer un seuil de coupure numérique supérieur dans `solver.py` pour éviter les divergences matricielles et les instabilités de propagation sous PT-HOPS.
- **Cas limite Éclairement Nul (Nuit / Éclipses) :** Le module Floquet doit désactiver complètement les termes dépendants du temps ($V(t) \to 0$) pour éviter des divisions par zéro dans les calculs d'interférence optique OMIT, revenant à un hamiltonien FMO statique standard.
- **Cas limite Épuisement des clés QKD (Bruit de champ élevé) :** Si la réconciliation de clés BB84 échoue, le module `iot_security/qkd.py` doit lever une exception capturée par `neb.py` qui force les vannes d'irrigation à utiliser un modèle local prédictif statique, empêchant le blocage de l'apport en eau des plantes.

---

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
Redac_Paper2/
├── parameters.yaml              # Source unique de vérité (YAML 1.2)
├── src/
│   ├── quantum_interface/       # [FR-1, FR-2, FR-3] Physique quantique et diagnostics NPoM
│   │   ├── __init__.py
│   │   ├── solver.py            # MesoHOPS wrapper à 8 sites et dynamique non-markovienne
│   │   ├── hamiltonian.py       # Définition de l'Hamiltonien de l'FMO et du piège RC
│   │   ├── pulse.py             # Formes d'onde Floquet et modulation Stark
│   │   └── diagnostics.py       # Modélisation optomécanique SERS in situ
│   ├── microclimate/            # [FR-4] Physique de la serre et agronomie
│   │   ├── __init__.py
│   │   └── fao56.py             # Calcul d'évapotranspiration FAO-56 Penman-Monteith
│   ├── lca/                     # [FR-5, FR-7] Évaluation de durabilité et socio-économie
│   │   ├── __init__.py
│   │   ├── neb.py               # Orchestration et intégration dynamique du NEB
│   │   └── database.py          # Modèles de subventions et d'amortissement CAPEX
│   └── iot_security/            # [FR-6, FR-8] Réseau de capteurs, ML et cryptographie
│       ├── __init__.py
│       ├── qkd.py               # Échange de clés quantiques BB84
│       └── sensing.py           # Analyse de stress hydrique par GQDs et IA d'irrigation
├── tests/
│   ├── unit/
│   │   ├── test_quantum_solver.py
│   │   ├── test_fao56.py
│   │   ├── test_lca_neb.py
│   │   └── test_qkd_security.py
├── data/
│   └── converged/               # Fichiers de sortie HDF5 (.h5)
└── logs/
    └── solver_errors.log        # Journal de stabilité numérique
```

### Architectural Boundaries

**API Boundaries:**
- Chaque package sous `src/` est strictement encapsulé. `quantum_interface` ne connaît ni le microclimat ni la LCA. Il reçoit une intensité lumineuse et renvoie une matrice de densité.
- `lca/neb.py` agit comme la seule passerelle qui interroge les APIs de tous les sous-composants pour agréger les calculs de bénéfice net.

**Data Boundaries:**
- Les fichiers HDF5 générés dans `data/converged/` sont l'unique pont persistant pour échanger les trajectoires de population quantique avec les visualisations ou l'audit de convergence.

### Requirements to Structure Mapping

- **Modèle FMO à 8 sites & Piège RC [FR-1] :** `src/quantum_interface/hamiltonian.py` et `solver.py`.
- **Diagnostics NPoM & SERS [FR-2] :** `src/quantum_interface/diagnostics.py`.
- **Désaccord Floquet Stark & OMIT [FR-3] :** `src/quantum_interface/pulse.py`.
- **Évapotranspiration FAO-56 [FR-4] :** `src/microclimate/fao56.py`.
- **Unité fonctionnelle LCA et NEB [FR-5] :** `src/lca/neb.py`.
- **Réseau de points quantiques & ML d'irrigation [FR-6] :** `src/iot_security/sensing.py`.
- **Fracture Quantique & Modèles Socio-Économiques [FR-7] :** `src/lca/database.py`.
- **Distribution Quantique de Clés QKD [FR-8] :** `src/iot_security/qkd.py`.

---

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
Toutes les technologies choisies (Python 3.12+, MesoHOPS v1.7.0, h5py v3.11+, Penman-Monteith agronomique, Pydantic, ML et BB84 QKD) sont compatibles et isolées au sein du Custom Monorepo, éliminant tout risque de conflit de bibliothèque.

**Pattern Consistency:**
Les règles de conversion d'indexation (sites 1-8 physiques vs 0-7 programmation) et le typage strict garantissent la cohérence des contributions futures des agents de développement.

**Structure Alignment:**
La structure du dépôt sépare rigoureusement la simulation quantique (micro), la modélisation de la serre (méso) et l'analyse de cycle de vie (macro), facilitant la maintenance.

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**
- Les FR-1 à FR-3 sont couverts par le module `quantum_interface`.
- Le FR-4 est couvert par le module `microclimate`.
- Le FR-5 et FR-7 sont couverts par le module `lca`.
- Les FR-6 et FR-8 sont couverts par le module `iot_security`.

**Non-Functional Requirements Coverage:**
La robustesse et la traçabilité des données physiques sont garanties par la validation Pydantic à l'initialisation et l'historique des paramètres sérialisés dans chaque fichier HDF5.

### Implementation Readiness Validation ✅
- Tous les choix technologiques et les chemins d'accès HDF5 sont explicitement documentés.
- Les cas limites critiques (volume de mode, éclairement nul, perte de clés QKD) sont couverts par des règles de repli précises.

### Gap Analysis Results
- **Gap Mineur :** La paramétrisation exacte des forces de couplage Stark et des énergies de réorganisation de l'FMO sous désaccord Floquet devra être affinée lors des premières simulations exploratoires.

### Architecture Completeness Checklist

- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION
**Confidence Level:** high

**Key Strengths:**
- Modélisation rigoureuse à 8 sites FMO avec piège RC pour corriger les faiblesses du premier papier.
- Couplage interdisciplinaire élégant reliant la nanophysique (SERS, polaritons) à la justice sociale (fracture quantique) et à la sécurité IoT (QKD).

### Implementation Handoff

**AI Agent Guidelines:**
- Respectez strictement le typage statique et les conventions de nommage `snake_case`.
- Ne jamais coder en dur des valeurs de paramètres physiques ; toujours les lire depuis `parameters.yaml`.

**First Implementation Priority:**
Exécutez la création de l'arborescence des répertoires sous `Redac_Paper2/` et créez le modèle Pydantic de validation de configuration initial dans `src/quantum_interface/solver.py`.
