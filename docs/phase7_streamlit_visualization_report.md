# Phase 7 — Visualisation & Application Streamlit

## 1. Objectif de la phase

La Phase 7 avait pour objectif de construire la couche de visualisation de la **Quality Intelligence Platform** à partir des données préparées dans PostgreSQL et des marts produits par dbt.

Le choix initial était Power BI. Après validation avec l’encadrant, la solution a été remplacée par **Streamlit**, afin de :

- accélérer le développement des dashboards ;
- centraliser les KPI dans une application unique ;
- faciliter l’accès aux données ;
- permettre une intégration plus naturelle avec le reste de la plateforme Python ;
- préparer l’exposition future des données via API et modules IA.

L’objectif n’était donc pas uniquement de produire des graphiques, mais de construire une véritable **application analytique interactive** connectée aux marts Analytics.

## 2. Architecture retenue

La couche de visualisation repose sur l’architecture suivante :

```text
Excel QHC
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
Streamlit
```

Streamlit ne lit pas directement le fichier Excel.

Les dashboards consomment uniquement les tables du schéma :

```text
analytics
```

Cela permet de séparer clairement :

- l’ingestion ;
- la qualité des données ;
- la modélisation métier ;
- la préparation analytique ;
- la visualisation.

## 3. Marts consommés

L’application Streamlit utilise principalement les marts suivants :

```text
analytics.mart_audit_overview
analytics.mart_account_clause_detail
analytics.mart_findings
analytics.mart_corrective_actions
analytics.mart_maturity_distribution
```

### `mart_audit_overview`

Granularité :

```text
1 ligne = 1 audit / compte / campagne
```

Utilisé pour :

- statut officiel de l’audit ;
- taux d’avancement ;
- score moyen de maturité ;
- badge de performance ;
- nombre de findings ;
- nombre d’actions.

### `mart_account_clause_detail`

Granularité :

```text
1 ligne = 1 contrôle ISO pour un compte
```

Le mart contient la grille complète :

```text
20 comptes × 37 contrôles ISO = 740 lignes
```

Il permet notamment de conserver les contrôles non encore évalués.

### `mart_findings`

Granularité :

```text
1 ligne = 1 finding
```

Utilisé pour les analyses des catégories :

- NC Majeure ;
- NC Mineure ;
- Observation ;
- OFI ;
- Bonne Pratique ;
- NA.

### `mart_corrective_actions`

Granularité :

```text
1 ligne = 1 action corrective
```

Utilisé pour :

- statut de l’action ;
- âge de l’action ;
- indicateur d’âge ;
- suivi des actions ouvertes ;
- escalades.

## 4. Structure de l’application

La structure finale est :

```text
streamlit_app/
│
├── app.py
│
├── data/
│   ├── __init__.py
│   ├── database.py
│   └── loaders.py
│
├── styles/
│   ├── __init__.py
│   └── theme.py
│
└── pages/
    ├── 1_Synthese_Executive.py
    ├── 2_Maturite_Performance.py
    ├── 3_Findings_Actions.py
    └── 4_Detail_Compte.py
```

Un fichier global de configuration Streamlit est également utilisé :

```text
.streamlit/config.toml
```

## 5. Connexion à PostgreSQL

Le module :

```text
streamlit_app/data/database.py
```

centralise la connexion PostgreSQL.

Les paramètres sont fournis par variables d’environnement :

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

L’application utilise `psycopg` et charge les résultats SQL dans des DataFrames Pandas.

## 6. Cache et rafraîchissement

Les loaders utilisent :

```python
@st.cache_data(ttl=300)
```

Le cache est donc conservé pendant 5 minutes.

Un bouton global a été ajouté dans la sidebar :

```text
Actualiser les données
```

Ce bouton exécute :

```python
st.cache_data.clear()
st.rerun()
```

Il permet donc à Streamlit de relire immédiatement les données mises à jour dans PostgreSQL.

Important : le bouton ne relance pas Airflow ni dbt. Il recharge uniquement les marts déjà produits par le pipeline.

# 7. Pages développées

## 7.1 Page d’accueil

Fichier :

```text
streamlit_app/app.py
```

Rôle :

- présenter la Quality Intelligence Platform ;
- afficher quelques KPI globaux ;
- introduire les différentes sections ;
- servir de point d’entrée vers les dashboards.

KPI affichés :

- nombre de comptes ;
- audits réalisés ;
- total findings ;
- actions ouvertes.

La page contient également des cartes présentant les quatre principales sections analytiques.

## 7.2 Synthèse Exécutive

Fichier :

```text
1_Synthese_Executive.py
```

Objectif : fournir une vue globale de la campagne d’audit.

### Filtres

- campagne ;
- compte ;
- statut d’audit.

### KPI

- audits planifiés ;
- audits réalisés ;
- audits en cours ;
- audits non démarrés ;
- pourcentage d’avancement ;
- score moyen de maturité ;
- total findings ;
- NC Majeures.

### Visualisations

- répartition des statuts d’audit ;
- nombre de findings par compte ;
- tableau global des comptes.

Le tableau contient notamment :

- compte ;
- statut ;
- avancement ;
- score ;
- badge ;
- findings ;
- escalades.

## 7.3 Maturité & Performance

Fichier :

```text
2_Maturite_Performance.py
```

Objectif : analyser la maturité ISO 9001 des comptes.

### KPI

- score moyen ;
- nombre de comptes par badge.

### Visualisations

- score moyen par compte ;
- distribution des niveaux de maturité ;
- matrice chapitre ISO × compte ;
- tableau comparatif des comptes.

### Matrice de maturité

La matrice couvre les chapitres :

```text
Ch4  — Contexte
Ch5  — Leadership
Ch6  — Planification
Ch7  — Support
Ch8  — Réalisation
Ch9  — Performance
Ch10 — Amélioration
```

Lorsque les données ne permettent pas encore de calculer un score, la valeur affichée est `WIP` (**Work In Progress**).

## 7.4 Findings & Actions Correctives

Fichier :

```text
3_Findings_Actions.py
```

Objectif : analyser les findings et suivre les actions correctives.

### KPI

- total findings ;
- NC Mineures ;
- NC Majeures ;
- Observations ;
- OFI ;
- Bonnes Pratiques ;
- actions ouvertes ;
- escalades.

### Visualisations

- findings par compte ;
- répartition par catégorie ;
- ancienneté des actions ;
- findings par clause ISO ;
- Top Findings ;
- actions prioritaires.

### Règle du total findings

Le KPI `Total Findings` exclut :

```text
Bonne Pratique
NA
```

Les OFI sont incluses.

### Règles d’ancienneté

```text
0–30 jours   → Normal
31–60 jours  → Alerte
61–90 jours  → Critique
>90 jours    → Escalade management
```

Les actions ne possédant pas de `date_debut` sont affichées comme `Non datée`. Aucun âge artificiel n’est calculé dans ce cas.

## 7.5 Détail Compte

Fichier :

```text
4_Detail_Compte.py
```

Objectif : fournir une vue détaillée d’un compte sélectionné.

### KPI

- statut officiel ;
- score de maturité ;
- badge ;
- taux d’avancement ;
- total findings ;
- NC Majeures ;
- NC Mineures ;
- Observations ;
- OFI ;
- Bonnes Pratiques ;
- actions ouvertes ;
- ancienneté moyenne.

### Analyses

- maturité par chapitre ;
- statut des actions ;
- détail des contrôles ISO.

Le tableau détaillé contient notamment :

- clause ISO ;
- libellé terrain ;
- contrôle attendu ;
- score ;
- niveau de maturité ;
- constat auditeur ;
- catégorie finding ;
- action corrective ;
- responsable ;
- statut de l’action ;
- âge ;
- indicateur d’âge.

# 8. Design et thème global

Une palette inspirée de DXC a été utilisée :

```text
Midnight Blue : #0E1020
Royal Blue    : #004AAC
Sky Blue      : #A1E6FF
Red           : #D94000
Gold          : #FFAE41
Canvas        : #F6F3F0
Peach         : #FFC082
Charcoal      : #2B2B2B
```

Le thème global est centralisé dans :

```text
streamlit_app/styles/theme.py
```

Ce module fournit notamment :

```text
apply_global_theme()
render_sidebar()
render_header()
kpi_card()
```

Le thème natif Streamlit est configuré dans :

```text
.streamlit/config.toml
```

# 9. Navigation

La navigation automatique Streamlit a été remplacée par une sidebar personnalisée.

Les pages disponibles sont :

```text
Accueil
Synthèse Exécutive
Maturité & Performance
Findings & Actions
Détail Compte
```

La sidebar contient également le nom de la plateforme, le contexte QHC ISO 9001, le bouton de rafraîchissement et la source de données.

# 10. Validation des KPI

Les KPI affichés dans Streamlit ont été vérifiés directement contre PostgreSQL/dbt.

| KPI | Valeur |
|---|---:|
| Audits planifiés | 20 |
| Audités | 5 |
| En cours | 4 |
| Non démarrés | 11 |
| Avancement global | 25 % |
| Score moyen des comptes audités | 3.24 / 5 |
| Total findings KPI | 51 |
| NC Majeures | 1 |
| NC Mineures | 44 |
| Observations | 6 |
| OFI | 0 |
| Bonnes Pratiques | 7 |
| Actions totales | 50 |
| Actions ouvertes | 50 |
| Actions clôturées | 0 |
| Escalades | 0 |
| Ancienneté moyenne connue | 64.05 jours |

### Validation du total findings

Le snapshot contient :

```text
58 findings
```

dont :

```text
7 Bonnes Pratiques
```

Le KPI métier est donc :

```text
58 - 7 = 51 findings comptés
```

# 11. Validation de l’ancienneté des actions

Les données disponibles donnent :

```text
1 action   → Alerte
20 actions → Critique
29 actions → âge non calculable
```

Pour les actions ayant une date exploitable :

```text
âge minimum : 49 jours
âge maximum : 67 jours
âge moyen   : 64.05 jours
```

Les 29 actions sans indicateur d’âge ne sont pas considérées comme une erreur. Elles ne possèdent simplement pas suffisamment d’information pour calculer `age_jours`.

# 12. Dockerisation de Streamlit

Streamlit a été intégré à Docker avec :

```text
Dockerfile.streamlit
```

Le service est ajouté à `docker-compose.yml`.

Architecture :

```text
Docker Compose
│
├── PostgreSQL
├── Airflow
├── Streamlit
└── dbt exécuté depuis Airflow
```

Dans Docker, Streamlit utilise :

```text
POSTGRES_HOST=postgres
```

et non `localhost`, car les conteneurs communiquent via le réseau Docker Compose.

L’application est exposée sur :

```text
http://localhost:8501
```

# 13. Test end-to-end

Un test réel de propagation a été effectué.

Un statut a été modifié dans la source Excel.

Le changement a ensuite été propagé via :

```text
Excel
→ Airflow
→ Staging
→ Core
→ dbt
→ Analytics Marts
→ Streamlit
```

Après actualisation, le nouveau statut a bien été affiché dans Streamlit.

Ce test valide le fonctionnement réel du flux complet.

# 14. Règles métier respectées

## Statut d’audit

Le statut officiel affiché provient du statut validé par l’équipe Qualité.

Le `statut_propose` reste une aide à la décision et n’est pas utilisé comme vérité officielle.

## Findings

Les catégories supportées sont :

```text
NC Mineure
NC Majeure
Bonne Pratique
OFI
Observation
NA
```

## Actions correctives

Une action corrective ne doit exister que lorsqu’un finding nécessite un traitement.

`NA` ne génère pas d’action corrective.

## Ancienneté

Tant qu’une action n’est pas clôturée :

```text
age_jours = date_du_jour - date_debut
```

Lorsqu’elle est clôturée, l’âge doit être figé.

# 15. Points volontairement non implémentés

## Priorité

La règle métier de priorité n’a pas encore été validée par l’équipe Qualité. Aucune règle artificielle n’a donc été ajoutée.

## Criticité

Même principe pour la criticité. Elle ne sera implémentée qu’après validation d’une règle métier officielle.

## Auditeur

L’information Auditeur n’est pas encore exposée de manière fiable dans les marts utilisés par Streamlit. Elle pourra être ajoutée ultérieurement si la source est suffisamment structurée.

# 16. Résultat de la phase

La Phase 7 fournit désormais une couche de visualisation fonctionnelle et intégrée à la plateforme.

```text
✅ Application Streamlit multi-pages
✅ Connexion PostgreSQL
✅ Consommation des marts dbt
✅ KPI métier
✅ Filtres interactifs
✅ Visualisations Plotly
✅ Tables détaillées
✅ Thème global
✅ Navigation personnalisée
✅ Cache et refresh
✅ Dockerisation
✅ Validation SQL des KPI
✅ Test de propagation Excel → Streamlit
```

La couche de visualisation n’est donc pas un dashboard isolé. Elle fait partie intégrante du pipeline Data de la Quality Intelligence Platform.

# 17. Architecture obtenue après la Phase 7

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
```

# 18. Prochaine étape

La prochaine phase pourra préparer l’industrialisation et l’exposition de la plateforme :

- API FastAPI ;
- couche de services ;
- endpoints métier ;
- intégration Docker Compose complète ;
- préparation au déploiement Cloud ;
- préparation des futurs modules Quality Copilot / AI.

La Phase 7 est considérée comme **terminée et validée**.
