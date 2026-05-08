---
name: agent-health-audit
description: Systematic health checks across Hermes agent fleets — detect crashes, stuck processes, missed cron executions, and systemic failures
triggers:
  - keywords: ["health check", "agent status", "watchdog", "fleet health", "audit agents", "check yoyo dmob desmond gentech"]
  - intent: "audit"  # when user wants to verify operational status
  - always_required: false
---

# Agent Health Audit

A disciplined, multi-source verification workflow for checking the operational status of Hermes agents. This skill prevents false negatives by cross-referencing process tables, log freshness, cron execution, and resource constraints.

## Trigger Conditions

Load this skill when:
- User asks to "check health" or "audit" any agent/fleet
- Watchdog/cron job needs to verify agent status
- Investigating "why isn't my agent running" or "cron didn't execute"
- Proactive health monitoring required
- Running scheduled Gentech Watchdog cron (this skill *is* the audit logic)
- Any query that explicitly lists agent names for health review (e.g., "check YoYo DMOB Desmond Gentech")

**Do NOT load for**: single-agent troubleshooting with a known error (use specific debug skills like `hermes-auth-incident-response`, `debugging-hermes-tui-commands`, or vault-specific audit skills instead).

## Methodology

### Phase 1 — Process Liveness Verification
**Never trust `pgrep` alone** — stale PIDs can linger in process tables during rapid restarts. Use this hierarchy:

1. `ps aux | grep -E 'hermes.*<agent>|<agent>.*gateway'` — check actual command lines
2. `pgrep -f 'hermes.*<agent>'` — get PIDs
3. **Validate each PID**: `ps -p <pid> -o pid,stat,etime,cmd` — confirm process exists and is not Zombie (Z) or Uninterruptible (D)
4. **Cross-check with log freshness**: Compare gateway.log modification time vs last log entry timestamp. If `now - last_entry > 300s` and process appears running, it's likely a dead process with stale log file handle.

**System user existence pre-check**: Before deep process investigation, verify the agent's system user account exists:
```bash
id <agent>  # e.g., id desmond
```
If the user is missing (`no such user`), the agent cannot have legitimate processes running under that account (unless manually launched with `sudo -u` misconfiguration). This finding overrides other process signals — a missing system user with an apparent gateway process indicates the process is running under a different user or the profile was launched incorrectly. Flag as **configuration drift** and investigate launch method.

**Why this matters**: May 5, 2026 discovery: `desmond` user absent from `/etc/passwd` yet `hermes-gateway-desmond.service` active. The gateway may have been started manually by root or another user, breaking systemd supervision and credential isolation. Always verify user existence first; if missing, treat agent as **misconfigured** regardless of process state.

**Profile directory case resolution**: Agents may be running with lowercase profile directory names (e.g., `/root/.hermes/profiles/yoyo`) even when referenced as `YoYo`. Always read `/root/.hermes/profiles/<agent>/gateway.pid` (JSON) to get the true profile path and PID rather than assuming case-matching from the display name.

**Log freeze detection**: When `gateway.log` modification age exceeds 300s, verify whether the process still holds the file open:
```bash
lsof -p $(cat /root/.hermes/profiles/<agent>/gateway.pid | jq -r .pid) | grep gateway.log
```
If the handle is open but the file is untouched, the process is likely hung/I/O-blocked rather than dead. Combine this with `ps` state and `%CPU` to distinguish between a truly dead process (no handle, old mtime) vs a live but blocked one (handle open, old mtime, possibly low/zero CPU).

**Red flags**: PID not found in `ps`, state includes `Z` or `D`, log modification age > 5 minutes with no entries, OR log file handle still open by live PID with no writes for >5 minutes.

### Phase 1.5 — Session File Integrity Verification (NEW)

After confirming process liveness, immediately audit recent session files for structural completeness. Incomplete/corrupted session files are a stronger indicator of systemic failure than process status alone.

**⚠️ Schema evolution warning**: Hermes session file format has changed across versions. Older sessions used `status` and `created_at` as top-level keys; current sessions (as of May 5, 2026) use `session_start`, `last_updated`, `message_count`, `model`, `platform`, etc. — **neither `status` nor `created_at` exist anymore**. Checking for those fields will produce a **permanent 0% false positive** across the entire fleet. Before interpreting results, first verify what keys the current session format actually uses:
```bash
# Quick schema probe — pick any recent session and check its top-level keys
python3 -c "
import json, os, glob
d = '/root/.hermes/profiles/gentech/sessions'
files = sorted(glob.glob(d+'/*.json'), key=os.path.getmtime, reverse=True)
if files:
    with open(files[0]) as f: data = json.load(f)
    print('Keys:', list(data.keys())[:15])
    print('Has status:', 'status' in data, '| Has created_at:', 'created_at' in data)
    print('Has session_start:', 'session_start' in data, '| Has last_updated:', 'last_updated' in data)
"
```

**Detection commands** (schema-aware):
```bash
# Check last 2 hours of sessions for completeness
# NOTE: Adapt REQUIRED_KEYS to match current schema before interpreting results
for agent in yoyo dmob desmond gentech; do
  dir="/root/.hermes/profiles/$agent/sessions"
  python3 -c "
import json, glob, os
from datetime import datetime, timedelta
cutoff = datetime.now().timestamp() - 7200
# --- Schema-aware required keys ---
# Old format: {'status', 'created_at'}
# New format (May 2026+): {'session_start', 'last_updated', 'messages'}
REQUIRED_KEYS = {'session_start', 'last_updated', 'messages'}
complete = 0; incomplete = 0; errors = 0
for f in glob.glob('$dir/*.json'):
  try:
    if os.path.getmtime(f) < cutoff: continue
    with open(f) as fh:
      d = json.load(fh)
    if REQUIRED_KEYS.issubset(d.keys()):
      complete += 1
    else:
      incomplete += 1
  except:
    errors += 1
total = complete + incomplete + errors
print(f'{agent.upper()}: total={total} complete={complete} incomplete={incomplete} errors={errors}')
  "
done
```

**Interpretation**:
- `incomplete > 0` → session database write failures, disk pressure, process kill during write, or gateway crash mid-session — **but only if REQUIRED_KEYS matches the current schema**. A 0% rate with the wrong keys set is a false positive, not corruption.
- If ALL recent sessions are incomplete across multiple agents **and you've confirmed the schema probe matches** → **systemic storage/corruption event** (coordinated restart, disk I/O issue)
- Combine with log error density: high incomplete + high 404/auth errors → cascading failure
- Combine with process liveness: gateway appears running but session traces never complete → agent functionally dead

**Recovery correlation**:
- If incomplete sessions coincide with `EOFError: marshal data too short` in logs → bytecode corruption; purge `.pyc` and restart
- If incomplete sessions coincide with `gateway drain timed out` messages → ungraceful shutdown; restart gateways and verify clean session writes
- If isolated to one agent →检查 that agent's disk quota, profile directory permissions, and gateway restart history

**Why this matters**: An agent can have a running process AND clean logs BUT still be functionally broken if every session write is truncated. Always verify session completeness as a **higher-order health signal** than log presence alone.

**Related evidence**: May 5, 2026 check found Yoyo (44/44 incomplete), DMOB (6/6), Desmond (6/6), Gentech (36/36) — all-zero completion rate across fleet despite active processes and Telegram responsiveness. Confirmed fleet-wide degradation.

### Phase 2 — Error Pattern Recognition
Scan logs in this order, marking severity:

**FATAL/IMMEDIATE** (alert):
- `EOFError.*marshal data too short` → bytecode corruption (requires restart + cleanup)
- `status=203/EXEC` in systemd → service path misconfiguration
- `Process not found` when gateway claims running → phantom process
- `sqlite3.DatabaseError: file is not a database` → session DB corruption
- `Refresh session has been revoked` → Nous Portal OAuth expired; all API-dependent jobs blocked until `hermes model` re-authentication
- `Hermes is not logged into Nous Portal` → same as above; primary provider unavailable
- `Model stepfun/step-3.5-flash not supported` or similar `ModelError` → provider has withdrawn support for the configured model; `hermes model` must switch to a supported alternative (e.g., Nous-rated models). This can cascade into all cron jobs failing with 401 even if credentials are valid.
- **Session completeness failure** (schema-validated): After confirming REQUIRED_KEYS match the current session format via schema probe, if >50% of recent sessions still fail the check → systemic session write corruption; agents functionally non-operational despite process liveness. **WARNING**: As of May 5, 2026, the session format no longer includes `status` or `created_at`. Using those keys produces 100% false positives fleet-wide. See schema evolution warning above.

**DEGRADED** (investigate):
- `401 Invalid API key` (ElevenLabs) → credential rotation needed
- `No Anthropic credentials found` → missing env vars
- `Bad Gateway`/`Connection refused` → network/telegram issues
- `last_run_at: null` for cron jobs → dispatch pipeline blocked
- `Auxiliary session_search.*connection error on auto` → auto provider endpoint unreachable; auxiliary client falling back to alternative providers (e.g., nous/google). Indicates misconfigured or unreachable default provider in agent config.yaml (`auxiliary.auto.provider`).
- `Chat not found` (Telegram BadRequest) → bot not in target chat, wrong chat ID, or chat restricted; verify `deliver` destination matches actual bot access
- `Firecrawl client initialization failed: missing direct config and tool-gateway auth` → tool expects tool-gateway auth flow but missing `FIRECRAWL_API_KEY` in `.env` or tool-gateway not providing context. Fix: set `FIRECRAWL_API_KEY` or configure tool-gateway integration properly.
- **False positive: no recent cron output but next_run in future** → Agent may be perfectly healthy; check `next_run_at` in jobs.json. If it's in the future (e.g., 8am job checked at 7:59am), absence of recent output is expected. Only flag as issue if `next_run_at` is in the past AND `last_run_at` is null.

**NORMAL** (no alert):
- `INFO gateway.platforms.telegram: [Telegram] Disconnected` — graceful disconnect, expected
- `Cron ticker started` — normal operation
- `INFO gateway.run: Press Ctrl+C to stop` — manual run indicator

**Implementation**: Always check both `gateway.log` (last 100–200 lines) AND `errors.log` (full tail). Use `grep -i` with patterns: `error|exception|crash|fatal|failed|marshal|401|403|404|timeout|connection refused|no such file|database error`.

**CRITICAL — jobs.json structure awareness**: Hermes cron jobs are stored as a **dictionary object** with a top-level `jobs` array, not a bare list. Expected structure:
```json
{
  "jobs": [
    { "name": "...", "schedule": {...}, "enabled": true, ... },
    ...
  ],
  "updated_at": "2026-05-05T..."
}
```
Access pattern: `data = json.load(file); jobs = data.get('jobs', [])`. Never iterate `data` directly — doing `for job in data[:5]` raises `TypeError: unhashable type: 'slice'` when `data` is a dict (observed May 5, 2026 in DMOB/Desmond audit). Always guard with `isinstance(data, dict) and 'jobs' in data`.

**Gateway log staleness as blocked-agent indicator**:
When an agent is blocked on provider I/O (auth failure, quota block, network hang), it may stop logging entirely despite the process still running. If `gateway.log` modification age > 5 minutes **and** the last log entry timestamp is also > 5 minutes old while the process appears alive, this indicates **provider-layer blockage** rather than a crash. This pattern commonly appears fleet-wide during OAuth revocation or API-key invalidation events. Recovery requires credential/billing fixes, not gateway restart.

**Distinguishing 401 auth/billing failures**:
Not all 401s are equal — correct remediation depends on the error body:

- `Refresh session has been revoked` → OAuth token revoked; requires `hermes model` re-authentication
- `Your API key is invalid, blocked or out of funds` → API key issue; examine `status` field:
  - `quota_exceeded` → valid key but no credits; top up account
  - `invalid_api_key` → key wrong/rotated; update `.env` with current key
- `No provider credentials found` → missing required env var; add key and restart

Never waste time restarting gateways for `Refresh session has been revoked` — only manual OAuth flow fixes it.

### Phase 3 — Cron Execution Verification
**Jobs can be "scheduled" but never execute** if the master cron service is down or if jobs are misassigned. Do not trust `last_run_at` in storage alone.

1. Check master service: `systemctl --user status hermes-gateway.service`
   - If `Active: failed` with exit code `203/EXEC` → ExecStart path likely wrong
   - If `disabled` → won't auto-restart on failure
   - **NOTE**: A failed systemd unit does NOT stop cron if gateways were manually started with `--replace`; cron runs inside each gateway process. Always verify actual cron activity via agent logs and output files, not just systemd state.

2. Verify cron daemon is actually running: `ps aux | grep -E 'hermes.*cron|schedule|scheduler'`
   - Expect a persistent cron/scheduler process per gateway. If absent, dispatch is dead.

3. Check each agent's cron activity evidence (in order of reliability):
   - **Execution markers in agent.log**: Search for `\[cron_<job_id>\]` pattern — this is the most reliable sign a job ran. Example: `grep -E '\[cron_[a-f0-9]+\]' /root/.hermes/profiles/<agent>/logs/agent.log | tail -20`
   - **Job output files**: Check per-agent output directory for recent files: `ls -lat /root/.hermes/profiles/<agent>/cron/output/` (NOT just global `/root/.hermes/cron/output/`). The presence of files with recent timestamps confirms cron dispatches are occurring.
   - Session traces: `find /root/.hermes/profiles/<agent>/sessions -name "session_cron_*<date>.json"` — actual execution creates session records
   - Avoid relying on generic "cron tick" messages alone; they indicate the scheduler thread is alive but not necessarily that jobs dispatched successfully.

4. Correlate: Compare `jobs.json` `last_run_at` vs actual cron.log entries and session timestamps. If `last_run_at` is null but job is `enabled: true` and `state: scheduled`, the dispatch pipeline is blocked.

**Critical distinction — Global vs Profile cron jobs**:
- Global jobs file `/root/.hermes/cron/jobs.json` may contain entries with empty `profile` field (`"profile": null`). These are **orphaned** and never dispatched by the cron scheduler. They are legacy/staging and should be ignored or fixed.
- Each agent's profile directory (`/root/.hermes/profiles/<agent>/cron/jobs.json` or loaded into the gateway's in-memory registry) is the **source of truth** for that agent's scheduled jobs.
- Always audit profile-level jobs first; global jobs.json is not authoritative for runtime dispatch.

**Orphaned Job Detection** (new pattern):
- Run: `hermes cron list` and capture active job IDs
- Cross-check against `/root/.hermes/cron/jobs.json`: any job defined there with `"profile": null` that appears in the active list is **misassigned**; it should not execute until a profile is set. Determine the intended agent from the job name and create the job in that agent's profile instead.
- Warning sign: A job appears in `hermes cron list` as `[active]` but its entry in `jobs.json` has `profile: null` → it was likely migrated improperly and may execute with no agent context or fail silently.
- **Pitfall**: `hermes cron list --json` is NOT a supported flag (returns "unrecognized arguments"). Parse the text output or read `jobs.json` directly instead.

**False positive guard — `last_run_at: null` may be normal**:
If `last_run_at` is null but `next_run_at` is in the future (e.g., checking at 07:59 for a 08:00 job), the job has not missed any executions yet. Only flag as an issue if `next_run_at` is in the past AND `last_run_at` remains null after 2× the schedule interval.

**Systemd vs manual operation**: `hermes-gateway.service` failure does NOT stop cron inside manually started gateways. Check both systemd status and actual gateway cron ticker logs to know true execution state.

### Phase 4 — Systemic Issue Detection
Look for fleet-wide patterns that affect multiple agents:

- **Shared credential failures**: Same error (e.g., `elevenlabs 401`) across all agents → rotate shared API key
- **Bytecode corruption**: Multiple agents showing `marshal data too short` → run `find /usr/local/lib/hermes-agent -name "*.pyc" -delete`, then restart all gateways
- **Disk pressure**: Check `df -h /` — if >80%, corruption risk high
- **Master service failure**: If `hermes-gateway.service` failed, ALL cron dispatch is blocked regardless of individual agent health.
- **Auto-provider connectivity**: Repeated `connection error on auto` in agent logs → auxiliary client cannot reach configured default provider; check `auxiliary.auto.provider` in agent `config.yaml` and verify endpoint reachability.
- **Cron pipeline blockage**: Jobs present in `jobs.json` but absent from `hermes cron list` output, or `last_run_at` remains null → cron scheduler not loading all jobs; check cron daemon process and service status.

## Advanced Diagnostic Patterns

**OAuth revocation + model support withdrawal compound failure**:
When both error types appear within a short window (e.g., `Refresh session has been revoked` AND `ModelError: not supported`), treat as a two-stage recovery:
1. Re-authenticate via `hermes model` immediately (OAuth is the blocker — without valid tokens, you cannot query model catalogs or switch providers)
2. After successful re-auth, check configured model in `config.model` — if the provider has withdrawn support (common with free-tier models like `stepfun/step-3.5-flash`), manually switch to a currently supported alternative before expecting cron jobs to run
3. Validate by running `hermes model list` and confirming the model exists in the provider's catalog

**Model support withdrawal masquerading as auth failure**:
Error pattern: `Model <model_id> not supported` or `ModelError: not supported` returning 401/403.
- This can look like an auth failure but is actually a provider-side deprecation.
- Always read the error body text, not just the HTTP status. If message mentions model support or not found, switch models first. `hermes model` to select a different model from the provider's active catalog.
- Compound failure pattern auth→model: Fix auth first (re-authenticate), then address model availability.

**Auth revocation cascade detection**:
When `Refresh session has been revoked` appears in gateway logs:
1. Expect subsequent Telegram disconnects within 1–3 minutes (auth failure prevents provider initialization)
2. Check `Nous OAuth Proactive Refresh` job status — it will also fail, creating a circular dependency
3. Agents will fall back to alternative providers; direct message responses may still work while scheduled jobs fail
4. Recovery requires manual `hermes model` re-authentication per agent profile; automatic refresh cannot recover from full revocation

**Auth→Disconnect correlation**:
- Scan last 100 lines of `gateway.log` for both `Primary provider auth failed` and `Disconnected from Telegram` within 5 lines
- If pattern found, disconnects are auth-driven, not network issues; focus on credential rotation rather than network debugging

**Process environment vs .env file validation** (extended):
When API keys appear correctly configured but authentication still fails:
1. Check `.env` file contains the key: `grep ELEVENLABS /root/.hermes/profiles/<agent>/.env`
2. **Validate the running process actually loaded it**: Read process environment from `/proc/<pid>/environ` and split by null bytes
   ```bash
   tr '\0' '\n' < /proc/$(cat /root/.hermes/profiles/<agent>/gateway.pid | jq -r .pid)/environ | grep -i elevenlabs
   ```
3. If key absent from process env but present in `.env`, the gateway was started before the key was added/updated — **restart required**.
4. **Also check HERMES_HOME**: The gateway process MUST have HERMES_HOME set in its environment. If missing, the agent crashes immediately with `KeyError: b'HERMES_HOME'`. Verify:
   ```bash
   tr '\0' '\n' < /proc/$(jq -r .pid /root/.hermes/profiles/<agent>/gateway.pid)/environ | grep -i HERMES_HOME
   ```
   If no output, HERMES_HOME is missing from the process environment. The gateway must be relaunched with HERMES_HOME pointing to the profile directory (e.g., `HERMES_HOME=/root/.hermes/profiles/gentech`).
5. When multiple agents share a key, verify **all** gateways were restarted after the last rotation.
6. **Key takeaway**: `.env` files are read at process startup only; no hot-reload. Changes require gateway restart. HERMES_HOME must be set in the environment that launches the gateway, not just in `.env`.

**OAuth session state fingerprint**:
When `Refresh session has been revoked` appears, check `auth.json` for confirming signatures:
- `tokens.expires_at` → `null` or past date indicates dead access token
- `agent_keys` array → empty (`[]`) or length 0 indicates no minted agent keys
- Credential pool exhausted → `credential_pool: no available entries (all exhausted or empty)`
- Combined, these three signs confirm full OAuth session collapse requiring `hermes model` re-auth

**Auth state desynchronization**:
When `Hermes is not logged into Nous Portal` appears with `needs_reauth: true` but a credential pool entry exists (non-empty `credential_pool.nous` with a refresh token), the provider singleton state may be missing. Check `auth.json`: if `providers.nous` is empty/absent and `credential_pool.nous[[0], ['z "$HERMES_HOME']].refresh_token` is present, this indicates desynchronization. Recovery: manually sync the pool entry into `providers.nous` (see `references/2026-05-03-oauth-state-sync-recovery.md`), then re-run the refresh script to determine true token status. If the refresh then fails with `Refresh session has been revoked`, the refresh token itself is invalid and manual `hermes model` re-authentication is required.

**Cron pipeline health — systemd vs manual operation**:
A failed `hermes-gateway.service` (systemd user unit) **does not stop** cron jobs if agents were manually started with `--replace`. The Hermes cron scheduler runs inside each gateway process, not in systemd. Check:
1. `systemctl --user status hermes-gateway.service` → tells you about service supervision, not cron functionality
2. `systemctl --user status hermes-gateway-<profile>.service` → per-agent unit state; it may be `active/running` even when the global unit is `inactive (dead)` for manually-started profiles (expected divergence)
3. Actual cron activity: `grep -i cron /root/.hermes/profiles/<agent>/logs/agent.log` — prefer searching for `[cron_<id>]` execution markers over `cron tick` lifecycle messages
4. Job execution evidence: Check `/root/.hermes/profiles/<agent>/cron/output/` for recent job output files
5. **Pitfall**: Assuming systemd unit status reflects cron health; it only reflects whether the gateway is supervised for auto-restart

**Gateway.pid file format awareness**:
Hermes gateway.pid files are **JSON objects**, not plain PIDs:
```json
{"pid": 307708, "kind": "hermes-gateway", "argv": [...], "start_time": 1091115}
```
Always parse with `jq` or Python `json.loads()` before using the PID value.

**Bytecode corruption detection (Python marshal errors)**:
- Corrupted `.pyc` files often have wrong magic numbers. Python 3.11 magic: `33 0d 0d 0a` (hex `\x33\x0d\x0d\x0a`). Common corruption signature: `a70d0d0a`.
- Find all corrupted caches: `find /usr/local/lib/hermes-agent -name "*.pyc" -exec python3 -m py_compile {} \; 2>&1 | grep -i marshal` or check magic directly: `xxd -l 4 <file>` should show `33 0d 0d 0a`.
- Deletion alone is insufficient; running processes hold corrupted bytecode in memory. Must restart ALL gateways after cleanup.

**Credential failure patterns**:
- ElevenLabs TTS: `elevenlabs.core.api_error.ApiError: status_code: 401` with `'Invalid API key'` — rotate immediately across all agents
- Anthropic: `hermes_cli.auth.AuthError: No Anthropic credentials found` — check profile `.env` for `ANTHROPIC_TOKEN` or `ANTHROPIC_API_KEY`

**Telegram connection health**:
- Normal: `Connected to Telegram (polling mode)` followed by periodic messages
- Degraded: `Telegram network error: Bad Gateway`, `Connection refused`, repeated disconnect/reconnect cycles in short timeframe
- Inactive: No gateway.log entries for >5 minutes while process claims running → stale file handle, process likely dead

**State/config file path fragmentation across profiles**:
A common source of silent divergence: scripts may look for config in `~/.hermes/scripts/` but the actual state symlink lives in the HERMES profile's home directory. Typical error pattern:
```
ERROR: AAE config missing: [Errno 2] No such file or directory: '/root/home/.hermes/scripts/.lfj-aae-config.json'
```
The correct location is usually `/root/.hermes/scripts/.lfj-aae-config.json` (global) or symlinked into the profile's home dir at `/root/.hermes/profiles/<agent>/home/.hermes/scripts/`. Always verify:
1. Where the script THINKS the file is (read script path references)
2. Where the file ACTUALLY lives (`find /root -name ".lfj-*.json" 2>/dev/null`)
3. If the profile-specific path is a broken symlink or missing, recreate it:
   ```bash
   mkdir -p /root/.hermes/profiles/<agent>/home/.hermes/scripts
   ln -sf /root/.hermes/scripts/.lfj-*.json \
          /root/.hermes/profiles/<agent>/home/.hermes/scripts/
   ```

**Cron pipeline file-handle errors**:
Repeated `ValueError: I/O operation on closed file.` in cron job output indicates the output file/stream is being closed prematurely — typically from gateway restart during job execution (race condition) or cron output file rotation mid-execution. This is often transient — clears after gateway restart — but can indicate misconfigured cron output destination if persistent.

**Check**: Inspect job output paths in `/root/.hermes/cron/output/` and verify files are opened in append mode, not write mode that truncates. If errors occurred during a known restart window (e.g., 23:05 drain timeout), treat as symptom, not root cause.

**New variant — Mess Hall shift-job I/O errors**: When multiple scheduled shift-handover jobs (Pre-Shift, Post-Shift, Break 1/2/3) simultaneously log `I/O operation on closed file`, this strongly suggests a **coordinated gateway restart** happened mid-execution across all shift-job outputs. Validate via gateway drain timeout correlation.

**Log staleness detection**:
- Compare gateway.log modification time vs last log entry timestamp within the file. If file modified >5 min ago but latest entry is older, process likely died without log rotation.
- Check agent.log modification age: if >10 min with no entries while systemd shows active, process may be hung (D-state) or zombie.

### Pattern: Coordinated Gateway Restart Detection

**Symptom**: All agents log `Gateway drain timed out after 60.0s with 1 active agent(s); interrupting remaining work.` within a narrow time window (±60 seconds).

**Interpretation**: This is not four independent failures. It indicates a **coordinated gateway restart** (manual `kill`/`systemctl restart`, crash-recovery loop, or deployment event). The drain timeout is the *symptom* of the shutdown, not the root cause.

**Diagnostic checklist**:
1. Verify process uptime across all agents: `ps -eo pid,etimes,cmd | grep hermes_cli.main`. If all PIDs have similar young uptimes (e.g., 5–10 minutes), a restart definitely occurred.
2. Check systemd journal for the restart event: `journalctl --user -u hermes-gateway.service --since "5 min ago"` or inspect per-agent units.
3. Look for `.clean_shutdown marker` skip messages in gateway.log:
   ```
   Skipping .clean_shutdown marker — drain timed out with interrupted agents; next startup will suspend recently active sessions.
   ```
   This confirms an ungraceful shutdown.
4. Correlate with external triggers: Was there a deployment? Manual restart? Crash? Check `dmesg` and `/var/log/syslog` for OOM or signal events.

**Recovery**: After coordinated restart, allow 2–3 minutes for all agents to reconnect to Telegram and reload credentials. Do NOT immediately re-restart if they are already up.

**Follow-up**: Determine *why* the restart happened. If not manual, investigate root cause (OOM? unhandled exception? watchdog kill?).

### Pattern: Cron List `system` Profile Artifact

**Symptom**: `hermes cron list` shows active jobs belonging to specific agents (e.g., "YoYo — Crypto Watchlist") but the `Profile:` field reads `system` instead of `yoyo`.

**Cause**: The master `hermes-gateway.service` is dead and agents are running manually with `--replace`. The global cron dispatcher (which normally aggregates per-agent jobs) is non-functional; `hermes cron list` falls back to showing global `jobs.json` entries with `profile: null` mislabeled as `system`. The jobs are *still executing* inside the individual agent gateways — the display is misleading, not the execution.

**Do NOT**:
- Migrate these jobs to the `system` profile
- Edit `jobs.json` to set `profile: "system"` — that creates orphaned global jobs

**DO**:
- Verify actual execution via agent-local cron output: `ls -lat /root/.hermes/profiles/<agent>/cron/output/`
- Check agent log for `[cron_<job_id>]` execution markers
- Restoring the global `hermes-gateway.service` will fix the display mismatch

**Permanent fix**: Repair `hermes-gateway.service` and restart it so per-agent jobs re-register correctly.

### Pattern: Agent Silence Detection via Session Analysis

**Symptom**: An agent's latest session file(s) contain only `user` role messages with **no assistant responses**. The gateway process appears running, cron jobs may be firing, but the agent produces no output. This is a stronger indicator of functional failure than process liveness alone — the agent is alive but broken.

**Typical causes** (in order of likelihood):
1. **Model initialization failure** — Invalid model ID (404), provider auth failure (401), or model withdrawal; agent cannot initialize LLM client and silently drops every request
2. **Missing required credentials** — `.env` file incomplete (e.g., missing `OPENROUTER_API_KEY`, `ANTHROPIC_TOKEN`); process starts but LLM/TTS toolchains fail on first use
3. **Stale/in-memory corruption** — Earlier bytecode or config corruption cleaned on disk but running process still holds bad state; requires gateway restart
4. **Telegram flood-control backoff saturation** — Agent is temporarily blocked by Telegram rate limits and cannot send messages; distinguish by checking `gateway.log` for flood-control retry messages

**Detection workflow**:
1. Get latest session file: `latest=$(ls -t /root/.hermes/profiles/<agent>/sessions/session_*.json | head -1)`
2. Count messages and roles:
   ```bash
   python3 -c "
import json
with open('$latest') as f:
    d = json.load(f)
msgs = d.get('messages', [])
roles = [m.get('role') for m in msgs]
has_assistant = 'assistant' in roles
print(f'Messages: {len(msgs)}, Has assistant: {has_assistant}')
if not has_assistant:
    print('SILENT AGENT — no assistant response found')
"
   ```
3. Correlate with process liveness and log errors:
   - If process is running but latest session shows only user messages → **agent is not responding**
   - Check `errors.log` immediately for model/credential errors matching the session timeframe
   - Check `gateway.log` for provider initialization failures around the same timestamp

**Cron-specific variant**: Silent cron jobs often leave behind user-triggered cron sessions with only user messages (the dispatched job payload) and no assistant response. Check for session files prefixed with `session_cron_` that have only user messages.

**Recovery**:
- If model 404 suspected: verify `config.yaml` model ID against provider catalog; fix and restart
- If missing credentials: add to `.env`, restart gateway
- If stale state: restart gateway (no file changes needed)
- Validate: Trigger a test message or wait for next cron; verify assistant response appears in session

**Key insight**: Session traces are persistent records of every message the agent processed and responded to. An agent that receives inputs but never emits assistant responses is functionally dead even if the process appears alive. Always cross-check session message roles when diagnosing "alive but not working" reports.

**Related**: See `references/2026-05-04-gentech-watchdog-silent-agents-detection.md` for session evidence showing YoYo/DMOB silent while Desmond responding.

### Pattern: Zero Cron Output Despite Active Ticker

**Symptom**: The agent's cron ticker is alive (`.tick.lock` mtime updates every 60s; gateway.log shows "Cron ticker started") but the cron output directory (`/root/.hermes/profiles/<agent>/cron/output/`) contains **zero files** or only ancient files. No job execution evidence appears despite enabled jobs and recent scheduled times.

**Interpretation**: This indicates the cron **scheduler thread** is alive but **dispatcher is blocked or misrouted**. Common causes:

1. **Provider/auth failure blocking job initialization** — The cron runner attempts to create a session for each job but fails immediately during LLM/client initialization (e.g., `RuntimeError: Refresh session has been revoked`, `No LLM provider configured`). The job is marked `error` and no output file is written.
2. **Cron daemon running but job registry empty** — The ticker thread started but no jobs were loaded into the in-memory registry (e.g., `jobs.json` malformed, unparsable, or `jobs` key missing; or `system` vs `profile` mismatch preventing job injection).
3. **Output directory permission/write error** — The cron daemon cannot write output files (disk full, permission denied, closed file handle). Check `errors.log` for `PermissionError` or `OSError: [Errno 5] Input/output error`.
4. **Silent exception during job dispatch** — An unhandled exception in the cron runner's pre-execution hook causes the job to abort before output file creation, with errors only in `errors.log` (not `cron.log`).

**Detection sequence**:
1. Confirm ticker alive: Check `.tick.lock` mtime; should be recent (≤2× tick interval). If stale → cron daemon dead (see Pattern: Cron daemon lifecycle tracking).
2. Verify jobs loaded: `cat /root/.hermes/profiles/<agent>/cron/jobs.json` — confirm `jobs` array present and non-empty; `enabled: true`. Cross-check with `hermes cron list` output.
3. Check for recent cron error entries in `errors.log` matching the scheduled times. Filter: `grep -E "cron.*failed|ERROR cron" errors.log | tail -20`.
4. Inspect output directory modification time: `stat /root/.hermes/profiles/<agent>/cron/output/` — if directory mtime is old while tick lock is fresh, output sink is blocked.
5. Validate `.env` and `auth.json` — missing credentials cause pre-execution failure without producing output.

**Recovery**:
- If auth errors → fix credentials, restart gateway
- If jobs.json malformed → restore from backup or `hermes cron create` to rebuild
- If output directory permission issue → `chown -R <agent>:<agent> /root/.hermes/profiles/<agent>/cron/output/`
- If daemon crashed but process alive → restart gateway to respawn cron thread

**Why this matters**: May 5, 2026 audit found DMOB, Desmond, Gentech all showing fresh `.tick.lock` timestamps but **zero** files in their per-agent `cron/output/` directories. The presence of a running ticker without execution artifacts is a red flag that requires deeper auth and job-registry validation, not just "wait for next tick."

### Pattern: Telegram Flood Control After Restart Burst

**Symptom**: Gateway logs show `Telegram flood control on send (attempt 1/3), retrying in 10.0s: Flood control exceeded`.

**Trigger**: Synchronized restart of multiple agents (or a single agent with many buffered messages) results in a burst of Telegram API calls within a short window. Telegram's rate limits kick in (≈20–30 messages/second per bot).

**Behavior**: The gateway automatically retries with exponential backoff (3 attempts). No manual intervention needed unless the flood persists over multiple cron cycles.

**Mitigation**:
- After any coordinated restart, expect 30–90 seconds of flood-control backoff.
- Avoid manual `send_message` during this window.
- If flood control persists beyond 5 minutes, check for runaway cron loops sending duplicate messages.

### Pattern: Quota Exceeded vs Invalid API Key (TTS)

Both return 401 but require different remediation:

| Error Body Fragment | Meaning | Fix |
|---|---|---|
| `'status': 'quota_exceeded'` | Valid key, zero credits remaining | Top up account or rotate to a different ElevenLabs account with quota |
| `'status': 'invalid_api_key'` | Key rejected as wrong/rotated | Update `.env` with current valid key |

**Quick check**: `grep ELEVENLABS /root/.hermes/profiles/*/.env` confirms key presence; `tail -20 errors.log` shows which status string appears.

### Pattern: Alive But Degraded (Process Running But Services Broken)

**Symptom**: Gateway process running, Telegram messages being sent/received, but core functionality broken (TTS fails, LLM calls fail, cron jobs error). The agent appears alive but is functionally degraded.

**Root causes** (often co-occurring):
1. **Shared provider quota exhausted** (e.g., ElevenLabs `quota_exceeded`) — all agents using same account hit limit simultaneously
2. **Nous OAuth tokens missing/expired** — `access_token` absent or `expires_at` in past; refresh_token alone insufficient if session revoked
3. **Missing required environment variables** (e.g., DMOB missing ANTHROPIC_TOKEN) — process runs but specific toolchains fail
4. **Stale in-memory bytecode or configuration** — earlier corruption cleaned from disk but running process still holds bad state

**Diagnostic sequence**:
1. Confirm process liveness: `ps -p $(jq -r .pid /root/.hermes/profiles/<agent>/gateway.pid) -o pid,stat,etime,cmd`
2. Check recent error.log entries (last 5–30 min) for recurring 401/403/auth errors
3. Validate `auth.json` provider state:
   ```bash
   python3 -c "
import json
with open('/root/.hermes/profiles/<agent>/auth.json') as f:
    d = json.load(f)
nous = d.get('providers', {}).get('nous', {})
print(' access_token?', 'access_token' in nous)
print(' expires_at?', nous.get('expires_at'))
print(' needs_reauth?', d.get('needs_reauth', 'N/A'))
"
   ```
4. Verify process environment loaded required keys:
   ```bash
   tr '\0' '\n' < /proc/$(jq -r .pid /root/.hermes/profiles/<agent>/gateway.pid)/environ | grep -iE 'elevenlabs|anthropic|nous'
   ```
5. Check `.env` file completeness: `grep -E 'ELEVENLABS|ANTHROPIC|OLLAMA' /root/.hermes/profiles/<agent>/.env`

**Recovery**:
- If **quota exceeded**: Rotate provider API key or top up account, update all affected `.env` files, restart all gateways
- If **OAuth access token missing/expired**: Run `hermes model` to re-authenticate; if refresh session revoked, manual re-auth required
- If **missing env var**: Add to `.env`, restart that agent's gateway
- If **stale bytecode**: Restart gateway after confirming `.pyc` cleanup already performed

**Key insight**: A running process does **not** imply functional health. Always audit error.log and auth state even when Telegram responsiveness is confirmed.

See also: `references/2026-05-04-fleet-alive-but-degraded.md` for full incident case study.

### Pattern: Process Uptime as Coordinated-Restart Evidence

When investigating "what happened at 23:05", process elapsed time (`etimes`) is more reliable than log timestamps alone:

```bash
ps -eo pid,etimes,cmd | grep hermes_cli.main
# etimes = elapsed seconds since process start
```

If all agent PIDs show `etimes` between 300–600 seconds, a restart occurred 5–10 minutes ago. Correlate with `ps -eo pid,lstart,cmd` for exact start timestamp.

Use this to distinguish:
- Single-agent crash (only one PID young, others old)
- Full fleet restart (all PIDs similarly young)
- Gradual drift (mix of ages)

### Pattern: Auth Revocation Cascade Detection (Enhanced)

When `Refresh session has been revoked` appears in **any** agent's logs, immediately scan the **entire fleet**:

```bash
for a in yoyo dmob desmond gentech; do
  count=$(grep -c "Refresh session has been revoked" \
    /root/.hermes/profiles/$a/logs/errors.log 2>/dev/null || echo 0)
  echo "$a: $count revocation events logged"
done
```

**Propagation window**: Revocation may affect agents at different times depending on when their last token refresh was attempted. Expect to see revocation entries appear over a 30–60 minute window across the fleet as different cron jobs hit the endpoint.

**Recovery coordination**: Authenticate all affected agents **before** expecting any Nous-dependent cron to succeed. Do not rely on fallback providers during recovery — they may be configured with stale credentials too.

**Post-auth validation**: After `hermes model`, run the Nous OAuth proactive refresh script manually to confirm tokens minted:
```bash
~/.hermes/profiles/gentech/scripts/refresh_nous_oauth.py
```
### Pattern: Model Provider Deprecation Cascade

**Symptom**: All agents simultaneously fail with `Model '<model_id>' not found` (404) errors. Gateways may show blank model configuration in `hermes status`. Fallback providers present in config (`openai`, `ollama`) are not operational due to missing credentials/configuration.

**Root causes** (two distinct scenarios):
1. **Model withdrawn** — provider removed the model from catalog (e.g., free-tier sunset)
2. **Model ID misconfiguration** — typo or wrong namespace/prefix (e.g., `nousresearch/trinity-large-thinking` instead of `arcee-ai/trinity-large-thinking`)

Both produce identical 404 errors. Always distinguish by checking the configured model ID against the provider's live catalog before assuming deprecation. Note: the error message's quoted model ID is what the agent *tried to use* — that's the string to verify in the catalog, not the human-readable model name.

**Quick verification checklist**:
- Check agent's configured model: `grep 'default:' /root/.hermes/profiles/<agent>/config.yaml`
- Query OpenRouter catalog: `curl -s https://openrouter.ai/api/v1/models -H "Authorization: Bearer $OPENROUTER_API_KEY" | jq -r '.data[].id' | grep -i trinity`
  Expected output includes `arcee-ai/trinity-large-thinking` (correct). The string `nousresearch/trinity-large-thinking` will NOT appear — that's the misconfiguration.
- **Fix**: Update all agent config.yaml files to `model.default: arcee-ai/trinity-large-thinking` OR run `hermes model` interactively per agent to select the correct model from the catalog. Restart all gateways after batch update.

**Differential recovery is possible**:
- Some agents may auto-recover before others if they have a working fallback provider configured and their auxiliary auto-detection triggers
- Always check each agent's last log entry individually to determine recovery state before manual intervention
- See Pattern: Differential Agent Recovery from Model Deprecation below for detection and interpretation

**Detection**:
- Scan `errors.log` across all agents for `Model.*not found` or `NotFoundError` with 404 status
- Run `hermes model` — if it shows blank or errors, the model is invalid
- Check agent config: `grep 'default:' /root/.hermes/profiles/<agent>/config.yaml`
- **Verify model existence**: Query provider's models API (e.g., `curl https://openrouter.ai/api/v1/models -H "Authorization: Bearer $OPENROUTER_API_KEY"`) and confirm the exact model ID string exists in the response
- Pay attention to **namespace/prefix**: `nousresearch/` models are hosted by OpenRouter under the Nous Research organization, while `arcee-ai/` are from a different organization on OpenRouter. Trinity is listed as `arcee-ai/trinity-large-thinking`, NOT `nousresearch/trinity-large-thinking`.

**Recovery sequence**:
1. Identify a valid replacement model from the provider's active catalog (watch for correct prefix/namespace)
2. Update each agent's config: edit `/root/.hermes/profiles/<agent>/config.yaml` → `model.default` to a correct model ID
3. Alternative: Run `hermes model` interactively per agent to select a working model from the catalog
4. Restart all gateways: `pkill -f hermes.*gateway` then restart each
5. Validate: Trigger a test cron job or send a direct message; confirm 200 responses

**Pitfalls**:
- Changing only the fallback provider models is insufficient — the primary `model.default` must be valid or the gateway fails to initialize the LLM client and crashes on first use. Fallbacks only engage when the primary fails; if primary is invalid from startup, the agent never reaches the fallback logic.
- **Namespace confusion**: Do not assume the model publisher name in the error (e.g., "nousresearch") matches the provider organization prefix. Always verify the exact ID in the provider's catalog. Trinity uses `arcee-ai/` prefix on OpenRouter, despite being a Nous Research model.
- **Recovery may be non-uniform**: Some agents may auto-recover via auxiliary provider fallback while others remain stuck, depending on their individual configuration. Audit each agent separately; do not assume all-or-nothing recovery.

**Prevention**:
- Subscribe to provider model deprecation announcements
- Periodically run `hermes model list` to verify configured models remain available
- Maintain a `references/model-catalog-snapshot.md` in this skill directory documenting known-good model IDs per provider, updated quarterly

**See also**: 
- `references/2026-05-04-model-deprecation-fleet-failure.md` (initial incident)
- `references/2026-05-04-model-deprecation-cascade-differential-recovery.md` (differential recovery pattern, stuck-timestamp detection, session silence confirmation)
- `references/2026-05-04-model-deprecation-fleet-failure.md` for full incident case study
- `references/2026-05-04-model-deprecation-cascade-differential-recovery.md` for follow-up check showing partial fleet recovery (Desmond auto-recovered, others remained stuck) and the stuck-timestamp detection technique

### Pattern: Differential Agent Recovery from Model Deprecation

**Symptom**: Following a fleet-wide model 404 error, some agents resume normal operation (auto-failover to alternative provider) while others remain stuck in repeating failure loops — even hours later.

**Diagnostic**: After confirming fleet-wide model deprecation, check each agent's **last log entry** and **recent activity** individually:

```bash
tail -1 /root/.hermes/profiles/<agent>/logs/agent.log
```

Auto-recovered signs:
- `Auxiliary auto-detect: using main provider nous (<fallback_provider>/<fallback_model>)`
- Absence of recent 404 model errors in the last 20–50 lines
- Presence of `[cron_<id>]` execution markers with exit code 0

Still-stuck signs:
- Last entry is a `RuntimeError: Model ... not found` or Traceback
- No successful cron runs since failure onset
- Log shows stuck-timestamp clusters (see next pattern)

**Why it happens**: Auto-failover requires:
1. A fallback provider configured in the agent's config with valid credentials
2. The auxiliary auto-detection logic to be triggered on a request *after* the primary provider fails
3. Sufficient gateway uptime for the fallback attempt to occur

Agents without a configured/working fallback remain indefinitely stuck. Recovery timing is non-uniform — depends on cron schedule and whether the gateway process survived.

**Recovery**:
- For auto-recovered agents: monitor, no manual action
- For stuck agents: manually correct the model ID (see main recovery sequence) or configure a valid fallback provider as interim mitigation

**Related**: See `references/2026-05-04-model-deprecation-cascade-differential-recovery.md` for timestamp-based stuck-detection and session silence confirmation methodology.

### Pattern: Stuck Timestamp Signature in Per-Agent Logs

**Symptom**: An agent's agent.log shows **multiple distinct log lines sharing identical timestamps** (down to the second), typically in clusters of 5–20 entries. This is a strong indicator of a **non-recovering, repeating failure loop** where the agent repeatedly attempts the same operation (e.g., cron job firing every N minutes) and fails within the same clock second each time.

**Detection**:
```bash
# Extract timestamps from last 150 lines, count duplicates
tail -150 /root/.hermes/profiles/<agent>/logs/agent.log | awk '{print $1" "$2}' | sort | uniq -c | sort -nr | head -20
```

If you see lines like:
```
   16 2026-05-04 21:00:30
   10 2026-05-04 21:05:32
```
— that's 16 separate log entries all timestamped `21:00:30`. This is abnormal and indicates the agent is stuck in a rapid retry/error cycle without backoff or recovery.

**Interpretation**:
- Clusters at Franken-times like `21:00:30`, `21:05:32` correspond to cron schedule boundaries (:00, :05, etc.)
- High cluster count (≥5) means the agent has failed at that scheduled time multiple days in a row without progressing to a healthy state
- **Not** seen in healthy agents; healthy agents show timestamp diversity (one or two entries per second at most)

**Why this works**: Normal log entries are spaced by at least hundreds of milliseconds or seconds. Getting 10+ entries within the same second means the error is being written repeatedly in a tight loop (likely each cron attempt writes multiple error lines, and those attempts are happening precisely on schedule without any recovery). A truly recovering agent would show a successful entry breaking the cluster pattern.

**Action**: Treat agents with stuck-timestamp clusters as **degraded/critical** even if the gateway process appears running. Investigate the underlying error (likely model deprecation, auth failure, or missing credentials) and apply targeted remediation.

**Case study**: `references/2026-05-04-model-deprecation-cascade-differential-recovery.md` documents this pattern across YoYo and DMOB during the May 4 Trinity model incident — timestamps clustered at every 5-minute boundary for hours, confirming agents were not recovering autonomously.

['f \'cron_<id>]` markers for >2× max job interval).\n4. **Cron database corruption** — `~/.hermes/cron/cron.db` or `jobs.db` empty (0 bytes) prevents job loading; `hermes cron list` may return empty or error.\n\n**Distinction from other patterns**:\n- *Orphaned cron*: Jobs exist in `jobs.json` but have `profile: null`; some agents may still run other jobs.\n- *Missing cron configuration*: Agent scripts exist but no cron entries; other agents unaffected.\n- *Pipeline dead*: Fleet-wide zero activity, regardless of job registration status.\n\n**Recovery**:\n1. If using separate cron daemon: `systemctl --user start hermes-cron.service` (or the appropriate service name); enable: `systemctl --user enable hermes-cron.service`\n2. If cron runs inside gateways: Ensure all agent gateway processes are running. Restart master `hermes-gateway.service` if failed:\n   ```bash\n   systemctl --user restart hermes-gateway.service\n   ```\n3. If cron database empty: Rebuild active registry from `jobs.json` (see `references/cron-registry-corruption.md`).\n4. After restoring, verify activity: `find ~/.hermes/cron/executions -type f -mmin -15` should produce recent files; agent logs should show `[cron_` markers.\n\n**See also**: `references/2026-05-05-cron-execution-missing-configuration.md` — May 5, 2026: DMOB, Desmond, Gentech have running gateways but zero cron execution since May 4; YoYo executing but with AAE config path error; demonstrates detection of missing cron triggers and HOME path fragmentation.\n\n### Pattern: Agent Script Present but No Cron Schedule\n\n**Symptom**: An agent profile directory contains executable scripts (e.g., `/root/.hermes/profiles/<agent>/scripts/`) but none of them are running on schedule. The agent\'s gateway process is healthy, but no work is being dispatched.\n\n**Root causes**:\n1. No crontab entry launching the script (system cron never triggers)\n2. Script not registered in Hermes internal cron registry (`jobs.json`)\n3. Cron daemon service stopped or not running\n4. Script marked executable but cron job entry deleted/disabled\n\n**Detection workflow**:\n1. List agent scripts: `ls -la /root/.hermes/profiles/<agent>/scripts/` — identify candidate automation scripts\n2. Check system crontab for that agent: `crontab -l` (as the hermes user) — look for entries referencing `/profiles/<agent>/scripts/`\n3. Check Hermes internal cron registry: `cat /root/.hermes/profiles/<agent>/cron/jobs.json` — confirm script registered with a schedule\n4. Verify cron activity evidence:\n   - **Agent log**: `grep -E \'\\\\[cron_[a-f0-9]+\\\\]\' /root/.hermes/profiles/<agent>/logs/agent.log | tail -20`\n   - **Cron output**: `ls -lat /root/.hermes/profiles/<agent>/cron/output/` (per-agent output dir)\n   - **Session records**: `find /root/.hermes/profiles/<agent>/sessions -name "session_cron_*"` — check timestamps\n\nIf scripts exist but no cron entries (system or Hermes) and no execution evidence → **agent is idle by misconfiguration**.\n\n**Recovery**:\n- Option A (preferred): Register script in Hermes internal cron for that agent profile:\n  ```bash\n  hermes cron create --profile <agent> --name "<descriptive name>" --schedule "<crontab>" --script "/root/.hermes/profiles/<agent>/scripts/<script>.py', "n  ```\n- Option B: Add system crontab entry for that agent (ensure HERMES_HOME env var set correctly):\n  ```\n  */10 * * * * HERMES_HOME=/root/.hermes/profiles/<agent> /usr/bin/env python3 /root/.hermes/profiles/<agent>/scripts/<script>.py >> /root/.hermes/profiles/<agent>/cron.log 2>&1\n  ```\n\n**Pitfall**: Mixing both system cron and Hermes internal cron for the same script causes duplicate execution (see Pattern: Duplicate Cron Execution Detection). Choose exactly one mechanism.\n\n**See also**: `references/2026-05-04-missing-cron-configuration.md` — DMOB and Desmond profiles with scripts present but no crontab entries, resulting in zero scheduled work.\n\n**New case**: `references/2026-05-05-cron-execution-missing-configuration.md` — May 5, 2026: DMOB, Desmond, Gentech have running gateways but zero cron execution since May 4; YoYo executing but with AAE config path error; demonstrates detection of missing cron triggers and HOME path fragmentation.\n\n### Pattern: Python NameError in Cron Scripts\n\n**Symptom**: Cron job repeatedly crashes with `NameError: name 'X' is not defined` in agent cron logs. The error appears on every execution at a consistent line number."]

**Symptom**: An agent profile directory contains executable scripts (e.g., `/root/.hermes/profiles/<agent>/scripts/`) but none of them are running on schedule. The agent's gateway process is healthy, but no work is being dispatched.

**Root causes**:
1. No crontab entry launching the script (system cron never triggers)
2. Script not registered in Hermes internal cron registry (`jobs.json`)
3. Cron daemon service stopped or not running
4. Script marked executable but cron job entry deleted/disabled

**Detection workflow**:
1. List agent scripts: `ls -la /root/.hermes/profiles/<agent>/scripts/` — identify candidate automation scripts
2. Check system crontab for that agent: `crontab -l` (as the hermes user) — look for entries referencing `/profiles/<agent>/scripts/`
3. Check Hermes internal cron registry: `cat /root/.hermes/profiles/<agent>/cron/jobs.json` — confirm script registered with a schedule
4. Verify cron activity evidence:
   - **Agent log**: `grep -E '\\[cron_[a-f0-9]+\\]' /root/.hermes/profiles/<agent>/logs/agent.log | tail -20`
   - **Cron output**: `ls -lat /root/.hermes/profiles/<agent>/cron/output/` (per-agent output dir)
   - **Session records**: `find /root/.hermes/profiles/<agent>/sessions -name "session_cron_*"` — check timestamps

If scripts exist but no cron entries (system or Hermes) and no execution evidence → **agent is idle by misconfiguration**.

**Recovery**:
- Option A (preferred): Register script in Hermes internal cron for that agent profile:
  ```bash
  hermes cron create --profile <agent> --name "<descriptive name>" --schedule "<crontab>" --script "/root/.hermes/profiles/<agent>/scripts/<script>.py"
  ```
- Option B: Add system crontab entry for that agent (ensure HERMES_HOME env var set correctly):
  ```
  */10 * * * * HERMES_HOME=/root/.hermes/profiles/<agent> /usr/bin/env python3 /root/.hermes/profiles/<agent>/scripts/<script>.py >> /root/.hermes/profiles/<agent>/cron.log 2>&1
  ```

**Pitfall**: Mixing both system cron and Hermes internal cron for the same script causes duplicate execution (see Pattern: Duplicate Cron Execution Detection). Choose exactly one mechanism.

**See also**: `references/2026-05-04-missing-cron-configuration.md` — DMOB and Desmond profiles with scripts present but no crontab entries, resulting in zero scheduled work.

['cron_[a-f0-9]+\\]\' /root/.hermes/profiles/<agent>/logs/agent.log | tail -20`\n   - **Cron output**: `ls -lat /root/.hermes/profiles/<agent>/cron/output/` (per-agent output dir)\n   - **Session records**: `find /root/.hermes/profiles/<agent>/sessions -name "session_cron_*"` — check timestamps\n\nIf scripts exist but no cron entries (system or Hermes) and no execution evidence → **agent is idle by misconfiguration**.\n\n**Recovery**:\n- Option A (preferred): Register script in Hermes internal cron for that agent profile:\n  ```bash\n  hermes cron create --profile <agent> --name "<descriptive name>" --schedule "<crontab>" --script "/root/.hermes/profiles/<agent>/scripts/<script>.py', 'Option B: Add system crontab entry for that agent (ensure HERMES_HOME env var set correctly):\n  ```\n  */10 * * * * HERMES_HOME=/root/.hermes/profiles/<agent> /usr/bin/env python3 /root/.hermes/profiles/<agent>/scripts/<script>.py >> /root/.hermes/profiles/<agent>/cron.log 2>&1\n  ```\n\n**Pitfall**: Mixing both system cron and Hermes internal cron for the same script causes duplicate execution (see Pattern: Duplicate Cron Execution Detection). Choose exactly one mechanism.\n\n**See also**: `references/2026-05-04-missing-cron-configuration.md` — DMOB and Desmond profiles with scripts present but no crontab entries, resulting in zero scheduled work.\n\n**New case**: `references/2026-05-05-cron-execution-missing-configuration.md` — May 5, 2026: DMOB, Desmond, Gentech have running gateways but no cron execution since May 4; YoYo executing but with AAE config path error; demonstrates detection of missing cron triggers and HOME path fragmentation.']

### Pattern: Python NameError in Cron Scripts

**Symptom**: Cron job repeatedly crashes with `NameError: name 'X' is not defined` in agent cron logs. The error appears on every execution at a consistent line number.

**Root cause**: Typo or wrong variable name in the script (e.g., `elif eff>= 30:` instead of `elif efficiency>= 30:`). Python NameError indicates the variable was never defined in the current scope.

**Detection**:
- Extract the exact error line from cron log: `grep -A 2 'NameError' /root/.hermes/profiles/<agent>/cron.log`
- Open the referenced script and line number: `sed -n '<N>,<N+5>p' /root/.hermes/profiles/<agent>/scripts/<script>.py`
- Verify variable name matches function parameter or prior assignment

**Recovery**:
1. Edit the script to correct the variable name
2. Test locally if possible: `python3 /root/.hermes/profiles/<agent>/scripts/<script>.py` (may require mock inputs)
3. Clear error history (optional): truncate cron log to avoid confusion
4. Wait for next scheduled execution; verify success in agent log (`[cron_<job_id>]` with exit code 0)

**Prevention**: Before deploying cron scripts, lint with `python3 -m py_compile <script>.py` to catch syntax errors and undefined names. Add defensive checks in critical branches.

**See also**: `references/2026-05-04-yoyo-nameerror-cron-crash.md` — YoYo `defi-milestone-tracker.py` line 307: `elif eff>= 30:` → corrected to `elif efficiency>= 30:`.

### Pattern: Shared OAuth Credential Fleet-Wide Cascade

**Symptom**: All agents fail simultaneously with model/API 404 or 401 errors, and investigation reveals all profiles share identical OAuth credentials (`refresh_token` prefix matches across all `auth.json` files). When the shared access token expires or the refresh token is revoked, the entire fleet becomes non-functional at once.

**Detection**:
```bash
# Compare refresh token prefixes across all profiles
for agent in yoyo dmob desmond gentech; do
  token=$(python3 -c "import json; print(json.load(open('/root/.hermes/profiles/$agent/auth.json'))['credential_pool']['nous'][0]['refresh_token'][:30])")
  echo "$agent: $token"
done
```
If all prefixes match → **shared credential pool**. A single expiry/revocation event immobilizes the entire fleet.

**Forensic follow-up** (after confirming sharing):
1. Check access token expiry across all agents — they will be identical:
   ```bash
   for agent in yoyo dmob desmond gentech; do
     exp=$(python3 -c "import json; print(json.load(open('/root/.hermes/profiles/$agent/auth.json'))['credential_pool']['nous'][0]['expires_at'])")
     echo "$agent: $exp"
   done
   ```
2. If `expires_at` is in the past → fleet-wide auth failure until `hermes model` re-authentication is performed per profile
3. Verify agent key expiry separately (`agent_key_expires_at`) — this may still be valid even when access token expired, but the access token is required for inference

**Root causes** (why sharing happens):
- Single `hermes model` login performed for one profile, then `auth.json` copied to other profiles
- Shared HOME or symlinked `~/.hermes/auth.json` across profiles (unlikely here; each has independent file but content cloned)
- Initial deployment script that populated credentials identically across all agents

**Impact scope**: 
- Fleet-wide model 404 errors (provider returns 404 when access token invalid)
- Fleet-wide Telegram disconnects (auth failure prevents gateway from initializing platforms)
- Cron jobs across all agents fail with `Hermes is not logged into Nous Portal` or `Refresh session has been revoked`
- Session completeness drops to 0% (agents cannot process requests)

**Recovery**:
1. **Do NOT** restart gateways repeatedly — OAuth revocation requires manual re-auth
2. On each agent, run interactive `hermes model` to re-authenticate with Nous Portal
3. After re-auth, verify token minted: check `auth.json` `expires_at` is in the future and `agent_key` present
4. Restart all gateways to pick up fresh credentials
5. Validate: tail `errors.log` for 5 min; confirm no more `not logged into Nous Portal` messages; check cron execution resumes

**Prevention**:
- **Never** copy `auth.json` between profiles; each agent should have independent OAuth device-code flow
- If credential rotation is needed, rotate via `hermes model` on EACH profile individually
- Consider per-agent Nous applications (different client IDs) to isolate rotation failures
- Add a health-check alert: `refresh_token` prefix drift detection — if all agents report same prefix, warn about shared credential risk

**Related case**: `references/2026-05-05-fleet-oauth-shared-credential-cascade.md`

### Pattern: Telegram "Chat not found" Access Failure

**Symptom**: Gateway logs show `[Telegram] Failed to send Telegram message: Chat not found` for a specific agent. The bot is either not a member of the target chat, the chat ID is stale/incorrect, or the chat has restricted bot access (privacy settings/kicked).

**Error signature**:
```
ERROR gateway.platforms.telegram: [Telegram] Failed to send Telegram message: Chat not found
```
Telegram HTTP 400 BadRequest with reason `chat not found`.

**Distinguish from other Telegram errors**:
- `Flood control exceeded` → rate limit
- `Network error, scheduling reconnect` → connectivity
- `Unauthorized` → invalid bot token
- `Chat not found` → **destination access problem**

**Common causes**:
1. Bot never joined the target chat/channel (invite link expired or never used)
2. Bot was removed/kicked from the chat
3. Chat ID changed (e.g., group converted to supergroup, migrated)
4. Bot blocked by chat privacy settings (Restrict saving content → bot can't post)
5. Using a user chat ID instead of group/channel ID

**Diagnostic sequence**:
1. Confirm bot token valid: `hermes telegram status`
2. Verify the target chat ID in agent config/cron job destination matches the actual chat:
   - Check `deliver` field in cron job definition (`jobs.json`)
   - Compare against known working chat IDs from other agents
3. Test manually:
   ```bash
   curl -s "https://api.telegram.org/bot<token>/getChat?chat_id=<target_chat_id>"
   ```
   If returns `{"ok":false,"error_code":400,"description":"Chat not found"}` → confirms access problem
4. Check if other agents can post to the same chat — if only one agent fails, that agent's bot may be using a different token or the chat ID is agent-specific

**Recovery**:
- Re-invite the bot to the group/channel using an active invite link
- Update the chat ID in the agent's cron job `deliver` field if the chat migrated
- If bot was kicked/restricted, adjust chat privacy settings
- After fix, test: `hermes send --profile <agent> --chat <chat_id> "test"`
- Verify gateway.log shows successful send

**Prevention**:
- Store Telegram chat IDs in vault with provenance (which bots are members)
- Before creating cron jobs, verify bot membership with `getChat` API
- If chat is private, generate never-expiring invite link and document it
- Monitor for sudden `Chat not found` spikes

**Related**: `references/2026-05-05-gentech-telegram-chat-not-found.md`

### Pattern: Missing Skill Registry Cron Skipping

**Symptom**: Cron jobs fail immediately with `Skill 'X' not found, skipping` errors. The job is enabled and scheduled, but the referenced skill module is absent from the agent's skill registry.

**Error signature**:
```
WARNING cron.scheduler: Cron job '...': skill not found, skipping — Skill 'cmc-watchlist-scraper' not found.
```
Job status becomes `error` and `last_run_at` remains null.

**Root causes**:
1. Skill directory deleted or moved (e.g., git clean, repo prune)
2. Skill registered in `jobs.json` but `__init__.py` missing from skill directory
3. Skill requires dependencies not installed (import error during skill load)
4. Agent's skill search path misconfigured or not including the skill's parent directory
5. Typo in skill name in job definition

**Detection**:
```bash
# List all skills actually present for an agent
ls /root/.hermes/profiles/<agent>/skills/

# Cross-check against missing skill names from errors
grep 'Skill.*not found' /root/.hermes/profiles/<agent>/logs/errors.log | awk -F"'" '{print $2}' | sort -u
```

**Recovery**:
1. Locate the missing skill source (vault `05-Agency/` or external repo)
2. Restore skill directory structure under the agent's `skills/` path, ensuring:
   - `SKILL.md` exists
   - `__init__.py` exists (can be empty but must be present)
   - Any required scripts/references present
3. If skill is from a git repo, re-link or re-clone
4. Restart agent gateway to refresh skill registry cache
5. Re-enable the cron job if it was auto-paused
6. Verify next execution shows upcoming `next_run_at`

**Prevention**:
- Store skills in Obsidian vault with symlinks into agent profiles; vault sync ensures presence
- Periodically run skill registry integrity check
- Use `hermes skills list` to confirm skill is discoverable before creating cron jobs
- Pin critical skills as git submodules to prevent accidental deletion

**Related**: `references/2026-05-05-missing-skill-registry-cron-skip.md`

### Pattern: Cron Daemon Lifecycle Tracking via agent.log Markers

**Symptom**: Need to determine whether the cron daemon inside a gateway is alive and when it last started/stopped. `cron tick` log entries alone are ambiguous; they only indicate scheduler ticks, not daemon lifecycle.

**Key log markers** (Hermes internal cron):
- `Cron ticker started (interval=60s)` → daemon thread launched
- `Cron ticker stopped` → daemon thread exited (expected on shutdown; unexpected if process remains running)
- Absence of either over long periods while process is alive → scheduler may be hung or crashed silently

**Detection workflow**:
```bash
# Check last 50 lines for lifecycle events
tail -50 /root/.hermes/profiles/<agent>/logs/agent.log | grep -i 'Cron ticker'

# Count start/stop occurrences to detect restarts
grep -c 'Cron ticker started' /root/.hermes/profiles/<agent>/logs/agent.log
grep -c 'Cron ticker stopped' /root/.hermes/profiles/<agent>/logs/agent.log

# If stops > starts or last stop is recent while process alive → daemon died unexpectedly
```

**Interpretation**:
- Normal: `started` appears once after gateway launch; `stopped` appears only during gateway shutdown
- Degraded: `stopped` appears without subsequent `started` while gateway process still running → cron daemon crashed; restart gateway
- Healthy: `started` present, no recent `stopped`, and `[cron_<job_id>]` execution markers progressing on schedule

**Why this matters**: A gateway can have a live process but a dead cron scheduler (scheduler thread exception). Always verify both process liveness AND cron daemon activity via execution markers.

**Correlation check**: If `Cron ticker stopped` appears in logs but the gateway process continues running for hours, this is a **scheduler thread crash**. The agent will not execute any cron jobs until restarted. Action: `hermes gateway run --profile <agent> --replace`.

**Related case**: `references/2026-05-05-cron-daemon-lifecycle-tracking.md`

### Pattern: OPENROUTER API Key Not Propagated to Agent Process

**Symptom**: OPENROUTER_API_KEY present in `~/.hermes/.env` but agent logs show `OPENROUTER_API_KEY=YOUR_OPENR...` placeholder or fallback to other providers fails with "provider not configured". OpenRouter API calls return 401.

**Root cause**: The agent process environment does not contain the API key even though it's in the `.env` file. Common causes:
1. Gateway process started before `.env` was updated
2. `.env` file syntax error (duplicate keys, malformed line) prevents proper parsing
3. Agent's profile-specific `.env` overrides with blank value
4. Process environment snapshot does not include the key due to `env_passthrough` filtering

**Detection**:
1. Check `.env` content: `grep OPENROUTER_API_KEY /root/.hermes/.env` — ensure no `YOUR_...` placeholder
2. Verify agent process environment: `tr '\\0' '\\n' < /proc/$(jq -r .pid /root/.hermes/profiles/<agent>/gateway.pid)/environ | grep -i openrouter`
3. Compare — if key absent from process env but present in `.env`, the gateway needs restart
4. Check for duplicate OPENROUTER_API_KEY lines in `.env` (last occurrence wins; preceding entries may be blank)

**Recovery**:
1. Clean `.env` file — keep only one `OPENROUTER_API_KEY=actual_key` line; remove placeholder `YOUR_...` lines
2. Restart the agent's gateway process (or all gateways if using shared key)
3. Re-validate: check process environment again for the key
4. Test: trigger a simple LLM call or check `hermes model list` for successful catalog fetch

**Pitfall**: `.env` files are read only at process startup; no hot-reload. Any key rotation requires gateway restart for all affected profiles.

**Related pattern**: See "Process environment vs .env file validation" in this skill for the full diagnostic framework.

### Pattern: Duplicate Cron Execution Detection

**Symptom**: Agent runs the same cron job twice per scheduled interval (e.g., every 5 minutes instead of every 10). In session logs, two cron sessions appear with near-identical timestamps but different job ID prefixes (e.g., `cron_9ecfada01952_` and `cron_3258c64b_`).

**Root causes**:
1. **Two independent cron triggers** pointing at the same script (system crontab + internal Hermes cron registry)
2. **Orphaned global cron job** that also executes inside the agent's gateway
3. **Misconfigured schedule** in both system cron and agent cron registry with overlapping intervals

**Detection workflow**:
1. Count cron executions per interval: compute average interval between last 20 sessions. If average ≈ half the expected interval → duplicate execution likely
2. Identify distinct job ID prefixes in session filenames. Two different prefixes = two different cron sources
3. Check system crontab: `crontab -l` and `/var/spool/cron/crontabs/*` for direct script invocations
4. Check agent cron registry: `cat /root/.hermes/profiles/<agent>/cron/jobs.json` — look for jobs with schedules that match the observed frequency
5. Cross-reference: if both system cron and agent cron contain the same script path, you've found the duplicate

**Resolution**:
- Choose ONE scheduling mechanism (prefer Hermes internal cron over system crontab for agent scripts)
- Remove the system crontab entry if internal cron handles it
- OR disable/delete the internal Hermes cron job if system cron must be used (but Hermes cron provides better integration, retry, and delivery)
- After removing duplicate, verify execution frequency returns to expected interval

**YoYo-specific case**: The `defi-milestone-tracker.py` script is both:
- Launched via system crontab (root): `*/10 * * * * HERMES_HOME=/root/.hermes/profiles/yoyo python3 /root/.hermes/profiles/yoyo/scripts/defi-milestone-tracker.py`
- Registered as internal Hermes cron job ID `3258c64b` with schedule `*/10 6-23 * * *`

This causes two executions every 10 minutes (overlap at :00 and :05, :10 and :15, etc.). Duplicate execution should be resolved by removing one trigger. Recommend keeping internal Hermes cron (better integration, output handling, exit code processing) and removing system crontab entry.

**Investigation command template**:
```bash
# Find all sessions with specific job ID prefix
find /root/.hermes/profiles/<agent>/sessions -name "session_*<prefix>*.json" | wc -l

# Show execution timeline for a specific job ID prefix
for f in $(ls -t /root/.hermes/profiles/<agent>/sessions/session_*<prefix>*.json | head -20); do
  stat -c '%y' "$f"
done
```

**Pitfall**: Don't assume `cron_<job_id>` in session filename equals the job ID in jobs.json — session prefixes are derived from the gateway's execution context and may differ. The mapping requires cross-referencing agent logs or output directory timestamps.

**See also**: `references/2026-05-04-yoyo-duplicate-cron-detection.md` (session evidence and remediation steps).

### Pattern: Cron Job Syntax Error (JSON/Parse Failure)

**Symptom**: A cron job repeatedly fails with a parse error such as `'{' was never closed` or `JSONDecodeError`. The job's `last_status` is `error` and `last_error` contains the parse message. The job may appear scheduled but never produces valid output.

**Root causes**:
- Unterminated dictionary or string literal in the script (often from incomplete edit)
- Malformed JSON configuration file read by the script
- Script edited with non-ASCII quotes or invisible characters
- Incomplete copy-paste of code snippet

**Detection**:
- Check `errors.log` or `cron.log` for `JSONDecodeError`, `SyntaxError`, or `'{' was never closed`
- Inspect the job's `last_error` field in `/root/.hermes/profiles/<agent>/cron/jobs.json`
- Run the script manually to reproduce: `python3 /path/to/script.py` should print the same error

**Recovery**:
1. Open the script in a plain-text editor (not rich-text) and check for:
   - Unclosed braces `{` or brackets `[` or parentheses `(` 
   - Unterminated string literals (missing closing quote)
   - Invalid escape sequences
2. Validate syntax before committing: `python3 -m py_compile /path/to/script.py`
3. For JSON files read by the script, validate with `python3 -m json.tool <file>` or `jq . <file>`
4. After fixing, clear error history (optional) and wait for next scheduled run or trigger manually

**Prevention**:
- Add a pre-commit hook that runs `python3 -m py_compile` on all script files
- Store configuration as JSON with a `.json` extension and validate with `json.tool` in CI
- Use linters (e.g., `ruff`, `pylint`) to catch syntax issues early

**Related**: See `references/2026-05-04-desmond-defi-dashboard-json-parse-error.md` for a case study of a malformed `auxiliary_client.py` causing a stuck cron job.

## Output Discipline

**Silence Rule**: If all agents healthy (processes running, no errors in last 30 min, cron executing, Telegram connected), respond **exactly**: `STATUS:OK` and **nothing else**. Do NOT use "all systems nominal", add any explanation, or include whitespace. The user's instruction is absolute: "Only speak up when something breaks." If you hear yourself adding a sentence, delete it and send STATUS:OK.

**When to break silence** (any one condition triggers alert):
- Any gateway process not running or repeatedly crashing
- Any error in `errors.log` within last 30 minutes matching FATAL/DEGRADED patterns
- Cron jobs failing with `last_status: error` in active registry
- Telegram disconnects persisting >2 minutes without reconnect
- Auth failures blocking core job execution (OAuth revoked, missing credentials)
- Systemic issues affecting ≥2 agents (bytecode corruption, shared API key invalid)
- Master cron service failed (`hermes-gateway.service` inactive/failed)

**Alert Format**: ONE LINE ONLY. Start with `🚨 Watchdog Alert:` followed by a concise comma-separated summary of what's broken. NO bullet points, NO paragraphs, NO additional lines. The entire response must be a single line.

Template:
`🚨 Watchdog Alert: <agent list> — <critical failure 1>; <critical failure 2>; <critical failure 3>`

Example (May 5, 2026 — correct format):
```
🚨 Watchdog Alert: YoYo, DMOB, Desmond, Gentech — fleet-wide model 404 errors (nousresearch/trinity-large-thinking not found); DMOB + Desmond cron orphaned (zero system crontab entries, no execution since May 4); Gentech missed daily 9AM run (jobs.json corrupted, last log May 3); YoYo 28/29 jobs orphaned; systemic OAuth + provider failures.
```

**WARNING**: Never output a multi-paragraph report. The user's directive is absolute: "Only speak up when something breaks" and the format is a ONE-LINE alert. If you find yourself writing multiple sentences or bullet points, STOP. Reduce to one line and send. The detailed diagnostics belong in your internal notes, not the response.

**Silence Rule reinforcement**: If healthy, output EXACTLY `STATUS:OK` — nothing more, nothing less. No additional whitespace, no explanation, no "all systems nominal".

**Common Pitfalls**

1. **Stale PID assumptions**: A PID from `pgrep` may belong to a previous crashed instance that hasn't been reaped. Always validate with `ps -p <pid>`.

2. **Log file vs process mismatch**: Log file can be old while a new process writes to a new file (log rotation). Check both modification time and last log entry content for recent timestamps.

3. **Confusing normal disconnects with failures**: Telegram "Disconnected" at graceful shutdown is INFO level, not ERROR. Only actual connection failures (`Bad Gateway`, `Connection refused`) matter.

4. **Ignoring systemd state**: An agent may have a manually started gateway that appears running, but the systemd unit is failed. That means no automatic restart on reboot/failure.

5. **Cron storage vs execution**: `jobs.json` / `hermes cron list` shows what *should* run; cron.log and session files show what *did* run. Always check both.

6. **`pgrep` cache returning stale PIDs**: During rapid restart scenarios, `pgrep -f` can return PIDs that no longer exist (cached from previous process table scans). Always validate each PID with `ps -p <pid>` and discard any that don't resolve to a live process.

7. **Profile directory absence**: An agent may appear "down" because `~/.hermes/profiles/<agent>` was deleted, not because the gateway crashed. When no process is found, always check: `ls /root/.hermes/profiles/<agent>` before attempting restart. Missing profile requires recreation/restoration, not just process launch.

8. **Process-state vs systemd disagreement**: A gateway may appear running in `ps aux` while its systemd unit is `inactive (dead)` or `failed`. This indicates a manually started process outside systemd supervision, meaning no auto-restart on reboot. Always check BOTH `ps` and `systemctl --user status hermes-gateway-<profile>.service`.

9. **Cron list command incompleteness and unsupported flags**: `hermes cron list` may omit some scheduled jobs or show stale `last_run_at` values. Cross-check with raw `jobs.json` entries and verify actual execution via cron output files in `/root/.hermes/cron/output/` and session records in the agent's `sessions/` directory. **NOTE**: `hermes cron list --json` is NOT supported and will fail with "unrecognized arguments"; use text output or parse `jobs.json` directly.

10. **Shared credential propagation gaps**: Shared API keys (e.g., ElevenLabs) must be updated in ALL agent `.env` files, not just one. Validate across all profiles after rotation.

11. **Orphaned global cron jobs**: Jobs appearing in `hermes cron list` that originate from `/root/.hermes/cron/jobs.json` with `profile: null` are **orphaned** — they may show as active but lack an agent context and can fail silently or behave unpredictably. Always verify each active job's `profile` assignment; if null, migrate the job definition into the correct agent's profile cron config and remove it from the global file.

12. **Nous model support withdrawal**: A provider may deprecate a model (e.g., `stepfun/step-3.5-flash`) causing `ModelError: not supported` even with valid credentials. This can masquerade as an auth issue. Always read the exact error text — if it mentions model support, switch via `hermes model` to a currently supported model before investigating credentials further.

13. **Profile directory case mismatch**: The profile directory name on disk may use lowercase letters (e.g., `yoyo`) even when referenced as `YoYo`. When a health check fails to find logs or PID files at the expected path, read `gateway.pid` (JSON) from the presumed profile location to get the actual PID and infer the true profile directory. The PID file contains the canonical profile identity in its `argv` array. Always trust the PID file over display-name-based path construction.

14. **Cron daemon hang detection via job execution**: Absence of `Cron ticker started` messages does *not* prove the cron daemon is dead. The reliable indicator is the presence of periodic `[cron_<job_id>]` execution markers in `agent.log` matching the expected job frequency (e.g., auxiliary health job every 5 minutes). If the gateway process is alive but these execution markers have ceased appearing for longer than the maximum job interval, the cron scheduler thread is hung — restart the gateway to recover. Verify by `tail -200 agent.log | grep '\[cron_'` and check that timestamps progress at the expected cadence.

15. **Per-agent systemd unit divergence**: When profiles are launched manually with `--replace`, the global `hermes-gateway.service` unit shows `inactive (dead)` while per-agent units (`hermes-gateway-<profile>.service`) remain `active/running`. This is expected and not a failure. Do not treat the global unit's state as indicative of per-agent health; always check the per-agent unit or the process itself.

16. **Ignoring per-agent cron output directories**: Each agent maintains its own cron output directory at `/root/.hermes/profiles/<agent>/cron/output/`. These directories contain the actual evidence of job execution (output files). Relying solely on the global `/root/.hermes/cron/output/` directory can miss agent-specific activity or produce false negatives when per-agent cron jobs are running correctly but global output is stale. Always check the agent-specific output directory as the primary source of truth for that agent's cron health.

17. **Cron output files are `.md` not `.json`**: Cron job output files in `/root/.hermes/profiles/<agent>/cron/output/<job_id>/` are saved as `.md` (markdown) files with timestamped filenames like `2026-05-05_13-00-50.md`. Commands that look for `*.json` will find nothing. Use `ls -t .../*.md | head -1` or `grep -l ... *.md` to locate recent outputs.

18. **`execute_code` (Python interpreter) requires explicit `terminal` import**: When using the `execute_code` tool (Python code interpreter), `terminal()` is NOT available by default. You must explicitly import it: `from hermes_tools import terminal`. Failing to do so raises `NameError: name 'terminal' is not defined`. The `terminal` tool IS available by default in regular chat, but `execute_code` runs in a sandboxed interpreter that needs explicit imports.

## Recovery Sequence (when problems detected)

1. **Restart crashed gateways** (in dependency order if shared resources):
   ```bash
   pkill -f "hermes.*<agent>.*gateway"
   /usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile <agent> gateway run --replace
   ```

2. **Fix master service** (if failed):
   ```bash
   # Edit ExecStart path
   sudo sed -i 's|/root/.hermes/hermes-agent/venv/bin/python|/usr/local/lib/hermes-agent/venv/bin/python|' /root/.config/systemd/user/hermes-gateway.service
   systemctl --user daemon-reload
   systemctl --user restart hermes-gateway.service
   ```

3. **Clear bytecode corruption** (if marshal errors present):
   ```bash
   find /usr/local/lib/hermes-agent -name "*.pyc" -delete
   # Then restart ALL agent gateways to flush in-memory cache
   ```

4. **Rotate credentials** (TTS 401):
   - Update ElevenLabs API key in shared config or per-agent env
   - Add missing ANTHROPIC_TOKEN to DMOB `.env`

5. **Validate recovery**: Re-run this audit skill after each fix to confirm resolution.

## Reference: Key Commands

```bash
# Process verification
ps aux | grep hermes
pgrep -f 'hermes.*<agent>'
ps -p <pid> -o pid,stat,etime,cmd

# Log inspection
tail -200 /root/.hermes/profiles/<agent>/logs/gateway.log
tail -100 /root/.hermes/profiles/<agent>/logs/errors.log

# Service status
systemctl --user status hermes-gateway.service

# Cron job inspection
hermes cron list  # (or read jobs.json if CLI fails)
cat /root/.hermes/cron/jobs.json | jq '.jobs[] | select(.name|test("YoYo|DMOB|Desmond|Gentech"))'

# Bytecode cleanup
find /usr/local/lib/hermes-agent -name "*.pyc" -delete

# Gateway restart
/usr/local/lib/hermes-agent/venv/bin/python -m hermes_cli.main --profile <agent> gateway run --replace

# Profile directory verification
ls -la /root/.hermes/profiles/<agent>  # confirm existence before restart

# Bytecode corruption scan (find all marshal errors)
find /usr/local/lib/hermes-agent -name "*.pyc" -exec python3 -m py_compile {} \; 2>&1 | grep -i marshal

# Check specific .pyc magic number (Python 3.11 should be 33 0d 0d 0a)
xxd -l 4 /usr/local/lib/hermes-agent/agent/__pycache__/some_file.cpython-311.pyc

# Systemd user services overview
systemctl --user list-units --type=service --all | grep hermes

# Validate a specific PID exists
ps -p <pid> -o pid,stat,etime,cmd 2>/dev/null || echo "PID not found"

# Count recent disconnects in gateway.log (last 2h)
grep -i disconnect /root/.hermes/profiles/<agent>/logs/gateway.log | tail -10
```

### Support Files

#### Reference Case Studies
- `references/2026-05-02-watchdog-3-down.md` — May 2, 2026 run: 3/4 gateways down, systemd state divergence, bytecode corruption persistence, stale PID cache trap, recovery checklist
- `references/2026-05-04-fleet-alive-but-degraded.md` — May 4, 2026: All agents running but critically degraded; fleet-wide TTS quota exceeded, LLM auth tokens missing/expired, DMOB missing ANTHROPIC_TOKEN; demonstrates "alive ≠ healthy" diagnostic trap
- `references/2026-05-04-gentech-hermes-home-crash.md` — May 4, 2026: Gentech agent crashed within 10 seconds of startup with `KeyError: b'HERMES_HOME'` and `OSError: Input/output error`; root cause: HERMES_HOME environment variable missing from gateway launch; recovery: ensure HERMES_HOME exported before gateway run
- `references/2026-05-04-yoyo-nameerror-cron-crash.md` — YoYo `defi-milestone-tracker.py` NameError on line 307 (`elif eff>= 30:` undefined variable `eff`; corrected to `elif efficiency>= 30:`); debugging cron script crashes
- `references/2026-05-05-session-integrity-check.md` — May 5, 2026 fleet health check: all agents showing 0% session completion despite active processes; introduces session completeness ratio as higher-order health indicator and detection method via JSON field validation
- `references/2026-05-05-fleet-oauth-shared-credential-cascade.md` — **NEW** May 5, 2026: All four agents (YoYo, DMOB, Desmond, Gentech) share identical Nous OAuth credentials; access token expired 14:56 UTC; fleet-wide model 404 errors and cron paralysis; recovery requires per-agent `hermes model` re-authentication
- `references/2026-05-05-gentech-telegram-chat-not-found.md` — **NEW** Gentech-specific Telegram access failure: bot cannot reach configured chat (kicked, stale ID, or missing membership); detection via API `getChat` test; recovery: re-invite bot or correct chat ID
- `references/2026-05-05-missing-skill-registry-cron-skip.md` — **NEW** DMOB and Desmond cron jobs skipping because referenced skills (`cmc-watchlist-scraper`, `crypto-monitoring-cron`) are absent from skill registry; recovery: restore skills from vault or clone repos; restart gateways
- `references/2026-05-05-cron-daemon-lifecycle-tracking.md` — **NEW** DMOB and Desmond show "Cron ticker stopped" while gateway still running → silent scheduler thread crash; detection via lifecycle marker counting; recovery: gateway restart
- `references/2026-05-04-model-deprecation-fleet-failure.md` — May 4, 2026: Fleet-wide 404 Model Error due to misconfigured model ID prefix (`nousresearch/trinity-large-thinking` instead of `arcee-ai/trinity-large-thinking`); how to verify model existence via API, correct config across all agents
- `references/2026-05-04-model-deprecation-cascade-differential-recovery.md` — May 4, 2026 (evening): Follow-up health check reveals Desmond auto-recovered (stepfun fallback) while YoYo/DMOB/Gentech remained stuck; introduces stuck-timestamp cluster detection and session-based silence verification as diagnostic tools
- `references/2026-05-04-watchdog-1-silent-agents-model-misconfiguration.md` — May 4, 2026 20:50: Watchdog detects silent agent pattern (sessions with only user messages, no assistant) across YoYo/DMOB; Gentech self-check also failing; root cause: fleet-wide wrong model namespace; introduces session-role-based silence detection and verify_model_config.py script
- `references/2026-05-04-watchdog-2-model-misconfiguration-fleet-outage.md` — **This session**: Full fleet 404 outage; all agents blocked by `nousresearch/trinity-large-thinking` misconfiguration; zero task completions; differential recovery detection (DMOB/Desmond auto-failed over, YoYo/Gentech stuck); introduces last-log-entry health determination, hourly error density trend analysis, and config-vs-global-default diffing technique
- `references/2026-05-04-watchdog-1-silent-agents-model-misconfiguration.md` — May 4, 2026 20:50: Watchdog detects silent agent pattern (sessions with only user messages, no assistant) across YoYo/DMOB; Gentech self-check also failing; root cause: fleet-wide wrong model namespace; introduces session-role-based silence detection and verify_model_config.py script
- `references/2026-05-03-fleet-health-audit.md`
- `references/2026-05-04-missing-cron-configuration.md` — May 4, 2026: DMOB and Desmond profiles contain monitoring scripts but have no crontab entries or internal cron registration; zero scheduled work execution despite active gateways
- `references/2026-05-04-yoyo-duplicate-cron-detection.md`
- `references/2026-05-03-oauth-state-sync-recovery.md`
- `references/2026-05-02-fleet-collapse.md`
- `references/2026-05-03-auth-revocation-cascade.md`
- `references/2026-05-03-oauth-revocation-cascade-env-load-gap.md`
- `references/2026-05-04-evening-auth-revocation-api-block-cascade.md`
- `references/2026-05-03-oauth-revocation-cascade-path-fragmentation.md`
- `references/2026-05-03-2300-watchdog-auth-cascade.md`
- `references/2026-05-04-model-misconfiguration-cascade-and-cron-silence.md`
- `references/2026-05-05-cron-execution-missing-configuration.md` — May 5, 2026: DMOB, Desmond, Gentech have running gateways but zero cron execution since May 4; YoYo executing but with AAE config path error; demonstrates detection of missing cron triggers and HOME path fragmentation
- `references/2026-05-05-session-schema-drift-false-positive.md` — **NEW** May 5, 2026: Session integrity check reported 0% fleet-wide completion — turned out to be schema drift (old keys `status`/`created_at` no longer exist; current format uses `session_start`/`last_updated`/`messages`). Documents schema probe technique, required_keys update, and false positive prevention
- `references/2026-05-05-watchdog-format-violation-multi-paragraph-report.md` — **NEW** May 5, 2026: Watchdog delivered multi-paragraph report instead of required one-line alert; documents correct output format and detection guardrail
- `references/2026-05-05-jobsjson-structure-discovery.md` — **NEW** May 5, 2026: Discovered `jobs.json` uses dict-with-jobs-key structure, not direct array; code assuming `jobs[:5]` crashes with `TypeError: unhashable type: 'slice'`; adds guard pattern `data.get('jobs', [])`
- `references/2026-05-05-missing-system-user-desmond.md` — **NEW** System user `desmond` absent from `/etc/passwd` despite active gateway service; indicates manual launch or user deletion; breaks systemd supervision and credential isolation
- `references/2026-05-05-zero-cron-output-active-ticker.md` — **NEW** Fleet-wide pattern: ticker alive (.tick.lock fresh) but cron/output/ directories empty; auth+model failures block dispatcher before output file creation; detection recipe included
#### Automation Scripts
- `scripts/check_hermes_home.py` — Validates HERMES_HOME environment variable in gateway process; detects missing env launches
- `scripts/detect_duplicate_cron.py` — Analyze an agent's cron session history to detect duplicate/overlapping cron triggers; reports distinct job ID prefixes and average execution intervals; flags when average interval ≈ half of expected (indicates double execution)
- `scripts/fix-model-id-misconfiguration.py` — Batch-update agent config.yaml files to replace incorrect model ID prefixes (e.g., `nousresearch/trinity-large-thinking` → `arcee-ai/trinity-large-thinking`); validates replacement against OpenRouter catalog before writing
- `scripts/verify_model_config.py` — Verify each agent's configured model ID against known-good values and/or OpenRouter live catalog; supports `--check` (report only), `--fix` (batch update), and `--catalog` (show live catalog matches). Primary tool for resolving model namespace misconfiguration incidents.
- `scripts/check_session_integrity.py` — Audit session completeness ratio across agents (status + created_at presence); exit 0=healthy (≥80%), 1=degraded, 2=critical; integrates with Watchdog cron
- `scripts/validate_alert_format.py` — **NEW** Pre-send validator for Watchdog cron output; ensures response matches required one-line format (`STATUS:OK` or `🚨 Watchdog Alert: ...`); catches multi-paragraph violations before delivery; returns exit 1 with diagnostic if format incorrect.

## Related Skills

- `agent-coordination` — For multi-agent orchestration beyond health checks
- `system-health` — System-level diagnostics (disk, memory, services)
