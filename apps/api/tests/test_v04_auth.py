from datetime import UTC, datetime, timedelta

from app.seed import DEMO_AUTH_USERS, seed_demo_accounts
from app.store import STORE


def test_seed_demo_accounts_are_first_class_rows():
    seed_demo_accounts(STORE)
    users = STORE.list_users()
    usernames = {user.username for user in users}

    assert {"organizer.demo", "merchant.m001.demo", "tourist.demo"} <= usernames
    assert STORE.get_payload("users", "organizer.demo") is None
    assert STORE.get_user_by_username("merchant.m001.demo").merchant_id == "m001"


def test_password_hash_never_stores_raw_password():
    seed_demo_accounts(STORE)
    user = STORE.get_user_by_username("organizer.demo")

    assert user is not None
    assert user.password_hash != DEMO_AUTH_USERS[0]["password"]
    assert "demo1234" not in user.password_hash
    assert user.password_hash.startswith("pbkdf2_sha256$")


def test_login_sets_http_only_cookie_and_me_returns_public_user(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "organizer.demo", "password": "demo1234"},
        headers={"origin": "http://127.0.0.1:5173"},
    )

    assert response.status_code == 200
    assert response.json()["user"] == {
        "user_id": "usr_org_demo",
        "username": "organizer.demo",
        "role": "organizer",
        "display_name": "Organizer Demo",
        "merchant_id": None,
    }
    assert "password_hash" not in response.text
    assert "token_hash" not in response.text
    assert "zhiyin_session=" in response.headers["set-cookie"]
    assert "httponly" in response.headers["set-cookie"].lower()
    assert "samesite=lax" in response.headers["set-cookie"].lower()

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["username"] == "organizer.demo"


def test_login_accepts_local_vite_fallback_origin(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "organizer.demo", "password": "demo1234"},
        headers={"origin": "http://127.0.0.1:5174"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["username"] == "organizer.demo"


def test_login_failure_is_generic_and_does_not_set_cookie(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "organizer.demo", "password": "wrong"},
        headers={"origin": "http://127.0.0.1:5173"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid credentials"
    assert "set-cookie" not in response.headers


def test_me_without_session_returns_401(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_logout_revokes_session_and_clears_cookie(client):
    client.post(
        "/api/auth/login",
        json={"username": "tourist.demo", "password": "demo1234"},
        headers={"origin": "http://127.0.0.1:5173"},
    )

    logout = client.post("/api/auth/logout", headers={"origin": "http://127.0.0.1:5173"})
    assert logout.status_code == 200
    assert "zhiyin_session=" in logout.headers["set-cookie"]

    me = client.get("/api/auth/me")
    assert me.status_code == 401


def test_disabled_user_cannot_login_and_existing_session_is_rejected(client):
    client.post(
        "/api/auth/login",
        json={"username": "merchant.m001.demo", "password": "demo1234"},
        headers={"origin": "http://127.0.0.1:5173"},
    )
    STORE.update_user_status("usr_merchant_m001_demo", "disabled")

    me = client.get("/api/auth/me")
    assert me.status_code == 401

    login = client.post(
        "/api/auth/login",
        json={"username": "merchant.m001.demo", "password": "demo1234"},
        headers={"origin": "http://127.0.0.1:5173"},
    )
    assert login.status_code == 401


def test_expired_and_revoked_sessions_are_rejected(client):
    login = client.post(
        "/api/auth/login",
        json={"username": "tourist.demo", "password": "demo1234"},
        headers={"origin": "http://127.0.0.1:5173"},
    )
    assert login.status_code == 200

    session = STORE.list_sessions_for_user("usr_tourist_demo")[0]
    STORE.set_session_expiry(session.session_id, datetime.now(UTC) - timedelta(minutes=1))

    expired = client.get("/api/auth/me")
    assert expired.status_code == 401

    login = client.post(
        "/api/auth/login",
        json={"username": "tourist.demo", "password": "demo1234"},
        headers={"origin": "http://127.0.0.1:5173"},
    )
    assert login.status_code == 200
    session = STORE.list_sessions_for_user("usr_tourist_demo")[0]
    STORE.revoke_session(session.session_id)

    revoked = client.get("/api/auth/me")
    assert revoked.status_code == 401
