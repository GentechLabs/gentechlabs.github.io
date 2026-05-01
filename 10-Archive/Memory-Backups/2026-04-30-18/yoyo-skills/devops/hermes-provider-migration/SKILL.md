---
name: hermes-provider-migration
description: Systematic recovery and migration of Hermes agents to a new LLM provider after upstream deprecation, with safe update practices and multi-agent coordination.
version: 1.0.0
author: Gentech Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, migration, provider-switch, recovery, multi-agent, configuration]
    related_skills: [hermes-agent, gentech-agent-reactivation]
---

# Hermes Agent Provider Migration

When an LLM provider deprecates or revokes access (e.g., Nous MIMO V2), agents become non-functional. This skill covers the systematic process of migrating all Hermes agent profiles to a new provider while preserving routing, cron jobs, skills, and custom configurations.

## When to Use

- Upstream provider deprecates an endpoint or revokes OAuth tokens
- Switching to a different model family (Nous → Stepfun, OpenRouter → Anthropic, etc.)
- Need to update credentials after auth failures
- Recovering from "Refresh session has been revoked" or 401/403 errors across all agents

## Critical Discovery

**Hermes update overwrites profile configs.** During `hermes update`, the installer asks *"restore local changes?"* — answering **YES** replaces all custom `config.yaml` settings with upstream defaults, wiping model blocks, routing, and schedule modifications. **Always answer NO.** If you answered yes accidentally, the recovery pattern below applies.

## Migration Workflow

### 1. Discovery & Assessment

```bash
# Check current agent status
hermes status --all              # Which agents are alive/dead
ps aux | grep hermes             # Running gateway processes
cat ~/.hermes/profiles/*/config.yaml | grep -E 'model|provider|base_url'

# Check auth state (will show OAuth tokens or missing API keys)
cat ~/.hermes/profiles/*/auth.json | jq .providers

# Identify what broke (logs)
grep -i "revoked\|401\|403" ~/.hermes/logs/gateway.log | tail -30
```

**Signs of provider deprecation:**
- Gateway logs: `Refresh session has been revoked`
- Auth.json shows old provider with `refresh_token` but no new access token
- All agents fail simultaneously with 401/403 errors
- Cron jobs fail with "authentication error" or "provider unavailable"

### 2. Choose New Provider & Get Credentials

Select a provider and obtain API keys or OAuth credentials:

| Provider | Auth Type | Key Env Var | Notes |
|----------|-----------|-------------|-------|
| Stepfun | API Key | `STEPFUN_API_KEY` | Direct key in config |
| OpenRouter | API Key | `OPENROUTER_API_KEY` | Pool across keys |
| Anthropic | API Key | `ANTHROPIC_API_KEY` | Stable but costly |
| Custom endpoint | API Key | Any | Set `base_url` manually |

For API-key providers (Stepfun, OpenRouter, Anthropic):
- Buy/obtain key from provider dashboard
- No OAuth flow needed — key goes directly in auth.json

For OAuth providers (Nous Portal, GitHub Copilot):
- Use `hermes login --provider <name>`
- Follow device-code flow

### 3. Update config.yaml for Each Profile

**Do NOT run `hermes update`** — it will ask about restoring local changes and break custom configs.

Edit each profile's `config.yaml` directly:

```yaml
# /root/.hermes/profiles/<profile>/config.yaml
model:
  default: stepfun/step-3.5-chat          # provider/model format
  provider: stepfun                       # Must match auth.json provider key
  base_url: https://api.stepfun.com/v1    # Custom endpoint if needed
  # Optional: context_length, temperature, etc.
```

**Verification:** Check all three (or four) profiles have consistent provider and base_url.

### 4. Add Provider Credentials to auth.json

Hermes uses **credential pools** — auth.json stores credentials per-provider.

**Structure:**
```json
{
  "providers": {
    "stepfun": {
      "api_key": "sk-...",
      "base_url": "https://api.stepfun.com/v1"
    },
    "openrouter": {
      "api_keys": ["key1", "key2", "..."],
      "base_url": "https://openrouter.ai/api/v1"
    }
    // ... other providers
  },
  "active": "stepfun"  // optional, determines default
}
```

**Add the new provider entry to EVERY profile's auth.json** (yoyo, dmob, desmond, default). Use the same key across all profiles for consistency, or set per-agent keys if you have multiples.

```bash
# Script template
for profile in yoyo dmob desmond; do
  auth="/root/.hermes/profiles/$profile/auth.json"
  # Add stepfun block if missing
  python3 -c "
import json
with open('$auth') as f: a = json.load(f)
a['providers']['stepfun'] = {'api_key': 'YOUR_KEY', 'base_url': 'https://api.stepfun.com/v1'}
with open('$auth', 'w') as f: json.dump(a, f, indent=2)
"
done
```

### 5. Kill Stale Gateway Processes

Old gateways are still running with revoked tokens — kill them before restart:

```bash
# Find PIDs
ps aux | grep 'hermes gateway' | grep -v grep

# Kill each profile's gateway
kill -9 $(cat /root/.hermes/profiles/yoyo/gateway.pid 2>/dev/null || true)
kill -9 $(cat /root/.hermes/profiles/dmob/gateway.pid 2>/dev/null || true)
kill -9 $(cat /root/.hermes/profiles/desmond/gateway.pid 2>/dev/null || true)
kill -9 $(cat /root/.hermes/profiles/default/gateway.pid 2>/dev/null || true)

# Or use process manager
systemctl --user stop hermes-gateway@yoyo 2>/dev/null || true
pkill -f "hermes gateway run"
```

**Warning:** Do NOT skip this step — dead gateways will spam error logs and consume resources.

### 6. Restart Gateways Fresh

Start each agent gateway cleanly:

```bash
# In separate tmux windows or background
HERMES_HOME=/root/.hermes/profiles/yoyo hermes gateway run &
HERMES_HOME=/root/.hermes/profiles/dmob hermes gateway run &
HERMES_HOME=/root/.hermes/profiles/desmond hermes gateway run &
HERMES_HOME=/root/.hermes/profiles/default hermes gateway run &
```

Or via systemd (if installed as service):

```bash
systemctl --user start hermes-gateway@yoyo
systemctl --user start hermes-gateway@dmob
systemctl --user start hermes-gateway@desmond
systemctl --user start hermes-gateway@default
```

**Verify startup:**
```bash
hermes doctor                    # Check config sanity
hermes status --all              # All profiles should show "running"
tail -f ~/.hermes/logs/gateway.log  # Watch for errors
```

### 7. Test Connectivity

Send a test message to each agent via Telegram:

```
/test hey   # Or any simple query
```

Expected response: Agent replies within 10-30 seconds with a normal answer (not auth error).

If still failing:
- Double-check `STEPFUN_API_KEY` matches exactly
- Verify `base_url` is correct (no trailing slash issues)
- Check `auth.json` JSON syntax (`jq . auth.json`)
- Inspect `~/.hermes/logs/gateway.log` for specific error

### 8. Verify Cron Jobs

Cron jobs should now execute without auth errors:

```bash
hermes cron list                 # All jobs present
hermes cron status               # Scheduler running
tail -f ~/.hermes/logs/cron.log  # Next execution log
```

Manually trigger a job to test:
```bash
hermes cron run <job-id>
```

Watch for successful delivery to Telegram groups (Mess Hall, Green Room).

### 9. Build Model-Switch Skill (Optional but Recommended)

Create a Telegram slash command skill to switch models without SSH access:

**Skill location:** `~/.hermes/skills/custom/telegram-model-switch/`

**Structure:**
```
telegram-model-switch/
├── SKILL.md            # Command spec, trigger conditions
└── skill.py            # Handler: edits config.yaml, restarts gateway
```

**SKILL.md essentials:**
```yaml
commands:
  - name: /model
    description: Switch LLM model/provider
    params: [provider/model]
    # Restrict to owner user_id only
  - name: /models
    description: List available providers
    params: []
```

**Skill logic (skill.py):**
1. Parse args: `/model stepfun/step-3.5-chat`
2. Identify which agent profile this gateway belongs to (from `HERMES_HOME`)
3. Update that profile's `config.yaml`:
   ```yaml
   model:
     default: <new_model>
     provider: <provider>
     base_url: <url if custom>
   ```
4. Restart that profile's gateway (soft restart via `/restart` or kill+start)
5. Confirm to user in Telegram

**Security:** Check `event.user_id` against a hardcoded allowlist — only your Telegram user ID can execute `/model`.

**Deployment:**
```bash
# Copy skill to Hermes skills directory
cp -r telegram-model-switch ~/.hermes/skills/custom/

# Restart all gateways to load new skill
systemctl --user restart hermes-gateway@{yoyo,dmob,desmond,default}
```

## Common Pitfalls & Fixes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `Refresh session has been revoked` | OAuth token expired, provider deprecated | Replace provider, update auth.json with API key, restart |
| 401 Unauthorized | API key missing or wrong | Add correct `STEPFUN_API_KEY` to auth.json |
| Gateway dies immediately | Stale `gateway.pid` file | Delete `*.pid` in profile directory |
| Tools not available | Old session still active | `/reset` in Telegram or restart gateway |
| No response to Telegram | Gateway not running | `hermes gateway run` and check logs |
| Model not switching | Skill not loaded | Add skill directory, restart gateway |
| Config resets after update | Answered YES to restore prompt | Restore from memory/skill, never say YES |

## Safe Update Practices

**Pre-update:**
1. `git status` in `~/.hermes/hermes-agent/` — commit any local changes if you want to preserve them
2. `hermes config export ~/backup-config-$(date +%Y%m%d).tar.gz` — backup all profiles
3. Note current model/provider in a permanent note

**During `hermes update`:**
- **ALWAYS answer NO to "restore local changes?"** — this preserves your profile configs
- If you accidentally say YES, recover using the migration workflow above

**Post-update:**
1. `hermes doctor` — check for missing dependencies
2. `hermes status` — verify all components running
3. Test one agent with a simple message
4. Check cron execution (`hermes cron list` then manual trigger)

## Prevention: Auto-Healthcheck Script

Create a script that runs after each update to verify agent health:

```bash
# /usr/local/bin/hermes-healthcheck
#!/bin/bash
PROFILES=(yoyo dmob desmond default)

for p in "${PROFILES[@]}"; do
  HOME=/root/.hermes/profiles/$p
  if ! grep -q "Error\|Failed\|revoked" ~/.hermes/logs/gateway.log; then
    echo "✓ $p: OK"
  else
    echo "✗ $p: FAILED — check logs"
    # Optional: auto-restart
    kill -9 $(cat $HOME/gateway.pid 2>/dev/null || true)
    HERMES_HOME=$HOME hermes gateway run &
  fi
done
```

Add to crontab: `@reboot /usr/local/bin/hermes-healthcheck` and as a cron job profile.

## Multi-Agent Recovery Checklist

- [ ] Identify affected profiles (yoyo, dmob, desmond, default)
- [ ] Select new provider and obtain API key
- [ ] Update `config.yaml` model block for each profile
- [ ] Add provider entry to `auth.json` for each profile
- [ ] Kill all stale gateway processes (check PID files)
- [ ] Restart each gateway cleanly
- [ ] Send test message to each Telegram agent
- [ ] Verify cron job execution (`hermes cron run <id>`)
- [ ] (Optional) Deploy `/model` Telegram skill for future switches
- [ ] Document the change in vault: `09-Green Room/agent-recovery-<date>.md`

## Related Skills

- `gentech-agent-reactivation` — Bring all YoYo/DMOB/Desmond agent gateways and cron jobs back online
- `hermes-agent` — General Hermes CLI, configuration, profiles, and troubleshooting
