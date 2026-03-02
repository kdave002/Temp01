# FEATURE_SPECS

## F001 Drift Diff Engine (Must)
- Compare previous and current schema versions.
- Output drift events: added, removed, renamed (candidate), type_changed.
- Acceptance: deterministic output for given input fixtures.

## F002 Impact Scoring (Must)
- Score drift severity based on downstream model dependencies.
- Acceptance: returns low/medium/high with rationale.

## F003 Patch Draft Generator (Must)
- Generate candidate dbt SQL transformation for breaking drifts.
- Acceptance: patch contains executable SQL template + notes.

## F004 Validation Rules (Must)
- Basic checks: null-rate guard, type cast feasibility, uniqueness preservation hint.
- Acceptance: pass/fail report object.

## F005 PR Payload Builder (Should)
- Build structured markdown for GitHub PR body.
- Acceptance: includes summary, risk, rollback, validation results.

## F006 Validation Summary + PR Body Composer (Must)
- Build deterministic remediation validation report and PR markdown payload.
- Acceptance: includes risk, events, patch SQL, rollback section.
