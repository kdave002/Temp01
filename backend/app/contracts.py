from dataclasses import dataclass
from .models import Column


@dataclass
class ContractCompatibility:
    compatible: bool
    breaking_reasons: list[str]


def evaluate_contract(previous_schema: list[Column], current_schema: list[Column]) -> ContractCompatibility:
    prev = {c.name: c.type for c in previous_schema}
    curr = {c.name: c.type for c in current_schema}

    reasons: list[str] = []

    removed = sorted(set(prev) - set(curr))
    for col in removed:
        reasons.append(f"removed:{col}")

    for col in sorted(set(prev) & set(curr)):
        if prev[col] != curr[col]:
            reasons.append(f"type_changed:{col}:{prev[col]}->{curr[col]}")

    compatible = len(reasons) == 0
    return ContractCompatibility(compatible=compatible, breaking_reasons=reasons)
