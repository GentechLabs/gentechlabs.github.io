---
name: defi-milestone-cron-operations
description: Check status, troubleshoot, and manually run DeFi milestone cron jobs in Hermes Agent
triggers:
  - "check d5 cron status"
  - "run d5 milestone job"
  - "d5 milestone crown jobs"
  - "defi milestone cron"
  - "hermes d5 cron"
  - "milestone cron job not running"
models: []
---

# Defi Milestone Cron Job Operations

Manage and inspect the D5 Milestone cron job within Hermes Agent's scheduled task system.

## Quick Reference

### DeFi Milestone Reports (Twice Daily — DMob)
**Job names:** `Defi Milestone — Morning`, `Defi Milestone — Evening`  
**Job IDs:** `f709d93b25ab` (morning), `6a85a903e471` (evening)  
**Schedule:** `30 8 * * *` (08:30 UTC) and `0 21 * * *` (21:00 UTC daily)  
**Deliver:** origin (Strategies thread 5930)  
**Skills used:** Consolidated Crypto Watchlist, LP Position Monitor, trade-off-platform  
**Note:** Original single daily job (ID `3fc1a11a88d7`) is now disabled.

### DeFi Milestone + LP Monitor (Every 10 min — YoYo)
**Job name:** `DeFi Milestone`  
**Job ID:** `3258c64b`  
**Schedule:** `*/10 6-23 * * *` (every 10 min, 6 AM–11 PM UTC)  
**Script:** `d5-lp-consolidated.py` (now `defi-milestone-consolidated.py` in vault)  
**Deliver:** telegram:-1002916759037  
**Silent-if-OK:** After 2 consecutive clean runs, further OK-status messages are suppressed until the hour changes. Alerts (out-of-range confirmed, low efficiency, milestones) always break silence and reset the OK-counter.

**Behavior:** Monitors LFJ AVAX/USDC LP with 5-minute debounce, dynamic DCA zones ($50/$30/$20/$10), shape-aware rebalance suggestions, milestone ladder tracking, and hourly broadcast throttling to reduce noise.

## Commands

### List all Hermes cron jobs
```bash
hermes cron list
```

### Check specific job status
```bash
hermes cron status
# Shows all active jobs, next run times, and last run results
```

### Manually trigger a job (immediate run)
```bash
hermes cron run <job-id>
# Example:
hermes cron run 3fc1a11a88d7
```
Note: The job runs on the next scheduler tick (usually within 1 minute). It does **not** execute immediately in the foreground.

### Run diagnostic script (from this skill)
```bash
# From the skill directory:
python3 scripts/check_d5_cron_health.py
# Or from anywhere:
python3 ~/.hermes/profiles/dmob/skills/devops/defi-milestone-cron-operations/scripts/check_d5_cron_health.py
```

### View job details
```bash
hermes cron list  # shows ID, schedule, next run, last run status
# Job details are stored in: ~/.hermes/profiles/<profile>/cron/
```

### Verify AAE config consistency (vault vs runtime)
```bash
# After making milestone config changes, ensure all Hermes profiles have the latest copy
python3 ~/.hermes/profiles/dmob/skills/devops/defi-milestone-cron-operations/scripts/verify_aae_config_consistency.py
# Exit 0 = all in sync; 1 = mismatch; 2 = file missing
```

### Check gateway status (required for cron to fire)
```bash
hermes status
# Verify "Gateway is running" before relying on scheduled execution
```

## Provider Pinning (Critical)

All DMOB cron jobs MUST have `model` and `provider` set explicitly. When `model: null`, Hermes falls through provider resolution — often hitting dead OAuth tokens (Nous 401) or unconfigured providers.

**Current provider:** `custom:XiaomiMega` / `mimo-v2.5`
- Custom provider name in config: `XiaomiMega` (under `custom_providers:` section)
- Cron model override format: `{"provider": "custom:XiaomiMega", "model": "mimo-v2.5"}`
- ⚠️ **Never use bare `custom`** — always `custom:<name>` with the suffix

**Pin all jobs after any config change:**
```bash
hermes cron update <job_id> --model '{"provider":"custom:XiaomiMega","model":"mimo-v2.5"}'
```

See `references/provider-config.md` for the full provider setup and naming rules.

## Diagnosing Cron Failures

### Read `jobs.json` directly for per-job errors
The `cronjob list` tool shows `last_status: error` but NOT the error message. To see actual errors:

```bash
# DMOB profile jobs:
cat /root/.hermes/profiles/dmob/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    if j.get('last_status') == 'error':
        print(f\"{j['name']}: {j.get('last_error', 'N/A')}\")
"
```

**Common error patterns:**
- `401 - API key invalid, blocked or out of funds` → Provider key dead (check which provider)
- `No LLM provider configured` → Provider resolution failed (needs explicit pin)
- `Not supported model mimo-2.5-pro` → Wrong model name (use `mimo-v2.5`)
- `Refresh session has been revoked` → OAuth token expired (`hermes model` to re-auth)

### Check gateway logs for runtime errors
```bash
tail -50 /root/.hermes/logs/errors.log
```

## Common Issues & Fixes

### ❌ Job failing with "No Anthropic credentials found"
**Cause:** The D5 milestone script requires Anthropic API key for LLM-based analysis.
**Fix:**
```bash
export ANTHROPIC_API_KEY=<your-key>
# Or use hermes auth to store credentials
hermes login anthropic
```
Alternatively, set `ANTHROPIC_TOKEN` or `ANTHROPIC_API_KEY` environment variable in your shell profile or Hermes config.

### ❌ Job shows "error" in last run
**Diagnose:**
1. Read `jobs.json` directly (see "Diagnosing Cron Failures" above) to get the actual error message
2. Check gateway: `hermes status`
3. Verify model/provider pin is set: `hermes cron list` — should show `model` and `provider` fields
4. Check script files exist in `~/.hermes/profiles/<profile>/scripts/`
5. Review logs: `tail -50 ~/.hermes/logs/errors.log`

### ❌ Cron job not firing
**Checklist:**
- Gateway PID is running (`hermes status` shows PIDs)
- Job is marked `[active]` in `hermes cron list`
- System time is correct (cron uses system clock)
- No overlapping lock files in cron directory

### ⚠️ Milestone ladder out of sync after config change
**Cause:** AAE config (`.lfj-aae-config.json`) exists in vault AND in 7+ runtime locations. Cron jobs use the runtime copy.
**Fix:** After updating the vault config, propagate to ALL runtime locations:
```bash
SRC=/root/vaults/gentech/03-Strategies/scripts/.lfj-aae-config.json
for dest in \
  /root/.hermes/scripts/ \
  /root/.hermes/profiles/dmob/home/.hermes/scripts/ \
  /root/.hermes/profiles/yoyo/home/.hermes/scripts/ \
  /root/.hermes/profiles/desmond/home/.hermes/scripts/ \
  /root/.hermes/profiles/gentech/home/.hermes/scripts/ \
  /root/.hermes/profiles/gentech/.hermes/scripts/ \
  /root/.hermes/profiles/gentech/scripts/; do
  cp "$SRC" "$dest" 2>/dev/null
done
echo "Synced to all profiles"
```
Verify: `grep range_low /root/.hermes/scripts/.lfj-aae-config.json`

## File Locations

| Item | Path |
|------|------|
| Job scripts | `~/.hermes/profiles/<profile>/scripts/` |
| State files | `~/.hermes/scripts/` (shared) |
| Cron DB | `~/.hermes/kanban.db` (internal) |
| Logs | `~/.hermes/logs/` |

## Updating LP Range Configuration

When adjusting the price range for an LFJ (Trader Joe) concentrated liquidity position, multiple configuration files must be updated consistently to ensure all monitoring tools and cron jobs use the same parameters.

### Step 0: Verify On-Chain Range First (CRITICAL)

Before updating ANY config, confirm the actual on-chain range via bin scan. Configs can be stale from planned-but-not-executed rebalances. See `references/onchain-bin-scan-technique.md` in the `de-fi-lp-milestone-analysis` skill for the full RPC probe script.

Quick check: if `lp-position-reader.py` shows unusual shape (e.g., 98% USDC) but claims "IN RANGE", the config range is likely wrong. Run the bin scan to get ground truth.

### Configuration Files to Update

1. **Position Tracker** (`~/.hermes/scripts/.lfj-position-tracker.json`)
   - Update `position.range.low` and `position.range.high`
   - Also update top-level `range_low` and `range_high` fields
   - Set `position.range.updated_at` to current timestamp

2. **Python Scripts with Hardcoded Ranges**
   - `lp-range-monitor-v2.py`: Update `RANGE_LOW` and `RANGE_HIGH` constants
   - `lp-range-monitor-v3.py`: Update `RANGE_LOW` and `RANGE_HIGH` constants
   - `d5-milestone-summary.py`: Update the `range_low` and `range_high` in the POOLS configuration
   - `aae-hybrid-signal.py`: Update `POSITION['range_low']` and `POSITION['range_high']`
   - `lp-aae-signal-monitor.py`: Update `DEFAULT_CONFIG['position']['range_low']` and `DEFAULT_CONFIG['position']['range_high']`
   - `d5-master-cron.py`: Update `POOL['range_low']` and `POOL['range_high']`
   - `lp-position-reader.py`: Update default fallback values if present

3. **JSON Configuration Files**
   - `.lfj-aae-config.json`: Update `position.range_low` and `position.range_high`

### Systematic Update Approach

Use `grep` to find all occurrences of the old range values:
```bash
grep -r "9\.25" /root/vaults/gentech/03-Strategies/scripts/
grep -r "9\.54" /root/vaults/gentech/03-Strategies/scripts/
```

Then update each file using appropriate methods:
- For JSON files: Use `execute_code` with Python's `json` module to avoid escaping issues
- For Python scripts: Use `patch` with exact string matching, or `execute_code` with string replacement
- For documentation files: Update manually if needed

### Tooling Tips

**When `patch` fails with "Escape-drift detected"**: This usually happens with JSON files due to quote escaping. Switch to `execute_code`:

```python
import json

with open('file.json', 'r') as f:
    data = json.load(f)

# Update values
data['position']['range']['low'] = 9.40
data['position']['range']['high'] = 9.63

with open('file.json', 'w') as f:
    json.dump(data, f, indent=2)
```

**Verify updates**: After making changes, run `lp-position-reader.py --json` and check that `range_check.range_low` and `range_check.range_high` match the new values. Then re-run the cron job:
```bash
python3 lp-position-reader.py --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Range: {d[\"range_check\"][\"range_low\"]}-{d[\"range_check\"][\"range_high\"]} | In range: {d[\"range_check\"][\"in_range\"]}')"
hermes cron run <job-id>
```

### Propagation to Runtime Locations

Remember that Hermes profiles use runtime copies of configuration files. After updating the vault version, propagate to all runtime locations:

```bash
SRC=/root/vaults/gentech/03-Strategies/scripts/.lfj-aae-config.json
for dest in \
  /root/.hermes/scripts/ \
  /root/.hermes/profiles/dmob/home/.hermes/scripts/ \
  /root/.hermes/profiles/yoyo/home/.hermes/scripts/ \
  /root/.hermes/profiles/desmond/home/.hermes/scripts/ \
  /root/.hermes/profiles/gentech/home/.hermes/scripts/ \
  /root/.hermes/profiles/gentech/.hermes/scripts/ \
  /root/.hermes/profiles/gentech/scripts/; do
  cp "$SRC" "$dest" 2>/dev/null
done
echo "Synced to all profiles"
```

### Testing the Update

After updating all configuration files, manually trigger the Defi Milestone cron job to verify correct behavior:
```bash
hermes cron run <job-id>
```

Check the output to ensure the new range is reflected correctly.

## Pro Tips

- Use `hermes cron run <id>` to test job changes immediately after editing scripts
- The D5 job runs **silently** unless there's an alert (out-of-range, low efficiency, milestone hit)
- Manual run doesn't guarantee immediate output — check state files for updated data
- For debugging, add `--debug` flag if supported by the underlying skill, or run the script directly from terminal

## Patterns & Best Practices

### Capital Injection Detection
When tracking progress toward funding goals, detect capital additions by persisting the last seen position value across runs:

```python
# State schema extension (add field)
state = {
    "last_position_usd": float,
    # ... existing fields
}

# Detection logic (place after state load, before report generation)
current_position = config["position"]["total_usd"]
last_position = state.get("last_position_usd", 0.0)
if current_position > last_position:
    injection_usd = current_position - last_position
    human_report = f"💸 Capital added: ${injection_usd:.2f} — progress recalculated.\\n\\n" + human_report
    json_output["capital_injection_usd"] = injection_usd
# Always update state after check
state["last_position_usd"] = current_position
```

This ensures that when you add funds (e.g., $50 DCA), the next run reflects the increased total and shows updated progress toward the next milestone tier.
### Scout Progress Bar Formatting

When configuring the Scout Progress section for DeFi milestone reports, ensure the prompt clearly distinguishes between the text percentage and the bar representation:

- **Text**: Show the exact calculated percentage (rounded to nearest integer). This provides accurate progress tracking.
- **Bar**: Use the rounded-to-nearest-10% value to determine the number of filled blocks. This gives a visual approximation.

**Example configuration:**
```
Append this section after the script output:

```
🎯 Scout Progress
[████████░░] X% — $Y / $5.00 daily fees
```

In the actual output, replace X with the exact calculated percentage (rounded to nearest integer) and replace Y with the actual cumulative_fees_est value. The bar should still use the rounded-to-nearest-10% value for the number of blocks.
```

**Why this matters:**  
Ambiguous rounding instructions can cause the output to show 50% (rounded to nearest 10%) when the actual progress is 46%, which is misleading. Clear separation between exact text and approximate bar ensures both accuracy and visual clarity.

### Script Consolidation Strategy
When merging multiple cron scripts into one unified job:
- Keep a single source of truth for state (one state file)
- Add a `--json` flag for structured output while preserving human-readable Telegram format
- Retire old cron jobs after deployment, but keep one frequent (e.g., 10-minute) monitor as a fallback during transition
- Archive retired scripts with a `-retired-YYYY-MM-DD` suffix; don't delete
- Test the unified script thoroughly (multiple runs, state persistence) before switching cron schedule

### State File Location Pattern
Hermes scripts typically define:
```python
STATE_DIR = os.path.expanduser("~/.hermes/scripts")
```
The resolved path depends on `$HOME`. Verify with:
```bash
python3 -c "import os; print(os.path.expanduser('~/.hermes/scripts'))"
```
LP tracking state file: `~/.hermes/scripts/.lfj-aae-state.json`

### Idempotency & Verification Checklist
After stateful changes, run the script multiple times to confirm:
- [ ] Exit code 0, no exceptions
- [ ] State file updates correctly (`last_position_usd` persists)
- [ ] JSON output well-formed (`jq .` or `python -m json.tool`)
- [ ] Capital injection banner appears only when `total_usd` increases
- [ ] No false positives on subsequent identical runs
- [ ] Human report renders cleanly in Telegram (no broken formatting)
