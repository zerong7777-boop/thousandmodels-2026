import pytest

from app.migrations.runner import latest_schema_version, run_migrations
from app.seed import seed_demo, seed_demo_accounts
from app.store import MVPStore


def test_store_initialization_records_latest_schema_version(tmp_path):
    db_path = tmp_path / "store.sqlite3"

    store = MVPStore(db_path)

    assert latest_schema_version(store.conn) == "0002_auth_tables"
    rows = store.conn.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()
    assert [row["version"] for row in rows] == ["0001_initial_records", "0002_auth_tables"]


def test_store_migration_preserves_existing_record_operations(tmp_path):
    store = MVPStore(tmp_path / "records.sqlite3")

    brief = seed_demo(store)

    summary = store.get_event_summary("demo-night-tour")
    assert summary is not None
    assert summary.event_id == brief.event_id
    assert store.get_event_brief("demo-night-tour") == brief
    assert store.list_route_points()


def test_store_migration_preserves_existing_auth_operations(tmp_path):
    store = MVPStore(tmp_path / "auth.sqlite3")

    seed_demo_accounts(store)

    organizer = store.get_user_by_username("organizer.demo")
    assert organizer is not None
    assert organizer.role == "organizer"
    assert len(store.list_users()) == 3


def test_ensure_auth_schema_delegates_to_idempotent_migrations(tmp_path):
    store = MVPStore(tmp_path / "compat.sqlite3")

    store.ensure_auth_schema()
    store.ensure_auth_schema()

    rows = store.conn.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()
    assert [row["version"] for row in rows] == ["0001_initial_records", "0002_auth_tables"]


def test_production_store_refuses_pending_migrations_when_auto_migrate_disabled(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTO_MIGRATE", "false")

    with pytest.raises(RuntimeError, match="AUTO_MIGRATE=false"):
        MVPStore(tmp_path / "pending.sqlite3")


def test_production_store_allows_current_schema_when_auto_migrate_disabled(
    tmp_path, monkeypatch
):
    db_path = tmp_path / "current.sqlite3"
    run_migrations(db_path)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTO_MIGRATE", "false")

    store = MVPStore(db_path)

    assert latest_schema_version(store.conn) == "0002_auth_tables"
