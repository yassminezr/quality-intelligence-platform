# Phase 3 — Ingestion & Raw Layer Report

## 1. Objectif de la phase

La Phase 3 avait pour objectif de construire la **porte d’entrée fiable de la Quality Intelligence Platform**.

L’objectif n’était pas encore de charger le modèle métier final dans PostgreSQL, mais de mettre en place une ingestion locale robuste, traçable, rejouable et orchestrable.

Le flux cible construit pendant cette phase est :

```text
Excel entrant
    ↓
détection du fichier
    ↓
calcul SHA-256
    ↓
détection de doublon
    ↓
création d’un ingestion_batch
    ↓
archivage du fichier dans le Raw Layer
    ↓
inventaire dynamique du workbook
    ↓
standardisation
    ↓
sortie standardized
    ↓
SUCCESS / FAILED
```

## 2. Structure mise en place

Les principaux dossiers utilisés sont :

```text
data/
├── incoming/
├── raw/
├── standardized/
├── profiling/
└── reference/

src/
├── common/
├── ingestion/
├── modeling/
├── profiling/
└── quality/

airflow/
└── dags/

tests/
```

- `data/incoming/` : zone d’arrivée du nouveau fichier Excel.
- `data/raw/` : conservation immuable du fichier source reçu.
- `data/standardized/` : données harmonisées et inventaire généré pour chaque batch.
- `src/ingestion/` : logique d’ingestion.
- `src/common/` : configuration et logging partagé.
- `airflow/dags/` : orchestration Airflow.
- `tests/` : tests automatisés.

## 3. Configuration centralisée

Le fichier `src/common/config.py` centralise notamment :

- `PROJECT_ROOT`
- `DATA_DIR`
- `INCOMING_DIR`
- `RAW_DIR`
- `STANDARDIZED_DIR`
- `PROFILING_DIR`
- `REFERENCE_DIR`
- `CURRENT_CAMPAIGN`

Cela évite les chemins codés en dur et facilite l’exécution locale et Docker.

## 4. Hash SHA-256 et idempotence

Chaque fichier entrant reçoit une empreinte SHA-256.

Règle retenue :

```text
même hash + batch SUCCESS
→ fichier déjà ingéré
→ ingestion ignorée
```

mais :

```text
même hash + batch FAILED
→ retraitement autorisé
```

Cette logique rend le pipeline idempotent.

## 5. Ingestion Batch

Chaque ingestion reçoit un identifiant unique de batch.

Les métadonnées conservées incluent :

- `batch_id`
- campagne
- fichier source
- hash
- timestamp d’ingestion
- statut

Cycle actuel :

```text
STARTED → SUCCESS
```

ou :

```text
STARTED → FAILED
```

Dans le prototype local, le registre est stocké en JSONL. À terme, cette logique sera portée par PostgreSQL.

## 6. Raw Layer

Le fichier Excel reçu est archivé avant les transformations métier.

Exemple :

```text
data/raw/
└── FY27/
    └── <date>/
        └── <batch_id>/
            └── fichier_source.xlsx
```

Le raw représente la copie fidèle de la source reçue et ne doit pas être modifié.

## 7. Inventaire dynamique du workbook

L’inventaire est recalculé pour chaque batch à partir du fichier raw réellement archivé.

Le pipeline génère `workbook_inventory.json`, contenant notamment :

- nombre de feuilles ;
- noms des feuilles ;
- type de feuille ;
- ligne d’en-tête détectée ;
- colonnes détectées.

Les feuilles d’audit sont détectées via une signature de colonnes métier.

## 8. Standardisation

Le fichier raw est ensuite standardisé à l’aide du mapping canonique défini pendant la Phase 1.

Sortie :

```text
data/standardized/
└── FY27/
    └── <batch_id>/
        ├── workbook_inventory.json
        └── standardized_audits.csv
```

Sur le dataset actuel :

```text
20 feuilles d’audit
45 lignes par feuille
900 lignes standardisées
```

## 9. Gestion des erreurs

Si une étape critique échoue, le batch est marqué `FAILED` et l’erreur est propagée pour le diagnostic.

En cas de succès complet, le batch est marqué `SUCCESS`.

## 10. Logging

Le pipeline utilise `logging` pour tracer :

- démarrage ;
- hash ;
- création du batch ;
- archivage raw ;
- inventaire ;
- standardisation ;
- succès ou échec.

Les logs sont visibles localement et dans Airflow.

## 11. Tests automatisés

Les tests couvrent notamment :

- hash stable sur même contenu ;
- hash différent si le fichier change ;
- détection d’un hash déjà traité avec succès ;
- retraitement autorisé après échec ;
- archivage raw fidèle ;
- sélection du fichier entrant ;
- comportement avec zéro ou plusieurs fichiers entrants ;
- test d’intégration complet.

Résultat actuel :

```text
9 tests passed
```

## 12. Sélection du fichier entrant

La règle actuelle de `data/incoming/` est :

```text
0 fichier .xlsx → erreur
1 fichier .xlsx → ingestion
plus d’un fichier .xlsx → erreur
```

Cette règle évite toute sélection arbitraire.

## 13. Airflow + Docker

Airflow est exécuté via Docker.

Une image Airflow personnalisée est construite avec les dépendances Python du projet.

Composants principaux :

- `airflow-init`
- `airflow-webserver`
- `airflow-scheduler`

Le DAG principal est :

```text
qhc_ingestion_pipeline
```

Le test Airflow a été validé :

- DAG importé sans erreur ;
- tâche lancée depuis l’interface ;
- logs présents ;
- fichier raw créé ;
- inventaire créé ;
- fichier standardized créé ;
- exécution réussie.

## 14. Architecture finale de Phase 3

```text
data/incoming/
       ↓
Airflow
       ↓
run_ingestion()
       ↓
SHA-256
       ↓
duplicate check
       ↓
ingestion_batch
       ↓
Raw immutable
       ↓
Workbook inventory
       ↓
Standardization
       ↓
data/standardized/
```

Puis :

```text
standardized
    ↓
Data Quality
    ↓
PostgreSQL Core Model
    ↓
dbt
    ↓
Data Marts
```

## 15. Résultat de la phase

La Phase 3 aboutit à une ingestion :

- traçable ;
- idempotente ;
- historisée au niveau source ;
- robuste aux doublons ;
- capable de gérer les échecs ;
- testée automatiquement ;
- orchestrée par Airflow ;
- exécutable dans Docker.

**Statut : Phase 3 prête pour validation finale.**
