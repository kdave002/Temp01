# TEST_REPORT

- Pending first test run.

- 2026-03-02: Added test cases for rename inference and impact scoring thresholds.
- 2026-03-02T00:30:30Z: Test run result: unit tests passed=3, failed=0.
- 2026-03-02T00:57:53Z: Test run result: unit tests passed=7, failed=0.
- 2026-03-02T01:14:33Z: Test run result: unit tests passed=8, failed=0.
- 2026-03-02T02:00:22Z: Test run result: unit tests passed=14, failed=0.
- 2026-03-02T02:03:57Z: Added Makefile lint/check targets + CI compileall step; local verification via `make check` passed (14/14).
- 2026-03-02T02:16:00Z: Added endpoint abuse-control regression tests for `/analyze` and `/pr-create` (error response shape + bounds); local run via `.venv/bin/python -m pytest -q` passed (29/29).
- 2026-03-02T02:28:38Z: Added `/pr-create` API-key protection tests for optional `DRIFTSHIELD_API_KEY` gating via `X-DriftShield-Key` (unset key allows legacy behavior; configured key requires exact match and returns safe 401 on mismatch); local run via `.venv/bin/python -m pytest -q` passed (38/38). [UTC DONE]
- 2026-03-02T05:09:13Z: Added `/simulate` regression coverage to reject empty `metric_baselines` objects with safe 422 validation envelope + request-id propagation; full suite re-run passed.
- 2026-03-02T02:35:30Z: Added lightweight smoke flow (`scripts/smoke.py`) to verify local app startup + `GET /health` + sample `POST /analyze`; local run via `.venv/bin/python scripts/smoke.py` passed (`SMOKE_OK`). [UTC DONE]
- 2026-03-02T04:10:00Z: Added `/simulate` endpoint abuse-control tests (reject empty schema input, reject endpoint-level downstream threshold), then ran `.venv/bin/python -m pytest -q` and `make check`; result: 46 passed, 0 failed. [UTC DONE]
- 2026-03-02T04:25:00Z: Added rate-limit tests (`tests/test_rate_limit.py`) covering enforced 429 on `POST /analyze` threshold exceedance and non-limiting behavior for `GET /health`; full suite + checks passed. [UTC DONE]
- 2026-03-02T04:39:00Z: Added rate-limit stale-bucket eviction coverage to prevent unbounded in-memory bucket growth with rotating clients; full suite run via `.venv/bin/python -m pytest -q` passed (49/49). [UTC DONE]
- 2026-03-02T04:54:07Z: Expanded rate-limit coverage tests for additional protected endpoints (`/simulate`, `/roi-estimate`, `/pilot-readiness`) and updated middleware scope; full suite run via `.venv/bin/python -m pytest -q` passed (52/52). [UTC DONE]
- 2026-03-02T05:23:00Z: Added rate-limit regression assertion for `Retry-After` header on 429 responses; full suite run via `.venv/bin/python -m pytest -q` passed (53/53). [UTC DONE]
