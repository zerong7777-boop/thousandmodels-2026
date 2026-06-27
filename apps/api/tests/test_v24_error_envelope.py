from fastapi.testclient import TestClient

from app.main import app
from app.observability import REQUEST_ID_HEADER


@app.get("/__test/unhandled-error")
def unhandled_error():
    raise RuntimeError("boom with private internals")


def test_http_exception_uses_error_envelope_and_request_id(client):
    request_id = "trace-http-404"

    response = client.get(
        "/api/public/events/missing-event",
        headers={REQUEST_ID_HEADER: request_id},
    )

    assert response.status_code == 404
    assert response.headers[REQUEST_ID_HEADER] == request_id
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"] == {
        "code": "http_404",
        "message": "plan not found",
        "request_id": request_id,
    }


def test_unhandled_exception_uses_safe_error_envelope_and_request_id():
    client = TestClient(app, raise_server_exceptions=False)
    request_id = "trace-unhandled-500"

    response = client.get(
        "/__test/unhandled-error",
        headers={REQUEST_ID_HEADER: request_id},
    )

    assert response.status_code == 500
    assert response.headers[REQUEST_ID_HEADER] == request_id
    body = response.json()
    assert body["error"] == {
        "code": "internal_server_error",
        "message": "internal server error",
        "request_id": request_id,
    }
    assert "boom" not in response.text
