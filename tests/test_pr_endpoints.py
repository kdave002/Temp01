from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def _valid_payload() -> dict:
    return {
        "previous_schema": [{"name": "id", "type": "int"}],
        "current_schema": [{"name": "id", "type": "int"}],
        "downstream_model_count": 1,
    }


def test_pr_preview_requires_repo_configuration(monkeypatch):
    monkeypatch.delenv("GITHUB_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_REPO", raising=False)

    res = client.post("/pr-preview", json=_valid_payload())

    assert res.status_code == 503
    assert res.json() == {"detail": "PR integration is not configured"}


def test_pr_preview_rejects_empty_schema(monkeypatch):
    monkeypatch.setenv("GITHUB_OWNER", "acme")
    monkeypatch.setenv("GITHUB_REPO", "driftshield")

    res = client.post(
        "/pr-preview",
        json={"previous_schema": [], "current_schema": [], "downstream_model_count": 1},
    )

    assert res.status_code == 422
    assert res.json() == {"detail": "schema input cannot be empty"}


def test_pr_preview_rejects_total_schema_size_for_endpoint(monkeypatch):
    monkeypatch.setenv("GITHUB_OWNER", "acme")
    monkeypatch.setenv("GITHUB_REPO", "driftshield")

    prev = [{"name": f"a_{i}", "type": "int"} for i in range(301)]
    curr = [{"name": f"b_{i}", "type": "int"} for i in range(300)]
    res = client.post(
        "/pr-preview",
        json={"previous_schema": prev, "current_schema": curr, "downstream_model_count": 1},
    )

    assert res.status_code == 422
    assert res.json() == {"detail": "schema input too large for PR endpoints"}


def test_pr_preview_rejects_endpoint_level_downstream_threshold(monkeypatch):
    monkeypatch.setenv("GITHUB_OWNER", "acme")
    monkeypatch.setenv("GITHUB_REPO", "driftshield")

    payload = _valid_payload()
    payload["downstream_model_count"] = 5001

    res = client.post("/pr-preview", json=payload)

    assert res.status_code == 422
    assert res.json() == {"detail": "downstream_model_count too high for PR endpoints"}


def test_pr_preview_bad_payload_has_safe_error_shape(monkeypatch):
    monkeypatch.setenv("GITHUB_OWNER", "acme")
    monkeypatch.setenv("GITHUB_REPO", "driftshield")

    res = client.post(
        "/pr-preview",
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


def test_pr_create_requires_repo_configuration(monkeypatch):
    monkeypatch.delenv("GITHUB_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_REPO", raising=False)

    res = client.post("/pr-create", json=_valid_payload())

    assert res.status_code == 503
    assert res.json() == {"detail": "PR integration is not configured"}


def test_pr_create_returns_dry_run_when_token_missing(monkeypatch):
    monkeypatch.setenv("GITHUB_OWNER", "acme")
    monkeypatch.setenv("GITHUB_REPO", "driftshield")
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    res = client.post("/pr-create", json=_valid_payload())

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "dry_run"
    assert body["missing"] == ["GITHUB_TOKEN"]
    assert "pr_payload" in body
