# YoYo Cron Silent Drop — Forensic Case File

**Date:** 2026-05-04  
**Agent:** YoYo (Strategies)  
**Script:** `/root/.hermes/profiles/yoyo/scripts/defi-milestone-tracker.py`  
**Symptom:** Cron executed but produced zero bytes in output log

---

## Timeline of Events

```
2026-05-03 23:50:01 UTC — CRON fires (normal)
  → Output appended to cron.log (last entry: May 3 20:00 report)
  
2026-05-04 00:00:01 UTC — CRON fires (May 4 run)
  → Syslog: CRON[443836] CMD line recorded
  → File mtime updates: 2026-05-04 00:00:02
  → File size remains 2332 bytes (unchanged)
  → No new report lines in file
  
2026-05-04 00:01:44 UTC — Watchdog detects stale cron.log
  → Manual run: python3 script → ✅ succeeds, outputs May 3 20:02 report
  → Cron env reproduction: ✅ succeeds, outputs May 3 20:03 report
  → Exit code in all manual tests: 0
```

**Gap:** Cron syslog says script ran, but nothing written. Manual execution always succeeds.

---

## Evidence Collected

### File Forensics
```
$ stat /root/.hermes/profiles/yoyo/cron.log
  Size: 2332    Blocks: 8    mtime: 2026-05-04 00:00:02.179326
  Inode: 1116212

$ wc -l cron.log
  64 lines

$ tail -5 cron.log
  (last line: `Mode: normal mode | baseline | Check: 20:00 EDT`)
```

**No May 4 date appears anywhere in file.** File mtime moved forward but content unchanged. This indicates either:
1. Cron redirected to a **different file** (path resolution issue)
2. Script crashed **before first print** and cron's shell-redirect buffer lost
3. File append permission denied at OS level but cron shell succeeded anyway (unlikely — would error)

### Syslog Correlation
```
$ grep defi-milestone-tracker /var/log/syslog | grep 2026-05-04
2026-05-04T00:00:01.958211+00:00 CRON[443836]: CMD (HERMES_HOME=/root/.hermes/profiles/yoyo /usr/bin/env python3 /root/.hermes/profiles/yoyo/scripts/defi-milestone-tracker.py >> /root/.hermes/profiles/yoyo/cron.log 2>&1)
```
**No stderr output recorded** from cron in syslog. If script crashed, cron would log nothing unless the shell itself failed.

### Manual Reproduction Matrix

| Environment | Command | Exit | Output? | Notes |
|-------------|---------|------|---------|-------|
| Interactive shell | `python3 script.py` | 0 | ✅ | Works |
| `HERMES_HOME` set | `HERMES_HOME=/... python3 script.py` | 0 | ✅ | Works |
| Cron env (captured) | `env -i PATH=... HERMES_HOME=... python3 script.py` | 0 | ✅ | Works |
| Pure empty env | `env -i python3 script.py` | 0 | ✅ | Works (script resilient) |

**Conclusion:** Script is robust to environment. Issue is external to script code.

---

## Working Hypotheses (ranked)

1. **Cron's stdout buffer not flushed** (most likely)
   - Cron uses `>>` which opens file in append mode
   - If Python exits before stdout buffer flush, output lost
   - But exit 0 should flush on normal exit… unless `os._exit()` used (it isn't)

2. **Transient disk I/O error at write()**
   - mtime updated (metadata write succeeded)
   - Data block write failed silently
   - Would show in `dmesg` — not checked yet

3. **File handle exhaustion / limit**
   - Cron opens file, fork+exec script, script runs, close
   - If system reached RLIMIT_NOFILE, open() could fail
   - Cron would error "cannot open" — not in syslog

4. **Path shadowing / different file**
   - Cron might resolve relative `./cron.log` differently
   - But absolute path `/root/.../cron.log` used — ruled out

5. **Script hung > cron timeout then killed**
   - Default cron timeout ≈ 1–5 min depending on distro
   - If killed with SIGKILL before flush, output lost
   - Syslog would show `killed process` — not present
   - File mtime updates immediately on open, not on close

**Leading candidate:** #1 (buffer flush issue) combined with **rapid exit** — script finishes so fast that stdout buffer never reaches OS before process exit, despite `sys.exit(0)`. Normally Python flushes on exit, but cron's subshell redirection might close FD before Python flushes.

---

## Evidence for Buffer-Flush Theory

- Script runtime: ~2–3 seconds ( evidenced by manual run timing )
- File mtime updated within 1 second of cron spawn (syslog→mtime delta ≈ 1s )
- No stderr written → no Python exception
- Manual run always produces output → code path is correct
- Cron run produced exit 0 but zero bytes → stdout never hit disk

**Testable prediction:** Add `sys.stdout.flush()` after final print will fix.

---

## Recommended Fix (to be applied by YoYo)

Edit `defi-milestone-tracker.py` — add explicit flush at end:

```python
# Existing final print:
print(f"\n`Mode: normal mode | baseline | Source: DexScreener | Check: {check_time} EDT`")

# ADD:
sys.stdout.flush()
```

Alternatively, change cron redirection to use `stdbuf`:
```bash
*/10 * * * * ... python3 script.py | stdbuf -o0 tee -a cron.log
```
But simpler to fix script.

---

## Replication Steps

1. Set up test cron writing short script
2. Make script exit immediately after `print("test")` without flush
3. Observe: file mtime updates, content empty
4. Add `sys.stdout.flush()` → content appears

---

## Follow-up Tasks

- [ ] Verify: Check next 3 cron ticks (00:10, 00:20, 00:30) for same pattern
- [ ] Instrument: Add script startup timestamp to cron.log on next run
- [ ] Check: `dmesg | tail -50` for I/O errors around 00:00:02
- [ ] Consider: Switch to gateway cron dispatcher (bypasses system cron entirely)

---

*Case file created 2026-05-04 as part of agent-fleet-health-audit findings.*