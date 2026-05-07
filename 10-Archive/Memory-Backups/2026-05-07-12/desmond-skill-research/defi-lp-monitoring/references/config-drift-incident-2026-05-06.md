# Config Drift Incident — May 6, 2026

## Symptom
Cron job `e00b46103b08` ("Defi Milestone — LP Monitor") reported:
- Range: $9.40–9.63, Shape: CURVE, Status: IN RANGE

Actual position (from `.env` vault config):
- Range: $9.44–9.74, Shape: BID-ASK, Status: IN RANGE at 93.5% efficiency

## Root Cause
Three compounding issues:

### 1. Config Drift Across 7 Copies
`.lfj-aae-config.json` existed in 7 locations with 3 different value sets:
- Copy #1 (`/root/.hermes/scripts/`): 9.44–9.74, bid-ask, $123.74 ← correct
- Copies #2–4 (profile `home/` dirs): 9.25–9.54, curve, $134.94 ← stale
- Copy #5 (gentech `home/`): 9.44–9.74, bidirectional, $134.94 ← partially updated
- Copies #6–7 (gentech alt paths): 9.25–9.54, curve, $134.94 ← stale

### 2. `HERMES_HOME` Path Resolution
The `d5-lp-consolidated.py` script resolves config via:
```python
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~"))
HOME_SCRIPTS_DIR = os.path.join(HERMES_HOME, "home", ".hermes", "scripts")
```
When run via cron, `HERMES_HOME` = `/root/.hermes/profiles/desmond`, so the script reads from copy #2 (stale), not copy #1 (correct).

### 3. Prompt-Only Cron Job Fabricates Data
The original cron job had a prompt telling the agent to "fetch price and compare to range" but used no script. The agent fabricated data based on stale knowledge instead of reading live data.

## Fix Applied
1. ✅ Synced all 7 config copies to latest values via batch Python script
2. ✅ Updated cron job to use `script: d5-lp-consolidated.py` (runs script first, agent formats output)
3. ✅ Simplified prompt to "format the script output above" instead of "fetch and report"
4. ✅ Verified script returns correct data: Price $9.58, In Range, 93.5% efficiency

## Detection Pattern
When cron output shows range/shape/status that doesn't match the vault `.env` config:
1. Run `find /root/.hermes -name ".lfj-aae-config.json" -type f` to find all copies
2. Check which copy the script reads (HERMES_HOME resolution)
3. Batch-sync all copies
4. Switch cron job to use `script` parameter

## Prevention
- After ANY rebalance, batch-sync all config copies (see skill's Group 1 table)
- Use `script` parameter in cron jobs instead of prompt-only approaches
- Add config path logging to scripts for debugging
