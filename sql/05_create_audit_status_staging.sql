CREATE TABLE IF NOT EXISTS staging.audit_status_snapshot (
    status_snapshot_id BIGSERIAL PRIMARY KEY,

    batch_id UUID NOT NULL
        REFERENCES metadata.ingestion_batch(batch_id),

    source_file TEXT NOT NULL,

    account_name TEXT NOT NULL,

    source_status TEXT NOT NULL,

    validated_status VARCHAR(30) NOT NULL,

    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (batch_id, account_name)
);