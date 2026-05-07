---
title: S2S Milestone Report JSON Schema
description: Canonical output format for Safe-to-Safe DeFi milestone analysis reports
updated: 2026-05-03
---

## File Location

`03-Projects/DeFi/s2s-milestone-report.json`

## Schema Structure

```json
{
  "timestamp": "2026-05-02T10:24:22.316110Z",
  "capital_update": {
    "status": "DCA_BOOST_DETECTED",
    "dca_injection_usd": 54.999999999999986,
    "dca_date": "2026-04-26",
    "last_recorded_total": 138.92,
    "current_total": 135.83,
    "net_change_since_injection": -3.089999999999975
  },
  "milestone_progress": {
    "milestone": "M2",
    "milestone_label": "Warlord+",
    "target_daily_fees_usd": 20.0,
    "current_daily_fees_est_usd": 0.19,
    "daily_yield_pct": 0.14,
    "apr_estimate_pct": 51.4,
    "fees_gap_daily_usd": 19.81,
    "gap_pct_of_target": 99.0
  },
  "capital_gap": {
    "principal_needed_at_current_yield_usd": 14205.26,
    "current_position_usd": 135.83,
    "gap_usd": 14069.43
  },
  "dca_path": {
    "weekly_dca_range_usd": [50, 100],
    "schedule": "Sun-Wed + Thu-Sat split",
    "weeks_to_target_at_50_usd": 281.4,
    "weeks_to_target_at_75_usd": 187.6,
    "weeks_to_target_at_100_usd": 140.7,
    "years_to_target_avg": 3.6
  },
  "pro_tips": [
    {
      "priority": 1,
      "title": "Range efficiency",
      "action": "Narrow range to $9.12–$9.18 (centered on $9.15)",
      "expected_impact": "Efficiency ↑42% → 70%+, daily fees $0.19 → ~$0.50"
    }
  ],
  "data_sources": {
    "position_tracker": "path/to/state.json",
    "config": "path/to/config.json",
    "vault_sync": "02-AAE/defi-position-log.md"
  }
}
```

## Field Explanations

### capital_update.status
- `DCA_BOOST_DETECTED`: position increased vs prior reading due to DCA injection
- `STEADY`: no significant change
- `DECLINED`: position decreased (IL or fee harvesting)

### milestone_progress
- `milestone`: current milestone identifier (M1, M2, M3, M4)
- `target_daily_fees_usd`: daily yield required to achieve and maintain this tier
- `apr_estimate_pct`: annualized rate based on recent pool volume and position share
- `gap_pct_of_target`: (current / target) × 100

### dca_path
Timeline projections at three DCA rates:
- Conservative: $50/week
- Baseline: $75/week (midpoint of [50,100] range)
- Aggressive: $100/week

All calculations assume no yield on DCA principal (simple) unless otherwise noted.

## Generation Rules

1. Capital Update: Compare `last_recorded_total` (from vault entry or previous report) with `current_total` (current combined LP + external wallet value)
2. DCA Detection: If `current_total - last_recorded_total ≥ $45` and within 48h of DCA window → `DCA_BOOST_DETECTED`
3. Milestone Selection: Use D5 tier ladder ($5/$20/$50/$100/$200 daily fees)
4. Pro Tips: Maximum three, sorted by impact magnitude; include efficiency, config drift, compounding cadence as applicable

## Consumer: AAE Frontend

This report feeds the DeFi Milestone Tracker UI cards. One card per section; timeline bars for DCA path; expandable pro tips.
