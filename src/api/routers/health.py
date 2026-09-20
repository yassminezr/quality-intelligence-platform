from fastapi import APIRouter, HTTPException

from src.api.database import fetch_one


router = APIRouter(
    tags=["Health"],
)


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "quality-intelligence-platform-api",
    }


@router.get("/health/db")
def database_health_check():
    try:
        result = fetch_one(
            """
            SELECT
                current_database() AS database,
                current_user AS user,
                NOW() AS checked_at
            """
        )

        return {
            "status": "ok",
            "database": result["database"],
            "user": result["user"],
            "checked_at": result["checked_at"],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from exc