# D5 LP Monitor — Debounce & Path Diagnostics (May 3, 2026)

## Symptom

`d5-lp-consolidated.py` exits with code 0 and produces **no Telegram output**, despite the position having material change.

```
$ python3 /root/.hermes/scripts/d5-lp-consolidated.py
# (nothing prints)
$ echo $?
0
```

Initial misdiagnosis: "Script not found" error from cron referencing wrong path.

## Root Causes

### A — Debounce Silencing (Expected, Normal)

The script implements a **2-clean-run debounce** in NORMAL mode:

| Condition | Consecutive Quiet Runs | Current Hour | Outcome |
|-----------|------------------------|--------------|---------|
| `consecutive_quiet_runs < 2` | First or second clean run this hour | Any | **Output sent** (hourly baseline) |
| `consecutive_quiet_runs >= 2` | Debounce satisfied | Same hour as `last_report_hour` | **Silenced** — debounce active |
| `consecutive_quiet_runs >= 2` | Debounce satisfied | Hour changed (new `last_report_hour`) | **Output sent** — counter resets |

State file: `$HERMES_HOME/home/.hermes/scripts/.lfj-defi-state.json`

Relevant fields:
```json
{
  "consecutive_quiet_runs": 2,
  "last_report_hour": 19,
  "last_price": 9.08596,
  "last_efficiency": 66.3,
  "last_zone": "zone_50_70",
  "last_in_range": true
}
```

**Decision rule** (function `should_send_report`):
- If `efficiency >= 70%` and `in_range` and `no alerts` → HIGH-EFFICIENCY STABLE override → silent (sets consecutive_quiet_runs=2 immediately even on first run)
- If material change detected (price moved ≥1% or ≥$0.20, **or** zone flipped, **or** in_range flipped, **or** new alert condition) → output sent, consecutive counter resets to 0
- Otherwise → quiet-run counting; if already at 2+, stay silent until hour rolls over

**In the session case**:
- Efficiency 63.4% in zone_50_70 → no zone flip (still zone_50_70)
- Price changed 0.10% → below threshold
- In range → unchanged
- No alerts → unchanged
- `consecutive_quiet_runs=2` and `last_report_hour=19` = current hour → debounce satisfied → silent

**Conclusion:** Exit code 0 with no output is **correct behavior**. Not an error.

### B — Path Resolution — Dual Config Locations

**Hermes HOME quirk:** The script builds config paths from `HERMES_HOME`:

```python
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~"))
HOME_SCRIPTS_DIR = os.path.join(HERMES_HOME, "home", ".hermes", "scripts")
```

When `HERMES_HOME=/root/.hermes/profiles/yoyo` (typical for Hermes agents), the script reads:
```
/root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-config.json
/root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-defi-state.json
```

**But** the files also exist at `/root/.hermes/scripts/` (a parallel copy). If your cron references the wrong base path, you can get file-not-found errors.

**Cron error observed** in this session:
```
Script not found: /root/.hermes/profiles/yoyo/scripts/d5-lp-consolidated.py
```
The path `/root/.hermes/profiles/yoyo/scripts/` does NOT exist — correct script location is `/root/.hermes/scripts/d5-lp-consolidated.py`.

**Fix**: Verify cron entry uses correct absolute path:
```bash
crontab -l | grep d5   # inspect current crontab
cat /root/.hermes/cron/jobs.json  # Gentech-wide registry
```

### C — DexScreener Transient 403

First API call in this session returned HTTP 403. A raw `curl` immediately after succeeded with HTTP 200. This suggests transient rate limiting or header-based filtering. The script uses `User-Agent: Gentech-DeFi/1.0`; if the provider blocks that UA occasionally, a retry-with-backoff wrapper would help. Not yet implemented; observed as transient.

## Diagnostic Checklist (Quick)

When `d5-lp-consolidated.py` produces no output:

```
✓ 1. Check quiet hours
   time now (ET): $(date +%H)
   Is hour >=23 or <6? → Yes: silent expected

✓ 2. Check debounce state
   cat $(hermes_path .lfj-defi-state.json) | jq '{consecutive_quiet_runs, last_report_hour, last_zone, last_price, last_efficiency}'
   Are consecutive_quiet_runs >= 2 AND last_report_hour == current_hour? → Yes: silent (debounce active)

✓ 3. Check for material change
   - Fetch current price from DexScreener
   - Compute current efficiency & zone
   - Compare: zone changed? in_range flipped? price moved ≥1% or ≥$0.20?
     → Yes: something's wrong (likely config path mismatch or state not being saved)

✓ 4. Verify config path being used
   Inject debug: replace hermes_path() with print-enabled version (see commands below)
   Confirm the directory it prints contains config files

✓ 5. Check exit code to interpret severity
   0 = healthy (even if silent)
   1 = MEDIUM alert (efficiency 30–50% zone)
   2 = CRITICAL alert (out of range or efficiency <30%)
```

## Commands

### Read config path resolution debug
```bash
python3 -c "
import sys
with open('/root/.hermes/scripts/d5-lp-consolidated.py') as f: c=f.read()
patch = '''def hermes_path(filename):
    import os, sys
    path = os.path.join(HOME_SCRIPTS_DIR, filename)
    print(f'[DBG] HOME_SCRIPTS_DIR={HOME_SCRIPTS_DIR}', file=sys.stderr)
    print(f'[DBG] RESOLVED={path}', file=sys.stderr)
    return path
'''
c = c.replace('def hermes_path(filename: str) -> str:\n    return os.path.join(HOME_SCRIPTS_DIR, filename)', patch)
with open('/tmp/d5-debug.py','w') as f: f.write(c)
"
python3 /tmp/d5-debug.py 2>&1 | grep DBG
```

### Read debounce state (wherever config lives)
```bash
# Try both common locations
for base in \
  '/root/.hermes/profiles/yoyo/home/.hermes/scripts' \
  '/root/.hermes/scripts'; do
  echo "=== $base ==="
  [ -f "$base/.lfj-defi-state.json" ] && jq '.consecutive_quiet_runs, .last_report_hour, .last_zone, .last_price, .last_efficiency' "$base/.lfj-defi-state.json" 2>/dev/null
done
```

### Fetch live price & recalc efficiency manually
```bash
POOL="0x864d4e5ee7318e97483db7eb0912e09f161516ea"
curl -s -H "User-Agent: Gentech-DeFi/1.0" \
  "https://api.dexscreener.com/latest/dex/pairs/avalanche/$POOL" |
python3 -c "
import sys, json
p = json.load(sys.stdin)['pair']
print(f\"Price: {p['priceNative']}\")
print(f\"Liq: \${p['liquidity']['usd']}\")
print(f\"Vol24h: \${p['volume']['h24']}\")
"
# Compute efficiency using your cfg (range_low/range_high/shape)
```

### Compare profile vs root config copies
```bash
diff -u \
  <(jq '.position' /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-config.json) \
  <(jq '.position' /root/.hermes/scripts/.lfj-aae-config.json)
```

## State Reset (Use Sparingly)

If debounce logic appears stuck, you may reset the counter **only if you understand you're forcing an immediate report**:

```bash
# Reset debounce counter and last_report_hour
jq 'del(.consecutive_quiet_runs) | del(.last_report_hour)' \
  /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-defi-state.json > /tmp/tmp.json && \
mv /tmp/tmp.json /root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-defi-state.json
```

## Related Reference

- `strategies` umbrella: Two-Mode Notification Throttling pattern, debounce implementation details
- `strategies`: Config-driven architecture and Hermes path resolution pattern
- `gentech` skill system: Cron health monitoring and job path verification
