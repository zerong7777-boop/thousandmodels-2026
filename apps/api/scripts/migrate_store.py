import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
API_ROOT = SCRIPT_DIR.parent
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.migrations.runner import run_migrations
from app.store_paths import database_path_from_env


def main() -> None:
    result = run_migrations(database_path_from_env())
    print(result.to_json())


if __name__ == "__main__":
    main()
