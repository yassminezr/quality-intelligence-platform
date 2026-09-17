select

    account_id,
    account_name,

    campaign_id,
    campaign_name,

    niveau_maturite,

    score_maturite,

    count(*) as evaluation_count

from {{ ref('int_audit_evaluations') }}

where
    score_maturite is not null

group by

    account_id,
    account_name,

    campaign_id,
    campaign_name,

    niveau_maturite,
    score_maturite