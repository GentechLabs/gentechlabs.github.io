# Kanban Dispatcher Failures — DMOB & Desmond (May 1–2, 2026)

## Error Transcript

**Log pattern:** Repeated `kanban notifier tick failed: disk I/O error` followed by `ERROR gateway.run: kanban dispatcher: tick failed`

### DMOB — gateway.log lines 1787–1821
```
2026-05-01 10:15:48,573 WARNING gateway.run: kanban notifier tick failed: disk I/O error
2026-05-01 10:15:53,580 WARNING gateway.run: kanban notifier tick failed: disk I/O error
2026-05-01 10:15:58,587 WARNING gateway.run: kanban notifier tick failed: disk I/O error
2026-05-01 10:16:03,594 WARNING gateway.run: kanban notifier tick failed: disk I/O error
2026-05-01 10:16:08,600 WARNING gateway.run: kanban notifier tick failed: disk I/O error
2026-05-01 10:16:13,607 ERROR gateway.run: kanban dispatcher: tick failed
Traceback (most recent call last):
  File "/usr/local/lib/hermes-agent/gateway/run.py", line 3253, in _tick_once
    conn = _kb.connect()
           ^^^^^^^^^^^^^
  File "/usr/local/lib/hermes-agent/hermes_cli/kanban_db.py", line 388, in connect
    conn.execute("PRAGMA journal_mode=WAL")
sqlite3.OperationalError: disk I/O error
2026-05-01 10:16:18,617 WARNING gateway.run: kanban notifier tick failed: disk I/O error
  [repeated through 10:17:13]
```

### Desmond — gateway.log lines 1847–1880
```
2026-05-01 10:14:40,756 ERROR gateway.run: kanban dispatcher: tick failed
Traceback (most recent call last):
  File "/usr/local/lib/hermes-agent/gateway/run.py", line 3253, in _tick_once
    conn = _kb.connect()
           ^^^^^^^^^^^^^
  File "/usr/local/lib/hermes-agent/hermes_cli/kanban_db.py", line 388, in connect
    conn.execute("PRAGMA journal_mode=WAL")
sqlite3.OperationalError: database is locked
```
*(Earlier instances showed `disk I/O error`; later ones showed `database is locked`)*

## Root Cause Analysis

1. **Initial trigger:** May 1, ~10:15 — kanban notifier begins failing with `disk I/O error`
2. **Cascade:** After ~5 failed ticks, dispatcher reports `tick failed` with full traceback
3. **State freeze:** `kanban.db` last modified May 1 10:15; content remains 0 tasks, 0 events through May 2 check
4. **DB state on disk:** 102,400 bytes (default empty WAL-mode SQLite DB), integrity OK but **unanimated**

**Mechanism:** The kanban ticker runs every 60s embedded in the gateway. A transient disk I/O error (likely temporary filesystem pressure or lock contention) prevented SQLite from executing `PRAGMA journal_mode=WAL`. The ticker did not recover — subsequent attempts continued to fail, leaving the kanban system non-functional.

## Recovery Steps

### Immediate fix (gateway restart):
```bash
# Stop affected agents
hermes -p dmob gateway stop
hermes -p desmond gateway stop

# Verify kanban DB is not held open by another process
lsof | grep kanban.db

# Restart
hermes -p dmob gateway start
hermes -p desmond gateway start
```

### If restart does not revive kanban ticker:
```bash
# Stop gateway
hermes -p dmob gateway stop

# Remove corrupted/blocked kanban DB (gateway will recreate on next start)
rm /root/.hermes/profiles/dmob/kanban.db
rm /root/.hermes/profiles/desmond/kanban.db

# Restart
hermes -p dmob gateway start
hermes -p desmond gateway start
```

### Post-recovery validation:
```bash
# Wait 2 minutes, then check DB activity
stat /root/.hermes/profiles/dmob/kanban.db  # mtime should be recent
# Or query:
sqlite3 /root/.hermes/profiles/dmob/kanban.db "SELECT COUNT(*) FROM tasks;"
# Should be > 0 if kanban is processing
```

## Prevention & Monitoring

- **Add to agent health checklist:** kanban DB modification timestamp should be < 2h old during normal operations
- **Alert on:** `kanban dispatcher: tick failed` in gateway.log (implies >5 notifier failures)
- **If disk I/O errors appear elsewhere:** Check system disk space (`df -h`) and inode availability (`df -i`); investigate I/O wait (`iostat`)
- **If `database is locked` persists after restart:** Likely another process holding lock; check for stray Python processes with open kanban.db handles

## Related tickets

- Internal: GENTECH-2026-05-01-disk-io-pressure (root cause under investigation)
- Hermes upstream: kanban ticker resilience gap — should recover from transient I/O errors rather than freezing

</content>