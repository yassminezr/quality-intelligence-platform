# Phase 9 — FastAPI & Data Product

## 1. Objectif de la phase

La Phase 9 avait pour objectif de transformer la Quality Intelligence Platform en un **Data Product exposable via API**.

Avant cette phase, les données étaient principalement consommées par Streamlit à partir des marts PostgreSQL/dbt.

L’objectif était d’ajouter une couche d’exposition standardisée permettant à d’autres applications ou services de consommer les données sans accéder directement à PostgreSQL.

Architecture cible :

```text
PostgreSQL / dbt marts
        ↓
      FastAPI
        ↓
 REST API versionnée
        ↓
Streamlit / services / futurs consommateurs
```

La Phase 9 ne correspond pas au déploiement cloud. Elle prépare la plateforme à être utilisée comme un produit applicatif. Le déploiement sera traité dans la Phase 10.

---

## 2. Technologies utilisées

La couche API repose sur :

```text
FastAPI
Uvicorn
Pydantic
psycopg
pytest
httpx
Swagger / OpenAPI
ReDoc
```

FastAPI a été choisi pour :

- sa simplicité d’intégration avec Python ;
- son support natif des schémas Pydantic ;
- la génération automatique de documentation OpenAPI ;
- sa compatibilité avec une future architecture microservices / data product ;
- sa bonne intégration avec Docker et les pipelines CI/CD.

---

## 3. Structure créée

La structure principale ajoutée est :

```text
src/
└── api/
    ├── __init__.py
    ├── main.py
    ├── database.py
    ├── schemas.py
    └── routers/
        ├── __init__.py
        ├── health.py
        ├── kpis.py
        ├── accounts.py
        ├── findings.py
        ├── actions.py
        └── monitoring.py
```

Les tests sont stockés dans :

```text
tests/
└── api/
    └── test_api.py
```

---

## 4. Initialisation FastAPI

Le point d’entrée de l’API est :

```text
src/api/main.py
```

L’application FastAPI est configurée avec :

```text
title = Quality Intelligence Platform API
version = 1.0.0
docs_url = /docs
redoc_url = /redoc
openapi_url = /openapi.json
```

L’API est lancée localement avec :

```powershell
python -m uvicorn src.api.main:app --reload
```

Par défaut, elle est accessible sur :

```text
http://127.0.0.1:8000
```

---

## 5. Connexion PostgreSQL

La couche API réutilise la connexion PostgreSQL déjà existante dans :

```text
src/common/database.py
```

avec :

```text
get_postgres_connection()
```

Une couche spécifique API a été créée dans :

```text
src/api/database.py
```

avec deux helpers :

```text
fetch_one()
fetch_all()
```

Ces fonctions permettent de centraliser :

- l’ouverture de connexion ;
- l’exécution SQL ;
- la récupération des résultats ;
- la transformation des lignes en dictionnaires ;
- la fermeture propre des connexions.

L’API consomme principalement les marts du schéma :

```text
analytics
```

---

## 6. Health Checks

Deux endpoints de santé ont été créés.

### API health

```text
GET /health
```

Réponse :

```json
{
  "status": "ok",
  "service": "quality-intelligence-platform-api"
}
```

### Database health

```text
GET /health/db
```

Cet endpoint vérifie réellement la connexion PostgreSQL.

Il retourne notamment :

```text
status
database
user
checked_at
```

Cela permet de distinguer :

```text
API disponible
```

de :

```text
API disponible + PostgreSQL accessible
```

---

## 7. Contrats Pydantic

Les réponses API sont structurées avec des modèles Pydantic dans :

```text
src/api/schemas.py
```

Les principaux schémas créés sont :

```text
HealthResponse
DatabaseHealthResponse
OverviewKPIResponse
AccountSummaryResponse
AccountDetailResponse
FindingResponse
CorrectiveActionResponse
MonitoringRunResponse
MonitoringHistoryResponse
```

L’utilisation de Pydantic permet :

- de contrôler le format des réponses ;
- de détecter les incohérences entre SQL et API ;
- de générer automatiquement la documentation OpenAPI ;
- de définir un contrat stable pour les consommateurs.

---

## 8. Endpoint KPI global

Endpoint :

```text
GET /api/v1/kpis/overview
```

Cet endpoint expose les principaux KPI globaux de la plateforme.

Il retourne notamment :

```text
audits_planned
audited
in_progress
not_started
progress_pct
avg_maturity_score
total_findings
major_nc
open_actions
escalations
```

Les données proviennent des marts :

```text
analytics.mart_audit_overview
analytics.mart_findings
analytics.mart_corrective_actions
```

Les calculs sont réalisés à partir des règles métier déjà validées dans les phases précédentes.

---

## 9. Endpoints Accounts

Deux endpoints ont été créés.

### Liste des comptes

```text
GET /api/v1/accounts
```

Il retourne notamment :

```text
account_id
account_name
official_audit_status
completion_rate
avg_maturity_score
account_badge
```

### Détail d’un compte

```text
GET /api/v1/accounts/{account_id}
```

Si le compte n’existe pas, l’API retourne :

```text
HTTP 404
```

avec :

```json
{
  "detail": "Account not found"
}
```

---

## 10. Endpoints Findings

Endpoint principal :

```text
GET /api/v1/findings
```

Les filtres disponibles sont :

```text
account_name
category
limit
```

Exemples :

```text
GET /api/v1/findings?category=NC%20Mineure
GET /api/v1/findings?limit=10
```

Les catégories autorisées sont :

```text
NC Mineure
NC Majeure
Observation
OFI
Bonne Pratique
NA
```

Une valeur non autorisée retourne :

```text
HTTP 400
```

---

## 11. Endpoints Corrective Actions

Deux endpoints ont été créés.

### Liste des actions

```text
GET /api/v1/actions
```

Filtres disponibles :

```text
account_name
is_open
age_level
limit
```

Exemples :

```text
GET /api/v1/actions?is_open=true
GET /api/v1/actions?age_level=Critique
```

Les niveaux acceptés sont :

```text
Normal
Alerte
Critique
Escalade management
```

### Actions critiques

```text
GET /api/v1/actions/critical
```

Cet endpoint retourne uniquement les actions ouvertes avec :

```text
Critique
Escalade management
```

Il réutilise les règles déjà validées dans la Phase 8.

---

## 12. Endpoints Monitoring

Deux endpoints permettent d’exposer les résultats de la Phase 8.

### Monitoring runs

```text
GET /api/v1/monitoring/runs
```

Cet endpoint retourne l’historique des exécutions du moteur de monitoring.

Champs exposés :

```text
run_id
started_at
finished_at
status
actions_evaluated
events_detected
messages_prepared
emails_sent
emails_failed
duration_seconds
```

Un paramètre `limit` permet de limiter le nombre de runs retournés.

### Monitoring history

```text
GET /api/v1/monitoring/history
```

Filtres disponibles :

```text
action_id
level
limit
```

Champs exposés :

```text
monitoring_log_id
action_id
age_jours
niveau_escalade
monitored_at
```

---

## 13. Validation des paramètres

La Phase 9 a introduit plusieurs mécanismes de validation.

Exemples :

```text
limit >= 1
limit <= 500
```

ou :

```text
category ∈ catégories autorisées
```

ou :

```text
age_level ∈ niveaux autorisés
```

FastAPI retourne automatiquement :

```text
HTTP 422
```

pour les paramètres qui ne respectent pas les contraintes Pydantic/FastAPI.

Les règles métier invalides explicites retournent :

```text
HTTP 400
```

Les ressources inexistantes retournent :

```text
HTTP 404
```

---

## 14. Pagination légère

Une pagination simple par `limit` a été ajoutée sur les endpoints de listes.

Exemples :

```text
GET /api/v1/findings?limit=10
GET /api/v1/actions?limit=10
GET /api/v1/monitoring/runs?limit=5
```

L’objectif n’était pas de construire une pagination complexe mais de limiter la quantité de données retournée par défaut.

---

## 15. Versioning API

Les endpoints métier utilisent :

```text
/api/v1/
```

Exemples :

```text
/api/v1/kpis/overview
/api/v1/accounts
/api/v1/findings
/api/v1/actions
/api/v1/monitoring/runs
```

Cela prépare l’évolution future de l’API sans casser les consommateurs existants.

---

## 16. Documentation automatique

FastAPI génère automatiquement deux interfaces de documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

Swagger permet notamment :

- de visualiser tous les endpoints ;
- de consulter les paramètres ;
- de voir les schémas de réponse ;
- d’exécuter les appels directement depuis le navigateur.

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

ReDoc fournit une documentation orientée lecture.

### OpenAPI

Le contrat brut est disponible sur :

```text
/openapi.json
```

---

## 17. Tests automatiques

Des tests FastAPI ont été ajoutés dans :

```text
tests/api/test_api.py
```

Les tests utilisent :

```text
pytest
FastAPI TestClient
httpx
```

Ils couvrent notamment :

```text
health
database health
KPI overview
accounts
account not found
findings
finding category validation
finding limit validation
actions
open action filtering
age level validation
critical actions
monitoring runs
monitoring history
monitoring level validation
```

Résultat final :

```text
15 passed
```

Les tests vérifient réellement la chaîne :

```text
FastAPI
→ code API
→ PostgreSQL
→ marts dbt
```

Il s’agit donc principalement de tests d’intégration légers.

---

## 18. Problèmes détectés pendant les tests

Les tests ont permis de détecter deux erreurs de routage importantes.

### Accounts

La route :

```text
/api/v1/accounts/{account_id}
```

avait été associée au mauvais handler et retournait la liste complète des comptes au lieu d’un seul compte.

La séparation correcte est maintenant :

```text
GET /api/v1/accounts
→ get_accounts()

GET /api/v1/accounts/{account_id}
→ get_account()
```

### Monitoring

La route :

```text
/api/v1/monitoring/history
```

appelait le mauvais handler et retournait les monitoring runs au lieu de l’historique des changements.

La séparation correcte est maintenant :

```text
GET /api/v1/monitoring/runs
→ get_monitoring_runs()

GET /api/v1/monitoring/history
→ get_monitoring_history()
```

Après correction :

```text
15 tests sur 15 passent
```

---

## 19. Validation end-to-end

La Phase 9 a été validée de bout en bout avec le flux suivant :

```text
PostgreSQL
    ↓
dbt Analytics Marts
    ↓
FastAPI
    ↓
Pydantic
    ↓
REST API
    ↓
JSON / Swagger / ReDoc
```

Les endpoints ont été testés depuis le navigateur et via `pytest`.

---

## 20. Architecture après la Phase 9

L’architecture globale devient :

```text
Excel / SharePoint
        ↓
Python Ingestion
        ↓
Airflow
        ↓
Data Quality
        ↓
PostgreSQL Core
        ↓
dbt
        ↓
Analytics Marts
        ↓
      FastAPI
      ↙    ↓    ↘
Streamlit  Monitoring  futurs consommateurs
```

La plateforme ne dépend donc plus uniquement de Streamlit pour exposer ses données.

FastAPI devient une couche d’accès standardisée.

---

## 21. Positionnement Data Product

La Phase 9 permet de considérer la plateforme comme un Data Product, car elle fournit :

```text
données fiables
+ contrats API
+ validation
+ versioning
+ documentation
+ tests
+ endpoints métier
```

L’API pourra être utilisée plus tard par :

```text
Streamlit
applications web
applications mobiles
agents
services internes
Quality AI Copilot
```

sans exposer directement PostgreSQL.

---

## 22. Résultat final de la phase

Fonctionnalités livrées :

```text
✅ FastAPI
✅ Uvicorn
✅ connexion PostgreSQL
✅ health checks
✅ KPI endpoint
✅ accounts endpoints
✅ findings endpoint
✅ corrective actions endpoints
✅ critical actions endpoint
✅ monitoring endpoints
✅ filtres
✅ validation des paramètres
✅ gestion des erreurs HTTP
✅ pagination légère
✅ schémas Pydantic
✅ versioning /api/v1
✅ Swagger
✅ ReDoc
✅ OpenAPI
✅ tests automatiques
✅ 15 tests passés
✅ validation end-to-end
```

---

## 23. Limites actuelles

La Phase 9 reste volontairement légère.

Les éléments suivants ne sont pas encore implémentés :

```text
authentification
autorisation / rôles
rate limiting
pagination offset/cursor avancée
cache API
observabilité détaillée
déploiement cloud
```

Ils pourront être traités dans la phase d’industrialisation si nécessaire.

---

## 24. Prochaine étape

La prochaine phase est :

```text
Phase 10 — Docker, CI/CD & Azure
```

Objectifs principaux :

```text
Dockeriser FastAPI
intégrer tous les services dans Docker Compose
mettre en place GitHub Actions
automatiser les tests
préparer le déploiement
déployer sur Azure si le temps le permet
```

La Phase 9 est considérée comme **terminée et validée**.
