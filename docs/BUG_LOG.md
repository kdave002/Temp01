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
