# DeFi LP Monitor — Two-Tier Alert System

> Updated: 2026-06-14
> Cron Job ID: 1b603cdca003
> Schedule: Every 10 minutes (6 AM - 11 PM)
> Delivery: Strategies group (telegram:-1002916759037)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEFI LP MONITOR (10min)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐                                           │
│  │ Check AVAX Price │ (DexScreener API)                        │
│  └────────┬─────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌──────────────────┐    YES    ┌─────────────────┐            │
│  │ Within 5% of     │─────────▶│ TIER 1: Warning │            │
│  │ range boundary?  │          │ "Approaching..." │            │
│  └────────┬─────────┘          └────────┬────────┘            │
│           │ NO                          │                       │
│           ▼                             ▼                       │
│  ┌──────────────────┐          ┌─────────────────┐            │
│  │ Check fee        │          │ Wait 5 minutes  │            │
│  │ efficiency       │          │ Re-check price  │            │
│  └────────┬─────────┘          └────────┬────────┘            │
│           │                             │                       │
│           ▼                             ▼                       │
│  ┌──────────────────┐          ┌─────────────────┐            │
│  │ If < 50%:        │          │ Still broken?   │            │
│  │ TIER 2: Efficiency│         │ YES → TIER 2    │            │
│  │ "Rebalance now"  │          │ NO → All clear  │            │
│  └──────────────────┘          └─────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Alert Types

| Tier | Trigger | Message | Action |
|------|---------|---------|--------|
| **Tier 1** | Price within 5% of range edge | ⚠️ Warning | Monitor |
| **Tier 2** | Price breaks range | 🔴 Action | Rebalance |
| **Efficiency** | Fee efficiency < 50% | 📉 Optimize | Rebalance to center |
| **All Clear** | Price returns to range | ✅ Safe | No action |

## Workflow

1. **Cron job checks** every 10 minutes
2. **Alert fires** → Jordan gets Telegram notification
3. **Check dashboard** → Verify at https://protojay4789.github.io/DeFi/defi-dashboard.html
4. **Go to Trader Joe** → Rebalance position
5. **Dashboard updates** → Auto-refresh every 60 seconds

## Fee Efficiency Formula

```
Fee Efficiency = (Actual Fees Earned / Maximum Possible Fees) × 100

If efficiency < 50%:
  → Position is too far from current price
  → Rebalancing to center could double daily earnings
  → Alert: "Rebalancing now could increase daily earnings by X%"
```

## Integration Points

| Component | Role |
|-----------|------|
| **Cron Job** | Mobile notifications (Strategies group) |
| **Dashboard** | Visual verification (auto-refresh 60s) |
| **Trader Joe** | Execute rebalance (manual) |
| **DexScreener** | Live price data |
| **LFJ Subgraph** | Position data |

## Related

- Dashboard: https://protojay4789.github.io/DeFi/defi-dashboard.html
- Cron Job: `1b603cdca003` (*/10 6-23 * * *)
- Delivery: Strategies group
