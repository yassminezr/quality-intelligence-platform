select
    audit_id,
    account_id,
    campaign_id,
    completion_rate,
    current_proposed_status,
    current_validated_status,
    status_last_updated_at,
    created_at,
    updated_at
from {{ source('core', 'audit') }}