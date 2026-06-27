import pytest
from fastapi.testclient import TestClient

from app import main
from app.settings import load_settings
from app.store import MVPStore


def demo_usernames(store: MVPStore) -> set[str]:
    return {user.username for user in store.list_users()}


def test_validate_and_seed_auth_seeds_demo_users_when_demo_mode_is_true():
    store = MVPStore(":memory:")
    settings = load_settings({"APP_ENV": "local", "DEMO_MODE": "true"})

    main.validate_and_seed_auth(store, settings)

    assert {"organizer.demo", "merchant.m001.demo", "tourist.demo"} <= demo_usernames(store)


def test_validate_and_seed_auth_does_not_seed_demo_users_when_demo_mode_is_false():
    store = MVPStore(":memory:")
    settings = load_settings({"APP_ENV": "local", "DEMO_MODE": "false"})

    main.validate_and_seed_auth(store, settings)

    assert demo_usernames(store) == set()


def test_startup_validation_failure_prevents_seeding_and_propagates_error():
    store = MVPStore(":memory:")
    settings = load_settings(
        {
            "APP_ENV": "production",
            "DEMO_MODE": "true",
            "APP_SECRET_KEY": "test-secret",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://example.com",
        }
    )

    with pytest.raises(RuntimeError, match="DEMO_MODE"):
        main.validate_and_seed_auth(store, settings)

    assert demo_usernames(store) == set()


def test_fastapi_startup_uses_validated_settings_loader(monkeypatch):
    store = MVPStore(":memory:")
    calls = []

    def fake_load_validated_settings():
        calls.append("validated")
        return load_settings({"APP_ENV": "local", "DEMO_MODE": "false"})

    monkeypatch.setattr(main, "STORE", store)
    monkeypatch.setattr(main, "load_validated_settings", fake_load_validated_settings, raising=False)

    with TestClient(main.app):
        pass

    assert calls == ["validated"]
    assert demo_usernames(store) == set()
