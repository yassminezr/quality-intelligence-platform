# Phase 2 — Data Modeling Report

## 1. Objectif de la phase

La Phase 2 avait pour objectif de transformer les données QHC issues d’Excel en un modèle de données métier cohérent, normalisé, historisable et adapté à la future Quality Intelligence Platform.

Cette phase ne correspond pas encore au modèle en étoile destiné à Power BI. Elle définit le **Core Data Model PostgreSQL**, qui servira ensuite de base aux transformations dbt et aux futurs data marts analytiques.

## 2. Entités principales

Le modèle logique final contient :

- `account`
- `campaign`
- `audit`
- `iso_clause`
- `iso_control`
- `evaluation`
- `finding`
- `corrective_action`
- `audit_status_validation`
- `evaluation_history`
- `corrective_action_status_history`
- `ingestion_batch`

## 3. Granularités

- **Account** : un compte/client.
- **Campaign** : une campagne d’audit.
- **Audit** : un compte audité dans une campagne.
- **ISO Clause** : une clause ISO.
- **ISO Control** : un contrôle opérationnel rattaché à une clause ISO.
- **Evaluation** : l’évaluation d’un contrôle dans un audit.
- **Finding** : le résultat/catégorie associé à une évaluation.
- **Corrective Action** : une action corrective liée à un finding.
- **Status Validation** : une décision de validation du statut d’un audit.
- **Ingestion Batch** : une ingestion de fichier source.

## 4. Relations et cardinalités clés

```text
ACCOUNT 1 ─── 0..N AUDIT
CAMPAIGN 1 ─── 0..N AUDIT

ISO_CLAUSE 1 ─── 1..N ISO_CONTROL
ISO_CONTROL 1 ─── 0..N EVALUATION
AUDIT 1 ─── 0..N EVALUATION

EVALUATION 1 ─── 1 FINDING
FINDING 1 ─── 0..1 CORRECTIVE_ACTION

AUDIT 1 ─── 0..N AUDIT_STATUS_VALIDATION
EVALUATION 1 ─── 0..N EVALUATION_HISTORY
CORRECTIVE_ACTION 1 ─── 0..N CORRECTIVE_ACTION_STATUS_HISTORY
```

## 5. Règles métier principales

### Audit
Un compte ne peut avoir qu’un seul audit par campagne :

```text
UNIQUE(account_id, campaign_id)
```

### Référentiel ISO
Le référentiel est séparé en deux niveaux :

- `iso_clause` : clause ISO et intitulé officiel ;
- `iso_control` : contrôle opérationnel utilisé pendant l’audit.

Le profiling a confirmé que chaque `clause_iso` possède un seul `intitule_iso` dans les données actuelles.

### Evaluation
Une évaluation est unique pour :

```text
(audit_id, control_id)
```

### Finding
Chaque évaluation possède obligatoirement un finding.

Valeurs métier actuelles :

- NC Mineure
- NC Majeure
- Bonne Pratique
- OFI
- NA

`NA` indique qu’aucun finding nécessitant un traitement n’a été constaté.

### Action corrective
Une action corrective est facultative, mais ne peut pas exister sans finding.

### Statut d’audit
La plateforme distingue :

- `proposed_status` : statut calculé automatiquement ;
- `validated_status` : statut confirmé par l’équipe Qualité.

Le statut validé constitue la référence métier officielle.

## 6. Historisation

La stratégie retenue repose sur trois niveaux :

1. **Raw immutable** : conservation des fichiers sources tels qu’ils ont été reçus.
2. **Core current state** : les tables principales PostgreSQL représentent l’état courant.
3. **History tables** : les changements métier importants sont historisés uniquement lorsqu’une vraie modification est détectée.

Les principales tables d’historique sont :

- `audit_status_validation`
- `evaluation_history`
- `corrective_action_status_history`

Chaque ingestion est tracée par `ingestion_batch`.

## 7. Données dérivées

`age_jours` et `indicateur_age` ne sont pas conservés comme source de vérité dans le modèle core.

Ils seront recalculés à partir de `date_debut`, `date_cloture` et `statut_action`.

Règle métier :

- 0–30 jours : Normal
- 31–60 jours : Alerte
- 61–90 jours : Critique
- > 90 jours : Escalade management

## 8. Core Model vs Data Marts

Le modèle de cette phase est un **modèle core normalisé**. Son rôle principal est d’assurer la cohérence, l’intégrité, les relations métier et l’historisation.

Les futurs modèles dbt auront un objectif analytique différent : produire des **data marts**, avec faits et dimensions, optimisés pour les KPI et Power BI.

```text
Excel / SharePoint
        ↓
Raw / Historical
        ↓
PostgreSQL Core Model
        ↓
dbt
        ↓
Data Marts
        ↓
Power BI / API / AI
```

## 9. Résultat de la phase

La Phase 2 aboutit à un modèle logique cohérent, normalisé, traçable et évolutif, capable de supporter :

- plusieurs campagnes d’audit ;
- plusieurs comptes ;
- un référentiel ISO structuré ;
- les évaluations et findings ;
- le suivi des actions correctives ;
- la validation métier des statuts ;
- l’historisation des changements ;
- les futurs traitements dbt, BI, API et fonctionnalités d’IA.

**Statut : Phase 2 validée.**
