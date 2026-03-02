from .models import DriftEvent


def recommend_action(risk: str, validation: dict, impact_score: int, events: list[DriftEvent]) -> tuple[str, list[str]]:
    reasons: list[str] = []

    if validation.get("overall") != "pass":
        reasons.append("Validation checks require manual review before merge.")

    breaking_kinds = {"removed", "type_changed"}
    breaking = [e for e in events if e.kind in breaking_kinds]
    if breaking:
        reasons.append(f"Detected {len(breaking)} potentially breaking drift event(s).")

    if risk == "high" or impact_score >= 70:
        return "manual_approval_required", reasons or ["High-risk drift requires approval."]

    if risk == "medium":
        return "open_pr_and_request_review", reasons or ["Medium risk should be reviewed by data owner."]

    return "auto_merge_candidate", reasons or ["Low risk and validation passed."]
