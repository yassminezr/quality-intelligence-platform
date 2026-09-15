CREATE TABLE IF NOT EXISTS core.account (
    account_id BIGSERIAL PRIMARY KEY,

    account_name TEXT NOT NULL UNIQUE,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS core.campaign (
    campaign_id BIGSERIAL PRIMARY KEY,

    campaign_name VARCHAR(50) NOT NULL UNIQUE,

    start_date DATE,
    end_date DATE,

    status VARCHAR(30),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS core.audit (
    audit_id BIGSERIAL PRIMARY KEY,

    account_id BIGINT NOT NULL
        REFERENCES core.account(account_id),

    campaign_id BIGINT NOT NULL
        REFERENCES core.campaign(campaign_id),

    completion_rate NUMERIC(5,2),

    current_proposed_status VARCHAR(30),

    current_validated_status VARCHAR(30),

    status_last_updated_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (
        account_id,
        campaign_id
    )
);


CREATE TABLE IF NOT EXISTS core.iso_clause (
    clause_id BIGSERIAL PRIMARY KEY,

    clause_iso TEXT NOT NULL UNIQUE,

    intitule_iso TEXT
);


CREATE TABLE IF NOT EXISTS core.iso_control (
    control_id BIGSERIAL PRIMARY KEY,

    clause_id BIGINT NOT NULL
        REFERENCES core.iso_clause(clause_id),

    libelle_terrain TEXT NOT NULL,

    controle_attendu TEXT,

    categorie_scope TEXT,

    reference_edge TEXT,

    preuves_attendues TEXT,

    UNIQUE (
        clause_id,
        libelle_terrain
    )
);


CREATE TABLE IF NOT EXISTS core.evaluation (
    evaluation_id BIGSERIAL PRIMARY KEY,

    audit_id BIGINT NOT NULL
        REFERENCES core.audit(audit_id),

    control_id BIGINT NOT NULL
        REFERENCES core.iso_control(control_id),

    score_maturite SMALLINT
        CHECK (
            score_maturite BETWEEN 1 AND 5
        ),

    niveau_maturite TEXT,

    constat_auditeur TEXT,

    evidence TEXT,

    commentaires TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (
        audit_id,
        control_id
    )
);


CREATE TABLE IF NOT EXISTS core.finding (
    finding_id BIGSERIAL PRIMARY KEY,

    evaluation_id BIGINT NOT NULL UNIQUE
        REFERENCES core.evaluation(evaluation_id),

    categorie_finding VARCHAR(50) NOT NULL
        CHECK (
            categorie_finding IN (
                'NC Mineure',
                'NC Majeure',
                'Bonne Pratique',
                'OFI',
                'Observation',
                'NA'
            )
        ),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS core.corrective_action (
    action_id BIGSERIAL PRIMARY KEY,

    finding_id BIGINT NOT NULL UNIQUE
        REFERENCES core.finding(finding_id),

    action_text TEXT NOT NULL,

    responsable TEXT,

    date_debut DATE,

    date_cloture DATE,

    statut VARCHAR(30),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (
        date_cloture IS NULL
        OR date_debut IS NULL
        OR date_cloture >= date_debut
    )
);


CREATE TABLE IF NOT EXISTS core.audit_status_validation (
    validation_id BIGSERIAL PRIMARY KEY,

    audit_id BIGINT NOT NULL
        REFERENCES core.audit(audit_id),

    proposed_status VARCHAR(30),

    validated_status VARCHAR(30),

    validation_date TIMESTAMPTZ,

    validated_by TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS core.evaluation_history (
    history_id BIGSERIAL PRIMARY KEY,

    evaluation_id BIGINT NOT NULL
        REFERENCES core.evaluation(evaluation_id),

    batch_id UUID
        REFERENCES metadata.ingestion_batch(batch_id),

    score_maturite SMALLINT,

    niveau_maturite TEXT,

    constat_auditeur TEXT,

    valid_from TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS core.corrective_action_status_history (
    history_id BIGSERIAL PRIMARY KEY,

    action_id BIGINT NOT NULL
        REFERENCES core.corrective_action(action_id),

    status VARCHAR(30),

    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    changed_by TEXT
);