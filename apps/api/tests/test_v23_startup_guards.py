import pytest

from app.settings import load_validated_settings
from app.store import MVPStore


def _restricted_env(**overrides):
    env = {
        "APP_ENV": "production",
        "DEMO_MODE": "false",
        "APP_SECRET_KEY": "test-secret",
        "CSRF_MODE": "double-submit",
        "ALLOWED_ORIGINS": "https://example.com",
        "AUTO_MIGRATE": "false",
    }
    env.update(overrides)
    return env


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_restricted_env_refuses_live_qwenpaw_smoke_flag(app_env):
    with pytest.raises(RuntimeError, match="RUN_LIVE_QWENPAW_SMOKE"):
        load_validated_settings(
            _restricted_env(APP_ENV=app_env, RUN_LIVE_QWENPAW_SMOKE="true")
        )


@pytest.mark.parametrize("app_env", ["staging", "production"])
@pytest.mark.parametrize(
    "base_url",
    [
        "http://127.0.0.1:8088",
        "http://localhost:8088",
        "http://[::1]:8088",
    ],
)
def test_restricted_env_refuses_local_qwenpaw_base_url(app_env, base_url):
    with pytest.raises(RuntimeError, match="QWENPAW_BASE_URL"):
        load_validated_settings(_restricted_env(APP_ENV=app_env, QWENPAW_BASE_URL=base_url))


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_restricted_env_refuses_auto_migrate_true(app_env):
    with pytest.raises(RuntimeError, match="AUTO_MIGRATE"):
        load_validated_settings(_restricted_env(APP_ENV=app_env, AUTO_MIGRATE="true"))


def test_production_accepts_manual_migration_policy_without_qwenpaw_smoke():
    settings = load_validated_settings(_restricted_env())

    assert settings.app_env == "production"
    assert settings.auto_migrate is False
    assert settings.run_live_qwenpaw_smoke is False


def test_local_allows_manual_qwenpaw_smoke_for_guarded_smoke_only():
    settings = load_validated_settings(
        {
            "APP_ENV": "local",
            "RUN_LIVE_QWENPAW_SMOKE": "true",
            "QWENPAW_BASE_URL": "http://127.0.0.1:8088",
        }
    )

    assert settings.run_live_qwenpaw_smoke is True


def test_store_refuses_auto_migrate_true_before_creating_restricted_database(
    monkeypatch, tmp_path
):
    db_path = tmp_path / "missing-parent" / "restricted.sqlite3"
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("AUTO_MIGRATE", "true")

    with pytest.raises(RuntimeError, match="AUTO_MIGRATE"):
        MVPStore(db_path)

    assert not db_path.exists()
    assert not db_path.parent.exists()


def test_store_refuses_malformed_app_env_before_creating_database(monkeypatch, tmp_path):
    db_path = tmp_path / "malformed-parent" / "invalid.sqlite3"
    monkeypatch.setenv("APP_ENV", "qa")

    with pytest.raises(ValueError, match="APP_ENV"):
        MVPStore(db_path)

    assert not db_path.exists()
    assert not db_path.parent.exists()
