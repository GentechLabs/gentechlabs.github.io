# May 04, 2026 — Evening Watchdog: Auth Revocation + API Key Block Cascade

**Session**: `cron_9ecfada01952_20260504_213058` (May 04, 2026 ~21:30 UTC)
**Watchdog**: Gentech (CEO/Lead)
**Agents audited**: YoYo, DMOB, Desmond, Gentech

---

## Executive Summary

All four agents have **running gateway processes**, but **15 of 29 scheduled cron jobs failed** in the last 24 hours due to two compound LLM provider failures:

1. **Nous Portal OAuth refresh session revoked** — Affects all agents using `nousresearch/trinity-large-thinking`
2. **StepFun/Trinity API key invalid or out of funds** (HTTP 401) — Blocks all jobs that depend on this model provider

**Additional issues**:
- Telegram delivery failures: `Chat not found` on Pre-Shift job
- Gateway log staleness: Some agents show no log updates for >2 hours despite running processes
- Systemic: No LLM API calls can succeed until both auth and billing issues are resolved

**Bottom line**: Agents are alive but **completely non-functional** for any LLM-dependent work. This is a higher-severity state than "alive but degraded" — it's "alive but blocked" at the provider layer.

---

## Findings per Agent

### YoYo
- **Process**: Running (PID 882, uptime ~2h), responding to Telegram
- **Gateway log**: Last update 2026-05-04 17:38:16 (stale)
- **Errors**: `Refresh session has been revoked` (Nous OAuth)
- **Cron jobs affected**: All jobs failing (Agent Check-in, Daily Rotation, Pre/Post-Shift, Mid-Shift, Breaks, etc.)
- **Status**: CRITICAL

### DMOB
- **Process**: Running (PID 872), responding to Telegram
- **Gateway log**: Last update 2026-05-04 17:38:15 (stale)
- **Errors**: OAuth revocation cascade; HTTP 401 from provider
- **Status**: CRITICAL

### Desmond
- **Process**: Running (PID 865), responding to Telegram
- **Gateway log**: Last update 2026-05-04 17:38:16 (stale)
- **Errors**: OAuth revocation cascade
- **Status**: CRITICAL

### Gentech
- **Process**: Running (PID 880), responding to Telegram
- **Gateway log**: Last update 2026-05-04 17:38:15 (stale)
- **Errors**: OAuth revocation cascade; HTTP 401 from provider
- **Status**: CRITICAL

---

## Root Cause Analysis

### Primary: Nous Portal OAuth Refresh Session Revoked
```
RuntimeError: Refresh session has been revoked
Run `hermes model` to re-authenticate.
```
- Affects all agents using `nousresearch/trinity-large-thinking`
- OAuth refresh token invalidated (manual revocation, policy expiry, or provider rotation)
- All Hermes API calls to Nous Portal return 401
- Blocks every cron job that needs LLM inference

### Secondary: StepFun/Trinity API Key Invalid or Out of Funds
```
RuntimeError: Error code: 401 - {'status': 401, 'message': 'Your API key is invalid, blocked or out of funds.'}
```
- Two meanings:
  1. **Invalid key** — key wrong/rotated
  2. **Out of funds** — valid key but zero credits
- This is **distinct** from OAuth revocation — separate provider
- If primary model provider returns 401, all jobs fail

### Impact: 15 of 29 Cron Jobs Failed
- Mess Hall shift schedule (8 jobs)
- LLM sync/digest jobs (3 jobs)
- Research/monitor jobs (4+ jobs)

---

## New Diagnostic Patterns

### Gateway Log Staleness as Blocked-Agent Indicator

When agents are blocked on provider I/O (auth failure, quota block, network hang), they stop logging even though processes remain running.

**Detection**:
```bash
# Check log modification age
age=$(( $(date +%s) - $(stat -c %Y /root/.hermes/profiles/<agent>/logs/gateway.log) ))
if [ $age -gt 1800 ]; then echo "STALE: ${age}s"; fi

# Check last log entry timestamp
tail -1 /root/.hermes/profiles/<agent>/logs/gateway.log
```

If `(now - last_entry) > 300s` **AND** process appears running → agent is **blocked on provider I/O**, not crashed.

---

### API Key Invalid vs Out of Funds vs OAuth Revoked

| Error | Type | Fix |
|---|---|---|
| `Refresh session has been revoked` | OAuth | `hermes model` re-authenticate |
| `Your API key is invalid, blocked or out of funds` | API Key | Read body: `quota_exceeded` → top up; `invalid_api_key` → rotate |
| `No provider credentials` | Missing Env | Add key to `.env`, restart |

**Do NOT restart gateways hoping auth fixes itself** — these require manual credential/billing action.

---

### Telegram "Chat not found" — Delivery Misconfiguration

**Error**: `delivery error: Telegram send failed: Chat not found`

**Cause**: Bot not in target group, wrong chat ID, or chat restrictions.

**Fix**: Verify bot membership; update `TELEGRAM_ALLOWED_USERS` or job `deliver` field with correct numeric ID.

---

## Evidence

**All 4 agents show identical stale gateway log cutoff**:
```
2026-05-04 17:38:15,639 INFO gateway.run: Agent cache idle sweep: evicted 1 agent(s)
```
No further log entries — processes alive but not progressing.

**Cron failure cluster (15 jobs)**:
All errors occurred within a 24h window; pattern clearly shows auth vs API-key failure variants.

**Transient agent failure burst** (same second across fleet):
```
2026-05-04 16:37:39,084 INFO gateway.run: Transient agent failure in session 20260504_130216_ee1b54b8 — persisting user message...
```
→ Coordinated restart event + slow recovery due to provider blockade.

---

## Recovery Order

1. `hermes model` per agent (OAuth re-auth)
2. StepFun API key: check error body, rotate or top up, update `.env`
3. Restart all gateways
4. Fix Telegram Chat not found
5. Validate: `hermes cron list` shows `ok` on all jobs

---

## Follow-ups

- Check `auth.json` expiry timestamps per agent after re-auth
- Enable proactive OAuth refresh monitoring
- Add billing alerts on provider portals
- Update this skill's main SKILL.md with "gateway log staleness as blockage indicator" pattern