# Phase 8 — Corrective Action Monitoring & Escalation Agent

## 1. Objectif de la phase

La Phase 8 avait pour objectif de construire un **moteur de surveillance automatique des actions correctives** au sein de la **Quality Intelligence Platform**.

L’objectif principal était de dépasser le simple affichage des actions dans Streamlit pour mettre en place un véritable mécanisme de monitoring capable de :

- recalculer l’ancienneté des actions ouvertes ;
- classifier automatiquement leur niveau de surveillance ;
- détecter les changements de niveau ;
- historiser les décisions ;
- préparer des messages d’alerte ;
- envoyer éventuellement des notifications email ;
- intégrer une couche LLM optionnelle limitée à la reformulation ;
- orchestrer automatiquement le traitement avec Airflow ;
- exposer les résultats dans PostgreSQL, dbt et Streamlit ;
- assurer la traçabilité, l’idempotence et les tests.

Le système reste **déterministe pour toutes les règles métier**.  
Le LLM ne décide jamais du niveau de criticité ou de l’escalade.

---

## 2. Architecture retenue

L’architecture finale de la Phase 8 est :

```text
analytics.mart_corrective_actions
        ↓
CorrectiveActionRepository
        ↓
Monitoring Rules
        ↓
CorrectiveActionMonitoringService
        ↓
Change Detection
        ↓
Monitoring Audit Log
        ↓
Alert Preparation
        ↓
Optional LLM Rewriting
        ↓
Email Notification
        ↓
Monitoring Run History
        ↓
dbt Monitoring Marts
        ↓
Streamlit Monitoring Dashboard
```

Le moteur de monitoring s’intègre donc directement dans l’architecture générale de la plateforme :

```text
Excel / Source QHC
        ↓
Python Ingestion
        ↓
Airflow
        ↓
Staging / Data Quality
        ↓
PostgreSQL Core
        ↓
dbt
        ↓
Analytics Marts
        ↓
Monitoring Agent
        ↓
Monitoring Logs / Notifications
        ↓
dbt Monitoring Marts
        ↓
Streamlit
```

---

## 3. Règles métier de monitoring

Les seuils d’ancienneté validés sont :

| Âge de l’action | Niveau |
|---|---|
| 0 à 30 jours | Normal |
| 31 à 60 jours | Alerte |
| 61 à 90 jours | Critique |
| > 90 jours | Escalade management |

Pour une action ouverte :

```text
age_jours = date_du_jour - date_debut
```

Lorsqu’une action est clôturée, son âge reste figé.

Si `date_debut` est absente, aucun âge n’est inventé.

Le moteur doit donc être capable de retourner :

```text
age_jours = NULL
niveau_escalade = NULL
```

si les informations disponibles ne permettent pas un calcul fiable.

---

## 4. Modèle Python

Le module principal est organisé dans :

```text
src/monitoring/
```

Structure principale :

```text
src/monitoring/
│
├── models.py
├── rules.py
├── repository.py
├── service.py
├── audit.py
├── run_audit.py
├── run_monitoring.py
│
└── notifications/
    ├── formatter.py
    ├── service.py
    ├── llm_writer.py
    ├── writing_service.py
    ├── email_sender.py
    ├── recipient_resolver.py
    ├── notification_service.py
    └── notification_config.py
```

Cette séparation permet de garder les responsabilités indépendantes.

---

## 5. Modèles de données du monitoring

Le fichier :

```text
src/monitoring/models.py
```

définit notamment :

### `EscalationLevel`

Les valeurs possibles sont :

```text
normal
alerte
critique
escalade_management
```

### `ActionMonitoringInput`

Représente les données nécessaires au monitoring d’une action corrective.

Les informations principales sont :

- `action_id`
- `date_debut`
- `is_closed`
- `frozen_age_days`
- `account_name`
- `action_text`
- `responsable`
- `statut`

### `ActionMonitoringResult`

Contient le résultat déterministe du moteur :

- `action_id`
- `age_jours`
- `niveau_escalade`
- `date_evaluation`

### `MonitoringEvent`

Représente un changement détecté :

```text
previous_level
→
current_level
```

---

## 6. Moteur de règles déterministes

Le fichier :

```text
src/monitoring/rules.py
```

contient deux fonctions principales.

### Calcul de l’âge

```text
calculate_action_age()
```

Règles appliquées :

- `date_debut = NULL` → âge non calculable ;
- `is_closed = NULL` → âge non calculable ;
- action clôturée → âge figé existant ;
- action ouverte → différence entre la date du jour et `date_debut` ;
- âge négatif → valeur non retenue.

### Classification du niveau

```text
classify_escalation_level()
```

La fonction applique exclusivement les seuils métier validés.

Le LLM n’intervient jamais dans cette classification.

---

## 7. Repository PostgreSQL

Le fichier :

```text
src/monitoring/repository.py
```

contient :

```text
CorrectiveActionRepository
```

Son rôle est uniquement de lire les données depuis :

```text
analytics.mart_corrective_actions
```

Les principales colonnes utilisées sont :

```text
action_id
date_debut
is_closed
age_jours
account_name
action_text
responsable
statut
```

Le repository ne contient aucune règle métier.

---

## 8. Service de monitoring

Le fichier :

```text
src/monitoring/service.py
```

contient :

```text
CorrectiveActionMonitoringService
```

Le service orchestre :

```text
Repository
   ↓
Rules
   ↓
Result
   ↓
Previous level
   ↓
Change detection
   ↓
Audit log
   ↓
MonitoringEvent
```

Un événement n’est créé que lorsque :

```text
previous_level != current_level
```

Cela permet d’éviter de créer la même alerte à chaque exécution quotidienne.

---

## 9. Historisation des décisions

Une table technique PostgreSQL a été créée :

```text
monitoring.action_monitoring_log
```

Elle conserve les changements de niveau détectés.

Colonnes principales :

```text
monitoring_log_id
action_id
age_jours
niveau_escalade
monitored_at
created_at
```

Cette table permet de retrouver le dernier niveau enregistré d’une action.

Exemple :

```text
Action 15
Alerte
→
Critique
```

Le changement est historisé une seule fois.

---

## 10. Idempotence et détection de changement

L’un des objectifs importants de la Phase 8 était d’éviter les doublons.

Principe :

```text
niveau actuel
=
dernier niveau historisé
```

Alors :

```text
aucun nouvel événement
aucune nouvelle alerte
aucun nouveau log métier
```

Un test réel a été effectué.

Lors de la première exécution du moteur :

```text
50 actions évaluées
21 événements détectés
```

Lors d’une seconde exécution sans changement métier :

```text
50 actions évaluées
0 événement
```

Le nombre de logs est donc resté stable.

---

## 11. Génération déterministe des messages

Le fichier :

```text
src/monitoring/notifications/formatter.py
```

construit un objet :

```text
AlertMessage
```

avec :

```text
subject
body
```

Le message est généré à partir des données déjà calculées par le moteur.

Aucune décision métier n’est prise à ce niveau.

Les valeurs manquantes sont affichées explicitement, par exemple :

```text
Non renseigné
Non calculable
Non déterminé
```

---

## 12. Service de préparation des alertes

Le fichier :

```text
src/monitoring/notifications/service.py
```

contient :

```text
AlertPreparationService
```

Le service transforme uniquement les `MonitoringEvent` en messages.

Conséquence :

```text
0 événement
→
0 message
```

Cela évite d’envoyer des notifications quotidiennes inutiles lorsque rien n’a changé.

---

## 13. Couche LLM optionnelle

Une couche LLM a été ajoutée dans :

```text
src/monitoring/notifications/llm_writer.py
```

Architecture :

```text
LLMWriter
├── DeterministicFallbackWriter
└── OpenAIAlertWriter
```

Le LLM peut uniquement :

- reformuler le message ;
- améliorer sa lisibilité ;
- produire un texte professionnel et concis.

Le LLM ne peut pas :

- calculer `age_jours` ;
- décider qu’une action est critique ;
- changer le niveau d’escalade ;
- modifier les noms, statuts ou valeurs ;
- inventer des informations.

En cas d’erreur du LLM :

```text
message déterministe
→
conservé automatiquement
```

La couche IA n’est donc jamais bloquante pour le monitoring.

---

## 14. Test de l’intégration OpenAI

Un script de test a été créé :

```text
scripts/test_openai_alert_writer.py
```

La connexion au SDK OpenAI et la lecture de la clé API ont été validées.

Lors du test réel, l’API a répondu avec une erreur de quota :

```text
429
credit_balance_exhausted
```

La génération LLM réelle n’a donc pas été finalisée faute de crédits disponibles.

Cependant, l’architecture, la configuration, le fallback déterministe et les tests sont en place.

---

## 15. Notifications email

L’envoi SMTP est géré dans :

```text
src/monitoring/notifications/email_sender.py
```

Composant principal :

```text
SMTPEmailSender
```

La configuration repose sur les variables :

```text
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_SENDER_EMAIL
SMTP_USE_TLS
```

Un test réel d’envoi email a été effectué avec succès.

---

## 16. Résolution des destinataires

Le fichier :

```text
src/monitoring/notifications/recipient_resolver.py
```

contient :

```text
RecipientResolver
```

Il associe un niveau d’escalade à une liste de destinataires configurés.

Les variables prévues sont :

```text
QIP_RECIPIENT_ALERT
QIP_RECIPIENT_CRITICAL
QIP_RECIPIENT_MANAGEMENT
```

Aucune adresse n’est inventée par le moteur ou par le LLM.

Les règles définitives de routage pourront évoluer lorsque l’organisation métier des destinataires sera formellement validée.

---

## 17. Service de notification

Le fichier :

```text
src/monitoring/notifications/notification_service.py
```

gère l’envoi des messages.

Pour chaque événement :

```text
niveau
→
résolution du destinataire
→
email
→
résultat de livraison
```

Le résultat contient notamment :

```text
action_id
recipient
success
error
```

Cela permet de distinguer :

```text
email envoyé
```

et :

```text
échec d’envoi
```

---

## 18. Exécution complète du moteur

Le point d’entrée principal est :

```text
src/monitoring/run_monitoring.py
```

Il orchestre :

```text
Connexion PostgreSQL
        ↓
Repository
        ↓
Monitoring Service
        ↓
Events
        ↓
Alert Preparation
        ↓
LLM optionnel
        ↓
Email optionnel
        ↓
Run Audit
```

Un run réel a retourné :

```text
Monitoring terminé :
50 action(s) évaluée(s),
0 événement(s),
0 message(s),
0 email(s) envoyé(s),
0 échec(s).
```

Ce résultat est normal lorsqu’aucun niveau n’a changé depuis l’exécution précédente.

---

## 19. Orchestration Airflow

Un DAG dédié a été créé :

```text
corrective_action_monitoring
```

Fichier :

```text
airflow/dags/corrective_action_monitoring_dag.py
```

Tâche :

```text
run_corrective_action_monitoring
```

Le DAG exécute :

```text
src.monitoring.run_monitoring.run_monitoring
```

La planification retenue est quotidienne :

```text
@daily
```

Une exécution réelle depuis l’interface Airflow a été validée avec le statut :

```text
success
```

---

## 20. Historisation des exécutions

Une seconde table a été ajoutée :

```text
monitoring.monitoring_run_log
```

Granularité :

```text
1 ligne = 1 exécution du moteur de monitoring
```

Colonnes principales :

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
error_message
created_at
```

Cela permet de distinguer :

```text
historique des exécutions
```

et :

```text
historique des décisions métier
```

---

## 21. Run logger Python

Le fichier :

```text
src/monitoring/run_audit.py
```

contient :

```text
MonitoringRunLogger
```

Méthodes principales :

```text
start_run()
finish_success()
finish_failed()
```

Cycle normal :

```text
running
→
success
```

En cas d’exception :

```text
running
→
failed
```

avec conservation de :

```text
error_message
```

---

## 22. Validation réelle de l’historisation

Des exécutions réelles ont été enregistrées.

Exemple :

| run_id | status | actions_evaluated | events_detected | emails_sent | emails_failed |
|---:|---|---:|---:|---:|---:|
| 1 | success | 50 | 0 | 0 | 0 |
| 2 | success | 50 | 0 | 0 | 0 |

L’historisation fonctionne donc aussi bien pour les exécutions manuelles que pour Airflow.

---

## 23. Intégration dbt

Les tables techniques du schéma `monitoring` ont été déclarées comme sources dbt.

Fichier :

```text
analytics/qip_analytics/models/staging/monitoring_sources.yml
```

Sources :

```text
monitoring.monitoring_run_log
monitoring.action_monitoring_log
```

Deux modèles staging ont été créés :

```text
stg_monitoring_runs
stg_action_monitoring_history
```

Ils sont matérialisés en vues.

---

## 24. Marts monitoring

Deux nouveaux marts ont été ajoutés :

```text
analytics.mart_monitoring_runs
analytics.mart_action_monitoring_history
```

### `mart_monitoring_runs`

Granularité :

```text
1 ligne = 1 exécution du moteur de monitoring
```

Il expose notamment :

- statut du run ;
- dates de début et de fin ;
- nombre d’actions évaluées ;
- événements détectés ;
- messages préparés ;
- emails envoyés ;
- emails en échec ;
- durée d’exécution.

### `mart_action_monitoring_history`

Granularité :

```text
1 ligne = 1 changement de niveau pour une action
```

Il expose notamment :

- action ;
- âge ;
- niveau d’escalade ;
- date du changement.

---

## 25. Tests dbt

Les deux marts disposent de tests dbt.

Résultat final :

```text
PASS=15
WARN=0
ERROR=0
SKIP=0
```

Les tests vérifient notamment :

- unicité des identifiants ;
- non-nullité des champs essentiels ;
- valeurs acceptées pour les statuts ;
- valeurs acceptées pour les niveaux d’escalade.

---

## 26. Page Streamlit Monitoring

Une page dédiée a été ajoutée :

```text
streamlit_app/pages/5_Monitoring.py
```

Elle consomme :

```text
analytics.mart_monitoring_runs
analytics.mart_action_monitoring_history
```

La page affiche :

- dernier statut du moteur ;
- nombre d’actions évaluées ;
- nombre d’événements détectés ;
- nombre d’emails envoyés ;
- nombre d’échecs email ;
- historique des exécutions ;
- historique des changements de niveau.

La page a été validée visuellement dans Streamlit.

---

## 27. Tests Python

Les tests couvrent plusieurs couches :

```text
rules
repository
audit
service
notifications
LLM writer
email sender
recipient resolver
notification service
run audit
integration
```

Les cas limites testés comprennent notamment :

- absence de `date_debut` ;
- âge figé pour une action clôturée ;
- transition Alerte → Critique ;
- stabilité lorsqu’un niveau ne change pas ;
- seuils exacts 30 / 31 / 60 / 61 / 90 / 91 jours ;
- fallback LLM ;
- notifications ;
- historisation.

Résultat final :

```text
46 passed
42 deselected
```

---

## 28. Docker hardening

Le fichier :

```text
docker-compose.yml
```

a été renforcé.

PostgreSQL possède un healthcheck :

```text
pg_isready
```

Les services suivants attendent désormais que PostgreSQL soit réellement healthy :

```text
airflow-init
airflow-webserver
airflow-scheduler
streamlit
```

Les services principaux utilisent également :

```text
restart: unless-stopped
```

---

## 29. Ordre de démarrage

L’ordre attendu est maintenant :

```text
PostgreSQL
   ↓
healthy
   ↓
Airflow Init
   ↓
Airflow Webserver / Scheduler

PostgreSQL healthy
   ↓
Streamlit
```

Cela évite le problème rencontré auparavant lorsque le DAG essayait d’accéder à :

```text
postgres
```

alors que PostgreSQL n’était pas encore disponible.

---

## 30. Correction du PID Airflow

Après redémarrage, l’interface Airflow a rencontré le problème :

```text
airflow-webserver.pid is stale
```

Le webserver Gunicorn refusait alors de redémarrer correctement.

La configuration a été renforcée pour supprimer le PID obsolète avant le démarrage du webserver.

Principe :

```text
rm -f /opt/airflow/airflow-webserver.pid
→
airflow webserver
```

Après correction, l’interface :

```text
http://localhost:8080
```

est redevenue accessible.

Une nouvelle exécution du DAG de monitoring a ensuite été lancée avec succès.

---

## 31. Services Docker validés

Après durcissement de la configuration :

```text
qip-postgres
→ healthy

qip-airflow-webserver
→ Up

qip-airflow-scheduler
→ Up

qip_streamlit
→ Up
```

Ports principaux :

```text
PostgreSQL : 5432
Airflow    : 8080
Streamlit  : 8501
```

---

## 32. Variables d’environnement

Le moteur utilise des variables d’environnement pour les paramètres techniques.

### PostgreSQL

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

### LLM

```text
OPENAI_API_KEY
OPENAI_MODEL
LLM_ENABLED
```

### Email

```text
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_SENDER_EMAIL
SMTP_USE_TLS
EMAIL_NOTIFICATIONS_ENABLED
```

### Destinataires

```text
QIP_RECIPIENT_ALERT
QIP_RECIPIENT_CRITICAL
QIP_RECIPIENT_MANAGEMENT
```

Les secrets ne doivent pas être codés directement dans les fichiers Python.

---

## 33. Validation end-to-end

La chaîne complète validée est :

```text
analytics.mart_corrective_actions
        ↓
Monitoring Python
        ↓
Règles déterministes
        ↓
Détection de changement
        ↓
Audit PostgreSQL
        ↓
Préparation des messages
        ↓
Notification optionnelle
        ↓
Historisation du run
        ↓
Airflow
        ↓
dbt
        ↓
Monitoring Marts
        ↓
Streamlit
```

Une exécution réelle depuis Airflow a été validée avec succès.

La page Streamlit Monitoring restitue les données produites par le moteur.

---

## 34. Principes d’architecture respectés

La Phase 8 respecte plusieurs principes importants.

### Déterminisme

Toutes les décisions métier sont produites par du code Python explicite.

### Séparation des responsabilités

```text
repository
≠
rules
≠
service
≠
audit
≠
notification
```

### Traçabilité

Les décisions et les exécutions sont historisées.

### Idempotence

Un même niveau ne produit pas un nouvel événement à chaque exécution.

### Tolérance aux erreurs

Le LLM est optionnel et dispose d’un fallback déterministe.

### Testabilité

La date d’évaluation est injectée dans les règles afin de rendre les tests reproductibles.

---

## 35. Points volontairement non imposés

### Destinataires métier définitifs

La règle organisationnelle finale indiquant précisément qui doit recevoir chaque type d’alerte n’a pas été inventée.

La configuration actuelle permet de tester techniquement le routage.

### LLM

Le LLM n’est pas utilisé comme moteur de décision.

### Données manquantes

Une donnée manquante n’est pas automatiquement considérée comme une erreur, car la campagne d’audit peut être encore en cours.

---

## 36. Résultat de la Phase 8

La Phase 8 fournit désormais :

```text
✅ Moteur déterministe de calcul d’âge

✅ Classification Normal / Alerte / Critique / Escalade management

✅ Repository PostgreSQL

✅ Service de monitoring

✅ Détection des changements

✅ Idempotence

✅ Historisation des décisions

✅ Historisation des exécutions

✅ Génération déterministe des alertes

✅ Couche LLM optionnelle

✅ Fallback sans LLM

✅ Notifications email SMTP

✅ Airflow DAG

✅ Staging dbt monitoring

✅ Marts dbt monitoring

✅ Tests dbt

✅ Page Streamlit Monitoring

✅ Tests Python et cas limites

✅ Docker healthchecks

✅ Ordre de démarrage sécurisé

✅ Validation end-to-end
```

Le monitoring n’est donc pas un simple script séparé.

Il constitue désormais un **module intégré de la Quality Intelligence Platform**, connecté à la couche Analytics, orchestré par Airflow, historisé dans PostgreSQL et exposé dans Streamlit.

---

## 37. Architecture obtenue après la Phase 8

```text
Excel / SharePoint
        ↓
Python Ingestion
        ↓
Airflow
        ↓
Raw / Staging
        ↓
Data Quality
        ↓
PostgreSQL Core
        ↓
dbt
        ↓
Analytics Marts
        ↓
Streamlit
        ↓
Utilisateurs Qualité

        +

Analytics Corrective Actions
        ↓
Monitoring Agent
        ↓
Rules Engine
        ↓
Change Detection
        ↓
Audit / Run History
        ↓
Alerts / Email
        ↓
dbt Monitoring Marts
        ↓
Streamlit Monitoring
```

La Phase 8 est considérée comme **terminée et validée**.
