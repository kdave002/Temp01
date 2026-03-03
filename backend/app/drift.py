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


def _parse_rename_detail(detail: str) -> tuple[str | None, str | None]:
    if "->" not in detail:
        return None, None
    old, new = detail.split("->", 1)
    old_name = old.strip()
    new_name = new.strip()
    if not old_name or not new_name:
        return None, None
    return old_name, new_name


def _bq_type(column_type: str) -> str:
    normalized = column_type.strip().lower()
    mapping = {
        "int": "INT64",
        "integer": "INT64",
        "bigint": "INT64",
        "smallint": "INT64",
        "float": "FLOAT64",
        "double": "FLOAT64",
        "number": "NUMERIC",
        "decimal": "NUMERIC",
        "bool": "BOOL",
        "boolean": "BOOL",
        "str": "STRING",
        "varchar": "STRING",
        "text": "STRING",
    }
    return mapping.get(normalized, column_type.upper())


def _type_change_targets(events: list[DriftEvent]) -> set[str]:
    targets: set[str] = set()
    for event in events:
        if event.kind != "type_changed" or ":" not in event.detail:
            continue
        name = event.detail.split(":", 1)[0].strip()
        if name:
            targets.add(name)
    return targets


def build_patch(
    events: list[DriftEvent],
    previous_schema: list[Column] | None = None,
    current_schema: list[Column] | None = None,
) -> str:
    if not events:
        return "-- no drift detected"

    lines = ["-- Auto-generated draft patch"]
    for event in events:
        conf = f" (confidence={event.confidence})" if event.confidence is not None else ""
        lines.append(f"-- [{event.severity}] {event.kind}: {event.detail}{conf}")

    if previous_schema is None or current_schema is None:
        lines.extend(
            [
                "with source as (",
                "  select * from source_table",
                ")",
                "select * from source;",
            ]
        )
        return "\n".join(lines)

    prev_types = {c.name: c.type for c in previous_schema}
    curr_types = {c.name: c.type for c in current_schema}

    rename_map: dict[str, str] = {}
    for event in events:
        if event.kind != "renamed_candidate":
            continue
        old_name, new_name = _parse_rename_detail(event.detail)
        if old_name and new_name:
            rename_map[new_name] = old_name

    type_change_targets = _type_change_targets(events)

    select_lines: list[str] = []
    for col in current_schema:
        target_name = col.name
        source_name = rename_map.get(target_name, target_name)

        needs_cast = (
            target_name in type_change_targets
            or (source_name in prev_types and prev_types[source_name] != curr_types.get(target_name, col.type))
        )

        if needs_cast:
            target_type = _bq_type(curr_types.get(target_name, col.type))
            expr = f"SAFE_CAST({source_name} AS {target_type}) AS {target_name}"
        else:
            expr = f"{source_name} AS {target_name}" if source_name != target_name else target_name

        select_lines.append(f"  {expr}")

    if not select_lines:
        select_lines = ["  *"]

    lines.extend(
        [
            "with source as (",
            "  select * from source_table",
            "),",
            "patched as (",
            "select",
            ",\n".join(select_lines),
            "from source",
            ")",
            "select * from patched;",
        ]
    )

    return "\n".join(lines)
