select

    monitoring_log_id,

    action_id,

    age_jours,
    niveau_escalade,

    monitored_at,
    created_at

from {{ ref('stg_action_monitoring_history') }}