from backend.app.github_payload import build_pr_payload
from backend.app.models import DriftResponse
from backend.app.config import Settings


def test_build_pr_payload_marks_draft_when_not_auto_merge():
    response = DriftResponse(
        events=[],
        impact_score=80,
        risk="high",
        patch_sql="select 1;",
        validation={"overall": "needs_review", "passed": 1, "failed": 1},
        pr_body="body",
        action_recommendation="manual_approval_required",
        recommendation_reasons=["reason"],
    )
    settings = Settings(github_owner="kdave002", github_repo="Temp01")
    payload = build_pr_payload(response, settings)

    assert payload["draft"] is True
    assert payload["owner"] == "kdave002"
    assert payload["repo"] == "Temp01"
    assert "risk:high" in payload["labels"]
