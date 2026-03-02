from backend.app.decision import recommend_action
from backend.app.models import DriftEvent


def test_recommend_manual_for_high_risk():
    action, reasons = recommend_action(
        "high",
        {"overall": "needs_review"},
        80,
        [DriftEvent(kind="removed", detail="x", severity="high")],
    )
    assert action == "manual_approval_required"
    assert len(reasons) >= 1


def test_recommend_auto_merge_for_low_risk_clean_validation():
    action, _ = recommend_action(
        "low",
        {"overall": "pass"},
        10,
        [DriftEvent(kind="added", detail="x", severity="low")],
    )
    assert action == "auto_merge_candidate"
