# LP Cron AAE Optimization — Desmond
**Date:** 2026-04-25  
**Status:** Done (1 item pending YoYo handoff)

---

## What Jordan Asked
Optimize the current LP + D5 milestone cron to reflect the AAE yield farm tracker work (frontend images + code dropped in HQ).

## What I Did

### 1. Updated Milestone Config to 8-Tier AAE Ladder
**File:** `~/.hermes/scripts/.lfj-aae-config.json` (vault mirror: `03-Strategies/scripts/`)

Aligned with `AAE-Signal-Spec-Structured.md` (Jordan confirmed dashboard elements):

| Tier | Label | Daily Fees | Unlock |
|------|-------|-----------|--------|
| 1 | Scout | $3 | Entry rank |
| 2 | Scout+ | $5 | Tighter ranges |
| 3 | Raider | $8 | SPOT shape |
| 4 | Raider+ | $10 | Bidirectional |
| 5 | Warlord | $15 | Multi-pool |
| 6 | Warlord+ | $20 | Custom ranges |
| 7 | Sovereign | $55 | Squad treasury |
| 8 | Freedom | $200 | Custom strategies |

### 2. Cleaned Up Desmond Profile Cron
**Job:** `2ca757ee055c` — "YoYo — LP + DeFi Milestone Tracker"

- **Removed** embedded sample output that had been accidentally pasted into the prompt
- **Standardized** on `lp-aae-monitor.py` (the script that matches AAE signal spec)
- **Schedule unchanged:** 4x/day at 8:25 AM, 12:25 PM, 4:25 PM, 8:25 PM ET
- **Deliver:** Origin (Strategies group)

### 3. Tested Script Output
- Ran `lp-aae-monitor.py` manually → returned `SILENT` (position healthy, in range)
- State file confirms 8-tier tracking active: `current_milestone_idx: 0`, est daily fees ~$0.20
- Working toward Tier 1 (Scout @ $3/day)

---

## 🔄 Pending: YoYo Handoff Needed
**Job:** `faed4f588aef` on **YoYo's profile** — "YoYo — AAE DeFi Milestone + LP Monitor"

- Runs daily at 10 AM, also runs `lp-aae-monitor.py`
- **Redundant** with the 4x/day Desmond profile cron
- Desmond can't access YoYo's profile to disable it

**Action needed:** YoYo (or Jordan) should pause/disable job `faed4f588aef` to prevent duplicate LP alerts.

---

### 4. Hybrid DCA Strategy Finalized
**Jordan's call:** Keep the weekly $50 Sunday DCA as a base commitment, but add a smaller $15 boost when fee efficiency drops below 50% (opportunistic, one side is cheap).

- Config updated: `dca.mode: hybrid`, `base_amount: 50`, `boost_amount: 15`, `boost_trigger_efficiency: 50`
- Cron prompt updated to reflect hybrid model
- Vault mirror synced

## Files Touched
- `~/.hermes/scripts/.lfj-aae-config.json` → 8-tier milestones + hybrid DCA
- `/root/vaults/gentech/03-Strategies/scripts/.lfj-aae-config.json` → synced mirror
- Desmond profile `jobs.json` → cleaned cron prompt for `2ca757ee055c`

## Next
- YoYo to disable `faed4f588aef`
- DMOB to scaffold contract structs per AAE Signal Spec Section 8 (when ready)
