select
    action_id,
    finding_id,
    action_text,
    responsable,
    date_debut,
    date_cloture,
    statut,
    created_at,
    updated_at
from {{ source('core', 'corrective_action') }}