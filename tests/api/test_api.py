from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


# =====================================================
# HEALTH
# =====================================================

def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "quality-intelligence-platform-api"


def test_database_health():
    response = client.get("/health/db")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["database"] == "quality_intelligence"
    assert data["user"] == "qip_user"


# =====================================================
# KPIs
# =====================================================

def test_kpis_overview():
    response = client.get(
        "/api/v1/kpis/overview"
    )

    assert response.status_code == 200

    data = response.json()

    assert "audits_planned" in data
    assert "audited" in data
    assert "in_progress" in data
    assert "not_started" in data
    assert "progress_pct" in data
    assert "avg_maturity_score" in data
    assert "total_findings" in data
    assert "major_nc" in data
    assert "open_actions" in data
    assert "escalations" in data


# =====================================================
# ACCOUNTS
# =====================================================

def test_accounts_list():
    response = client.get(
        "/api/v1/accounts"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    first_account = data[0]

    assert "account_id" in first_account
    assert "account_name" in first_account
    assert "official_audit_status" in first_account


def test_account_not_found():
    response = client.get(
        "/api/v1/accounts/999999"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Account not found"
    )


# =====================================================
# FINDINGS
# =====================================================

def test_findings():
    response = client.get(
        "/api/v1/findings?limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 10


def test_findings_invalid_category():
    response = client.get(
        "/api/v1/findings?category=XYZ"
    )

    assert response.status_code == 400


def test_findings_invalid_limit():
    response = client.get(
        "/api/v1/findings?limit=1000"
    )

    assert response.status_code == 422


# =====================================================
# ACTIONS
# =====================================================

def test_actions():
    response = client.get(
        "/api/v1/actions?limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 10


def test_open_actions_filter():
    response = client.get(
        "/api/v1/actions?is_open=true&limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    for action in data:
        assert action["is_open"] is True


def test_invalid_age_level():
    response = client.get(
        "/api/v1/actions?age_level=XYZ"
    )

    assert response.status_code == 400


def test_critical_actions():
    response = client.get(
        "/api/v1/actions/critical?limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    for action in data:
        assert action["is_open"] is True
        assert action["indicateur_age"] in {
            "Critique",
            "Escalade management",
        }


# =====================================================
# MONITORING
# =====================================================

def test_monitoring_runs():
    response = client.get(
        "/api/v1/monitoring/runs?limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 5


def test_monitoring_history():
    response = client.get(
        "/api/v1/monitoring/history?limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 10


def test_monitoring_invalid_level():
    response = client.get(
        "/api/v1/monitoring/history?level=XYZ"
    )

    assert response.status_code == 400