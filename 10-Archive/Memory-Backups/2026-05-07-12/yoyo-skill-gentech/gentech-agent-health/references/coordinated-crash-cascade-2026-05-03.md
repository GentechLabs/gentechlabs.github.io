# Coordinated Gateway Crash Cascade — May 3, 2026

**Event:** All 4 Hermes gateways (YoYo, DMOB, Desmond, Gentech) crashed within 60 seconds and failed to restart cleanly until manual intervention.

**Timeline (May 3, 2026):**

| Time (UTC) | Agent | PID | Exit Code | Interpretation |
|------------|-------|-----|-----------|----------------|
| 11:52:48 | desmond | — | code=killed, status=10/USR1 | Killed by signal (likely external SIGHUP/SIGUSR1) |
| 11:52:53 | gentech | — | code=exited, status=75/TEMPFAIL | Temporary failure (config/credential issue) |
| 11:53:24 | (gap) | | | Monitoring shows 401 errors in logs |
| 11:53:48 | desmond | restarted | — | systemd auto-restart |
| 11:53:53 | gentech | restarted | — | systemd auto-restart |
| 11:54:13 | yoyo | — | code=exited, status=75/TEMPFAIL | Temporary failure |
| 11:54:21 | dmob | — | code=exited, status=75/TEMPFAIL | Temporary failure |
| 11:55:13 | yoyo | restarted | — | manual start |
| 11:55:21 | dmob | restarted | — | manual start |

**Systemd logs:**
```
May 03 11:52:48 hermes-gateway-desmond.service: Main process exited, code=killed, status=10/USR1
May 03 11:52:48 hermes-gateway-desmond.service: Failed with result 'signal'.
May 03 11:52:53 hermes-gateway-gentech.service: Main process exited, code=exited, status=75/TEMPFAIL
May 03 11:52:53 hermes-gateway-gentech.service: Failed with result 'exit-code'.
May 03 11:54:13 hermes-gateway-yoyo.service: Main process exited, code=exited, status=75/TEMPFAIL
May 03 11:54:21 hermes-gateway-dmob.service: Main process exited, code=exited, status=75/TEMPFAIL
```

---

## Root Cause Hypotheses

1. **Primary trigger:** **Nous Portal refresh token revocation** (see `nous-portal-refresh-token-revocation-2026-05-03.md`). All agents using the `nous` provider hit `RuntimeError: Refresh session has been revoked` simultaneously when the shared token became invalid. This exception likely propagated to the gateway run loop, causing TEMPFAIL exits.

2. **Secondary factor:** **Python bytecode corruption** (`EOFError: marshal data too short`) in `/usr/local/lib/hermes-agent/agent/__pycache__/`. Corrupted imports can cause segfaults or unhandled exceptions in the gateway main thread, especially if affected modules are imported during startup after a restart.

3. **Resource contention:** Disk I/O errors were previously observed (May 1-2) with `sqlite3.OperationalError: database disk image is malformed` and `No space left on device`. While disk was not full at crash time (`df -h` showed 37G free on /dev/sda1), earlier corruption may have lingering effects.

4. **Coordinated health-check side effect:** The `Gentech Watchdog` cron job (ID `9ecfada01952`) itself was executing at 11:30–12:30 and encountering auth errors. It may have triggered agent restarts via a self-heal hook that backfired when the refresh token was already invalid.

---

## Crash Modalities

| Agent | Exit Code | What Happened |
|-------|-----------|----------------|
| Desmond | 10/USR1 (SIGUSR1) | Killed by external signal — likely a stop command (systemctl stop OR manual `hermes gateway stop`) |
| Gentech | 75/TEMPFAIL | Hermes temporary failure (config/credential error preventing startup) |
| YoYo | 75/TEMPFAIL | Same as above |
| DMOB | 75/TEMPFAIL | Same as above |

**TEMPFAIL (75)** is Hermes' exit code for transient startup failure — commonly credential missing, provider unreachable, or config parse error. The pattern suggests the gateways attempted a restart (possibly auto-restart from systemd), hit a credential error during init, and exited with TEMPFAIL again.

---

## Detection: Coordinated Crash Wave

**Check systemd journal for clustered exits within 1 minute:**
```bash
journalctl --user -u hermes-gateway-*.service --since "10 minutes ago" \
  | grep "Main process exited" \
  | awk '{print $1, $2, $3, $15, $16}' \
  | sort
```

**Script to detect coordinated exits:**
```python
import subprocess, re
from datetime import datetime, timedelta

result = subprocess.run(
  ['journalctl', '--user', '-u', 'hermes-gateway-*.service',
   '--since', '30 minutes ago'],
  capture_output=True, text=True
)

exits = {}
for line in result.stdout.split('\n'):
  m = re.search(r'hermes-gateway-(\w+)\.service: Main process exited.*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
  if m:
    agent = m.group(1)
    time = datetime.strptime(m.group(2), '%Y-%m-%d %H:%M:%S')
    exits.setdefault(agent, []).append(time)

# Check if last exit wave was coordinated
all_last = [v[-1] for v in exits.values() if v]
if all_last:
  spread = max(all_last) - min(all_last)
  if spread < timedelta(seconds=60):
    print(f"🚨 Coordinated crash wave: {len(all_last)} agents exited within {spread}")
    for agent, times in exits.items():
      print(f"  {agent}: {times[-1].strftime('%H:%M:%S')}")
```

---

## Recovery Sequence (What Worked May 3)

**Initial state** (11:52–11:56): All gateways crashed or exited with TEMPFAIL. Automatic systemd restart attempts produced TEMPFAIL loops.

**Failed recovery attempts observed in logs:**
- Auto-restart (systemd) — gateways started but immediately hit auth error → exited with TEMPFAIL again
- No manual intervention initially; processes remained down for ~8 minutes

**Successful recovery (manual):**
1. **Stop all gateways** (if any zombie processes):
   ```bash
   for a in yoyo dmob desmond gentech; do
     hermes -p $a gateway stop 2>/dev/null || true
   done
   ```

2. **Re-authenticate Nous Portal** on each profile (`hermes model`) — this is the **critical path**. Without valid tokens, gateways cannot initialize the model provider and exit with TEMPFAIL.

3. **Purge corrupted bytecode** (observed in earlier session, not performed May 3 but recommended):
   ```bash
   find /usr/local/lib/hermes-agent -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
   ```

4. **Start gateways one at a time:**
   ```bash
   for a in gentech yoyo dmob desmond; do
     hermes -p $a gateway start
     sleep 3
   done
   ```

5. **Verify Telegram connectivity** (gateway.log should show "Connected to Telegram" within 30s).

---

## Post-Mortem: Why did this happen?

### Chain of events (reconstructed):

1. **May 1 23:24 UTC** — Nous Portal access token expired (`auth.json` `last_status: None`, `access_token_expires: 2026-05-01T23:24:26Z`).

2. **May 1–2** — Multiple agents attempted token refresh using stale refresh token. Hermes' auto-refresh logic called `POST /api/oauth/token` multiple times across different agent processes (each gateway has its own credential cache but shares `~/.hermes/auth.json` pool). This triggered **refresh-token reuse detection** on Nous side, which **revoked the session entirely**.

3. **May 2–3** — Some jobs continued to fail with 401 errors; `hermes status` incorrectly showed "logged in" due to stale cached state.

4. **May 3 11:30** — `Gentech Watchdog` cron job executed and encountered auth error. There may have been a self-heal script or health-check that attempted to restart gateways.

5. **May 3 11:52–11:56** — Either:
   - A health-check cycle (cron ticker) detected gateways unhealthy and issued stop commands (explains Desmond's SIGUSR1), or
   - The auth error caused an unhandled exception in the gateway run loop (explains TEMPFAIL exits)

6. **11:53–11:55** — systemd auto-restart attempted, but gateways failed again because Nous token still revoked.

7. **Post-11:55** — Manual `hermes model` re-authentication restored tokens; gateways remained running after restart.

---

## Prevention Checklist

- [ ] **Single Hermes process per profile** — Ensure no parallel gateways for the same agent (`ps aux | grep hermes` should show exactly 4 processes, one per profile)
- [ ] **No external auth token polling** — All credential health checks must route through `hermes auth status`, not direct API calls that consume the refresh token
- [ ] **Auth expiry monitoring** — Add watchdog cron (system-level, outside Hermes) to alert 24h before Nous tokens expire:
  ```bash
  # Check Nous expiry in yoyo profile (most active)
  exp=$(hermes -p yoyo auth status 2>&1 | grep -oP 'expires:\s*\K.*')
  if [[ $(date -d "$exp" +%s) -lt $(date -d '+24 hours' +%s) ]]; then
    echo "⚠️  Nous token expiring soon: $exp" | telegraph -G Gentech-Alerts
  fi
  ```
- [ ] **Gateways restart orchestration** — Use coordinated restart script (stop all → wait → start all) rather than independent restarts during auth rotation
- [ ] **Post-restart health verification** — After any gateway restart, confirm:
  ```bash
  hermes -p <agent> gateway status | grep -q "Cron ticker started" || \
    echo "CRITICAL: $agent cron ticker not running"
  ```
- [ ] **Bytecode cache purge before major restart waves** — If upgrading Hermes or rotating credentials fleet-wide, clear `__pycache__` first to avoid `marshal data too short` crashes on import

---

## Related Signal Correlation

When you see a coordinated crash wave, check these logs **in order**:

1. **`/root/.hermes/profiles/*/logs/errors.log`** — last 20 lines per agent BEFORE the crash
   - Look for: `Refresh session has been revoked`, `AuthError`, `No API key`, `EOFError: marshal data too short`

2. **`journalctl --user -u hermes-gateway-*.service --since "5 minutes before crash"`**
   - Look for: External stop commands (`systemctl stop`), OOM kills, disk pressure events

3. **`df -h` and `dmesg | tail -20`** at crash time (if systemd captured it)
   - Look for: `No space left on device`, `I/O error`, `kernel: Out of memory`

4. **Cron job that triggered just before crash** (`hermes cron list --show-next` + gateway.log job dispatch lines)
   - Was the crash coincident with a specific job execution? That job's code/script may have raised fatal exception.

---

## Quick Diagnosis Decision Tree

```
All agents down simultaneously?
│
├─ Yes → Check auth status first:
│   └─ All show "Refresh session has been revoked"?
│       ├─ YES → Systemic Nous auth cascade. Run `hermes model` on all profiles.
│       └─ NO → Check systemd journal for coordinated stop/kill signals.
│
├─ Partial outage → Check per-agent:
│   ├─ TEMPFAIL exit on start → Credential/config issue; run `hermes -p <agent> gateway start --debug`
│   ├─ Signal 10/15 killed → External orchestrator (self-heal, update script) — check cron health
│   └─ Pure crash (segfault/SIGSEGV) → Bytecode corruption or native extension bug; purge `__pycache__`
│
└─ Gateways running but cron not executing → Cron executor deadlock (see skill main doc)
```

---

## Files to Audit After Recovery

- `~/.hermes/auth.json` — confirm `nous` credentials refreshed, `last_status` no longer "None"
- `/root/.hermes/cron/jobs.json` — verify no corruption (all jobs have `profile`, `script`, `task_id`)
- `/root/.hermes/profiles/*/logs/gateway.log` — confirm "Cron ticker started" within last 5 min
- `/root/.hermes/profiles/*/logs/errors.log` — ensure no new error entries after restart
