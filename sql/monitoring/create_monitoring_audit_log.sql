CREATE SCHEMA IF NOT EXISTS monitoring;

CREATE TABLE IF NOT EXISTS monitoring.action_monitoring_log (
    monitoring_log_id BIGSERIAL PRIMARY KEY,

    action_id BIGINT NOT NULL,

    age_jours INTEGER,

    niveau_escalade VARCHAR(50),

    monitored_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
