# AAE Signal Specification — DeFi LP Position + Progression

> Version: 2.0
> Date: 2026-04-25
> Scope: Squad Treasury + Squad Progression signals
> Source: Jordan's Yield Farm Tracker + Milestone Dashboard

---

## Overview

This document defines the structured signal format for AAE (Agent/Automated Agent Economy) DeFi position monitoring. All dashboard metrics from Jordan's personal LP tracker are formalized as typed fields for ingestion by squad treasury views, progression systems, and automated agents.

---

## Signal Types

| Type | Description | Trigger |
|------|-------------|---------|
| `POSITION` | Current LP position state | Every monitoring cycle |
| `MILESTONE` | Tier progression event | Daily fee crosses threshold |
| `ALERT` | Action-required condition | Out of range, low efficiency |
| `COMPOUND` | Compound opportunity | Cumulative fees ≥ threshold |
| `DCA` | DCA deployment reminder | Configured day of week |

---

## Core Signal Schema

### Position Identification

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `timestamp` | ISO8601 string | `"2026-04-25T11:45:00-04:00"` | Signal generation time |
| `signal_type` | enum | `"POSITION"` | Signal category |
| `severity` | enum | `"SILENT"` | `SILENT`, `OK`, `ALERT`, `CRITICAL` |
| `pool_address` | address | `"0x864d...16ea"` | LP pool contract address |
| `chain` | string | `"avalanche"` | Blockchain network |
| `token0_symbol` | string | `"AVAX"` | Base token symbol |
| `token1_symbol` | string | `"USDC"` | Quote token symbol |
| `data_source` | string | `"dexscreener"` | Primary data source used |
| `squad_id` | string \| null | `"squad-alpha-1"` | Optional squad identifier |

### Price Data

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `price` | float | `9.4566` | Current token0 price in token1 |
| `price_change_24h` | float \| null | `-2.5` | 24h price change % |
| `range_low` | float | `9.33` | Lower bound of LP range |
| `range_high` | float | `9.52` | Upper bound of LP range |
| `in_range` | boolean | `true` | Price within range bounds |
| `fee_efficiency` | float | `87.5` | % of max fee capture (0-100) |
| `shape` | enum | `"curve"` | `curve`, `spot`, `bidirectional` |

### Squad Treasury Metrics

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `position_value_usd` | float | `83.92` | Total position value in USD |
| `token0_split_pct` | float | `39.5` | % of position in token0 |
| `token1_split_pct` | float | `60.5` | % of position in token1 |
| `fees_24h` | float | `0.33` | Estimated fees earned (24h) |
| `fees_since_deposit` | float | `12.45` | Cumulative fees since tracking start |
| `claimable_rewards_usd` | float | `1.13` | Rewards ready to compound |
| `apr` | float | `5138.0` | Annual percentage rate from volume |

### Squad Progression Metrics

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `current_tier` | int | `1` | Current milestone tier (1-indexed) |
| `current_tier_label` | string | `"Scout"` | Human-readable rank name |
| `next_tier` | int | `2` | Next milestone tier |
| `next_tier_label` | string | `"Raider"` | Next rank name |
| `progress_to_next_pct` | float | `6.6` | % progress toward next tier |
| `days_in_range` | float | `14.3` | Cumulative days position was in range |

### Action Signals

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `compound_ready` | boolean | `false` | Cumulative fees ≥ compound threshold |
| `dca_ready` | boolean | `false` | Today is configured DCA day |
| `suggested_action` | string | `"HOLD: Position healthy..."` | Human-readable recommended action |

---

## Severity Logic

```python
def determine_severity(in_range, efficiency, compound_ready, dca_ready, milestone_changed):
    if not in_range:
        return "ALERT"
    if efficiency < 30:
        return "CRITICAL"
    if efficiency < 50:
        return "ALERT"
    if compound_ready or dca_ready or milestone_changed:
        return "OK"
    return "SILENT"
```

| Severity | Telegram | AAE Ingestion | Use Case |
|----------|----------|---------------|----------|
| `SILENT` | No | Yes (log only) | Healthy position, routine monitoring |
| `OK` | Yes | Yes | Milestone, compound, or DCA event |
| `ALERT` | Yes + mention | Yes | Action needed (rebalance, check position) |
| `CRITICAL` | Yes + urgent | Yes + escalate | Immediate risk (severe IL, crash) |

---

## Tier System

### Tier Definitions

| Tier | Label | Daily Fee Target | Shape Unlock | Description |
|------|-------|-----------------|--------------|-------------|
| 1 | Scout | $5/day | CURVE | Entry rank — basic strategies |
| 2 | Raider | $20/day | SPOT + BIDIRECTIONAL | Intermediate — multi-shape |
| 3 | Warlord | $55/day | Multi-pool | Advanced — portfolio LP |
| 4 | Sovereign | $200/day | Custom creation | Freedom milestone |

### Progress Calculation

```python
progress_pct = ((current_daily_fees - current_tier_target) 
                / (next_tier_target - current_tier_target)) * 100
```

- Clamped to `[0, 100]`
- Returns `100.0` if at max tier

---

## Fee Efficiency by Shape

### Curve (Default)
```
position = (price - range_low) / (range_high - range_low)
efficiency = (1 - abs(position - 0.5) * 2) * 100
```
- Peak at center (50%)
- Zero at edges

### Spot
```
efficiency = 100 if in_range else 0
```
- Uniform within range
- Binary out of range

### Bidirectional
```
position = (price - range_low) / (range_high - range_low)
efficiency = abs(position - 0.5) * 2 * 100
```
- Peak at edges
- Zero at center

---

## Data Source Priority

| Priority | Source | Auth | Fallback Latency |
|----------|--------|------|-----------------|
| 1 | Birdeye x402 | API key required | ~500ms |
| 2 | DexScreener | None | ~300ms |
| 3 | On-chain RPC | None | ~800ms (no volume) |

---

## State Persistence

### File: `.lfj-aae-state.json`

```json
{
  "tracking_started": "2026-04-18T09:00:00-04:00",
  "total_fees_earned_usd": 12.45,
  "total_days_in_range": 14.3,
  "last_in_range_check": "2026-04-25T11:00:00-04:00",
  "current_milestone_idx": 0,
  "last_compound_date": null,
  "last_dca_date": "2026-04-21T08:00:00-04:00",
  "compound_events": [],
  "daily_fee_log": [],
  "price_history": [9.45, 9.46, 9.44],
  "alert_history": [],
  "out_of_range_since": null,
  "last_alert": "2026-04-24T16:25:00-04:00",
  "last_price": 9.4566,
  "last_check": "2026-04-25T11:45:00-04:00"
}
```

---

## Integration Points

### AAE Squad Treasury View
- Consumes: `position_value_usd`, `token0_split_pct`, `token1_split_pct`, `fees_24h`, `claimable_rewards_usd`, `in_range`, `fee_efficiency`
- Display: Real-time position card with range status badge

### AAE Squad Progression View
- Consumes: `current_tier`, `current_tier_label`, `progress_to_next_pct`, `next_tier_label`, `days_in_range`
- Display: Rank badge, progress bar, days to next tier estimate

### AAE Alert Router
- Consumes: `severity`, `suggested_action`, `signal_type`
- Routes: Telegram bot (immediate), in-app notification ( batched), email digest (daily)

### AAE Compound Agent
- Consumes: `compound_ready`, `claimable_rewards_usd`, `fees_since_deposit`
- Triggers: Auto-compound transaction (with squad vote if > threshold)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-18 | Initial LP monitor (text output only) |
| 2.0 | 2026-04-25 | Structured AAE signals, tier system, multi-shape support, squad context |

---

## Tags
#project:aae #spec:signal #layer:body #integration:treaury #integration:progression
