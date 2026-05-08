# Cron DB Deadlock Repair Procedure

**Scenario:** `/root/.hermes/cron/jobs.db` is 0 bytes or corrupted; all cron jobs show `last_run: null` and never execute despite being enabled.

## Diagnosis

```bash
# 1. Check jobs DB size
ls -lh /root/.hermes/cron/jobs.db
# Expected: >0 bytes (typically 3–20 KB). If 0 bytes → corrupted.

# 2. Verify jobs.json is intact
jq '.' /root/.hermes/cron/jobs.json > /dev/null && echo "jobs.json OK" || echo "jobs.json CORRUPT"

# 3. Check for lockfiles
ls -la /root/.hermes/cron/*.lock 2>/dev/null
# If present, stop all gateways first (they hold locks)

# 4. Confirm no cron scheduler process is running
ps aux | grep -E 'hermes.*cron|scheduler' | grep -v grep
# Should see nothing (cron runs as threads within gateways, not standalone processes)
```

## Repair (Data-Loss Tolerant)

The `jobs.db` is a runtime cache. The source of truth is `jobs.json`. Safe to rebuild:

```bash
# 1. Stop all Hermes gateways (prevents write conflicts)
systemctl --user stop hermes-gateway-yoyo
systemctl --user stop hermes-gateway-dmob
systemctl --user stop hermes-gateway-desmond
systemctl --user stop hermes-gateway-gentech

# Or kill directly:
pkill -f 'hermes_cli.main --profile yoyo gateway run'
pkill -f 'hermes_cli.main --profile dmob gateway run'
pkill -f 'hermes_cli.main --profile desmond gateway run'
pkill -f 'hermes_cli.main --profile gentech gateway run'

# 2. Remove corrupted DB
rm -f /root/.hermes/cron/jobs.db

# 3. Also clear any lockfiles/state
rm -f /root/.hermes/cron/executor.lock
rm -f /root/.hermes/cron/executor.state

# 4. Restart gateways (they will recreate jobs.db from jobs.json)
# Start each profile:
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile yoyo gateway run --replace &
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile dmob gateway run --replace &
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile desmond gateway run --replace &
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile gentech gateway run --replace &

# Or via systemd user units:
systemctl --user start hermes-gateway-yoyo
systemctl --user start hermes-gateway-dmob
systemctl --user start hermes-gateway-desmond
systemctl --user start hermes-gateway-gentech
```

## Verification

```bash
# After 30 seconds, check DB is recreated and populated
ls -lh /root/.hermes/cron/jobs.db
sqlite3 /root/.hermes/cron/jobs.db "SELECT COUNT(*) FROM jobs;"

# Check jobs now have last_run timestamps (after first execution)
jq '.jobs[] | "\(.name) last=\(.last_run_at)"' /root/.hermes/cron/jobs.json

# Monitor scheduler log for dispatches
tail -f /root/.hermes/cron/scheduler.log
# Should see "Dispatching job..." entries
```

## Prevention

- Monitor `jobs.db` size via cron: alert if < 100 bytes
- Ensure gateways are not killed with `SIGKILL` (use `SIGTERM` or systemd stop)
- Avoid concurrent gateway restarts (stagger by 10s)

## Recovery Checklist

- [ ] All 4 gateways stopped
- [ ] `jobs.db` removed
- [ ] Lockfiles cleared
- [ ] Gateways restarted cleanly
- [ ] `jobs.db` size > 0 within 60 seconds
- [ ] At least one cron job executes within schedule window
- [ ] No `database is locked` errors in agent logs
