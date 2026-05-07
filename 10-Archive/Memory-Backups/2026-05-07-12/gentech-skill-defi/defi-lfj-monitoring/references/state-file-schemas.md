# State File JSON Schemas — LFJ Monitoring Persistence

State files live in `~/.hermes/scripts/` (Gentech profile) and must be JSON-serializable. These are **persistent across runs**; do not delete unless resetting.

---

## 1. `.lfj-position-state.json`

Tracks last-known price, alert status, cumulative metrics.

```json
{
  "warning_sent": false,
  "last_price": 9.25,
  "last_check": "2026-04-28 01:09 UTC",
  "last_alert": "NONE",
  "total_days_in_range": 0.0,
  "total_fees_earned_usd": 0.0,
  "current_milestone_idx": 0,
  "price_history": [9.11, 9.12, 9.10, ...]  // last 100 prices
}
```

**Fields**:
- `warning_sent` — has out-of-range alert been sent? (suppresses duplicates)
- `last_price` — last AVAX/USDC price observed
- `last_check` — ISO timestamp of last run
- `last_alert` — `NONE` / `YELLOW` / `RED` / `RECOVERED`
- `total_days_in_range` — sum of `(1/144)` per minute in range (144 ticks = 1 day at 5min intervals)
- `total_fees_earned_usd` — cumulative fees since first tracked (not just active period)
- `current_milestone_idx` — index into `milestones[]` array (-1 = unranked, 0 = Scout, …)
- `price_history` — rolling 100-entry list for volatility analysis

**Updated by**: `lp-aae-signal-monitor.py`, `lfj_monitor.py`  
**Read by**: `d5-master-cron.py` (for trend detection)

---

## 2. `.lfj-milestone-tracker.json`

Tracks crown milestones (cumulative fee thresholds reached).

```json
{
  "milestones_reached": [0.5, 1.0],
  "last_milestone": 1.0
}
```

**Fields**:
- `milestones_reached` — sorted array of crown thresholds hit (float values)
- `last_milestone` — most recent crown value (null if none)

**Updated by**: `lp-range-monitor-v3.py` via `update_milestone(fees_earned, price, efficiency)`  
**Read by**: `lp-aae-signal-monitor.py` (for celebration triggers), vault logging

**Note**: This file is **not** auto-created by all scripts. If missing, `lp-range-monitor-v3.py` will create it on first run. If you see `FileNotFoundError`, run that script once or manually `touch` the file with `{}`.

---

## 3. `.lfj-efficiency-trend.json`

Tracks efficiency history for dashboard/trend analysis.

```json
{
  "efficiencies": [
    {
      "timestamp": "2026-05-02T06:23:00Z",
      "efficiency_pct": 50.3,
      "price": 9.1132,
      "in_range": true
    },
    ...
  ]
}
```

**Fields per entry**:
- `timestamp` — ISO UTC time of reading
- `efficiency_pct` — capital efficiency from share-weighted calculation
- `price` — AVAX/USDC price at reading
- `in_range` — boolean (within strategic band)

**Updated by**: `lp-aae-signal-monitor.py` (appends each run)  
**Used by**: Yoyo's efficiency dashboard; trend analysis

---

## 4. `.lfj-aae-config.json` (Configuration, not state, but co-located)

Master config pool params + milestone ladder + DCA rules.

```json
{
  "pool_address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
  "chain": "avalanche",
  "bin_step": 10,
  "fee_tier_bps": 5,
  "position": {
    "total_usd": 134.94,
    "token0_amount": 3.446,
    "token1_amount": 103.38,
    "range_low": 9.0,
    "range_high": 9.3,
    "shape": "curve"
  },
  "milestones": [  // Ladder A from reference file
    {"tier":1,"label":"Scout","daily_fees":3.0,"description":"..."},
    ...
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
  "squad": {"squad_id": null, "contribution_pct": 100.0}
}
```

**Primary location**: `~/.hermes/scripts/.lfj-aae-config.json`  
**Backup location**: `/root/vaults/gentech/03-Strategies/scripts/.lfj-aae-config.json`

**DO NOT** edit the backup without updating primary. Use `diff` then sync both.

---

## File Location Map

| File | Primary | Backup / Vault | Created By |
|------|---------|----------------|------------|
| `.lfj-position-state.json` | `~/.hermes/scripts/` | — | `lp-aae-signal-monitor.py` |
| `.lfj-milestone-tracker.json` | `~/.hermes/scripts/` | — | `lp-range-monitor-v3.py` |
| `.lfj-efficiency-trend.json` | `~/.hermes/profiles/yoyo/home/.hermes/scripts/` | — | `lp-aae-signal-monitor.py` |
| `.lfj-aae-config.json` | `~/.hermes/scripts/` | `/root/vaults/gentech/03-Strategies/scripts/` | manual / DMOB |

**⚠️ Path bug**: Yoyo profile scripts write to a nested home path. If running as Yoyo, use:
```bash
STATE_DIR=~/.hermes/profiles/yoyo/home/.hermes/scripts/
```

**DMOB fix**: Symlink all state files to a unified location:
```bash
ln -sf ~/.hermes/scripts/.lfj-* ~/.hermes/profiles/yoyo/home/.hermes/scripts/
```

---

## Validation CLI

Before running any monitoring script, verify state integrity:

```bash
#!/usr/bin/env python3
import json, os, sys

STATE_DIR = os.path.expanduser("~/.hermes/scripts")
REQUIRED = [".lfj-position-state.json", ".lfj-aae-config.json"]
OPTIONAL = [".lfj-milestone-tracker.json", ".lfj-efficiency-trend.json"]

for fname in REQUIRED:
    path = os.path.join(STATE_DIR, fname)
    if not os.path.exists(path):
        print(f"❌ MISSING: {fname}")
        sys.exit(1)
    try:
        with open(path) as f:
            json.load(f)
        print(f"✅ {fname} — valid JSON")
    except json.JSONDecodeError:
        print(f"❌ {fname} — malformed JSON")
        sys.exit(1)

for fname in OPTIONAL:
    path = os.path.join(STATE_DIR, fname)
    if os.path.exists(path):
        try:
            with open(path) as f:
                json.load(f)
            print(f"✅ {fname} — valid JSON")
        except json.JSONDecodeError:
            print(f"⚠️  {fname} — malformed, will be overwritten")
    else:
        print(f"⚪ {fname} — missing (optional)")

print("✅ State validation passed")
```

Save as `scripts/validate-lfj-state.py` and run pre-cron.

---

## Reset Procedures

**Full reset** (corrupted state, garbage metrics):
```bash
cd ~/.hermes/scripts
mv .lfj-position-state.json .lfj-position-state.json.bak
mv .lfj-milestone-tracker.json .lfj-milestone-tracker.json.bak
mv .lfj-efficiency-trend.json .lfj-efficiency-trend.json.bak
# Then rerun lp-aae-signal-monitor.py to regenerate clean slate
```

**Config reset** (accidental edits):
```bash
# Restore from vault backup
cp /root/vaults/gentech/03-Strategies/scripts/.lfj-aae-config.json ~/.hermes/scripts/
```

---

*Last updated: 2026-05-02 — initial schema capture after first multi-script integration test.*