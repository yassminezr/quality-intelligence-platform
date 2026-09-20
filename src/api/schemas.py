from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class DatabaseHealthResponse(BaseModel):
    status: str
    database: str
    user: str
    checked_at: datetime


class OverviewKPIResponse(BaseModel):
    audits_planned: int
    audited: int
    in_progress: int
    not_started: int
    progress_pct: float
    avg_maturity_score: float | None
    total_findings: int
    major_nc: int
    open_actions: int
    escalations: int

class AccountSummaryResponse(BaseModel):
    account_id: int
    account_name: str
    official_audit_status: str | None
    completion_rate: float | None
    avg_maturity_score: float | None
    account_badge: str | None


class AccountDetailResponse(BaseModel):
    account_id: int
    account_name: str
    official_audit_status: str | None
    completion_rate: float | None
    avg_maturity_score: float | None
    account_badge: str | None

class FindingResponse(BaseModel):
    finding_id: int
    account_name: str
    clause_iso: str | None
    libelle_terrain: str | None
    categorie_finding: str | None
    is_counted_in_total_findings: bool | None


class CorrectiveActionResponse(BaseModel):
    action_id: int
    account_name: str
    clause_iso: str | None
    action_text: str | None
    responsable: str | None
    statut: str | None
    age_jours: int | None
    indicateur_age: str | None
    is_open: bool | None
    is_closed: bool | None
    requires_attention: bool | None

class MonitoringRunResponse(BaseModel):
    run_id: int
    started_at: datetime
    finished_at: datetime | None
    status: str
    actions_evaluated: int
    events_detected: int
    messages_prepared: int
    emails_sent: int
    emails_failed: int
    duration_seconds: float | None


class MonitoringHistoryResponse(BaseModel):
    monitoring_log_id: int
    action_id: int
    age_jours: int | None
    niveau_escalade: str | None
    monitored_at: datetime