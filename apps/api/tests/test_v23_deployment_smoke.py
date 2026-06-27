import io
import json

from scripts import deployment_smoke
from scripts.deployment_smoke import SmokeResponse


def _fake_request(responses):
    def request(_base_url: str, path: str) -> SmokeResponse:
        response = responses[path]
        if isinstance(response, Exception):
            raise response
        return response

    return request


def _success_responses():
    return {
        "/api/health": SmokeResponse(200, {"status": "ok", "secret": "gho_should_not_print"}),
        "/api/ready": SmokeResponse(200, {"status": "ready", "APP_SECRET_KEY": "hidden"}),
        "/api/public/events/demo-night-tour": SmokeResponse(200, {"event_id": "demo-night-tour"}),
    }


def test_deployment_smoke_success_returns_zero_and_summarizes_endpoints():
    output = io.StringIO()

    exit_code = deployment_smoke.run_smoke(
        "http://api.example",
        request=_fake_request(_success_responses()),
        output=output,
    )

    assert exit_code == 0
    lines = [json.loads(line) for line in output.getvalue().splitlines()]
    assert [line["endpoint"] for line in lines] == ["health", "ready", "public_event"]
    assert all(line["ok"] for line in lines)
    assert "gho_should_not_print" not in output.getvalue()
    assert "APP_SECRET_KEY" not in output.getvalue()


def test_deployment_smoke_health_failure_returns_nonzero():
    responses = _success_responses()
    responses["/api/health"] = SmokeResponse(503, {"detail": "unavailable"})

    assert deployment_smoke.run_smoke(
        "http://api.example",
        request=_fake_request(responses),
        output=io.StringIO(),
    ) == 1


def test_deployment_smoke_ready_failure_returns_nonzero():
    responses = _success_responses()
    responses["/api/ready"] = SmokeResponse(503, {"status": "not_ready"})

    assert deployment_smoke.run_smoke(
        "http://api.example",
        request=_fake_request(responses),
        output=io.StringIO(),
    ) == 1


def test_deployment_smoke_ready_not_ready_payload_returns_nonzero():
    responses = _success_responses()
    responses["/api/ready"] = SmokeResponse(200, {"status": "not_ready"})

    assert deployment_smoke.run_smoke(
        "http://api.example",
        request=_fake_request(responses),
        output=io.StringIO(),
    ) == 1


def test_deployment_smoke_public_event_failure_returns_nonzero():
    responses = _success_responses()
    responses["/api/public/events/demo-night-tour"] = SmokeResponse(404, {"detail": "not found"})

    assert deployment_smoke.run_smoke(
        "http://api.example",
        request=_fake_request(responses),
        output=io.StringIO(),
    ) == 1


def test_deployment_smoke_request_error_returns_nonzero_and_redacted_summary():
    responses = _success_responses()
    responses["/api/ready"] = RuntimeError("boom secret-token")
    output = io.StringIO()

    exit_code = deployment_smoke.run_smoke(
        "http://api.example",
        request=_fake_request(responses),
        output=output,
    )

    assert exit_code == 1
    assert "RuntimeError" in output.getvalue()
    assert "secret-token" not in output.getvalue()
