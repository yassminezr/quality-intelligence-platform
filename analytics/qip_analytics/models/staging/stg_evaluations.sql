select
    evaluation_id,
    audit_id,
    control_id,
    score_maturite,
    niveau_maturite,
    constat_auditeur,
    evidence,
    commentaires,
    created_at,
    updated_at
from {{ source('core', 'evaluation') }}