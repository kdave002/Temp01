from fastapi.testclient import TestClient

from backend.app.main import app, _rate_limit_buckets


client = TestClient(app)


def _valid_payload() -> dict:
    return {
        "previous_schema": [{"name": "id", "type": "int"}],
        "current_schema": [{"name": "id", "type": "int"}],
        "downstream_model_count": 1,
    }


def test_analyze_rate_limit_enforced(monkeypatch):
    _rate_limit_buckets.clear()
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "2")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")

    payload = _valid_payload()

    first = client.post("/analyze", json=payload)
    second = client.post("/analyze", json=payload)
    third = client.post("/analyze", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429

    body = third.json()
    assert body["detail"] == "rate limit exceeded"
    assert isinstance(body["request_id"], str)


def test_get_health_not_rate_limited(monkeypatch):
    _rate_limit_buckets.clear()
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "1")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")

    for _ in range(3):
        res = client.get("/health")
        assert res.status_code == 200
