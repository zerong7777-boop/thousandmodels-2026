from dataclasses import dataclass


@dataclass(frozen=True)
class Migration:
    version: str
    statements: tuple[str, ...]


MIGRATIONS: tuple[Migration, ...] = (
    Migration(
        version="0001_initial_records",
        statements=(
            """
            CREATE TABLE IF NOT EXISTS records (
              collection TEXT NOT NULL,
              item_key TEXT NOT NULL,
              payload TEXT NOT NULL,
              PRIMARY KEY (collection, item_key)
            )
            """,
        ),
    ),
    Migration(
        version="0002_auth_tables",
        statements=(
            """
            CREATE TABLE IF NOT EXISTS users (
              user_id TEXT PRIMARY KEY,
              username TEXT UNIQUE NOT NULL,
              password_hash TEXT NOT NULL,
              role TEXT NOT NULL,
              display_name TEXT NOT NULL,
              merchant_id TEXT NULL,
              status TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sessions (
              session_id TEXT PRIMARY KEY,
              token_hash TEXT UNIQUE NOT NULL,
              user_id TEXT NOT NULL,
              created_at TEXT NOT NULL,
              expires_at TEXT NOT NULL,
              revoked_at TEXT NULL,
              FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
            """,
            "CREATE INDEX IF NOT EXISTS idx_sessions_token_hash ON sessions(token_hash)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)",
        ),
    ),
)
