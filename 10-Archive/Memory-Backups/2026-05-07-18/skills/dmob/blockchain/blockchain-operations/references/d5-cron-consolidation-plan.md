# Consolidation Plan: Remove Daily D5 Cron, Enable Hourly Unified

## Problem
Two parallel systems computing fee efficiency differently:
- Daily: `d5-master-cron.py` + `d5-milestone-summary.py` (standalone, duplicates logic)
- Hourly: `lp-aae-signal-monitor.py` (intended unified, currently broken, not scheduled)

## Steps to Consolidate

### 1. Fix Unified Script
```bash
python3 /root/vaults/gentech/03-Strategies/scripts/lp-aae-signal-monitor.py
```
Fix `NameError: EFFICIENCY_RED_THRESHOLD` by adding:
```python
EFFICIENCY_RED_THRESHOLD = 0.30   # 30%
EFFICIENCY_YELLOW_THRESHOLD = 0.50  # 50%
```

Add out-of-range debounce logic in `determine_severity()`:
- Track `out_of_range_since` timestamp in state
- If price exits range: set timestamp = now
- If price re-enters before 10 min: clear timestamp, status = OK
- If out-of-range for 10+ minutes but <15: status = WATCH (confirming)
- If out-of-range for 15+ minutes: status = ALERT/CRITICAL (red alert)

### 2. Update Milestone Thresholds Everywhere
**Files to patch:**
- `~/.hermes/scripts/.lfj-aae-config.json` → milestones array
- `/root/vaults/gentech/03-Strategies/scripts/d5-master-cron.py` → MILESTONES list
- `/root/vaults/gentech/03-Strategies/scripts/d5-milestone-summary.py` → MILESTONES list
- `/root/vaults/gentech/03-Strategies/scripts/lp-aae-signal-monitor.py` → MILESTONES dict

**New thresholds:**
```json
[
  {"tier": 1, "label": "Scout",     "daily_fees": 5.0},
  {"tier": 2, "label": "Raider",    "daily_fees": 20.0},
  {"tier": 3, "label": "Warlord",   "daily_fees": 50.0},
  {"tier": 4, "label": "Sovereign", "daily_fees": 100.0},
  {"tier": 5, "label": "Freedom",   "daily_fees": 200.0}
]
```

### 3. Switch Hermes Cron
```bash
# Remove old daily job
hermes cron remove 3fc1a11a88d7

# Create new hourly job (7AM–9PM EDT = 11:00–23:00 UTC)
hermes cron create \
  --name "LP Position Monitor Hourly" \
  --schedule "0 11-23/1 * * *" \
  --skill "blockchain-operations" \
  --command "python3 /root/vaults/gentech/03-Strategies/scripts/lp-aae-signal-monitor.py" \
  --deliver origin
```

Expected job ID: `faed4f588aef` (or new UUID)

### 4. Archive Legacy Scripts
Move to archive or add `.bak` suffix:
```bash
mv /root/vaults/gentech/03-Strategies/scripts/d5-master-cron.py{,.bak-$(date +%Y-%m-%d)}
mv /root/vaults/gentech/03-Strategies/scripts/d5-milestone-summary.py{,.bak-$(date +%Y-%m-%d)}
```

Keep them until unified script proves stable for 1 week.

## Verification
1. Run unified script manually → no errors, sensible output
2. `hermes cron list` → shows new hourly job active
3. Check next run time aligns with schedule
4. Wait for first automated run → verify Telegram message arrives with correct thresholds
