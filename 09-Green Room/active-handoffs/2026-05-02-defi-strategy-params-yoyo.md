---
handoff_id: H2026-05-02-02
from: Gentech (CEO)
to: YoYo (GenTech Strategies)
date: 2026-05-02
status: 🚀 Pending Ack
priority: P0
deadline: 2026-05-03 (EOD)
---

## Task

Define and document **strategy parameters** for the enhanced D5 Milestone cron logic.

## Background

Jordan approved new monitoring rules (May 2 voice msg): 5-min breakout confirmation, efficiency ≤30% immediate rebalance flag, bid-ask edge accumulation strategy. DMOB will implement code; you own the numeric thresholds and strategy rationale.

**Reference doc:** `03-Strategies/Defi-Monitor/d5-milestone-enhancements-2026-05.md`

## What Needs To Be Done

### 1. Confirm Config Values

Update `00-HQ/config/defi-lp-config.env` with:

| Parameter | Proposed | Your Action |
|-----------|----------|-------------|
| `BID_ASK_BOOST_MULTIPLIER` | `1.5` | Confirm or set final value |
| `LOWER_EDGE_BUFFER_PCT` | `0.02` (2%) | Confirm or adjust buffer size |
| `EFFICIENCY_IMMEDIATE_ALERT_THRESHOLD` | `30` | Confirm 30% is correct for curve shape |
| `EFFICIENCY_WATCH_THRESHOLD` | `50` | Existing — verify |
| `TARGET_LOW` / `TARGET_HIGH` | (optional) inside range | Define if you want tighter strategic band |

**Current pool config** (in `d5-master-cron.py`):
```python
POOL = {
    "range_low": 8.95,
    "range_high": 9.36,
    "shape": "curve",
}
```

### 2. Write Strategy Note

Create file: `03-Strategies/Defi-Monitor/strategy-params-2026-05.md`

Contents:
- Why these thresholds (curve shape fee efficiency curve)
- Bid-ask opportunity thesis (price near lower edge + 30–50% eff = accumulation)
- DCA boost logic rationale (temporary 1.5× for 3 cycles)
- Cross-check against D5 milestone ladder ($5/$20/$55/$200)
- Risk notes (false breakout risk in choppy markets)

### 3. Sync with DMOB

Once you set values in `defi-lp-config.env`, notify DMOB so they can harden the code (read env at runtime, not hardcoded).

## Files to Modify

| File | Your Change |
|------|-------------|
| `00-HQ/config/defi-lp-config.env` | Add new parameters (BID_ASK_BOOST_MULTIPLIER, etc.) |
| `03-Strategies/Defi-Monitor/strategy-params-2026-05.md` | Write one-page strategy doc |

## Acceptance Criteria

- [ ] Config file contains all new keys with numeric values
- [ ] Strategy doc explains rationale for each threshold
- [ ] DMOB has been pinged (in `GenTech Labs` or Green Room) that config is ready
- [ ] Values align with Jordan's curve/edge description ("30% or below")

## Questions for You

1. Is 30% efficiency the correct "edge zone" cutoff for **curve** shape? (Script uses curve math; spot/bidirectional may differ — confirm curve only)
2. Should the bid-ask edge buffer be fixed at 2% or dynamic based on volatility? (Simple is fine: `price ≤ range_low * 1.02`)
3. How many DCA cycles should the boost last? (suggestion: 3 cycles ≈ 3 days if 4× daily)
4. Do we need a "panic zone" at `eff < 20%` with separate messaging? (Current bands: ≥70% center, 50–70% mid, 30–50% low, <30% edge/crash)

## Coordination

- After writing config + doc, change handoff status to `🟢 Ready for DMOB`
- Post a one-liner in `GenTech Strategies` group: "D5 strategy params set — see 03-Strategies/Defi-Monitor/strategy-params-2026-05.md"
- Tag DMOB if they need clarification

---

**BRAIN LAYER REGISTRATION:** Yes — handoff registered under Active Handoffs
