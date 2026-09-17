select
    finding_id,
    evaluation_id,
    categorie_finding,
    created_at
from {{ source('core', 'finding') }}