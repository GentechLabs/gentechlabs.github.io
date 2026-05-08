# 2026-05-02 Watchdog Health Check — Critical Findings

**Date**: 2026-05-02 02:19 UTC  
**Scope**: YoYo, DMOB, Desmond, Gentech agents  
**Status**: 🔴 All four agents exhibiting active failures

---

## Agent-by-Agent Failures

### YoYo & Gentech (CRITICAL)
- **Issue**: Python bytecode corruption causing `EOFError: marshal data too short`
- **Trace pattern**:
  ```
  File "/usr/local/lib/hermes-agent/agent/auxiliary_client.py", line 1902, in _to_async_client
    from agent.copilot_acp_client import CopilotACPClient
  EOFError: marshal data too short
  ```
- **Impact**: Session summarization and any LLM call failing; Telegram gateway stalled despite processes "running"
- **Affected files**: `/usr/local/lib/hermes-agent/agent/__pycache__/` and `tools/__pycache__/`
- **Confirmed corrupted**: `gemini_native_adapter.cpython-311.pyc` (16,384 bytes, modified 2026-05-01 10:17:45)
- **Required action**: Clear `.pyc` directories AND restart gateways (in-memory cache persists)
- **Verification**: `python3 -c "from agent.copilot_acp_client import CopilotACPClient; print('OK')"` succeeds without marshal error

### DMOB (HIGH)
- **Issue 1**: Invalid ElevenLabs TTS API key
  - Error: `elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}`
  - Affects all TTS functionality
- **Issue 2**: Missing Anthropic credentials
  - Error: `RuntimeError: No Anthropic credentials found`
  - Breaks "Defi Milestone" cron job (ID: `3fc1a11a88d7`)
- **Env**: `ELEVENLABS_API_KEY` present but invalid; no `ANTHROPIC_TOKEN` or `ANTHROPIC_API_KEY` in `/root/.hermes/profiles/dmob/.env`
- **Gateway history**: Disconnected and restarted on May 1 23:20:36–23:20:41

### Desmond (HIGH)
- **Issue**: Invalid ElevenLabs TTS API key (same key as DMOB)
  - 186 of 191 recent errors are TTS 401 failures
- **Gateway history**: Shutdown/restart cycle on May 1 at 23:20 matching system-wide instability
- **Env**: `ELEVENLABS_API_KEY` present but invalid

### Gentech (CRITICAL)
- Same bytecode corruption as YoYo (`EOFError: marshal data too short`)
- Gateway process stopped at 00:56 and restarted (observed in error log)
- Still failing post-restart if bytecode cache not cleared before restart

---

## Systemic Infrastructure Failures

### Cron Execution Pipeline — BROKEN
**Observation**: Four agent-specific scheduled jobs defined in global `/root/.hermes/cron/jobs.json` have **never executed** (`last_run_at: null`).

| Job ID | Name | Intended Agent | Profile in jobs.json | Last Run |
|--------|------|----------------|----------------------|----------|
| `64cfa447b338` | Desmond — Creative Sync | desmond | `None` | never |
| `c578000c1d4a` | Gentech — HQ Daily Update | gentech | `None` | never |
| `a47474bb0f0c` | YoYo — LP Watchlist Check | yoyo | `None` | never |
| `ec74c26ad123` | DMOB — Labs Daily Standup | dmob | `None` | never |

**Root cause**: Global `jobs.json` has `"profile": null` (or missing `profile` key) for all four jobs. Without a profile, the cron dispatcher never copies them into any agent's `~/cron/jobs.json`. The jobs sit idle in the global store.

**Cross-contamination**: Each agent's personal cron directory contains ~30 jobs, but many belong to other agents (e.g., "Gentech — HQ Update" appears in YoYo's cron file). This happens when the first gateway to boot claims unprofile-assigned jobs and writes them to its own cron directory. Subsequent gateways don't re-sync.

**Evidence**:
- YoYo cron file has 29 jobs including "Gentech LLC Reminder", "Gentech Watchdog", "The Brain Review" — clearly not YoYo responsibilities
- DMOB cron file has 6 jobs; none are the target "Labs Daily Standup"
- Desmond cron file has 6 jobs; none are the target "Creative Sync"
- Gentech cron file has 31 jobs including "YoYo — Crypto Watchlist" and "DMOB — Hackathon Scout" — massive cross-contamination

**Fix required**:
1. Add correct `profile` field to each global job:
   ```json
   { "id": "ec74c26ad123", "profile": "dmob", ... }
   { "id": "a47474bb0f0c", "profile": "yoyo", ... }
   { "id": "c578000c1d4a", "profile": "gentech", ... }
   { "id": "64cfa447b338", "profile": "desmond", ... }
   ```
2. Delete per-agent cron job files to force regeneration from corrected global source
3. Restart all gateways

**Cron ticker status**: Running but only dispatching jobs from per-agent cron directories; global jobs.json not being synced.

### Disk Space Pressure
- Root partition (`/dev/sda1`): 157G/193G used (**82%**)
- Impact: `SessionDB` init failures: "database or disk is full"
- Risk: Further `.pyc` corruption likely if disk fills during compilation

### Telegram Connectivity
- DMOB experiencing `Bad Gateway` errors at 2026-05-02 01:10:41
- Multiple "Mess Hall" jobs failing with `RuntimeError: Refresh session has been revoked` — stale Telegram auth tokens

---

## Verification Commands (Re-run Checklist)

```bash
# 1. Confirm all gateways running with correct profiles
ps aux | grep hermes | grep gateway

# 2. Check for residual marshal errors in last 30 lines of each errors.log
for a in yoyo dmob desmond gentech; do
  echo "=== $a ==="
  tail -30 /root/.hermes/profiles/$a/logs/errors.log | grep -i marshal || echo "No marshal errors"
done

# 3. Verify global jobs.json profile assignments
python3 -c "
import json
with open('/root/.hermes/cron/jobs.json') as f:
    jobs = json.load(f)['jobs']
for j in jobs:
    prof = j.get('profile')
    print(f\"{j['id']} | {j['name'][:45]:45s} | profile={prof} | last_run={j['last_run_at']}\")
"

# 4. Detect cross-contamination: list jobs in each agent's cron that don't match that agent
for agent in yoyo dmob desmond gentech; do
  echo \"=== $agent cron jobs mismatched ===\"
  python3 -c \"
import json, sys
with open('/root/.hermes/profiles/$agent/cron/jobs.json') as f:
    jobs = json.load(f)['jobs']
for j in jobs:
    name = j.get('name','').lower()
    if '$agent' not in name:
        print(f'  MISMATCH: {j[\"name\"][:50]}')
\" || true
done

# 5. Check disk pressure
df -h /

# 6. Test fresh bytecode import (do this AFTER any restart)
python3 -c "from agent.copilot_acp_client import CopilotACPClient; print('OK')" && echo "Bytecode clean" || echo "STILL CORRUPTED"
```

---

## Evidence Log

- **Process PIDs** (May 02 00:55 UTC): desmond=922877, dmob=922890, gentech=923094, yoyo=923106
- **Gateway command pattern**: `/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile <agent> gateway run --replace`
- **Error log paths**:
  - `/root/.hermes/profiles/yoyo/logs/errors.log` — marshal errors
  - `/root/.hermes/profiles/dmob/logs/errors.log` — ElevenLabs 401 + Anthropic missing
  - `/root/.hermes/profiles/desmond/logs/errors.log` — ElevenLabs 401
  - `/root/.hermes/profiles/gentech/logs/errors.log` — marshal errors
- **Corrupted bytecode file**: `/usr/local/lib/hermes-agent/agent/__pycache__/gemini_native_adapter.cpython-311.pyc` (16,384 bytes, 2026-05-01 10:17:45)
- **Cron directory state**:
  - `/root/.hermes/cron/jobs.json` — global store, 4 jobs, all `profile: null`
  - `/root/.hermes/profiles/*/cron/jobs.json` — per-agent stores with 29–31 jobs each, heavy misassignment
  - `/root/.hermes/cron/output/` — last output 2+ hours old for target agents
- **ElevenLabs API key** (shared across DMOB/Desmond/YoYo/Gentech): `ff52c5...6d55` — **invalid** (returning 401)
- **Anthropic credentials**: Absent from DMOB env; present in other agents

---

## Related Skill Documentation

- **Bytecode corruption**: `references/bytecode-corruption.md` (general pattern)
- **ElevenLabs 401**: `references/elevenlabs-401.md` (provider-specific fix)
- **Cron job execution**: `references/jobs-not-executing.md` (dispatcher troubleshooting)
