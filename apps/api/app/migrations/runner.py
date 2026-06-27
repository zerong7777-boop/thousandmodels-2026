import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from app.migrations.versions import MIGRATIONS


SCHEMA_MIGRATIONS_SQL = """
CREATE TABLE IF NOT EXISTS schema_migrations (
  version TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL
)
"""


@dataclass(frozen=True)
class MigrationResult:
    applied_versions: list[str]
    current_version: str | None
    pending_versions: list[str]

    def to_json(self) -> str:
        return json.dumps(
            {
                "applied_versions": self.applied_versions,
                "current_version": self.current_version,
                "pending_versions": self.pending_versions,
            },
            ensure_ascii=False,
            sort_keys=True,
        )


MigrationTarget = Path | str | sqlite3.Connection


def _migration_versions() -> list[str]:
    return [migration.version for migration in MIGRATIONS]


def _connect(target: MigrationTarget) -> tuple[sqlite3.Connection, bool]:
    if isinstance(target, sqlite3.Connection):
        return target, False
    db_path = Path(target)
    if str(db_path) != ":memory:":
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn, True


def _connect_readonly(target: MigrationTarget) -> tuple[sqlite3.Connection | None, bool]:
    if isinstance(target, sqlite3.Connection):
        return target, False
    db_path = Path(target)
    if str(db_path) == ":memory:":
        conn = sqlite3.connect(":memory:")
    elif not db_path.exists():
        return None, False
    else:
        uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn, True


def ensure_schema_migrations(conn: sqlite3.Connection) -> None:
    conn.execute(SCHEMA_MIGRATIONS_SQL)


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _run_in_savepoint(conn: sqlite3.Connection, statements: Iterable[str]) -> None:
    savepoint = f"migration_{uuid4().hex}"
    conn.execute(f"SAVEPOINT {savepoint}")
    try:
        for statement in statements:
            conn.execute(statement)
        conn.execute(f"RELEASE SAVEPOINT {savepoint}")
    except Exception:
        conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
        conn.execute(f"RELEASE SAVEPOINT {savepoint}")
        raise


def _apply_migration(conn: sqlite3.Connection, version: str, statements: Iterable[str]) -> None:
    savepoint = f"migration_{uuid4().hex}"
    conn.execute(f"SAVEPOINT {savepoint}")
    try:
        for statement in statements:
            conn.execute(statement)
        conn.execute(
            "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
            (version, datetime.now(UTC).isoformat()),
        )
        conn.execute(f"RELEASE SAVEPOINT {savepoint}")
    except Exception:
        conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
        conn.execute(f"RELEASE SAVEPOINT {savepoint}")
        raise


def applied_versions(conn: sqlite3.Connection) -> list[str]:
    if not _table_exists(conn, "schema_migrations"):
        return []
    rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    observed = {row["version"] if isinstance(row, sqlite3.Row) else row[0] for row in rows}
    return [version for version in _migration_versions() if version in observed]


def _pending_versions_for_applied(applied: Iterable[str]) -> list[str]:
    applied_set = set(applied)
    return [version for version in _migration_versions() if version not in applied_set]


def run_migrations(target: MigrationTarget) -> MigrationResult:
    conn, should_close = _connect(target)
    applied_now: list[str] = []
    try:
        if not _table_exists(conn, "schema_migrations"):
            _run_in_savepoint(conn, [SCHEMA_MIGRATIONS_SQL])
        applied = set(applied_versions(conn))
        for migration in MIGRATIONS:
            if migration.version in applied:
                continue
            _apply_migration(conn, migration.version, migration.statements)
            applied.add(migration.version)
            applied_now.append(migration.version)
        current = latest_schema_version(conn)
        return MigrationResult(
            applied_versions=applied_now,
            current_version=current,
            pending_versions=_pending_versions_for_applied(applied),
        )
    finally:
        if should_close:
            conn.close()


def pending_versions(target: MigrationTarget) -> list[str]:
    conn, should_close = _connect_readonly(target)
    if conn is None:
        return _migration_versions()
    try:
        return _pending_versions_for_applied(applied_versions(conn))
    finally:
        if should_close:
            conn.close()


def latest_schema_version(target: MigrationTarget) -> str | None:
    conn, should_close = _connect_readonly(target)
    if conn is None:
        return None
    try:
        applied = applied_versions(conn)
        return applied[-1] if applied else None
    finally:
        if should_close:
            conn.close()
