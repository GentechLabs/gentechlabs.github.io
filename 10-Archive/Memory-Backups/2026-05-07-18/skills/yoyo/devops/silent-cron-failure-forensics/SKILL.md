---
name: silent-cron-failure-forensics
description: Diagnostic methodology for cron jobs that appear to run (mtime updates, exit 0) but produce zero output. Diagnoses environment/state discrepancies between cron and interactive shells.
triggers:
  - cron_debug
  - silent_failure
  - missed_cron
  - log_stale
---

# Silent Cron Failure Forensics

When a cron job executes (CRON syslog entry present, output file mtime updates) but produces no content in the redirected log, use this diagnostic sequence.

## SYMPTOM

```bash
# Cron fired (syslog shows execution)
grep "defi-milestone-tracker" /var/log/syslog
  → 2026-05-04T00:00:01 CRON[443836]: CMD (HERMES_HOME=/... >> cron.log 2>&1)

# Log file mtime updated
stat cron.log
  → mtime: 2026-05-04 00:00:02

# But file size unchanged, content stale
tail cron.log
  → Still shows previous run (May 3), no May 4 entry

# Manual run works fine
python3 script.py
  → ✅ produces expected output
```

## DIAGNOSTIC SEQUENCE

### **Step 1: Verify File Append Works**
```bash
# Test write access
echo "TEST $(date)" >> /path/to/cron.log
# Check if line appears immediately
grep "TEST" /path/to/cron.log
```
If test write fails → permission issue, disk full, or file handle limit.

### **Step 2: Cron Environment Isolation**
Cron provides minimal environment (no `~/.bashrc`, limited `PATH`). Reproduce exactly:
```bash
# Recreate cron's environment
env -i \
  PATH=/usr/bin:/bin \
  HOME=/root \
  SHELL=/bin/bash \
  LOGNAME=root \
  USER=root \
  HERMES_HOME=/root/.hermes/profiles/yoyo \
  /usr/bin/env python3 /root/.hermes/profiles/yoyo/scripts/defi-milestone-tracker.py \
  2>&1 | tee /tmp/cron_test.out
```
If this fails but interactive run succeeds → missing env var or PATH dependency.

### **Step 3: Check Cron Redirect Integrity**
Cron line: `>> cron.log 2>&1` means:
- Stdout **append** to file
- Stderr also redirected to same file

If script crashes **before any stdout flush**, file may only contain stderr. But if script exits 0 silently, nothing gets written.

Test redirect chain works:
```bash
# Simulate cron's exact redirection
env -i ... python3 script.py >> /tmp/cron_redirect_test.log 2>&1
echo "Exit code: $?"
wc -l /tmp/cron_redirect_test.log
```
Zero lines + exit 0 → silent early exit.

### **Step 4: Script State/Path Issues**
Common silent-drop causes:
- `sys.path` missing script directory → ImportError before log init
- Missing `HERMES_SCRIPTS_DIR` → tries to read non-existent config → exits
- Network call hangs → cron's implicit timeout (usually 1–5 min) kills process *before* write
- File lock contention → script exits on lock failure (no output)

Check script for:
```python
# Does it log early?
print("Starting…", file=sys.stderr)  # Should appear immediately

# Does it require HERMES_HOME specifically?
config_path = os.path.expanduser("~/.hermes/scripts")  # Fails if HOME not set
```

### **Step 5: Inotify / fsync Verification**
Rare: file buffering delay. Force sync:
```bash
python3 -c "
import sys, os
sys.path.insert(0, '/usr/local/lib/hermes-agent')
exec(open('script.py').read())
" 2>&1 | tee -a cron.log
```
If this writes but cron doesn't → cron's stdout buffering or parent shell issue.

## QUICK REPRODUCTION

From 2026-05-04 YoYo investigation:
- Crontab: `*/10 * * * * HERMES_HOME=/root/.hermes/profiles/yoyo python3 defi-milestone-tracker.py >> cron.log 2>&1`
- Fired at 00:00:01 UTC, exit 0, log mtime updated, **0 bytes output**
- Manual run (any env) succeeded
- Root cause: **Undetermined** — transient environment state (possibly network glitch during API fetch or Hermes client init race)

## FIXES TO TRY (in order)

1. **Add强制日志头** — modify script to write before any network calls:
   ```python
   print(f"🔄 Cron start: {datetime.now()}", flush=True)
   ```
2. **Timeout wrapper** — prevents silent hang:
   ```bash
   */10 * * * * timeout 30 env ... python3 script.py >> cron.log 2>&1
   ```
3. **Separate stdout/stderr** — helps diagnose which stream is failing:
   ```bash
   */10 * * * * env ... python3 script.py >> cron.log 2>> cron.err
   ```
4. **Heartbeat file** — proves script started:
   ```bash
   */10 * * * * touch /tmp/cron_heartbeat && env ... python3 script.py >> cron.log 2>&1
   ```

## ESCALATION TRIGGERS

- Silent failure repeats on next cron tick (next 10min window) → likely environment bug in script
- Manual run works, cron fails consistently → env diff; dump cron env with `env > /tmp/cron_env_dump`
- Script takes > cron interval → overlapping runs; add lockfile

---

*Skill created from 2026-05-04 YoYo defi-milestone-tracker silent drop. See references/cron-silent-drop-2026-05-04.md for full forensic timeline.*