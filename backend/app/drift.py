from difflib import SequenceMatcher
from .models import Column, DriftEvent


def _similarity(a: str, b: str) -> float:
    a_l = a.lower()
    b_l = b.lower()
    raw = SequenceMatcher(None, a_l, b_l).ratio()

    # Lightweight token/synonym boost for common business naming shifts.
    alias = {
        "customer": "client",
        "client": "customer",
        "amount": "total",
        "total": "amount",
    }
    a_tokens = a_l.split("_")
    b_tokens = b_l.split("_")
    overlap = len(set(a_tokens) & set(b_tokens)) / max(1, len(set(a_tokens) | set(b_tokens)))

    boosted_tokens = [alias.get(t, t) for t in a_tokens]
    alias_overlap = len(set(boosted_tokens) & set(b_tokens)) / max(1, len(set(boosted_tokens) | set(b_tokens)))

    return max(raw, overlap, alias_overlap)


def _candidate_renames(removed: set[str], added: set[str], prev: dict[str, str], curr: dict[str, str]) -> list[tuple[str, str, float]]:
    pairs: list[tuple[str, str, float]] = []
    used_added: set[str] = set()

    for old_name in sorted(removed):
        best_name = None
        best_score = 0.0
        for new_name in sorted(added - used_added):
            name_score = _similarity(old_name, new_name)
            type_bonus = 0.1 if prev.get(old_name) == curr.get(new_name) else 0.0
            score = min(1.0, name_score + type_bonus)
            if score > best_score:
                best_score = score
                best_name = new_name

        if best_name and best_score >= 0.62:
            pairs.append((old_name, best_name, round(best_score, 2)))
            used_added.add(best_name)

    return pairs


def detect_drift(previous_schema: list[Column], current_schema: list[Column]) -> list[DriftEvent]:
    prev = {c.name: c.type for c in previous_schema}
    curr = {c.name: c.type for c in current_schema}

    prev_names = set(prev.keys())
    curr_names = set(curr.keys())
    removed = prev_names - curr_names
    added = curr_names - prev_names

    events: list[DriftEvent] = []

    rename_pairs = _candidate_renames(removed, added, prev, curr)
    renamed_old = {old for old, _, _ in rename_pairs}
    renamed_new = {new for _, new, _ in rename_pairs}

    for old_name, new_name, conf in rename_pairs:
        events.append(
            DriftEvent(
                kind="renamed_candidate",
                detail=f"{old_name} -> {new_name}",
                severity="high",
                confidence=conf,
            )
        )

    for name in sorted(removed - renamed_old):
        events.append(DriftEvent(kind="removed", detail=f"Column removed: {name}", severity="high"))

    for name in sorted(added - renamed_new):
        events.append(DriftEvent(kind="added", detail=f"Column added: {name}", severity="medium"))

    for name in sorted(prev_names & curr_names):
        if prev[name] != curr[name]:
            events.append(
                DriftEvent(
                    kind="type_changed",
                    detail=f"{name}: {prev[name]} -> {curr[name]}",
                    severity="high",
                )
            )

    return events


def compute_impact(events: list[DriftEvent], downstream_model_count: int) -> tuple[int, str]:
    weights = {"removed": 35, "renamed_candidate": 30, "type_changed": 30, "added": 10}
    score = sum(weights.get(e.kind, 5) for e in events) + min(25, downstream_model_count * 2)
    score = min(100, score)

    if score >= 70:
        risk = "high"
    elif score >= 35:
        risk = "medium"
    else:
        risk = "low"
    return score, risk


def build_patch(events: list[DriftEvent]) -> str:
    if not events:
        return "-- no drift detected"

    lines = ["-- Auto-generated draft patch"]
    for event in events:
        conf = f" (confidence={event.confidence})" if event.confidence is not None else ""
        lines.append(f"-- [{event.severity}] {event.kind}: {event.detail}{conf}")

    lines.extend(
        [
            "with source as (",
            "  select * from source_table",
            ")",
            "select * from source;",
        ]
    )
    return "\n".join(lines)
