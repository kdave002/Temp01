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

### 3) Run tests
```bash
make test
```

### 4) Start the API
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
GitHub Actions runs Python tests automatically on every push using `.github/workflows/python-tests.yml`.

## Environment
Set optional repo settings for PR payload preview:

```bash
export GITHUB_OWNER=kdave002
export GITHUB_REPO=Temp01
export GITHUB_BASE_BRANCH=main
```

## API
- `GET /health` → service status + repo config signal
- `POST /analyze` → drift analysis, patch, validation, merge recommendation
- `POST /pr-preview` → structured GitHub PR payload draft
