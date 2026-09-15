ALTER TABLE core.corrective_action_status_history
ADD COLUMN IF NOT EXISTS batch_id UUID
REFERENCES metadata.ingestion_batch(batch_id);


CREATE UNIQUE INDEX IF NOT EXISTS
idx_evaluation_history_evaluation_batch
ON core.evaluation_history (
    evaluation_id,
    batch_id
);


CREATE UNIQUE INDEX IF NOT EXISTS
idx_action_status_history_action_batch
ON core.corrective_action_status_history (
    action_id,
    batch_id
)
WHERE batch_id IS NOT NULL;


CREATE INDEX IF NOT EXISTS
idx_evaluation_history_batch
ON core.evaluation_history(batch_id);


CREATE INDEX IF NOT EXISTS
idx_action_status_history_batch
ON core.corrective_action_status_history(batch_id);