# DriftShield

DriftShield is an autonomous schema-drift repair assistant for dbt + BigQuery teams.

## Why
Data contract breaks silently destroy trust in analytics and AI workflows. DriftShield detects schema changes, estimates downstream blast radius, and opens safe repair PRs.

## MVP Scope (v0)
- Detect schema drift events (rename/type/add/drop)
- Infer semantic mapping between old/new fields
- Generate dbt SQL patch suggestions
- Validate patches with rule checks
- Open GitHub PR with risk summary

## Repo Layout
- `backend/` FastAPI service for drift analysis + patch generation
- `docs/` roadmap, specs, research, logs
- `tests/` core unit tests

## Quickstart

### 1) Clone and enter the repo
```bash
git clone <your-repo-url>
cd Temp01
```

### 2) Set up a local Python environment
```bash
make setup
```

### 3) Configure environment (recommended)
```bash
cp .env.example .env
# then edit values as needed
```

### 4) Run checks (static + tests)
```bash
make check
```

### 5) Run smoke test (startup + health + analyze)
```bash
make smoke
```

### 6) Start the API
```bash
make run
```

Service will be available at `http://127.0.0.1:8000`.

## Manual commands (without Makefile)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pytest -q
uvicorn backend.app.main:app --reload
```

## CI
GitHub Actions runs a lightweight static check (`python -m compileall`), Python tests, and a local smoke check (`python scripts/smoke.py`) automatically on every push using `.github/workflows/python-tests.yml`.

## Environment
Set optional repo settings for PR payload preview, and tokenized PR creation:

```bash
export GITHUB_OWNER=kdave002
export GITHUB_REPO=Temp01
export GITHUB_BASE_BRANCH=main
export GITHUB_HEAD_BRANCH=driftshield/auto-fix
export GITHUB_TOKEN=ghp_xxx   # required for live PR creation
export GITHUB_API_TIMEOUT_SECONDS=10
export DRIFTSHIELD_API_KEY=change-me  # optional, recommended: protects /pr-create via X-DriftShield-Key
```

## API
- `GET /health` → service status + repo config signal
- `POST /analyze` → drift analysis, patch, validation, merge recommendation
- `POST /pr-preview` → structured GitHub PR payload draft
- `POST /pr-create` → runs analysis + payload build; creates GitHub PR when token/repo are configured, otherwise returns dry-run payload. If `DRIFTSHIELD_API_KEY` is set, callers must send matching header `X-DriftShield-Key`; if unset, endpoint behavior is unchanged (no API-key gate).
- `POST /roi-estimate` → estimates monthly/annual engineering time and cost savings from DriftShield adoption based on incident baseline inputs
- `POST /simulate` → concise preflight simulation report with predicted breakage class, expected repair path, and confidence band (supports optional metric baselines; rejects empty schema input and applies stricter endpoint-level anti-abuse caps)
- `POST /pilot-readiness` → deterministic pilot go/no-go scorecard from operational readiness checks

### Request correlation + audit logging
- Every request supports/returns `X-Request-ID`.
  - If caller sends `X-Request-ID`, it is propagated in the response.
  - If omitted, DriftShield generates one and returns it.
- Error responses for `POST /analyze`, `POST /pr-preview`, `POST /pr-create`, and `POST /roi-estimate` include top-level `request_id` for tracing.
- Each request emits an audit log line:
  - `method=<METHOD> path=<PATH> status=<STATUS> request_id=<REQUEST_ID>`

### ROI estimate payload example
```json
{
  "incidents_per_month": 10,
  "mean_time_to_detect_hours": 2,
  "mean_time_to_resolve_hours": 4,
  "engineers_involved_per_incident": 2,
  "hourly_engineering_cost_usd": 100,
  "driftshield_adoption_rate": 0.75
}
```

### Simulation payload example
```json
{
  "previous_schema": [{"name": "customer_id", "type": "string"}],
  "current_schema": [{"name": "client_id", "type": "string"}],
  "downstream_model_count": 6,
  "metric_baselines": {
    "incidents_per_month": 12,
    "mean_time_to_detect_hours": 3,
    "mean_time_to_resolve_hours": 5
  }
}
```
