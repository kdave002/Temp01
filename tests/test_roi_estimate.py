from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_roi_estimate_returns_projected_savings():
    payload = {
        "incidents_per_month": 10,
        "mean_time_to_detect_hours": 2,
        "mean_time_to_resolve_hours": 4,
        "engineers_involved_per_incident": 2,
        "hourly_engineering_cost_usd": 100,
        "driftshield_adoption_rate": 1.0,
    }

    res = client.post("/roi-estimate", json=payload)

    assert res.status_code == 200
    body = res.json()
    assert body["baseline_monthly_engineering_hours"] == 120.0
    assert body["baseline_monthly_cost_usd"] == 12000.0
    assert body["projected_monthly_engineering_hours"] == 59.2
    assert body["projected_monthly_cost_usd"] == 5920.0
    assert body["monthly_engineering_hours_saved"] == 60.8
    assert body["monthly_cost_saved_usd"] == 6080.0
    assert body["annual_cost_saved_usd"] == 72960.0
    assert body["monthly_cost_savings_percent"] == 50.67
    assert body["assumptions"]["incident_reduction_rate"] == 0.2


def test_roi_estimate_zero_adoption_means_no_savings():
    payload = {
        "incidents_per_month": 12,
        "mean_time_to_detect_hours": 1,
        "mean_time_to_resolve_hours": 2,
        "engineers_involved_per_incident": 1,
        "hourly_engineering_cost_usd": 150,
        "driftshield_adoption_rate": 0.0,
    }

    res = client.post("/roi-estimate", json=payload)

    assert res.status_code == 200
    body = res.json()
    assert body["monthly_cost_saved_usd"] == 0.0
    assert body["annual_cost_saved_usd"] == 0.0
    assert body["monthly_cost_savings_percent"] == 0.0


def test_roi_estimate_invalid_payload_has_safe_error_shape():
    payload = {
        "incidents_per_month": 10,
        "mean_time_to_detect_hours": 2,
        "mean_time_to_resolve_hours": 4,
        "engineers_involved_per_incident": 2,
        "hourly_engineering_cost_usd": 100,
        "driftshield_adoption_rate": 1.2,
    }

    res = client.post("/roi-estimate", json=payload)

    body = res.json()
    assert res.status_code == 422
    assert body["detail"] == "invalid request payload"
    assert isinstance(body["errors"], list)
    assert isinstance(body["request_id"], str)
    assert res.headers["X-Request-ID"] == body["request_id"]
