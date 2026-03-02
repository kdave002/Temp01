# RESEARCH_REPORT

## Problem Statement
Schema drift in modern stacks (warehouse + dbt + BI + ML features) causes silent breakages, wrong metrics, and delayed incident resolution.

## Market Signal (qualitative)
- Data teams increasingly rely on contracts but still face upstream source volatility.
- Existing observability tools detect issues; auto-remediation remains limited and risky.

## Product Wedge
- Start with dbt + BigQuery drift repair PR generation.
- Avoid broad observability dashboards in MVP.

## Free-First Stack
- FastAPI, Pydantic, SQLGlot, pytest, GitHub API, Open-source rule checks.
