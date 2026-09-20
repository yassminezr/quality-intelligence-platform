CREATE SCHEMA IF NOT EXISTS monitoring;

CREATE TABLE IF NOT EXISTS monitoring.monitoring_run_log (
    run_id BIGSERIAL PRIMARY KEY,

    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,

    status VARCHAR(20) NOT NULL,

    actions_evaluated INTEGER NOT NULL DEFAULT 0,
    events_detected INTEGER NOT NULL DEFAULT 0,
    messages_prepared INTEGER NOT NULL DEFAULT 0,
    emails_sent INTEGER NOT NULL DEFAULT 0,
    emails_failed INTEGER NOT NULL DEFAULT 0,

    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);