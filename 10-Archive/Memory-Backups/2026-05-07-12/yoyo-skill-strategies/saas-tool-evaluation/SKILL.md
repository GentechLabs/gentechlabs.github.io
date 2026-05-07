---
name: saas-tool-evaluation
description: Systematic evaluation framework for SaaS/API platform adoption — pricing extraction, ROI modeling, risk assessment, and phased implementation planning
triggers:
  - "evaluate a new SaaS tool"
  - "cost-benefit analysis for"
  - "should we subscribe to"
  - "pricing analysis for"
  - "ROI calculation for"
  - "tool adoption decision"
outputs:
  - Business case document with quantified ROI
  - Usage scenario modeling (conservative/base/peak)
  - Risk matrix with mitigations
  - Phase 1 implementation plan (Kanban)
  - Cost sensitivity analysis
steps:
  1. PRICING DISCOVERY — Extract tier structure, quotas, overage rates
  2. USAGE MODELING — Estimate monthly calls/operations across 3 scenarios
  3. QUANTIFIED BENEFITS — Calculate time saved, incidents avoided, capabilities unlocked
  4. ROI CALCULATION — Net present value, break-even point, sensitivity thresholds
  5. RISK ASSESSMENT — Rate limits, vendor lock-in, security, cost overruns
  6. IMPLEMENTATION PLAN — Phase 1 scope, Kanban board, delivery timeline
  7. RECOMMENDATION — Clear tier choice + go/no-go + next steps
pivots:
  - If pricing page is JS-heavy: use curl + HTML parsing (see references/pricing-scraping.md)
  - If usage uncertain: model conservative/base/peak + 20% safety margin
  - If team size small: focus on 1–2 P0 integrations first
format: Business case → Kanban → Decision matrix + next steps
tone: Numbers-first, direct recommendation, concise risk-aware analysis
references:
  - pricing-scraping
  - roi-calculation-template
  - kanban-template
  - cost-sensitivity-analysis
---

## How to Use This Skill

**When to invoke:**
- Evaluating a new SaaS/API service for Gentech stack
- Comparing pricing tiers for existing tooling
- Building business case for procurement
- Planning phased rollout of integrations

**Inputs needed:**
- Tool name + website URL
- Integration scope (what we want to DO with it)
- Team size/usage context (small team = conservative estimates)

**Outputs produced:**
- Business case doc (`03-Strategies/analysis/YYYY-MM-DD-<tool>-cost-benefit.md`)
- Kanban board (`03-Strategies/<tool>/phase1-kanban.md`)
- Summary for HQ (with clear recommendation)

---

## Common Pitfalls

### Pitfall 1 — Free Tier Trap
**Symptom:** Analysis shows Free tier sufficient, but 3 months later we hit quotas.
**Fix:** Always model with 20% safety margin; if baseline usage > 50% of free tier, recommend paid.

### Pitfall 2 — Single-Point Forecast
**Symptom:** "We'll use 15K calls/month" → unexpected spikes cause overages.
**Fix:** Build three scenarios: conservative (day-to-day), base (typical), peak (busy week). Use base + 20% for tier selection.

### Pitfall 3 — Hidden Costs Ignored
**Symptom:** Only subscription cost counted; implementation effort, training, migration overhead forgotten.
**Fix:** Quantify dev hours at $100/hr rate; include testing/monitoring setup time.

### Pitfall 4 — No Exit Strategy
**Symptom:** Vendor lock-in; switching costs high if tool disappointed.
**Fix:** Design abstraction layer; keep fallback to manual process; document migration path.

### Pitfall 3 — Vague Success Criteria
**Symptom:** "Integrate tool" → no way to know when done.
**Fix:** Define DoR/DoD per integration; measurable KPIs (calls/day, error rate < 1%).

---

## Templates Provided

- **Business case template:** `templates/business-case.md`
- **Kanban board template:** `templates/phase1-kanban.md`
- **Cost model spreadsheet (CSV):** `templates/cost-model.csv`

---

## Related Skills

- `strategies` — parent department umbrella
- `research` — for market/competitive analysis
- `project-management` — for execution tracking (if available)

---

## Last Updated

2026-05-03 — Added pricing extraction from JS-heavy sites (Composio case study)
