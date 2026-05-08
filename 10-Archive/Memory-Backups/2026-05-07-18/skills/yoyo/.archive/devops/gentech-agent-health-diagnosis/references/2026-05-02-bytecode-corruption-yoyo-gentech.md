# Incident: 2026-05-02 — Marshal Bytecode Cache Corruption Affecting YoYo & Gentech

**Date:** May 2, 2026  
**Agents affected:** YoYo (PID 899631), Gentech (PID 899618)  
**Agents unaffected:** DMOB (PID 899554), Desmond (PID 899540)  
**Severity:** MEDIUM — Agents remain running but session summarization feature broken

---

## Error Pattern

**System journal entries (repeat every ~5 seconds per agent):**

```
May 02 00:30:44 srv1582785 python[899631]: WARNING root: Session summarization failed after 3 attempts: marshal data too short
May 02 00:30:44 srv1582785 python[899631]: EOFError: marshal data too short
May 02 00:30:44 srv1582785 python[899631]: WARNING root: Session summarization failed after 3 attempts: marshal data too short
...
File "<frozen importlib._bootstrap_external>", line 729, in _compile_bytecode
  EOFError: marshal data too short
```

**Traceback origin:** `session_search_tool.py` → `_summarize_session()` → LLM call → module import triggers bytecode compilation

**Timing correlation:** Gentech errors start at 00:31:09, YoYo at 00:30:44 — within 25 seconds, suggesting shared cache mutation.

---

## Root Cause

Python bytecode cache (`.pyc` files and `__pycache__` directories) in `/usr/local/lib/hermes-agent/` became corrupted, likely due to:

1. **Concurrent writes** during package update/installation while gateways were running
2. **Disk I/O error or interrupted write** (check `dmesg` for I/O errors around May 1–2)
3. **NFS/synchronization issue** if Hermes installed on network-mounted filesystem

Marshal format corruption means Python's import machinery reads an incomplete/truncated `.pyc` file and fails with `data too short`.

---

## Affected Components

- `/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages/` — compiled packages in virtualenv
- `/usr/local/lib/hermes-agent/` — agent installation `.pyc` files
- `/root/.hermes/profiles/*/__pycache__/` — profile-specific compiled code

**Not affected:** `auth.json`, vault data, session transcripts (these are data, not bytecode).

---

## Resolution Applied

Cleared all Python bytecode caches across the installation:

```bash
find /usr/local/lib/hermes-agent -type d -name "__pycache__" -exec rm -rf {} +
find /usr/local/lib/hermes-agent -name "*.pyc" -delete
find /root/.hermes/profiles -type d -name "__pycache__" -exec rm -rf {} +
find /root/.hermes/profiles -name "*.pyc" -delete
rm -rf /root/.hermes/__pycache__
```

Cleared gateway locks and restarted all four gateways sequentially with 5s stagger.

**Post-restart verification:**
```bash
# Check journal for recurrence (5-minute window)
journalctl --since "5 min ago" | grep -E 'marshal data too short'  # → empty

# Confirm agents healthy
ps aux | grep 'hermes gateway run' | grep -v grep  # → 4 processes
```

---

## Detection Script (for future watchdog use)

Save as `/root/.hermes/scripts/check_marshal_corruption.sh`:

```bash
#!/bin/bash
# Check all agents for marshal bytecode corruption in last 10 minutes

CORRUPTED=0
for agent in yoyo dmob desmond gentech; do
  pid_file="/root/.hermes/profiles/$agent/gateway.pid"
  if [ -f "$pid_file" ]; then
    pid=$(python3 -c "import json; print(json.load(open('$pid_file'))['pid'])")
    count=$(journalctl --since "10 min ago" | grep "python\\[$pid\\]" | grep -c 'marshal data too short' || echo 0)
    if [ "$count" -gt 0 ]; then
      echo "⚠️  $agent (PID $pid): $count marshal errors detected"
      CORRUPTED=1
    fi
  fi
done

if [ "$CORRUPTED" -eq 1 ]; then
  echo "🚨 BYTECODE CORRUPTION DETECTED — run: find /usr/local/lib/hermes-agent -type d -name __pycache__ -exec rm -rf {} +"
  exit 1
else
  echo "✓ No marshal corruption detected"
  exit 0
fi
```

**Cron usage:** `*/10 * * * * /root/.hermes/scripts/check_marshal_corruption.sh && echo "OK" || /root/.hermes/scripts/clear_bytecode_cache.sh`

---

## Correlation with Other Failure Modes

Bytecode corruption can **trigger secondary failures:**

1. **Cron executor stalls** — Import error during job dispatch kills executor thread silently. Gateway still shows "Cron ticker started" but never executes jobs.
   - **Check:** `grep -E 'checking|executing' /root/.hermes/profiles/*/logs/gateway.log`
   - **Fix:** Clear cache AND restart gateways (this recovery)

2. **Session search/summarization broken** — `session_search_tool.py` fails to import helper modules; all session queries return "summarization failed" warnings.
   - **Check:** `grep 'Session summarization failed' /root/.hermes/logs/agent.log`
   - **Fix:** Clear cache; no data loss

3. **SessionDB initialization warnings** — May cascade: `WARNING cli: Failed to initialize SessionDB — session will NOT be indexed for search: database or disk is full` (seen May 1 10:17). Disk pressure can exacerbate cache corruption.
   - **Check:** `df -h /root` and `df -i /root`
   - **Fix:** Clear cache; free disk space if needed

---

## Reproduction (test environment only)

```bash
# Artificially corrupt a .pyc file to reproduce error pattern
find /usr/local/lib/hermes-agent -name "*.pyc" | head -1 | while read pyc; do
  echo "Corrupting $pyc"
  truncate -s 0 "$pyc"  # zero out file
done

# Trigger session search (will fail immediately)
hermes sessions search "test"

# Check journal
journalctl --since "1 min ago" | grep marshal
```

**Expected:** `EOFError: marshal data too short` within seconds.

**Recovery:** Run cache clear procedure above.

---

## Related Incidents

- **2026-05-01:** Model deprecation errors for `minimax/minimax-m2.5:free` (OpenRouter) — unrelated, provider catalog issue
- **2026-05-01 10:17:** SessionDB disk full warning — possible correlation (disk pressure → incomplete writes)
- **2026-05-02:** Present incident — bytecode corruption affecting 50% of agents

---

## Watchdog Integration

**Health-check command for Watchdog cron:**

```bash
#!/bin/bash
# /root/.hermes/scripts/watchdog_bytecode_check.sh

AGENTS=("yoyo" "dmob" "desmond" "gentech")
ALERT=0

for agent in "${AGENTS[@]}"; do
  pid_file="/root/.hermes/profiles/$agent/gateway.pid"
  if [ -f "$pid_file" ]; then
    pid=$(python3 -c "import json; print(json.load(open('$pid_file'))['pid'])")
    if ! ps -p "$pid" > /dev/null; then
      echo "❌ $agent: process not running"
      ALERT=1
    else
      marshal_count=$(journalctl --since "15 min ago" | grep "python\\[$pid\\]" | grep -c 'marshal data too short' || echo 0)
      if [ "$marshal_count" -gt 3 ]; then
        echo "🚨 $agent: marshal corruption ($marshal_count hits)"
        ALERT=1
      fi
    fi
  fi
done

exit $ALERT
```

**Cron entry:** Run every 15 minutes; alert if any agent shows >3 marshal errors in window.

---

## Prevention

1. **Never upgrade Hermes while gateways are running.** Stop all gateways before `pip install --upgrade hermes-agent`.
2. **Monitor disk I/O health.** I/O errors or full disks can truncate `.pyc` writes. Check `dmesg | grep -i error` weekly.
3. **Consider read-only installation.** If Hermes installed in `/usr/local/lib/`, make `.pyc` cache volatile by setting `PYTHONDONTWRITEBYTECODE=1` in gateway startup (not recommended for production due to performance).
4. **Regular bytecode cache validation.** Monthly: `python3 -m compileall /usr/local/lib/hermes-agent` to ensure all source compiles cleanly.

---

**Last updated:** May 2, 2026 — Initial incident documented  
**Skill patch:** `devops/gentech-agent-health-diagnosis` gained Phase 3.5 (Bytecode Cache Corruption Detection)
