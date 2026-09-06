# Canonical Audit Schema

## Purpose

The canonical schema defines the standardized representation
of QHC audit data after extraction from heterogeneous Excel sheets.

It does not represent the final analytical database model.

## Traceability

- source_file
- source_sheet

## ISO Audit Information

- clause_iso
- intitule_iso
- libelle_terrain
- controle_attendu
- categorie
- reference_edge
- preuves_attendues

## Auditor Assessment

- constat_auditeur
- categorie_finding
- niveau_maturite
- score_maturite

## Corrective Action

- action_corrective
- responsable_action
- date_debut
- date_cloture
- statut_action
- age_jours
- indicateur_age
- evidence
- commentaires

## Date Mapping Rules

The following source columns are standardized as `date_debut`:

- Date de début
- Date de réalisation prévisionnelle
- Date de réalisation previsionelle

The following source columns are standardized as `date_cloture`:

- Date de clôture
- Délai prévu
- Délai Prévu
- Délai de clôture

These mappings are business-approved conventions for this project.

Raw source data must remain unchanged.