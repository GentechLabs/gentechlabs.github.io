# D5 LP Monitor — Session Diagnostics (2026-05-03)

## Problem
Cron job execution produced exit code 0 with **zero stdout**, triggering a "Script not found" alert, but the script actually exists and runs correctly. Root cause was a path-resolution mismatch plus debounce silencing.

## Error Observed
```
Script not found: /root/.hermes/profiles/yoyo/scripts/d5-lp-consolidated.py
```
The path `/root/.hermes/profiles/yoyo/scripts/` **does not exist**. The real script is at `/root/.hermes/scripts/d5-lp-consolidated.py`.

## Root Causes

### 1. Dual Hermes Config Locations
Hermes home directory layout creates two potential config roots:

| HERMES_HOME setting | Script location | Config location read by script |
|---------------------|----------------|-------------------------------|
| `/root/.hermes/profiles/yoyo` (default) | `/root/.hermes/scripts/` | `/root/.hermes/profiles/yoyo/home/.hermes/scripts/` |
| unset or `/root` | `/root/.hermes/scripts/` | `/root/.hermes/scripts/` |

**Finding:** Both `/root/.hermes/profiles/yoyo/home/.hermes/scripts/` and `/root/.hermes/scripts/` contain `.lfj-*` JSON configs. The script's `hermes_path()` resolves based on `HERMES_HOME`, so whichever location has files is the one being used. In this session, the **profile location had the freshest data**.

### 2. Debounce Silencing (Expected Behavior)
State file (`consecutive_quiet_runs=2`, `last_report_hour=19`, efficiency 63.4% in same zone, no material change) correctly suppressed output per the 2-clean-run debounce rule. This is **healthy behavior**, not a failure.

### 3. Cron Path Reference Stale
Alert mentioned non-existent path `/root/.hermes/profiles/yoyo/scripts/`. Check cron jobs:
```bash
crontab -l
cat /root/.hermes/cron/jobs.json
```
Fix by updating the command's working directory or using the correct absolute path.

## Commands Used During Diagnosis

### Check which config path the script uses (inject debug)
```bash
# Temporary debug patch: replace hermes_path() with print-enabled version
python3 -c "
with open('/root/.hermes/scripts/d5-lp-consolidated.py') as f:
    c = f.read()
c = c.replace(
    'def hermes_path(filename: str) -> str:\n    return os.path.join(HOME_SCRIPTS_DIR, filename)',
    'def hermes_path(filename: str) -> str:\n    path = os.path.join(HOME_SCRIPTS_DIR, filename)\n    import sys; print(f\"[DEBUG] resolved={path}\", file=sys.stderr)\n    return path'
)
with open('/tmp/d5-debug.py','w') as f: f.write(c)
"
python3 /tmp/d5-debug.py 2>&1 | grep resolved
```

### Verify DexScreener API availability
```bash
curl -s -H "User-Agent: Gentech-DeFi/1.0" \
  "https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); p=d['pair']; print(f\"Price: {p['priceNative']}, Liq: {p['liquidity']['usd']}\")"
```

### Read current debounce state
```bash
cat /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-defi-state.json | python3 -m json.tool | grep -E 'consecutive_quiet_runs|last_report_hour|last_zone|last_price'
```

### Compare both config locations
```bash
diff -u <(jq '.position' /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-config.json) \
         <(jq '.position' /root/.hermes/scripts/.lfj-aae-config.json)
```

## Takeaways for Future Sessions
1. Whenever `d5-lp-consolidated.py` exits 0 with no output, **first check `consecutive_quiet_runs`** — debounce is the most common reason.
2. If state looks stale or mismatched, verify which config path is active via `HERMES_HOME` and your actual profile directory contents.
3. Do NOT treat silent output as a failure unless quiet hours are off, debounce is not active, and price/efficiency have materially changed.
4. When debugging cron runs, always print the **resolved script path** and **config file path** at the top of the script to eliminate path-mismatch ambiguity.
