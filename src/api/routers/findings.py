from fastapi import APIRouter, HTTPException, Query

from src.api.database import fetch_all
from src.api.schemas import FindingResponse


router = APIRouter(
    prefix="/api/v1/findings",
    tags=["Findings"],
)


ALLOWED_CATEGORIES = {
    "NC Mineure",
    "NC Majeure",
    "Observation",
    "OFI",
    "Bonne Pratique",
    "NA",
}
@router.get(
    "",
    response_model=list[FindingResponse],
    summary="List quality findings",
)


@router.get(
    "",
    response_model=list[FindingResponse],
)
def get_findings(
    account_name: str | None = Query(
        default=None,
        description="Filtrer par nom de compte",
    ),
    category: str | None = Query(
        default=None,
        description="Filtrer par catégorie de finding",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
        description="Nombre maximum de findings retournés",
    ),
):

    if category is not None and category not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid finding category. "
                f"Allowed values: {sorted(ALLOWED_CATEGORIES)}"
            ),
        )

    conditions = []
    params = []

    if account_name:
        conditions.append("account_name = %s")
        params.append(account_name)

    if category:
        conditions.append("categorie_finding = %s")
        params.append(category)

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    params.append(limit)

    query = f"""
        SELECT
            finding_id,
            account_name,
            clause_iso,
            libelle_terrain,
            categorie_finding,
            is_counted_in_total_findings
        FROM analytics.mart_findings
        {where_clause}
        ORDER BY account_name, clause_iso
        LIMIT %s
    """

    return fetch_all(
        query,
        tuple(params),
    )