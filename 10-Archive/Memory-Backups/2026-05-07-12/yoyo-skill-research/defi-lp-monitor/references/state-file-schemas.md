# LFJ Position State File Schemas

All state files live in `~/.hermes/scripts/` as hidden JSON files. They track position health, milestone progression, and range status.

---

## `.lfj-range-state.json` — Range Alert State

**Purpose:** Tracks whether position is in/out of range and last alert raised.

**Schema:**
```json
{
  "out_of_range_since": "2026-04-27T23:48:00-04:00" | null,
  "last_alert": "YELLOW_LOW_EFFICIENCY" | "GREEN_OK" | "RED_OUT_OF_RANGE",
  "last_price": 9.2509,
  "last_check": "2026-04-27T23:48:00-04:00",
  "data_source": "dexscreener" | "birdeye" | "rpc",
  "alert_reason": "Price at (n)% of range — approaching upper bound. Low fee efficiency (m%)."
}
```

**Fields:**
- `out_of_range_since`: ISO8601 timestamp when price first crossed outside range, or `null` if currently in range
- `last_alert`: Highest severity alert currently active
- `last_price`: Most recent price observed
- `last_check`: Timestamp of last successful price fetch
- `data_source`: Which API source provided the price (for debugging flaky sources)
- `alert_reason`: One-line human explanation (used in report generation)

**Updated by:** `d5-master-cron.py`, `lp-aae-signal-monitor.py` on each run.

---

## `.lfj-position-state.json` — Position Tracker

**Purpose:** Historical price recording and token split tracking for IL and rebalance decisions.

**Schema:**
```json
{
  "last_update": "2026-04-29T20:31:02Z",
  "price_history": [
    { "ts": 1777408740.6186345, "price": 9.1772 },
    { "ts": 1777408883.0446882, "price": 9.1772 }
  ],
  "last_price": 9.08596
}
```

**Fields:**
- `last_update`: ISO8601 UTC of last position snapshot
- `price_history`: Array of `{ts, price}` — timestamp is Unix float (seconds since epoch)
- `last_price`: Most recent recorded price (for quick access)

**Updated by:** `lp-aae-signal-monitor.py` primarily; `d5-master-cron.py` reads but doesn't write.

---

## `.lfj-milestone-tracker.json` — D5 Milestone Progression

**Purpose:** Tracks cumulative fees collected and milestone achievement status.

**Schema:**
```json
{
  "current_tier": 1,
  "current_label": "Scout",
  "daily_fees_usd": 0.04,
  "cumulative_fees_usd": 0.00,
  "next_tier": 2,
  "next_label": "Raider",
  "next_threshold_usd": 20.00,
  "progress_pct": 0.2,
  "consecutive_days_above_target": 3,
  "last_compound_date": "2026-04-27T12:00:00Z",
  "compound_threshold_usd": 50.00,
  "compound_ready": false
}
```

**Fields:**
- `current_tier`: Integer tier number (1–8)
- `current_label`: Human tier name (Scout, Raider, …)
- `daily_fees_usd`: Most recent 24h fee run-rate
- `cumulative_fees_usd`: Total fees collected since last rebalance/compound event
- `next_tier`: Next tier number (locked until current target achieved)
- `next_label`: Name of next tier
- `next_threshold_usd`: Daily fee target needed to unlock next tier
- `progress_pct`: `daily_fees_usd / next_threshold_usd × 100`
- `consecutive_days_above_target`: Days in a row current tier's target has been exceeded (crown job unlock condition)
- `last_compound_date`: When fees were last claimed/compounded
- `compound_threshold_usd`: Threshold to trigger compound action (default $50)
- `compound_ready`: Boolean — `true` when cumulative exceeds threshold

**Updated by:** `d5-master-cron.py` on each run; read by `d5-milestone-summary.py`.

---

## `.lfj-aae-config.json` — Master Configuration (canonical source)

**Purpose:** Single source of truth for all pipeline parameters.

**Schema:**
```json
{
  "pool_address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
  "chain": "avalanche",
  "rpc_url": "https://api.avax.network/ext/bc/C/rpc",
  "token0": {
    "symbol": "AVAX",
    "address": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
    "decimals": 18
  },
  "token1": {
    "symbol": "USDC",
    "address": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
    "decimals": 6
  },
  "wallet_address": "[REDACTED_WALLET]",
  "bin_step": 10,
  "fee_tier_bps": 5,
  "position": {
    "total_usd": 134.94,
    "token0_amount": 0.0,
    "token1_amount": 134.94,
    "range_low": 8.95,
    "range_high": 9.36,
    "shape": "curve",
    "rebalanced_at": "2026-04-29T11:10:00Z"
  },
  "milestones": [
    { "tier": 1, "label": "Scout",  "daily_fees": 3.0,  "description": "Entry rank — basic strategies" },
    { "tier": 2, "label": "Scout+", "daily_fees": 5.0,  "description": "Consistent earner — tighter ranges" },
    { "tier": 3, "label": "Raider", "daily_fees": 8.0,  "description": "Intermediate — SPOT shape" },
    { "tier": 4, "label": "Raider+", "daily_fees": 10.0, "description": "Advanced — bidirectional" },
    { "tier": 5, "label": "Warlord","daily_fees": 15.0, "description": "Multi-pool ready" },
    { "tier": 6, "label": "Warlord+","daily_fees": 20.0, "description": "High capital efficiency" },
    { "tier": 7, "label": "Sovereign","daily_fees": 55.0,"description": "Squad treasury mgmt" },
    { "tier": 8, "label": "Freedom","daily_fees": 200.0,"description": "Custom strategy creation" }
  ],
  "compound_threshold_usd": 50.0,
  "dca": {
    "base_amount": 50,
    "boost_amount": 15,
    "boost_trigger_efficiency": 50,
    "day_of_week": 0,
    "enabled": true,
    "mode": "hybrid"
  },
  "quiet_hours": {
    "start": 23,
    "end": 6,
    "timezone_offset": -4
  },
  "squad": {
    "squad_id": null,
    "contribution_pct": 100.0
  },
  "alert_rules": {
    "silent_if": ["in_range", "efficiency_ok", "no_action_needed"],
    "alert_if": ["out_of_range", "efficiency_low", "milestone_hit", "compound_ready", "dca_day"],
    "critical_if": ["price_crash", "il_severe"]
  }
}
```

**Important notes:**
- `range_low` / `range_high` in config should match active LP range
- `daily_fees` in milestones array is the **target** per-tier, not actual earned
- `shape`: one of `curve` (default), `spot` ( Concentrated at edges), `bidirectional` (two centering peaks)
- `position.rebalanced_at`: ISO8601 UTC timestamp of last manual/auto-rebalance

---

## State File Update Protocol

All scripts follow read-modify-write pattern:

```python
import json, os
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.lfj-range-state.json")

# 1. Read existing state
try:
    with open(STATE_FILE) as f:
        state = json.load(f)
except FileNotFoundError:
    state = {"out_of_range_since": None, "last_alert": None}

# 2. Update based on fresh data
state["last_price"] = current_price
state["last_check"] = datetime.now(timezone.utc).isoformat()

# 3. Write atomically (atomic write prevents corruption on crash)
import tempfile
with tempfile.NamedTemporaryFile('w', dir=os.path.dirname(STATE_FILE), delete=False) as tf:
    json.dump(state, tf, indent=2)
    temp_name = tf.name
os.replace(temp_name, STATE_FILE)  # atomic on POSIX
```

**Critical:** Always use `os.replace()` (atomic rename) to avoid partial-write corruption if the process is killed mid-write.