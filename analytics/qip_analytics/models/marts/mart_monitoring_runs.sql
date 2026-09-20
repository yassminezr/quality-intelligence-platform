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

    case
        when finished_at is not null
            then extract(
                epoch from (finished_at - started_at)
            )
        else null
    end as duration_seconds,

    created_at

from {{ ref('stg_monitoring_runs') }}