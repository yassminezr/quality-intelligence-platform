# Quality Intelligence Platform

Plateforme Data end-to-end dédiée au pilotage des audits qualité, à l’analyse de la maturité, au suivi des findings et à la surveillance des actions correctives.

Le projet a été conçu à partir d’une mission réelle de stage autour des **Quality Health Checks (QHC)** et a été transformé en une plateforme complète combinant :

- Data Engineering
- Analytics Engineering
- Data Quality
- Data Visualization
- API / Data Product
- Monitoring automatisé
- Docker
- CI/CD
- Cloud Azure

---

## 1. Objectif du projet

La Quality Intelligence Platform permet de :

- centraliser les données d’audit issues de fichiers Excel multi-feuilles ;
- standardiser et fiabiliser les données ;
- historiser les évolutions ;
- calculer des KPI qualité ;
- analyser la maturité par compte et par clause ISO ;
- suivre les findings et les actions correctives ;
- surveiller automatiquement l’ancienneté des actions ;
- déclencher des niveaux d’escalade ;
- exposer les données via une API FastAPI ;
- visualiser les résultats dans une application Streamlit ;
- industrialiser le projet avec Docker, GitHub Actions et Azure.

---

## 2. Architecture globale

```text
Excel / SharePoint
        ↓
Python Ingestion
        ↓
Apache Airflow
        ↓
Data Quality
        ↓
PostgreSQL
        ↓
dbt
        ↓
Analytics Marts
     ↙      ↓       ↘
Streamlit FastAPI Monitoring
        ↓
Docker / CI
        ↓
Azure PostgreSQL + Azure Container Apps
```

---

## 3. Stack technique

### Data Engineering

- Python
- Pandas
- PostgreSQL
- Apache Airflow
- psycopg

### Analytics Engineering

- dbt
- SQL
- PostgreSQL analytics marts

### Data Quality

- contrôles de schéma
- règles métier
- contrôles de cohérence
- gestion des niveaux WARNING / ERROR / BLOCKING

### Data Visualization

- Streamlit

### API

- FastAPI
- Pydantic
- Uvicorn
- OpenAPI / Swagger
- ReDoc

### Monitoring

- Python
- moteur de règles déterministe
- historique des changements de niveau
- notifications email
- intégration LLM optionnelle uniquement pour la rédaction

### DevOps / Cloud

- Docker
- Docker Compose
- GitHub Actions
- Azure Database for PostgreSQL Flexible Server
- Azure Container Registry
- Azure Container Apps

---

## 4. Règles métier principales

### Statut audit proposé

```text
0 %        → non_audite
> 0 et <65 → en_cours
>= 65 %    → audite
```

Le statut proposé est un indicateur d’aide à la décision.

Le statut officiel reste le **statut validé par l’équipe Qualité**.

---

### Ancienneté des actions correctives

Pour une action ouverte :

```text
age_jours = date_du_jour - date_debut
```

Pour une action clôturée :

```text
age_jours = date_cloture - date_debut
```

L’âge est figé après clôture.

---

### Niveaux d’escalade

```text
0 – 30 jours   → Normal
31 – 60 jours  → Alerte
61 – 90 jours  → Critique
> 90 jours     → Escalade management
```

---

### Findings

Catégories gérées :

```text
NC Mineure
NC Majeure
Bonne Pratique
OFI
Observation
NA
```

Le KPI **Total findings** exclut les Bonnes Pratiques.

---

## 5. Modèle de données

Principales entités :

```text
Campagne
Compte
Audit
Clause ISO
Contrôle attendu
Évaluation
Finding
Action corrective
Statut proposé / validé
Historique
Temps
```

Principales cardinalités :

```text
1 Campagne → plusieurs Audits
1 Compte → 1 Audit par campagne
1 Audit → plusieurs Évaluations
1 Évaluation → 1 Finding
1 Finding → 0..1 Action corrective
```

---

## 6. Pipeline Data

Le pipeline principal suit les étapes :

```text
1. Ingestion Excel
2. Normalisation
3. Data Quality
4. Chargement staging
5. Chargement PostgreSQL Core
6. Historisation
7. Chargement des statuts validés
8. dbt run
9. dbt tests
10. Analytics marts
```

Airflow orchestre le pipeline.

---

## 7. Analytics marts

Principaux marts dbt :

```text
analytics.mart_audit_overview
analytics.mart_account_clause_detail
analytics.mart_findings
analytics.mart_corrective_actions
analytics.mart_maturity_distribution
analytics.mart_monitoring_runs
analytics.mart_action_monitoring_history
```

---

## 8. Streamlit

L’application Streamlit est accessible localement sur :

```text
http://localhost:8501
```

Pages principales :

```text
Synthèse Executive
Maturité & Performance
Findings & Actions
Détail Compte
Monitoring & Escalades
```

Principaux KPI :

```text
comptes audités
comptes en cours
comptes non audités
% avancement
score moyen de maturité
total findings
NC majeures
actions ouvertes
actions critiques
escalades
```

---

## 9. Monitoring des actions correctives

Le moteur de monitoring :

```text
PostgreSQL
    ↓
lecture actions
    ↓
calcul age_jours
    ↓
classification
    ↓
détection changement de niveau
    ↓
historisation
    ↓
préparation message
    ↓
notification optionnelle
```

Le moteur est déterministe.

Le LLM, lorsqu’il est activé, ne décide jamais du niveau d’escalade. Il sert uniquement à reformuler les messages.

---

## 10. FastAPI

L’API est accessible localement sur :

```text
http://localhost:8000
```

Swagger :

```text
http://localhost:8000/docs
```

ReDoc :

```text
http://localhost:8000/redoc
```

Principaux endpoints :

```text
GET /health
GET /health/db

GET /api/v1/kpis/overview

GET /api/v1/accounts
GET /api/v1/accounts/{account_id}

GET /api/v1/findings

GET /api/v1/actions
GET /api/v1/actions/critical

GET /api/v1/monitoring/runs
GET /api/v1/monitoring/history
```

L’API inclut :

- schémas Pydantic ;
- validation des paramètres ;
- filtres ;
- pagination légère ;
- erreurs HTTP 400 / 404 / 422 ;
- versioning `/api/v1`.

---

## 11. Tests

Le projet contient des tests couvrant notamment :

- Data Quality ;
- ingestion ;
- monitoring ;
- escalade ;
- notifications ;
- historisation ;
- hash ;
- API FastAPI.

Résultat final du pipeline CI :

```text
103 tests exécutés
103 tests passés
```

---

## 12. CI avec GitHub Actions

Le workflow CI est défini dans :

```text
.github/workflows/ci.yml
```

Il se déclenche sur :

```text
push sur main
pull request vers main
```

Étapes principales :

```text
Checkout
Setup Python
Install dependencies
Start PostgreSQL
Initialize API test database
Install dbt
dbt debug
dbt deps
dbt parse
pytest
```

---

## 13. Docker

Services Docker :

```text
postgres
airflow-init
airflow-webserver
airflow-scheduler
streamlit
api
```

Lancement global :

```powershell
docker compose up -d
```

Vérification :

```powershell
docker compose ps
```

Arrêt :

```powershell
docker compose down
```

---

## 14. Configuration

Créer un fichier `.env` à partir de :

```text
.env.example
```

Variables principales :

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD

OPENAI_API_KEY
OPENAI_MODEL
LLM_ENABLED

SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_SENDER_EMAIL
SMTP_USE_TLS

QIP_RECIPIENT_ALERT
QIP_RECIPIENT_CRITICAL
QIP_RECIPIENT_MANAGEMENT

EMAIL_NOTIFICATIONS_ENABLED
```

Le fichier `.env` ne doit jamais être versionné.

---

## 15. Déploiement Azure

La partie cloud comprend :

```text
Azure Resource Group
Azure Database for PostgreSQL Flexible Server
Azure Container Registry
Azure Container Apps
```

Architecture :

```text
Azure Resource Group
│
├── Azure PostgreSQL
│     └── quality_intelligence
│
├── Azure Container Registry
│     └── qip-api:v1
│
└── Azure Container Apps
      └── qip-api
            ↓
      Azure PostgreSQL
```

La base locale a été migrée vers Azure via :

```text
pg_dump
pg_restore
```

Validation :

```text
analytics.mart_audit_overview → 20 comptes
```

FastAPI a été déployée sur Azure Container Apps.

Endpoints cloud validés :

```text
/health
/docs
/health/db
```

---

## 16. Structure principale du repository

```text
quality-intelligence-platform/
│
├── airflow/
│   └── dags/
│
├── analytics/
│   └── qip_analytics/
│
├── docs/
│
├── src/
│   ├── api/
│   ├── common/
│   ├── ingestion/
│   ├── monitoring/
│   └── ...
│
├── streamlit_app/
│   ├── app.py
│   ├── data/
│   ├── pages/
│   └── styles/
│
├── tests/
│   ├── api/
│   └── fixtures/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile.airflow
├── Dockerfile.api
├── Dockerfile.streamlit
├── requirements.txt
└── README.md
```

---

## 17. Lancement local rapide

### 1. Cloner le projet

```powershell
git clone <repository-url>
cd quality-intelligence-platform
```

### 2. Créer le fichier `.env`

Copier :

```text
.env.example
```

vers :

```text
.env
```

Puis renseigner les variables nécessaires.

### 3. Lancer la plateforme

```powershell
docker compose up -d
```

### 4. Vérifier les services

```text
Airflow   → http://localhost:8080
Streamlit → http://localhost:8501
FastAPI   → http://localhost:8000
Swagger   → http://localhost:8000/docs
```

---

## 18. Documentation

Les rapports détaillés des différentes phases sont disponibles dans :

```text
docs/
```

Ils couvrent notamment :

```text
modélisation
ingestion
Data Quality
PostgreSQL
dbt
Streamlit
monitoring
FastAPI
Docker / CI/CD / Azure
```

---

## 19. Extensions futures

Évolutions possibles :

```text
déploiement Streamlit sur Azure
déploiement Airflow sur Azure
Azure Key Vault
private networking
Azure Monitor
CD automatique
Quality AI Copilot
authentification / rôles API
cache API
observabilité avancée
```

---

## 20. Statut du projet

```text
Quality Intelligence Platform — v1.0.0
```

Statut :

```text
✅ projet terminé
✅ pipeline Data opérationnel
✅ dashboards opérationnels
✅ monitoring opérationnel
✅ API opérationnelle
✅ tests automatisés
✅ CI verte
✅ Docker opérationnel
✅ PostgreSQL Azure déployé
✅ FastAPI Azure déployée
```

---

## 21. Auteur

Projet réalisé dans le cadre d’un projet Data / stage ingénieur.

**Yassmine ZERAIDI**  
ENSIAS — Génie de la Data
