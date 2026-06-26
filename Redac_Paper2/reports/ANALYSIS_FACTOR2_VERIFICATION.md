# Vérification du facteur 2 dans Φ_FT

## Dérivation mathématique

### Hamiltonien non-Hermitien
Le Hamiltonien dans `hamiltonian.py`:
```
H_eff = H - iΓ_RC|3⟩⟨3| - iΓ_RC|4⟩⟨4|
```
où Γ_RC = 0.15 ps⁻¹.

### Évolution temporelle
d|ψ⟩/dt = -iH_eff|ψ⟩

### Décroissance de la norme
d⟨ψ|ψ⟩/dt = -2Γ_RC(|ψ₃|² + |ψ₄|²) = -2Γ_RC(P₃ + P₄)

### Population piégée cumulée
Φ_FT = ∫₀ᵀ 2Γ_RC(P₃+P₄) dt = **2Γ_RC × ∫(P₃+P₄) dt** ✅

### Opérateur de Lindblad correspondant
H_eff = H - i/2 Σ L_n†L_n → L_n = √(2Γ_RC)|g⟩⟨n|

L'équation maîtresse de Lindblad donne:
dρ_gg/dt = Σ L_n ρ L_n† = 2Γ_RC(P₃+P₄)

Soit: ρ_gg(T) = 2Γ_RC × ∫(P₃+P₄) dt ✅

**Le ×2 est physiquement correct.**

---

## Ancien code (AVANT le fix)
```python
trap_yield = gamma_rc * np.sum(trapped_pop) * dt_fs  # manque ×2
```
Ceci calcule: Γ_RC × ∫(P₃+P₄) dt = Φ_FT/2

Pour NPoM ON: 0.0803 (au lieu de 0.1606)
Pour 77K: 0.1685 (au lieu de 0.3370)
Baseline N=1000: 0.98 ✅ (déjà ×2, calculé par MesoHOPS directement)

---

## Nouveau code (APRÈS le fix, actuel)
```python
trap_yield = 2.0 * gamma_rc * np.sum(trapped_pop) * dt_fs  # ×2 correct
```

---

## MAX_TRAPPING_YIELD

Actuellement: **1.96** (en `constants.py`)
- Justification: 2 × 0.98 (baseline)
- Problème: sous la formule ×2, le maximum physique est 1.0 (100% de piégeage)
- La baseline 0.98 est DÉJÀ un rendement physique correct (98%)

**Valeur recommandée: 0.98** (ou 1.0 comme marge de sécurité)
- Pourquoi: Φ_FT = 2Γ_RC × ∫(P₃+P₄) dt = 0.98 pour la baseline N=1000
- Le plafond à 0.98 protège contre les runs mal convergés (N=20 donne ~4.0)

---

## Manuscrit : incohérence actuelle

L'Éq. (2) définit: Φ_FT = 2Γ_RC × ∫(P₃+P₄) dt
Les valeurs rapportées sont: Γ_RC × ∫(P₃+P₄) dt (ANCIEN code)

### Deux options de correction

#### Option A : Multiplier toutes les valeurs ×2
| Valeur | Ancienne (tex) | Corrigée (×2) |
|--------|:--------------:|:-------------:|
| Φ_FT à V=1.2 nm³ | 0.0804 | **0.1608** |
| Φ_FT à 77K | 0.1685 | **0.3370** |
| Φ_FT_NPoM | 0.077 | **0.154** |
| Abstract: "8%" | 8% | **16%** |
| Abstract: "98%" | 98% | ✅ correct |
| Baseline | 0.98 | ✅ correct |

#### Option B : Supprimer le ×2 de l'Éq. (2)
- Changer: Φ_FT = Γ_RC × ∫(P₃+P₄) dt
- Toutes les valeurs texte restent identiques
- MAX_TRAPPING_YIELD = 0.49 (sous cette définition)
- Le code doit REVENIR à: `1.0 * gamma_rc * np.sum(trapped_pop) * dt_fs`
- Physiquement moins précis (ignore le ×2 du formalisme non-Hermitien)

---

## Recommandation

**Option A** est recommandée car:
1. Mathématiquement exacte (découle du Hamiltonien non-Hermitien)
2. Cohérente avec l'Éq. (2) existante
3. MAX_TRAPPING_YIELD = 0.98 (naturel)
4. Seulement 4-5 valeurs à mettre à jour dans le manuscrit
