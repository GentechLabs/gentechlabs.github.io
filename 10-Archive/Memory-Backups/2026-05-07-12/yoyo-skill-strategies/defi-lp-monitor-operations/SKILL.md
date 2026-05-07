---
name: defi-lp-monitor-operations
category: strategies
description: YoYo's operational guide for DeFi Milestone + LP Monitor — debugging silent executions, path resolution quirks, debounce state interpretation, cron prompt management, and milestone tier tracking.
triggers:
  - running d5-lp-consolidated.py produces no output
  - verifying DeFi LP cron job health
  - interpreting debounce/silence behavior in LP monitoring
  - troubleshooting Hermes config path mismatches
  - updating the Defi Milestone cron job prompt
  - calculating Scout progress bar for LP reports
reasoning: >
  Class-level skill for DeFi monitoring operations. Covers systematic diagnosis of silent/no-output script
  executions, Hermes multi-location config resolution, reading debounce state from .lfj-defi-state.json,
  and validating cron path configuration. Pattern: script runs exit 0 but produces no report → check
  consecutive_quiet_runs debounce, not API failure.
---

# DeFi LP Monitor Operations

## Overview

The D5 Milestone + LP Monitor (`d5-lp-consolidated.py`) is YoYo's primary tool for tracking LFJ AVAX/USDC LP position health, fee efficiency, and rebalancing signals. This skill covers operational debugging when the script appears to fail silently.

## Two-Tier Config Resolution

The script resolves config paths via `HERMES_HOME`:

```python
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~"))
HOME_SCRIPTS_DIR = os.path.join(HERMES_HOME, "home", ".hermes", "scripts")
```

**Consequence:** Configs live in **two possible locations**:
- `/root/.hermes/profiles/yoyo/home/.hermes/scripts/` ← used when `HERMES_HOME=/root/.hermes/profiles/yoyo`
- `/root/.hermes/scripts/` ← used when `HERMES_HOME` unset/`/root`

Both locations may contain `.lfj-aae-config.json` and `.lfj-defi-state.json`. The script reads from the path derived from `HERMES_HOME`. If you see stale/no data, verify which location the script is actually using.

## Interpreting Silent Output (Exit Code 0, No Print)

**Exit code rules:**
- `0` = OK or intentionally silent (no material change + debounce satisfied)
- `1` = WARNING (efficiency 30–50% range, or other medium alerts)
- `2` = CRITICAL (out of range or efficiency <30%)

**Silence is NOT an error if:**
| Condition | Exit Code | Output |
|-----------|-----------|--------|
| Quiet hours (23:00–06:00 ET) | 0 | None |
| Debounce active (consecutive_quiet_runs ≥ 2 within same hour) | 0 | None |
| High-efficiency stable zone (≥70% efficiency, in range, no alerts) | 0 | None (skips baseline reports) |
| First-run high-efficiency catch-up | 0 | None (sets consecutive_quiet_runs=2 immediately) |

To diagnose, read the **state file** (path resolution-aware):

```bash
# Read the state file the script actually uses
cat /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-defi-state.json
# OR if HERMES_HOME is unset
cat /root/.hermes/scripts/.lfj-defi-state.json
```

Key fields:
- `consecutive_quiet_runs` — if ≥2 and `last_report_hour == current_hour`, script will stay silent
- `last_zone` — compare to current efficiency zone to detect material changes
- `last_in_range` — flip triggers report
- `last_report_time` — presence indicates prior reports sent

## DexScreener API & 403 Transients

The script uses `urllib.request` with custom User-Agent. Occasional HTTP 403 errors may occur. If persistent:
- Check User-Agent string (`Gentech-DeFi/1.0`)
- Verify no rate limiting hit
- As a sanity check, use `curl` to validate API availability:
  ```bash
  curl -s -H "User-Agent: Gentech-DeFi/1.0" \
    "https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea" | head -c 500
  ```

## Cron Job Prompt Management

**Pitfall:** `cronjob list` only shows `prompt_preview` (truncated). To see the full prompt, read the profile's `jobs.json` directly:

```bash
# Yoyo's cron jobs (the actual source of truth for this profile)
cat /root/.hermes/profiles/yoyo/cron/jobs.json | python3 -c "
import sys, json
jobs = json.load(sys.stdin)['jobs']
for j in jobs:
    if j['id'] == '3258c64b':
        print(json.dumps(j, indent=2))
"
```

**Key paths:**
- `/root/.hermes/profiles/yoyo/cron/jobs.json` — Yoyo's job definitions (prompt, schedule, script, deliver)
- `/root/.hermes/cron/jobs.json` — legacy global registry (may be stale/empty)
- `/root/.hermes/cron/jobs.db` — SQLite DB (not used by Hermes cron daemon)

**Updating prompts:** Use `cronjob update` with the job_id. Common edits:
- Rename references (e.g., "D5" → "DeFi")
- Remove sections the LLM agent injects (e.g., "reward bin")
- Add new output sections (e.g., Scout progress bar)

## Cron Path Mismatch

**Common pitfall:** Cron configuration points to `/root/.hermes/profiles/yoyo/scripts/d5-lp-consolidated.py` but the script lives at `/root/.hermes/scripts/d5-lp-consolidated.py`.

Verify the script path in the cron job definition (see above). Fix by updating the cron entry to the absolute correct path.

## Milestone Tiers & Scout Progress

The config at `.lfj-aae-config.json` defines milestone tiers:

| Tier | Label | Daily Fees Target | Description |
|------|-------|-------------------|-------------|
| 1 | Scout | $5.00 | Entry strategies (CURVE) |
| 2 | Raider | $20.00 | SPOT + BIDIRECTIONAL shapes |
| 3 | Warlord | $50.00 | Multi-pool positions |
| 4 | Sovereign | $100.00 | Custom strategy creation + mentorship |

**Scout progress bar** (appended to cron output):
- Read `cumulative_fees_est` from `.lfj-position-tracker.json`
- Calculate: `cumulative_fees_est / 5.00 * 100` (cap at 100%)
- Render as 10-block bar: `[████████░░] 46% — $2.29 / $5.00 daily fees`

## Quick Diagnostic Checklist

```
1. Is current hour within quiet hours? (23–06 ET)
   → Yes: silent expected. No action.

2. Read .lfj-defi-state.json:
   → consecutive_quiet_runs ≥ 2 AND last_report_hour == current_hour?
     → Yes: debounce active. Script correctly silent.

3. Fetch current price/efficiency manually:
   → Compare to last_price/last_zone in state
   → Has zone flipped or range status changed?
     → Yes: should_send would be True. If script still silent, config path mismatch likely.

4. Verify which config file the script reads:
   → Print HOME_SCRIPTS_DIR via debug injection
   → Confirm .lfj-aae-config.json exists at that path

5. Exit code:
   → 0 = healthy (silent per rules)
   → 1 = efficiency dropped to 30–50% zone (MEDIUM alert)
   → 2 = out of range or efficiency <30% (CRITICAL alert)
```

## Manual State Reset (When Needed)

If debounce logic stuck in quiet state and you need to force a baseline report:

```bash
# Reset consecutive_quiet_runs to 0 and clear last_report_hour
jq '.consecutive_quiet_runs = 0 | .last_report_hour = null' \
  /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-defi-state.json > /tmp/tmp.json \
  && mv /tmp/tmp.json /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-defi-state.json
```

**Do not force-reset** unless you understand the silencing rules — they prevent alert fatigue.

## Related Skills

- `strategies/d5-lp-monitor` — actual monitoring strategy and alert thresholds
- `gentech-cron-ops` — cron job health and path verification
