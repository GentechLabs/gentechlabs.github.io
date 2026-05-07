# Session Reference — Gentech Enterprise Agent Health Check
**Date:** 2026-05-02
**Context:** Scheduled watchdog cron job; early shift (03:00 UTC)
**Agents checked:** YoYo, DMOB, Desmond, Gentech

---

## Critical Findings

### Cron Staleness Thresholds
| Agent | Last Run | Hours Ago | Status |
|-------|----------|-----------|--------|
| DMOB | 2026-04-24 11:10 | **193** | 🔴 CRITICAL |
| Gentech | 2026-04-24 11:37 | **193** | 🔴 CRITICAL |
| Desmond | 2026-04-30 08:20 | **52** | 🔴 STALE |
| YoYo | 2026-05-02 09:00 | **51** | 🔴 STALE |

**Threshold used:** 24h without cron execution = stale alarm

### Authentication Failures (from `/tmp/cron_health.txt`)
```
RuntimeError: Refresh session has been revoked
  → Affected: DMOB (2026-04-22, 2026-04-24), Gentech (2026-04-22×2), Desmond (2026-04-22)
  → Resolution: `hermes model` re-authentication required

RuntimeError: No Anthropic credentials found
  → Affected: DMOB only
  → Resolution: Set ANTHROPIC_TOKEN or `claude /login`
```

### Service Errors (syslog, last hour)
```
elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
  → Occurrences: 3 (Desmond, Gentech, YoYo gateways)
  → Root cause: Expired/invalid ElevenLabs API key in agent environment
```

### Error Log Accumulation
- `/tmp/dr_errors.txt` — 160,751 bytes, 173 error-indicating lines
- `/tmp/th_errors.txt` — 164,308 bytes, 183 error-indicating lines
- Dominant exception: `RuntimeError: Event loop is closed` (benign asyncio cleanup noise)
- Real failures prefixed with `error:` or `ApiError`

---

## Proven Commands (Copy-Paste Verified)

### Agent Cron Status One-Liner
```bash
for agent in desmond dmob gentech yoyo; do
  echo "=== $agent ==="
  grep -i "Last run:" /tmp/${agent}_cron.txt 2>/dev/null | tail -1 || echo "NO CRON FILE"
done
```

### Gateway Process Liveness
```bash
ps aux | grep hermes_cli.main | grep -E '(desmond|dmob|gentech|yoyo).*gateway' | \
  awk '{print $1, $2, $3"%"CPU, $4"%"MEM, $11}'
```

### Recent Syslog Error Scan (last 30 min)
```bash
tail -200 /var/log/syslog | grep -iE '(error|exception|failed|api_error)' | grep -v "Event loop is closed"
```

### High-CPU Sandbox Detection
```bash
ps aux | awk '$3 > 60 && /python.*script.py/ {print $0}'
```

### Error Log Size Check
```bash
for log in /tmp/dr_errors.txt /tmp/th_errors.txt; do
  [ -f "$log" ] && echo "$(ls -lh "$log" | awk '{print $5}') $log"
done
```

---

## Cron File Format Reference

Each agent maintains a Hermes-managed cron transcript at `/tmp/<agent>_cron.txt`. Content pattern:

```
Job e00b46103b08 [active]
  Name:      YoYo — DeFi Milestone + LP Monitor
  Schedule:  10 14 * * *
  Repeat:    ∞
  Next run:  2026-04-30T14:10:00+00:00
  Deliver:   origin
  Skills:    crypto-lp-monitoring
  Last run:  2026-04-30T09:00:31.681521+00:00  ok
```

Key fields:
- `Last run:` — ISO8601 timestamp + `ok` or `error: MESSAGE`
- `Next run:` — scheduled next execution
- `Deliver:` — output destination (`origin`, `telegram:CHAN`, etc.)

**File mtime vs Last run:** File modification time should be close to the `Last run` timestamp. If file mtime is much older than the last run entry, the cron is not writing fresh output (stale/locked).

---

## Error Message Catalog

| Error String | Severity | Likely Cause | Recovery |
|--------------|----------|--------------|----------|
| `Refresh session has been revoked` | 🔴 Critical | OAuth token expired or revoked | `hermes model` re-login |
| `No Anthropic credentials found` | 🔴 Critical | Missing ANTHROPIC_TOKEN env var | `claude /login` or set token |
| `Agent completed but produced empty response` | 🟡 Degraded | Model timeout, misconfiguration, or empty skill output | Check model quota, retry, review skill logic |
| `Event loop is closed` | 🟢 Noise | Asyncio cleanup on process exit | **Ignore** (non-blocking) |
| `elevenlabs ... 401 Invalid API key` | 🔴 Critical | TTS API key invalid/expired | Update ElevenLabs key in agent env |
| `ApiError: status_code: 429` | 🟡 Rate limit | External API rate limit exceeded | Backoff, check quota |

---

## Agent State Matrix Template

Use this markdown table for daily health snapshots in `11-Mess Hall/`:

```markdown
# Agent Health Snapshot — 2026-05-02

| Agent | Cron Status | Gateway | Auth | Last Error | Hours Ago | Action |
|-------|-------------|---------|------|------------|-----------|--------|
| YoYo | 🔴 STALE (51h) | 🟢 RUNNING | 🔴 FAILED | TTS 401 | 51 | Update ElevenLabs key + re-auth |
| DMOB | 🔴 STALE (193h) | 🟢 RUNNING | 🔴 FAILED | Session revoked | 193 | `hermes model` re-login |
| Desmond | 🔴 STALE (52h) | 🟢 RUNNING | 🟢 OK | TTS 401 | 52 | Update ElevenLabs key |
| Gentech | 🔴 STALE (193h) | 🟢 RUNNING | 🔴 FAILED | Session revoked | 193 | `hermes model` re-login |

**Summary:** All agents cron-dead. Priority: DMOB/Gentech auth recovery (193h stale), then TTS key rotation.
```

---

## Gateway Process Expectations

| Agent | Expected CMD Pattern | Typical RSS | CPU (idle) |
|-------|---------------------|-------------|------------|
| Desmond | `.../python -m hermes_cli.main --profile desmond gateway run --replace` | ~716k | 0.4% |
| DMOB | `.../python -m hermes_cli.main --profile dmob gateway run --replace` | ~701k | 0.4% |
| Gentech | `.../python -m hermes_cli.main --profile gentech gateway run --replace` | ~875k | 0.7% |
| YoYo | `.../python -m hermes_cli.main --profile yoyo gateway run --replace` | ~888k | 1.1% |

If RSS drifts >200 MB from baseline OR CPU% >5% at idle → investigate memory leak or stuck task.

---

## Mess Hall Reporting Template

```markdown
# 🚨 Agent Health Alert — <DATE>

**Check:** Enterprise agent cron + gateway health
**Scope:** YoYo, DMOB, Desmond, Gentech

## Findings

- [x] Cron staleness checked
- [x] Gateway processes verified
- [x] Error log accumulation reviewed
- [x] Service failures identified

## Status Table

| Agent | Cron | Gateway | Auth | Action Required |
|-------|------|---------|------|-----------------|
| ... | ... | ... | ... | ... |

## Immediate Actions

1. **P0:** <highest priority fix>
2. **P1:** <secondary fix>
3. **P2:** <monitoring/cleanup>

## Escalation

- If gateway down → `gentech-agent-reactivation`
- If auth revoked → `gentech-agent-reactivation` + `hermes model`
- If cron not reinstalling → Green Room handoff to DMOB
```

---

## Recurrence & Watch Schedule

- **Business hours** (09:00–17:00 UTC): check every 4 hours
- **Weekends/holidays**: check once daily (12:00 UTC)
- **Post-deployment window**: check at +1h and +3h after any agent gateway restart or credential rotation

Log each check to `11-Mess Hall/agent-health/YYYY-MM-DD-HH-health-check.md` with outcome and any new anomalies.