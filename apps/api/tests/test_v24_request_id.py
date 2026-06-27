from fastapi import Request

from app.main import app
from app.observability import REQUEST_ID_HEADER


@app.get("/__test/request-id-state")
def request_id_state(request: Request):
    return {"request_id": request.state.request_id}


def test_generated_request_id_is_added_to_response(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    request_id = response.headers[REQUEST_ID_HEADER]
    assert request_id


def test_safe_request_id_is_reused_and_stored_on_request_state(client):
    request_id = "client-request_123.abc:trace"

    response = client.get(
        "/__test/request-id-state",
        headers={REQUEST_ID_HEADER: request_id},
    )

    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER] == request_id
    assert response.json()["request_id"] == request_id


def test_unsafe_long_request_id_is_replaced(client):
    unsafe_request_id = "x" * 129

    response = client.get(
        "/api/health",
        headers={REQUEST_ID_HEADER: unsafe_request_id},
    )

    assert response.status_code == 200
    replacement = response.headers[REQUEST_ID_HEADER]
    assert replacement
    assert replacement != unsafe_request_id
    assert len(replacement) <= 128
