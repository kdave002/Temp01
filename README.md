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

## Run (dev)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
