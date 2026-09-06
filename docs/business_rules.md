# Business Rules — Quality Intelligence Platform

## 1. Contexte

Le dataset actuel représente un snapshot intermédiaire d’une campagne d’audit encore en cours.

Les données vont continuer à être enrichies à mesure que de nouveaux comptes seront audités.

Par conséquent, les valeurs manquantes actuelles ne doivent pas être considérées automatiquement comme des anomalies définitives.

---

# 2. Statut d’audit du compte

## 2.1 Statut proposé

La plateforme calcule un statut proposé à partir du taux de complétude.

Règle provisoire :

- 0 % → `non_audite`
- > 0 % et < 65 % → `en_cours`
- > 65 % → `audite`

Le cas exactement égal à 65 % devra être clarifié si nécessaire.

Cette règle est une aide à la décision uniquement.

## 2.2 Statut validé

Le statut final reste sous la responsabilité de l’équipe Qualité.

L’équipe peut :

- confirmer le statut proposé ;
- le modifier ;
- renseigner elle-même le statut.

Le statut validé manuellement est la référence officielle.

La plateforme doit distinguer :

- `statut_propose`
- `statut_valide`
- `date_validation`
- `valide_par`

## 2.3 Comptes actuellement confirmés comme audités

À la date du snapshot actuel :

- RAM
- Min. Intérieur
- AtlanticRe
- Servier
- ONCF MW

Cette liste est amenée à évoluer au fur et à mesure de la campagne d’audit.

---

# 3. Taux de complétude

Le taux de complétude est différent du statut officiel d’audit.

Il mesure la proportion de contrôles applicables ayant été évalués.

Un compte peut donc être :

- officiellement audité ;
- mais avoir un taux de complétude inférieur à 100 %.

Le taux de complétude est un indicateur analytique, pas une source de vérité métier.

---

# 4. Périmètre des contrôles

Les valeurs actuellement observées pour `categorie_scope` sont :

- `Compte`
- `Entité`
- `Entité et Compte`

Pour le calcul exploratoire de la complétude d’un compte, les contrôles considérés comme applicables au compte sont :

- `Compte`
- `Entité et Compte`

La logique devra être confirmée et affinée avec l’équipe Qualité si nécessaire.

---

# 5. Score de maturité

Le champ canonique est :

`score_maturite`

Les valeurs actuellement observées sont :

- 1
- 2
- 3
- 4

Le référentiel métier prévoit une échelle pouvant aller jusqu’à 5.

Aucun score 5 n’est actuellement observé.

Les scores doivent être numériques.

Une valeur en dehors du domaine métier attendu devra être considérée comme une anomalie Data Quality.

---

# 6. Niveau de maturité

Le champ canonique est :

`niveau_maturite`

Les principaux niveaux observés sont :

- `Non en place/Elémentaire`
- `Partiellement en place/Réactif`
- `Largement en place/Stable`
- `Totalement en place/Proactif`

Des variantes de libellé existent actuellement, par exemple :

- `Partiellement`
- `Largement en place`
- `Totalement en place / Proactif`

Ces variantes devront être harmonisées dans une étape de standardisation métier.

La valeur :

`⏳ Non audité`

ne représente pas réellement un niveau de maturité et devra être traitée séparément lors de la standardisation métier.

---

# 7. Catégories de findings

Les catégories actuellement observées sont :

- `NC Mineure`
- `NC Majeure`
- `Observation`
- `Bonne Pratique`

`Bonne Pratique` ne doit pas être considérée comme une non-conformité négative dans les KPI de findings.

Les KPI devront distinguer les différents types de findings.

---

# 8. Actions correctives

Une action corrective peut contenir notamment :

- responsable ;
- date de début ;
- date de clôture ;
- statut ;
- âge ;
- indicateur d’âge ;
- commentaires ;
- preuves.

La présence d’une action corrective peut rendre certains champs obligatoires.

Exemple de future règle Data Quality :

Si `action_corrective` est renseignée, alors certains champs comme `responsable_action` et `statut_action` devront être contrôlés.

Les règles exactes seront définies dans la phase Data Quality.

---

# 9. Dates canoniques

Le schéma canonique contient uniquement :

- `date_debut`
- `date_cloture`

## Mapping vers date_debut

Les colonnes suivantes sont normalisées vers `date_debut` :

- `Date de début`
- `Date de réalisation prévisionnelle`
- `Date de réalisation previsionelle`

## Mapping vers date_cloture

Les colonnes suivantes sont normalisées vers `date_cloture` :

- `Date de clôture`
- `Délai prévu`
- `Délai Prévu`
- `Délai de clôture`

Les données de la raw layer restent inchangées.

---

# 10. Calcul de l’âge des actions

Le champ canonique est :

`age_jours`

Tant que l’action n’est pas clôturée :

`age_jours = date_du_jour - date_debut`

Lorsque le statut devient `Clôturé`, l’âge doit cesser d’évoluer.

La valeur doit donc être figée selon la logique d’historisation retenue lors de l’implémentation.

---

# 11. Indicateur d’âge

L’indicateur est calculé de manière déterministe à partir de `age_jours`.

Règle actuelle :

- 0–30 jours → `Normal`
- 31–60 jours → `Alerte`
- 61–90 jours → `Critique`
- > 90 jours → `Escalade management`

Actions associées :

- Normal → suivi normal
- Alerte → relance / escalade N+1
- Critique → suivi critique
- Escalade management → escalade management

Le LLM ne décide jamais du niveau de criticité.

---

# 12. Erreurs Excel

Les valeurs telles que :

`#REF!`

ne sont jamais considérées comme des valeurs métier valides.

Elles doivent être détectées par les futures règles de Data Quality.

Les indicateurs calculés dans Excel ne doivent pas devenir la source de vérité de la plateforme.

La plateforme doit recalculer elle-même les indicateurs critiques lorsque leur logique métier est connue.

---

# 13. Valeurs manquantes

Un NULL n’est pas automatiquement une anomalie.

La validité dépend du contexte métier.

Exemples :

- un compte non encore audité peut légitimement ne pas avoir de score ;
- une ligne sans action corrective peut légitimement ne pas avoir de statut d’action ;
- une action corrective renseignée mais sans responsable peut en revanche constituer une anomalie.

Les règles de complétude devront donc être conditionnelles.

---

# 14. Traçabilité

La plateforme doit préserver la provenance des données.

Au minimum :

- `source_file`
- `source_sheet`

Pour les validations métier :

- `statut_propose`
- `statut_valide`
- `date_validation`
- `valide_par`

Plus tard, l’architecture pourra également ajouter :

- `batch_id`
- `ingestion_timestamp`
- `campaign_id`

---

# 15. Gouvernance des règles

Les règles métier doivent être classées selon leur niveau de confiance :

## Règles validées

Règles confirmées par l’équipe métier ou explicitement retenues pour le projet.

## Règles provisoires

Règles utilisées comme aide à la décision mais susceptibles d’évoluer.

## Points à confirmer

Éléments dont la définition métier n’est pas encore suffisamment claire.

Une règle provisoire ne doit jamais être présentée comme une décision métier officielle.