from backend.app.drift import build_patch, compute_impact, detect_drift
from backend.app.models import Column


def test_detect_drift_type_change_and_addition():
    prev = [Column(name="id", type="int"), Column(name="amount", type="int")]
    curr = [
        Column(name="id", type="int"),
        Column(name="amount", type="float"),
        Column(name="currency", type="string"),
    ]

    events = detect_drift(prev, curr)
    kinds = sorted([e.kind for e in events])
    assert kinds == ["added", "type_changed"]


def test_detects_rename_candidate_with_confidence():
    prev = [Column(name="customer_id", type="string")]
    curr = [Column(name="client_id", type="string")]

    events = detect_drift(prev, curr)
    assert len(events) == 1
    assert events[0].kind == "renamed_candidate"
    assert events[0].confidence is not None


def test_impact_score_high_when_many_breaking_events():
    prev = [Column(name="a", type="int"), Column(name="b", type="int")]
    curr = [Column(name="a", type="string"), Column(name="c", type="int")]
    events = detect_drift(prev, curr)

    score, risk = compute_impact(events, downstream_model_count=10)
    assert score >= 70
    assert risk == "high"


def test_build_patch_infers_rename_projection():
    prev = [Column(name="customer_id", type="string")]
    curr = [Column(name="client_id", type="string")]

    events = detect_drift(prev, curr)
    patch = build_patch(events, prev, curr)

    assert "customer_id AS client_id" in patch
    assert "select * from patched" in patch


def test_build_patch_adds_safe_cast_for_type_changes():
    prev = [Column(name="amount", type="int")]
    curr = [Column(name="amount", type="float")]

    events = detect_drift(prev, curr)
    patch = build_patch(events, prev, curr)

    assert "SAFE_CAST(amount AS FLOAT64) AS amount" in patch
