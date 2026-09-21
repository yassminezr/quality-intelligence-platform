# Phase 10 — Docker, CI/CD & Azure

## 1. Objectif de la phase

La Phase 10 avait pour objectif d’industrialiser la Quality Intelligence Platform et de préparer une version exploitable au-delà du poste local.

Les objectifs principaux étaient :

```text
Dockeriser FastAPI
intégrer les services dans Docker Compose
mettre en place un pipeline CI avec GitHub Actions
valider le projet dbt dans le CI
sécuriser la configuration avec des variables d’environnement
préparer le projet au déploiement
déployer une partie de l’architecture sur Azure
```

Cette phase constitue la dernière grande phase technique du projet.

---

## 2. Architecture avant la Phase 10

Avant cette phase, la plateforme était déjà fonctionnelle avec :

```text
Excel / SharePoint
        ↓
Python ingestion
        ↓
Airflow
        ↓
Data Quality
        ↓
PostgreSQL
        ↓
dbt
        ↓
Analytics marts
      ↙      ↓       ↘
Streamlit  FastAPI  Monitoring
```

La Phase 10 a ajouté :

```text
Dockerisation complète
CI GitHub Actions
gestion propre des secrets
Azure PostgreSQL
Azure Container Registry
Azure Container Apps
```

---

## 3. Dockerisation de FastAPI

Un fichier dédié a été créé :

```text
Dockerfile.api
```

Configuration finale :

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --default-timeout=120 --retries 5 -r requirements.txt

COPY src ./src

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

FastAPI est donc packagée dans une image Docker indépendante.

Le service expose :

```text
port 8000
```

et démarre automatiquement Uvicorn.

---

## 4. Intégration dans Docker Compose

Le fichier :

```text
docker-compose.yml
```

regroupe désormais les principaux composants de la plateforme.

Services :

```text
postgres
airflow-init
airflow-webserver
airflow-scheduler
streamlit
api
```

Architecture Docker locale :

```text
Docker Compose
│
├── PostgreSQL
├── Airflow init
├── Airflow webserver
├── Airflow scheduler
├── Streamlit
└── FastAPI
```

Les conteneurs communiquent sur le réseau Docker via :

```text
POSTGRES_HOST=postgres
```

alors que les exécutions locales utilisent :

```text
POSTGRES_HOST=localhost
```

---

## 5. Validation Docker locale

La plateforme a été validée avec :

```powershell
docker compose up -d
docker compose ps
```

Résultat final :

```text
PostgreSQL          Up / healthy
Airflow webserver   Up
Airflow scheduler   Up
Streamlit           Up
FastAPI             Up
```

Les services ont été validés via :

```text
Airflow   → http://localhost:8080
Streamlit → http://localhost:8501
FastAPI   → http://localhost:8000
Swagger   → http://localhost:8000/docs
```

Le health check base de données FastAPI a aussi été validé :

```text
GET /health/db
```

---

## 6. Configuration des variables d’environnement

Les valeurs sensibles ont été centralisées dans :

```text
.env
```

Le fichier `.env` est exclu de Git grâce à :

```gitignore
.env
```

Un fichier :

```text
.env.example
```

a été créé avec uniquement des placeholders.

Exemple :

```text
POSTGRES_PASSWORD=change_me
OPENAI_API_KEY=change_me
SMTP_PASSWORD=change_me
```

Cela permet à un autre utilisateur de comprendre quelles variables sont nécessaires sans exposer de secrets.

---

## 7. Nettoyage des secrets

Le `docker-compose.yml` a été modifié pour consommer les variables d’environnement.

Exemple :

```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

au lieu de :

```yaml
POSTGRES_PASSWORD: qip_password
```

La configuration dbt a également été nettoyée afin d’utiliser :

```yaml
password: "{{ env_var('POSTGRES_PASSWORD') }}"
```

sans fallback sensible.

Une vérification Git a été réalisée avec :

```powershell
git grep -n "OPENAI_API_KEY\|SMTP_PASSWORD\|POSTGRES_PASSWORD"
```

Les seules occurrences restantes concernent :

```text
placeholders
références de variables d’environnement
configuration CI temporaire
documentation
```

Aucun vrai secret n’est versionné.

---

## 8. Mise en place de GitHub Actions CI

Un workflow a été créé :

```text
.github/workflows/ci.yml
```

Déclencheurs :

```text
push sur main
pull request vers main
```

Le CI exécute :

```text
checkout repository
setup Python 3.12
installation des dépendances
démarrage PostgreSQL
initialisation d’une base de test API
installation dbt
dbt debug
dbt deps
dbt parse
pytest
```

---

## 9. PostgreSQL de test dans GitHub Actions

Les tests FastAPI utilisent réellement PostgreSQL.

Le PostgreSQL créé par GitHub Actions étant vide, une fixture SQL a été ajoutée :

```text
tests/fixtures/init_api_test_db.sql
```

Elle crée un environnement analytics minimal :

```text
analytics.mart_audit_overview
analytics.mart_findings
analytics.mart_corrective_actions
analytics.mart_monitoring_runs
analytics.mart_action_monitoring_history
```

Chaque table reçoit quelques données de test.

L’objectif est de tester FastAPI de manière isolée sans avoir besoin de reconstruire toute la plateforme Data dans GitHub Actions.

---

## 10. Résultat des tests CI

Le pipeline CI lance l’ensemble des tests du projet.

Résultat final :

```text
103 tests exécutés
103 tests passés
```

Les tests couvrent notamment :

```text
Data Quality
ingestion
monitoring
escalade
notifications
historique
hash
Phase 5
FastAPI
```

Le workflow est maintenant vert à chaque push valide.

---

## 11. Intégration dbt dans le CI

dbt a été ajouté au workflow GitHub Actions.

Commandes utilisées :

```text
dbt debug
dbt deps
dbt parse
```

Ces étapes permettent de vérifier :

```text
connexion PostgreSQL
validité du profil
dépendances
syntaxe du projet
sources
modèles
macros
tests YAML
```

Le projet dbt est donc automatiquement validé dans le CI.

Un `dbt build` complet n’a pas été ajouté afin d’éviter de recréer l’ensemble des sources Data dans l’environnement CI.

---

## 12. Préparation au déploiement

La préparation du déploiement a inclus :

```text
.env.example
.gitignore
README local run
Dockerfiles
Docker Compose
CI GitHub Actions
tests
versioning API
```

Le projet peut être lancé localement avec :

```powershell
docker compose up -d
```

---

## 13. Azure — activation de la subscription

Une subscription :

```text
Azure for Students
```

a été activée.

Un resource group a été créé :

```text
rg-qip
```

Région utilisée pour le déploiement final :

```text
italynorth
```

Certaines régions initialement testées étaient limitées par les policies de la subscription étudiante.

---

## 14. Azure Database for PostgreSQL Flexible Server

Un serveur PostgreSQL managé a été créé :

```text
qip-postgres-yz
```

Endpoint :

```text
qip-postgres-yz.postgres.database.azure.com
```

Utilisateur admin :

```text
qipadmin
```

Version :

```text
PostgreSQL 16
```

Tier :

```text
Burstable
```

SKU :

```text
Standard_B1ms
```

Une base dédiée a été créée :

```text
quality_intelligence
```

---

## 15. Configuration réseau PostgreSQL Azure

Une règle firewall a été créée pour autoriser l’accès depuis le poste local.

La connexion a été validée avec :

```text
sslmode=require
```

Résultat :

```text
SSL connection
TLSv1.3
```

Cela confirme que la connexion entre le client local et Azure PostgreSQL est chiffrée.

---

## 16. Migration PostgreSQL local vers Azure

La base locale a été exportée avec :

```text
pg_dump
```

Format utilisé :

```text
custom format
```

Puis le dump a été restauré vers Azure avec :

```text
pg_restore
```

Les options suivantes ont été utilisées :

```text
--no-owner
--no-privileges
```

afin d’éviter les conflits entre :

```text
qip_user
```

en local et :

```text
qipadmin
```

sur Azure.

---

## 17. Validation des données migrées

La table :

```text
analytics.mart_audit_overview
```

a été vérifiée directement sur Azure.

Résultat :

```text
20 comptes
```

La migration PostgreSQL local → Azure est donc validée.

---

## 18. Azure Container Registry

Un registry Azure a été créé :

```text
qipregistryyz2026
```

Une image FastAPI a été construite localement puis poussée dans Azure Container Registry.

Image :

```text
qipregistryyz2026.azurecr.io/qip-api:v1
```

Repository :

```text
qip-api
```

Tag :

```text
v1
```

---

## 19. Limitation ACR Tasks

La commande :

```text
az acr build
```

n’a pas pu être utilisée avec la subscription Azure for Students.

Erreur :

```text
TasksOperationsNotAllowed
```

La solution utilisée a été :

```text
docker build local
→ docker tag
→ az acr login
→ docker push
```

Cette approche permet d’utiliser Azure Container Registry même lorsque ACR Tasks est restreint.

---

## 20. Azure Container Apps

Un environnement Azure Container Apps a été créé :

```text
qip-env
```

Providers utilisés :

```text
Microsoft.App
Microsoft.OperationalInsights
```

L’application :

```text
qip-api
```

a ensuite été créée dans Azure Container Apps à partir de l’image :

```text
qipregistryyz2026.azurecr.io/qip-api:v1
```

Ingress :

```text
external
```

Port cible :

```text
8000
```

---

## 21. Gestion des secrets dans Container Apps

Le mot de passe Azure PostgreSQL n’est pas exposé directement comme variable d’environnement.

Il est enregistré comme secret Container Apps :

```text
pg-password
```

Puis référencé via :

```text
POSTGRES_PASSWORD=secretref:pg-password
```

Les autres paramètres PostgreSQL sont injectés comme variables d’environnement :

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
```

---

## 22. Validation FastAPI sur Azure

La FastAPI déployée a été testée publiquement.

Endpoints validés :

```text
/health      ✅
/docs        ✅
/health/db   ✅
```

Cela confirme :

```text
Azure Container Apps
        ↓
FastAPI
        ↓
Azure PostgreSQL
        ↓
analytics marts
```

Le déploiement cloud fonctionne donc de bout en bout.

---

## 23. Sécurisation finale Azure

Après le push de l’image vers ACR, l’accès admin du registry a été désactivé.

Cela réduit l’exposition du registry après le déploiement.

---

## 24. Architecture finale de la Phase 10

Architecture locale :

```text
Docker Compose
│
├── PostgreSQL
├── Airflow
├── Streamlit
└── FastAPI
```

Architecture CI :

```text
GitHub
   ↓
GitHub Actions
   ↓
PostgreSQL de test
   ↓
dbt validation
   ↓
pytest
   ↓
103 tests passés
```

Architecture Azure :

```text
Azure Resource Group: rg-qip
│
├── Azure Database for PostgreSQL
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

---

## 25. Résultat final de la phase

Fonctionnalités livrées :

```text
✅ FastAPI dockerisée
✅ Docker Compose global
✅ PostgreSQL healthy
✅ Airflow opérationnel
✅ Streamlit opérationnel
✅ FastAPI opérationnelle
✅ .env centralisé
✅ .env.example
✅ secrets exclus de Git
✅ GitHub Actions CI
✅ PostgreSQL de test CI
✅ 103 tests passés
✅ dbt debug
✅ dbt deps
✅ dbt parse
✅ Azure for Students configuré
✅ resource group Azure
✅ PostgreSQL Flexible Server
✅ base quality_intelligence
✅ données migrées vers Azure
✅ connexion TLS validée
✅ Azure Container Registry
✅ image qip-api:v1
✅ Azure Container Apps
✅ FastAPI publique
✅ Swagger public
✅ FastAPI ↔ Azure PostgreSQL fonctionnel
✅ secrets PostgreSQL gérés côté Container Apps
```

---

## 26. Limites actuelles

Les éléments suivants ne sont pas inclus dans le périmètre final :

```text
déploiement Streamlit sur Azure
déploiement Airflow sur Azure
private networking complet
Azure Key Vault
autoscaling avancé
observabilité cloud complète
alerting Azure Monitor
CD automatique vers Container Apps
```

Ils peuvent être considérés comme des extensions futures.

---

## 27. Conclusion

La Phase 10 permet de passer d’un projet Data fonctionnel localement à une plateforme :

```text
dockerisée
testée automatiquement
versionnée
déployable
déployée partiellement sur Azure
```

La Quality Intelligence Platform dispose désormais :

```text
d’une architecture Data complète
d’une API
d’un dashboard
d’un moteur de monitoring
d’une CI
d’une base PostgreSQL managée
d’un registry d’images
d’un déploiement FastAPI cloud
```

La Phase 10 est considérée comme **terminée et validée**.
