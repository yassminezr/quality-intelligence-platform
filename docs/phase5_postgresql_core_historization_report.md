# Phase 5 — PostgreSQL, Core Model & Historical Loading

## 1. Objectif

Construire une couche PostgreSQL persistante, traçable, incrémentale et historisée pour la plateforme QIP.

```text
Excel
  ↓
Airflow
  ↓
Raw / Standardized
  ↓
Data Quality
  ↓
PostgreSQL
  ├── metadata
  ├── staging
  ├── quality
  └── core
```

## 2. Schémas PostgreSQL

- `metadata` : suivi technique des batchs.
- `staging` : données standardisées complètes et permissives.
- `quality` : anomalies Data Quality.
- `core` : modèle métier normalisé.

Tables principales :

```text
metadata.ingestion_batch
staging.standardized_audits
quality.dq_issues

core.account
core.campaign
core.audit
core.iso_clause
core.iso_control
core.evaluation
core.finding
core.corrective_action
core.audit_status_validation
core.evaluation_history
core.corrective_action_status_history
```

## 3. Staging

`standardized_audits.csv` est chargé dans `staging.standardized_audits`.

Le staging conserve les données même lorsqu'elles contiennent des anomalies métier. Le chargement est transactionnel et idempotent.

## 4. Data Quality dans PostgreSQL

Les anomalies sont chargées dans `quality.dq_issues`, avec référence au `batch_id`.

```text
staging.standardized_audits
→ données source standardisées

quality.dq_issues
→ anomalies détectées
```

## 5. Core Model

Le Core transforme les lignes techniques en entités métier.

Résultat actuel :

```text
20 accounts
1 campaign
20 audits
```

Le statut d'audit distingue :

```text
current_proposed_status
→ calcul automatique

current_validated_status
→ validation officielle équipe Qualité
```

Règle actuelle de proposition :

```text
0 % → non_audite
> 0 % et < 65 % → en_cours
65 % → a_valider
> 65 % → audite
```

## 6. Référentiel ISO

La source contenait 45 valeurs distinctes dans `clause_iso`, mais 8 étaient des lignes structurelles :

```text
Amélioration
Contexte
Leadership
Libellé
Performance
Planification
Réalisation
Support
```

Le Core conserve uniquement les vraies références métier.

Résultat actuel :

```text
37 clauses ISO
37 contrôles ISO
```

Les lignes structurelles restent disponibles dans staging.

## 7. Evaluations, findings et actions

Résultat actuel :

```text
214 evaluations
58 findings
50 corrective actions
```

Répartition des findings :

```text
NC Mineure      44
Bonne Pratique   7
Observation      6
NC Majeure       1
```

Les catégories autorisées restent :

```text
NC Mineure
NC Majeure
Bonne Pratique
OFI
Observation
NA
```

Les `156` évaluations sans finding correspondent aux anomalies `DQ_COMPLETENESS_001`.

```text
214 evaluations
- 58 findings
= 156 evaluations sans finding
```

Le système n'invente jamais une catégorie manquante.

## 8. Actions correctives

Résultat :

```text
50 corrective actions
```

Répartition observée :

```text
NC Mineure     43
Observation     6
NC Majeure      1
```

Validation métier :

```text
finding = NA
→ 0 corrective action
```

## 9. Historisation

Le Core conserve l'état courant, les tables d'historique conservent les versions.

```text
core.evaluation
→ état courant

core.evaluation_history
→ versions successives
```

```text
core.corrective_action
→ état courant

core.corrective_action_status_history
→ historique des statuts
```

Chaque version est reliée au `batch_id`.

Backfill initial :

```text
evaluation_history = 214
corrective_action_status_history = 50
```

Le second batch identique n'a créé aucune nouvelle version :

```text
evaluation_history = 214
corrective_action_status_history = 50
```

Cela confirme que l'historisation se fait sur changement réel.

## 10. Validations officielles

Le fichier :

```text
data/reference/account_status_validations.csv
```

alimente :

```text
core.audit.current_validated_status
core.audit_status_validation
```

Comptes validés audités dans le snapshot actuel :

```text
RAM
Min. Intérieur
AtlanticRe
Servier
ONCF MW
```

Le statut proposé ne remplace jamais le statut validé.

## 11. Intégration Airflow

Le DAG complet est :

```text
ingest_qhc_file
        ↓
run_data_quality
        ↓
load_postgres_staging
        ↓
load_postgres_dq
        ↓
load_core_audits
        ↓
load_core_iso
        ↓
load_core_evaluations
        ↓
load_core_validations
```

Les 8 tâches ont été exécutées avec succès.

## 12. Validation sur deux batchs

Résultat :

```text
metadata.ingestion_batch      = 2
staging.standardized_audits   = 1800
quality.dq_issues             = 324
```

Donc :

```text
Batch 1 → 900 lignes + 162 anomalies
Batch 2 → 900 lignes + 162 anomalies
```

Le Core reste stable :

```text
account              20
audit                20
iso_clause           37
iso_control          37
evaluation          214
finding              58
corrective_action    50
```

Cela confirme l'absence de duplication métier.

## 13. Idempotence

L'idempotence est assurée à plusieurs niveaux :

```text
même batch staging rejoué
→ pas de duplication

même batch DQ rejoué
→ pas de duplication

même entité Core
→ UPDATE ou aucune modification

même état historique
→ aucune nouvelle version
```

## 14. Résultat de la phase

La Phase 5 aboutit à une couche PostgreSQL :

- persistante ;
- normalisée ;
- traçable ;
- incrémentale ;
- idempotente ;
- historisée ;
- compatible avec la gouvernance métier ;
- orchestrée avec Airflow.

La plateforme est désormais prête pour la Phase 6 — dbt / Analytics Engineering.

**Statut : Phase 5 prête pour validation finale.**
