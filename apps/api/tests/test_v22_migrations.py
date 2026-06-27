import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from app.migrations import runner
from app.migrations.runner import (
    applied_versions,
    latest_schema_version,
    pending_versions,
    run_migrations,
)
from app.migrations.versions import Migration


EXPECTED_MIGRATIONS = ["0001_initial_records", "0002_auth_tables"]


def table_names(db_path):
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    return {row[0] for row in rows}


def test_fresh_database_applies_all_migrations(tmp_path):
    db_path = tmp_path / "fresh.sqlite3"

    result = run_migrations(db_path)

    assert result.applied_versions == EXPECTED_MIGRATIONS
    assert result.current_version == "0002_auth_tables"
    assert result.pending_versions == []
    assert latest_schema_version(db_path) == "0002_auth_tables"
    assert pending_versions(db_path) == []
    assert {"schema_migrations", "records", "users", "sessions"}.issubset(table_names(db_path))


def test_migration_runner_is_idempotent(tmp_path):
    db_path = tmp_path / "idempotent.sqlite3"

    first = run_migrations(db_path)
    second = run_migrations(db_path)

    assert first.applied_versions == EXPECTED_MIGRATIONS
    assert second.applied_versions == []
    assert second.current_version == "0002_auth_tables"
    assert second.pending_versions == []


def test_pending_migrations_detect_partially_applied_database(tmp_path):
    db_path = tmp_path / "partial.sqlite3"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE schema_migrations (
              version TEXT PRIMARY KEY,
              applied_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
            ("0001_initial_records", "2026-06-27T00:00:00+00:00"),
        )

    assert applied_versions(sqlite3.connect(db_path)) == ["0001_initial_records"]
    assert pending_versions(db_path) == ["0002_auth_tables"]


def test_run_migrations_accepts_existing_connection(tmp_path):
    db_path = tmp_path / "connection.sqlite3"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        result = run_migrations(conn)

        assert result.applied_versions == EXPECTED_MIGRATIONS
        assert latest_schema_version(conn) == "0002_auth_tables"
        conn.execute("INSERT INTO records(collection, item_key, payload) VALUES (?, ?, ?)", ("c", "k", "{}"))
        assert conn.execute("SELECT COUNT(*) FROM records").fetchone()[0] == 1
    finally:
        conn.close()


def test_failed_migration_rolls_back_schema_changes(monkeypatch, tmp_path):
    db_path = tmp_path / "failed.sqlite3"
    monkeypatch.setattr(
        runner,
        "MIGRATIONS",
        (
            Migration(
                "9999_bad",
                (
                    "CREATE TABLE should_rollback(id TEXT PRIMARY KEY)",
                    "INSERT INTO missing_table(id) VALUES ('boom')",
                ),
            ),
        ),
    )

    with pytest.raises(sqlite3.OperationalError):
        run_migrations(db_path)

    assert "should_rollback" not in table_names(db_path)
    assert applied_versions(sqlite3.connect(db_path)) == []


def test_read_helpers_do_not_commit_caller_transaction(tmp_path):
    db_path = tmp_path / "read_helpers.sqlite3"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("CREATE TABLE caller_data(id TEXT PRIMARY KEY)")
        conn.commit()
        conn.execute("BEGIN")
        conn.execute("INSERT INTO caller_data(id) VALUES ('uncommitted')")

        assert latest_schema_version(conn) is None
        assert pending_versions(conn) == EXPECTED_MIGRATIONS
    finally:
        conn.close()

    with sqlite3.connect(db_path) as check:
        assert check.execute("SELECT COUNT(*) FROM caller_data").fetchone()[0] == 0
        assert "schema_migrations" not in table_names(db_path)


def test_path_read_helpers_do_not_create_missing_database_or_parent(tmp_path):
    db_path = tmp_path / "missing-parent" / "missing.sqlite3"

    assert latest_schema_version(db_path) is None
    assert pending_versions(db_path) == EXPECTED_MIGRATIONS
    assert not db_path.exists()
    assert not db_path.parent.exists()


def test_migrate_script_reports_applied_versions_for_fresh_database(tmp_path):
    db_path = tmp_path / "script.sqlite3"
    result = subprocess.run(
        [sys.executable, "apps/api/scripts/migrate_store.py"],
        cwd=Path(__file__).resolve().parents[3],
        env={"DATABASE_URL": f"sqlite:///{db_path}"},
        text=True,
        capture_output=True,
        check=True,
    )

    assert '"applied_versions": ["0001_initial_records", "0002_auth_tables"]' in result.stdout
