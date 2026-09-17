select
    account_id,
    account_name,
    is_active,
    created_at
from {{ source('core', 'account') }}