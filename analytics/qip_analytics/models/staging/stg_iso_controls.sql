select
    control_id,
    clause_id,
    libelle_terrain,
    controle_attendu,
    categorie_scope,
    reference_edge,
    preuves_attendues
from {{ source('core', 'iso_control') }}