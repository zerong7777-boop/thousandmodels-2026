import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed_demo_accounts
from app.store import STORE


@pytest.fixture(autouse=True)
def reset_store():
    STORE.clear_demo()
    if hasattr(STORE, "clear_auth_for_tests"):
        STORE.clear_auth_for_tests()
    if hasattr(STORE, "ensure_auth_schema"):
        STORE.ensure_auth_schema()
    seed_demo_accounts(STORE)
    yield
    STORE.clear_demo()


@pytest.fixture
def client():
    return TestClient(app)


def login_as(client: TestClient, username: str, password: str = "demo1234"):
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
        headers={"origin": "http://127.0.0.1:5173"},
    )
    assert response.status_code == 200, response.text
    return response
