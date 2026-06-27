import pytest

from app.settings import load_settings, load_validated_settings


def test_local_defaults_enable_demo_mode():
    settings = load_settings({})

    assert settings.app_env == "local"
    assert settings.demo_mode is True
    assert settings.app_secret_key is None
    assert settings.session_cookie_secure is False
    assert settings.session_samesite == "lax"
    assert settings.session_ttl_hours == 8
    assert settings.csrf_mode == "demo"
    assert settings.allowed_origins == (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    )


@pytest.mark.parametrize("app_env", ["local", "demo", "staging", "production"])
def test_allowed_app_env_values(app_env):
    settings = load_settings(
        {
            "APP_ENV": app_env,
            "APP_SECRET_KEY": "test-secret",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://example.com",
        }
    )

    assert settings.app_env == app_env


def test_invalid_app_env_is_rejected():
    with pytest.raises(ValueError, match="APP_ENV"):
        load_settings({"APP_ENV": "qa"})


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("0", False),
        ("no", False),
    ],
)
def test_demo_mode_explicit_parsing(value, expected):
    settings = load_settings({"DEMO_MODE": value})

    assert settings.demo_mode is expected


def test_invalid_demo_mode_is_rejected():
    with pytest.raises(ValueError, match="DEMO_MODE"):
        load_settings({"DEMO_MODE": "maybe"})


def test_app_secret_key_optional_for_local_and_required_secret_has_dev_fallback():
    settings = load_settings({"APP_ENV": "local"})

    settings.validate_startup()
    assert settings.required_secret() == "local-dev-only-secret"


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_app_secret_key_required_for_staging_and_production(app_env):
    settings = load_settings(
        {
            "APP_ENV": app_env,
            "DEMO_MODE": "false",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://example.com",
        }
    )

    with pytest.raises(RuntimeError, match="APP_SECRET_KEY"):
        settings.validate_startup()
    with pytest.raises(RuntimeError, match="APP_SECRET_KEY"):
        settings.required_secret()


@pytest.mark.parametrize(
    ("app_env", "expected"),
    [("production", True), ("staging", True), ("local", False), ("demo", False)],
)
def test_session_cookie_secure_auto_resolves_by_environment(app_env, expected):
    settings = load_settings(
        {
            "APP_ENV": app_env,
            "APP_SECRET_KEY": "test-secret",
            "DEMO_MODE": "false",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://example.com",
        }
    )

    assert settings.session_cookie_secure is expected


@pytest.mark.parametrize(("value", "expected"), [("true", True), ("false", False)])
def test_session_cookie_secure_explicit_parsing(value, expected):
    settings = load_settings({"SESSION_COOKIE_SECURE": value})

    assert settings.session_cookie_secure is expected


def test_invalid_session_cookie_secure_is_rejected():
    with pytest.raises(ValueError, match="SESSION_COOKIE_SECURE"):
        load_settings({"SESSION_COOKIE_SECURE": "sometimes"})


@pytest.mark.parametrize("same_site", ["lax", "strict", "none"])
def test_session_samesite_accepts_known_values(same_site):
    settings = load_settings({"SESSION_SAMESITE": same_site, "SESSION_COOKIE_SECURE": "true"})

    assert settings.session_samesite == same_site


def test_session_samesite_none_requires_secure_cookies():
    settings = load_settings({"SESSION_SAMESITE": "none", "SESSION_COOKIE_SECURE": "false"})

    with pytest.raises(RuntimeError, match="SESSION_SAMESITE"):
        settings.validate_startup()


@pytest.mark.parametrize("ttl", ["1", "24", "720"])
def test_session_ttl_hours_must_be_positive_integer(ttl):
    settings = load_settings({"SESSION_TTL_HOURS": ttl})

    assert settings.session_ttl_hours == int(ttl)


@pytest.mark.parametrize("ttl", ["0", "-1", "1.5", "abc"])
def test_invalid_session_ttl_hours_is_rejected(ttl):
    with pytest.raises(ValueError, match="SESSION_TTL_HOURS"):
        load_settings({"SESSION_TTL_HOURS": ttl})


@pytest.mark.parametrize("csrf_mode", ["demo", "double-submit"])
def test_csrf_mode_accepts_known_values(csrf_mode):
    settings = load_settings({"CSRF_MODE": csrf_mode})

    assert settings.csrf_mode == csrf_mode


def test_invalid_csrf_mode_is_rejected():
    with pytest.raises(ValueError, match="CSRF_MODE"):
        load_settings({"CSRF_MODE": "token"})


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_staging_and_production_require_double_submit_csrf(app_env):
    settings = load_settings(
        {
            "APP_ENV": app_env,
            "APP_SECRET_KEY": "test-secret",
            "DEMO_MODE": "false",
            "CSRF_MODE": "demo",
            "ALLOWED_ORIGINS": "https://example.com",
        }
    )

    with pytest.raises(RuntimeError, match="CSRF_MODE"):
        settings.validate_startup()


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_staging_and_production_reject_demo_mode_true(app_env):
    settings = load_settings(
        {
            "APP_ENV": app_env,
            "DEMO_MODE": "true",
            "APP_SECRET_KEY": "test-secret",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://example.com",
        }
    )

    with pytest.raises(RuntimeError, match="DEMO_MODE"):
        settings.validate_startup()


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_staging_and_production_reject_insecure_session_cookie(app_env):
    settings = load_settings(
        {
            "APP_ENV": app_env,
            "DEMO_MODE": "false",
            "APP_SECRET_KEY": "test-secret",
            "SESSION_COOKIE_SECURE": "false",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://example.com",
        }
    )

    with pytest.raises(RuntimeError, match="SESSION_COOKIE_SECURE"):
        settings.validate_startup()


@pytest.mark.parametrize("app_env", ["local", "demo"])
def test_local_and_demo_allowed_origins_default_to_localhost(app_env):
    settings = load_settings({"APP_ENV": app_env})

    assert "http://localhost:5173" in settings.allowed_origins
    assert "http://127.0.0.1:5174" in settings.allowed_origins


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_staging_and_production_require_explicit_https_allowed_origins(app_env):
    missing = load_settings(
        {
            "APP_ENV": app_env,
            "APP_SECRET_KEY": "test-secret",
            "DEMO_MODE": "false",
            "CSRF_MODE": "double-submit",
        }
    )
    http = load_settings(
        {
            "APP_ENV": app_env,
            "APP_SECRET_KEY": "test-secret",
            "DEMO_MODE": "false",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://example.com,http://localhost:5173",
        }
    )

    with pytest.raises(RuntimeError, match="ALLOWED_ORIGINS"):
        missing.validate_startup()
    with pytest.raises(RuntimeError, match="ALLOWED_ORIGINS"):
        http.validate_startup()


@pytest.mark.parametrize("app_env", ["staging", "production"])
@pytest.mark.parametrize(
    "origin",
    [
        "https://",
        "https://example.com/path",
        "https://user@example.com",
        "https://example.com?x=1",
        "https://example.com:bad",
        "https://example.com:99999",
        "https://example.com:",
        "https:// example.com",
        "https://example.com\x7f",
        "https://example.com/",
    ],
)
def test_staging_and_production_reject_malformed_allowed_origins(app_env, origin):
    settings = load_settings(
        {
            "APP_ENV": app_env,
            "APP_SECRET_KEY": "test-secret",
            "DEMO_MODE": "false",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": origin,
        }
    )

    with pytest.raises(RuntimeError, match="ALLOWED_ORIGINS"):
        settings.validate_startup()


def test_allowed_origins_are_trimmed_and_empty_values_are_ignored():
    settings = load_settings(
        {"ALLOWED_ORIGINS": " https://one.example, ,https://two.example "}
    )

    assert settings.allowed_origins == ("https://one.example", "https://two.example")


def test_load_validated_settings_rejects_unsafe_production_config():
    with pytest.raises(RuntimeError, match="DEMO_MODE"):
        load_validated_settings(
            {
                "APP_ENV": "production",
                "DEMO_MODE": "true",
                "APP_SECRET_KEY": "test-secret",
                "CSRF_MODE": "double-submit",
                "ALLOWED_ORIGINS": "https://example.com",
            }
        )


def test_load_validated_settings_rejects_unsafe_staging_config():
    with pytest.raises(RuntimeError, match="SESSION_COOKIE_SECURE"):
        load_validated_settings(
            {
                "APP_ENV": "staging",
                "DEMO_MODE": "false",
                "APP_SECRET_KEY": "test-secret",
                "SESSION_COOKIE_SECURE": "false",
                "CSRF_MODE": "double-submit",
                "ALLOWED_ORIGINS": "https://example.com",
            }
        )


def test_load_validated_settings_returns_valid_production_config():
    settings = load_validated_settings(
        {
            "APP_ENV": "production",
            "DEMO_MODE": "false",
            "APP_SECRET_KEY": "test-secret",
            "CSRF_MODE": "double-submit",
            "ALLOWED_ORIGINS": "https://example.com",
            "AUTO_MIGRATE": "false",
        }
    )

    assert settings.app_env == "production"
    assert settings.app_secret_key == "test-secret"
    assert settings.session_cookie_secure is True
    assert settings.allowed_origins == ("https://example.com",)
