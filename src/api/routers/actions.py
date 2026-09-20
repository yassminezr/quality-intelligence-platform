from fastapi import APIRouter, HTTPException, Query

from src.api.database import fetch_all
from src.api.schemas import CorrectiveActionResponse


router = APIRouter(
    prefix="/api/v1/actions",
    tags=["Corrective Actions"],
)


ALLOWED_AGE_LEVELS = {
    "Normal",
    "Alerte",
    "Critique",
    "Escalade management",
}


@router.get(
    "",
    response_model=list[CorrectiveActionResponse],
)

@router.get(
    "",
    response_model=list[CorrectiveActionResponse],
    summary="List corrective actions",
)
@router.get(
    "/critical",
    response_model=list[CorrectiveActionResponse],
    summary="List critical corrective actions",
)
def get_actions(
    account_name: str | None = Query(
        default=None,
        description="Filtrer par compte",
    ),
    is_open: bool | None = Query(
        default=None,
        description="Filtrer sur les actions ouvertes",
    ),
    age_level: str | None = Query(
        default=None,
        description="Filtrer par niveau d'ancienneté",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Nombre maximum d'actions retournées",
    ),
):

    if (
        age_level is not None
        and age_level not in ALLOWED_AGE_LEVELS
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid age level. "
                f"Allowed values: {sorted(ALLOWED_AGE_LEVELS)}"
            ),
        )

    conditions = []
    params = []

    if account_name:
        conditions.append("account_name = %s")
        params.append(account_name)

    if is_open is not None:
        conditions.append("is_open = %s")
        params.append(is_open)

    if age_level:
        conditions.append("indicateur_age = %s")
        params.append(age_level)

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    params.append(limit)

    query = f"""
        SELECT
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
        FROM analytics.mart_corrective_actions
        {where_clause}
        ORDER BY age_jours DESC NULLS LAST
        LIMIT %s
    """

    return fetch_all(
        query,
        tuple(params),
    )


@router.get(
    "/critical",
    response_model=list[CorrectiveActionResponse],
)
def get_critical_actions(
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
):

    return fetch_all(
        """
        SELECT
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
        FROM analytics.mart_corrective_actions
        WHERE
            is_open = TRUE
            AND indicateur_age IN (
                'Critique',
                'Escalade management'
            )
        ORDER BY age_jours DESC NULLS LAST
        LIMIT %s
        """,
        (limit,),
    )