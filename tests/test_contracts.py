from backend.app.contracts import evaluate_contract
from backend.app.models import Column


def test_contract_compatible_when_only_additions():
    prev = [Column(name="id", type="int")]
    curr = [Column(name="id", type="int"), Column(name="new_col", type="string")]
    result = evaluate_contract(prev, curr)
    assert result.compatible is True
    assert result.breaking_reasons == []


def test_contract_breaks_on_removed_or_type_change():
    prev = [Column(name="id", type="int"), Column(name="amount", type="int")]
    curr = [Column(name="id", type="string")]
    result = evaluate_contract(prev, curr)
    assert result.compatible is False
    assert any(r.startswith("removed:amount") for r in result.breaking_reasons)
    assert any(r.startswith("type_changed:id") for r in result.breaking_reasons)
