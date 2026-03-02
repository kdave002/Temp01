# RESEARCH_REPORT

## Problem Statement
Schema drift in modern stacks (warehouse + dbt + BI + ML features) causes silent breakages, wrong metrics, and delayed incident resolution.

## 2026 US Market Pain Points (Practical)
1. **Late detection in production analytics paths**
   - Drift is often discovered only after dashboard anomalies, broken downstream models, or stakeholder escalation.
   - Cost is less about compute and more about **lost analyst/engineer time** and decision delays.

2. **High triage overhead across fragmented ownership**
   - Data engineering owns ingestion, analytics engineering owns dbt models, BI teams own semantic layers, and app teams own event producers.
   - Incidents stall because no single team can quickly identify root cause + safe fix path.

3. **Contract adoption is uneven, especially in mid-market orgs**
   - Teams may define contracts for critical tables but not for long-tail sources.
   - Result: recurring “known unknowns” in less-governed pipelines.

4. **Rename/type-change ambiguity creates risky remediation**
   - Real-world drift is rarely clean add/remove; it is often rename-like changes, widened/narrowed types, and nullability shifts.
   - Manual fixes are cautious and slow because wrong assumptions can corrupt trusted metrics.

5. **Alert fatigue from broad observability tooling**
   - Existing monitors produce many alerts, but not all are actionable.
   - Teams need issue ranking tied to downstream business impact, not raw anomaly counts.

6. **PR and review bottlenecks during incident response**
   - Even when a likely fix is known, generating compliant PRs with context, tests, and rollback notes takes time.
   - During peak reporting windows (month-end/quarter-end), this bottleneck is especially painful.

## Competitive Landscape (Category View)
1. **Data observability platforms**
   - Strength: broad monitoring, anomaly detection, lineage visualization.
   - Gap: often stop at detection/diagnosis; remediation remains manual.

2. **Data quality/testing frameworks (dbt tests, expectations, rule engines)**
   - Strength: codified checks and CI integration.
   - Gap: require teams to author/maintain rules; limited automated repair suggestions.

3. **Catalog/lineage/governance tools**
   - Strength: metadata visibility, ownership, governance workflows.
   - Gap: governance context does not automatically generate fix-ready code changes.

4. **Warehouse-native features and adapters**
   - Strength: tight integration and fast local execution.
   - Gap: usually scoped to one platform; cross-tool incident workflows still manual.

5. **Internal platform scripts/copilots**
   - Strength: tailored to local conventions.
   - Gap: brittle, person-dependent, weak policy controls/auditability at scale.

## Differentiated Wedge for DriftShield
**“From drift signal to safe remediation PR for dbt + BigQuery, with impact-aware risk gating.”**

Why this wedge is practical:
- Narrow integration surface (dbt + BigQuery + GitHub) reduces time-to-value.
- Converts noisy drift events into a **ranked, explainable fix proposal**.
- Produces PR artifacts teams already trust (diff + rationale + validation report), rather than introducing a new destination UI dependency.
- Applies policy gating (auto-merge vs review vs manual) to reduce operational risk.

Wedge boundaries (to avoid overreach):
- No claim of full autonomous healing across all data stacks.
- Focus on high-confidence schema-change classes first (rename candidates, compatible type evolutions, additive changes).
- Keep human-in-the-loop defaults for medium/high-risk modifications.

## Top 3 Pilot Verticals (US, 2026)
1. **B2B SaaS (product analytics + RevOps reporting)**
   - Frequent event/schema evolution from rapid product iteration.
   - Strong pain from KPI instability and board/investor reporting pressure.
   - Usually already on dbt + BigQuery/Snowflake with GitHub-centric workflows.

2. **Fintech and payments analytics teams**
   - High consequence of metric drift (risk, fraud, reconciliation, compliance reporting).
   - Need auditable change paths and stricter approval gates.
   - Good fit for policy-based merge decisions and validation evidence.

3. **Digital health / healthcare operations analytics**
   - Multi-source ingestion (EHR, claims, product telemetry) with frequent schema inconsistency.
   - Operational dashboards are mission-critical; downtime and misreporting are costly.
   - Preference for controlled, reviewable remediation workflows over black-box automation.

## Product Wedge (MVP Alignment)
- Start with dbt + BigQuery drift repair PR generation.
- Prioritize explainability and policy-safe merge decisions over broad dashboard breadth.

## Free-First Stack
- FastAPI, Pydantic, SQLGlot, pytest, GitHub API, open-source rule checks.
