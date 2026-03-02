from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def _valid_payload() -> dict:
    return {
        "previous_schema": [{"name": "id", "type": "int"}],
        "current_schema": [{"name": "id", "type": "int"}],
        "downstream_model_count": 1,
    }


def test_analyze_invalid_payload_has_safe_error_shape():
    res = client.post(
        "/analyze",
        json={
            "previous_schema": [{"name": "id", "type": "int"}],
            "current_schema": [{"name": "id", "type": "int"}],
            "downstream_model_count": "oops",
        },
    )

    body = res.json()
    assert res.status_code == 422
    assert body["detail"] == "invalid request payload"
    assert isinstance(body["errors"], list)
    assert isinstance(body["request_id"], str)


def test_analyze_enforces_model_level_downstream_upper_bound():
    payload = _valid_payload()
    payload["downstream_model_count"] = 10001

    res = client.post("/analyze", json=payload)

    body = res.json()
    assert res.status_code == 422
    assert body["detail"] == "invalid request payload"
    assert isinstance(body["errors"], list)
    assert isinstance(body["request_id"], str)


def test_pr_create_invalid_payload_has_safe_error_shape(monkeypatch):
    monkeypatch.setenv("GITHUB_OWNER", "acme")
    monkeypatch.setenv("GITHUB_REPO", "driftshield")

    res = client.post(
        "/pr-create",
        json={
            "previous_schema": [{"name": "id", "type": "int"}],
            "current_schema": [{"name": "id", "type": "int"}],
            "downstream_model_count": "oops",
        },
    )

    body = res.json()
    assert res.status_code == 422
    assert body["detail"] == "invalid request payload"
    assert isinstance(body["errors"], list)
    assert isinstance(body["request_id"], str)


def test_pr_create_rejects_total_schema_size_for_endpoint(monkeypatch):
    monkeypatch.setenv("GITHUB_OWNER", "acme")
    monkeypatch.setenv("GITHUB_REPO", "driftshield")

    prev = [{"name": f"a_{i}", "type": "int"} for i in range(301)]
    curr = [{"name": f"b_{i}", "type": "int"} for i in range(300)]

    res = client.post(
        "/pr-create",
        json={"previous_schema": prev, "current_schema": curr, "downstream_model_count": 1},
    )

    assert res.status_code == 422
    body = res.json()
    assert body["detail"] == "schema input too large for PR endpoints"
    assert isinstance(body["request_id"], str)


def test_pr_create_rejects_endpoint_level_downstream_threshold(monkeypatch):
    monkeypatch.setenv("GITHUB_OWNER", "acme")
    monkeypatch.setenv("GITHUB_REPO", "driftshield")

    payload = _valid_payload()
    payload["downstream_model_count"] = 5001

    res = client.post("/pr-create", json=payload)

    assert res.status_code == 422
    body = res.json()
    assert body["detail"] == "downstream_model_count too high for PR endpoints"
    assert isinstance(body["request_id"], str)
