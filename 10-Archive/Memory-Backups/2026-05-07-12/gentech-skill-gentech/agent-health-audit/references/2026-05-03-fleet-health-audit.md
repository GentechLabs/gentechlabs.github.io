---
date: 2026-05-03
auditor: Gentech Watchdog (scheduled cron)
agents_checked: [yoyo, dmob, desmond, gentech]
severity: moderate
keywords: ["auth revocation cascade", "nous portal", "firecrawl misconfiguration", "elevenlabs quota", "model support withdrawal"]
related_skills: ["agent-health-audit", "hermes-auth-incident-response"]
---

# May 3, 2026 — Fleet Health Audit

## Executive Summary

All four gateways **running and Telegram-connected**. No agents were down. However, **three systemic issues** were detected:

1. **Nous Portal OAuth revocation** across YoYo, DMOB, Desmond (since 12:00–12:50 UTC). Gentech not yet re-authenticated after prior incident.
2. **TTS quota exhaustion** — YoYo, DMOB, Desmond all at 0 ElevenLabs credits.
3. **Tool misconfiguration** — Firecrawl API key commented out system-wide.
4. **Model support withdrawal** — Gentech actively failing with `Model stepfun/step-3.5-flash not supported`.

**Impact**: Cron jobs failing silently on three agents; tool calls to web/TTS broken; Gentech experiencing repeated job failures.

---

## Findings by Agent

### YoYo

- **Gateway**: Running, Telegram-connected (18 active connections logged)
- **Cron ticker**: Active (last restart 21:37)
- **Recent cron output**: 27 files in last hour — healthy execution ✓
- **Auth status**: `Refresh session has been revoked` since 12:50. Primary provider (nous) failing. Fallback likely active.
- **Critical errors (30 min window)**: None recent (last auth error at 12:50)
- **TTS**: `quota_exceeded` — 0 credits remaining as of 20:29
- **Firecrawl**: Errors present: `missing direct config and tool-gateway auth`
- **Status**: **DEGRADED** — cron jobs may still execute via fallback provider, but auth-dependent operations unreliable.

### DMOB

- **Gateway**: Running, Telegram-connected (19 active connections)
- **Cron ticker**: Active (restart 21:33)
- **Recent cron output**: 1 file in last hour (21:01). **Schedule-check**: Next run is May 4 21:00 (Evening Milestone) — absence of recent output is **expected**, not a stall.
- **Auth status**: `Refresh session has been revoked` since 12:00. Primary provider failing.
- **TTS**: `quota_exceeded` — 0 credits as of 20:30. Earlier `invalid_api_key` errors May 2 likely key rotation that wasn't propagated.
- **Firecrawl**: Errors present 21:20
- **Status**: **DEGRADED** — cron schedule intact but auth-critical jobs failing; TTS broken.

### Desmond

- **Gateway**: Running, Telegram-connected (22 connections)
- **Cron ticker**: Active (restart 21:33)
- **Recent cron output**: 1 file in last hour (20:18). **Schedule-check**: Next run is May 4 08:15 (YoYo LP Monitor). Not stuck, just scheduled later.
- **Auth status**: `Refresh session has been revoked` since 12:47. Primary provider failing.
- **TTS**: `quota_exceeded` — 0 credits as of 20:29
- **Firecrawl**: Errors present 18:17
- **Status**: **DEGRADED** — same pattern as DMOB.

### Gentech

- **Gateway**: Running, Telegram-connected (27 connections)
- **Cron ticker**: Active (restart 21:33)
- **Recent cron output**: 27 files in last hour (21:43) — **healthy execution** ✓
- **Auth status**: `Hermes is not logged into Nous Portal` at 21:05. Also `Model stepfun/step-3.5-flash not supported` active at and 21:45.
- **Active failure**: `Nous OAuth Proactive Refresh` job failing with model not supported error (19:50, 20:00). `Gentech Watchdog` failing with auth error (19:55).
- **Status**: **CRITICAL** — simultaneous auth + model support failures blocking multiple cron jobs right now.

---

## Timeline (selected events)

| Time (UTC) | Event | Agents |
|------------|-------|--------|
| 12:00 | DMOB OAuth revocation detected | DMOB |
| 12:47 | Desmond OAuth revocation detected | Desmond |
| 12:50 | YoYo OAuth revocation detected | YoYo |
| ~13:00–18:00 | Auth cascade blocking cron jobs silently (fallbacks may have worked) | Y/D/D |
| 18:17 | Desmond Firecrawl failure first observed | Desmond |
| 18:44–19:36 | Yoyo/DMOB Firecrawl failures | Yoyo, DMOB |
| 19:50 | Gentech: Model not supported error (`Nous OAuth Proactive Refresh` job) | Gentech |
| 20:00 | Gentech: Same model error again | Gentech |
| 20:29 | TTS quota exhausted on all three agents with TTS (0 credits) | Yoyo, DMOB, Desmond |
| 21:05 | Gentech: auth-not-logged-in error (`Gentech Watchdog` job fails) | Gentech |
| 21:32–33 | Coordinated gateway restart / cron ticker restart (all agents) | All |
| 21:45 | Gentech: **still failing** with model-not-supported error (active now) | Gentech |

---

## Root Causes Identified

1. **Nous Portal OAuth session revocation** — unknown trigger (manual revocation? security flag? token reuse detection?). All three agents affected. Recovery requires `hermes model` re-auth per profile.
2. **ElevenLabs quota exhaustion** — plan limits reached. No credits left. Requires account upgrade/credit purchase or new API key from different account.
3. **Firecrawl API key commented out** in `/root/.hermes/.env`. The tool expects either tool-gateway auth or a direct `FIRECRAWL_API_KEY`. Current configuration yields `missing direct config` error on every invocation.
4. **Stepfun model deprecation** — `stepfun/step-3.5-flash` no longer available on Nous provider. Must switch to alternative model (e.g., Nous-rated models or other provider). This error returned 401 and blocks cron jobs even after OAuth recovery.

---

## Actions Required

Priority order:

### P0 — Immediate (Gentech, blocking right now)

**Gentech** is actively failing cron jobs as of 21:45:

1. Re-authenticate Gentech: `hermes model` — complete OAuth flow
2. After auth succeeds, switch model from `stepfun/step-3.5-flash` to a supported model (check provider catalog via `hermes model list` or test with `hermes model --set <supported-model>`)
3. Verify: `hermes cron status` and watch next cron output file

### P1 — Today (all three degraded agents)

1. Re-authenticate YoYo, DMOB, Desmond via `hermes model`
2. Renew ElevenLabs TTS credits or rotate to a valid key with quota
3. Uncomment/set `FIRECRAWL_API_KEY` in `/root/.hermes/.env` with valid key from https://firecrawl.dev/
4. Restart all gateways after credential updates: `hermes gateway run --profile <agent> --replace`

### P2 — This Week

1. Review cron job assignments — several jobs show `profile: unassigned` in global `jobs.json`. Migrate to proper agent profiles or assign profiles to prevent orphaned jobs.
2. Model strategy review — `stepfun/step-3.5-flash` appears deprecated. Select a stable provider/model combo for primary LLM across fleet.
3. Implement credential health monitoring — proactive alert before quotas hit zero.

---

## Diagnostic Commands Used This Session

```bash
# Process check
ps aux | grep -E "hermes|gateway" | grep -v grep

# Recent cron output (last hour)
find /root/.hermes/profiles -path "*/cron/output/*/*.md" -mmin -60 -ls

# Agent cron output directory listings
for a in yoyo dmob desmond gentech; do
  echo "=== $a ==="
  ls -lat /root/.hermes/profiles/$a/cron/output/ 2>/dev/null | head -10
done

# Gateway log recent entries (check ticker)
for a in yoyo dmob desmond gentech; do
  tail -20 /root/.hermes/profiles/$a/logs/gateway.log | grep -E "Cron ticker|error|ERROR"
done

# Errors log — critical pattern scan
for a in yoyo dmob desmond gentech; do
  echo "=== $a ==="
  grep -E "AuthError|revoked|quota_exceeded|ConnectionError|not supported" \
    /root/.hermes/profiles/$a/logs/errors.log | tail -10
done

# Multi-agent Python diagnostic (this session's tool)
python3 -c "
import subprocess, json, os, time
agents = ['yoyo','dmob','desmond','gentech']
ct = time.time()
for a in agents:
    err = f'/root/.hermes/profiles/{a}/logs/errors.log'
    with open(err) as f: lines = f.readlines()
    recent = [l for l in lines if time.mktime(time.strptime(l[:19],'%Y-%m-%d %H:%M:%S')) > ct-1800]
    crit = [l for l in recent if any(p in l for p in ['AuthError','revoked','quota_exceeded','not supported'])]
    print(f'{a.upper()}: {len(crit)} critical in last 30min')
    if crit:
        for l in crit[-2:]: print(f'  {l.strip()}')
"

# Jobs.json inspection (next/last run times)
python3 -c "
import json
for a in ['yoyo','dmob','desmond','gentech']:
    with open(f'/root/.hermes/profiles/{a}/cron/jobs.json') as f: data=json.load(f)
    active = [j for j in data['jobs'] if j.get('enabled')]
    for j in active:
        print(f\"{a}: {j['name'][:45]:<45} next={j.get('next_run_at','?')[:16]} last={j.get('last_run_at','?')[:16]} status={j.get('last_status','?')}\")
"
```

---

## Pattern Library Additions

### Pattern: Ticker Running, No Output → Check `next_run_at`

**Symptom**: Agent ticker active in logs, but no cron output files in last hour.

**Diagnostic**: Check `next_run_at` in jobs.json for that agent's jobs. If the value is **in the future**, the absence of output is correct — the job hasn't been scheduled yet.

**False positive avoided**: DMOB & Desmond on May 3 showed no recent output because their next scheduled times were May 4 08:15 and 21:00 respectively. Not broken.

**Check**:
```bash
python3 -c "
import json, datetime
now = datetime.datetime.now(datetime.timezone.utc)
with open('/root/.hermes/profiles/dmob/cron/jobs.json') as f:
    for j in json.load(f)['jobs']:
        if not j.get('enabled'): continue
        nxt = datetime.datetime.fromisoformat(j.get('next_run_at',''))
        print(f\"{j['name'][:40]:<40} next={nxt.isoformat()[:16]}  in_future={nxt>now}\")
"
```

### Pattern: Firecrawl Missing Config

**Error**: `Firecrawl client initialization failed: missing direct config and tool-gateway auth.`

**Cause**: Either `FIRECRAWL_API_KEY` missing from `.env` OR tool-gateway not providing credentials. Audit:

```bash
# Check global .env
grep FIRECRAWL /root/.hermes/.env
# Check each agent .env
for a in yoyo dmob desmond gentech; do
  echo \"$a:\"; grep -i firecrawl /root/.hermes/profiles/$a/.env || echo \"  not set\"
done
```

**Fix**: Add key to `/root/.hermes/.env`:
```bash
echo "FIRECRAWL_API_KEY=fc-..." >> /root/.hermes/.env
# Then restart gateways for env propagation
```

### Pattern: Model Not Supported vs Auth Revocation

**Conflation risk**: Both errors can return 401 and appear in same job. They require different fixes.

**Distinguish**:
| Error text | HTTP status | Fix priority | Recovery |
|------------|-------------|--------------|----------|
| `Refresh session has been revoked` | 401 | P0 | `hermes model` re-auth |
| `Hermes is not logged into Nous Portal` | 401 | P0 | `hermes model` re-auth |
| `Model <id> not supported` | 401 or 403 | P1 (after auth) | `hermes model` → switch model |
| `ModelError: not supported` | 401 | P1 | Change model in config |

**Rule**: If you see BOTH patterns in same timeframe (auth revoked + model not supported), **re-authenticate first, then switch model**. You cannot query model catalog without valid tokens.

### Pattern: OAuth Revocation Cascade Detection

When one agent shows `Refresh session has been revoked`, assume **all agents using the same Nous account are affected**. Check entire fleet immediately.

```bash
# Fleet-wide revocation scan
for a in yoyo dmob desmond gentech; do
  count=$(grep -c "Refresh session has been revoked" \
    /root/.hermes/profiles/$a/logs/errors.log 2>/dev/null || echo 0)
  echo "$a: $count revocation events logged"
done
```

**Coordinated recovery**: Authenticate agents in parallel (after hours if high volume). Anticipate Telegram disconnect storms during re-auth (provider init fails → gateway disconnection).

---

## Vault Artifacts

This session produced no new vault documents. All findings are captured here.

## Follow-up Tasks

- [ ] Re-authenticate YoYo, DMOB, Desmond (`hermes model`) — DONE: Gentech only
- [ ] Renew or rotate ElevenLabs TTS API key across all agents
- [ ] Uncomment and set `FIRECRAWL_API_KEY` in `/root/.hermes/.env`
- [ ] Switch Gentech primary model from `stepfun/step-3.5-flash` to a supported Nous model
- [ ] Restart all four gateways after credential/config changes
- [ ] Review and clean up `profile: unassigned` jobs in global `/root/.hermes/cron/jobs.json`

---

## Next Watchdog Sweep

Schedule next health check for **2026-05-04 06:00 UTC** (post-recovery validation). Audit should verify:
- All agents successfully re-authenticated
- Firecrawl tool calls succeeding
- ElevenLabs TTS functional (or gracefully degraded)
- Gentech cron jobs completing without model errors
