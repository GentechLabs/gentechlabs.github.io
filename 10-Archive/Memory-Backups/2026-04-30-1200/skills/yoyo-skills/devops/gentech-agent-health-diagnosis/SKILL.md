---
name: gentech-agent-health-diagnosis
description: Systematic diagnostic workflow to determine why Hermes agent gateways are down — distinguishes between stale locks, auth failures, revoked tokens, and config issues before attempting recovery
tags:
  - debugging
  - troubleshooting
  - agent-monitoring
  - health-check
related_skills:
  - devops/gentech-agent-reactivation
trigger: "agent gateway down investigation"
---

# Diagnose Hermes Agent Gateway Health Issues

**Purpose:** Determine the root cause of dead/failing agent gateways before attempting recovery. Saves time by identifying the actual problem (stale locks, auth revocation, InvalidToken, config errors) vs. guessing.

**When to use:**
- `ps aux` shows no `hermes gateway run` processes
- Telegram agents not responding
- Watchdog cron reports failures
- Gateways crash immediately on startup
- You need to know *why* agents are down before fixing

---

## Diagnostic Workflow

### Phase 1 — Quick Process Check

```bash
# Check for any running gateway processes
ps aux | grep -E '(hermes|gateway)' | grep -v grep

# Check for Hermes agent main process (the CLI itself)
ps aux | grep hermes-agent | grep -v grep
```

**Expected output when healthy:**
```
root  <PID>  ...  /root/.hermes/hermes-agent/venv/bin/python3 /root/.local/bin/hermes gateway run
```

**If nothing:** Gateways are completely down → proceed to Phase 2.

---

### Phase 2 — Lock File Forensics

Lock files persist after process death and block restarts.

```bash
# Check gateway.pid (main single-process lock)
cat /root/.hermes/gateway.pid 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "No main gateway.pid"

# Check per-profile gateway.pid files
for agent in yoyo dmob desmond; do
  pid_file="/root/.hermes/profiles/$agent/gateway.pid"
  if [ -f "$pid_file" ]; then
    echo "$agent: $(cat $pid_file)"
    pid=$(cat $pid_file | python3 -c "import sys,json; print(json.load(sys.stdin)['pid'])")
    if ! ps -p $pid > /dev/null 2>&1; then
      echo "  ⚠️ PID $pid is DEAD (stale lock)"
    else
      echo "  ✅ PID $pid is running"
    fi
  else
    echo "$agent: no gateway.pid"
  fi
done

# Check Telegram platform scoped locks (critical!)
ls -la /root/.local/state/hermes/gateway-locks/
```

**Stale lock signs:**
- `gateway.pid` references a PID that `ps -p` can't find
- Lock files exist but no corresponding processes
- `gateway_state.json` says `"gateway_state": "running"` but process not in `ps aux`

**If stale locks found → clear them:**
```bash
rm -f /root/.hermes/gateway.pid
rm -f /root/.hermes/profiles/*/gateway.pid
rm -f /root/.local/state/hermes/gateway-locks/telegram-bot-token-*.lock
```

**Then attempt restart** and check if they stay up. If they crash again → Phase 3.

---

### Phase 3 — Log Analysis (Critical — gateway.out vs agent.log)

**⚠️ gateway.out is often stale** — it retains old error banners from previous runs because log file isn't truncated on restart. **Use agent.log as source of truth.**

```bash
# Check main agent.log for recent activity (last 5 minutes)
tail -50 /root/.hermes/logs/agent.log | grep -E '(ERROR|WARNING|error|exception|fail|invalid)' | tail -20

# Also check timestamp of last entry
tail -1 /root/.hermes/logs/agent.log
```

**Then check each profile's gateway.out ONLY for startup errors:**
```bash
for agent in yoyo dmob desmond; do
  echo "=== $agent gateway.out (last 30 lines) ==="
  tail -30 /root/.hermes/profiles/$agent/logs/gateway.out 2>/dev/null || echo "(no log file)"
  echo
done
```

**Error pattern recognition:**

| Error Message (from gateway.out) | Likely Cause | Next Step |
|---------------------------------|-------------|-----------|
| `PID file race lost to another gateway instance` | Concurrent startup conflict | Check for zombie gateways, clear PIDs/locks, restart sequentially |
| `Telegram bot token already in use (PID XXXX)` | Stale Telegram lock | Verify PID exists; if dead → clear locks (Phase 2) |
| `The token \`<number>:***\` was rejected by the server` / `InvalidToken` | **Revoked/expired bot token** | → Phase 4 (token check) |
| `Model 'X' not found` | Wrong model catalog ID | Check config.yaml model format (should be `stepfun/step-3.5-flash`) |
| `Refresh session has been revoked` | Nous OAuth refresh token expired | Full provider migration needed (see reactivation skill) |
| `No access token found for Nous Portal login` | Partial credential corruption (single agent) | Copy auth.json from healthy agent |

**If you see `InvalidToken` → immediate Phase 4.**

---

### Phase 4 — Telegram Token Validation

**Context:** Hermes agents use per-agent Telegram bot tokens stored in profile `.env` files (NOT in `auth.json` or `config.yaml`). When Telegram revokes a bot token (suspension, manual revocation by @BotFather, or security rotation), gateways reject it with `InvalidToken` and exit.

**Locate tokens in profile .env files:**
```bash
for agent in yoyo dmob desmond; do
  env_file="/root/.hermes/profiles/$agent/.env"
  echo "=== $agent .env ==="
  if [ -f "$env_file" ]; then
    grep -E 'TELEGRAM_BOT_TOKEN' "$env_file" || echo "No TELEGRAM_BOT_TOKEN found"
  else
    echo ".env file not found"
  fi
done
```

**Expected format:**
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_TOKEN_YOYO=1234567890:ABC...   # agent-specific variant
TELEGRAM_ALLOWED_USERS=7105876857
TELEGRAM_HOME_CHANNEL=-100XXXXX
```

**Verify token validity (without exposing it):**
```bash
# Extract just the bot ID (number before colon) to check if format looks right
grep -oE 'TELEGRAM_BOT_TOKEN=[0-9]+:' /root/.hermes/profiles/*/.env
```

**If tokens are present but rejected → they are revoked.** Telegram has invalidated them.

**Recovery path:**
1. Create 3 new bots via @BotFather (one per agent)
2. Update each profile's `.env` with the new token
3. Clear all gateway locks (Phase 2)
4. Restart gateways sequentially (Phase 5)

---

### Phase 5 — Verify Profile Integrity

Before restarting, ensure profiles are structurally sound:

```bash
# Check config.yaml exists and has provider/model
for agent in yoyo dmob desmond; do
  config="/root/.hermes/profiles/$agent/config.yaml"
  echo "=== $agent config.yaml ==="
  if [ -f "$config" ]; then
    grep -E '^(model|provider|base_url):' "$config" | head -5
  else
    echo "❌ config.yaml missing"
  fi
  
  # Check auth.json exists and has nous provider
  auth="/root/.hermes/profiles/$agent/auth.json"
  if [ -f "$auth" ]; then
    python3 -c "import json; a=json.load(open('$auth')); print('Providers:', list(a.get('providers',{}).keys()))"
  else
    echo "❌ auth.json missing"
  fi
done

# Verify auxiliary_client.py is valid (not corrupted)
python3 -m py_compile /root/.hermes/profiles/yoyo/home/auxiliary_client.py 2>&1 && echo "yoyo: OK" || echo "yoyo: CORRUPT"
```

**Red flags:**
- Missing `auth.json` → copy from `~/.hermes/auth.json`
- `auxiliary_client.py` syntax error → replace from `/root/.hermes/hermes-agent/agent/auxiliary_client.py`
- `home/.hermes` symlink broken → `ln -sf /root/.hermes $PROFILE_HOME/home/.hermes`

---

### Phase 6 — Restart & Verify

After fixing the root cause:

```bash
# Kill any lingering gateways
pkill -f "hermes gateway run" 2>/dev/null || true
sleep 2

# Clear ALL stale artifacts
rm -f /root/.hermes/gateway.pid
rm -f /root/.hermes/profiles/*/gateway.pid
rm -f /root/.local/state/hermes/gateway-locks/telegram-bot-token-*.lock

# Start gateways sequentially with 4s stagger
AGENTS=(yoyo dmob desmond)
for agent in "${AGENTS[@]}"; do
  profile="/root/.hermes/profiles/$agent"
  echo "Starting $agent..."
  HERMES_HOME="$profile" nohup \
    /root/.hermes/hermes-agent/venv/bin/python3 \
    /root/.local/bin/hermes gateway run \
    >> "$profile/logs/gateway.out" 2>&1 &
  sleep 4
done

# Wait for startup
sleep 10

# Verify running
ps aux | grep 'gateway run' | grep -v grep

# Check agent.log for successful connections
tail -20 /root/.hermes/logs/agent.log | grep -E '(telegram connected|Cron ticker started|ERROR)'
```

**Success indicators:**
- 3 gateway processes running (different PIDs)
- `agent.log` shows `✓ telegram connected` with recent timestamp
- No ERROR lines in last 2 minutes of agent.log
- Watchdog cron (every 15min) will report "All agents healthy"

---

## Decision Tree Summary

```
Gateways down?
├─ Check processes → None running
├─ Check lock files → Stale PIDs?
│  └─ YES → Clear locks → Attempt restart
│     └─ Crashes again → Check logs
├─ Check logs (gateway.out)
│  ├─ "PID file race" → Concurrent startup; kill all, restart sequentially
│  ├─ "Telegram bot token already in use" → Stale Telegram lock; clear it
│  ├─ "InvalidToken" / "token was rejected" → **TOKEN REVOKED** → Phase 4
│  ├─ "Model not found" → Wrong model ID in config.yaml
│  └─ "Refresh session revoked" → Nous OAuth expired → full provider migration
└─ Check .env for TELEGRAM_BOT_TOKEN (if InvalidToken)
   └─ Token present but rejected → Must regenerate via @BotFather
```

---

## Common Pitfalls

| Symptom | Misdiagnosis | Correct Approach |
|---------|--------------|-----------------|
| Gateways exit instantly, gateway.out empty | "Silent failure, investigate config" | gateway.out is stale — check agent.log for actual current errors |
| "Telegram polling conflict" warnings | "All agents failing, need full restart" | Usually transient; if persistent, check for duplicate bot tokens across agents |
| Lock files reference dead PIDs | "All clear, no action needed" | **Must clear stale locks** or gateways can't start |
| auth.json shows `nous` provider but config says `stepfun` | "Auth provider mismatch" | This is normal — auth.json stores credentials, config.yaml stores model+provider selection |
| Cannot find bot token in auth.json | "Token missing, re-auth needed" | Telegram tokens are in `.env` files, NOT in `auth.json` |
| `ps aux` shows no gateways but watchdog should restart | "Watchdog broken" | Watchdog itself is a cron job — if cron daemon is down or jobs are paused, watchdog won't run |

---

## Related Skills

- `devops/gentech-agent-reactivation` — Recovery procedures after root cause is identified
- `devops/hermes-provider-migration` — OAuth token revocation (Nous Portal) recovery
- `devops/hermes-vision-debug` — Debugging vision/photo analysis failures (different domain)

## Notes

**Discovered 2026-04-22:** Telegram bot token revocation is a silent killer — gateways fail with `InvalidToken` and exit immediately. Tokens are stored in profile `.env` files, not in `auth.json`. The fix requires manual @BotFather interaction; no automated recovery exists.

**Log hygiene:** Always check `agent.log` for current state. `gateway.out` may contain pre-restart error banners that are no longer relevant due to log file reuse.
