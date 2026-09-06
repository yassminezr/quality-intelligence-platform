# Phase 1 Profiling Report
## Quality Intelligence Platform

## 1. Objectif de la phase

La Phase 1 avait pour objectif de comprendre précisément :

- la structure réelle du classeur Excel ;
- les différences entre feuilles ;
- les principales entités métier ;
- les valeurs observées ;
- les anomalies existantes ;
- les règles métier déjà connues ;
- les points restant à confirmer.

Cette phase constitue la base avant la modélisation des données et l'automatisation du pipeline.

---

# 2. Source analysée

La source actuelle est un classeur Excel de suivi des audits QHC / ISO 9001.

Le dataset actuel n'est pas final.

La campagne d'audit est toujours en cours et les données vont continuer à être renseignées progressivement par l'équipe Qualité.

Les taux de valeurs manquantes observés pendant cette phase représentent donc un snapshot intermédiaire et ne doivent pas être interprétés automatiquement comme des problèmes définitifs de qualité.

---

# 3. Structure du classeur

Le classeur contient actuellement :

- 30 feuilles au total ;
- 20 feuilles correspondant à des comptes ;
- des feuilles de documentation ;
- une feuille de règles de gestion ;
- plusieurs feuilles de reporting / consolidation dérivées.

Les feuilles telles que :

- `CONSOLIDATION`
- `DASHBOARD AUDITS`
- `ANALYSE FINDINGS`
- `PLAN ACTION GLOBAL`
- `GRAPHIQUES`

sont considérées comme des données dérivées et ne constituent pas les sources analytiques principales.

---

# 4. Feuilles d'audit

20 feuilles d'audit ont été détectées automatiquement à partir de leur structure, et non à partir d'une liste de noms codée en dur.

Cette stratégie permet à la plateforme de reconnaître automatiquement de nouveaux comptes si leur structure respecte le format attendu.

Chaque feuille contient actuellement :

- 45 lignes de checklist.

Total :

- 900 lignes standardisées.

---

# 5. Variantes de schéma

Le profiling structurel a identifié :

- 4 variantes de schéma ;
- 25 colonnes sources observées ;
- 18 colonnes communes à toutes les feuilles d'audit.

Ces différences proviennent notamment de variantes de nommage historiques.

Exemples :

- `Date de début`
- `Date de réalisation prévisionnelle`
- `Délai prévu`
- `Délai de clôture`

Ces variantes sont normalisées via un schéma canonique.

---

# 6. Schéma canonique

Les 25 colonnes sources observées sont entièrement couvertes par le mapping.

Résultat :

- 25 colonnes observées ;
- 25 colonnes mappées ;
- 0 colonne non mappée ;
- 21 colonnes canoniques.

Deux colonnes techniques supplémentaires sont ajoutées :

- `source_file`
- `source_sheet`

Le dataset standardisé contient donc :

- 23 colonnes.

---

# 7. Granularité

La granularité actuelle est :

Une ligne = un contrôle / une clause ISO pour un compte donné.

La présence d'une ligne ne signifie pas nécessairement que le contrôle a déjà été audité.

Un compte non encore audité possède quand même ses lignes de checklist.

---

# 8. Statut d'audit du compte

Le statut métier du compte est séparé du taux de complétude.

Deux notions sont distinguées :

- `statut_propose`
- `statut_valide`

Le statut proposé est calculé automatiquement par une règle déterministe.

Règle provisoire actuelle :

- 0 % → `non_audite`
- > 0 % et < 65 % → `en_cours`
- > 65 % → `audite`

Le statut validé est renseigné ou confirmé par l'équipe Qualité et constitue la référence métier officielle.

Comptes actuellement confirmés comme audités :

- RAM
- Min. Intérieur
- AtlanticRe
- Servier
- ONCF MW

La liste est évolutive.

---

# 9. Taux de complétude observés

Quelques exemples :

- AtlanticRe : 100 %
- RAM : 100 %
- ONCF MW : 100 %
- MEN : 96.55 %
- Servier : 79.41 %
- Min. Intérieur : 67.65 %
- CDG Capital : 35.71 %
- CDG Sécurité : 29.41 %

Plusieurs autres comptes sont actuellement à 0 %.

Le taux de complétude reste un indicateur analytique et ne remplace pas le statut validé par le métier.

---

# 10. Score de maturité

Sur 900 lignes :

- 199 scores sont renseignés ;
- 701 sont actuellement vides.

Valeurs observées :

- 1 : 4 occurrences
- 2 : 34 occurrences
- 3 : 95 occurrences
- 4 : 66 occurrences

Aucun score hors plage 1–5 n'a été détecté.

Aucun score 5 n'est actuellement observé.

---

# 11. Niveau de maturité

201 valeurs sont renseignées.

Valeurs principales :

- `Largement en place/Stable`
- `Totalement en place/Proactif`
- `Partiellement en place/Réactif`
- `Non en place/Elémentaire`

Des variantes existent :

- `Partiellement`
- `Largement en place`
- `Totalement en place / Proactif`

La valeur :

`⏳ Non audité`

a également été observée mais ne représente pas réellement un niveau de maturité.

Ces valeurs devront être harmonisées ultérieurement.

---

# 12. Findings

58 catégories de findings sont renseignées.

Distribution :

- NC Mineure : 44
- Bonne Pratique : 7
- Observation : 6
- NC Majeure : 1

La catégorie `Bonne Pratique` ne doit pas être comptabilisée comme une non-conformité négative.

---

# 13. Actions correctives

33 statuts d'action sont actuellement renseignés.

Valeurs observées :

- En cours : 21
- Ouvert : 12

D'autres statuts peuvent apparaître au fur et à mesure de la campagne, notamment `Clôturé`.

Les règles de complétude devront être contextuelles.

Par exemple :

Si aucune action corrective n'existe, un `statut_action` NULL peut être parfaitement normal.

---

# 14. Dates

## date_debut

- 22 valeurs renseignées ;
- 0 date invalide ;
- période observée : 13/07/2026 à 31/07/2026.

## date_cloture

- 1 valeur renseignée ;
- 0 date invalide ;
- valeur observée : 15/09/2026.

Les faibles taux de remplissage sont cohérents avec une campagne et des plans d'actions encore en cours.

---

# 15. Age des actions

26 valeurs d'âge sont actuellement renseignées.

Valeurs numériques observées :

- minimum : 33 jours ;
- maximum : 51 jours.

4 valeurs non numériques ont également été détectées.

La règle métier est :

Tant qu'une action n'est pas clôturée :

`age_jours = date_du_jour - date_debut`

Lorsque l'action devient clôturée, l'âge cesse d'évoluer.

---

# 16. Indicateur d'âge

Valeurs actuellement observées :

- 🟠 : 15
- 🔴 : 7
- `#REF!` : 4

Les valeurs `#REF!` sont des anomalies Excel et ne doivent jamais être considérées comme des valeurs métier valides.

La plateforme recalculera l'indicateur à partir de `age_jours`.

Règle retenue :

- 0–30 jours → Normal
- 31–60 jours → Alerte
- 61–90 jours → Critique
- > 90 jours → Escalade management

---

# 17. Scope des contrôles

Valeurs actuellement observées :

- Compte : 297
- Entité et Compte : 243
- Entité : 200
- valeurs manquantes : 160

Pour le profiling de complétude des comptes, les contrôles `Compte` et `Entité et Compte` ont été considérés comme applicables.

Cette logique peut être affinée ultérieurement avec l'équipe Qualité.

---

# 18. Principales anomalies identifiées

Les anomalies ou risques actuellement identifiés sont notamment :

- erreurs Excel `#REF!` ;
- variantes de libellé du niveau de maturité ;
- anciennes variantes de noms de colonnes ;
- valeurs de maturité non canoniques ;
- présence de `⏳ Non audité` dans un champ de maturité ;
- complétude conditionnelle des actions correctives ;
- dépendance actuelle à certaines formules Excel ;
- absence actuelle de validation systématique des domaines métier.

---

# 19. Principes Data Quality retenus

Les futures règles Data Quality devront :

- être contextualisées ;
- ne pas considérer tous les NULL comme des erreurs ;
- contrôler les domaines de valeurs ;
- détecter les nouvelles colonnes inconnues ;
- détecter les nouvelles variantes de schéma ;
- recalculer les indicateurs critiques lorsque possible ;
- conserver la raw layer intacte ;
- journaliser les anomalies.

---

# 20. Traçabilité

Les données standardisées contiennent actuellement :

- `source_file`
- `source_sheet`

La future plateforme devra également gérer :

- `batch_id`
- `ingestion_timestamp`
- `campaign_id`

Pour les validations métier :

- `statut_propose`
- `statut_valide`
- `date_validation`
- `valide_par`

---

# 21. Conclusions de la Phase 1

Le fichier Excel peut être utilisé comme source initiale du projet, mais il ne doit pas devenir directement le modèle analytique final.

Les principaux besoins techniques confirmés sont :

1. standardisation automatique des structures ;
2. ingestion incrémentale ;
3. conservation de l'historique ;
4. contrôles de Data Quality ;
5. séparation entre données sources et données dérivées ;
6. modélisation analytique dédiée ;
7. gouvernance explicite des règles métier ;
8. traçabilité des décisions et validations.

L'architecture générale du projet reste donc cohérente :

Excel / SharePoint
→ Python
→ Raw / Historical Data
→ Data Quality
→ PostgreSQL
→ dbt
→ Data Marts
→ Power BI

Les couches AI et Findings Intelligence pourront être ajoutées ultérieurement sur une base de données fiabilisée.