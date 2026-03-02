from fastapi.testclient import TestClient
import pytest

from backend.app.main import app, _cleanup_rate_limit_buckets, _rate_limit_buckets


client = TestClient(app)


def _valid_payload() -> dict:
    return {
        "previous_schema": [{"name": "id", "type": "int"}],
        "current_schema": [{"name": "id", "type": "int"}],
        "downstream_model_count": 1,
    }


def _valid_roi_payload() -> dict:
    return {
        "incidents_per_month": 10,
        "mean_time_to_detect_hours": 2,
        "mean_time_to_resolve_hours": 4,
        "engineers_involved_per_incident": 2,
        "hourly_engineering_cost_usd": 100,
        "driftshield_adoption_rate": 0.75,
    }


def _valid_pilot_payload() -> dict:
    return {
        "data_owner_identified": True,
        "repo_access_configured": True,
        "ci_green": True,
        "rollback_plan_defined": True,
        "oncall_contact_set": True,
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

    assert first.headers["X-RateLimit-Limit"] == "2"
    assert first.headers["X-RateLimit-Remaining"] == "1"
    assert 1 <= int(first.headers["X-RateLimit-Reset"]) <= 60

    assert second.headers["X-RateLimit-Limit"] == "2"
    assert second.headers["X-RateLimit-Remaining"] == "0"
    assert 1 <= int(second.headers["X-RateLimit-Reset"]) <= 60

    body = third.json()
    assert body["detail"] == "rate limit exceeded"
    assert isinstance(body["request_id"], str)
    retry_after = int(third.headers["Retry-After"])
    assert 1 <= retry_after <= 60
    assert third.headers["X-RateLimit-Limit"] == "2"
    assert third.headers["X-RateLimit-Remaining"] == "0"
    assert 1 <= int(third.headers["X-RateLimit-Reset"]) <= 60


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("/simulate", _valid_payload()),
        ("/roi-estimate", _valid_roi_payload()),
        ("/pilot-readiness", _valid_pilot_payload()),
    ],
)
def test_additional_protected_post_endpoints_rate_limited(monkeypatch, path, payload):
    _rate_limit_buckets.clear()
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "1")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")

    first = client.post(path, json=payload)
    second = client.post(path, json=payload)

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["detail"] == "rate limit exceeded"


def test_get_health_not_rate_limited(monkeypatch):
    _rate_limit_buckets.clear()
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "1")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")

    for _ in range(3):
        res = client.get("/health")
        assert res.status_code == 200
        assert "X-RateLimit-Limit" not in res.headers


def test_cleanup_rate_limit_buckets_removes_stale_entries():
    _rate_limit_buckets.clear()
    _rate_limit_buckets[("/analyze", "active-client")].append(100.0)
    _rate_limit_buckets[("/simulate", "stale-client")].append(1.0)

    _cleanup_rate_limit_buckets(now=200.0, window_seconds=60)

    assert ("/analyze", "active-client") in _rate_limit_buckets
    assert ("/simulate", "stale-client") not in _rate_limit_buckets
