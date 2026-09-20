from fastapi import FastAPI

from src.api.routers.accounts import router as accounts_router
from src.api.routers.actions import router as actions_router
from src.api.routers.findings import router as findings_router
from src.api.routers.health import router as health_router
from src.api.routers.kpis import router as kpis_router
from src.api.routers.monitoring import router as monitoring_router


app = FastAPI(
    title="Quality Intelligence Platform API",
    description=(
        "REST API for the Quality Intelligence Platform. "
        "It exposes quality audit KPIs, accounts, findings, "
        "corrective actions and monitoring data produced by "
        "PostgreSQL and dbt analytics marts."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


app.include_router(health_router)
app.include_router(kpis_router)
app.include_router(accounts_router)
app.include_router(findings_router)
app.include_router(actions_router)
app.include_router(monitoring_router)