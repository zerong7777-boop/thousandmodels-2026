import json
import logging

from app.main import app
from app.observability import REQUEST_ID_HEADER, log_event
from tests.conftest import login_as


@app.get("/__test/structured-log-unhandled-error")
def structured_log_unhandled_error():
    raise RuntimeError("structured log private internals")


def _json_messages(caplog):
    return [json.loads(record.message) for record in caplog.records]


def test_request_log_includes_request_context_without_sensitive_headers(client, caplog):
    caplog.set_level(logging.INFO, logger="app.observability")
    request_id = "trace-v24-structured"

    response = client.get(
        "/api/health",
        headers={
            REQUEST_ID_HEADER: request_id,
            "Cookie": "zhiyin_session=secret-session",
            "Authorization": "Bearer secret-token",
        },
    )

    assert response.status_code == 200
    request_logs = [
        item for item in _json_messages(caplog) if item.get("event") == "api_request"
    ]
    assert request_logs
    event = request_logs[-1]
    assert event["request_id"] == request_id
    assert event["method"] == "GET"
    assert event["path"] == "/api/health"
    assert event["path_template"] == "/api/health"
    assert event["status_code"] == 200
    assert "duration_ms" in event

    serialized = "\n".join(record.message for record in caplog.records)
    assert "secret-session" not in serialized
    assert "secret-token" not in serialized


def test_request_log_includes_authenticated_actor(client, caplog):
    login_as(client, "organizer.demo")
    caplog.clear()
    caplog.set_level(logging.INFO, logger="app.observability")

    response = client.get("/api/events")

    assert response.status_code == 200
    event = [item for item in _json_messages(caplog) if item.get("event") == "api_request"][-1]
    assert event["actor_role"] == "organizer"
    assert event["actor_user_id"] == "usr_org_demo"


def test_unhandled_exception_still_emits_request_log(caplog):
    from fastapi.testclient import TestClient

    caplog.set_level(logging.INFO, logger="app.observability")
    client = TestClient(app, raise_server_exceptions=False)
    request_id = "trace-v24-unhandled-log"

    response = client.get(
        "/__test/structured-log-unhandled-error",
        headers={REQUEST_ID_HEADER: request_id},
    )

    assert response.status_code == 500
    request_log = [
        item for item in _json_messages(caplog) if item.get("event") == "api_request"
    ][-1]
    assert request_log["request_id"] == request_id
    assert request_log["status_code"] == 500
    assert request_log["path_template"] == "/__test/structured-log-unhandled-error"


def test_log_event_redacts_sensitive_fields_and_local_paths(caplog):
    caplog.set_level(logging.INFO, logger="app.observability")

    log_event(
        "info",
        "probe",
        authorization="Bearer secret-token",
        cookie="zhiyin_session=secret-session",
        local_path=r"Q:\PrivateWorkspace\data\runtime\zhiyin.sqlite3",
        message=r"failed at Q:\PrivateWorkspace\data\runtime\zhiyin.sqlite3 with Bearer secret-token",
        note="token=secret-token",
        spaced_path=r"failed at Q:\Jane Doe\secret.txt with Bearer sk-secret",
        safe="visible",
    )

    event = _json_messages(caplog)[-1]
    assert event["authorization"] == "[redacted]"
    assert event["cookie"] == "[redacted]"
    assert event["local_path"] == "[redacted]"
    assert r"Q:\PrivateWorkspace" not in event["message"]
    assert "secret-token" not in event["message"]
    assert event["note"] == "token=[redacted]"
    assert "Jane Doe" not in event["spaced_path"]
    assert "secret.txt" not in event["spaced_path"]
    assert "sk-secret" not in event["spaced_path"]
    assert event["safe"] == "visible"
