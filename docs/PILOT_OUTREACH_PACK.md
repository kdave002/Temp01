# DriftShield Pilot Outreach Pack (dbt + BigQuery)

Practical outreach material for Analytics Engineering, Data Platform, and RevOps teams running dbt on BigQuery.

## 1) Cold Email Templates (3)

### Email 1 — Cost + Reliability Angle
**Subject:** Quick idea to cut BigQuery waste in dbt runs

Hi {{FirstName}},

Noticed your team is running dbt on BigQuery. Teams at your stage usually have 2 issues at once:
- query spend creeping up from model sprawl, and
- brittle pipelines where one upstream model causes downstream churn.

DriftShield is a lightweight layer for dbt+BigQuery teams that flags model/data drift early and highlights cost-heavy model changes before they become expensive incidents.

Open to a 20-min pilot scoping call next week? If there’s no clear ROI in 2 weeks, we stop.

— {{YourName}}

---

### Email 2 — Incident Prevention Angle
**Subject:** Prevent “silent” dbt breakages before dashboards drift

Hi {{FirstName}},

A lot of dbt+BigQuery teams don’t fail loudly—they drift quietly (schema changes, freshness shifts, logic regressions) and business users notice later.

DriftShield helps catch those changes in CI + scheduled runs and routes actionable alerts to the right owner.

Would you be open to a small pilot on 1–2 critical marts? Goal: reduce surprise breakages and cut time-to-detect.

If useful, I can send a 1-page pilot plan.

— {{YourName}}

---

### Email 3 — VP/Head of Data Angle (Business Outcome)
**Subject:** 30-day pilot: improve trust in dbt outputs

Hi {{FirstName}},

If your team relies on dbt + BigQuery for revenue/ops reporting, trust erosion is costly: teams re-check numbers, rerun jobs, and decisions slow down.

DriftShield is designed for this exact stack—surfacing risky model changes, anomalous shifts, and pipeline drift so teams can act before stakeholders lose confidence.

Would you consider a 30-day pilot with clear success criteria (incident reduction, faster triage, lower avoidable compute)?

Happy to share a concrete rollout plan.

— {{YourName}}

## 2) LinkedIn DM Templates (3)

### DM 1 — Direct + Low Friction
Hey {{FirstName}} — quick one: are you responsible for dbt + BigQuery reliability/cost at {{Company}}?

I work with teams using DriftShield to catch drift and risky model changes before they become fire drills. If relevant, I can send a short pilot outline.

---

### DM 2 — Problem-Led
Seeing many dbt+BigQuery teams struggle with “quiet failures” (metrics drift without hard pipeline failure).

We built DriftShield to detect that early and speed up root-cause for model owners. Worth a quick chat to see if this is a fit for your team?

---

### DM 3 — Social Proof Style (without hard claims)
I’m speaking with a few data teams running dbt on BigQuery about reducing avoidable reruns and late-stage dashboard surprises.

Would you be open to a 15–20 min conversation? If there’s no obvious pilot value, we won’t force it.

## 3) Pilot Qualification Checklist

Use this to quickly decide if an account is pilot-ready.

### Technical Fit
- [ ] Uses **dbt** in production workflows
- [ ] Core warehouse is **BigQuery**
- [ ] Has at least 1 critical data product/dashboard tied to dbt models
- [ ] Can grant read-level metadata/query history access needed for drift/cost analysis

### Pain + Urgency
- [ ] Recent incident involving model breakage, metric drift, freshness issues, or cost spike
- [ ] Team reports alert noise or slow root-cause on failures
- [ ] Rising BigQuery spend without clear model-level accountability
- [ ] Leadership asking for better reliability/trust in analytics outputs

### Operational Readiness
- [ ] Clear internal owner (Data Eng Manager / Analytics Eng Lead)
- [ ] Slack/Teams + ticketing workflow available for alert routing
- [ ] Willing to run a 2–4 week pilot with weekly check-ins
- [ ] Agrees to baseline current metrics before pilot starts

### Success Metrics Defined
- [ ] Time-to-detect (TTD) drift incidents
- [ ] Time-to-resolve (TTR) data reliability incidents
- [ ] Number of downstream stakeholder-reported issues
- [ ] Avoidable BigQuery compute spend tied to problematic model changes

**Pilot Go/No-Go Rule:** Proceed if Technical Fit is complete + at least 2 Pain/Urgency boxes + named owner + agreed success metrics.

## 4) Discovery Call Script (20–30 min)

### 0–3 min: Context
- “Can you walk me through your dbt + BigQuery setup at a high level?”
- “Which team owns model quality and cost governance today?”

### 3–10 min: Current Pain
- “Where do issues show up most: CI, scheduled runs, or business dashboards?”
- “What’s your current process when a metric suddenly shifts?”
- “Any recent incidents that were expensive or embarrassing internally?”

### 10–16 min: Quantify Impact
- “How many incidents/month require manual triage?”
- “Roughly how much engineer/analyst time goes into investigation and reruns?”
- “Any estimate of wasted BigQuery spend from regressions or inefficient model changes?”

### 16–22 min: Fit + Pilot Scope
- “If we pilot, which 1–2 domains are highest risk (e.g., finance, funnel, retention)?”
- “Who should receive alerts, and what would ‘actionable’ look like for them?”
- “What would make you call this pilot a win in 30 days?”

### 22–30 min: Close
- Recap pains + quantified impact
- Propose pilot scope (models, owners, cadence)
- Confirm success metrics + timeline
- Book kickoff and technical onboarding

## 5) ROI Pitch Snippets (Tailored to dbt + BigQuery)

Use these in emails, decks, or live calls.

- **Incident Cost Framing:**
  “Every drift incident you catch before business users notice saves rework across analytics, engineering, and stakeholder time. DriftShield shifts detection left so problems are fixed at model-owner level.”

- **Compute Spend Framing:**
  “In BigQuery environments, inefficient or regressive model changes can silently raise run costs. DriftShield helps surface those changes early so you can avoid paying for preventable waste.”

- **Trust + Speed Framing:**
  “When teams trust dbt outputs, decisions move faster. DriftShield reduces ‘is this number right?’ loops by flagging risky changes before they affect executive dashboards.”

- **Pilot Risk Reversal:**
  “Keep the pilot narrow: 1–2 critical marts, 2–4 weeks, and pre-agreed success metrics. If we don’t show measurable improvement in reliability/cost visibility, stop.”

- **Capacity Recovery Framing:**
  “Instead of senior analytics engineers repeatedly firefighting root-cause, DriftShield helps standardize detection and triage so the team can focus on roadmap work.”
