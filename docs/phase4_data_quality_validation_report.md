# Phase 4 — Data Quality & Validation Layer Report

## 1. Objectif de la phase

La Phase 4 avait pour objectif de construire une couche de **Data Quality structurée, traçable et exploitable par l’équipe Qualité** avant le chargement dans PostgreSQL.

Le flux cible devient :

```text
Excel
  ↓
Phase 3 — Ingestion / Raw / Standardization
  ↓
standardized_audits.csv
  ↓
Phase 4 — Data Quality
  ↓
DQ Report + DQ Gate
  ↓
Phase 5 — PostgreSQL Core
```

## 2. Familles de contrôles

Les contrôles ont été organisés en cinq familles :

- `SCHEMA`
- `DOMAIN`
- `COMPLETENESS`
- `CONSISTENCY`
- `DATES`

Exemples :

```text
SCHEMA
→ colonne obligatoire absente
```

```text
DOMAIN
→ score_maturite hors [1,5]
```

```text
COMPLETENESS
→ ligne évaluée mais categorie_finding absente
```

```text
CONSISTENCY
→ action corrective présente sans finding valide
```

```text
DATES
→ date invalide ou clôture antérieure au début
```

## 3. Sévérités

Trois niveaux ont été définis :

```text
WARNING
ERROR
BLOCKING
```

- `WARNING` : anomalie à surveiller ; le pipeline continue.
- `ERROR` : anomalie métier réelle ; le pipeline continue, mais l’équipe Qualité doit pouvoir la consulter et la corriger.
- `BLOCKING` : problème structurel majeur ; le pipeline s’arrête.

## 4. Règles implémentées

```text
DQ_SCHEMA_001
→ colonne obligatoire absente

DQ_DOMAIN_001
→ score_maturite invalide

DQ_DOMAIN_002
→ categorie_finding invalide

DQ_COMPLETENESS_001
→ ligne évaluée mais categorie_finding absente

DQ_CONSISTENCY_001
→ finding = NA avec action corrective

DQ_CONSISTENCY_002
→ action corrective avec finding absent ou NA

DQ_CONSISTENCY_003
→ action clôturée sans date_cloture

DQ_DATE_001
→ date invalide

DQ_DATE_002
→ date_cloture antérieure à date_debut
```

## 5. Domaine métier final des findings

Après validation avec l’encadrant, `Observation` a été confirmée comme catégorie officielle.

Le domaine final est :

```text
NC Mineure
NC Majeure
Bonne Pratique
OFI
Observation
NA
```

Les règles Data Quality et les tests ont été mis à jour en conséquence.

## 6. Calcul déterministe de l’âge des actions

`age_jours` et `indicateur_age` ne sont plus considérés comme des valeurs sources de référence.

La logique retenue est :

```text
action ouverte / en cours
→ age_jours = aujourd’hui - date_debut
```

```text
action clôturée
→ age_jours = date_cloture - date_debut
```

Puis :

```text
0–30 jours → Normal
31–60 jours → Alerte
61–90 jours → Critique
>90 jours → Escalade management
```

## 7. Data Quality Engine

Un moteur centralisé a été créé dans :

```text
src/quality/dq_engine.py
```

Il exécute l’ensemble des règles et produit un `DQReport` exposant notamment :

```text
total_issues
warning_count
error_count
blocking_count
has_blocking_issues
```

## 8. Data Quality Gate

Un gate a été créé dans :

```text
src/quality/dq_gate.py
```

Politique retenue :

```text
WARNING
→ CONTINUE

ERROR
→ CONTINUE
→ rapport visible pour l’équipe Qualité

BLOCKING
→ BLOCK
```

Cette politique a été choisie parce que les erreurs métier ne doivent pas empêcher par défaut le chargement dans PostgreSQL, tant que la structure reste exploitable.

## 9. Résultat réel sur le dataset

Le moteur Data Quality a été exécuté sur le batch standardisé courant.

Résultat :

```text
Total issues: 162
Warnings: 0
Errors: 162
Blocking: 0
Has blocking issues: False
```

Répartition principale :

```text
DQ_COMPLETENESS_001
→ 156 anomalies

DQ_CONSISTENCY_002
→ 6 anomalies
```

Les anomalies concernent principalement des lignes évaluées dont la catégorie de finding n’est pas encore renseignée.

## 10. Reporting Data Quality

Pour chaque batch, les fichiers suivants sont générés :

```text
quality/
├── dq_report.json
├── dq_issues.csv
├── dq_issues_business.csv
├── dq_summary_by_rule.csv
└── dq_summary_by_account.csv
```

### `dq_report.json`

Résumé global avec :

- total d’anomalies ;
- nombre de `WARNING` ;
- nombre de `ERROR` ;
- nombre de `BLOCKING` ;
- décision du DQ Gate.

### `dq_issues.csv`

Détail technique des anomalies.

### `dq_issues_business.csv`

Vue métier enrichie avec :

- règle ;
- sévérité ;
- compte ;
- ligne source ;
- description métier ;
- action recommandée.

### `dq_summary_by_rule.csv`

Synthèse des anomalies par règle.

### `dq_summary_by_account.csv`

Synthèse des anomalies par compte.

## 11. Intégration Airflow

La Data Quality a été intégrée au DAG Airflow.

Le pipeline devient :

```text
ingest_qhc_file
        ↓
run_data_quality
```

Le `batch_id` est transmis via XCom.

La tâche Data Quality :

1. récupère le batch ;
2. localise `standardized_audits.csv` ;
3. exécute les règles ;
4. génère les rapports ;
5. évalue le DQ Gate ;
6. bloque uniquement en cas de `BLOCKING`.

L’intégration Airflow a été testée avec succès.

## 12. Tests

La Phase 4 comprend des tests sur :

- schéma ;
- domaines ;
- complétude conditionnelle ;
- cohérence métier ;
- dates ;
- moteur Data Quality ;
- DQ Gate ;
- génération des rapports métier.

Les tests finaux ont été validés.

## 13. Architecture finale de Phase 4

```text
standardized_audits.csv
        ↓
Data Quality Engine
        ↓
DQ Report
        ↓
DQ Gate
        │
        ├── WARNING / ERROR
        │       ↓
        │   CONTINUE
        │
        └── BLOCKING
                ↓
              BLOCK
```

En parallèle :

```text
DQ Engine
   ↓
Reporting métier
   ↓
Équipe Qualité
   ↓
Correction dans la source / workflow métier
   ↓
Prochaine ingestion
```

## 14. Résultat de la phase

La Phase 4 aboutit à une couche Data Quality :

- structurée ;
- testée ;
- traçable ;
- intégrée à Airflow ;
- lisible pour l’équipe métier ;
- capable de différencier erreurs métier et erreurs bloquantes ;
- prête à sécuriser le futur chargement PostgreSQL.

**Statut : Phase 4 prête pour validation finale.**
