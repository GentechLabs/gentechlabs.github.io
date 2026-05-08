# Multi-Agent Coordinated Restart & Auth Failure Patterns
**Date:** 2026-05-02  
**Session:** cron_9ecfada01952_20260502_053044 (Watchdog health check)  
**Agents affected:** YoYo, DMOB, Desmond, Gentech  

---

## Executive Summary

All four gateways underwent coordinated stop/restart cycles within a ~12-second window on May 2, 2026 (~00:55 UTC). Concurrent authentication failures blocked cron job execution across the fleet, while infrastructure corruption (bytecode, database) caused feature-level degradation.

---

## Event Timeline (May 2, 2026 ~00:55 UTC)

| Agent | Stop Timestamp | Restart Timestamp | Gap |
|-------|----------------|-------------------|-----|
| **Desmond** | 00:55:10.622 | 00:55:14.190 | ~3.5s |
| **DMOB** | 00:55:15.687 | 00:55:18.759 | ~3.1s |
| **Gentech** | 00:55:17.431 | 00:55:22.432* | ~5.0s |
| **YoYo** | 00:56:51.682 | 00:56:55.936 | ~4.3s |

*Gentech restart delayed; no explicit start entry until 00:56:49 (process confirmed running by 00:56:55).

**Observation:** Desmond, DMOB, and Gentech stopped within a 7-second span (00:55:10 → 00:55:17), indicating a potential shared trigger (resource pressure, upstream signal, or coordinated shutdown). YoYo's later stop is temporally separated (~90s after the cluster) and may be unrelated or a secondary cascade effect.

---

## Diagnostic Approach Used

### 1. Correlation of Gateway Lifecycle Events

```bash
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent last stops ==="
  grep -E 'Gateway stopped|Exiting with code' \
    /root/.hermes/profiles/$agent/logs/gateway.log | tail -5
done
```

**Output (excerpt):**
```
DESMOND: 2026-05-02 00:55:10 ... Gateway stopped ... Exiting with code 1
DMOB:    2026-05-02 00:55:15 ... Gateway stopped ... Exiting with code 1
GENTECH: 2026-05-02 00:55:17 ... Gateway stopped ... Exiting with code 1
YOYO:    2026-05-02 00:56:51 ... Gateway stopped ... Exiting with code 1
```

All exits are `code 1` with "signal-initiated shutdown without restart request" — consistent with an external termination (SIGTERM/SIGINT) rather than internal crash. Systemd's `Restart=on-failure` then auto-restarted them.

### 2. Signal Source Hypothesis

Given the tight clustering, possible sources:
- **Manual stop command:** `hermes gateway stop --all` or `systemctl --user stop hermes-gateway-*`
- **Automated maintenance:** Brain backup script (`hermes brain backup`), update script, or custom health-loop that cycles gateways
- **System-level event:** OOM killer (unlikely; no memory pressure), cron job that restarts services

**Check performed:**
```bash
journalctl -n 500 --no-pager | grep -E 'stop hermes-gateway|gateway stop|hermes.*stop' | grep -v 'Stopping'
```
No explicit stop command found in the pre-cascade window, suggesting either:
- A script not logging to system journal (direct `pkill -f` or `killall`)
- A user shell command not captured (non-root session?)

### 3. Post-Restart Health State

Despite successful restart (gateway processes running, cron ticker active), cron job execution remained blocked due to credential failures:
- **YoYo:** 144 cron failures (Nous Portal auth expired + ElevenLabs 401)
- **DMOB:** 5 cron failures (missing Anthropic key + ElevenLabs 401)
- **Desmond:** 7 cron failures (ElevenLabs 401 + OpenAI 404)
- **Gentech:** 45+ session summarization failures (marshal bytecode corruption)

**Key insight:** Gateway uptime does not imply operational health.Credential/auth failures can paralyze the cron executor even while the process runs.

---

## Authentication Failure Combinations (Per Agent)

| Agent | Provider | Failure Pattern | Error Message |
|-------|----------|----------------|---------------|
| **YoYo** | Nous Portal | Auth expired | `RuntimeError: Hermes is not logged into Nous Portal` |
| | ElevenLabs TTS | API key invalid | `elevenlabs.core.api_error.ApiError: status_code: 401` |
| | | | |
| **DMOB** | Anthropic | Missing API key | `RuntimeError: No Anthropic credentials found` |
| | ElevenLabs TTS | API key invalid | `status_code: 401` (463 occurrences) |
| | OpenAI | 404 Not Found | `openai.NotFoundError: "Couldn't find that"` |
| | | | |
| **Desmond** | ElevenLabs TTS | API key invalid | `status_code: 401` (279+ occurrences) |
| | OpenAI | 404 Not Found | Vision tool: `Error code: 404` |
| | | | |
| **Gentech** | — | Bytecode corruption | `EOFError: marshal data too short` (3 in last 50 lines) |
| | — | Session DB corruption | `sqlite3.OperationalError: database disk image is malformed` |

**Note:** No auth failures detected for Gentech in the most recent log slice, suggesting its degradation is infrastructure-only (bytecode/database) vs credential-based.

---

## Error Volume & Health Correlation

Quick health metric from this session:

| Agent | errors.log size | Error lines | Recent error rate (last 30) | Credential issues detected? |
|-------|----------------|-------------|----------------------------|----------------------------|
| YoYo   | 601,676 bytes | 6,574       | High (cron + auth)          | Yes (Nous + ElevenLabs)    |
| DMOB   | 159,835 bytes | 1,790       | Medium (Anthropic + TTS)    | Yes (Anthropic + ElevenLabs) |
| Desmond| 141,453 bytes | 1,571       | Medium (TTS + OpenAI 404)  | Yes (ElevenLabs + OpenAI)  |
| Gentech| 215,365 bytes | 3,073       | Medium (marshal + DB)       | No (infrastructure only)   |

**Takeaway:** Error volume alone is not a reliable health indicator; skillfully filter for *blocking* patterns (auth failures, bytecode corruption) rather than raw count.

---

## Recovery Actions Required (Outstanding)

1. **YoYo:**
   - Re-authenticate Nous Portal via `hermes model`
   - Refresh ElevenLabs API key in profile `.env`
   - Clear `.pyc` corruption if recurring (checked 30 files; no immediate corruption but monitor)

2. **DMOB:**
   - Set `ANTHROPIC_TOKEN` in profile config or `.env`
   - Refresh ElevenLabs API key
   - Investigate Telegram "Bad Gateway" transient (likely upstream; monitor)

3. **Desmond:**
   - Refresh ElevenLabs API key (shared with DMOB likely)
   - Verify OpenAI vision model access / correct model ID (404 error)

4. **Gentech:**
   - Monitor `marshal data too short` trend (3 occurrences in last 50 lines)
   - Investigate root cause of database corruption earlier (now passing integrity_check)

5. **Infrastructure:**
   - Determine initiator of coordinated stop at 00:55 UTC (check shell history, automated scripts)
   - Document and, if non-critical, disable any automated cycling that doesn't coordinate with agent state

---

## Methodological Lesson: Avoid Transcript-Only False Negatives

**Initial health check passes** (early cron runs) incorrectly returned `STATUS:OK` because `session_search` queried transcripts but found no matching error sessions. In reality, agents were degraded but not generating *transcribed* error sessions (the failures were in `errors.log`, not user-facing conversation transcripts).

**Corrective procedure:**
- Always perform **direct log inspection** (`errors.log`, `gateway.log`) regardless of transcript search results.
- Transcript search is useful for historical patterns but insufficient for real-time health.
- Combine three signals: (1) process existence, (2) log recency/error patterns, (3) cron job state via `hermes cron list`.

---

## Quick Diagnostic Commands (Derived from This Session)

```bash
# 1. Get gateway stop/start timeline for correlation
for a in gentech yoyo dmob desmond; do
  echo "=== $agent ==="
  grep -E 'Gateway stopped|Exiting with code|Cron ticker started' \
    /root/.hermes/profiles/$a/logs/gateway.log | tail -8
done

# 2. Count credential-related failures per agent
for a in gentech yoyo dmob desmond; do
  c1=$(grep -c 'Nous Portal' /root/.hermes/profiles/$a/logs/errors.log 2>/dev/null || echo 0)
  c2=$(grep -c 'No Anthropic' /root/.hermes/profiles/$a/logs/errors.log 2>/dev/null || echo 0)
  c3=$(grep -c 'elevenlabs.*401' /root/.hermes/profiles/$a/logs/errors.log 2>/dev/null || echo 0)
  echo "$a: nous=$c1 anthropic=$c2 elevenlabs_401=$c3"
done

# 3. Verify agents are still running after cascade
ps aux | grep 'hermes_cli.main --profile' | grep -v grep

# 4. Check cron job state (scheduled vs active)
hermes cron list | grep -E 'yoyo|dmob|desmond|gentech'

# 5. Database integrity (should be added to standard checklist)
python3 -c "import sqlite3; print('state.db:', sqlite3.connect('/root/.hermes/state.db').execute('PRAGMA integrity_check').fetchone()[0])"
```

---

## Related

- See `gentech-agent-health-diagnosis` skill main document for full diagnostic phases.
- `references/2026-05-02-cron-executor-stall-pattern.md` for cron subsystem paralysis recovery.
- `references/2026-05-02-bytecode-corruption-yoyo-gentech.md` for marshal error deep-dive.
