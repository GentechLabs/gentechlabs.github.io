## Tactical Retreat — Phase 1 Build
**Adds:** Breakout detection timer + defense state machine to LP monitor
**Target file:** `/root/.hermes/profiles/gentech/scripts/lp-monitor-v2.py`
**State file:** `.lfj-defi-state.json` (updated with defense fields)

### What changes

**1. New defense state fields in .lfj-defi-state.json:**
- `defense_mode`: `null` | `"SENTINEL"` | `"RETREATED"` — tracks current defense posture
- `breakout_start`: ISO timestamp when continuous out-of-range *started* (null = in range)
- `breakout_confirmed`: `true` / `false` — true when timer exceeds threshold
- `breakout_threshold_seconds`: configurable (default 180 = 3 min)
- `last_defense_action`: ISO timestamp of last retreat/entry

**2. State machine flow:**

```
IN RANGE → null defense, reset breakout_start
     ↓ (price exits range)
OUT OF RANGE → set breakout_start = now, defense_mode = "SENTINEL"
     ↓ (stays out for X seconds)
BREAKOUT CONFIRMED → defense_mode = "RETREATED", emit signal
     ↓ (price re-enters)
RECOVERED → reset everything, null defense
```

**3. Integration points:**
- fed-event-tracker.py can set `defense_mode = "SENTINEL"` 24h before FOMC
- Cron-readable: report includes defense posture
- Future: wire to auto-action (retreat position)

### Files to modify
- `/root/.hermes/profiles/gentech/scripts/lp-monitor-v2.py` — add timer + state
- No new files needed
