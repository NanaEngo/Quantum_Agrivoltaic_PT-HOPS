# Spécification Verrouillée du Modèle : Hamiltonien, Paramètres Physiques, Régimes, Scénarii & Approche Interprétative

* **Code document :** `MS-RE-261112-V2.4`  
* **Cible :** *Renewable Energy* (Elsevier)  
* **Source de Vérité :** `parameters.yaml` (`v2.4.0`)  
* **Objectif :** Verrouiller tous les choix physiques (Hamiltonien LHCII, pile optique TMM/LUE, bilan foliaire LWIR–Medlyn, profil horaire diurne/nocturne usine, ACV double unité fonctionnelle) et réaliser une **revue complète pré-WP1**.

---

## 1. Hamiltonien LHCII & Équation Maîtresse sous Lumière Solaire

### 1.1 Modèle Primaire vs. Contre-Test Électrostatique
- **Complexe biologique retenu :** Monomère **LHCII de plante supérieure à 14 chlorophylles** — 8 Chl *a* (`602, 603, 604, 610, 611, 612, 613, 614`) et 6 Chl *b* (`601, 605, 606, 607, 608, 609`), dans la fenêtre spectrale PAR (`400–700 nm`). Tout reliquat FMO bactérien (750–820 nm) est banni.
- **Double verrouillage de Hamiltonien (sensibilité structurale) :**
  1. **H1 (Référence spectroscopique ajustée) :** **Novoderezhkin, Marin & van Grondelle (2011)**, *PCCP*, DOI [`10.1039/c1cp21079c`](https://doi.org/10.1039/c1cp21079c). Inclut le goulot lent `Chl a604` (>13 ps), le domaine émetteur terminal `Chl a610–a611–a612` et le couplage mixte `Chl b -> Chl a`.
  2. **H2 (Contre-test ab initio électrostatique) :** **Müh, Madjet & Renger (2010)** (*J. Phys. Chem. B*) sur structure cristallographique `1RWT`/`2BHW`, décalant notamment `Chl a610` en puits principal et modulant les niveaux de `a604/b608/b605/b609`. Comparer H1 et H2 prouve que la borne macroscopique $g_c$ ne dépend pas d'une calibration spécifique des énergies de site.

### 1.2 Approximations Valides & Hiérarchie des Solveurs
1. **Excitation solaire continue incohérente (NESS — Brumer, Tscherbul, Mančal) :**
   Le soleil filtre par $T_{\text{OPV}}(\lambda)$ n'est pas un laser femtoseconde pulsé. Il établit un **État Stationnaire Hors Équilibre (NESS)** régi par le flux spectral incident $S_{\text{sub}}(\lambda) = S_{\text{AM1.5G}}(\lambda) T_{\text{OPV}}(\lambda)$.
   - **Dipôles non orthogonaux :** À partir des géométries PDB `1RWT`/`2BHW`, on évalue le solveur **Bloch–Redfield partiellement séculaire** (conservant les couplages population–cohérence de type Fano/V) face à la **limite séculaire de Pauli** (taux purs). Cela répond directement au débat Brumer–Tscherbul–Mančal sur les cohérences stationnaires induites par la lumière thermique.
2. **Régime de couplage exciton–phonon intermédiaire :**
   Dans LHCII, certains amas ont des couplages forts ($|J_{nm}| > 15\ \text{cm}^{-1}$) et d'autres faibles ($\le 15\ \text{cm}^{-1}$). L'approximation optimale validée est la méthode hybride **Modified Redfield ($|J_{nm}| > 15\ \text{cm}^{-1}$) – Generalized Förster ($\le 15\ \text{cm}^{-1}$)** avec bain de Drude-Lorentz ($\lambda_D = 35\ \text{cm}^{-1}, \gamma_D = 50\ \text{cm}^{-1}$) + **48 modes vibrationnels intramoléculaires** sur $N = 200$ réalisations de désordre statique ($\text{FWHM} \approx 110\ \text{cm}^{-1}$).
3. **Rôle exact de MesoHOPS v1.8.0 (`HopsTensorTrajectory`) :**
   Calculer 100 trajectoires HOPS complètes à 48 modes pour une source thermique continue serait numériquement absurde. MesoHOPS v1.8.0 (env. `MesoHOP-sim-18` sur HPC `100.73.21.40`) est réservé à un **benchmark de borne d'erreur non-markovienne** ($N = 32$, bain réduit Drude-Lorentz + 2 modes résonants dominants à $\sim 340$ et $\sim 740\ \text{cm}^{-1}$) sur le sous-réseau goulot `Chl b -> Chl a`, afin de borner $|\eta_{\text{HOPS}} - \eta_{\text{mR-GF}}|$.
4. **Fermeture des centres réactionnels (RC) & NPQ $q_E$ :**
   Sous fort éclairement de midi, la fraction de centres PSII ouverts $q_L(I_{\text{ePAR}}, T_l)$ chute et le quenching non photochimique $\Gamma_{\text{NPQ}}(I, T_l)$ augmente en compétition directe avec le piégeage $k_{\text{trap}}$ sur `Chl a610–a612`, réduisant $\Phi_{\text{PSII}}$.

---

## 2. Raffinement des Paramètres Physiques & Écophysiologiques

| Domaine | Variable clé ajoutée / corrigée | Justification physique / Source primaire | Statut |
|---|---|---|---|
| **Altitude Foumbot & Djuttitsa** | Foumbot **`1044 m`**, Djuttitsa **`1400 m`** (Ndu jusqu'à `1850 m`), Penja **`273 m`** | Altitudes exactes de la grille ERA5 2023 vérifiées dans `climate_summary_2023.json`. | `WP1 ✅` |
| **Coefficient thermique PV** | **OPV PM6:Y6 :** $\beta_{\text{PCE}} = -0.008\,\%/^\circ\text{C}$ vs. **c-Si :** $-0.38\,\%/^\circ\text{C}$ | Les NFA-OPV gardent une PCE quasi plate à chaud, alors que le c-Si perd ~10–13 % à $55\ ^\circ\text{C}$ en plaine (Penja). | `WP1 ✅` |
| **Conductance mésophyllienne Café** | **$g_{m25} = 0.116$ (soleil) / $0.076$ (ombre) $\text{mol m}^{-2}\text{ s}^{-1}$** | Martins et al. (2014, `PMC3990704`) : ratio d'acclimatation $g_m$ ombre/soleil $= 0.655$ (`Cc`-basis `58.1 / 78.5`). | `WP1 ✅` |
| **Stomates & Eau** | Medlyn exact ($1.6(1 + g_1/\sqrt{\text{VPD}_l})A/C_a$) + réserve utile `AWC = 160 mm` `[120, 220]` | Capture la fermeture stomatique en saison sèche (`VPD p95 = 4.07 kPa` à Foumbot) et le proxy FAO-56 sol volcanique. | `WP1 ✅` |
| **Optique atmosphérique** | TMM ($300\text{–}1100\ \text{nm}$) + $f_{\text{diff}}$ ERA5 (`0.26–0.50`) + angles $0\text{–}60^\circ$ + **ePAR (`400–750` nm)** + **R:FR (`660/730` nm)** | Évite le piège de la moyenne annuelle : Djuttitsa atteint `f_diff = 0.486` en saison humide contre `0.260` à Foumbot en saison sèche. | `WP1 ✅` |
| **Couplage thermique bidirectionnel** | Syst. itératif $(T_{\text{pv}}, T_{\text{leaf}})$ avec **LWIR panneau** ($F_{l\to p}\varepsilon_p\sigma T_p^4$) $\leftrightarrow$ refroidissement latent foliaire ($\lambda E$) | Barron-Gafford et al. (2019) / Broadbent : vérifie s'il y a surchauffe IR à faible hauteur (`2.2 m` sur thé) ou refroidissement bénéfique du c-Si/OPV. | Couplé |

### 2.1 Architecture de la Pile ST-OPV & Contrainte de Pareto ($\text{LUE} = \text{PCE} \times \text{APT}$)
Il est physiquement interdit de fixer indépendamment $\text{PCE} = 10,5\,\%$ et $\text{APT} \in [35\,\%, 70\,\%]$ : ce serait violer la conservation des photons ($T + R + A \le 1$).
- **Empilement explicite modélisé en TMM (`parameters.yaml`) :** `Barrier PET / ITO (100 nm) / ZnO (35 nm) / PM6:Y6 (d_act = 50–120 nm, D:A 1:1.2 à 1:3) / MoO3 (10 nm) / Ag ultra-mince (d_Ag = 10–16 nm) / capuchon diélectrique MoO3 (0–50 nm)`.
- **Couplage auto-cohérent :** Pour chaque couple $(d_{\text{act}}, d_{\text{Ag}}, d_{\text{cap}})$, le solveur TMM calcule simultanément $T_{\text{OPV}}(\lambda, \theta)$, $\text{APT}$, $\text{ePAR}$, $\text{R:FR}$ **et** l'absorption dans la couche active $\to J_{\text{sc}} \to \text{PCE}(\text{APT})$ le long du front de Pareto $\text{LUE} \in [2,5\,\%, 4,2\,\%]$.
- **Conséquence directe pour Penja :** Une ultra-haute transparence ($\text{APT} > 65\,\%$) réduit mécaniquement la PCE unitaire, forçant un arbitrage entre densité surfacique (GCR élevé `0.75–0.85`) et coût BOS face au c-Si espacé.

### 2.2 Profil d'Autoconsommation des Usines & Enjeu du Flétrissage Nocturne
Confondre charge totale d'une usine de thé et charge diurne surestimerait artificiellement l'autoconsommation PV :
- **Séparation électricité / chaleur (Thé) :** Demande électrique médiane **`380 kWh_el/t`** (plage `250–500 kWh_el/t` en usines CTC modernes, jusqu'à `600 kWh_el/t` sur anciennes unités camerounaises) distincte de la chaleur de séchage biomasse/bois (`~4 500 kWh_th/t`).
- **Profil diurne vs. nocturne :**
  - **Thé (`55 %` jour / `45 %` nuit) :** Le **flétrissage (withering)** tourne `12–18 h` en continu **pendant la nuit** (ventilateurs axiaux), avec **0 % de couverture PV directe sans batterie**. Seuls broyage CTC, triage et soufflantes de jour coïncident avec le soleil.
  - **Café (`90 %` jour)** & **Poivre (`85 %` jour) :** Dépulpage humide, lavage/rouissage et ventilation diurne sont intrinsèquement synchronisés avec le PV.
- **3 architectures de dispatch évaluées (`bess_dispatch_options`) :** (a) *Sans BESS* (effacement diurne + diesel nocturne), (b) *Tampon LFP 2 h* (secours anti-gaspillage de lot + écrêtage), (c) *BESS LFP complet* (`220 USD/kWh`, 10 ans, $\eta_{\text{rt}}=90\,\%$) couvrant le flétrissage nocturne.

### 2.3 Paradoxe ACV (Double Unité Fonctionnelle) & Réalisme Tropical
- **Double unité fonctionnelle (ISO 14040/14044) :** (i) $\text{kg CO}_2\text{e}/\text{ha}\cdot\text{an}$ et (ii) $\text{g CO}_2\text{e}/\text{kWh}$ + crédit diesel évité.
- **Paradoxe $T_{80}$ vs. Acier BOS :** La ST-OPV possède une empreinte unitaire initiale bien plus basse (`~18 kg CO2e/m²` module + `10 kg CO2e/m²` BOS câble léger vs. `~55` + `~48 kg CO2e/m²` pour c-Si surélevé en acier lourd). Toutefois, un remplacement tous les 5 ans ($4\times$ sur 20 ans) à faible PCE peut rendre sa dette carbone **par kWh** supérieure au c-Si 25 ans — d'où le calcul explicite du seuil $T_{80,\text{carbone}}^*$.
- **Encrassement & Ruissellement :** Facteur d'encrassement saisonnier (`2–6 %` : poussières d'Harmattan en saison sèche vs. lessivage de mousson) et gestion des lignes d'égouttement (drip-lines) sous pluies intenses de Penja (`400–500 mm/mois`).

---

## 3. Matrice des Régimes Physiques & Écophysiologiques

Le modèle ne doit jamais lisser des comportements opposés dans une moyenne annuelle. Il résout explicitement **4 axes de régimes** au pas horaire (`8760 h/an`) :

1. **Régime Quantique & Photophysique (LHCII $\to$ PSII) :**
   - *Régime A (Sous-saturant / Couvert nuageux, $I_{\text{ePAR}} < I_{\text{sat}},\ A = A_j$) :* $\partial A / \partial \eta_{\text{ET}} > 0$ ; le rendement d'antenne $\eta_{\text{NESS}}(T_{\text{OPV}})$ se propage proportionnellement au taux de transport d'électrons $J$.
   - *Régime B (Midi clair / Saturant, $I_{\text{ePAR}} \ge I_{\text{sat}},\ A = A_v$) :* Limitation stricte par la RuBisCO ($V_{c\max}$) + $g_m$, d'où $\partial A / \partial \eta_{\text{ET}} \equiv 0$.
2. **Régime Optique & Climatique (Saison Sèche vs. Mousson Camerounaise) :**
   - *Saison Sèche (Déc.–Fév./Mars, fort éclairement direct, forte VPD) :* L'ombrage sélectif supprime la photoinhibition PSII et réduit $T_l$ et $\text{VPD}_l$ $\implies$ **gain agronomique positif**.
   - *Grande Saison des Pluies (Juin–Oct., forte nébulosité $f_{\text{diff}} > 0.60$, VPD faible) :* À Penja (`3.7 kWh/m²/j`) ou Djuttitsa (brouillards d'altitude), une transmittance trop basse (APT < 45 % ou GCR c-Si > 0.5) fait basculer la culture en **déficit de PAR** $\implies$ arbitrage saisonnier explicite.
3. **Régime Thermique Panneau–Canopée :**
   - *Régime Ventilé/Haut ($H_{\text{mount}} \ge 3.5\ \text{m}$, poivre) :* Faible facteur de vue $F_{l\to p}$, refroidissement convectif maximal.
   - *Régime Proche/Confiné ($H_{\text{mount}} = 2.2\ \text{m}$, thé à `1.0 m`) :* $F_{l\to p}$ élevé ; teste explicitement la compensation entre blocage SW et émission LWIR descendante du panneau.
4. **Régime Technico-Économique :**
   - *Autoconsommation diurne vs. nocturne* (thé `380 kWh_el/t` médian dont `55 %` jour / `45 %` flétrissage nocturne ; `0.45 USD/kWh` diesel évité vs. `0.085 USD/kWh` réseau ; arbitrage 3 options BESS LFP), et *bascule ST-OPV vs. c-Si espacé* en fonction de $T_{80}^{\text{OPV}}$ (`5` vs `10–25` ans), de la courbe Pareto $\text{PCE}(\text{APT})$, et du coût BOS.

---

## 4. Matrice des 6 Scénarii Comparatifs

| ID Scénario | Description | Rôle analytique dans l'article |
|---|---|---|
| **S0** | Monoculture plein soleil + transformation diesel | Témoin agricole actuel (pénalité photoinhibition/chaleur + coût diesel). |
| **S1** | Agroforesterie biologique (ombrage naturel 30–40 % ; tuteurs vivants *Spondias mombin* pour Penja) | Contrefactuel agronomique réaliste (inclut risque de mortalité racinaire du tuteur et absence de revenu PV). |
| **S2** | **c-Si monocristallin opaque espacé** (PCE `20.5 %`, $\beta_T = -0.38\,\%/^\circ\text{C}$, 25 ans, GCR `0.20–0.70`, BOS `55 USD/m²`, sensibilité BESS LFP) | Contrefactuel PV mature obligatoire pour prouver où la ST-OPV gagne ou perd. |
| **S3** | **ST-OPV PM6:Y6 baseline réaliste** (pile TMM couplée Pareto $\text{PCE}(\text{APT})$, $\beta_T \approx 0$, APT `35–70 %`, $T_{80}=5$ ans tropical humide + remplacement à 5 ans, carbone = `0`) | Scénario central réaliste et conservateur du manuscrit. |
| **S4** | **ST-OPV encapsulé optimiste** ($T_{80} = 10\text{–}25$ ans selon Li et al. 2021 + amélioration BOS) | Explore la frontière de rentabilité si la stabilité tropicale rejoint la durée intrinsèque de laboratoire. |
| **S5** | **Stress dispatch, politiques & climat** (BESS nocturne vs diurne seul, prix carbone `0→25 USD/t`, WACC `6→15 %`, pluvial vs irrigation d'appoint) | Teste la robustesse des frontières de décision sans dépendre d'hypothèses complaisantes. |

---

## 5. Liste de Contrôle du Réalisme (Biais Éliminés)

1. **Aucune moyenne climatique annuelle lissée** : résolution horaire `8760 h` sur profils saisonniers distincts (Foumbot, Djuttitsa, Penja) incluant stress hydrique pluvial en saison sèche et nébulosité de mousson.
2. **Aucun crédit carbone ni subvention dans le cas de base (`S3`)** : rentabilité vérifiée à `0 USD/tCO2e` et `0 %` de subvention.
3. **Aucun rendement OPV perpétuel ni coût nul d'exploitation** : dégradation annuelle `4 %/an` + remplacement complet des modules tous les 5 ans (`25 USD/m²`) en `S3` + part d'autoconsommation réaliste (`65 %` sans stockage batterie massif).
4. **Validation empirique croisée obligatoire en WP4** :
   - Café ombragé (Brésil / BREEDCAFS) : $\Delta T_l \in [-2, -4]\ ^\circ\text{C}$ sous ombrage optimal, reproduction de la sensibilité à $g_m$.
   - Thé sous PV (Chine, `10.3390/agriculture16010125`) : à PAR $\approx 53\,\%$ du témoin, $\Delta Y \in [+9, +15]\,\%$ et réduction de photoinhibition PSII.
   - Afrique de l'Est CAPEX (`10.1016/j.apenergy.2026.128450`) : part de structure dans le CAPEX cohérente (~40–50 % hors batterie).

---

## 6. Les 5 Éléments de l'Approche Interprétative (Cœur de l'Article)

Au lieu de décrire des tableaux de simulation, la section Résultats & Discussion est structurée autour de **5 diagnostics causaux et cartes décisionnelles** :

1. **Décomposition causale en 4 leviers de $\Delta Y_{\text{crop}}$ (attribution Shapley/locale) :** Quantifie pour chaque culture et chaque technologie (`S2` vs `S3`) la part exacte du gain/perte due à : (i) modération PAR & levée de photoinhibition PSII, (ii) bilan thermique net $\Delta T_l$ (ombrage SW net du LWIR panneau), (iii) réouverture stomatique via $\text{VPD}_l$ (Medlyn) & eau du sol, et (iv) qualité spectrale (`ePAR`, `R:FR`, et borne quantique $\Delta\eta_{\text{NESS}}$).
2. **Partitionnement de $\Delta ET_c$ & Productivité de l'Eau (WUE) :** Sépare l'économie d'eau radiative (baisse de $R_n$) de la réponse physiologique ($g_s$, $\text{VPD}_l$).
3. **Cartes de régimes sans dimension 2D (Diagrammes de phases) :**
   - *Carte agronomique :* $\big(\text{PAR}_{\text{saison}} / I_{\text{sat}},\ \text{VPD}_{\text{midi}}\big)$ montrant les zones de **gain par photo-protection** vs les zones de **pénalité par déficit lumineux de mousson** (ex. saison des pluies à Penja si APT < 55 %).
   - *Frontière technologique (`G6`) :* $\big(T_{80}^{\text{OPV}},\ C_{\text{mod}}^{\text{OPV}} / C_{\text{BOS}}^{\text{c-Si}}\big)$ et $(\text{GCR},\ \text{APT})$ traçant l'isocline exacte $\Delta\text{NPV}(\text{ST-OPV} - \text{c-Si}) = 0$ pour chaque culture.
4. **Analyse d'asymétrie thermique et spectrale ST-OPV vs. c-Si :** Explique *physiquement* pourquoi $\beta_T \approx 0$ favorise la ST-OPV dans les basses terres chaudes (Penja) alors que la longue durée de vie (25 ans) et la forte PCE du c-Si dominent en altitude fraîche (Djuttitsa) dès que $T_{80}^{\text{OPV}} < T_{80}^*$.
5. **Critère explicite de réfutabilité sur la cohérence quantique :** Confronte $\Delta Y^{\text{quantique}}$ (calculé sans préjugé via H1/H2 + NESS partiellement séculaire + FVCB $A_j/A_v$) aux amplitudes classiques ($\Delta Y_{\text{therm}}, \Delta Y_{\text{PAR/PI}}$) et aux incertitudes de Monte Carlo ($N=10\,000$, indices de Sobol $S_i, S_{Ti}$), démontrant rigoureusement si l'effet quantique est statistiquement noyé dans le bruit agronomique.

---

## 7. Revue Complète de Cohérence Pré-WP1 (Verdict d'Audit)

| Axe vérifié | Risque critique identifié lors de la revue | Verrou mis en place (`v2.4.0`) | Statut |
|---|---|---|---|
| **Quantique / Hamiltonien** | Confusion laser/FMO vs lumière solaire continue ; sensibilité au jeu d'énergies de site ; coût MesoHOPS excessif | **LHCII 14 sites (H1 Novoderezhkin + H2 Müh–Renger)**, NESS partiellement séculaire vs Pauli, MesoHOPS v1.8.0 limité au benchmark d'erreur 2-modes ($N=32$) | Verrouillé |
| **Optique ST-OPV** | Violation conservation des photons (`PCE = 10.5%` fixe à `APT = 70%`) | Empilement explicite `ITO/ZnO/PM6:Y6/MoO3/Ag/MoO3` résolu en TMM le long de la frontière de Pareto $\text{LUE} = \text{PCE} \times \text{APT}$ | Verrouillé |
| **Physiologie & Climat** | Ignorer $g_m$ finie du café ; moyenne annuelle masquant le déficit de mousson à Penja ; LWIR panneau | $g_{m25}$ (`0.04–0.15 mol m⁻² s⁻¹`) en base $C_c$, bilan horaire `8760 h` ($f_{\text{diff}}$ saisonnier, `AWC 160 mm`), solveur itératif $(T_{\text{pv}}, T_{\text{leaf}})$ avec LWIR | Verrouillé |
| **Énergie Usines** | Supposer `600 kWh/t` diurnes pour le thé alors que le flétrissage est nocturne | Séparation chaleur biomasse / `380 kWh_el/t` médian (`55%` jour / `45%` nuit) + 3 options LFP BESS | Verrouillé |
| **ACV & Durabilité** | Oublier que 4 remplacements OPV ($T_{80}=5$ ans) peuvent inverser le bilan carbone par kWh | Double unité fonctionnelle (`kgCO2e/ha/an` et `gCO2e/kWh`) traçant le seuil $T_{80,\text{carbone}}^*$ face à l'acier BOS c-Si | Verrouillé |
| **Barrière WP1 clôturée** | Toutes les constantes primaires ont été extraites et traçées (`parameters.yaml v2.5.0`, zéro `[VERIFY]`) | `H1/H2/H3` 14×14, `1RWT/2BHW`, `(n,k)` `300–1100 nm`, `ERA5 8760 h`, traits FvCB–Medlyn vérifiés (`make test`: `4/4 OK`) | **Prêt pour WP2** |
