from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_simulate_returns_concise_report_for_breaking_change():
    payload = {
        "previous_schema": [{"name": "amount", "type": "int"}],
        "current_schema": [{"name": "amount", "type": "string"}],
        "downstream_model_count": 8,
    }

    res = client.post("/simulate", json=payload)

    assert res.status_code == 200
    body = res.json()
    assert body["predicted_breakage_class"] == "likely_breaking"
    assert body["expected_repair_path"] in {
        "open PR + data-owner review",
        "manual approval + staged rollout",
    }
    assert body["confidence_band"] in {"low", "medium", "high"}
    assert body["confidence_range"]["min"] <= body["confidence_range"]["max"]
    assert "impact" in body["summary"]


def test_simulate_uses_optional_metric_baselines():
    payload = {
        "previous_schema": [{"name": "id", "type": "int"}],
        "current_schema": [{"name": "id", "type": "int"}],
        "metric_baselines": {
            "incidents_per_month": 12,
            "mean_time_to_detect_hours": 2.5,
            "mean_time_to_resolve_hours": 4.0,
        },
    }

    res = client.post("/simulate", json=payload)

    assert res.status_code == 200
    body = res.json()
    assert body["predicted_breakage_class"] == "non_breaking"
    assert body["expected_repair_path"] == "auto patch + lightweight review"
    assert body["confidence_band"] in {"medium", "high"}


def test_simulate_invalid_payload_has_safe_error_shape():
    payload = {
        "previous_schema": [{"name": "id", "type": "int"}],
        "current_schema": [{"name": "id", "type": "int"}],
        "metric_baselines": {"mean_time_to_detect_hours": -1},
    }

    res = client.post("/simulate", json=payload)

    assert res.status_code == 422
    body = res.json()
    assert body["detail"] == "invalid request payload"
    assert isinstance(body["errors"], list)
    assert isinstance(body["request_id"], str)
    assert res.headers["X-Request-ID"] == body["request_id"]


def test_simulate_rejects_empty_schema_input():
    res = client.post("/simulate", json={"previous_schema": [], "current_schema": []})

    assert res.status_code == 422
    body = res.json()
    assert body["detail"] == "schema input cannot be empty"
    assert isinstance(body["request_id"], str)
    assert res.headers["X-Request-ID"] == body["request_id"]


def test_simulate_rejects_endpoint_level_downstream_threshold():
    payload = {
        "previous_schema": [{"name": "id", "type": "int"}],
        "current_schema": [{"name": "id", "type": "int"}],
        "downstream_model_count": 5001,
    }

    res = client.post("/simulate", json=payload)

    assert res.status_code == 422
    body = res.json()
    assert body["detail"] == "downstream_model_count too high for simulation endpoint"
    assert isinstance(body["request_id"], str)
