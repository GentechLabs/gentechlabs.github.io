---
name: hermes-agent-environment-debugging
version: "1.0.0"
description: Diagnose missing credential issues caused by Hermes env_loader not loading profile-specific .env files — systematic environment variable debugging for gateway processes
trigger:
  - missing credentials
  - 401 unauthorized errors
  - environment not loaded
  - profile .env ignored
  - gateway process environment check
  - credential debugging
steps:
  - Verify process environment via /proc/<pid>/environ (NOT from profile .env file contents)
  - Map env_loader.load_hermes_dotenv() actual behavior: loads only ~/.hermes/.env and <cwd>/.env, NEVER profile .env
  - Check presence of credentials in ~/.hermes/.env; if absent, profile .env contents are irrelevant at runtime
  - Identify gap: profile .env exists but process environ lacks vars → classic symptom of this bug
  - Remediate by copying keys to ~/.hermes/.env or exporting in gateway startup shell
  - Restart gateways to pick up new environment
  - Verify via /proc/<new-pid>/environ that keys are present
  - Check logs for disappearance of 401/No credentials errors
pitfalls:
  - Profile .env files are backup/export only; they are NOT read by gateway processes at runtime (env_loader does not reference profile_dir/.env)
  - hermes model manages Nous Portal OAuth, NOT environment variables — does not fix missing ANTHROPIC_API_KEY etc.
  - Systemd service files for hermes gateways are not installed by default, so EnvironmentFile= overrides won't work unless manually created
  - Cron jobs inherit environment from gateway process; fixing gateway env fixes cron automatically
  - Process environment is a snapshot at fork/exec time; modifying .env files does NOT affect already-running processes
  - sudo or su can reset environment; always check the actual process environ via /proc, not shell variables
  - The env_loader sanitizes corrupted .env files but still only applies to global locations, not per-profile
  - Missing NOUS_TOKEN shows as "Hermes is not logged into Nous Portal" — re-auth via hermes model is separate from .env keys
references:
  - references/env_loader-load-order.md
scripts:
  - scripts/check-process-env.sh
  - scripts/verify-credentials-loaded.sh
---
# Hermes Agent Environment Debugging

**Scope**: Gateway credential failures where profile `.env` files exist but variables are absent from the running process environment.

---

## Problem Statement

Hermes agents (YoYo, DMOB, Desmond, Gentech) exhibit credential-related errors:
- `401 Unauthorized` from ElevenLabs, Anthropic, OpenAI
- `RuntimeError: No Anthropic credentials found`
- `RuntimeError: Hermes is not logged into Nous Portal`
- `elevenlabs.core.api_error.ApiError: status_code: 401`

**Despite**: Profile-specific `.env` files (`~/.hermes/profiles/<agent>/.env`) contain valid API keys.

**Root cause**: The `env_loader.load_hermes_dotenv()` function ONLY loads:
- `~/.hermes/.env` (global user environment)
- `<cwd>/.env` (development fallback, only if global missing)

It **never loads** `~/.hermes/profiles/<agent>/.env`. Consequently, gateway processes inherit the calling shell's environment, which lacks these keys.

---

## Diagnostic Flow

### Step 1: Confirm Missing Credentials in Process
```bash
# Get gateway PID
ps aux | grep hermes_cli.main | grep gateway

# Read actual process environment
sudo cat /proc/<pid>/environ | tr '\0' '\n' | grep -E 'NOUS|ANTHROPIC|ELEVENLABS|OPENAI|OPENCODE'
```
**If output shows none of these keys** → environment not loaded.

### Step 2: Check What .env Files Exist
```bash
ls -la ~/.hermes/.env
ls -la ~/.hermes/profiles/yoyo/.env
cat ~/.hermes/profiles/yoyo/.env | head -20
```
**Expected anomaly**: Profile `.env` has keys; global `~/.hermes/.env` does not.

### Step 3: Check Gateway Startup Context
```bash
ps -o pid,cmd -p <pid>
# Command shows: python -m hermes_cli.main --profile yoyo gateway run --replace
# Gateway inherits env from parent shell (likely cron or interactive)
```
If launched from a shell without `source ~/.hermes/profiles/yoyo/.env`, keys are absent.

### Step 4: Verify Env Loader Code Path
```bash
grep -r "load_hermes_dotenv" /usr/local/lib/hermes-agent/hermes_cli/ | head -5
# hermes_cli/main.py calls load_hermes_dotenv(project_env=PROJECT_ROOT / ".env")
```
No code path loads `profile_dir/.env` into the gateway environment.

---

## Remediation Paths

### Path A: Ad-hoc Fix (Session-Local)
For immediate testing without file changes:
```bash
# In same shell that will launch gateway:
export $(grep -v '^#' ~/.hermes/profiles/yoyo/.env | xargs)
# OR selectively:
export ANTHROPIC_API_KEY=$(grep ANTHROPIC ~/.hermes/profiles/yoyo/.env | cut -d= -f2)

# Then start gateway
hermes gateway run --profile yoyo --replace
```
**Limitation**: Lost on shell exit.

### Path B: Permanent Fix — Populate ~/.hermes/.env
```bash
# Append missing keys to global .env
cat ~/.hermes/profiles/yoyo/.env >> ~/.hermes/.env

# De-duplicate if needed
awk -F= '!seen[$1]++' ~/.hermes/.env > /tmp/.env.clean && mv /tmp/.env.clean ~/.hermes/.env

# Restart all gateways (they need to re-fork to pick up new env)
pkill -f "hermes_cli.main.*gateway"
# Gateways auto-restart via cron or manual:
hermes gateway run --profile yoyo --replace &
hermes gateway run --profile dmob --replace &
hermes gateway run --profile desmond --replace &
hermes gateway run --profile gentech --replace &
```
**Note**: `~/.hermes/.env` takes precedence; keys here are always loaded.

### Path C: Systemd Unit Override (Production)
If systemd units exist (not currently installed):
```bash
systemctl edit hermes-gateway-yoyo.service
# Add:
[Service]
EnvironmentFile=/root/.hermes/profiles/yoyo/.env
# Reload and restart
systemctl daemon-reload
systemctl restart hermes-gateway-yoyo.service
```

---

## Environment Variable Precedence (Hermes env_loader)

| Source | Priority | Loaded by env_loader? | Affects gateway? |
|--------|----------|----------------------|------------------|
| Shell exports (at gateway launch) | 1 (highest) | N/A (already in environ) | YES — inherited |
| `~/.hermes/.env` | 2 | YES | YES — loaded by env_loader |
| `<cwd>/.env` (project fallback) | 3 | YES (only fills missing) | YES — loaded by env_loader |
| `~/.hermes/profiles/<agent>/.env` | N/A | NO | **NO** — never loaded |

**Conclusion**: Only sources 1–2 reliably affect gateway processes. Source 3 is ignored.

---

## Validation Checklist

After remediation, verify:
- [ ] `sudo cat /proc/<new-pid>/environ | tr '\0' '\n'` shows `NOUS_TOKEN`, `ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`
- [ ] `grep "401\|No Anthropic credentials" ~/.hermes/profiles/yoyo/logs/errors.log` shows no new occurrences in last 10 minutes
- [ ] TTS tool works: `hermes run --profile yoyo "use tts_tool to say credential test"`
- [ ] Cron job executes: wait for next scheduled run or manually trigger
- [ ] No `Refresh session has been revoked` errors

---

## Chronic Symptoms Table

| Symptom | Misdiagnosis | Actual Cause | Fix |
|---------|--------------|--------------|-----|
| Profile `.env` has keys but 401 persists | "Wrong API key value" | Keys never loaded into process environ | Copy keys to `~/.hermes/.env` |
| `hermes model` shows connected but tools fail | "Provider outage" | Missing ANTHROPIC/OPENAI keys in environ | Populate global `.env` |
| All agents fail simultaneously | "Shared provider down" | Shared root cause: global `.env` missing | Restore global env |
| Cron jobs say "not logged in" despite `hermes model` working | "Cron broken" | Cron inherits gateway environ lacking NOUS_TOKEN | Fix gateway env |
| Changing profile `.env` has no effect | "Caching bug" | Profile `.env` not in env_loader path | Edit `~/.hermes/.env` |
| Env vars set in shell but gateway doesn't see them | "Gateway ignores env" | Launched from different shell | Export in same shell before launch |

---

## Monitoring & Alerting

Add to `hermes-agent-health-check` skill alert rules:
```
If: errors.log contains 'status_code: 401' + 'invalid_api_key' ≥ 3 times in 5 min
Then: Check process environ for missing *_API_KEY
      Alert: "Agent <name> missing API credentials"

If: ~/.hermes/profiles/<agent>/.env exists AND size > 100 bytes
    AND process environ lacks ANTHROPIC/ELEVENLABS keys
Then: "Profile .env not loaded — fix env_loader or populate ~/.hermes/.env"
```

---

## Session Notes (May 2, 2026 Watchdog Health Check)

**Discovery**: All 4 agents (YoYo, DMOB, Desmond, Gentech) showed 186-279 ElevenLabs 401 errors, Anthropic credential failures, and "not logged into Nous Portal" cron blocks.

**Root cause investigation**:
- Profile `.env` files confirmed present with API keys
- Process `/proc/<pid>/environ` showed ZERO credential variables
- `~/.hermes/.env` missing ANTHROPIC_API_KEY, ELEVENLABS_API_KEY, OPENAI_API_KEY, NOUS_TOKEN
- `env_loader.py` examined: loads only global `~/.hermes/.env` and project `.env`, never profile `.env`
- `hermes model` manages OAuth but does NOT populate environment variables

**Secondary findings**:
- Disk pressure at 82% contributed to SQLite and bytecode corruption
- Coordinated gateway restart event on May 1 23:20 UTC
- Network errors: Telegram flood control (Desmond), disconnects (Gentech)
- Stuck error loops: same 401 repeated 10-99+ times per agent

**Corrective actions taken**: None (diagnostic-only session). Recommendations issued to Gentech team.

**Key insight for future**: Always check process environment when troubleshooting credential errors; never assume `.env` file presence equals loaded environment.