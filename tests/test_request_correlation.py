import logging

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def _analyze_payload() -> dict:
    return {
        "previous_schema": [{"name": "id", "type": "int"}],
        "current_schema": [{"name": "id", "type": "int"}],
        "downstream_model_count": 1,
    }


def test_x_request_id_is_propagated_on_success():
    request_id = "req-12345"

    res = client.post("/analyze", json=_analyze_payload(), headers={"X-Request-ID": request_id})

    assert res.status_code == 200
    assert res.headers["X-Request-ID"] == request_id


def test_request_id_generated_and_returned_on_error():
    res = client.post(
        "/roi-estimate",
        json={
            "incidents_per_month": 10,
            "mean_time_to_detect_hours": 2,
            "mean_time_to_resolve_hours": 4,
            "engineers_involved_per_incident": 2,
            "hourly_engineering_cost_usd": 100,
            "driftshield_adoption_rate": 9.9,
        },
    )

    body = res.json()
    assert res.status_code == 422
    assert isinstance(body["request_id"], str)
    assert len(body["request_id"]) > 0
    assert res.headers["X-Request-ID"] == body["request_id"]


def test_audit_log_contains_method_path_status_and_request_id(caplog):
    request_id = "audit-req-1"
    caplog.set_level(logging.INFO, logger="driftshield.audit")

    res = client.post("/analyze", json=_analyze_payload(), headers={"X-Request-ID": request_id})

    assert res.status_code == 200
    messages = [record.getMessage() for record in caplog.records if record.name == "driftshield.audit"]
    assert any(
        "method=POST path=/analyze status=200 request_id=audit-req-1" in msg
        for msg in messages
    )
