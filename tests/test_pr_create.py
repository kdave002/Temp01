import json
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def _sample_request() -> dict:
    return {
        "previous_schema": [{"name": "customer_id", "type": "string"}],
        "current_schema": [{"name": "client_id", "type": "string"}],
        "downstream_model_count": 3,
    }


def test_pr_create_returns_dry_run_when_token_missing(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("GITHUB_OWNER", "octocat")
    monkeypatch.setenv("GITHUB_REPO", "hello-world")

    response = client.post("/pr-create", json=_sample_request())

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "dry_run"
    assert body["dry_run"] is True
    assert body["missing"] == ["GITHUB_TOKEN"]
    assert "pr_payload" in body


def test_pr_create_posts_to_github_when_configured(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("GITHUB_OWNER", "octocat")
    monkeypatch.setenv("GITHUB_REPO", "hello-world")
    monkeypatch.setenv("GITHUB_HEAD_BRANCH", "driftshield/auto-fix")

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({"html_url": "https://github.com/octocat/hello-world/pull/42", "number": 42}).encode("utf-8")

    with patch("backend.app.github_client.urlopen", return_value=_Resp()):
        response = client.post("/pr-create", json=_sample_request())

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "created"
    assert body["dry_run"] is False
    assert body["pull_request_url"].endswith("/pull/42")
    assert body["pull_request_number"] == 42


def test_pr_create_returns_504_on_timeout(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("GITHUB_OWNER", "octocat")
    monkeypatch.setenv("GITHUB_REPO", "hello-world")

    with patch("backend.app.github_client.urlopen", side_effect=TimeoutError("boom")):
        response = client.post("/pr-create", json=_sample_request())

    assert response.status_code == 504
    assert "timed out" in response.json()["detail"].lower()
