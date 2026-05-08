# ROI Calculation Template — SaaS Tool Evaluation

**Used in:** Composio analysis (2026-05-03), applicable to any subscription tool evaluation

---

## 1. Cost Model

### Subscription Tiers
| Tier | Monthly | Annual | Quota | Overage Rate |
|------|---------|--------|-------|--------------|
| Free | $0 | $0 | X units | N/A |
| Starter | $X | $12X | Y units | $Z/unit |
| Pro | $X | $12X | Y units | $Z/unit |
| Enterprise | Custom | Custom | Custom | Custom |

### Implementation Costs (One-Time)
| Item | Hours | Rate | Cost |
|------|-------|------|------|
| Setup/integration | TBD | $100/hr | = hours × 100 |
| Testing/QA | TBD | $100/hr | = hours × 100 |
| Documentation | TBD | $100/hr | = hours × 100 |
| **Total** | — | — | **Σ** |

---

## 2. Benefit Quantification

### Direct Time Savings
| Task | Current Time (hrs/yr) | Post-Tool Time (hrs/yr) | Net Saved | Value @ $100/hr |
|------|----------------------|------------------------|-----------|-----------------|
| Manual data aggregation | TBD | TBD | Δ | = Δ × 100 |
| Email/notification triage | TBD | TBD | Δ | = Δ × 100 |
| Reporting/analytics | TBD | TBD | Δ | = Δ × 100 |
| **Total** | — | — | **ΣΔ** | **ΣΔ × 100** |

### Incident Reduction
| Incident Type | Current Frequency | Post-Tool Frequency | Reduction | Cost/Incident | Value |
|---------------|------------------|---------------------|-----------|---------------|-------|
| API failures | TBD | TBD | Δ | $500 | = Δ × 500 |
| Data errors | TBD | TBD | Δ | $300 | = Δ × 300 |
| Missed alerts | TBD | TBD | Δ | $1,000 | = Δ × 1000 |
| **Total** | — | — | — | — | **Σ** |

### New Capabilities (Qualitative → Quantified Where Possible)
| Capability | Current State | Future State | Value Estimate |
|------------|---------------|--------------|---------------|
| Real-time monitoring | Manual (daily) | Automated (real-time) | $1,000–5,000 |
| Multi-source aggregation | Impossible | Native | $2,000–10,000 |
| Alert fatigue reduction | High | Low | $500–2,000 |
| **Subtotal** | — | — | **$3,500–17,000** |

---

## 3. ROI Calculation

### Year 1 Cash Flow
```
Month 0: -$[Implementation Cost]  (one-time)
Months 1–12: -$[Monthly Subscription] × 12
Months 1–12: +$[Monthly Time Savings] × 12
Months 1–12: +$[Incident Reduction Value]/12 × 12
```

**Net Year 1:** `Σ Benefits − Σ Costs`

### Year 2+ Cash Flow (no implementation cost)
```
Annual: +$[Annual Benefits] − $[Annual Subscription]
```

**3-year total:** `Year1 + Year2 + Year3`

---

## 4. Break-Even Analysis

**Formula:**
```
Break-even (months) = Implementation Cost / (Monthly Benefit − Monthly Cost)
```

**Example (Composio):**
- Implementation: 18 hrs × $100 = $1,800
- Monthly benefit: $417 ($5,000/yr ÷ 12)
- Monthly cost: $29
- Monthly net: $417 − $29 = $388
- **Break-even:** $1,800 ÷ $388 = **4.6 months**

---

## 5. Sensitivity Analysis

| Scenario | Monthly Cost | Monthly Benefit | Net/Mo | Annual Net |
|----------|--------------|----------------|--------|------------|
| Conservative (50% benefit) | $29 | $208 | $179 | $2,148 |
| Base (expected) | $29 | $417 | $388 | $4,656 |
| Aggressive (150% benefit) | $29 | $625 | $596 | $7,152 |

**Key sensitivity drivers:**
1. Actual dev hours saved (±20%)
2. Overage charges if quotas exceeded
3. Team adoption rate (0–100%)

---

## 6. Tier Selection Decision Tree

```
Free tier sufficient?
├─ Yes, if: baseline usage < 50% of quota AND no critical SLA needs
│   └─ Risk: quotas tighten as team grows → monitor monthly
├─ No, if: baseline > 50% OR burst usage common OR need support
│   └─ Choose paid tier
└─ Decision rule: (peak_month_usage × 1.2) ≤ tier_quota
```

**Composio example:**
- Peak estimate: 23K calls/mo
- 23K × 1.2 = 27.6K
- Free tier: 20K → ❌ insufficient
- Starter tier: 200K → ✅ 10× buffer

---

## 7. Risk-Adjusted ROI

**Adjust benefits down by risk factor:**
```
Adjusted Annual Benefit = Σ Benefits × (1 − Risk Factor)
```

| Risk | Probability | Impact | Adjustment |
|------|-------------|--------|------------|
| Low adoption | 30% | −50% value | ×0.85 |
| Integration delays | 20% | +$500 cost | ×0.95 |
| Overage surprise | 15% | +$100/mo | ×0.90 |

**Composio risk-adjusted ROI:** $4,656 × 0.85 ≈ **$3,957** (still positive)

---

## 8. Recommendation Template

```
🏆 Recommendation: [Go/No-Go] — [Tier Name] at $X/mo

ROI: [X:1 positive / negative]
Break-even: [X months]
3-year net: $[XXXX]

✅ Pros:
• [Quantified benefit 1]
• [Quantified benefit 2]
• [Qualitative advantage]

⚠️ Cons:
• [Cost/con]
• [Risk factor]

🎯 Next steps:
1. [Action 1]
2. [Action 2]
3. [Action 3]

📊 Assumptions:
• [Assumption 1] (valid through [date])
• [Assumption 2] (needs validation by [owner])
```

---

## Quick Reference: When to Upgrade Tiers

| Signal | Action |
|--------|--------|
| Consistent 70%+ quota usage for 2 months | Upgrade next month |
| Overage charges > $10 in a month | Upgrade immediately |
| Support tickets delayed > 24h | Upgrade for SLA |
| New integration needs > 20% more quota | Preemptive upgrade |

---

**Document version:** 1.0
**Author:** YoYo (Strategies)
**First used:** Composio evaluation, 2026-05-03
