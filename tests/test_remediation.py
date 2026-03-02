from backend.app.models import DriftEvent
from backend.app.remediation import validate_patch, build_pr_body


def test_validate_patch_requires_review_on_high_severity():
    events = [DriftEvent(kind="removed", detail="Column removed: amount", severity="high")]
    report = validate_patch(events)
    assert report["overall"] == "needs_review"
    assert report["failed"] >= 1


def test_build_pr_body_contains_risk_and_patch():
    events = [DriftEvent(kind="added", detail="Column added: currency", severity="medium")]
    validation = validate_patch(events)
    body = build_pr_body(events, impact_score=40, risk="medium", patch_sql="select 1;", validation=validation)
    assert "Impact score" in body
    assert "```sql" in body
    assert "currency" in body
