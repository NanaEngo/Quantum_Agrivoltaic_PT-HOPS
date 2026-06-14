# Roadmap de Révision: Manuscrit JPCL (jz-2026-00994t.R1)

Ce document présente un plan d'action détaillé pour répondre aux commentaires des Reviewers 2 et 3 datés du 10 Juin 2026, et préparer la soumission de la révision majeure R2.

> [!WARNING]
> La date limite de soumission d'une révision majeure pour JPCL est généralement de 30 jours, mais l'éditeur (Prof. Gregory Scholes) encourage une soumission dans les deux semaines (soit vers le 24 Juin 2026).

## Phase 1: Préparation de l'Environnement de Rédaction

La première étape consiste à créer un nouvel espace de travail pour la révision R2 afin de préserver l'historique de la soumission précédente.

> [!IMPORTANT]
> **SOURCE DE VÉRITÉ (RÉVISION R2)** : La source de vérité absolue pour tous les fichiers de la version révisée est le répertoire `Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/JPCL/JPCL_Submission_Package_2026-06-13`. Toute modification rédactionnelle doit s'effectuer exclusivement dans ce dossier.

1. **Créer le nouveau répertoire de soumission:**
   Créer une copie du répertoire de la soumission précédente avec la date du jour (13 Juin 2026).
   ```bash
   cp -r Redac_Paper1/JPCL Redac_Paper1/JPCL_Submission_Package_2026-06-13
   ```
2. **Renommer les fichiers tex et le package:**
   Renommer les fichiers de la nouvelle version avec la date actuelle:
   - `Manuscript_JPCL_26-06-13.tex`
   - `SI_JPCL_26-06-13.tex`
   - `Response_to_Reviewers_26-06-13.tex`
   - `Cover_Letter_JPCL_26-06-13.tex`

## Phase 2: Mises à Jour des Simulations & du Codebase

Le codebase officiel est situé dans `/quantum_simulations_framework_parallel_260612/`. Les commentaires du Reviewer 3 nécessitent plusieurs correctifs au niveau des scripts d'analyse et potentiellement de la dynamique.

### 1. Définition du Rendement de Transfert (Transfer Yield)
- **Problème (Rev 3, Pt 1):** La définition basée sur `1 - probabilité de survie` n'est pas adéquate pour un système multi-états.
- **Action Codebase:** Modifier le script de génération de figures (`utils/figure_generator.py` ou équivalent) pour utiliser la **population à l'équilibre aux temps longs (long-time population) de l'état cible**.
- **Action Manuscrit:** Mettre à jour l'équation de définition du transfert dans le texte.

### 2. Tracés de la Décohérence et de la Population (Fig 3a, 3b)
- **Problème (Rev 3, Pt 3):** Les figures 3a et 3b ne montrent pas de décohérence temporelle (elles ressemblent à un système isolé sans environnement dissipatif).
  - **Action Codebase**:
    - Vérifier l'intégration du terme dissipatif (bain) dans `main.py` et `hops_simulator.py`.
    - S'assurer que les couplages (e.g., $\lambda_D=35 \text{ cm}^{-1}$, $\gamma_D=50 \text{ cm}^{-1}$) sont correctement appliqués au système pendant la génération du CSV de production.
    - Relancer une trajectoire en mode "Laptop" avec `python main.py --config laptop_parameters.yaml` pour diagnostiquer pourquoi les oscillations ne s'amortissent pas.
    - **Indiquer qu'à l'issue des tests sur laptop, la version doit être mise à jour pour la simulation sur le serveur.**
- **Génération de Figure:** Regénérer la Figure 3 avec des courbes montrant clairement l'amortissement.

### 3. Densité Spectrale (Figure 3e et SI)
- **Problème (Rev 3, Pt 2):** La fonction de densité spectrale dans la Figure 3e (600-900 cm⁻¹) est étrange (linéaire) par rapport à la SI. Clarifier le choix de 12 modes pour la FMO et l'énergie de réorganisation totale de 53 cm⁻¹.
- **Action Codebase:**
  - Modifier le script de traçage de la densité spectrale pour s'assurer qu'il trace correctement la distribution des 12 modes (modèle de Kleinekathöfer/Coker) au lieu d'une fonction linéaire.
- **Action Manuscrit:**
  - Expliquer dans le texte pourquoi 12 modes effectifs ont été choisis (et d'où sort le chiffre de 189 modes mentionné par erreur ou si cela se réfère aux modes du réseau entier $7 \times 27$ etc.).
  - Justifier la valeur de l'énergie de réorganisation totale par rapport à la littérature de la chlorophylle.

## Phase 3: Révision du Manuscrit et de la S.I.

### 1. Adresser les Commentaires du Reviewer 2
- **Citations (Pt i):** Ajouter les références concernant la résonance vibronique (JPC. Lett. 6(4), 627 (2015) et JPC. Lett. 13, 6831 (2022)) dans `references.bib` et les discuter dans l'introduction.
- **Terminologie (Pt ii):** Remplacer/Clarifier le terme "polaron transformation" par "vibronic basis" (base vibronique) de manière cohérente à travers tout le manuscrit.
- **Proofreading (Pt iii):** Effectuer une relecture grammaticale approfondie pour corriger toutes les fautes de frappe.

### 2. Adresser le Jargon Informatique et le Reviewer 3
- **Suppression du Jargon (Rev 3, Pt 5):**
  > [!IMPORTANT]
  > JPCL est un journal de chimie physique, pas d'informatique. Le jargon doit être complètement retiré.
  - Supprimer les mentions telles que "hardware-hardened pipeline", "numerical delta = 0.0", "Hardware-aware scheduling", et "54GB RAM footprint per path".
  - Reformuler pour se concentrer sur la *méthode physique* (Hiérarchie d'équations, troncature) plutôt que sur les optimisations logicielles.
- **Figure 2:** Remplacer l'organigramme de l'algorithme (flowchart informatique) par une figure expliquant la physique (ex: schéma du modèle, couplage vibronique, ou bath spectral density), ou bien déplacer le flowchart dans la SI.
- **Scalabilité et Convergence (Rev 3, Pt 4):**
  - Nuancer la phrase "O(1) with system size" et "non-Markovian memory without exponential scaling". Préciser que la scalabilité est contrôlée par le Stochastic Bundled Dissipator (SBD) et non que le coût est indépendant du système.
  - Justifier physiquement la convergence avec 2 termes de Matsubara (K=2) à 300 K, en référant à l'analyse déjà présente dans la SI (Section S2.3) où une erreur de 3.32e-05 MAE est démontrée.

## Plan d'Exécution Suggéré

1. [x] Valider les paramètres du serveur (`parameters.yaml` et `constants.py`) : $L=8$, $K=2$, 100 trajectoires, $\lambda_D=35$ cm$^{-1}$, $T=295$ K. Les paramètres sont corrects pour la production.
2. [ ] Lancer la simulation de production (100 trajectoires) sur le serveur/cluster pour capturer la décohérence complète :
   ```bash
   cd /home/taamangtchu/Documents/Github/Quantum_Agrivoltaic_PT-HOPS/quantum_simulations_framework_parallel_260612/
   PYTHONPATH=. /home/taamangtchu/miniforge3/envs/MesoHOP-sim/bin/python reproducibility/main.py --config config/parameters.yaml --parallel --skip-audit
   ```
3. [ ] Corriger le script de génération de figures pour le Transfer Yield (utiliser la population à temps long) et la Densité Spectrale (12 modes discrets).
4. [ ] Regénérer les figures 2 et 3 avec les données de la simulation serveur pour prouver l'amortissement (décohérence).
5. [ ] Créer le nouveau répertoire `JPCL_Submission_Package_2026-06-13`.
6. [ ] Modifier `Manuscript_JPCL_26-06-13.tex` pour nettoyer le jargon (Rev 3) et ajuster la terminologie polaron/vibronic (Rev 2).
7. [ ] Mettre à jour `references.bib` et le texte pour inclure les citations de 2015 et 2022 suggérées.
8. [ ] Rédiger le fichier `Response_to_Reviewers_26-06-13.tex` avec les réponses point par point.
