---
name: gentech-agent-reactivation
description: Bring all YoYo/DMOB/Desmond agent gateways and cron jobs back online — full restoration workflow for "agents off today" situations, including Nous Portal auth revocation recovery
triggers:
  - agent downtime recovery
  - cron job bulk-resume
  - gateway reactivation
  - post-maintenance startup
  - Nous Portal auth revocation
  - "Refresh session has been revoked" error recovery
---

# Reactivate Gentech Agent Ecosystem After Downtime

Bring all YoYo/DMOB/Desmond agent gateways and cron jobs back online — full restoration workflow for "agents off today" situations.

## When to Use

- Agent watchdog reports gateways down or not responding
- After system reboot or maintenance window
- Cron jobs paused (mass pause detected)
- Agents need to be brought back online after intentional downtime

## Prerequisites

- Hermes agent installed at `~/.hermes/hermes-agent`
- Agent profiles exist at `~/.hermes/profiles/{yoyo,dmob,desmond}`
- Main gateway daemon running (`hermes gateway run`)
- Agent watchdog script at `~/.hermes/scripts/agent-watchdog.sh`
- Cron jobs managed via `hermes cron`

## Steps

### 1 — Check Gateway Status

```bash
# Check main Hermes status
hermes status

# Inspect running processes
ps aux | grep -E "(cron|hermes|agent)" | grep -v grep

# Check cron job list to see paused state
hermes cron list
```

**What you're looking for:** Gateway processes absence, many jobs with `"state": "paused"` or `"enabled": false`.

### 2 — Resume Paused Cron Jobs

Identify all paused jobs and resume them:

```python
import json
with open('/root/.hermes/cron/jobs.json', 'r') as f:
    data = json.load(f)
paused_ids = [j['id'] for j in data.get('jobs', []) if not j.get('enabled', True) or j.get('state') == 'paused']
print(f"Paused jobs to resume: {len(paused_ids)}")
```

Then resume in parallel using `cronjob` tool or in shell:

```bash
for job_id in $(jq -r '.jobs[] | select(.enabled == false or .state == "paused") | .id' ~/.hermes/cron/jobs.json); do
  hermes cron resume "$job_id" &
done
wait
```

Or using the tool directly in parallel tool calls.

### 3 — Start Agent Gateway Processes

Each agent runs as a separate gateway with its own profile HOME:

```bash
AGENTS=(yoyo dmob desmond)
for agent in "${AGENTS[@]}"; do
  profile_home="$HOME/.hermes/profiles/$agent"
  cd "$profile_home"
  HERMES_HOME="$profile_home" nohup \
    $HOME/.hermes/hermes-agent/venv/bin/python3 \
    $HOME/.local/bin/hermes gateway run \
    >> "$profile_home/logs/gateway.out" 2>&1 &
  sleep 2  # stagger starts
done
```

**Key detail:** `HERMES_HOME` must be set to the profile directory; `gateway run` must be invoked, not just `hermes` alone.

### 4 — Verify via Watchdog

Use the existing watchdog script (runs every 15m by cron) to validate:

```bash
bash ~/.hermes/scripts/agent-watchdog.sh
```

Expected output:
```
=== Agent Watchdog Summary ===
All agents healthy.
✅ yoyo running (PID XXXX)
✅ dmob running (PID XXXX)
✅ desmond running (PID XXXX)
```

The watchdog checks both process liveness and gateway state.

### 5 — Model Name Resolution & Verification (Critical!)

If gateways fail with **"Model 'X' not found"** errors, the model identifier in `config.yaml` doesn't match the provider's catalog.

**Diagnose the exact model name via Nous API catalog:**
```bash
curl -s https://inference-api.nousresearch.com/v1/models | jq -r '.data[].id' | grep step
```

**Hermes Step model naming on Nous:**
- Incorrect: `step-3.5-flash` (404: not found)
- Incorrect: `nous/step-3.5-flash` (404: no such model)
- Correct: `stepfun/step-3.5-flash` ✓

**Why the confusion:** The agent auto-detects `provider: nous` from `NOUS_API_KEY` env var and the OpenRouter-style endpoint, but the model catalog uses the `stepfun/` namespace prefix. The model field must be the full catalog ID including provider namespace.

**Fix — Update all agent configs:**
```yaml
# ~/.hermes/profiles/{yoyo,dmob,desmond}/config.yaml
model: stepfun/step-3.5-flash
# providers: {}  (leave empty — agent resolves from NOUS_API_KEY env)
```

Then **fully restart gateways** to pick up config change:
```bash
pkill -f 'hermes gateway run'
rm -f ~/.hermes/profiles/*/gateway.pid
rm -f ~/.local/state/hermes/gateway-locks/telegram-bot-token-*.lock
# Sequential restart
for agent in yoyo dmob desmond; do
  HERMES_HOME=~/.hermes/profiles/$agent hermes gateway run &
  sleep 4
done
```

**Log verification tip:** `gateway.out` may show stale content from previous runs (old error banners that don't flush). Use `agent.log` to confirm current state — look for `✓ telegram connected` and the absence of recent ERROR lines.

---

### 6 — Detect & Fix Nous Portal Auth Revocation

If gateways are running but cron jobs are failing with **"Refresh session has been revoked"**, the Nous Portal OAuth session needs renewal:

```bash
# Check recent cron failures
hermes cron list | grep -i "error\|failed"

# Or inspect agent logs
tail -50 ~/.hermes/profiles/yoyo/logs/gateway.out | grep -i "refresh\|revoked\|auth"
```

**Fix — Re-authenticate with Nous:**
```bash
# MUST be run interactively (not via tools/automation)
hermes model
```
This opens OAuth flow in browser. Complete login at https://portal.nousresearch.com.

**Propagate fresh credentials to all agent profiles:**
```bash
# After hermes model succeeds, copy updated auth.json to each profile
cp ~/.hermes/auth.json ~/.hermes/profiles/yoyo/auth.json
cp ~/.hermes/auth.json ~/.hermes/profiles/dmob/auth.json
cp ~/.hermes/auth.json ~/.hermes/profiles/desmond/auth.json

# Restart agent gateways to pick up new credentials
# (kill + re-run gateway start commands from Step 3, or use watchdog)
```

**Why this happens:** Nous Portal refresh tokens have limited lifetime (~24h). When expired, API calls fail but gateway processes stay alive. Cron jobs report the error; agents appear "online" but non-functional.

### 6 — Fix Partial Credential Pool Corruption (Single-Agent Failure)

If **only one agent** fails with `RuntimeError: No access token found for Nous Portal login` while other agents work fine, the broken profile's `auth.json` has an **empty `credential_pool.nous[0].access_token`** while `providers.nous` still contains an API key placeholder. This is a partial credential corruption, not a full provider revocation.

**Diagnosis:**
```bash
# Check the failing agent's auth.json structure
python3 -c "import json; a=json.load(open('/root/.hermes/profiles/yoyo/auth.json')); print(json.dumps(a['credential_pool'], indent=2))"
# Look for: "access_token": "" (empty string) in credential_pool.nous[0]
```

**Repair — Copy working credential from a healthy agent:**
```bash
# 1. Pick a working agent (dmob or desmond) and extract their Nous credential
python3 -c "import json; a=json.load(open('/root/.hermes/profiles/dmob/auth.json')); cred=a['credential_pool']['nous'][0]; print('access_token:', cred['access_token'][:30], '...'); print('refresh_token:', cred['refresh_token'][:30], '...');"

# 2. Inject into broken profile (yoyo example)
python3 -c "import json; src='/root/.hermes/profiles/dmob/auth.json'; dst='/root/.hermes/profiles/yoyo/auth.json'; a=json.load(open(dst)); dm=json.load(open(src)); a['credential_pool']['nous'][0]['access_token']=dm['credential_pool']['nous'][0]['access_token']; a['credential_pool']['nous'][0]['refresh_token']=dm['credential_pool']['nous'][0]['refresh_token']; json.dump(a, open(dst,'w'), indent=2); print('Updated yoyo credential_pool')"

# 3. Also sync providers.nous.api_key (for backward compatibility)
python3 -c "import json; a=json.load(open('/root/.hermes/profiles/yoyo/auth.json')); dm=json.load(open('/root/.hermes/profiles/dmob/auth.json')); a['providers']['nous']['api_key']=dm['providers']['nous'].get('api_key',''); json.dump(a, open('/root/.hermes/profiles/yoyo/auth.json','w'), indent=2)"

# 4. Clear stale PID and restart the agent
rm -f /root/.hermes/profiles/yoyo/gateway.pid
HERMES_HOME=/root/.hermes/profiles/yoyo hermes gateway run &
```

**Why this happens:** OAuth tokens are refreshed per-profile on different schedules. When one agent's refresh fails or its credential entry gets corrupted (empty access_token), it becomes non-functional while others remain online. The fix is surgical — only the broken profile needs repair; full provider migration is unnecessary.

**Detection tip:** The error message distinguishes the two patterns:
- `No access token found for Nous Portal login` → **Partial corruption** (single-agent, credential_pool empty)
- `Refresh session has been revoked` → **Full revocation** (all-agents, need `hermes model` + provider switch)

### 6 — Clear Stale Platform Locks (Critical for Telegram)

If gateways fail with **"Telegram bot token already in use (PID XXXX)"** but the referenced PID is dead, stale platform locks are blocking startup. These locks survive process death and must be cleared manually.

**Diagnose first:**
```bash
# Check if the referenced PID actually exists
ps -p XXXX -o pid,stat,cmd   # replace XXXX with the PID from error
# Or check /proc
ls /proc/XXXX 2>/dev/null || echo "PID does not exist"
```

**If PID is dead → clear stale Telegram locks:**
```bash
# Lock directory location
LOCK_DIR="$HOME/.local/state/hermes/gateway-locks"

# Remove ALL Telegram bot token locks (each agent uses a unique token, no conflict expected)
rm -f "$LOCK_DIR"/telegram-bot-token-*.lock

# Also clear gateway.pid files (stale single-process lock)
rm -f ~/.hermes/profiles/*/gateway.pid
```

**Why this happens:** Hermes uses scoped platform locks (`acquire_scoped_lock`) to prevent multiple local gateways from using the same external identity (e.g., same Telegram bot token). Lock files live at `~/.local/state/hermes/gateway-locks/{scope}-{identity_hash}.lock`. If a gateway dies without releasing its lock (crash, SIGKILL), the lock file persists and blocks restarts. The lock-check code (`os.kill(pid, 0)`) should detect stale locks, but in practice race conditions or filesystem quirks can leave stale locks that need manual removal.

**Verify lock clearance:**
```bash
ls "$LOCK_DIR"/telegram-bot-token-*.lock   # should show nothing after rm
```

Then proceed to restart gateways (Step 3).

### 6 — Detect & Fix Telegram Bot Token Revocation

**Symptom:** Gateways crash immediately on startup with error:
```
ERROR gateway.platforms.telegram: [Telegram] Failed to connect to Telegram: The token `8640344678:***` was rejected by the server.
telegram.error.InvalidToken: Unauthorized
```
or in `gateway.out`:
```
The token `<bot_id>:***` was rejected by the server.
```

**Root cause:** Telegram has revoked the bot token (suspension, manual revocation by @BotFather, security rotation, or expired token). Unlike stale platform locks, this is a **credential validity issue** — the token stored in the agent's `.env` file is no longer accepted by Telegram's API.

**How this differs from stale Telegram locks:**
| Issue | Error message | Location | Fix |
|-------|--------------|----------|-----|
| Stale platform lock | `Telegram bot token already in use (PID XXXX)` | Lock file `~/.local/state/hermes/gateway-locks/` | Clear `.lock` files |
| Token revocation | `InvalidToken` / `token was rejected by the server` | Profile `.env` file | **Regenerate bot via @BotFather** |

**Diagnosis:**
```bash
# 1. Confirm InvalidToken in logs
tail -30 /root/.hermes/profiles/yoyo/logs/gateway.out | grep -i "rejected\|invalidtoken"

# 2. Locate the token in profile .env files (NOT in auth.json!)
grep -H 'TELEGRAM_BOT_TOKEN' /root/.hermes/profiles/{yoyo,dmob,desmond}/.env 2>/dev/null

# Expected output:
# /root/.hermes/profiles/yoyo/.env:TELEGRAM_BOT_TOKEN=872776...soWY
# /root/.hermes/profiles/yoyo/.env:TELEGRAM_BOT_TOKEN_YOYO=872776...soWY
# /root/.hermes/profiles/dmob/.env:TELEGRAM_BOT_TOKEN_DMOB=871032...etc
```

**Recovery requires manual intervention (no automated fix):**

**Step 1 — Regenerate each bot via @BotFather** (in Telegram):
```
/newbot
Name: Gentech YoYo
Username: GentechYoYo_bot
→ Copy token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

Repeat for DMOB and Desmond with unique usernames.

**Step 2 — Update profile .env files** with the fresh tokens:
```bash
# Edit each agent's .env directly
vi /root/.hermes/profiles/yoyo/.env      # replace TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN_YOYO
vi /root/.hermes/profiles/dmob/.env     # replace TELEGRAM_BOT_TOKEN_DMOB
vi /hermes/profiles/desmond/.env        # replace TELEGRAM_BOT_TOKEN_DESMOND

# Or using sed (be careful with token exposure in shell history!)
sed -i 's/^TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=NEW_TOKEN_HERE/' /root/.hermes/profiles/yoyo/.env
sed -i 's/^TELEGRAM_BOT_TOKEN_YOYO=.*/TELEGRAM_BOT_TOKEN_YOYO=NEW_TOKEN_HERE/' /root/.hermes/profiles/yoyo/.env
```

**Important:** Each agent should use its own dedicated bot (no token sharing across agents).

**Step 3 — Clear ALL gateway artifacts and restart:**
```bash
# Kill any dying gateway processes
pkill -f "hermes gateway run" 2>/dev/null || true
sleep 2

# Clear stale locks and PIDs
rm -f /root/.hermes/gateway.pid
rm -f /root/.hermes/profiles/*/gateway.pid
rm -f /root/.local/state/hermes/gateway-locks/telegram-bot-token-*.lock

# Start gateways sequentially (4s stagger)
for agent in yoyo dmob desmond; do
  HERMES_HOME="/root/.hermes/profiles/$agent" nohup \
    /root/.hermes/hermes-agent/venv/bin/python3 \
    /root/.local/bin/hermes gateway run \
    >> "/root/.hermes/profiles/$agent/logs/gateway.out" 2>&1 &
  sleep 4
done

# Verify
sleep 8
ps aux | grep 'gateway run' | grep -v grep
tail -20 /root/.hermes/logs/agent.log | grep -i "telegram connected"
```

**Prevention:** Telegram bot tokens are permanent until manually revoked. However, if bots are accidentally deleted in @BotFather, tokens become invalid immediately. Keep a secure backup of tokens (encrypted password manager) to enable quick rotation.

**Quick reference — Token storage locations:**
- **Telegram bot tokens:** `~/.hermes/profiles/{agent}/.env` (TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_TOKEN_{AGENT})
- **Nous/LLM provider credentials:** `~/.hermes/profiles/{agent}/auth.json` (OAuth tokens in `credential_pool`)
- **Model configuration:** `~/.hermes/profiles/{agent}/config.yaml` (model: stepfun/step-3.5-flash, provider: nous)

See also: `gentech-agent-health-diagnosis` skill for the full diagnostic decision tree.


### 7 — Check Logs Correctly (Critical Tip)

**gateway.out is often stale** — it retains old error banners from previous runs because the log file isn't truncated on restart and the shell wrapper may keep old file descriptors open. **Always use `agent.log` as the source of truth for current agent state.**

```bash
# CORRECT: Check agent.log for recent activity
tail -20 ~/.hermes/profiles/yoyo/logs/agent.log

# gateway.out may show pre-restart errors (stale)
tail -30 ~/.hermes/profiles/yoyo/logs/gateway.out  # often stale — don't trust
```

**In agent.log, verify:**
- `✓ telegram connected` (with recent timestamp, within last 60s)
- `Cron ticker started (interval=60s)`
- No ERROR lines in the last 2 minutes of log

**Error signature taxonomy — match error → fix:**

| Error text | Likely cause | Fix |
|------------|-------------|-----|
| `PID file race lost to another gateway instance` | Concurrent startup | Kill all gateways, clear PIDs/locks, restart **sequentially** (3–4s between agents) |
| `Telegram bot token already in use (PID XXXX)` | Stale Telegram lock | Check if PID exists (`ps -p XXXX`); if dead → `rm ~/.local/state/hermes/gateway-locks/telegram-bot-token-*.lock` |
| `Model 'X' not found` | Wrong model catalog ID | Query API to find correct ID (see Step 8), update `config.yaml`, fully restart |
| `Refresh session has been revoked` | OAuth refresh token expired | Pause cron job, run `hermes model` interactively to re-auth, copy `auth.json` to all profiles, restart |
| `No access token found for Nous Portal login` | Partial credential corruption (single-agent) | Copy working `auth.json` from another profile, restart only that agent |

### 8 — Inspect OAuth Credential State (auth.json)

The `auth.json` `credential_pool` contains OAuth tokens with expiry timestamps. Check these to diagnose auth failures:

```bash
python3 -c "
import json, os
for agent in ['yoyo','dmob','desmond']:
    path = f'/root/.hermes/profiles/{agent}/auth.json'
    with open(path) as f: a = json.load(f)
    cred = a['credential_pool']['nous'][0]
    print(f'{agent}: expires_at={cred.get("expires_at")}, agent_key_expires={cred.get("agent_key_expires_at")}')
"
```

Key fields:
- `expires_at` — access token expiry (typically ~1 hour after last call)
- `agent_key_expires_at` — agent key / refresh token lifetime (typically ~24 hours)
- `refresh_token` — the token sent to Nous to get new access tokens
- `last_status` / `last_status_at` — last successful auth check

If `expires_at` is in the past, the access token needs refresh. If `agent_key_expires_at` is past **and** `refresh_token` is revoked by the provider, `hermes model` interactive re-auth is required.

### 9 — Discovery: Finding the Correct Model Catalog ID

When the API returns 404, the model identifier in `config.yaml` doesn't match the provider's live model catalog. Nous Inference API uses OpenRouter-compatible model IDs with namespace prefixes.

**Query the live catalog:**
```bash
# List all available models
curl -s https://inference-api.nousresearch.com/v1/models | jq -r '.data[] | .id' | head -30

# Filter specifically for Step models
curl -s https://inference-api.nousresearch.com/v1/models | jq -r '.data[] | select(.id | contains("step")) | .id'
```

**Model ID format rules (Nous Inference API):**
- ✗ `step-3.5-flash` — bare name, no namespace → 404 not found
- ✗ `nous/step-3.5-flash` — wrong namespace (Nous doesn't own the `stepfun` namespace) → 404
- ✓ `stepfun/step-3.5-flash` — correct: full `{provider_namespace}/{model_name}`
- ✓ `openai/gpt-4o` — correctly formatted example

**Why the confusion:** The agent auto-detects `provider: nous` from the `NOUS_API_KEY` environment variable (or from credentials), but the model catalog uses a separate namespace (`stepfun`) for Step models hosted on the Nous inference platform. The `model:` field must be the **full catalog ID** including namespace.

**Fix across all agent profiles:**
```yaml
# ~/.hermes/profiles/{yoyo,dmob,desmond}/config.yaml
model: stepfun/step-3.5-flash
providers: {}  # leave empty — agent resolves provider from NOUS_API_KEY or auth.json
```

After updating `config.yaml`, you must **fully restart gateways** (kill all, clear PIDs/locks, then sequential launch) to ensure every agent process reloads the fresh configuration.

## Verification

- All 3 agent gateways running as distinct processes (different PIDs)
- `hermes cron list` shows `"state": "scheduled"` and `"enabled": true` for expected jobs
- Watchdog reports "All agents healthy"
- Agent channel directories show updated `channel_directory.json` with recent timestamp

## Common Pitfalls

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| No processes after startup | HERMES_HOME not set per-agent | Use explicit `HERMES_HOME="$profile_home"` |
| Gateways start then exit | auth.json missing in profile | Copy main `~/.hermes/auth.json` to each profile or run `hermes login` per profile |
|| Log files empty | Background wrapper swallowed output | Run directly via `terminal(background=true)` tool instead of shell backgrounding ||
|| Gateways produce zero logs, stay in S (sleep) state | **Auth format mismatch** — auth.json contains OAuth tokens but provider expects API key env var (or vice versa); wrong base_url; provider import error | **Fix:** 1) Kill gateways and clear locks 2) Verify `config.yaml` provider+base_url 3) Match auth format to provider (OAuth tokens in `auth.json['providers']` vs API key in `STEPFUN_API_KEY` env var) 4) Check `logs/gateway.log` for import errors 5) Use `terminal` not shell `nohup` to capture stdout ||
| Model "not found" (404) | Incorrect model catalog ID format | Use `stepfun/step-3.5-flash` not `step-3.5-flash` or `nous/step-3.5-flash`; verify via /v1/models endpoint |
| Cron jobs show paused but `enabled: true` | Paused via watchdog or manual; **state field overrides enabled** — `state: "paused"` takes precedence | Use `hermes cron resume <id>` to set `state: "scheduled"` |
| Cannot find jobs to resume | jobs.json structure is `{"jobs": [...]}` not bare list | Access `data.get('jobs', [])` |
| Cron jobs fail: "Refresh session has been revoked" | **Provider revoked OAuth tokens** (Nous MIMO V2 deprecation) | **Full provider migration required** — cannot re-login. See "Provider Migration" section below. |
| PID file race / gateway already running | Stale `gateway.pid` from previous crash | Kill stale process: `kill -9 $(cat profile/gateway.pid 2>/dev/null)`, then delete `.pid` file |
| `auxiliary_client.py` syntax corruption | Corrupted import file in `$PROFILE_HOME/home/` with non-UTF8 bytes; blocks Python import at gateway startup | Replace with clean copy from `/root/.hermes/hermes-agent/agent/auxiliary_client.py` or reinstall hermes-agent |
| `home/.hermes` symlink broken or missing | Symlink replaced by directory or deleted; profile cannot access shared brain data | Repoint symlink: `rm -rf $PROFILE_HOME/home/.hermes && ln -s /root/.hermes $PROFILE_HOME/home/.hermes` (backup directory first if needed) |
| Config resets after `hermes update` | Answered YES to "restore local changes?" prompt | **Always answer NO.** If YES, recover from backup or use migration skill to rebuild. |

### Provider Migration Pattern (Auth Revocation Recovery)

When **all agents fail simultaneously** with `Refresh session has been revoked` errors, the provider has revoked existing OAuth tokens and a full migration to a new provider is required.

**Step-by-step:**

1. **Choose new provider and obtain credentials** (API key, not OAuth):
   ```bash
   # Stepfun example
   export STEPFUN_API_KEY=sk-...
   ```
2. **Update each profile's config.yaml** directly (do NOT use `hermes model`):
   ```yaml
   model:
     default: stepfun/step-3.5-flash
     provider: stepfun
     base_url: https://inference-api.nousresearch.com/v1  # Stepfun models hosted on Nous inference API
   ```
3. **Add credentials in the format the provider expects**:
   - **OAuth providers** (Nous, Anthropic via portal): `auth.json` populated automatically by `hermes login` / `hermes model`
   - **API-key providers** (Stepfun, OpenRouter): Preferred — set env var `STEPFUN_API_KEY=sk-...` in each profile's environment OR add to `auth.json`:
     ```bash
     python3 -c "
import json, os
key = os.environ['STEPFUN_API_KEY']
for p in ['yoyo','dmob','desmond']:
  path = f'/root/.hermes/profiles/{p}/auth.json'
  with open(path) as f: a = json.load(f)
  a['providers']['stepfun'] = {'api_key': key, 'base_url': 'https://api.stepfun.ai/step_plan/v1'}
  with open(path, 'w') as f: json.dump(a, f, indent=2)
"
     ```
   **⚠️ Auth format mismatch causes silent gateway hangs** — If `auth.json` contains OAuth tokens but the provider expects an API key env var (or vice versa), the gateway imports the provider module, fails to find valid credentials, and sleeps indefinitely with zero logs. Ensure the credential format matches the provider type. Remove stale/incompatible provider entries from `auth.json['providers']` when switching schemes.
4. **Kill ALL stale gateway processes** before restart:
   ```bash
   pkill -f "hermes gateway run" 2>/dev/null
   rm -f ~/.hermes/profiles/*/gateway.pid
   ```
5. **Restart gateways clean** (per-profile):
   ```bash
   HERMES_HOME=/root/.hermes/profiles/yoyo hermes gateway run &
   HERMES_HOME=/root/.hermes/profiles/dmob hermes gateway run &
   HERMES_HOME=/root/.hermes/profiles/desmond hermes gateway run &
   HERMES_HOME=/root/.hermes/profiles/default hermes gateway run &
   ```
6. **Test via Telegram** — each agent should respond to `/test` messages without auth errors
7. **Verify cron jobs** — `hermes cron run <id>` should succeed

**Why OAuth re-login doesn't work:** Providers that revoke tokens (Nous MIMO V2) invalidate refresh tokens system-wide. `hermes login` uses OAuth device-code flow but needs a working refresh token first — a chicken-egg problem. API-key providers (Stepfun, OpenRouter, Anthropic) sidestep this entirely.

**Full guide:** See `hermes-provider-migration` skill.
## Diagnostic Checklist (Post-Recovery Validation)

After restoring gateways, verify agent health systematically:

\`\`\`bash
# 1. Check all 3 agent processes are running
ps aux | grep 'hermes gateway run' | grep -v grep

# 2. Inspect each agent's auth.json provider format
for agent in yoyo dmob desmond; do
  echo "=== $agent ==="
  python3 -c "
import json
with open(f'/root/.hermes/profiles/$agent/auth.json') as f:
    a = json.load(f)
prov = a.get('providers', {})
print('Providers:', list(prov.keys()))
for p,data in prov.items():
    print(f'  {p}: keys={list(data.keys())}')
  "
done

# 3. Check each agent's config.yaml provider match
for agent in yoyo dmob desmond; do
  echo "=== $agent config ===" 
  grep -E '^(provider|base_url|default):' /root/.hermes/profiles/$agent/config.yaml
done

# 4. Verify auxiliary_client.py is valid UTF-8 / importable
python3 -c "
import py_compile, sys
for agent in ['yoyo','dmob','desmond']:
    path = f'/root/.hermes/profiles/{agent}/home/auxiliary_client.py'
    try:
        py_compile.compile(path, doraise=True)
        print(f'{agent}: OK')
    except Exception as e:
        print(f'{agent}: CORRUPT - {e}')
"
\`\`\`

**Red flags:**  
- auth.json has OAuth tokens but config uses API-key provider (or vice versa)  
- `base_url` mismatches provider (e.g., stepfun .com vs .ai domain)  
- `auxiliary_client.py` raises SyntaxError / UnicodeDecodeError  
- `home/.hermes` not a symlink or points to non-existent directory  

## Pre-emptive Maintenance Tasks

Run monthly to avoid surprise downtime:

1. **Rotate hermes agent OAuth tokens** — Nous Portal refresh tokens expire ~30d. Run:
   \`hermes model\` in each profile to refresh before expiry.

2. **Validate provider keys** — Ensure configured LLM provider has sufficient credits/funds.

3. **Check symlink integrity**:
   \`find /root/.hermes/profiles -type l -name .hermes -exec readlink {} \;\`

4. **Inspect auxiliary_client.py** periodically for corruption:
   \`python3 -m py_compile /root/.hermes/profiles/*/home/auxiliary_client.py\`


## Context

**Agent routing:**
- YoYo → Strategies channel / Labs workflow
- DMOB → Labs channel  
- Desmond → Creative channel / Entertainment

**Boot-time dependencies:**
1. Main Hermes gateway must be running first (daemon PID ~213xxx)
2. Agent profiles must have valid auth.json (Telegram tokens)
3. Channel directory must be populated (happens after first successful connection)

**Watchdog** runs every 15 minutes and will auto-restart any dead agents. The manual restart above is a one-time "bring all online now" operation.

## Related Skills

- `devops/hermes-provider-migration` — Systematic provider migration after OAuth token revocation (Nous MIMO V2 → Stepfun pattern)
- `devops/gentech-agent-reactivation` — This skill (general agent restart)
- `autonomous-ai-agents/hermes-council/skills/council/agent-watchdog-management` — if it exists
- `github/github-issues` — for tracking agent downtime incidents
- `devops/process-monitoring` — general process supervision patterns
### 6 — Diagnose Silent Gateway Hangs (Gateway produces zero logs)

If gateways show as running (`ps aux`) but `logs/gateway.out` is empty and cron jobs never fire:

**Common causes & checks:**
```bash
# 1. Verify config.yaml syntax and values
cat ~/.hermes/profiles/yoyo/config.yaml | grep -A3 'model:'

# 2. Check for provider import errors in system/hermes logs
journalctl -u hermes -n 50 2>/dev/null || dmesg | tail -20
tail -20 ~/.hermes/logs/hermes.log 2>/dev/null || echo "No main hermes.log"

# 3. Validate auth.json structure matches provider type
python3 -c "
import json, sys
path = '/root/.hermes/profiles/yoyo/auth.json'
with open(path) as f: a = json.load(f)
prov = a.get('providers', {})
print('Providers found:', list(prov.keys()))
for k,v in prov.items():
  print(f'  {k}: keys={list(v.keys())}')
"
```

**Fix sequence:**
1. Kill all gateways: `pkill -f "hermes gateway run"`
2. Remove stale locks: `rm -f ~/.hermes/profiles/*/gateway.pid ~/.hermes/profiles/*/auth.lock`
3. Ensure credentials in correct format (see auth format mismatch pitfall)
4. Restart gateways using `terminal(background=true)` to capture stdout/stderr

**Why this happens:** The gateway imports the provider module at startup. If the provider specifies an env var auth scheme (like `STEPFUN_API_KEY`) but auth.json only contains OAuth tokens, the provider fails silently during initialization and the process sleeps waiting for valid credentials.
