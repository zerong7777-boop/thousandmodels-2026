import json
from typing import TYPE_CHECKING

from app.seed import DEMO_AUTH_USERS, seed_demo, seed_demo_accounts
from app.settings import AppSettings, load_settings

if TYPE_CHECKING:
    from app.store import MVPStore


EVENT_ID = "demo-night-tour"


def ensure_reset_allowed(settings: AppSettings) -> None:
    if settings.app_env not in {"local", "demo"}:
        raise RuntimeError("Demo reset is allowed only in local/demo environments")
    if not settings.demo_mode:
        raise RuntimeError("Demo reset requires DEMO_MODE=true")


def reset_demo_state(
    store: "MVPStore | None" = None,
    event_id: str = EVENT_ID,
    settings: AppSettings | None = None,
) -> dict:
    ensure_reset_allowed(settings or load_settings())
    if store is None:
        from app.store import STORE

        store = STORE
    store.clear_demo(event_id)
    if hasattr(store, "clear_auth_for_tests"):
        store.clear_auth_for_tests()
    if hasattr(store, "ensure_auth_schema"):
        store.ensure_auth_schema()
    seed_demo_accounts(store)
    brief = seed_demo(store, event_id=event_id)
    return {
        "status": "reset",
        "event_id": brief.event_id,
        "demo_accounts": [
            account["username"] for account in DEMO_AUTH_USERS
        ],
    }


def main() -> None:
    print(json.dumps(reset_demo_state(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
