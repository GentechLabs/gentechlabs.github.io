---
name: hermes-vps-debugging
description: Debug multi-agent Hermes setups on headless VPS servers — diagnose auth failures, Telegram token issues, profile config drift, and process state across multiple agent profiles. Companion skill to hermes-agent.
version: 1.1.0
author: DMob (Gentech)
tags: [hermes, vps, debugging, multi-agent, headless, telegram, troubleshooting]
related_skills: [hermes-agent]
---

# Hermes VPS Debugging

Systematic debugging for multi-agent Hermes deployments on headless Linux VPS servers. Each agent runs in its own profile under `~/.hermes/profiles/<name>/` with isolated auth, config, and `.env`.

## When to Use This Skill

- Multiple agents returning "Provider authentication failed"
- Agents that died silently (not in tmux/process list)
- Telegram bot rejecting tokens on startup
- Config drift between profiles created at different times

## Critical Lesson: "Provider auth failed" is Often Wrong

The "Hermes is not logged into Nous Portal" error can be misleading. In multi-agent setups, the real failure is frequently a **Telegram bot token issue**, not Nous Portal OAuth. Always verify Telegram tokens independently before re-running OAuth flows.

### Access Token vs Agent Key

Nous Portal auth has two layers:
- **Access token**: Short-lived (15 min), used to mint agent keys. Auto-refreshed via refresh token.
- **Agent key**: Longer-lived (typically ~24 hrs), used for actual inference calls.

If the agent key is still valid, the agent works fine even if the access token expired momentarily. The gateway auto-refreshes access tokens. The "Provider auth failed" message can appear briefly during refresh cycles — wait a few seconds before troubleshooting.

## Debugging Checklist

### 1. Inventory Profiles and Processes

```bash
ls ~/.hermes/profiles/
ps aux | grep -E "hermes|gateway" | grep -v grep
tmux list-sessions 2>/dev/null
```

### 2. Check Nous Auth State Per Profile

Each profile has its own `auth.json` with Nous Portal OAuth tokens. Check expiration and refresh token presence for each profile.

```bash
for p in ~/.hermes/profiles/*/; do
  echo "=== $(basename $p) ==="
  python3 << 'PYEOF'
import json
import os
import sys

profile_dir = sys.argv[1]
auth_file = os.path.join(profile_dir, "auth.json")
try:
    with open(auth_file) as f:
        d = json.load(f)
    nous = d.get("providers", {}).get("nous", {})
    print(f"  expires_at: {nous.get('expires_at', 'MISSING')}")
    print(f"  has_refresh: {bool(nous.get('refresh_token'))}")
    print(f"  agent_key_expires: {nous.get('agent_key_expires_at', 'MISSING')}")
except FileNotFoundError:
    print("  NO auth.json")
PYEOF
done
```

### 3. Verify Telegram Bot Tokens

Use Telegram Bot API directly to test each bot token from each profile's `.env`:

```bash
for p in ~/.hermes/profiles/*/; do
  token=$(grep "^TELEGRAM_BOT_TOKEN=" "$p/.env" 2>/dev/null | cut -d= -f2)
  name=$(basename $p)
  if [ -n "$token" ]; then
    echo "$name: token present"
    # Test: curl -s "https://api.telegram.org/bot${token}/getMe"
    # Should return ok=true with bot username
  else
    echo "$name: NO TOKEN SET"
  fi
done
```

A bot returning `ok=false` means the token was revoked in @BotFather. The error log will show:
```
telegram.error.InvalidToken: The token `BOTID:***` was rejected by the server.
```

### 4. Check Profile Logs

```bash
tail -10 ~/.hermes/profiles/*/logs/errors.log 2>/dev/null
```

### 5. Verify .env Completeness

Check that tokens are uncommented (no leading `#`) and non-empty:

```bash
for p in ~/.hermes/profiles/*/; do
  name=$(basename $p)
  echo "=== $name ==="
  grep -v "^#" "$p/.env" 2>/dev/null | grep -E "^[A-Z_]+=.]" | head -5
done
```

### 6. Check Config Version Drift

```bash
grep "_config_version" ~/.hermes/profiles/*/config.yaml 2>/dev/null
```

Fix mismatches with: `hermes config migrate`

## Common Failure Modes

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| "Provider auth failed" + Telegram crash | Bot token revoked/invalid | Regenerate in @BotFather, update `.env` |
| Auth token expired, no refresh | Refresh token stale | `hermes model --no-browser` (device code) |
| Agent not in process list | `.env` missing tokens | Check logs, fix `.env`, restart |
| Config version mismatch | Profiles created at different times | `hermes config migrate` per profile |
| Gateway dies on SSH logout | No linger configured | See gateway troubleshooting in hermes-agent skill |
| "Provider auth failed" during normal use | Access token refresh cycle | Wait 10 seconds — agent key is still valid |

## Fixing an Invalid Telegram Bot Token

1. Open @BotFather on Telegram
2. Select the bot (check which bot ID prefix matches)
3. Generate new token or check if bot was deleted
4. Update `TELEGRAM_BOT_TOKEN=` in the profile's `.env`
5. Restart the agent's tmux session or gateway process

## Fixing Expired Nous Auth

```bash
HERMES_HOME=~/.hermes/profiles/<name> hermes model --no-browser
# Follow the device code URL, authorize in browser
```

## Restarting Agents

```bash
tmux send-keys -t bot-<name> '/quit' Enter
sleep 2
tmux new-session -d -s bot-<name> -x 120 -y 40 \
  "HERMES_HOME=/root/.hermes/profiles/<name> hermes gateway run"
```

## Multi-Agent Organization Pattern

For organizations with multiple specialist agents:

- **Coordinator** (e.g., Gentech): Receives all messages, analyzes, delegates to specialists
- **Specialists** (e.g., YoYo/Strategies, DMob/Labs, Desmond/Creative): Only respond when delegated
- Agents share Telegram groups but should not overtalk — each has a domain
- **Green Room** (vault): Active task collaboration between agents
- **Mess Hall** (vault): Afterthought notes, context switching between tasks

Communication flow: Main group → Coordinator analyzes → Specialist works in their group → Response delivered.
