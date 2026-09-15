CREATE TABLE IF NOT EXISTS metadata.ingestion_batch (
    batch_id UUID PRIMARY KEY,
    campaign VARCHAR(50) NOT NULL,
    source_file TEXT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    ingestion_timestamp TIMESTAMPTZ NOT NULL,
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_ingestion_batch_file_hash
ON metadata.ingestion_batch(file_hash);

CREATE INDEX IF NOT EXISTS idx_ingestion_batch_campaign
ON metadata.ingestion_batch(campaign);


CREATE TABLE IF NOT EXISTS staging.standardized_audits (
    staging_id BIGSERIAL PRIMARY KEY,

    batch_id UUID NOT NULL
        REFERENCES metadata.ingestion_batch(batch_id),

    source_file TEXT,
    source_sheet TEXT,
    source_row_number TEXT,

    clause_iso TEXT,
    intitule_iso TEXT,
    libelle_terrain TEXT,
    controle_attendu TEXT,

    categorie_scope TEXT,
    reference_edge TEXT,
    preuves_attendues TEXT,

    constat_auditeur TEXT,
    categorie_finding TEXT,

    niveau_maturite TEXT,
    score_maturite TEXT,

    action_corrective TEXT,
    responsable_action TEXT,

    date_debut TEXT,
    date_cloture TEXT,

    statut_action TEXT,
    age_jours TEXT,
    indicateur_age TEXT,

    evidence TEXT,
    commentaires TEXT,

    loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_staging_batch_id
ON staging.standardized_audits(batch_id);

CREATE INDEX IF NOT EXISTS idx_staging_source_sheet
ON staging.standardized_audits(source_sheet);

CREATE INDEX IF NOT EXISTS idx_staging_clause_iso
ON staging.standardized_audits(clause_iso);


CREATE TABLE IF NOT EXISTS quality.dq_issues (
    issue_id BIGSERIAL PRIMARY KEY,

    batch_id UUID NOT NULL
        REFERENCES metadata.ingestion_batch(batch_id),

    rule_id VARCHAR(100) NOT NULL,

    severity VARCHAR(20) NOT NULL
        CHECK (
            severity IN (
                'WARNING',
                'ERROR',
                'BLOCKING'
            )
        ),

    message TEXT,

    source_file TEXT,
    source_sheet TEXT,
    source_row_number TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_dq_issues_batch
ON quality.dq_issues(batch_id);

CREATE INDEX IF NOT EXISTS idx_dq_issues_rule
ON quality.dq_issues(rule_id);

CREATE INDEX IF NOT EXISTS idx_dq_issues_severity
ON quality.dq_issues(severity);