# SECURITY_AUDIT

Date: 2026-03-02 (UTC)
Scope: `backend/app` request/response model validation and abuse resistance.

## Summary

Implemented baseline input hardening in Pydantic models to reduce malformed input, silent correctness issues, and abuse potential.

## Findings and Remediations

1. **Unbounded/loosely validated model fields**
   - **Risk:** Large payloads and malformed values could increase memory/CPU usage or produce undefined behavior.
   - **Fix:** Added strict bounds and format checks in `backend/app/models.py`:
     - `Column.name`: length bound + identifier regex
     - `Column.type`: length bound + conservative type descriptor regex
     - `DriftEvent.confidence`: bounded to `[0.0, 1.0]`
     - `DriftRequest.previous_schema/current_schema`: max 500 columns each
     - `DriftRequest.downstream_model_count`: bounded `0..10000`
     - `DriftResponse.impact_score`: bounded `0..100`
     - `risk`/`severity` constrained to expected literals

2. **Silent key-collision correctness bug from duplicate column names**
   - **Risk:** Duplicate names were collapsed when building dictionaries in drift detection, hiding input inconsistencies.
   - **Fix:** Added post-model validator to reject duplicate column names in `previous_schema` and `current_schema`.

3. **Whitespace-only input acceptance risk**
   - **Risk:** Empty/blank values could bypass naive checks and degrade output quality.
   - **Fix:** Added field validator to trim and reject blank `name`/`type` values.

## Validation

Added abuse-focused tests in `tests/test_input_validation.py`:
- reject SQL-like/injection-shaped column names
- reject duplicate schema column names
- reject oversized schema payloads (>500)
- reject negative downstream model counts

Result: `12 passed`.

## Residual Risk / Next Steps

- Consider request size limits at API gateway/reverse proxy layer for defense in depth.
- Consider stricter allow-list for SQL type strings if type catalog is known.
- Add rate limiting on `/analyze` if exposed publicly.

## 2026-03-02T02:06:34Z Update [DONE]

Additional API misuse-resistance hardening implemented:
- Added endpoint-level guardrails for PR-facing routes (`/pr-preview`, `/pr-create`):
  - reject empty combined schema (`422`)
  - cap combined schema size at 600 columns for PR endpoints (`422`)
  - cap `downstream_model_count` at 5000 for PR endpoints (`422`)
- Added explicit PR integration gate for missing repo config on PR endpoints (`503`, safe message).
- Added safe structured validation error response for malformed payloads (`detail=invalid request payload`, `errors=[]`) to avoid leaking framework internals.
- Sanitized upstream GitHub failure responses on `/pr-create`:
  - timeout => `504` with generic safe detail
  - GitHub API failure => `502` with generic safe detail

Validation coverage added in `tests/test_pr_endpoints.py` for:
- missing repo config flows on `/pr-preview` and `/pr-create`
- endpoint-level oversize and threshold rejection on `/pr-preview`
- malformed payload handling shape on `/pr-preview`
- `/pr-create` dry-run contract when token is missing

## 2026-03-02T02:16:00Z Update [DONE]

Abuse-control consistency review completed across `/analyze`, `/pr-preview`, and `/pr-create`.

Findings:
- All three endpoints now consistently return the custom safe validation envelope for malformed payloads:
  - `422`
  - `{"detail": "invalid request payload", "errors": [...]}`
- `/analyze` enforces model-level bounds (`previous_schema/current_schema <= 500` each, `downstream_model_count <= 10000`).
- `/pr-preview` and `/pr-create` apply stricter endpoint-level anti-abuse bounds on top of model limits:
  - combined schema size cap: `<= 600`
  - `downstream_model_count <= 5000`

Regression tests added in `tests/test_endpoint_abuse_controls.py`:
- `/analyze`: malformed payload error-shape contract
- `/analyze`: model bound rejection (`downstream_model_count=10001`) with safe error envelope
- `/pr-create`: malformed payload error-shape contract
- `/pr-create`: endpoint-level combined-schema cap rejection
- `/pr-create`: endpoint-level downstream threshold rejection
