select

    monitoring_log_id,

    action_id,

    age_jours,
    niveau_escalade,

    monitored_at,
    created_at

from {{ source('monitoring', 'action_monitoring_log') }}