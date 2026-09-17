# Rapport Phase 6 — dbt / Analytics Engineering

## Projet
**Quality Intelligence Platform — Intelligent Quality Audit & Decision Platform**

## Objectif de la phase
La Phase 6 avait pour objectif d’ajouter une véritable couche **Analytics Engineering** au-dessus du modèle Core PostgreSQL afin de :

- séparer le modèle métier normalisé du modèle analytique ;
- préparer des données directement exploitables par Power BI ;
- centraliser les transformations SQL ;
- versionner et tester les modèles analytiques ;
- documenter automatiquement les dépendances et le lineage ;
- intégrer l’exécution dbt dans Airflow.

---

## 1. Architecture retenue

L’architecture finale de la phase est :

```text
PostgreSQL Core
    ↓
dbt Sources
    ↓
dbt Staging
    ↓
dbt Intermediate
    ↓
dbt Marts
    ↓
Power BI
```

Le pipeline orchestré complet devient :

```text
Excel
↓
Ingestion Python
↓
Data Quality
↓
PostgreSQL Staging
↓
PostgreSQL Core
↓
Validation métier
↓
dbt run
↓
dbt test
↓
Marts Analytics
↓
Power BI
```

## 2. Installation et configuration dbt

### Versions retenues

```text
dbt-core==1.10.23
dbt-postgres==1.10.0
```

Ces versions ont été épinglées pour garantir la compatibilité avec l’environnement Windows/Python du projet.

### Projet dbt

Chemin :

```text
analytics/qip_analytics/
```

Configuration principale :

```yaml
name: qip_analytics
version: 1.0.0
profile: qip_analytics
```

### Connexion PostgreSQL

En local :

```text
host = localhost
```

Dans Docker / Airflow :

```text
host = postgres
```

Base :

```text
quality_intelligence
```

Schéma analytique :

```text
analytics
```

## 3. Sources dbt

Les sources déclarées dans `models/staging/sources.yml` sont principalement :

### Schéma `core`

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

### Schéma `quality`

- `dq_issues`

Exemple :

```sql
{{ source('core', 'evaluation') }}
```

## 4. Modèles Staging

Modèles créés :

```text
stg_accounts
stg_campaigns
stg_audits
stg_iso_clauses
stg_iso_controls
stg_evaluations
stg_findings
stg_corrective_actions
```

Matérialisation :

```text
VIEW
```

Objectif :

- éviter la duplication inutile ;
- exposer des colonnes propres et stables ;
- fournir l’interface d’entrée aux modèles dbt suivants.

Exécution validée :

```text
PASS=8
ERROR=0
```

## 5. Modèles Intermediate

### `int_audit_evaluations`

Joint :

```text
evaluation
+ audit
+ account
+ campaign
+ iso_control
+ iso_clause
```

### `int_findings_enriched`

Ajoute aux findings :

- compte ;
- campagne ;
- clause ISO ;
- contrôle ;
- score de maturité ;
- niveau de maturité ;
- constat auditeur.

### `int_corrective_actions_enriched`

Ajoute aux actions correctives :

- compte ;
- campagne ;
- clause ISO ;
- catégorie du finding ;
- âge calculé ;
- indicateur d’âge.

Règle d’âge :

```text
Action non clôturée
→ current_date - date_debut

Action clôturée
→ date_cloture - date_debut
```

Seuils :

```text
0–30 jours  → Normal
31–60 jours → Alerte
61–90 jours → Critique
>90 jours   → Escalade management
```

## 6. Data Marts

Les marts sont matérialisés en :

```text
TABLE
```

### 6.1 `mart_audit_overview`

Granularité :

```text
1 ligne = 1 audit / compte / campagne
```

Principaux indicateurs :

- completion rate ;
- statut proposé ;
- statut officiel validé ;
- score moyen ;
- badge du compte ;
- nombre d’évaluations ;
- findings ;
- NC Mineures ;
- NC Majeures ;
- OFI ;
- Observations ;
- Bonnes Pratiques ;
- NA ;
- actions correctives ;
- actions ouvertes ;
- alertes ;
- actions critiques ;
- escalades.

Badge compte :

```text
>= 4.5 → Très Performant
>= 3.5 → Performant
>= 2.5 → À surveiller
>= 1.5 → À Risque
< 1.5  → Critique
```

Le KPI Total Findings exclut :

```text
Bonne Pratique
NA
```

### 6.2 `mart_account_clause_detail`

Granularité :

```text
1 ligne = 1 audit × 1 contrôle ISO
```

Grille complète :

```text
20 comptes × 37 contrôles ISO = 740 lignes
```

Les clauses non évaluées sont conservées avec des valeurs analytiques `NULL`.

Principales colonnes :

- compte ;
- campagne ;
- clause ISO ;
- intitulé ISO ;
- libellé terrain ;
- contrôle attendu ;
- score ;
- niveau ;
- constat ;
- finding ;
- action corrective ;
- responsable ;
- statut action ;
- date début ;
- date clôture ;
- âge ;
- indicateur âge.

### 6.3 `mart_findings`

Granularité :

```text
1 ligne = 1 finding
```

Permet :

- findings par compte ;
- findings par catégorie ;
- findings par clause ISO ;
- analyse transverse des clauses problématiques ;
- top clauses.

### 6.4 `mart_corrective_actions`

Granularité :

```text
1 ligne = 1 action corrective
```

Principales colonnes :

- compte ;
- clause ;
- catégorie finding ;
- action ;
- responsable ;
- dates ;
- statut ;
- âge ;
- indicateur âge ;
- `is_open` ;
- `is_closed` ;
- `requires_attention`.

### 6.5 `mart_maturity_distribution`

Permet l’analyse de la distribution des scores et niveaux de maturité par compte et campagne.

## 7. Couverture Power BI

### Synthèse exécutive

Source :

```text
mart_audit_overview
```

KPI possibles :

- comptes audités ;
- comptes en cours ;
- comptes non démarrés ;
- % avancement ;
- score moyen ;
- total findings ;
- NC Majeures ;
- NC Mineures ;
- OFI ;
- Bonnes Pratiques ;
- actions ouvertes ;
- escalades.

### Vue détaillée d’un compte

Source :

```text
mart_account_clause_detail
```

Un filtre `Compte` permet d’afficher l’audit détaillé du compte sélectionné.

### Analyse Findings

Source :

```text
mart_findings
```

### Suivi CAPA

Source :

```text
mart_corrective_actions
```

## 8. Gestion du statut d’audit

La plateforme distingue :

```text
current_proposed_status
```

et :

```text
current_validated_status
```

Le statut proposé est calculé automatiquement.

Le statut validé est confirmé par l’équipe Qualité et constitue la vérité officielle.

Un statut officiel manquant n’est pas remplacé automatiquement par le statut proposé.

## 9. Tests dbt

Tests génériques utilisés :

- `not_null`
- `unique`
- `relationships`
- `accepted_values`

Tests métier personnalisés :

```text
assert_no_na_corrective_actions
```

et :

```text
assert_score_between_1_and_5
```

Les tests dbt ont été exécutés avec succès.

## 10. Data Quality vs tests dbt

### Data Quality Python

Politique :

```text
WARNING  → continue
ERROR    → continue
BLOCKING → stop
```

Exemple :

```text
action corrective présente
+ finding absent
→ DQ_CONSISTENCY_002
→ ERROR
→ pipeline continue
```

### Tests dbt

Ils interviennent après la construction des modèles analytiques et sécurisent :

- clés ;
- relations ;
- domaines ;
- contraintes analytiques ;
- règles métier finales.

## 11. Documentation dbt et Lineage

La documentation a été générée avec :

```text
dbt docs generate
dbt docs serve
```

Le lineage a été visualisé avec succès.

Exemple :

```text
core.evaluation
↓
stg_evaluations
↓
int_audit_evaluations
↓
mart_audit_overview
```

Autre exemple :

```text
core.corrective_action
↓
stg_corrective_actions
↓
int_corrective_actions_enriched
↓
mart_corrective_actions
```

## 12. Intégration dbt dans Airflow

Le DAG final contient désormais 10 tâches :

```text
1. ingest_qhc_file
2. run_data_quality
3. load_postgres_staging
4. load_postgres_dq
5. load_core_audits
6. load_core_iso
7. load_core_evaluations
8. load_core_validations
9. run_dbt_models
10. run_dbt_tests
```

Le DAG complet a été exécuté avec succès :

```text
10 / 10 tâches SUCCESS
```

Airflow orchestre donc automatiquement le pipeline jusqu’aux marts analytiques.

## 13. Problème environnemental rencontré

Lors de l’installation de Git dans l’image Airflow, Docker a rencontré :

```text
Release file ... is not valid yet
```

La cause identifiée est une désynchronisation de l’horloge Windows / WSL2 / Docker.

Décision :

- ne pas bloquer la Phase 6 sur ce problème ;
- Git n’est pas nécessaire pour les commandes dbt actuellement utilisées ;
- traiter Windows Time lorsque cela devient réellement nécessaire dans le projet.

## 14. Résultat final de la Phase 6

```text
6.1 Installation dbt                  ✅
6.2 Configuration projet              ✅
6.3 Déclaration des sources           ✅
6.4 Modèles staging                   ✅
6.5 Modèles intermédiaires            ✅
6.6 Data marts                        ✅
6.7 Tests dbt                         ✅
6.8 Documentation + lineage           ✅
6.9 Intégration Airflow               ✅
6.10 Validation finale                ✅
```

## 15. Questions d’entretien à retenir

### Pourquoi utiliser dbt alors que PostgreSQL existe déjà ?

PostgreSQL stocke le modèle métier Core. dbt transforme ce Core en modèles analytiques versionnés, testés, documentés et adaptés à la BI.

### Différence entre `source()` et `ref()`

```text
source()
→ table externe à dbt

ref()
→ modèle dbt
```

### Pourquoi Staging / Intermediate / Marts ?

```text
Staging
→ interface propre avec les sources

Intermediate
→ jointures et règles réutilisables

Marts
→ modèles prêts pour la consommation BI
```

### Pourquoi des vues pour Staging/Intermediate et des tables pour les Marts ?

Les vues limitent la duplication de données pendant les transformations intermédiaires. Les marts sont matérialisés en tables pour faciliter et accélérer leur consommation par Power BI.

### Différence Data Quality et tests dbt

La Data Quality contrôle la qualité des données entrant dans le pipeline. Les tests dbt vérifient la cohérence et l’intégrité des modèles analytiques après transformation.

# Conclusion

La Phase 6 transforme le projet en une architecture complète de **Data Engineering + Analytics Engineering**.

Le système dispose désormais :

- d’un modèle métier Core ;
- d’une couche analytique dbt ;
- de marts prêts pour Power BI ;
- de tests automatisés ;
- d’une documentation ;
- d’un lineage ;
- d’une orchestration Airflow complète.

La plateforme est prête à utiliser ces marts comme fondation des prochaines phases.
