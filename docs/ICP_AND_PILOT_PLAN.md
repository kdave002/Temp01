# DriftShield — ICP & Pilot Plan

## 1) ICP Segmentation (Practical, outreach-first)

### Core problem DriftShield likely solves
Organizations with customer-facing web apps lose revenue and trust when bots, abuse, credential stuffing, fake signups, promo abuse, scraping, and account takeover go unchecked.

### Segment A — API-first SaaS (B2B/B2C)
- **Profile:** 20–500 employees, cloud-native stack, self-serve onboarding or free trial.
- **Pain signals:** Sudden signup spikes, trial fraud, fake accounts, suspicious login failures, support burden.
- **Buying trigger:** Security incident, infra cost jump, growth KPI distortion, or investor pressure to reduce risk.
- **Economic buyer:** CTO / VP Eng.
- **Technical champion:** Staff engineer, SRE lead, security engineer.
- **Why good ICP:** Fast cycles, measurable abuse, engineering-led decision-making.

### Segment B — E-commerce / DTC brands
- **Profile:** Shopify/BigCommerce/custom stores with paid acquisition.
- **Pain signals:** Card testing, checkout abuse, coupon abuse, scraper-driven price undercutting, ad spend waste from bot traffic.
- **Buying trigger:** Chargeback rise, failed checkout spikes, peak season prep.
- **Economic buyer:** Head of E-commerce / COO.
- **Champion:** Dev lead, fraud/risk manager.
- **Why good ICP:** Direct link between abuse and margin loss.

### Segment C — Fintech / Wallet / Payments apps
- **Profile:** Regulated or semi-regulated digital finance products.
- **Pain signals:** Account takeover attempts, credential stuffing, synthetic signups, referral abuse.
- **Buying trigger:** Compliance pressure, incident postmortem, fraud reserve increase.
- **Economic buyer:** CISO / Head of Risk.
- **Champion:** Fraud ops lead, security architect.
- **Why good ICP:** High-loss events, clear ROI from prevention.

### Segment D — Marketplaces / Classifieds / Gig platforms
- **Profile:** Two-sided platforms dependent on trust.
- **Pain signals:** Fake listings, spam accounts, lead fraud, scraping inventory, reputation manipulation.
- **Buying trigger:** User trust decline, moderation cost increase.
- **Economic buyer:** GM / VP Product.
- **Champion:** Trust & Safety lead.
- **Why good ICP:** Abuse degrades core network effect.

### Segment E — Gaming / EdTech / Consumer apps with freemium funnels
- **Profile:** High-volume account creation and promo incentives.
- **Pain signals:** Multi-accounting, bonus abuse, fake engagement, credential stuffing.
- **Buying trigger:** CAC-to-LTV deterioration, referral fraud.
- **Economic buyer:** VP Product / Growth.
- **Champion:** Data lead, backend lead.
- **Why good ICP:** Growth + abuse are tightly linked.

### Ideal first beachhead (recommended)
1. **B2B SaaS with free trial** (fast pilot velocity + data visibility)
2. **E-commerce mid-market brands** (clear financial narrative)
3. **Marketplaces with Trust & Safety teams** (strong champion function)

---

## 2) Top 25 Outreach Target Archetypes (Role + company pattern)

Use these as target *archetypes* for outbound list-building (LinkedIn + company websites + job posts + tech stack signals).

1. **CTO at Series A–C B2B SaaS with free trial**
2. **VP Engineering at API-first developer tools company**
3. **Head of Security at growth-stage SaaS (100–1000 employees)**
4. **Staff Security Engineer at recently breached startup**
5. **SRE/Platform leader at high-login consumer app**
6. **Head of Fraud at fintech app with referral program**
7. **Trust & Safety lead at marketplace platform**
8. **VP Product at marketplace with spam/listing quality issues**
9. **Director of Risk at neobank or wallet product**
10. **Head of E-commerce at DTC brand with high paid traffic**
11. **Director of Digital at retailer facing scraper/coupon abuse**
12. **Payments/Fraud manager at online checkout-heavy merchant**
13. **COO at scaling e-commerce brand with chargeback growth**
14. **Head of Growth at freemium SaaS seeing signup anomalies**
15. **Lifecycle/CRM leader impacted by fake account cohorts**
16. **Engineering manager at company hiring “bot mitigation/fraud” roles**
17. **CISO at mid-market B2C app after credential-stuffing event**
18. **Data science lead managing fraud models with limited signals**
19. **Customer support leader with abuse-driven ticket spikes**
20. **Compliance lead where fraud controls affect audit outcomes**
21. **Head of Revenue Ops where fake leads distort pipeline metrics**
22. **Head of Partnerships at affiliate-heavy growth programs (promo abuse risk)**
23. **GM of regional marketplace with trust decline complaints**
24. **Founder/CEO of bootstrapped SaaS with lean security team**
25. **Technical Product Manager owning authentication/onboarding funnels**

### Free-research sourcing checklist for each target
- Company has self-serve signup/login visible publicly.
- Careers page mentions fraud, abuse prevention, trust & safety, risk, SOC2, or security hardening.
- Public incident discussion (blog, status page, Reddit/X/LinkedIn comments).
- Tech stack indicates scale (Cloudflare/Akamai/Fastly, auth providers, observability tools).
- Evidence of paid growth + incentives (trials, coupons, referral credits).

---

## 3) Pilot Offer Terms (designed to reduce buyer risk)

### Pilot objective
Prove measurable abuse reduction and operational lift in 30–45 days without disruptive re-architecture.

### Recommended pilot structure
- **Duration:** 6 weeks (2 setup + 4 measured run).
- **Scope:** 1–2 abuse vectors max (e.g., fake signup + credential stuffing).
- **Integration:** Reverse proxy/API middleware/SDK event stream (choose least-friction path).
- **Success metrics (baseline vs pilot):**
  - % drop in fraudulent signups or suspicious login attempts
  - Reduced support tickets tied to abuse
  - Improvement in conversion quality (trial-to-paid cleanliness)
  - Infra/API cost reduction from bot traffic suppression
- **Commercial model:**
  - Low fixed pilot fee (or paid setup + conditional scale contract)
  - Optional performance kicker tied to agreed metric improvements
- **Data & privacy:**
  - DPA in place, no unnecessary PII retention
  - Clear logging and model decision explainability for security teams
- **Exit/expand clause:**
  - If minimum KPI threshold not met, customer can stop
  - If met, auto-convert to annual/monthly plan with pilot credit applied

### Example pilot package (template)
- **Setup:** $7,500 one-time
- **Pilot run:** $5,000/month for 2 months
- **Expansion:** Convert to $4k–$15k MRR depending on event volume and modules
- **Guarantee option:** If <20% abuse reduction on agreed metric, extend pilot 30 days no extra platform fee

---

## 4) ROI Calculator Assumptions (simple, CFO-friendly)

Use conservative assumptions first; let prospect edit values.

### Input variables
- Monthly signup volume
- % estimated fraudulent signups
- Cost per fraudulent signup (infra + support + downstream sales noise)
- Monthly login attempts
- % malicious login attempts
- Estimated account takeover (ATO) rate from malicious attempts
- Average loss per ATO event
- Support ticket cost (blended)
- Current chargeback/fraud loss (if commerce/fintech)
- Current tool + internal labor cost for handling abuse
- DriftShield expected reduction rate (%) by abuse type

### Baseline formulas
- **Fake signup loss/month** = Monthly signups × Fraud % × Cost per fraudulent signup
- **ATO loss/month** = Malicious login attempts × ATO conversion % × Loss per ATO
- **Ops burden/month** = Abuse-related tickets × Cost per ticket + analyst hours × loaded hourly rate
- **Total abuse cost/month** = Fake signup loss + ATO loss + Ops burden + chargebacks/other known loss

### With-DriftShield formulas
- **Prevented loss/month** = Total abuse cost × Expected reduction %
- **Net benefit/month** = Prevented loss − DriftShield monthly cost
- **Payback period (months)** = Setup cost / Net benefit (if Net benefit > 0)
- **Annual ROI %** = ((12 × Net benefit) − setup cost) / (12 × DriftShield monthly cost + setup cost) × 100

### Conservative default assumptions (if no customer data yet)
- Fraudulent signups: **5–15%** of total (varies by funnel incentive)
- Credential-stuffing malicious attempts: **10–35%** of login traffic for targeted apps
- ATO conversion from malicious attempts: **0.05–0.5%**
- Cost per abuse ticket: **$6–$25**
- DriftShield impact: **20–50% reduction** in prioritized abuse vector during pilot

(Use these only as placeholders; replace with customer telemetry in week 1.)

---

## 5) Objection Handling (field-ready)

### Objection 1: “We already use Cloudflare/Akamai/WAF rules.”
**Response:** Great—DriftShield is complementary. WAFs block known patterns at edge; DriftShield focuses on behavioral abuse patterns and business-logic attacks that pass generic rules. Pilot can isolate one gap your WAF currently misses.

### Objection 2: “We don’t have engineering bandwidth.”
**Response:** That’s exactly why pilot scope is narrow. We use lowest-friction integration, shared implementation checklist, and weekly hands-on support. Goal: measurable outcome in <2 engineer-weeks.

### Objection 3: “False positives could hurt conversion.”
**Response:** Agreed, so we run phased controls: monitor → challenge/score → block only after confidence thresholds. We jointly define guardrails and review precision/recall weekly.

### Objection 4: “Hard to prove ROI.”
**Response:** We baseline your current abuse costs before controls, then track deltas on pre-agreed metrics. Finance-friendly model: prevented loss, support savings, and infra reduction vs subscription cost.

### Objection 5: “Security/legal review will take too long.”
**Response:** We provide security pack upfront (architecture, data handling, retention, DPA templates, subprocessors). Parallelize legal + technical review during pilot setup.

### Objection 6: “Build vs buy—we can do this internally.”
**Response:** Internal builds are valuable but expensive to maintain against evolving adversaries. Pilot shows whether DriftShield accelerates time-to-value and frees team capacity; if not, you should not buy.

### Objection 7: “Budget is frozen.”
**Response:** Start with a constrained pilot tied to one measurable loss bucket and a conversion clause only if threshold outcomes are achieved. Can be funded from fraud-loss reduction or support-efficiency initiatives.

### Objection 8: “We don’t think abuse is a big issue.”
**Response:** Common until measured. Let’s run a 2-week passive assessment to quantify suspicious traffic and account behaviors. If materiality is low, we’ll say so.

---

## 6) Practical outreach motion (optional execution notes)

- Build 100-account list from one beachhead segment first.
- Prioritize accounts with **observable pain signals** (hiring, incident chatter, trust complaints).
- Message sequence: pain hypothesis → evidence ask → low-risk pilot CTA.
- Run founder-led technical call for first 10 opportunities.
- Convert wins into mini case studies (before/after metric snapshots).

This keeps GTM evidence-driven, fast, and affordable using public/free research channels.
