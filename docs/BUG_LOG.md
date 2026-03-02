# BUG_LOG

## 2026-03-02 (UTC)

### BUG-001: Duplicate schema column names silently overwritten
- **Area:** `backend/app/drift.py` + request model
- **Severity:** Medium (correctness + trust)
- **Symptom:** Duplicate column names in input schema were collapsed in dict conversion (`{c.name: c.type}`), potentially hiding drift conditions.
- **Root Cause:** No uniqueness validation on `DriftRequest.previous_schema/current_schema`.
- **Fix:** Added `DriftRequest` model-level validator to reject duplicate column names before analysis.
- **Status:** Fixed
- **Tests:** `test_rejects_duplicate_column_names_in_schema`

### BUG-002: Missing bounds on user-controlled payload sizes
- **Area:** `backend/app/models.py`
- **Severity:** Medium (abuse/perf risk)
- **Symptom:** Very large schema arrays and unbounded counts could be submitted.
- **Root Cause:** Model fields lacked upper/lower bounds.
- **Fix:** Added max length 500 for schema lists and bounded downstream count `0..10000`.
- **Status:** Fixed
- **Tests:** `test_rejects_excessive_schema_size`, `test_rejects_negative_downstream_model_count`

### BUG-003: Weak format checks for identifiers
- **Area:** `backend/app/models.py`
- **Severity:** Low-Medium (input quality/security hygiene)
- **Symptom:** Column identifiers accepted arbitrary strings including SQL-like payload patterns.
- **Root Cause:** `Column.name` and `Column.type` had no format constraints.
- **Fix:** Added regex/length constraints and blank-string rejection.
- **Status:** Fixed
- **Tests:** `test_rejects_non_identifier_column_name`

### BUG-004: PR endpoints allowed high-cost but low-value requests
- **Area:** `backend/app/main.py` (`/pr-preview`, `/pr-create`)
- **Severity:** Medium (abuse/performance)
- **Symptom:** PR endpoints accepted empty schemas and did not enforce stricter endpoint-level thresholds.
- **Root Cause:** Only model-level bounds existed; no route-specific policy checks.
- **Fix:** Added route guardrails for empty schema rejection, combined schema cap (600), and stricter downstream limit (5000).
- **Status:** Fixed
- **Tests:** `test_pr_preview_rejects_empty_schema`, `test_pr_preview_rejects_total_schema_size_for_endpoint`, `test_pr_preview_rejects_endpoint_level_downstream_threshold`

### BUG-005: Missing repo config handling on PR surfaces was inconsistent/silent
- **Area:** `backend/app/main.py` (`/pr-preview`, `/pr-create`)
- **Severity:** Medium (operational safety)
- **Symptom:** PR-facing routes did not consistently fail fast with clear, safe errors when repo configuration was missing.
- **Root Cause:** No explicit configuration gate shared across PR endpoints.
- **Fix:** Added explicit repo-config gate returning safe `503` detail.
- **Status:** Fixed
- **Tests:** `test_pr_preview_requires_repo_configuration`, `test_pr_create_requires_repo_configuration`

### BUG-006: Error details could expose upstream/internal context
- **Area:** `backend/app/main.py`
- **Severity:** Low-Medium (information disclosure hygiene)
- **Symptom:** Validation and GitHub client exceptions could bubble raw detail strings.
- **Root Cause:** Default/propagated exception text was returned directly.
- **Fix:** Added safe structured validation handler and generic safe `502/504` error messages for GitHub failures.
- **Status:** Fixed
- **Tests:** `test_pr_preview_bad_payload_has_safe_error_shape`, `test_pr_create_returns_504_on_timeout`

Updated: 2026-03-02T02:06:34Z [DONE]
