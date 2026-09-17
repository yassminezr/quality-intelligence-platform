select
    campaign_id,
    campaign_name,
    start_date,
    end_date,
    status,
    created_at
from {{ source('core', 'campaign') }}