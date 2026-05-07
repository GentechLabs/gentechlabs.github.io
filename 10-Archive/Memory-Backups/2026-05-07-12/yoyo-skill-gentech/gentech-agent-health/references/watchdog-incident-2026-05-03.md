# Watchdog Incident: 2026-05-03 — System-Wide OAuth & Tool-Gateway Failure

**Detected:** 2026-05-03 18:47 UTC by Gentech Watchdog (YoYo)  
**Severity:** 🔴 CRITICAL (fleet-wide functional degradation)  
**Status:** ⏳ OPEN (requires DMOB + Jordan intervention)  
**Agents affected:** yoyo, dmob, desmond, gentech (all 4)  
**Duration:** Ongoing since 12:44 UTC (6+ hours)

---

## Executive Summary

All four Gentech agents are experiencing **systemic credential and tooling failures**:

1. **Nous OAuth session revoked** — all agents missing `nous_tokens` in `auth.json`; data-collection scripts failing with 401
2. **Tool-gateway (Firecrawl) down** — no tool-gateway process running; web search broken fleet-wide
3. **Desmond missing critical skills** — `cmc-watchlist-scraper`, `crypto-monitoring-cron` not found
4. **Stalled handoffs** — 6+ days overdue (Apr 24)
5. **Telegram flood control** — ongoing rate limiting

Agent gateways are running and Telegram-connected; breakage is at credential/tooling layer, not process layer.

---

## Detection Evidence

### OAuth Failure

```bash
# All agents return empty nous_tokens from auth.json
$ cat /root/.hermes/profiles/yoyo/auth.json | python3 -c "import json,sys; a=json.load(sys.stdin); print('nous_tokens' in a)"
False
$ cat /root/.hermes/profiles/dmob/auth.json | python3 -c "import json,sys; a=json.load(sys.stdin); print('nous_tokens' in a)"
False
$ cat /root/.hermes/profiles/desmond/auth.json | python3 -c "import json,sys; a=json.load(sys.stdin); print('nous_tokens' in a)"
False
$ cat /root/.hermes/profiles/gentech/auth.json | python3 -c "import json,sys; a=json.load(sys.stdin); print('nous_tokens' in a)"
False
```

**Refresh script response:**
```json
{
  "success": false,
  "message": "No access token found for Nous Portal login. Run `hermes model` to re-authenticate.",
  "needs_reauth": true
}
```

**Error log pattern (all agents):**
```
ERROR tools.web_tools: Firecrawl client initialization failed: missing direct config and tool-gateway auth.
RuntimeError: Refresh session has been revoked Run `hermes model` to re-authenticate.
```

### Tool-Gateway Absence

```bash
$ ps aux | grep -i 'tool-gateway' | grep -v grep
(no output)

$ netstat -tlnp | grep -E '3000|8080|5000' | grep -v grep
(no output)
```

### Missing Skills (Desmond + YoYo)

Gateway logs show:
```
WARNING cron.scheduler: Cron job 'YoYo — Crypto Watchlist + LP Monitor (Hardened)': skill not found, skipping — Skill 'cmc-watchlist-scraper' not found.
WARNING cron.scheduler: Cron job 'YoYo — Crypto Watchlist + LP Monitor (Hardened)': skill not found, skipping — Skill 'crypto-monitoring-cron' not found.
```

---

## Timeline of Events

| Time (UTC) | Event |
|------------|-------|
| 12:44:21 | Nous access token expires |
| 12:45–12:50 | Proactive refresh script runs */10 schedule; detects `needs_reauth: true`; logs error |
| 12:37–12:47 | DMOB runs `hermes model` in GenTech Labs to re-authenticate Nous provider (per today-context.md) |
| 13:01 | Alert drafted in Mess Hall (`nous-oauth-revoked-alert.md`) |
| 13:41 | Alert published; status: **STILL AWAITING MANUAL FIX** |
| 14:33 | Gentech gateway restarted (gateway.log shows shutdown diagnostic) |
| 18:44–18:47 | Watchdog runs health check; discovers OAuth tokens still missing from auth.json; tool-gateway still not running |
| 18:47 | Watchdog Alert published |

**Gap identified:** DMOB's `hermes model` execution did not persist Nous tokens to disk. Root cause unknown — possible Hermes provider state commit bug or disk write permission issue.

---

## Impact Assessment

| Component | Impact | Severity |
|-----------|--------|----------|
| Data-collection scripts (kite-hackathon-checks, layerzero-monitor, social-monitors) | All failing 401 | 🔴 Critical |
| Web search / Firecrawl tool | Unavailable for all agents | 🔴 Critical |
| LP & crypto watchlist monitoring | Silent skip (missing skills) | 🟡 Medium |
| Overdue handoffs | 6+ days blocked | 🟡 Medium |
| Telegram messaging | Operational but flood-controlled | 🟢 Low |
| Agent gateways | Running and connected | ✅ Healthy |

---

## Recovery Checklist

### Phase 1 — Restore Data Collection (DMOB)

- [ ] Run `hermes model` in **each** agent profile sequentially:
  ```bash
  HERMES_HOME=/root/.hermes/profiles/yoyo hermes model
  HERMES_HOME=/root/.hermes/profiles/dmob hermes model
  HERMES_HOME=/root/.hermes/profiles/desmond hermes model
  HERMES_HOME=/root/.hermes/profiles/gentech hermes model
  ```
- [ ] Verify tokens persisted:
  ```bash
  python3 -c "import json; a=json.load(open('/root/.hermes/profiles/yoyo/auth.json')); print('OK' if 'nous_tokens' in a else 'MISSING')"
  ```
- [ ] Re-run refresh script manually and expect `{"success": true, "needs_reauth": false}`:
  ```bash
  python3 /root/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
  ```
- [ ] Test a Nous-dependent script:
  ```bash
  python3 /root/vaults/gentech/02-Labs/scripts/kite-hackathon-checks.py
  ```
  Expected exit code: 0

**If tokens still missing after two `hermes model` runs:** check disk write permissions on profile directories; check Hermes logs for provider state commit failures; consider restarting gateway before re-auth.

### Phase 2 — Restore Tool-Gateway (DMOB/YoYo)

- [ ] Check tool-gateway config directory exists:
  ```bash
  ls /root/.hermes/tool-gateway/ 2>/dev/null || ls ~/.config/hermes/tool-gateway/ 2>/dev/null
  ```
- [ ] Start tool-gateway:
  ```bash
  hermes tool-gateway start
  # or if systemd managed:
  systemctl --user start hermes-tool-gateway
  ```
- [ ] Verify process and port:
  ```bash
  ps aux | grep -i tool-gateway | grep -v grep
  netstat -tlnp | grep -E '3000|8080|5000' | grep -v grep
  ```
- [ ] Test Firecrawl access (if test script available)
- [ ] Restart all agent gateways to refresh tool connections:
  ```bash
  for agent in yoyo dmob desmond gentech; do
    HERMES_HOME=/root/.hermes/profiles/$agent hermes gateway restart
  done
  ```
- [ ] Verify error logs stop showing `Firecrawl client initialization failed` within 5 minutes

**Related cron:** Verify `Tool-Gateway Auto-Start` cron job exists and is enabled in Gentech cron.

### Phase 3 — Repair Desmond Missing Skills (Desmond)

- [ ] Search vault for missing skills:
  ```bash
  find /root/vaults/gentech -type d -name "cmc-watchlist-scraper*"
  find /root/vaults/gentech -type d -name "crypto-monitoring-cron*"
  ```
- [ ] If found, install to Desmond:
  ```bash
  hermes skill install /root/vaults/gentech/gentech-skills/cmc-watchlist-scraper
  hermes skill install /root/vaults/gentech/gentech-skills/crypto-monitoring-cron
  ```
- [ ] If not found in vault, notify vault manager (YoYo) to restore/create these skills
- [ ] Restart Desmond gateway after skill installation:
  ```bash
  HERMES_HOME=/root/.hermes/profiles/desmond hermes gateway restart
  ```
- [ ] Verify cron jobs execute on next schedule; check gateway.log for `Skill ... loaded` messages

### Phase 4 — Clear Stalled Handoffs (Jordan + All Leads)

- [ ] Review `11-Mess Hall/approvals.md` for all `⏳ Pending` items older than 6 days
- [ ] Jordan to approve or reject pending items from Apr 24–30 vault sweep
- [ ] Teams to update handoff statuses in `09-Green Room/handoff-tracker.md`
- [ ] Watchdog to verify resolution on next cycle

### Phase 5 — Cron Consolidation (YoYo)

- [ ] Consolidate 4 overlapping YoYo cron jobs per plan in `09-Green Room/cron-consolidation-d5-milestone-tracker.md`
- [ ] Decommission legacy jobs after new consolidated tracker is live and verified
- [ ] Update skill references and handoff documentation

---

## Root Cause Hypotheses

1. **OAuth refresh token lifetime exceeded** — Nous Portal refresh tokens may have shorter TTL than access tokens; automatic refresh failed due to session revocation requiring full re-auth flow
2. **Hermes provider state not persisting** — After `hermes model`, Nous OAuth tokens may not be flushed to `auth.json` due to a configuration write error or disk write permission issue
3. **Tool-gateway auto-start cron not firing** — `Tool-Gateway Auto-Start` cron job may be misconfigured or its skill missing
4. **Skill vault sync incomplete** — Desmond/YoYo skill sets out of sync with vault master copy, possibly from interrupted skill install

---

## Monitoring & Prevention

1. **Watchdog enhancement** — Add explicit OAuth health check (verify `nous_tokens` present) and tool-gateway liveness to regular health cycles
2. **Pre-cron skill resolution check** — Before each cron tick, verify all scheduled job skills exist; fail fast with alert if missing
3. **Dashboard alert** — Tag this incident type as `infrastructure-credential-cascade` and track MTTR

---

## Related Incidents

- `references/nous-portal-refresh-token-revocation-2026-05-03.md` — refresh token revocation pattern
- `references/tool-gateway-outage-pattern.md` — tool-gateway monitoring and recovery
- `references/missing-skill-cron-failures.md` — silent cron skip detection
- `references/systemic-correlation-detection.md` — fleet-wide failure pattern framework

---

## Resolution Log

_To be filled as recovery progresses:_

| Step | Action | Owner | Timestamp (UTC) | Result |
|------|--------|-------|----------------|--------|
| 1 | `hermes model` re-auth (yoyo) | DMOB | TBD | TBD |
| 2 | `hermes model` re-auth (dmob) | DMOB | TBD | TBD |
| 3 | `hermes model` re-auth (desmond) | DMOB | TBD | TBD |
| 4 | `hermes model` re-auth (gentech) | DMOB | TBD | TBD |
| 5 | Start tool-gateway | DMOB | TBD | TBD |
| 6 | Restart all agent gateways | DMOB | TBD | TBD |
| 7 | Install missing skills to Desmond | Desmond | TBD | TBD |
| 8 | Verify data-collection scripts succeed | YoYo | TBD | TBD |
| 9 | Clear overdue handoffs | Jordan | TBD | TBD |

---

**Last updated:** 2026-05-03 18:47 UTC (initial write)  
**Next review:** After Phase 1 recovery completes
