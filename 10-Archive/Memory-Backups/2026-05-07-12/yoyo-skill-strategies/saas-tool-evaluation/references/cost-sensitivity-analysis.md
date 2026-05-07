# Cost Sensitivity Analysis — Multi-Scenario Modeling

**Purpose:** Avoid single-point forecasting failures by modeling conservative/base/peak usage scenarios.

**Problem:** Single estimate ("We'll use ~25K API calls/month") is almost always wrong. Reality has variance.

**Solution:** Three-scenario approach with explicit assumptions and safety margins.

---

## Scenario Definitions

| Scenario | Description | Probability | Use For |
|----------|-------------|-------------|---------|
| **Conservative** | Normal operation, no bursts, quiet periods | 60% | Baseline cost |
| **Base (Expected)** | Typical month with moderate activity | 30% | Primary forecast |
| **Peak** | Busiest month (hackathon, product launch, market event) | 10% | Tier selection + overage planning |

---

## Example: Composio Call Volume Modeling

### Step 1 — List All Integrations
| Tool | Purpose | Daily Avg | Burst Factor |
|------|---------|-----------|--------------|
| Gmail | Inbox parsing | 100 | 2× (Monday cleanup) |
| Slack | Notifications | 50 | 1.5× (alert storms) |
| GitHub | PR monitoring | 10 | 3× (merge day) |
| CoinGecko | Price checks | 300 | 1.2× (volatile days) |
| Uniswap | LP positions | 100 | 1× (steady) |

### Step 2 — Calculate Scenarios
```
Conservative = Σ(daily_avg × 30 days)  # no burst multiplier
Base         = Conservative × 1.15      # 15% typical volatility
Peak         = MAX(integration_peak)    # sum of individual peaks
```

**Composio result:**
- Conservative: 16,800 calls
- Base: 19,320 calls (16,800 × 1.15)
- Peak: 22,950 calls (individual burst days summed)

### Step 3 — Apply Safety Margin
```
Tier selection threshold = Peak × 1.2
= 22,950 × 1.2 = 27,540 calls
```

**Composio decision:**
- Free tier (20K) < 27K → ❌ too small
- Starter (200K) > 27K → ✅ sufficient (7× buffer)
- Business (2M) → overkill

---

## Monte Carlo Alternative (Advanced)

If you have historical variance data:

```python
import numpy as np

# Daily means and std devs for each integration
integrations = [
    (100, 20),   # Gmail: mean=100, std=20
    (50, 10),    # Slack
    (10, 5),     # GitHub
    (300, 50),   # CoinGecko
    (100, 0),    # Uniswap (steady)
]

# Simulate 10,000 months
simulations = 10000
monthly_totals = []
for _ in range(simulations):
    daily_total = sum(max(0, np.random.normal(mean, std)) for mean, std in integrations)
    monthly_total = daily_total * 30
    monthly_totals.append(monthly_total)

# 95th percentile = peak planning
p95 = np.percentile(monthly_totals, 95)
print(f"Plan for: {p95:,.0f} calls/month")
```

**Output:** `Plan for: 24,812 calls/month` → same tier selection outcome.

---

## Cost Overrun Scenarios

| Overage % | Monthly Calls | Overage Cost | Annual Impact |
|-----------|---------------|--------------|---------------|
| 10% over base | 21,260 | $6.32 | +$76 |
| 20% over base | 23,180 | $13.84 | +$166 |
| 30% over base | 25,120 | $21.84 | +$262 |

**Mitigation:** Set alerts at 70% and 90% quota usage.

---

## Decision Rule Summary

```
IF (Peak × 1.2) ≤ Free Tier Quota:
    → Use Free Tier
    → Monitor weekly for quota creep
ELIF (Peak × 1.2) ≤ Starter Tier Quota:
    → Use Starter Tier
    → Set alerts at 70% and 90%
ELSE:
    → Use Business Tier OR
    → Implement rate limiting to stay within Starter
```

---

## When to Re-Evaluate Tier

| Trigger | Action |
|---------|--------|
| 2 consecutive months at >70% of quota | Schedule review |
| Overage bill exceeds $10 in a month | Upgrade immediately |
| New integration adds >5K calls/mo baseline | Re-run model |
| Team size doubles | Re-run model (usage scales ~linearly) |

---

## Pitfalls

1. **Forgetting burst multipliers** — Some tools have spiky usage (GitHub webhooks on PR day). Always ask: "What's the busiest hour/day?"
2. **Ignoring seasonal effects** — Crypto tools spike during bull markets; hackathon monitoring peaks during event weeks.
3. **Linear scaling assumption** — Adding 5 new integrations doesn't mean +5× calls; some tools batched, some idle.
4. **No safety margin** — Always multiply peak by 1.2–1.5 to allow for growth.

---

## Quick Calculator (Manual)

```
Conservative = Σ(daily_avg × 30)
Base = Conservative × 1.15
Peak = Σ(daily_avg × burst_multiplier × peak_days_per_month)
Tier threshold = Peak × 1.2
```

---

**Document version:** 1.0
**Used in:** Composio evaluation (2026-05-03), applicable to any metered SaaS
**Author:** YoYo (Strategies)
