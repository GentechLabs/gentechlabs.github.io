# Reference: 2026-05-02 Watchdog Health Sweep — Cron Execution Failure & Multi-Provider Credential Cascade

**Date:** 2026-05-02  **Trigger:** YoYo Watchdog cron executing health check across all agent profiles.  **Scope:** Full system inspection — cron metadata, output directories, agent logs, gateway status, process table, disk space.

---

## Executive Summary

All four agent gateways were **running and Telegram-connected** at sweep start. No cron jobs had executed in the previous 2+ hours despite cron ticker active in all gateways. `jobs.json` metadata showed `last_run_at: null` across all scheduled jobs and `cron/output/` directories were empty. Multiple credential failures discovered: ElevenLabs TTS invalid API key (DMOB, Desmond), missing Anthropic credentials (DMOB cron job), model catalog 404 (Gentech), and GitHub Copilot token type rejection.

**Root cause:** Cron scheduler not dispatching jobs despite ticker running — jobs remained in `scheduled` state with stale `next_run_at` values but no execution. Concurrent credential cascades degrading non-cron agent functionality.

---

## Chronology of Observations (2026-05-02 00:11–00:22 UTC)

| Time | Observation | Profile |
|------|-------------|---------|
| 00:11 | Gateway processes confirmed running for all 4 profiles via `ps aux` | All |
| 00:12 | `cron/output/` directories empty; no files modified in previous 2h | All |
| 00:13 | `jobs.json` last_updated timestamp: 2026-04-30 (unchanged for 2 days) | All |
| 00:14 | All jobs show `last_run_at: null`, `last_status: null`, `next_run_at` in past | All |
| 00:15 | Cron ticker active in gateway logs (60s interval) | All |
| 00:16 | Zero files in `/root/.hermes/cron/output/` (global output dir empty) | System |
| 00:17 | Agent errors tail: Gemini marshal errors present but subsiding (corruption from 2026-05-01 still clearing) | YoYo, Gentech |
| 00:18 | DMOB errors: ElevenLabs TTS 401 ×3; "No Anthropic credentials found" ×1 (cron job failure) | DMOB |
| 00:19 | Desmond errors: ElevenLabs TTS 401 ×3 | Desmond |
| 00:20 | Gateway shutdown/restart sequence logged for DMOB (23:20) and Desmond (23:20) — manual intervention | DMOB, Desmond |
| 00:21 | Gentech errors: Model 404 `minimax/minimax-m2.5:free` not found (OpenRouter) | Gentech |
| 00:22 | GitHub Copilot warning: Classic PAT (ghp_*) rejected — OAuth/fine-grained PAT required | System |

---

## Failure Signatures Documented

### A. Cron Scheduler Stasis — Ticker Running, Jobs Not Dispatching

**Symptoms:**
- `cron ticker started (interval=60s)` present in gateway logs
- `jobs.json` shows enabled jobs with `next_run_at` in the past
- `last_run_at` remains `null` across all jobs
- `/root/.hermes/profiles/<profile>/cron/output/<job_id>/` directories empty or contain only very old files
- `hermes cron status` reports "✓ Gateway is running — cron jobs will fire automatically" but next_run_at never advances

**Diagnostic commands:**
```bash
# 1. Inspect raw jobs metadata (all profiles)
for p in yoyo dmob desmond gentech; do
  echo \"=== $p ===\"
  python3 -c \"\nimport json, os\npath = f'/root/.hermes/profiles/{p}/cron/jobs.json'\nwith open(path) as f: data = json.load(f)\nfor j in data.get('jobs', []):\n    if not j.get('enabled'): continue\n    print(f\\\"{j['id'][:12]} | {j['name'][:45]:<45} | next={j.get('next_run_at','?')} | last={j.get('last_run_at','?')} | status={j.get('last_status','?')}\\\")\n\" 2>/dev/null || echo 'FAIL: cannot parse jobs.json'\ndone

# 2. Check cron output directory mtime (should be recent if jobs firing)
find /root/.hermes/profiles -path '*/cron/output/*/*.md' -mmin -120 -ls 2>/dev/null | wc -l

# 3. Search gateway logs for cron ticker AND any job execution log lines
grep -E 'Cron ticker|running job|job executed|cronjob' /root/.hermes/profiles/*/logs/gateway.log | tail -30

# 4. Check if cron subsystem is actually attached to the gateway
/usr/local/bin/hermes cron status 2>/dev/null || echo 'cron command unavailable'

# 5. Verify the cron ticker thread is alive in each gateway process
ps -o pid,cmd -C python3 | grep hermes | grep gateway
# Then check each gateway log for \"Cron ticker started\" within the last 5 minutes
```

**Probable causes (ranked):**
1. **Gateway zombie** — process alive but scheduler thread dead/crashed. Look for `Cron ticker stopped` without a subsequent `started`. Fix: `hermes gateway run --profile <p> --replace`.  
2. **Cron daemon not loaded** — Hermes main process running but cron subsystem not initialized (older versions). Check for `cron.scheduler` messages in `errors.log`. Fix: restart gateway with explicit `--cron` flag or upgrade.  
3. **Job metadata cache desync** — `jobs.json` edited manually or corrupted; in-memory cache not refreshed. Fix: restart gateway (forces reload).  
4. **System clock jump** — `next_run_at` computed with old system time; after NTP sync the computed times are all in the past but ticker logic has a bug skipping them. Fix: check `date`; if recently adjusted, restart gateway.  
5. **Timezone confusion** — `next_run_at` stored as UTC but gateway interpreting as local (or vice versa). If system timezone changed recently, computed next run may be far in future even though value looks like \"past\". Fix: verify `TZ` env; restart.

**Workaround (immediate):** Restart all gateways simultaneously:
```bash
hermes gateway run --profile yoyo --replace
hermes gateway run --profile dmob --replace
hermes gateway run --profile desmond --replace
hermes gateway run --profile gentech --replace
```

**Verification after restart:** Within 1× schedule interval, `cron/output/<job_id>/` should contain at least one new `.md` file with timestamp ≥ restart time.

---

### B. Credential Cascade Failures — TTS and Anthropic

#### B1. ElevenLabs TTS Invalid API Key (401)

**Error (appears 3× per agent):**
```
elevenlabs.core.api_error.ApiError: status_code: 401, body: {'detail': {'status': 'invalid_api_key', 'message': 'Invalid API key'}}
```

**Profiles affected:** DMOB, Desmond (observed 2026-05-01 17:17–17:25, repeated May 1 evening)

**Fix:**
1. Check current key: `echo $ELEVENLABS_API_KEY` (likely set in `~/.hermes/.env` or profile config)
2. Rotate key in ElevenLabs dashboard → copy new key
3. Update in Hermes: edit `~/.hermes/.env` or profile-specific environment, then restart affected gateways
4. Verify: run a TTS tool call manually to confirm success

**Note:** This is a **service-level revocation/invalidation**, not a rate limit. Old key must be replaced; retries will not recover.

#### B2. Missing Anthropic Credentials

**Error:**
```
RuntimeError: No Anthropic credentials found. Set ANTHROPIC_TOKEN or ANTHROPIC_API_KEY, run 'claude setup-token', or authenticate with 'claude /login'.
```

**Context:** Cron job "Defi Milestone" failed to execute (job id `64cfa447b338` in DMOB profile). Job requires Claude model; Anthropic token absent.

**Fix:**
```bash
claude /login          # interactive OAuth flow (preferred)
# OR
export ANTHROPIC_API_KEY=<your-key>
hermes gateway run --profile dmob --replace
```

**Scope:** Any job requesting `claude-*` models will fail until token is present.

---

### C. Model Catalog Unavailability (HTTP 404)

**Error:**
```
2026-05-01 23:10:18,577 ERROR ... Non-retryable client error: Error code: 404 -
{'status': 404, 'message': "Model 'minimax/minimax-m2.5:free' not found.
The requested model does not exist in our configuration or OpenRouter catalog."}
```

**Profile:** Gentech (session `20260501_231017_aa0d51`, also `20260501_231015_e30868`)

**Impact:** Any job explicitly requesting `minimax/minimax-m2.5:free` fails immediately with empty response.

**Fix:**
1. `hermes models` — list available models on current provider (OpenRouter)
2. Substitute a valid free-tier model: `stepfun/step-3.5-flash`, `google/gemini-3-flash-preview`, or `mistralai/mistral-small-3.1-24b-instruct:free`
3. Update job configuration in `jobs.json` or prompt template to use new model string
4. Restart gateway if model is cached in session

---

### D. GitHub Copilot Token Type Rejection

**Error:**
```
2026-05-01 23:16:16,804 WARNING hermes_cli.copilot_auth: Token from GITHUB_TOKEN is not supported: Classic Personal Access Tokens (ghp_*) are not supported by the Copilot API.
Use one of:
→ copilot login or hermes model to authenticate via OAuth
→ A fine-grained PAT (github_pat_*) with Copilot Requests permission
→ gh auth login with the default device code flow (produces gho_* tokens)
```

**Profile:** System-wide (Gentech, DMOB logs)

**Fix:**
```bash
gh auth login  # produces gho_* token (recommended)
# OR generate a fine-grained PAT with "Copilot Requests" permission and export GITHUB_TOKEN
```

---

## Cron Job Execution State Snapshot (2026-05-02 00:14)

All jobs in `scheduled` state, none having executed since Apr 30:

| Profile | Job Name | Job ID (prefix) | Schedule | next_run_at | last_run_at | last_status |
|---------|----------|----------------|----------|-------------|-------------|-------------|
| gentech | HQ Daily Update | c578000c1d4a | 09:00 UTC | 2026-04-30 09:00 | null | null |
| yoyo | LP Watchlist Check | a47474bb0f0c | 06/12/18 UTC | 2026-04-30 06:00 | null | null |
| dmob | Labs Daily Standup | ec74c26ad123 | 08/20 UTC | 2026-04-30 08:00 | null | null |
| desmond | Creative Sync | 64cfa447b338 | 07/19 UTC | 2026-04-30 07:00 | null | null |

**Conclusion:** Cron dispatch system non-functional across all profiles despite gateways and tickers running.

---

## Additional Systemic Issues

### Disk Space Pressure
`/dev/sda1` at 82% used (157G/193G). Not yet critical but correlated with earlier SessionDB warning (`database or disk is full` on 2026-05-01 10:17:45). Monitor `/tmp` and `/var/log` as well; clean old hermes caches if needed.

### Gemini Native Adapter Corruption (Carryover from 2026-05-01)
`EOFError: marshal data too short` still appearing in agent logs, frequency reduced from peak but not fully cleared. Requires confirmation that corrupted `.pyc` has been regenerated on all gateways.

**Validate fix:**
```bash
# Should produce NO output (exit 0)
python3 -c "import importlib; importlib.invalidate_caches(); import agent.gemini_native_adapter" 2>&1
# Check .pyc size is now ~47KB
find /usr/local/lib/hermes-agent/agent/__pycache__ -name '*gemini_native_adapter*.pyc' -exec ls -lh {} \;
```

---

## Recovery Actions Taken (Watchdog)

1. **Compiled this reference** — documented new failure signatures
2. **Flagged all cron jobs as stale** — all 4 profiles require gateway restart to revive scheduler
3. **Noted credential failures** — DMOB/Desmond TTS key invalid; DMOB Anthropic missing; Gentech model 404; system Copilot token type invalid
4. **Confirmed no cron output produced in last 2h** — execution gap ≥ schedule interval × 2 for every job

---

## Lessons Learned (New)

1. **Ticker ≠ Scheduler** — `Cron ticker started` only means the heartbeat thread is alive. It does NOT guarantee jobs are being dispatched. Always cross-check `cron/output/` for actual artifacts.
2. **Empty `cron/output/` is a canary** — If the directory is empty (or newest file >2× interval old) while ticker runs, the scheduler thread is likely dead or desynced from the job queue. Restart gateway.
3. **Credential cascades are multi-provider** — One broken API key (ElevenLabs) or missing token (Anthropic) can silently fail multiple jobs. Audit all external service keys weekly.
4. **Model string 404s are silent on some gateways** — Not all gateways log the 404 visibly; the job just returns empty response. If a job suddenly starts erroring with empty output, check provider catalog immediately.
5. **GitHub Copilot classic PAT dead** — ghp_* tokens no longer accepted. Enforce fine-grained or OAuth tokens in skill-env setup scripts.
6. **Gateway restart scope matters** — When core bytecode corruption is suspected, restart **all** gateways, not just the profile showing errors, because shared install means all processes have the bad `.pyc` cached in memory.

---

## Watchdog Decision Log (2026-05-02)

| Agent | Cron Health | Credential Health | Other | Verdict |
|-------|-------------|-------------------|-------|---------|
| YoYo | ❌ Stale (no runs Apr 30–May 2) | ⚠️ Gemini marshal errors (clearing) | — | **ALERT** |
| DMOB | ❌ Stale + ❌ Missing Anthropic cron credential | ❌ ElevenLabs TTS 401 | Gateway restarted 23:20 | **ALERT** |
| Desmond | ❌ Stale | ❌ ElevenLabs TTS 401 | Gateway restarted 23:20 | **ALERT** |
| Gentech | ❌ Stale | ❌ Model 404 (minimax) | Gemini marshal errors | **ALERT** |

**System-wide:** Cron dispatch non-functional; credential cascade affecting TTS and Anthropic-dependent jobs; model catalog mismatch; Copilot token deprecated.

**Action required:** Restart all gateways → rotate ElevenLabs key → add Anthropic token → fix minimax model string → upgrade Copilot auth.

---
