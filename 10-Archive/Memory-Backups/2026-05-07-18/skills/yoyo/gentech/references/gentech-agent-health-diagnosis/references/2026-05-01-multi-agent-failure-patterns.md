# Post-Crash Diagnostic Patterns (Discovered 2026-05-01)

## Incident Overview

All four Hermes agents (Gentech, YoYo, DMOB, Desmond) experienced simultaneous failures after a restart cycle at 23:19–23:22. Root causes spanned multiple failure classes: bytecode corruption, credential expiry, and provider API rejections.

## New Error Signatures

### 1. Python Bytecode Corruption

**Symptom:**
```
EOFError: marshal data too short
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1069, in get_code
```

**Affected agents:** Gentech, DMOB

**Trigger:** Interrupted module update, disk write truncation, or venv corruption during pip install/upgrade.

**Detection:**
```bash
# Search errors.log for marshal errors
grep -C2 'marshal data too short' /root/.hermes/profiles/*/logs/errors.log
```

**Recovery:**
```bash
# Clear all .pyc caches (multi-level search)
find /usr/local/lib/hermes-agent -type f -name '*.pyc' -delete
find /usr/local/lib/hermes-agent -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null

# If corruption persists in venv, reinstall hermes-agent
/root/.hermes/hermes-agent/venv/bin/pip install --force-reinstall --no-cache-dir hermes-agent
```

**Prevention:** Ensure atomic package installs; avoid killing Hermes during pip operations.

---

### 2. Process-List Corruption in error.log

**Symptom:** `errors.log` contains lines that look like `ps aux` output:
```
  root      899540  1.8  0.8 370396 132500 ?       Ssl  23:20   0:01 /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main ...
```

**Affected agents:** YoYo (7 lines), DMOB (10 lines), Desmond (7 lines)

**Root cause:** File descriptor collision where a subprocess's stdout is redirected to the same inode as the agent's error log stream. Typically triggered by:
- Concurrent cron jobs writing to the same log file
- `subprocess.run(..., capture_output=False)` with inherited FD descriptors
- Multiple Hermes processes sharing log rotation context

**Impact:** Noise that inflates error log size and obscures real tracebacks. May also cause log parsing failures in monitoring tools.

**Mitigation:**
```bash
# 1. Truncate corrupted sections
> /root/.hermes/profiles/yoyo/logs/errors.log   # clear stale corruption

# 2. Ensure log rotation uses O_APPEND correctly; verify no double-opened files
lsof /root/.hermes/profiles/yoyo/logs/errors.log
```

**Prevention:** Enforce log file exclusive-open mode (`os.O_EXCL` or append-only with coordinated rotation).

---

### 3. Provider Authentication Pipeline Failures

| Agent | Error Message | Provider | Recovery |
|-------|--------------|----------|---------|
| YoYo | `RuntimeError: Hermes is not logged into Nous Portal. Run \`hermes model\` to re-authenticate.` | Nous (StepFun) | `hermes model` → interactive login; or copy `auth.json` from healthy agent |
| DMOB | `RuntimeError: No Anthropic credentials found. Set ANTHROPIC_TOKEN or ANTHROPIC_API_KEY` | Anthropic | `export ANTHROPIC_TOKEN=sk-ant-...` in profile `.env` or `config.yaml` provider section |
| Desmond | `elevenlabs.core.api_error.ApiError: status_code: 401` | ElevenLabs TTS | Refresh `ELEVENLABS_API_KEY` in profile config; verify account quota |

**Key insight:** Different agents use different providers. YoYo uses Nous (StepFun), DMOB uses Anthropic, Desmond uses ElevenLabs. Cross-profile credential isolation means one agent's downtime doesn't auto-recover others.

---

## Agent Status Snapshot (2026-05-01 23:25)

| Agent | Status | Root Cause | Error Log Size | Process PID |
|-------|--------|------------|----------------|-------------|
| Gentech | Running (degraded) | Bytecode corruption + Nous auth missing | 2,007,470 B | 899618 |
| YoYo | Running (degraded) | Nous auth expired + process-list noise | 462,592 B | 899631 |
| DMOB | Running (degraded) | Missing Anthropic token + ElevenLabs 401s + process-list noise | 158,386 B | 899554 |
| Desmond | Running (degraded) | ElevenLabs API key invalid | 138,906 B | 899540 |

**Common trait:** All agents have non-zero error log tails, indicating continuous failed cron cycles even while gateway processes remain alive.

---

## Quick Verification Sequence

```bash
# 1. Check process liveness
ps aux | grep 'hermes gateway run' | grep -v grep

# 2. Check recent agent.log for gateway health
for agent in gentech yoyo dmob desmond; do
  echo "=== $agent ==="
  tail -5 /root/.hermes/profiles/$agent/logs/agent.log | grep -E '(Cron ticker started|Connected to Telegram|ERROR)' || true
done

# 3. Search for known corruption patterns
grep -r 'marshal data too short' /root/.hermes/profiles/*/logs/ 2>/dev/null
grep -r '^  root *[0-9]' /root/.hermes/profiles/*/logs/errors.log 2>/dev/null | head -5
```

---

## Recovery Playbook Order

1. **Bytecode corruption** — clear `*.pyc`, restart agent
2. **Provider auth** — re-login or set env vars, restart agent
3. **TTS API keys** — refresh third-party tokens in profile config
4. **Log pollution** — truncate error logs, investigate concurrent writers
5. **Stale locks** — clear `gateway.pid` and `gateway-locks/` if present

---

## Related

- Main skill: `gentech-agent-health-diagnosis` (see decision tree)
- Reactivation: `devops/gentech-agent-reactivation`
- Provider migration: `devops/hermes-provider-migration`
