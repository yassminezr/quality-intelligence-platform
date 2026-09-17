select
    clause_id,
    clause_iso,
    intitule_iso
from {{ source('core', 'iso_clause') }}