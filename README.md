# Quality Intelligence Platform

> **End-to-end Quality Audit & Decision Platform** — from heterogeneous Excel audit workbooks to a governed PostgreSQL model, dbt analytics marts, Streamlit dashboards, automated corrective-action monitoring, FastAPI data products, CI/CD and Azure deployment.

---

## Project overview

The **Quality Intelligence Platform (QIP)** was built from a real internship use case around **Quality Health Checks (QHC)** and progressively transformed into a complete Data Engineering / Analytics Engineering platform.

The initial business need was to centralize, clean, analyze and visualize quality audit data. The final platform goes much further by combining:

- Data Engineering
- Analytics Engineering
- Data Quality
- Data Modeling
- Data Visualization
- Monitoring & Escalation
- API / Data Product
- Docker
- CI/CD
- Azure Cloud

The platform covers the full lifecycle:

```text
Excel / SharePoint
        ↓
Python ingestion
        ↓
Apache Airflow
        ↓
Data Quality
        ↓
PostgreSQL
        ↓
dbt
        ↓
Analytics marts
     ↙      ↓       ↘
Streamlit FastAPI Monitoring Agent
        ↓
Docker / GitHub Actions
        ↓
Azure PostgreSQL + Azure Container Apps
```

---

# Key capabilities

The platform provides:

- automated ingestion of heterogeneous Excel audit sheets;
- canonical schema normalization;
- incremental and traceable loading;
- data quality controls and business-rule validation;
- historical and auditable PostgreSQL storage;
- dbt analytics marts;
- KPI calculation;
- executive and operational Streamlit dashboards;
- account-level and ISO clause-level analysis;
- corrective-action ageing;
- deterministic escalation monitoring;
- change detection and idempotence;
- monitoring run history;
- SMTP notifications;
- optional LLM-assisted message rewriting;
- FastAPI REST endpoints;
- automated tests;
- GitHub Actions CI;
- Dockerized local execution;
- Azure PostgreSQL deployment;
- FastAPI deployment on Azure Container Apps.

---

# Development roadmap

The project was developed through the following phases:

```text
Data Understanding & Profiling

1. Data Modeling
2. Automated & Incremental Ingestion
3. Data Quality
4. PostgreSQL / Physical Modeling & Loading
5. Analytics Engineering with dbt
6. KPI & Streamlit
7. Corrective Action Monitoring & Escalation Agent
8. FastAPI & Data Product
9. Docker, CI/CD & Azure
```

---

# Data Understanding & Profiling

The first stage focused on understanding the real audit workbook before implementing any architecture.

Main work:

- audit-sheet identification;
- schema-variant detection;
- profiling of maturity scores;
- profiling of findings and corrective actions;
- missing-value analysis;
- date consistency analysis;
- business-rule clarification;
- canonical field mapping;
- confirmation of analytical granularity.

Dataset characteristics included:

```text
20 audit accounts
45 source rows per account
37 real ISO clauses / controls
multiple schema variants
heterogeneous date and status columns
```

Confirmed analytical grain:

```text
1 row = 1 account × 1 ISO clause
```

This profiling phase was essential to avoid designing the platform around incorrect assumptions.

---

# 1. Data Modeling

The spreadsheet structure was transformed into a normalized and traceable data model.

Main entities:

```text
Campaign
Account
Audit
ISO Clause
Expected Control
Evaluation
Finding
Corrective Action
Validated Audit Status
History
Time
```

Main relationships:

```text
1 Account → 1 Audit per Campaign
1 Audit → many Evaluations
1 Evaluation → 1 Finding
1 Finding → 0..1 Corrective Action
```

The model separates:

- reference data;
- audit results;
- findings;
- corrective actions;
- validated statuses;
- historical changes.

This prevents mixing expected ISO controls with operational audit results.

---

# 2. Automated & Incremental Ingestion

A Python ingestion pipeline standardizes heterogeneous Excel sheets.

Main responsibilities:

- sheet detection;
- source-column mapping;
- normalization;
- canonical schema creation;
- source traceability;
- incremental loading preparation;
- reusable ingestion logic.

Flow:

```text
Excel workbook
    ↓
Python ingestion
    ↓
schema normalization
    ↓
standardized dataset
    ↓
PostgreSQL staging
```

The ingestion is orchestrated by **Apache Airflow**.

---

# 3. Data Quality

A dedicated Data Quality layer validates incoming data before downstream consumption.

Checks include:

- schema conformity;
- required fields;
- maturity-score validity;
- finding-category validity;
- date consistency;
- corrective-action consistency;
- duplicates;
- status consistency;
- business-rule validation.

Severity policy:

```text
WARNING  → continue + report
ERROR    → continue + report + correction expected
BLOCKING → stop pipeline
```

This prevents poor source quality from silently propagating into analytics.

---

# 4. PostgreSQL / Physical Modeling & Loading

PostgreSQL is the central persistence layer.

Logical schemas include:

```text
metadata
staging
quality
core
analytics
monitoring
```

The physical model supports:

- technical IDs;
- business keys;
- source traceability;
- immutable source preservation;
- audit status validation;
- evaluation history;
- monitoring history;
- analytics-ready consumption.

This provides both operational reliability and auditability.

---

# 5. Analytics Engineering with dbt

dbt transforms the core model into reusable analytics datasets.

Main marts:

```text
analytics.mart_audit_overview
analytics.mart_account_clause_detail
analytics.mart_findings
analytics.mart_corrective_actions
analytics.mart_maturity_distribution
analytics.mart_monitoring_runs
analytics.mart_action_monitoring_history
```

The dbt layer provides:

- modular SQL transformations;
- documented analytics logic;
- tests;
- separation between core storage and reporting logic;
- stable datasets for Streamlit and FastAPI.

The account-clause mart preserves the grain:

```text
1 account × 1 ISO clause
```

---

# 6. KPI & Streamlit

A Streamlit application was built as the decision-support interface for the Quality team.

Main pages:

```text
Executive Summary
Maturity & Performance
Findings & Actions
Account Detail
Monitoring & Escalations
```

Main KPIs:

- planned audits;
- audited accounts;
- audits in progress;
- non-audited accounts;
- audit progress rate;
- average maturity score;
- total findings;
- major non-conformities;
- open corrective actions;
- critical actions;
- escalations.

Local URL:

```text
http://localhost:8501
```

The dashboard supports both executive and operational analysis.

---

# 7. Corrective Action Monitoring & Escalation Agent

One of the strongest components of the project is the automated monitoring engine for corrective actions.

The objective is not only to display actions, but to continuously evaluate their ageing and detect when an escalation level changes.

## Core capabilities

```text
✅ deterministic rule engine
✅ corrective-action age calculation
✅ escalation-level classification
✅ change detection
✅ idempotence
✅ business logs
✅ monitoring run history
✅ deterministic messages
✅ optional LLM rewriting
✅ SMTP email notifications
✅ Airflow orchestration
✅ PostgreSQL integration
✅ dbt staging
✅ dbt marts
✅ dbt tests
✅ Python tests
✅ dedicated Streamlit page
✅ Docker hardening
✅ end-to-end validation
```

## Age calculation

For an open action:

```text
age_jours = current_date - date_debut
```

For a closed action:

```text
age_jours = date_cloture - date_debut
```

Once closed, the age is frozen.

## Escalation levels

```text
0–30 days   → Normal
31–60 days  → Alert
61–90 days  → Critical
>90 days    → Management Escalation
```

## Change detection & idempotence

The engine compares the current level with the last historical level.

An event is created only when the level changes.

Example:

```text
Alert
  ↓
Critical
  ↓
Monitoring event
```

This prevents repeated alerts for an unchanged state.

## Persistence

Dedicated monitoring structures:

```text
monitoring.action_monitoring_log
monitoring.monitoring_run_log
```

They preserve:

- action monitoring history;
- detected level changes;
- run start/end timestamps;
- run status;
- actions evaluated;
- events detected;
- messages prepared;
- emails sent;
- failed notifications;
- execution duration.

## Optional LLM

The LLM is intentionally restricted.

It never decides:

```text
age calculation
classification
escalation level
change detection
```

It may only rewrite a deterministic message for communication.

This keeps the monitoring logic explainable, testable and auditable.

---

# 8. FastAPI & Data Product

The analytics layer is exposed as a reusable REST API.

Local API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Main endpoints:

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

The API includes:

- Pydantic contracts;
- parameter validation;
- HTTP 400 / 404 / 422 handling;
- filters;
- lightweight pagination;
- `/api/v1` versioning;
- OpenAPI documentation.

This turns the analytics layer into a true **Data Product** and avoids direct database access for consumers.

---

# 9. Docker, CI/CD & Azure

The final phase industrialized the platform.

## Docker

Main services:

```text
postgres
airflow-init
airflow-webserver
airflow-scheduler
streamlit
api
```

Start locally:

```powershell
docker compose up -d
```

Check:

```powershell
docker compose ps
```

---

## GitHub Actions CI

The CI pipeline runs on:

```text
push to main
pull request to main
```

Main steps:

```text
Checkout
Python setup
Install dependencies
Start PostgreSQL
Initialize API test database
Install dbt
dbt debug
dbt deps
dbt parse
pytest
```

Final CI result:

```text
103 tests executed
103 tests passed
```

Tests cover major parts of the platform including:

```text
Data Quality
ingestion
monitoring
escalation
notifications
history
hash logic
FastAPI
```

---

## Azure deployment

The project includes a real cloud deployment.

### Azure Database for PostgreSQL

```text
Azure Database for PostgreSQL Flexible Server
PostgreSQL 16
Database: quality_intelligence
TLS connection validated
```

The local database was migrated with:

```text
pg_dump
pg_restore
```

Validation:

```text
analytics.mart_audit_overview → 20 accounts
```

### Azure Container Registry

FastAPI image:

```text
qip-api:v1
```

was pushed to Azure Container Registry.

### Azure Container Apps

FastAPI was deployed publicly through Azure Container Apps.

Validated endpoints:

```text
/health      ✅
/docs        ✅
/health/db   ✅
```

Cloud flow:

```text
Azure Container Apps
        ↓
FastAPI
        ↓
Azure PostgreSQL
        ↓
Analytics marts
```

---

# Main business rules

## Audit status

The platform distinguishes:

```text
statut_propose
statut_valide
```

Proposal rule:

```text
0% completion        → non_audite
>0% and <65%         → en_cours
>=65%                → audite
```

The validated status remains the official source of truth.

## Findings

Supported categories:

```text
NC Mineure
NC Majeure
Bonne Pratique
OFI
Observation
NA
```

The **Total Findings** KPI excludes `Bonne Pratique`.

## Corrective actions

A corrective action exists only when a finding requires treatment.

Examples:

```text
Bonne Pratique → action optional
NA             → no corrective action
```

---

# Repository structure

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
├── .github/
│   └── workflows/
│       └── ci.yml
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

# Quick start

## 1. Clone

```powershell
git clone <repository-url>
cd quality-intelligence-platform
```

## 2. Configure environment

Copy:

```text
.env.example
```

to:

```text
.env
```

and fill the required values.

Never commit `.env`.

## 3. Start the platform

```powershell
docker compose up -d
```

## 4. Access services

```text
Airflow   → http://localhost:8080
Streamlit → http://localhost:8501
FastAPI   → http://localhost:8000
Swagger   → http://localhost:8000/docs
```

---

# Testing

Run the Python test suite:

```powershell
python -m pytest -v
```

Run API tests:

```powershell
python -m pytest tests/api/test_api.py -v
```

Validate dbt:

```powershell
cd analytics/qip_analytics
dbt debug
dbt deps
dbt parse
```

---

# Documentation

Detailed phase reports are available in:

```text
docs/
```

Coverage:

```text
Data Understanding & Profiling
Data Modeling
Automated & Incremental Ingestion
Data Quality
PostgreSQL
Analytics Engineering with dbt
KPI & Streamlit
Corrective Action Monitoring & Escalation Agent
FastAPI & Data Product
Docker, CI/CD & Azure
```

---

# Why this project is valuable

This project goes beyond a classic dashboard or ETL pipeline.

It combines:

```text
real business data
+
data modeling
+
orchestration
+
data quality
+
historization
+
analytics engineering
+
decision dashboards
+
automated monitoring
+
API productization
+
testing
+
CI/CD
+
cloud deployment
```

The result is a complete Data Platform addressing both **analytical decision-making** and **operational quality monitoring**.

---

# Future improvements

Possible extensions:

```text
Streamlit deployment on Azure
Airflow deployment on managed cloud infrastructure
Azure Key Vault
private networking
Azure Monitor
automatic CD to Azure Container Apps
API authentication / RBAC
advanced observability
Quality AI Copilot
```

---

# Project status

```text
Quality Intelligence Platform — v1.0.0
```

```text
✅ Data pipeline operational
✅ Data Quality operational
✅ PostgreSQL model operational
✅ dbt analytics layer operational
✅ Streamlit dashboards operational
✅ Monitoring & Escalation Agent operational
✅ FastAPI Data Product operational
✅ Docker environment operational
✅ CI pipeline green
✅ 103 automated tests passed
✅ Azure PostgreSQL deployed
✅ FastAPI deployed on Azure
```

---

# Author

**Yassmine ZERAIDI**  
ENSIAS — Génie de la Data
