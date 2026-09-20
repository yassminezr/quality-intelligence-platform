from fastapi import APIRouter, HTTPException, Query

from src.api.database import fetch_all
from src.api.schemas import (
    MonitoringHistoryResponse,
    MonitoringRunResponse,
)


router = APIRouter(
    prefix="/api/v1/monitoring",
    tags=["Monitoring"],
)


ALLOWED_LEVELS = {
    "Normal",
    "Alerte",
    "Critique",
    "Escalade management",
}


# =====================================================
# MONITORING RUNS
# =====================================================

@router.get(
    "/runs",
    response_model=list[MonitoringRunResponse],
    summary="List monitoring runs",
)
def get_monitoring_runs(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Nombre maximum de runs retournés",
    ),
):

    return fetch_all(
        """
        SELECT
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
        FROM analytics.mart_monitoring_runs
        ORDER BY started_at DESC
        LIMIT %s
        """,
        (limit,),
    )


# =====================================================
# MONITORING HISTORY
# =====================================================

@router.get(
    "/history",
    response_model=list[MonitoringHistoryResponse],
    summary="List monitoring history",
)
def get_monitoring_history(
    action_id: int | None = Query(
        default=None,
        description="Filtrer sur une action",
    ),
    level: str | None = Query(
        default=None,
        description="Filtrer sur un niveau d'escalade",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Nombre maximum d'événements retournés",
    ),
):

    if level is not None and level not in ALLOWED_LEVELS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid monitoring level. "
                f"Allowed values: {sorted(ALLOWED_LEVELS)}"
            ),
        )

    conditions = []
    params = []

    if action_id is not None:
        conditions.append(
            "action_id = %s"
        )
        params.append(action_id)

    if level:
        conditions.append(
            "niveau_escalade = %s"
        )
        params.append(level)

    where_clause = ""

    if conditions:
        where_clause = (
            "WHERE "
            + " AND ".join(conditions)
        )

    params.append(limit)

    query = f"""
        SELECT
            monitoring_log_id,
            action_id,
            age_jours,
            niveau_escalade,
            monitored_at
        FROM analytics.mart_action_monitoring_history
        {where_clause}
        ORDER BY monitored_at DESC
        LIMIT %s
    """

    return fetch_all(
        query,
        tuple(params),
    )