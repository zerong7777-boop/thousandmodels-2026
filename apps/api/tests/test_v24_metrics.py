from app.metrics import METRICS
from tests.conftest import login_as


def _counter(name: str) -> int:
    return METRICS.snapshot().get(name, 0)


def test_metrics_endpoint_returns_counters_without_secrets(client):
    response = client.get("/api/metrics")

    assert response.status_code == 200
    body = response.json()
    assert body["scope"] == "process"
    assert isinstance(body["counters"], dict)
    serialized = response.text
    assert "APP_SECRET_KEY" not in serialized
    assert "DASHSCOPE_API_KEY" not in serialized
    assert "zhiyin_session" not in serialized


def test_health_check_increments_metric(client):
    before = _counter("health_checks_total")

    response = client.get("/api/health")

    assert response.status_code == 200
    assert _counter("health_checks_total") == before + 1


def test_invalid_login_increments_auth_failure_metric(client):
    before = _counter("auth_failures_total|reason=invalid_credentials")

    response = client.post(
        "/api/auth/login",
        json={"username": "organizer.demo", "password": "wrong"},
        headers={"origin": "http://127.0.0.1:5173"},
    )

    assert response.status_code == 401
    assert _counter("auth_failures_total|reason=invalid_credentials") == before + 1


def test_protected_route_increments_missing_session_auth_failure_metric(client):
    before = _counter("auth_failures_total|reason=missing_session")

    response = client.get("/api/events")

    assert response.status_code == 401
    assert _counter("auth_failures_total|reason=missing_session") == before + 1


def test_forbidden_role_increments_auth_failure_metric(client):
    login_as(client, "merchant.m001.demo")
    before = _counter("auth_failures_total|reason=forbidden_role")

    response = client.get("/api/events")

    assert response.status_code == 403
    assert _counter("auth_failures_total|reason=forbidden_role") == before + 1
