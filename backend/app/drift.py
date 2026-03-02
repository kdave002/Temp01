from .models import Column, DriftEvent


def detect_drift(previous_schema: list[Column], current_schema: list[Column]) -> list[DriftEvent]:
    prev = {c.name: c.type for c in previous_schema}
    curr = {c.name: c.type for c in current_schema}

    events: list[DriftEvent] = []

    for name in sorted(prev.keys() - curr.keys()):
        events.append(DriftEvent(kind="removed", detail=f"Column removed: {name}"))

    for name in sorted(curr.keys() - prev.keys()):
        events.append(DriftEvent(kind="added", detail=f"Column added: {name}"))

    for name in sorted(prev.keys() & curr.keys()):
        if prev[name] != curr[name]:
            events.append(
                DriftEvent(kind="type_changed", detail=f"{name}: {prev[name]} -> {curr[name]}")
            )

    return events


def build_patch(events: list[DriftEvent]) -> str:
    if not events:
        return "-- no drift detected"

    lines = ["-- Auto-generated draft patch"]
    for event in events:
        lines.append(f"-- {event.kind}: {event.detail}")
    lines.append("select * from source_table;")
    return "\n".join(lines)
