from .models import DriftEvent


def validate_patch(events: list[DriftEvent]) -> dict:
    checks = []

    has_high = any(e.severity == "high" for e in events)
    checks.append({"name": "high_severity_review", "passed": not has_high, "detail": "Manual review required for high severity events." if has_high else "No high severity blockers."})

    type_changes = [e for e in events if e.kind == "type_changed"]
    checks.append({"name": "type_change_cast_plan", "passed": len(type_changes) == 0, "detail": "Type changes detected; cast plan required." if type_changes else "No type cast risks."})

    removed = [e for e in events if e.kind == "removed"]
    checks.append({"name": "removed_column_backfill", "passed": len(removed) == 0, "detail": "Removed columns detected; verify downstream backfill strategy." if removed else "No removed columns."})

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    overall = "pass" if failed == 0 else "needs_review"

    return {
        "overall": overall,
        "passed": passed,
        "failed": failed,
        "checks": checks,
    }


def build_pr_body(events: list[DriftEvent], impact_score: int, risk: str, patch_sql: str, validation: dict) -> str:
    lines = [
        "## DriftShield Auto-Repair Draft",
        "",
        f"- Impact score: **{impact_score}/100**",
        f"- Risk: **{risk.upper()}**",
        f"- Validation: **{validation['overall']}** (passed={validation['passed']}, failed={validation['failed']})",
        "",
        "### Detected Events",
    ]

    if not events:
        lines.append("- No drift events detected")
    else:
        for e in events:
            conf = f" | confidence={e.confidence}" if e.confidence is not None else ""
            lines.append(f"- [{e.severity}] {e.kind}: {e.detail}{conf}")

    lines.extend(
        [
            "",
            "### Proposed Patch",
            "```sql",
            patch_sql,
            "```",
            "",
            "### Rollback",
            "- Revert this PR commit and rerun upstream sync.",
        ]
    )

    return "\n".join(lines)
