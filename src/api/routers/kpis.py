from fastapi import APIRouter

from src.api.database import fetch_one
from src.api.schemas import OverviewKPIResponse


router = APIRouter(
    prefix="/api/v1/kpis",
    tags=["KPIs"],
)
@router.get(
    "/overview",
    response_model=OverviewKPIResponse,
    summary="Get global quality KPIs",
    description=(
        "Returns the main quality indicators calculated "
        "from the analytics marts."
    ),
)

@router.get(
    "/overview",
    response_model=OverviewKPIResponse,
)
def get_overview_kpis():

    audit_kpis = fetch_one(
        """
        SELECT
            COUNT(*) AS audits_planned,

            COUNT(*) FILTER (
                WHERE official_audit_status = 'audite'
            ) AS audited,

            COUNT(*) FILTER (
                WHERE official_audit_status = 'en_cours'
            ) AS in_progress,

            COUNT(*) FILTER (
                WHERE official_audit_status = 'non_audite'
            ) AS not_started,

            ROUND(
                100.0
                * COUNT(*) FILTER (
                    WHERE official_audit_status = 'audite'
                )
                / NULLIF(COUNT(*), 0),
                2
            ) AS progress_pct,

            ROUND(
                AVG(avg_maturity_score)
                FILTER (
                    WHERE official_audit_status = 'audite'
                )::numeric,
                2
            ) AS avg_maturity_score

        FROM analytics.mart_audit_overview
        """
    )


    findings_kpis = fetch_one(
        """
        SELECT
            COUNT(*) FILTER (
                WHERE is_counted_in_total_findings = TRUE
            ) AS total_findings,

            COUNT(*) FILTER (
                WHERE categorie_finding = 'NC Majeure'
            ) AS major_nc

        FROM analytics.mart_findings
        """
    )


    actions_kpis = fetch_one(
        """
        SELECT
            COUNT(*) FILTER (
                WHERE is_open = TRUE
            ) AS open_actions,

            COUNT(*) FILTER (
                WHERE indicateur_age = 'Escalade management'
            ) AS escalations

        FROM analytics.mart_corrective_actions
        """
    )


    return {
        "audits_planned": audit_kpis["audits_planned"],
        "audited": audit_kpis["audited"],
        "in_progress": audit_kpis["in_progress"],
        "not_started": audit_kpis["not_started"],
        "progress_pct": float(audit_kpis["progress_pct"] or 0),
        "avg_maturity_score": (
            float(audit_kpis["avg_maturity_score"])
            if audit_kpis["avg_maturity_score"] is not None
            else None
        ),
        "total_findings": findings_kpis["total_findings"],
        "major_nc": findings_kpis["major_nc"],
        "open_actions": actions_kpis["open_actions"],
        "escalations": actions_kpis["escalations"],
    }