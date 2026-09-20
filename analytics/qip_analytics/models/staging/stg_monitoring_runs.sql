select

    run_id,

    started_at,
    finished_at,

    status,

    actions_evaluated,
    events_detected,
    messages_prepared,

    emails_sent,
    emails_failed,

    error_message,

    created_at

from {{ source('monitoring', 'monitoring_run_log') }}