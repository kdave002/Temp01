from backend.app.drift import detect_drift
from backend.app.models import Column


def test_detect_drift_type_change_and_addition():
    prev = [Column(name="id", type="int"), Column(name="amount", type="int")]
    curr = [Column(name="id", type="int"), Column(name="amount", type="float"), Column(name="currency", type="string")]

    events = detect_drift(prev, curr)
    kinds = sorted([e.kind for e in events])
    assert kinds == ["added", "type_changed"]
