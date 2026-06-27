import json

from app.main import app
from app.store import STORE


def test_ready_reports_operational_summary_without_secrets_or_paths(client):
    response = client.get("/api/ready")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["settings"]["app_env"] == "local"
    assert "pending_migrations" in payload["store"]
    assert payload["store"]["connectivity"] == "ok"
    assert payload["auth_policy"]["csrf_mode"] in {"demo", "double-submit"}
    assert payload["providers"]["qwenpaw_smoke"]["enabled"] is False

    serialized = json.dumps(payload, ensure_ascii=False)
    assert "APP_SECRET_KEY" not in serialized
    assert "DASHSCOPE_API_KEY" not in serialized
    assert "gho_" not in serialized
    assert str(STORE.db_path) not in serialized


def test_ready_route_is_registered_on_app():
    paths = {route.path for route in app.routes}

    assert "/api/ready" in paths
