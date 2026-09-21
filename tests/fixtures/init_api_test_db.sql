CREATE SCHEMA IF NOT EXISTS analytics;

-- =====================================================
-- AUDIT OVERVIEW
-- =====================================================

CREATE TABLE analytics.mart_audit_overview (
    account_id INTEGER PRIMARY KEY,
    account_name TEXT NOT NULL,
    official_audit_status TEXT,
    completion_rate NUMERIC(5, 2),
    avg_maturity_score NUMERIC(5, 2),
    account_badge TEXT
);

INSERT INTO analytics.mart_audit_overview (
    account_id,
    account_name,
    official_audit_status,
    completion_rate,
    avg_maturity_score,
    account_badge
)
VALUES
(
    1,
    'Test Account',
    'audite',
    100.00,
    3.50,
    'Performant'
);


-- =====================================================
-- FINDINGS
-- =====================================================

CREATE TABLE analytics.mart_findings (
    finding_id INTEGER PRIMARY KEY,
    account_name TEXT NOT NULL,
    clause_iso TEXT,
    libelle_terrain TEXT,
    categorie_finding TEXT,
    is_counted_in_total_findings BOOLEAN
);

INSERT INTO analytics.mart_findings (
    finding_id,
    account_name,
    clause_iso,
    libelle_terrain,
    categorie_finding,
    is_counted_in_total_findings
)
VALUES
(
    1,
    'Test Account',
    '4.1',
    'Test finding',
    'NC Mineure',
    TRUE
);


-- =====================================================
-- CORRECTIVE ACTIONS
-- =====================================================

CREATE TABLE analytics.mart_corrective_actions (
    action_id INTEGER PRIMARY KEY,
    account_name TEXT NOT NULL,
    clause_iso TEXT,
    action_text TEXT,
    responsable TEXT,
    statut TEXT,
    age_jours INTEGER,
    indicateur_age TEXT,
    is_open BOOLEAN,
    is_closed BOOLEAN,
    requires_attention BOOLEAN
);

INSERT INTO analytics.mart_corrective_actions (
    action_id,
    account_name,
    clause_iso,
    action_text,
    responsable,
    statut,
    age_jours,
    indicateur_age,
    is_open,
    is_closed,
    requires_attention
)
VALUES
(
    1,
    'Test Account',
    '4.1',
    'Test corrective action',
    'Test Owner',
    'Ouvert',
    65,
    'Critique',
    TRUE,
    FALSE,
    TRUE
);


-- =====================================================
-- MONITORING RUNS
-- =====================================================

CREATE TABLE analytics.mart_monitoring_runs (
    run_id INTEGER PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    actions_evaluated INTEGER NOT NULL,
    events_detected INTEGER NOT NULL,
    messages_prepared INTEGER NOT NULL,
    emails_sent INTEGER NOT NULL,
    emails_failed INTEGER NOT NULL,
    duration_seconds NUMERIC
);

INSERT INTO analytics.mart_monitoring_runs (
    run_id,
    started_at,
    finished_at,
    status,
    actions_evaluated,
    events_detected,
    messages_prepared,
    emails_sent,
    emails_failed,
    duration_seconds
)
VALUES
(
    1,
    NOW(),
    NOW(),
    'success',
    1,
    1,
    1,
    0,
    0,
    0.10
);


-- =====================================================
-- MONITORING HISTORY
-- =====================================================

CREATE TABLE analytics.mart_action_monitoring_history (
    monitoring_log_id INTEGER PRIMARY KEY,
    action_id INTEGER NOT NULL,
    age_jours INTEGER,
    niveau_escalade TEXT,
    monitored_at TIMESTAMPTZ NOT NULL
);

INSERT INTO analytics.mart_action_monitoring_history (
    monitoring_log_id,
    action_id,
    age_jours,
    niveau_escalade,
    monitored_at
)
VALUES
(
    1,
    1,
    65,
    'Critique',
    NOW()
);