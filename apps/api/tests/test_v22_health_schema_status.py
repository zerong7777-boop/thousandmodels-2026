from fastapi.testclient import TestClient

from app.main import app
from app.migrations.runner import run_migrations


def test_health_reports_store_schema_metadata():
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["agent_backend"]
    assert payload["store"]["kind"] == "sqlite"
    assert payload["store"]["schema_version"] == "0002_auth_tables"
    assert payload["store"]["pending_migrations"] == 0


def test_health_reports_pending_migration_count(monkeypatch, tmp_path):
    db_path = tmp_path / "partial.sqlite3"
    run_migrations(db_path)

    from app import main

    pending_store = main.MVPStore(db_path)
    pending_store.conn.execute("DELETE FROM schema_migrations WHERE version = ?", ("0002_auth_tables",))
    pending_store.conn.commit()

    monkeypatch.setattr(main, "STORE", pending_store)
    client = TestClient(main.app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["store"]["pending_migrations"] == 1


def test_health_omits_database_path_in_production(monkeypatch, tmp_path):
    from app import main

    prod_store = main.MVPStore(tmp_path / "prod.sqlite3")
    monkeypatch.setattr(main, "STORE", prod_store)
    monkeypatch.setenv("APP_ENV", "production")

    client = TestClient(main.app)
    response = client.get("/api/health")

    assert response.status_code == 200
    assert "database_path" not in response.json()["store"]


def test_health_omits_database_path_in_staging(monkeypatch, tmp_path):
    from app import main

    staging_store = main.MVPStore(tmp_path / "staging.sqlite3")
    monkeypatch.setattr(main, "STORE", staging_store)
    monkeypatch.setenv("APP_ENV", "staging")

    client = TestClient(main.app)
    response = client.get("/api/health")

    assert response.status_code == 200
    assert "database_path" not in response.json()["store"]
