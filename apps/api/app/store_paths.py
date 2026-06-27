import os
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def database_path_from_env() -> Path:
    raw = os.getenv("DATABASE_URL", "sqlite:///./data/runtime/zhiyin.sqlite3")
    if raw.startswith("sqlite:///"):
        raw = raw.removeprefix("sqlite:///")
    path = Path(raw)
    if not path.is_absolute():
        path = project_root() / path
    return path
