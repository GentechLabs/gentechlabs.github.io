# Multi-Agent Systemic Failure — May 3, 2026

**Incident ID:** INC-20260503-ALL-AUTH-REVOKE

**Scope:** All four agents (YoYo, DMOB, Desmond, Gentech) simultaneously degraded.

## Timeline Summary

- **May 1 23:24 UTC** — Nous Portal refresh token revoked for the shared organization account. All agents using `stepfun/step-3.5-flash` began failing with `Refresh session has been revoked`.
- **May 3 12:04–12:05 UTC** — Coordinated gateway crash cascade: all four gateways crashed within 60 seconds, exited code 1, systemd Restart=on-failure revived them.
- **May 3 14:35 UTC** — Gentech gateway stopped via `--replace` takeover (planned), restarted cleanly.
- **Ongoing** — Cron subsystem partially blocked; 24 of 70 jobs failing across agents due to auth + Python threading issues in Gentech.

## Error Patterns Observed

### Primary: Nous Portal Auth Revocation (Shared)

```
RuntimeError: Refresh session has been revoked Run `hermes model` to re-authenticate.
AuthError: Refresh session has been revoked
```

**Affected:** ALL agents (broadcast failure due to shared Nous auth token)

**Impact:** Blocks any job that calls an LLM provider (scheduler, summarization, content generation). Jobs fail immediately; gateways stay running but most cron jobs error out.

**Detection across agents:**
```bash
grep -r 'Refresh session has been revoked' /root/.hermes/profiles/*/logs/errors.log
```

**Recovery:** `hermes model` per-profile re-authentication. Note: all four agents need individual re-auth even though they share the same Nous account.

---

### Secondary: Nous API Key Invalid (401)

```
RuntimeError: Error code: 401 - {'status': 401, 'message': 'Your API key is invalid, blocked or out of funds.'}
```

**Affected:** DMOB, Desmond, Gentech (3 of 4)

**Impact:** Same as auth revocation but at API key level. Jobs calling stepfun fail.

**Note:** Same underlying cause (Nous Portal credential issue) but manifests as 401 on API calls rather than refresh-token error.

---

### Tertiary: Python Interpreter Threading Failure (Gentech-specific)

```
delivery error: Telegram send failed:
  Unknown error in HTTP implementation:
  RuntimeError('cannot schedule new futures after interpreter shutdown')
```

**Affected:** Gentech only (observed)

**Impact:** Telegram delivery fails for ANY job after this error appears. The cron executor's futures thread pool has been shut down, typically after an unhandled exception in a job that closes the interpreter's thread context. Recovery requires gateway restart.

**Diagnostic markers:**
- Error appears in `gateway.log` in the delivery/TTS module stack
- Follows a prior unhandled exception (e.g., auth failure, DB corruption) that may have triggered interpreter cleanup
- Multiple subsequent jobs all fail with the same "cannot schedule new futures" message

**Recovery:**
1. Stop Gentech gateway: `hermes -p gentech gateway stop`
2. Clear stale locks: `rm -f /root/.hermes/profiles/gentech/gateway.pid`
3. Restart: `hermes -p gentech gateway run`
4. Verify: Check `gateway.log` for `Cron ticker started` followed by successful job executions (no threading errors)

---

## Cron Job Failure Spread (as of May 3 15:00 UTC)

| Agent   | Total Jobs | Failed Jobs | Failed Rate |
|---------|------------|-------------|-------------|
| YoYo    | 27         | 5           | 19%         |
| DMOB    | 8          | 2           | 25%         |
| Desmond | 6          | 3           | 50%         |
| Gentech | 31         | 14          | 45%         |
| **Total** | **72**   | **24**      | **33%**     |

**Failed job categories:**
- **Mess Hall shifts** (Gentech: Pre, Post, Breaks 1–3) — auth-blocked
- **Skills Update** (YoYo, Gentech) — auth-blocked
- **Brain Backup** (YoYo, Gentech) — auth-blocked
- **LayerZero DVN Monitor** (DMOB, Desmond, Gentech) — auth-blocked
- **x402 Monitor** (YoYo, Gentech) — auth-blocked
- **Social monitoring** (Gentech: social-briefing, social-monitor) — auth-blocked
- **Hackathon bounty monitoring** (Gentech) — auth-blocked
- **Kite AI submission check** (Gentech) — auth-blocked

**Healthy jobs:**
- D5 Milestone (YoYo) — running every 10 minutes with on-chain verification logic, unaffected (uses direct RPC, no LLM)
- Omni-Summary Master Brief (YoYo)
- Vault Manager — Nightly Sweep (Gentech)
- Most labs daily standup jobs (DMOB)

---

## Correlation: Shared Nous Auth Token

All four agents use the same Nous model provider (`stepfun/step-3.5-flash`), which authenticates via a shared org-level refresh token stored in each profile's `auth.json`. When Nous Portal revoked the token on May 1, **all agents became unable to call the model simultaneously**.

**Detection pattern:** Multiple agents logging identical `Refresh session has been revoked` within minutes of each other (check system journal for correlation).

**Recovery coordination:** All agents must be re-authenticated individually (`hermes model` per profile). There is no single "re-auth all" command; must loop:
```bash
for agent in yoyo dmob desmond gentech; do
  HERMES_PROFILE=$agent hermes model
done
```

**Prevention:**
- Monitor Nous Portal token expiry (typically 30-day refresh window)
- Set calendar reminder to re-auth all agents before token expiration
- Consider token rotation alerting via email/SMS from Nous Portal

---

## Python Threading Error: "cannot schedule new futures after interpreter shutdown"

**Context:** This error appears in Gentech's gateway logs when the cron executor's thread pool executor (`concurrent.futures.ThreadPoolExecutor`) has been shut down, but a job still attempts to submit new work (typically a Telegram send or skill invocation).

**Trigger chain:**
1. An unhandled exception in a cron job's `finally`/`except` block triggers interpreter cleanup
2. The executor's `_python_exit` shuts down the thread pool
3. Subsequent cron jobs attempt to dispatch via the same (now closed) executor
4. Python raises `RuntimeError: cannot schedule new futures after interpreter shutdown`

**Error signature:**
```
WARNING gateway.run: Delivery error: Telegram send failed:
  Unknown error in HTTP implementation:
  RuntimeError('cannot schedule new futures after interpreter shutdown')
```

**Immediate fix:** Restart the affected agent's gateway (clears executor state).

**Long-term fix:** Identify the root unhandled exception that triggered the interpreter shutdown cascade. Check `gateway.log` 5–10 minutes BEFORE the first threading error for:
- Uncaught tracebacks in job execution
- Database corruption errors (SQLite `database disk image is malformed`)
- Memory errors (`MemoryError`, `OSError: [Errno 28] No space left on device`)
- Auth failures that were not caught

**Monitoring:** Add a health-check probe that scans `gateway.log` for this string and auto-restarts the gateway if detected.

---

## Cron Job Status Inspection via jobs.json

When `hermes cron list` does not show `last_run` or `last_status` fields (showing `N/A`), the embedded cron database may be out of sync. **Direct `jobs.json` inspection is more reliable.**

**Per-agent cron job files:**
```
/root/.hermes/cron/jobs.json              # global/default (only 5 jobs, outdated)
/root/.hermes/profiles/yoyo/cron/jobs.json   # authoritative for YoYo
/root/.hermes/profiles/dmob/cron/jobs.json   # authoritative for DMOB
/root/.hermes/profiles/desmond/cron/jobs.json
/root/.hermes/profiles/gentech/cron/jobs.json
```

**Quick status check script:**
```bash
for agent in yoyo dmob desmond gentech; do
  cron_file="/root/.hermes/profiles/$agent/cron/jobs.json"
  if [ -f "$cron_file" ]; then
    errors=$(python3 -c "
import json, sys
d=json.load(open('$cron_file'))
fails=[j for j in d['jobs'] if j.get('last_status')=='error']
print(len(fails))
")
    total=$(python3 -c "import json; print(len(json.load(open('$cron_file'))['jobs']))")
    echo "$agent: $errors / $total jobs with errors"
  fi
done
```

---

## Correlation Matrix — May 3 Failure Modes

| Failure Mode                | YoYo | DMOB | Desmond | Gentech | Shared Root Cause |
|-----------------------------|------|------|---------|---------|-------------------|
| Nous auth revocation        | ✅   | ✅   | ✅      | ✅      | Nous token revoked May 1 |
| Nous API 401 errors         | ✅   | ✅   | ✅      | ✅      | Same |
| Python threading crash     | ❌   | ❌   | ❌     | ✅      | Unhandled exception in Gentech job triggered interpreter shutdown |
| Cron executor deadlock     | ❌   | ❌   | ❌     | ❌      | DEPRECATED — was Phase 7 old pattern; current failures are pure auth-blocked |
| SQLite corruption          | ❌   | ❌   | ✅     | ✅      | Desmond's DB malformed; Gentech unrelated |
| ElevenLabs TTS 401 errors  | ❌   | ✅   | ✅      | ❌      | DMOB+Desmond share expired key |
| Telegram "Chat not found"  | ❌   | ✅   | ❌      | ❌      | DMOB channel `-100386354028` mismatch (should be `-1003863540828` HQ) |

**Conclusion:** The dominant failure mode (24/24 failed jobs) is **Nous auth revocation affecting all agents**. Secondary issues (Python threading in Gentech, SQLite in Desmond, TTS keys) compound but are not the primary cause.

---

## Health Status Reporting Rule (USER PREFERENCE)

**User directive:** "If all agents are healthy and no issues detected, respond with exactly `STATUS:OK` and nothing else. Do NOT report 'all systems nominal' or any health summary."

**When issues detected:** Use alert format only:
```
🚨 Watchdog Alert: [what's wrong]
```

**Do NOT:** Prepend explanations, state the obvious, or add filler. The user will see the alert details in the alert body itself.

---

## Recovery Sequence (May 3 Priority Order)

1. **Re-authenticate all agents to Nous Portal** (unblocks 24/24 failing cron jobs)
   ```bash
   for agent in yoyo dmob desmond gentech; do
     HERMES_PROFILE=$agent hermes model
   done
   ```

2. **Restart Gentech** only (fix Python threading error)
   ```bash
   hermes -p gentech gateway stop
   rm -f /root/.hermes/profiles/gentech/gateway.pid
   hermes -p gentech gateway run
   ```

3. **Refresh DMOB & Desmond ElevenLabs keys** (restore TTS functionality)
   - Update `ELEVENLABS_API_KEY` in profile config

4. **Repair Desmond SQLite DB** (malformed)
   - Restore from backup or rebuild kanban.db

5. **Fix DMOB Telegram channel** (`-100386354028` → `-1003863540828`)
   - Edit `/root/.hermes/profiles/dmob/.env` or config.yaml

6. **Clear corrupted bytecode** (if marshal errors appear again)
   ```bash
   find /usr/local/lib/hermes-agent -name "*.pyc" -delete
   find /root/.hermes/profiles -name "*.pyc" -delete
   ```

7. **Monitor Watchdog job (runs every 5 min)** for clearance of all error statuses.
