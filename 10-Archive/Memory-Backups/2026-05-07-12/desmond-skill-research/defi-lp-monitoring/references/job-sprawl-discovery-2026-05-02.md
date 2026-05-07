# DeFi Monitoring Job Sprawl — Discovery Log
**Date:** 2026-05-02
**Discovered by:** Desmond (Creative)
**Context:** Jordan requested dual-schedule milestone reporting (8:30 AM & 9:00 PM) plus silent 10-min LP range monitoring

## Initial State (Before Consolidation)

### How Sprawl Was Discovered

1. Jordan asked to change LP monitoring to:
   - Twice-daily milestone reports (8:30 AM, 9:00 PM)
   - Silent 10-min range crime job (alerts only when out of range)

2. Checked `hermes cron list` output — saw 6 active jobs but unclear which profile owns which

3. Inspected all `jobs.json` files across profiles:
   ```bash
   find /root/.hermes/profiles/*/cron/jobs.json -exec grep -H 'LP\|Milestone\|Watchlist' {} \;
   ```
   Revealed duplicate jobs in **dmob**, **desmond**, **yoyo**, and **gentech** profiles

4. Matched job names + schedules to map ownership:
   - DMOB: `Defi Milestone` (daily), `LP Range Monitor` (every 10 min, stale), `Consolidated Crypto Watchlist` (2h)
   - Desmond: `Defi Milestone` (daily duplicate), `YoYo — Crypto Watchlist + LP Monitor` (4× daily), `YoYo — LP Position Monitor` (10 min)
   - YoYo: `YoYo — Crypto Watchlist + LP Monitor` (4× daily), `YoYo — DeFi Milestone + LP Monitor` (daily, erroring)
   - Gentech: cloned YoYo watchlist (not loaded in hermes but present in jobs.json)

5. Verified no output logs existed in any `output/` directories — jobs may be failing silently or never firing due to script path issues

6. Checked authoritative script locations:
   - Vault master: `/root/vaults/gentech/03-Strategies/scripts/`
   - DMOB runtime copy: `/root/.hermes/profiles/dmob/home/.hermes/scripts/`

## Technical Findings

### Script Source of Truth

**Vault location:** `/root/vaults/gentech/03-Strategies/scripts/`

| Script | Purpose | Used By |
|--------|---------|---------|
| `d5-master-cron.py` | Daily milestone aggregator (reads milestone ladder, tracks tier progression) | DMOB `Defi Milestone` job |
| `d5-lp-consolidated.py` | LP range + efficiency monitor (15 min schedule) | DMOB `D5 Milestone` (every 15 min) |
| `lp-range-monitor-v3.py` | Silent range watcher (only alerts on breakout) | DMOB `LP Range Monitor` (every 10 min, currently stale) |

**Note:** `lp-range-monitor-v3.py` already implements Jordan's preferred behavior:
- In range + efficiency ≥ 75% → prints `SILENT` → no Telegram message
- Out of range → `ALERT:warning_<direction>` or `ALERT:red_breakout_<direction>`
- Milestone crossed → `MILESTONE:$X.XX` → always announces
- Low efficiency (< 75%) → still reports (configurable)

### Config File Sprawl

`.lfj-aae-config.json` exists in multiple locations (risk of drift):
1. `/root/.hermes/scripts/.lfj-aae-config.json` — main runtime (used by DMOB cron)
2. `/root/.hermes/profiles/gentech/scripts/.lfj-aae-config.json` — Gentech jobs
3. `/root/.hermes/profiles/yoyo/home/repos/gentech-vault/03-Strategies/scripts/.lfj-aae-config.json` — YoYo vault sync
4. `/root/vaults/gentech/00-HQ/config/defi-lp-config.env` — env backup (should match)

**Post-rebalance update command:**
```bash
find /root/.hermes -name ".lfj-aae-config.json" -exec cp /root/vaults/gentech/00-HQ/config/defi-lp-config.env {} \;
```

## Jordan's Preferences (May 2026)

### Milestone Reporting Cadence
- **Frequency:** Twice daily only
- **Times:** 08:30 AM and 09:00 PM (EDT)
- **Content:** Current tier, distance to next tier, today's fees, LP efficiency snapshot
- **Exceptions:** Send immediately if tier boundary crossed (milestone event)

### Range Monitoring Behavior
- **Frequency:** Every 10 minutes (crime job)
- **Silent when:** IN RANGE and efficiency ≥ 75%
- **Alert when:** OUT OF RANGE (warning → red escalation after 5 min)
- **Noise reduction:** Do NOT send Telegram message if `SILENT` status

## Consolidation Plan (Recommended)

### Phase 1 — Pause Duplicates (Safe, Reversible)
```bash
hermes cron pause 0c8debb70799   # Desmond Defi Milestone
hermes cron pause e00b46103b08   # Desmond YoYo Watchlist
hermes cron pause 0b2beec3f702   # Desmond LP Position Monitor
hermes cron pause faed4f588aef   # YoYo YoYo Watchlist
hermes cron pause cfa8d1c19357   # YoYo DeFi Milestone (erroring)
# Gentech jobs not loaded in hermes — edit jobs.json directly to remove
```

### Phase 2 — Update Schedules
- DMOB `Defi Milestone` (`3fc1a11a88d7`): change from `every 1440m` → `30 8,21 * * *`
- DMOB `LP Range Monitor` (`b2bb2bae4fc5`): ensure schedule `*/10 6-23 * * *` and script points to `lp-range-monitor-v3.py`

### Phase 3 — Verify Single Source
- Confirm only one job writes to `.lfj-aae-state.json`:
  ```bash
  lsof /root/.hermes/scripts/.lfj-aae-state.json 2>/dev/null
  ```
  Should show only one process (the authoritative job)

### Phase 4 — Clean Up Config Drift
- Re-sync all `.lfj-aae-config.json` copies to vault master
- Update milestone ladder in vault to match Jordan's current tier targets:
  ```json
  "milestones": [
    {"tier": 1, "label": "Scout",     "daily_fees": 5.0,   "unlocks": "Entry strategies (CURVE)"},
    {"tier": 2, "label": "Raider",    "daily_fees": 20.0,  "unlocks": "SPOT + BIDIRECTIONAL shapes"},
    {"tier": 3, "label": "Warlord",   "daily_fees": 55.0,  "unlocks": "Multi-pool positions"},
    {"tier": 4, "label": "Sovereign", "daily_fees": 200.0, "unlocks": "Custom strategy creation"}
  ]
  ```

---

## Related Commands

```bash
# List all jobs (all profiles)
hermes cron list

# Pause a duplicate job (keeps history)
hermes cron pause <job-id>

# Resume if needed
hermes cron resume <job-id>

# Check job output
ls -la ~/.hermes/profiles/<profile>/cron/output/<job-id>/

# Run job manually (test)
hermes cron run <job-id>

# Edit a job's prompt
hermes cron edit <job-id>  # opens editor

# Find all config copies
find /root/.hermes -name ".lfj-aae-config.json"

# Verify state file writers
lsof /root/.hermes/scripts/.lfj-aae-state.json
```

---

## Open Questions

- Should the Price Watchlist (YoYo job `faed4f588aef`) continue running at 4× daily, or is it redundant now that DMOB's watchlist runs every 2h?
- Does the `LP Range Monitor` job (`b2bb2bae4fc5`) need its prompt updated to reference the consolidated state, or does `lp-range-monitor-v3.py` already work standalone?
- Are there any Telegram group delivery differences between jobs that need standardizing?
