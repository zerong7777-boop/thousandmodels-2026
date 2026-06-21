import json

from app.seed import DEMO_AUTH_USERS, seed_demo, seed_demo_accounts
from app.store import STORE, MVPStore


EVENT_ID = "demo-night-tour"


def reset_demo_state(store: MVPStore = STORE, event_id: str = EVENT_ID) -> dict:
    store.clear_demo(event_id)
    if hasattr(store, "clear_auth_for_tests"):
        store.clear_auth_for_tests()
    if hasattr(store, "ensure_auth_schema"):
        store.ensure_auth_schema()
    seed_demo_accounts(store)
    brief = seed_demo(store, event_id=event_id)
    return {
        "status": "ok",
        "event_id": brief.event_id,
        "demo_account_usernames": [
            account["username"] for account in DEMO_AUTH_USERS
        ],
    }


def main() -> None:
    print(json.dumps(reset_demo_state(), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
