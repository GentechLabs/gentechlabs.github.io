# Nous OAuth Cascade Failure — Fleet-Wide Auth Incident

**Date:** 2026-05-03  
**Incident ID:** INC-20260503-1930  
**Severity:** 🔴 CRITICAL — Fleet-wide LLM dependency outage  
**Detected:** 18:49 UTC by Gentech Watchdog cron (cron_9ecfada01952)  
**Status:** ACTIVE (requires manual intervention)  

---

## Executive Summary

Nous Portal OAuth refresh token expired and was revoked server-side. All four Hermes agents (Gentech, YoYo, DMOB, Desmond) lost LLM access simultaneously. Data collection cron jobs and agent tool calls failed fleet-wide. Automated refresh script (`refresh_nous_oauth.py`) cannot recover; requires interactive `hermes model` re-authentication in a TTY.

**Timeline to full cascade:** ~30 minutes from token expiry to complete fleet lockout.

---

## Tiered Failure Progression

### Tier 1 — OAuth Expiry (T=0)

**Time:** 12:44 UTC (initial token expiry; not detected until later)

- Nous access token naturally expires (30-day TTL)
- Refresh token remains valid but is not automatically used by Hermes core
- No immediate impact: existing token valid until exact expiry timestamp

---

### Tier 2 — First Failure Detection (T≈18:30–18:49 UTC)

**Detection:** Proactive refresh script (`*/10 * * * *`) attempts refresh

```bash
# refresh_nous_oauth.py output
{ "success": false, "needs_reauth": true, "message": "Refresh session has been revoked" }
```

**Simultaneous symptoms across all agents:**

| Agent | Error in gateway.log |
|-------|----------------------|
| Gentech | `ERROR tools.web_tools: Firecrawl client initialization failed: missing direct config and tool-gateway auth.` |
| YoYo | `ERROR tools.web_tools: Firecrawl client initialization failed: missing direct config and tool-gateway auth.` |
| DMOB | `ERROR tools.web_tools: Firecrawl client initialization failed: missing direct config and tool-gateway auth.` |
| Desmond | `ERROR tools.web_tools: Firecrawl client initialization failed: missing direct config and tool-gateway auth.` |

**Why Firecrawl fails first:** Hermes initializes tools lazily on first use. The first agent to attempt a web tool call triggers the auth check, fails, and logs the error. Within minutes, all agents exhibit this pattern as they try to use Nous-managed tools.

**auth.json state:** Still shows Nous provider entry, but `access_token_expiry` in past.

---

### Tier 3 — Cron Job Failures (T≈19:00 UTC)

**First failing cron:** "Gentech Watchdog" at 19:01:26

```
2026-05-03 19:01:26,869 ERROR [20260503_182520_6404ebc0] tools.web_tools: Firecrawl client initialization failed...
2026-05-03 19:01:28,293 WARNING hermes_cli.copilot_auth: Token from GITHUB_TOKEN is not supported...
2026-05-03 19:01:??,??? ERROR cron.scheduler: Job 'Gentech Watchdog' failed: RuntimeError: Hermes is not logged into Nous Portal
```

**Cascading cron failures (order observed):**

1. **19:01** — Gentech Watchdog (first)
2. **19:06** — DMOB checkpoint jobs
3. **19:11–19:15** — YoYo Crypto Watchlist + LP Monitor
4. **19:30–19:36** — Desmond monitoring jobs (Kite AI, LayerZero)

**Error signature consistency:**
```
RuntimeError: Refresh session has been revoked
Run `hermes model` to re-authenticate.
```

Traceback chain:
```
cron/scheduler.py → resolve_runtime_provider → resolve_nous_runtime_credentials
→ _refresh_access_token → raise AuthError("Refresh session has been revoked")
→ RuntimeError
```

---

### Tier 4 — Auth State Corruption (T≈19:30–19:45 UTC)

**Critical transition:** `auth.json` loses provider configuration entirely.

Before (suspected):
```json
{
  "providers": {
    "nous": {
      "access_token": "...",
      "expires_at": 1748892800,
      "refresh_token": "..."
    }
  }
}
```

After (confirmed at 19:47):
```json
{
  "providers": {}
}
```

**Cause:** Hermes credential pool eviction after repeated failed refresh attempts. The auth subsystem clears invalid credentials from the pool, leaving `providers` empty. This is **by design** (failed auth → credential removal) but manifests as systemic corruption.

**Symptoms:**
- Refresh script now returns: `"No access token found for Nous Portal login. Run hermes model to re-authenticate."`
- Every Hermes operation hitting Nous API fails immediately
- Gateway processes remain running but are functionally offline

---

### Tier 5 — Cron Registry Corruption (T≈19:50 UTC)

**Observed:** `hermes cron list` shows **0 jobs** for gentech profile.

Actual state: Jobs exist in `jobs.json` but `jobs.db` runtime DB is unreachable or empty.

```
$ hermes cron list
┌─────────────────────────────────────────────────────────────────────────┐
│                         Scheduled Jobs                                  │
└─────────────────────────────────────────────────────────────────────────┘

  682e9597b8d6 [active]   ← shown but details missing
```

**Root cause:** Cron scheduler cannot read/write `jobs.db` due to auth failure locking or filesystem sync issue. Running `hermes cron list` queries the DB directly; if DB is 0 bytes or locked, no jobs appear.

**Verification:**

```bash
# DB size check
ls -lh /root/.hermes/cron/jobs.db
# Expected: ~4–20 KB. If 0 bytes → corruption.

# JSON source check
jq '.jobs[] | .name' /root/.hermes/cron/jobs.json | head
# Should list all expected jobs (Watchdog, Mess Hall, Kite AI, etc.)
```

In this incident: `jobs.db` present but unreadable; `jobs.json` intact. Recovery requires stopping all gateways and letting cron executor rebuild DB on next launch.

---

## Diagnostic Command Reference

### Immediate Fleet Status (run as root)

```bash
#!/bin/bash
# 1. Gateway liveness
ps aux | grep 'hermes_cli.main --profile' | grep -v grep

# 2. Auth state snapshot (all agents)
for p in yoyo dmob desmond gentech; do
  echo "=== $p ==="
  auth="/root/.hermes/profiles/$p/auth.json"
  if [ -f "$auth" ]; then
    python3 -c "
import json, datetime
d = json.load(open('$auth'))
providers = d.get('providers', {})
print(f'Providers: {len(providers)}')
if 'nous' in providers:
    np = providers['nous']
    exp = np.get('expires_at', 0)
    print(f'Nous expires: {datetime.datetime.fromtimestamp(exp) if exp else \"NEVER\"}')
else:
    print('NO NOUS PROVIDER')
active = d.get('active_provider', 'none')
print(f'Active: {active}')
"
  else
    echo 'NO auth.json'
  fi
done

# 3. Refresh script test (gentech profile)
python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py

# 4. Error velocity (last 50 lines)
for p in yoyo dmob desmond gentech; do
  errcount=$(tail -50 /root/.hermes/profiles/$p/logs/errors.log 2>/dev/null | grep -c ' ERROR ' || echo 0)
  echo "[$p] $errcount ERRORS in last 50 lines"
done

# 5. Cron registry health
hermes cron list 2>/dev/null | head -20
echo "Jobs DB size: $(du -h /root/.hermes/cron/jobs.db 2>/dev/null || echo 'missing')"
echo "Jobs JSON count: $(jq '.jobs | length' /root/.hermes/cron/jobs.json 2>/dev/null || echo 'parse error')"

# 6. Last organic session check (are agents actually working?)
for p in yoyo dmob desmond gentech; do
  latest=$(ls -t /root/.hermes/profiles/$p/sessions/session_*.json 2>/dev/null | grep -v session_cron_ | head -1)
  if [ -n "$latest" ]; then
    status=$(python3 -c "import json; print(json.load(open('$latest')).get('status','unknown'))" 2>/dev/null)
    echo "[$p] Latest organic: $(basename $latest) → $status"
  else
    echo "[$p] NO organic sessions found"
  fi
done
```

---

## Recovery Playbook

**Owner:** @DMOB (Hermes infrastructure lead)

**Prerequisites:** Interactive TTY access (SSH with terminal, not just file access)

### Step 1 — Immediate Stabilization (5 min)

**Action:** Re-authenticate Nous Portal for the Gentech profile (primary credential holder).

```bash
# Switch to gentech profile (if not root)
su - gentech 2>/dev/null || true

# Trigger interactive OAuth flow
hermes model
```

**Expected flow:**
1. Hermes prints: "Nous Portal device authorization initiated"
2. Shows verification URL with 10-minute window
3. Complete browser auth at https://portal.nousresearch.com/manage-subscription?user_code=XXXX-XXXX
4. After browser completion, wait ~30 sec for token propagation
5. Return to terminal; hermes model exits with success

**If `hermes model` fails with "Token from GITHUB_TOKEN not supported":**
```bash
# Use device flow bypass (non-interactive)
python3 -m hermes_cli.main --profile gentech auth login --provider nous --no-browser
# Then manually visit the printed URL within 10 minutes
```

---

### Step 2 — Verify Token Renewal (2 min)

```bash
# Run refresh script manually — should return success
python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py

# Expected output:
# { "success": true, "needs_reauth": false, "expires_at": "2026-06-02T..." }
```

If `needs_reauth` still true after Step 1 → OAuth rate-limited. Wait 15 min, retry.

---

### Step 3 — Restore Cron Registry (2 min)

If `hermes cron list` still shows 0 jobs after Step 2:

```bash
# Stop all gateways first
pkill -f 'hermes_cli.main --profile'

# Check jobs.json integrity
jq '.jobs[] | {id, name, profile, script, task_id}' /root/.hermes/cron/jobs.json | head

# If valid, truncate jobs.db to force rebuild
> /root/.hermes/cron/jobs.db

# Restart gateways
systemctl restart --user hermes-gateway 2>/dev/null || true
# Or start manually:
for p in gentech yoyo dmob desmond; do
  hermes --profile $p gateway run --replace &
done

# Wait 10 sec, then verify
hermes cron list | head -20
```

---

### Step 4 — Validate Recovery (5 min)

```bash
# 1. Check error log quieting
tail -20 /root/.hermes/profiles/gentech/logs/errors.log | grep -c 'ERROR'  # should be 0 or single isolated

# 2. Test a Nous-dependent cron job manually
hermes cron run --name "YoYo — Crypto Watchlist + LP Monitor" 2>&1 | tail -20

# 3. Verify Telegram gateways responding
tail -5 /root/.hermes/profiles/yoyo/logs/gateway.log | grep 'Sending response'
```

**Success criteria:**
- `refresh_nous_oauth.py` returns `"success": true`
- At least one agent shows `Sending response` in gateway.log within last 2 min
- `hermes cron list` shows all expected jobs with future `next_run` timestamps
- No `Firecrawl client initialization failed` errors in last 50 lines per agent

---

## Post-Incident Actions

1. **Update alert threshold:** Set `WARNING` if auth.json providers count drops below 1 for any profile
2. **Add watchdog pre-check:** Before each watchdog run, verify `auth.json` providers non-empty fleet-wide — if empty, skip health checks and alert immediately (watchdog cannot function without auth)
3. **Document rate-limit behavior:** Nous OAuth device flow endpoint (`POST /oauth/device/code`) returns 429 after 5 concurrent requests from same IP. If re-auth fails with 429, wait 15 minutes before retrying.
4. **Consider fallback provider:** Add Ollama Cloud as secondary provider for cron jobs; route non-critical tasks to alternate LLM when Nous auth fails (see `nous-to-ollama-migration.md`)

---

## References

- Incident log: `/root/vaults/gentech/00-HQ/Operations/Infrastructure-Issues.md` (section 2026-05-03)
- Alert messages: `/root/vaults/gentech/11-Mess Hall/2026-05-03/nous-oauth-revoked-alert.md`
- Migration plan: `/root/vaults/gentech/03-Strategies/nous-to-ollama-migration.md`
- Skill notes: `references/nous-portal-refresh-token-revocation-2026-05-03.md`
- Skill notes: `references/nous-oauth-rate-limit-2026-05-03.md`

---

**Last updated:** 2026-05-03 20:20 UTC by Watchdog health check INC-20260503-1930
