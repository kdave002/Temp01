from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_pilot_readiness_ready():
    payload = {
        "data_owner_identified": True,
        "repo_access_configured": True,
        "ci_green": True,
        "rollback_plan_defined": True,
        "oncall_contact_set": True,
    }

    response = client.post("/pilot-readiness", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["readiness_score"] == 100
    assert body["status"] == "ready"
    assert body["missing_items"] == []


def test_pilot_readiness_ready_with_risks():
    payload = {
        "data_owner_identified": True,
        "repo_access_configured": True,
        "ci_green": False,
        "rollback_plan_defined": True,
        "oncall_contact_set": False,
    }

    response = client.post("/pilot-readiness", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["readiness_score"] == 60
    assert body["status"] == "ready_with_risks"
    assert set(body["missing_items"]) == {"ci_green", "oncall_contact_set"}


def test_pilot_readiness_not_ready():
    payload = {
        "data_owner_identified": False,
        "repo_access_configured": False,
        "ci_green": False,
        "rollback_plan_defined": True,
        "oncall_contact_set": False,
    }

    response = client.post("/pilot-readiness", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["readiness_score"] == 20
    assert body["status"] == "not_ready"
