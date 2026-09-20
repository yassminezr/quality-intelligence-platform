from fastapi import APIRouter, HTTPException

from src.api.database import fetch_all, fetch_one
from src.api.schemas import (
    AccountDetailResponse,
    AccountSummaryResponse,
)


router = APIRouter(
    prefix="/api/v1/accounts",
    tags=["Accounts"],
)


# =====================================================
# LISTE DES COMPTES
# =====================================================

@router.get(
    "",
    response_model=list[AccountSummaryResponse],
    summary="List audited accounts",
)
def get_accounts():

    return fetch_all(
        """
        SELECT
            account_id,
            account_name,
            official_audit_status,
            completion_rate,
            avg_maturity_score,
            account_badge
        FROM analytics.mart_audit_overview
        ORDER BY account_name
        """
    )


# =====================================================
# DETAIL D'UN COMPTE
# =====================================================

@router.get(
    "/{account_id}",
    response_model=AccountDetailResponse,
    summary="Get account details",
)
def get_account(
    account_id: int,
):

    row = fetch_one(
        """
        SELECT
            account_id,
            account_name,
            official_audit_status,
            completion_rate,
            avg_maturity_score,
            account_badge
        FROM analytics.mart_audit_overview
        WHERE account_id = %s
        """,
        (account_id,),
    )

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return row