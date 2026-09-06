# Data Quality Catalog — Quality Intelligence Platform

## 1. Objectif

Ce document recense les anomalies, risques de qualité et règles de contrôle identifiés pendant la Phase 1.

Les contrôles ne sont pas encore tous implémentés.

Ils serviront de base à la Phase 4 — Data Quality.

Le dataset actuel étant encore en cours d’enrichissement, une valeur manquante ne doit pas être considérée automatiquement comme une anomalie.

---

# 2. Principes généraux

## DQ-001 — Préserver la donnée source

La raw layer ne doit jamais être modifiée.

Toute correction ou standardisation doit être réalisée dans une couche dérivée.

---

## DQ-002 — Aucun champ canonique inconnu

Toute colonne provenant des feuilles d’audit doit être :

- reconnue ;
- comprise ;
- mappée vers le schéma canonique ;
- ou explicitement signalée comme nouvelle colonne à examiner.

Une nouvelle colonne inconnue ne doit pas être ignorée silencieusement.

---

# 3. Contrôles sur le score de maturité

## DQ-SCORE-001 — Score numérique

### Champ

`score_maturite`

### Règle

Une valeur renseignée doit être numérique.

### Exemple invalide

`Excellent`

### Action future

Rejeter ou mettre en quarantaine la ligne selon la stratégie Data Quality.

---

## DQ-SCORE-002 — Domaine du score

### Champ

`score_maturite`

### Règle actuelle

Le score doit être compris entre 1 et 5.

### Valeurs observées actuellement

1, 2, 3, 4.

Aucune valeur 5 n'est observée actuellement.

---

# 4. Contrôles sur le niveau de maturité

## DQ-MATURITY-001 — Vocabulaire contrôlé

### Champ

`niveau_maturite`

### Valeurs canoniques envisagées

- `Non en place/Elémentaire`
- `Partiellement en place/Réactif`
- `Largement en place/Stable`
- `Totalement en place/Proactif`

Les variantes de libellé doivent être normalisées.

### Variantes actuellement observées

- `Partiellement`
- `Largement en place`
- `Totalement en place / Proactif`

---

## DQ-MATURITY-002 — Non audité n'est pas un niveau de maturité

La valeur :

`⏳ Non audité`

ne représente pas un niveau de maturité.

Elle devra être traitée séparément du niveau de maturité.

---

# 5. Contrôles sur les findings

## DQ-FINDING-001 — Catégorie contrôlée

### Champ

`categorie_finding`

Valeurs actuellement observées :

- `NC Mineure`
- `NC Majeure`
- `Observation`
- `Bonne Pratique`

Toute nouvelle catégorie devra être contrôlée par rapport au référentiel métier.

---

## DQ-FINDING-002 — Bonne pratique

`Bonne Pratique` ne doit pas être comptabilisée comme une non-conformité négative.

Les KPI de findings doivent distinguer :

- non-conformités ;
- observations ;
- bonnes pratiques.

---

# 6. Contrôles sur les actions correctives

## DQ-ACTION-001 — Action et responsable

Si `action_corrective` est renseignée, alors `responsable_action` devrait être renseigné.

La criticité exacte de cette règle reste à confirmer avec l'équipe Qualité.

---

## DQ-ACTION-002 — Action et statut

Si `action_corrective` est renseignée, alors `statut_action` devrait être renseigné.

Un statut manquant n'est donc pas automatiquement une anomalie si aucune action corrective n'existe.

---

## DQ-ACTION-003 — Vocabulaire des statuts

Les statuts actuellement observés sont :

- `En cours`
- `Ouvert`

D'autres statuts peuvent apparaître plus tard, notamment `Clôturé`.

Le domaine officiel doit rester configurable ou référencé dans une table métier.

---

# 7. Contrôles sur les dates

## DQ-DATE-001 — Date de début valide

`date_debut` doit être convertible en date lorsqu'elle est renseignée.

---

## DQ-DATE-002 — Date de clôture valide

`date_cloture` doit être convertible en date lorsqu'elle est renseignée.

---

## DQ-DATE-003 — Mapping canonique

Les variantes historiques doivent être standardisées.

Vers `date_debut` :

- Date de début
- Date de réalisation prévisionnelle
- Date de réalisation previsionelle

Vers `date_cloture` :

- Date de clôture
- Délai prévu
- Délai Prévu
- Délai de clôture

---

# 8. Contrôles sur l'âge des actions

## DQ-AGE-001 — Âge numérique

`age_jours` doit être numérique lorsqu'il est renseigné.

Les valeurs telles que :

`#REF!`

sont invalides.

---

## DQ-AGE-002 — Âge non négatif

`age_jours` ne doit pas être négatif.

---

## DQ-AGE-003 — Calcul de l'âge

Pour une action non clôturée :

`age_jours = date_du_jour - date_debut`

Lorsque l'action devient `Clôturé`, l'âge cesse d'évoluer.

La manière exacte de figer cette valeur sera définie lors de l'implémentation.

---

# 9. Contrôles sur l'indicateur d'âge

## DQ-AGE-IND-001 — Valeur recalculée

`indicateur_age` ne doit pas dépendre des formules Excel comme source de vérité.

Il doit être recalculé par la plateforme à partir de `age_jours`.

---

## DQ-AGE-IND-002 — Règle de classification

- 0–30 jours → `Normal`
- 31–60 jours → `Alerte`
- 61–90 jours → `Critique`
- > 90 jours → `Escalade management`

---

## DQ-AGE-IND-003 — Erreur Excel interdite

Une valeur comme :

`#REF!`

est toujours invalide.

---

# 10. Contrôles sur le scope

## DQ-SCOPE-001 — Domaine du scope

Valeurs actuellement observées :

- `Compte`
- `Entité`
- `Entité et Compte`

Toute nouvelle valeur devra être examinée.

---

## DQ-SCOPE-002 — Valeur manquante

Une valeur manquante dans `categorie_scope` n'est pas automatiquement une erreur.

La règle devra dépendre du type de ligne et du contexte métier.

---

# 11. Contrôles sur le statut du compte

## DQ-AUDIT-STATUS-001 — Proposition automatique

La plateforme peut calculer un statut proposé.

Règle provisoire actuelle :

- 0 % → `non_audite`
- > 0 % et < 65 % → `en_cours`
- > 65 % → `audite`

Le cas exactement égal à 65 % reste à clarifier.

---

## DQ-AUDIT-STATUS-002 — Validation humaine

Le statut proposé ne doit jamais être considéré automatiquement comme une validation métier.

Le statut officiel est celui confirmé ou renseigné par l'équipe Qualité.

---

## DQ-AUDIT-STATUS-003 — Traçabilité de validation

Lorsqu'un statut est validé, la plateforme doit conserver :

- `statut_valide`
- `date_validation`
- `valide_par`

---

# 12. Contrôles de complétude conditionnels

Les règles de complétude doivent être conditionnelles.

Exemples :

### Cas acceptable

`action_corrective = NULL`

`statut_action = NULL`

Cela peut être normal.

### Cas potentiellement invalide

`action_corrective = "Mettre à jour la procédure"`

`responsable_action = NULL`

Ce cas devra être contrôlé.

---

# 13. Contrôles de schéma

## DQ-SCHEMA-001 — Nouvelle variante de structure

Si un nouveau fichier contient une structure de feuille inconnue, le pipeline doit :

1. détecter la variante ;
2. la journaliser ;
3. empêcher une transformation silencieusement incorrecte ;
4. demander une revue si nécessaire.

---

## DQ-SCHEMA-002 — Nouvelle colonne inconnue

Une colonne non présente dans `COLUMN_MAPPING` doit être signalée.

Le pipeline ne doit jamais l'ignorer silencieusement.

---

# 14. Contrôles de traçabilité

Chaque ligne standardisée doit permettre de remonter au minimum à :

- `source_file`
- `source_sheet`

Plus tard, les métadonnées techniques pourront inclure :

- `batch_id`
- `ingestion_timestamp`
- `campaign_id`

---

# 15. Niveaux de sévérité futurs

Les règles Data Quality pourront être classées selon plusieurs niveaux.

Exemple envisagé :

- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

Cette classification sera définie pendant la Phase 4.

Une anomalie ne devra pas nécessairement bloquer tout le pipeline.

La stratégie pourra distinguer :

- anomalies bloquantes ;
- anomalies mises en quarantaine ;
- anomalies simplement journalisées.