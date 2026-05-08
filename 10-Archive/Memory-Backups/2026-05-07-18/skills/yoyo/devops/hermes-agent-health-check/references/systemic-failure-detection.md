# Systemic Failure Detection — Advanced Diagnostics

**Purpose**: Detect infrastructure-level corruption and systemic degradation across the Hermes agent fleet. Use when basic health checks pass but agents remain degraded, or when coordinated failures are suspected.

## 1. Python Bytecode Corruption Detection

### Symptoms
- `EOFError: marshal data too short` during module import
- Session summarization failures across multiple agents simultaneously
- Errors appear in `copilot_acp_client.py`, `gemini_native_adapter.py`, or other core modules

### Diagnosis
```bash
# 1. Check .pyc file sizes vs source files
SOURCE_SIZE=$(wc -c < /usr/local/lib/hermes-agent/agent/gemini_native_adapter.py)
PYC_SIZE=$(wc -c < /usr/local/lib/hermes-agent/agent/__pycache__/gemini_native_adapter.cpython-311.pyc)
echo "Source: $SOURCE_SIZE bytes, PYC: $PYC_SIZE bytes"

# 2. Find suspiciously small .pyc files (typical .pyc > 5KB; < 2KB likely corrupt)
find /usr/local/lib/hermes-agent -name '*.pyc' -size -2k

# 3. Verify Python magic number (first 4 bytes should match Python version)
# Python 3.11 magic: 0x33 0x0d 0x0d 0x0a (330d0d0a)
xxd -l 4 /usr/local/lib/hermes-agent/agent/__pycache__/gemini_native_adapter.cpython-311.pyc
# Expected output: 00000000: 330d 0d0a   (Python 3.11)
# Corruption shows: a70d 0d0a   (Python 3.9 magic) or truncated file
```

### Root Causes
- Interrupted `hermes update` or concurrent import during bytecode compilation
- Disk I/O errors during .pyc write (check dmesg for I/O errors)
- Filesystem corruption or full disk conditions

### Remediation
```bash
# Stop all agents first
find /usr/local/lib/hermes-agent -name '__pycache__' -type d -exec rm -rf {} +
# or more targeted:
find /usr/local/lib/hermes-agent/agent/__pycache__ -name '*.pyc' -delete
# Restart all gateways to regenerate clean bytecode
```

---

## 2. Cron Database Integrity Verification

### Global vs Local Cron Databases
- **Global DB**: `/root/.hermes/cron/jobs.db` (SQLite) — single source of truth for cron daemon
- **Local DBs**: `/root/.hermes/profiles/<agent>/cron/jobs.json` — per-agent fallback/state copy

### Corruption Signs
```bash
# Check global database health
ls -la /root/.hermes/cron/jobs.db
# Size 0 bytes → CORRUPTED (empty file)

# Verify SQLite integrity
sqlite3 /root/.hermes/cron/jobs.db "PRAGMA integrity_check;"
# Returns "ok" or error message

# Check WAL/SHM companion files
ls -la /root/.hermes/cron/jobs.db-*  # should not exist in normal operation
```

### Cron Executor Deadlock Detection
**Pattern**: Ticker alive but zero job dispatches system-wide for >2 hours.

**Diagnostic Commands**:
```bash
# 1. Check if cron daemon process exists
ps aux | grep hermes | grep cron
# Should see: python -m hermes_cli.cron

# 2. Verify database file is non-empty and writable
stat -c %s /root/.hermes/cron/jobs.db  # expect > 4096 bytes
touch /root/.hermes/cron/jobs.db       # test write permission (no error)

# 3. Look for executor thread pool exhaustion in logs
grep -i "cron executor\|tick lock\|dispatcher" /root/.hermes/logs/*.log
# Look for: "tick lock held" + "skipping dispatch" messages

# 4. Cross-check agent logs — absence of 'cron.scheduler: Running job' for >2 schedule intervals
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  grep "cron.scheduler: Running job" /root/.hermes/profiles/$agent/logs/agent.log | tail -5
done
```

**Remediation**: Simultaneous gateway restart of ALL agents to reset thread pools. Single-agent restart insufficient.

---

## 3. Coordinated Gateway Restart Correlation

### Detection Pattern
All four agents (YoYo, DMOB, Desmond, Gentech) stop and restart within seconds of each other, indicating a shared dependency failure or system-level event.

**Investigation**:
```bash
# Extract stop/start events from gateway logs across agents
for agent in yoyo dmob desmond gentech; do
  echo "=== $agent ==="
  grep -E "Gateway (stopped|exited|failed|restarted)" /root/.hermes/profiles/$agent/logs/gateway.log \
    | tail -20
done

# Align timestamps and look for common triggers:
# - Resource pressure: OOM killer (check dmesg | grep -i kill)
# - Disk pressure: ENOSPC errors preceding crash
# - Network outage: Telegram API connection failures
# - Shared dependency: Nous Portal auth expiry, OpenRouter outage
```

### Specific Event from May 1–2, 2026
```
All agents stopped ~23:20–23:22 UTC, restarted automatically.
Trigger: Combined effect of Nous Portal auth expiry (23:24) + disk pressure (82% full) + Python bytecode corruption wave.
```

---

## 4. Advanced Credential Pool Analysis

### auth.json Structure (per-agent)
```json
{
  "version": 1,
  "providers": {},        // rarely used; providers are inferred
  "credential_pool": {
    "nous": null,         // not yet resolved to a specific credential
    "opencode-go": [
      {
        "id": "e8b12b",
        "label": "OPENCODE_GO_API_KEY",
        "auth_type": "api_key",
        "priority": 0,
        "source": "env:OPENCODE_GO_API_KEY",
        "access_token": "***",
        "last_status": "exhausted",   // ok / exhausted / None / error_code
        "last_status_at": 1777510433.564707,
        "last_error_code": 429,
        "last_error_reason": null
      }
    ],
    "ollama-cloud": { "last_status": "ok" },
    "copilot": null
  }
}
```

### Health Indicators
- `last_status: "exhausted"` → API quota exceeded; switch to fallback provider
- `last_status: null` → not yet checked (fresh config) OR auth flow not completed
- Missing `nous` credential → provider not configured; agent forced to fallback chain
- `.env` file present but `auth.json` shows `None` → Nous Portal device-code flow not completed

### Provider Selection Flow
1. Agent checks config.yaml `provider:` setting
2. Looks up `auth.json` credential_pool for that provider
3. If `last_status` is healthy → uses it; otherwise cascades to auto-detection chain
4. **Blocking condition**: All providers exhausted → job fails with Hermes not logged in

### DMOB-Specific Failure (May 02)
```
RuntimeError: No Anthropic credentials found
```
Root: `ANTHROPIC_TOKEN` env var missing from `.env` AND not in `auth.json` credential_pool.

Fix: Add `ANTHROPIC_API_KEY=sk-ant-...` to DMOB's `.env`, restart gateway.

---

## 5. Error Pattern Taxonomy (Hermes-specific)

| Error Message | Likely Cause | Affected Agents | Fix Priority |
|---------------|-------------|-----------------|--------------|
| `EOFError: marshal data too short` | Bytecode corruption | YoYo, Gentech | HIGH — purge pycache |
| `sqlite3.OperationalError: database disk image is malformed` | DB corruption (kanban or session DB) | Desmond, Gentech | HIGH — repair/restore |
| `RuntimeError: Hermes is not logged into Nous Portal` | Auth expired | All (Nous users) | HIGH — `hermes model` |
| `RuntimeError: Refresh session has been revoked` | OAuth token revoked | Yoyo, others | HIGH — re-auth |
| `RuntimeError: No Anthropic credentials found` | Missing `ANTHROPIC_TOKEN` | DMOB | MEDIUM — add env var |
| `elevenlabs.core.api_error.ApiError: status_code: 401` | Invalid/expired ElevenLabs key | Desmond, DMOB | MEDIUM — rotate key |
| `openai.NotFoundError: 404` | Model not found (deprecated/typo) | Desmond | MEDIUM — fix model name |
| `telegram.error.BadRequest: Chat not found` | Telegram chat ID invalid or bot not member | Gentech | MEDIUM — verify channel |
| `ps aux` lines appearing in errors.log | File descriptor leak / stdout-stderr merge | All | LOW — monitor |
| `[Errno 28] No space left on device` | Disk full (root partition) | Historical | MEDIUM — cleanup |

### Telegram-Specific Errors
- **"Chat not found"**: Bot token valid but target `-100...` chat ID either:
  1. Bot not added to group/channel
  2. Chat ID typo in config
  3. Bot was kicked/banned
- **"Bad Gateway"**: Telegram MTProto API transient error; retry logic should handle

### Model/Provider Errors
- **OpenRouter 404**: Model name incorrect (e.g., `minimax/minimax-m2.5:free` deprecated)
- **Nous "exhausted"**: Device-code flow quota exceeded; wait 24h or use fallback

---

## 6. Environment & Configuration Health

### Critical .env Variables (per agent)
```bash
TELEGRAM_BOT_TOKEN=...
ELEVENLABS_API_KEY=...      # TTS
OPENCODE_GO_API_KEY=...     # Code autocomplete
OBSIDIAN_VAULT_PATH=/root/vaults/gentech
TELEGRAM_ALLOWED_USERS=...
TELEGRAM_HOME_CHANNEL=-100...
OLLAMA_API_KEY=...          # Local LLM
# ANTHROPIC_TOKEN missing in DMOB → CRITICAL
```

### config.yaml vs .env Precedence
- YAML errors (syntax) force fallback to `.env`
- Check both if agent not using expected provider
- YAML line 130 in early YoYo config had mapping error (spaces/tabs issue)

### Provider Resolution Order
1. Explicit `provider:` in config.yaml or .env (`HERMES_PROVIDER`)
2. Credential pool `last_status: ok` entry
3. Auto-detection chain (`default_model` fallback)

---

## 7. Disk & Filesystem Health Checks

### Current Status (May 02 2026)
```
/dev/sda1 193G total, 105G used (55%), 89G free
Inode usage: ~8% (healthy)
```
Prior state was 82% used → contributed to I/O errors.

### Watch For
- `sqlite3.OperationalError: disk I/O error` + `[Errno 28] No space left on device`
- Session directory creation failures
- WAL file accumulation (indicates long-running transactions)

---

## 8. Cron Job Execution Verification

### Three-Tier Verification (all must agree)

**Tier 1 — jobs.json** (agent-local)
```json
{
  "last_run_at": "2026-05-02T09:11:39+00:00",
  "last_status": "ok",
  "last_error": null
}
```

**Tier 2 — agent.log** (actual dispatch proof)
```
2026-05-02 09:11:39,190 INFO cron.scheduler: Running job 'Gentech Watchdog' (ID: ...)
2026-05-02 09:11:39,195 INFO [cron_9ecfada01952_...] agent.auxiliary_client: ...
2026-05-02 09:11:39,450 INFO cron.scheduler: Job '9ecfada01952': completed successfully
```
**Must see**: `Running job` + `[cron_<ID>_...]` context + completion line.

**Tier 3 — Output artifact** (optional but definitive)
Check `~/cron/output/<job-id>/<timestamp>.md` file exists and populated.

### False Positive Patterns
- jobs.json shows `last_run_at` but no corresponding `Running job` in agent.log → database out of sync (manual edit required)
- `[cron_<id>_...]` log context visible but no `Running job` → session orphan; dispatcher crashed mid-flight
- Telegram ticker active but no `Running job` → cron executor thread dead (restart gateway)

---

## 9. Quick Health Status Matrix (May 02 snapshot)

| Agent | Cron | Auth | Bytecode | DB | Telegram | Overall |
|-------|------|------|----------|----|----------|---------|
| YoYo | ✅ executing (9 min ago) | ⚠️ Nous OK | ✅ clean | ✅ | ✅ | YELLOW |
| DMOB | ✅ executing (4 min ago) | ❌ Anthropic missing | ✅ clean | ✅ | ⚠️ 2 disconnects | YELLOW |
| Desmond | ✅ executed (59 min ago) | ⚠️ ElevenLabs 401 | ✅ clean | ✅ | ✅ | YELLOW |
| Gentech | ✅ executing (4 min ago) | ⚠️ Nous OK | ✅ clean | ✅ | ❌ Chat not found | YELLOW |

**Classification**: YELLOW = functional but degraded individual features; RED would be no cron execution or crashed gateways.

---

## 10. Post-Mortem Action Items (Immediate)

1. **Gentech**: Add its Telegram bot to channel `-100386354028` or update `TELEGRAM_HOME_CHANNEL` to correct chat ID
2. **DMOB**: Add `ANTHROPIC_API_KEY` to `/root/.hermes/profiles/dmob/.env`
3. **Desmond**: Rotate ElevenLabs API key (invalid 401 across agents suggests shared expired key)
4. **All agents**: Purge global `__pycache__` under `/usr/local/lib/hermes-agent` to prevent future corruption
5. **Cron daemon**: Verify `/root/.hermes/cron/jobs.db` is restored from backup or recreated if remains 0 bytes
6. **Monitor**: Daily watchdog scan for the next 72h to catch recurrence
