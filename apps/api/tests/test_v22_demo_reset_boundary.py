import pytest
import os
import subprocess
import sys
from pathlib import Path

from app.seed import seed_demo
from app.settings import AppSettings, load_settings
from app.store import MVPStore
from scripts.reset_demo_state import reset_demo_state


def test_reset_demo_state_allows_local_demo_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("DEMO_MODE", "true")
    store = MVPStore(tmp_path / "local.sqlite3")

    result = reset_demo_state(store=store)

    assert result["status"] == "reset"
    assert store.get_event_summary("demo-night-tour") is not None
    assert store.get_user_by_username("organizer.demo") is not None


def test_reset_demo_state_refuses_when_demo_mode_is_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("DEMO_MODE", "false")
    store = MVPStore(tmp_path / "disabled.sqlite3")
    brief = seed_demo(store)

    with pytest.raises(RuntimeError, match="DEMO_MODE=true"):
        reset_demo_state(store=store)

    assert store.get_event_brief(brief.event_id) == brief


def test_reset_demo_state_refuses_production_even_with_demo_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEMO_MODE", "true")
    store = MVPStore(":memory:")
    brief = seed_demo(store)

    with pytest.raises(RuntimeError, match="local/demo"):
        reset_demo_state(store=store)

    assert store.get_event_brief(brief.event_id) == brief


def test_reset_demo_state_boundary_can_use_explicit_settings(tmp_path):
    store = MVPStore(tmp_path / "explicit.sqlite3")
    settings = AppSettings(
        app_env="local",
        demo_mode=False,
        app_secret_key=None,
        session_cookie_secure=False,
        session_samesite="lax",
        session_ttl_hours=8,
        csrf_mode="double-submit",
        allowed_origins=(),
    )

    with pytest.raises(RuntimeError, match="DEMO_MODE=true"):
        reset_demo_state(store=store, settings=settings)


def test_reset_demo_state_uses_environment_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ENV", "demo")
    monkeypatch.setenv("DEMO_MODE", "true")
    settings = load_settings()
    store = MVPStore(tmp_path / "demo.sqlite3")

    result = reset_demo_state(store=store, settings=settings)

    assert result["status"] == "reset"


def test_reset_demo_state_refuses_before_creating_default_store(tmp_path, monkeypatch):
    db_path = tmp_path / "should-not-exist.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEMO_MODE", "true")

    with pytest.raises(RuntimeError, match="local/demo"):
        reset_demo_state()

    assert not db_path.exists()


def test_importing_reset_module_does_not_create_default_store(tmp_path, monkeypatch):
    db_path = tmp_path / "import-should-not-exist.sqlite3"
    env = os.environ.copy()
    env.update({"DATABASE_URL": f"sqlite:///{db_path}", "PYTHONPATH": "apps/api"})
    result = subprocess.run(
        [sys.executable, "-c", "import scripts.reset_demo_state"],
        cwd=Path(__file__).resolve().parents[3],
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )

    assert result.stderr == ""
    assert not db_path.exists()
