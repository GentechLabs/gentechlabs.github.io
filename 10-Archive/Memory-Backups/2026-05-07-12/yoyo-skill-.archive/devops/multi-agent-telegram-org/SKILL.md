---
name: multi-agent-telegram-org
description: Set up multiple Hermes agents as a coordinated Telegram organization with smart routing, shared vault access, and specialist groups.
color: purple
emoji: 🤖
vibe: Orchestrator pattern — one coordinator routes to specialists who work in their own groups.
tools: terminal, file, cronjob
---

# Multi-Agent Telegram Organization

Set up multiple Hermes agents as a coordinated team on Telegram, each with their own persona, department, and specialist Telegram group.

## When To Use
- You need multiple AI agents with different roles on Telegram
- You want an orchestrator pattern (one coordinator routes to specialists)
- Agents need shared context (Obsidian vault, file system)
- You want agents working in separate Telegram groups with observers

## Prerequisites
- Hermes Agent installed
- Telegram bot tokens (one per agent, from @BotFather)
- Node.js 22+ (for Obsidian Headless if using vault sync)
- `tmux` installed

## Setup Steps

### 1. Create Agent Profiles
Each agent gets its own Hermes profile with isolated config, sessions, and SOUL.md.

```bash
hermes profile create yoyo --clone
hermes profile create dmob --clone
hermes profile create desmond --clone
```

### 2. Configure Each Profile

**Copy auth.json** — the `--clone` flag does NOT copy auth.json. Copy it manually or agents will get "Provider authentication failed":
```bash
cp ~/.hermes/auth.json ~/.hermes/profiles/yoyo/auth.json
cp ~/.hermes/auth.json ~/.hermes/profiles/dmob/auth.json
cp ~/.hermes/auth.json ~/.hermes/profiles/desmond/auth.json
```

**Set each agent's bot token** in their profile's `.env`:
```bash
# ~/.hermes/profiles/yoyo/.env
TELEGRAM_BOT_TOKEN=<yoyo-bot-token>
TELEGRAM_ALLOWED_USERS=<your-telegram-user-id>
TELEGRAM_HOME_CHANNEL=<main-hq-group-id>
```

**Set model config** in each profile's `config.yaml`:
```yaml
model:
  default: xiaomi/mimo-v2-pro
  provider: nous
  base_url: https://inference-api.nousresearch.com/v1
```

### 3. Write SOUL.md for Each Agent
Each profile's SOUL.md defines their personality, domain, rules, and smart routing protocol.

### 4. Start Gateways via tmux
Each agent needs its own gateway process:
```bash
for name in yoyo dmob desmond; do
  profile_home="$HOME/.hermes/profiles/$name"
  tmux new-session -d -s "bot-$name" -x 120 -y 40 \
    "HERMES_HOME=$profile_home hermes gateway run"
done
```

### 5. Verify Connections
```bash
tail -5 ~/.hermes/profiles/yoyo/logs/agent.log
# Look for: "✓ telegram connected"
```
Note: tmux pane may show frozen "Starting..." even after success. Check log file.

## Smart Routing Protocol

### The Orchestrator Pattern

**Core principle:** Specialists are ON-DEMAND, not always-on. They only activate when:
1. **Routed to** by the orchestrator (Gentech)
2. **@mentioned directly** by Jordan or another agent
3. **Cron job triggers** their scheduled task
4. **Explicit handoff** in Green Room

**They stay silent when:**
- General conversation in shared groups
- Messages not addressed to them
- Tasks outside their domain
- Orchestrator is handling coordination

**Why:** Idle agents burn ~10-20K tokens per message in every group they're in. On-demand activation reduces idle token burn by 60-70%.

### Routing Flow
```
User → HQ (Orchestrator) → Analyze content → Route to specialist → Specialist works → Report back to HQ
```

### Content-Based Routing

Orchestrator reads EVERY message and routes based on content analysis:

**High confidence (>80%):** Route immediately
**Medium confidence (50-80%):** Route with "cc: @Jordan"
**Low confidence (<50%):** Ask Jordan before routing

### Domain-to-Agent Map

| Domain | Agent | Group | Trigger Keywords |
|--------|-------|-------|-----------------|
| Tokenomics, LP, yield, market analysis | YoYo | Strategies | token, price, portfolio, LP, yield, farm, DeFi, research |
| Smart contracts, code, deployment, security | DMOB | Labs | contract, Solidity, deploy, audit, security, code |
| Content, social media, hackathon submissions | Desmond | Entertainment | post, tweet, content, social, hackathon, submission |
| Coordination, status, approvals, emergencies | Gentech | HQ | (self-handle) |

**Rule of thumb:** If it involves writing code or on-chain logic → Labs. If it involves numbers/economics without code → Strategies. If it involves words/brand/pitch → Creative.

### Context Injection

Before routing, orchestrator reads specialist context files:
- `03-Strategies/agent-memory/yoyo-context.md`
- `03-Strategies/agent-memory/dmob-context.md`
- `03-Strategies/agent-memory/desmond-context.md`

Injects relevant context (current projects, blockers, recent work, preferences). This way specialists don't need persistent memory — context comes from vault.

### Routing Format

```
📊 @YoYo — [Task Type]
[Context from message]
Priority: [High/Medium/Low]
Deadline: [If applicable]
```

```
🔧 @DMOB — [Task Type]
[Context from message]
Priority: [High/Medium/Low]
Deadline: [If applicable]
```

```
📢 @Desmond — [Task Type]
[Context from message]
Priority: [High/Medium/Low]
Deadline: [If applicable]
```

### Multi-Specialist Tasks

Some messages need multiple agents:
- **Primary + Secondary:** Route to primary, CC secondary if needed
- **Sequential:** "YoYo analyzes, then DMOB implements"
- **Parallel:** "YoYo and Desmond work on this together"

### Routing Rules
1. Always route with context — don't just tag
2. Read specialist context before routing
3. Track routing accuracy for weekly review
4. Escalate to Jordan when blocked or uncertain
5. Use Green Room for cross-department coordination
6. Agents do NOT respond in HQ unless explicitly asked
7. Agents do NOT ask the user questions in HQ — route to your group first
8. **Always relay a summary to HQ after routing** — Jordan needs to see what's happening

### Agent Culture: Debate, Don't Just Execute
Jordan expects agents to THINK and PUSH BACK, not just run commands:
- When Jordan shares an idea, agents should have opinions — agree, disagree, suggest alternatives
- Write thoughts to Green Room or Mess Hall, not just your own group
- Build on each other's ideas — if one agent writes something, others should engage
- Jordan doesn't want yes-men. Challenge assumptions. Offer better versions.
- Cross-pollinate: YoYo should comment on DMOB's contract designs, DMOB should flag security in YoYo's strategies

### Token Optimization Tracking

Track routing accuracy and token savings:
- **Correct routes:** Specialist handles task successfully
- **Misroutes:** Task had to be re-routed
- **Misses:** Message needed routing but was ignored
- **False positives:** Routed when should have stayed silent

Review weekly in vault: `03-Strategies/token-optimization-tracker.md`

## Shared Context: Three Spaces
1. **Telegram Groups** — real-time, observers can watch
2. **Green Room** (vault folder) — active collaboration, handoffs
3. **Mess Hall** (vault folder) — stopping points, status dumps

## Obsidian Vault Sync
```bash
npm install -g obsidian-headless
ob login --email <email> --password <password>
ob sync-setup --vault "VaultName" --path /root/vaults/myvault \
  --password <encryption-password> --device-name server
cd /root/vaults/myvault && ob sync
```

## Cron Job Routing
Create cron jobs per domain, delivering to the specialist group:
```
hermes cron create "0 6,10,14,18 * * *" \
  --name "YoYo — LP Watchlist Check" \
  --deliver "telegram:<strategies-group-id>" \
  --prompt "Check LP positions, report APR/IL..."
```
Keep a `cron-registry.md` in the vault's skills folder tracking all jobs, IDs, and schedules.

## Vault Restructuring Tips
When vaults grow organically, watch for:
- **Duplicate Green Rooms** — agents won't know which to use. Merge into ONE `09-Green Room/`.
- **Duplicate number prefixes** — `03-Projects`, `03-Strategies`, `03-Technical` confuses agents. Consolidate.
- **Root-level clutter** — images/PDFs at root. Move to `assets/`.
- **Stale state files** — old `agent-states/` accumulate. Archive regularly.

Recommended folder structure:
```
00-Inbox/  01-Agency/  02-Labs/  03-Strategies/  04-Creative/
05-Learning/  06-Security/  07-Ideas/  08-Daily/
09-Green Room/  10-Archive/  11-Mess Hall/  12-Skills/  assets/
```

## What --clone Does and Doesn't Copy

`hermes profile create NAME --clone` copies:
- ✅ `.env` (environment variables)
- ✅ `config.yaml` (configuration)

It does NOT copy:
- ❌ `auth.json` (OAuth tokens) — **copy manually or agents fail auth**
- ❌ `skills/` — reinstall or git clone manually
- ❌ `sessions/`, `memories/`, `state.db` — clean slate
- ❌ `cron/` — no cron jobs carry over
- ❌ `SOUL.md` — write fresh per agent

Always copy after cloning:
```bash
cp ~/.hermes/auth.json ~/.hermes/profiles/<name>/auth.json
# Reinstall skills or clone from GitHub
cd ~/.hermes/skills && git clone <repo> <category>/<name>
```

## Pitfalls

1. **auth.json not cloned** — `--clone` copies .env and config.yaml but NOT auth.json. Copy it manually or agents get "Provider authentication failed: Hermes is not logged into Nous Portal."

2. **Bot token truncation** — If a token is shorter than ~46 chars, Telegram rejects it with `InvalidToken`. Regenerate via @BotFather.

3. **Gateway shows "Starting..." forever in tmux** — The tmux pane display freezes. The gateway IS running. Verify via log file: `tail -5 ~/.hermes/profiles/<name>/logs/agent.log` — look for "✓ telegram connected".

4. **Obsidian E2E encryption** — `ob sync-setup` requires `--password` flag if vault has encryption. Without it: "Failed to validate password."

5. **Memory overflow** — With multiple profiles, memory fills up fast. Consolidate entries, avoid saving task progress.

6. **Duplicate .env tokens** — If .env has both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_BOT_TOKEN_<NAME>`, the first one wins. For profiles, overwrite the main `TELEGRAM_BOT_TOKEN` line with the agent-specific token.

7. **Token precedence: gateway reads ONLY base token** — The Hermes gateway reads `TELEGRAM_BOT_TOKEN` (typically line 402) and does **NOT** fall back to `TELEGRAM_BOT_TOKEN_<NAME>` overrides. Agent-specific token lines are never consulted during gateway startup. If the base token is invalid, the agent fails to connect regardless of what agent-specific lines contain. Fix: ensure **line 402** contains a valid bot token for that agent.

8. **Cross-contamination causes startup failure** — If multiple profiles were copy-pasted from a template and each `.env` contains tokens for **all** agents (not just its own), the gateway will attempt to use every token found, producing confusing "token already in use" or generic "InvalidToken" errors. Cleanup: remove all `TELEGRAM_BOT_TOKEN_<OTHER_NAME>` lines from each profile's `.env`, leaving only its own token on line 402. Do this before attempting token regeneration.

9. **Agent token is different from bot token** — An agent like YoYo has a bot identity (@JetsetRadiobot) and a bot token. The agent-specific naming (`TELEGRAM_BOT_TOKEN_YOYO`) is just a convenience; the gateway **ignores** this label. You must copy its value into the base `TELEGRAM_BOT_TOKEN` line for the gateway to use it.

10. **Use raw HTTP calls to validate tokens** — Python's LLM output masking can hide token values (`***`), making local validation unreliable. Use subprocess with `sed`/`grep` to extract raw token strings, then test with `curl` or raw `urllib` calls: `curl -s "https://api.telegram.org/bot<token>/getMe"`. Check for `"ok":true` and the bot's username.

11. **Detect token rotation by comparing base vs agent-specific tokens** — When all agents suddenly show HTTP 401 despite previously working, run a parallel validation of all token patterns found in every `.env`. The working token (often stored as an agent-specific override) reveals which bot was rotated. Then either upgrade the base line or regenerate via @BotFather.

12. **Post-fix cleanup: delete all non-base token lines** — After resolving which token each agent should use, remove any `TELEGRAM_BOT_TOKEN_<NAME>` lines (typically 421-423) from that agent's `.env` to prevent future confusion and potential cross-contamination if templates get copy-pasted again. Each profile should have **exactly one** `TELEGRAM_BOT_TOKEN` line on or around line 402. Verify with: `grep -n '^TELEGRAM_BOT_TOKEN' ~/.hermes/profiles/<name>/.env`.

13. **Vaultnotes contain bot IDs but never full tokens** — Vault memory entries typically store bot usernames and numeric IDs (e.g., `@ProtoJaybot (8710327768)`), not full tokens. When tokens are rotated, the vault won't have the new value — you must retrieve it from @BotFather or your credential manager and update the `.env` manually.

7. **Profile config.yaml must set model** — Cloned profiles inherit model config, but if it references a provider that needs auth (like `nous`), you MUST copy auth.json too.

8. **Skills installed via hub don't carry to profiles** — Each profile has its own `HERMES_HOME`. Hub-installed skills go to the main `~/.hermes/skills/`, not profiles. If you want agents to have skills, either:
   - Install in main and symlink: `ln -s ~/.hermes/skills ~/.hermes/profiles/<name>/skills`
   - Or clone per profile (wastes disk but fully isolated)

9. **Vault sync with E2E encryption** — `ob sync-setup` requires `--password` flag if the vault has encryption. Without it you get "Failed to validate password." The encryption password is separate from the login password.

10. **Home channel misconfiguration** — Each agent's `TELEGRAM_HOME_CHANNEL` in their `.env` should point to their specialist group, NOT HQ. YoYo→Strategies, DMOB→Labs, Desmond→Creative. If all agents deliver to HQ, messages get noisy and routing breaks.

11. **Models not found on provider** — If a profile's `config.yaml` references a model that doesn't exist on the provider (e.g., `google/gemini-3-flash`), the gateway starts but agent calls fail. Verify model names match what's available on the provider.

## Troubleshooting & Restarting Agents

### Diagnose All Agents at Once

```bash
# Reliable check using /proc env + cmdline (works with or without tmux/PID files)
for name in yoyo dmob desmond; do
  echo "=== $name ==="
  pid=""
  for pid_dir in /proc/[0-9]*; do
    p=$(basename "$pid_dir")
    h=$(cat "$pid_dir/environ" 2>/dev/null | tr '\0' '\n' | grep "^HERMES_HOME=" | cut -d= -f2)
    if [ "$h" = "$HOME/.hermes/profiles/$name" ]; then
      if cat "$pid_dir/cmdline" 2>/dev/null | tr '\0' ' ' | grep -q "gateway run"; then
        pid=$p; break
      fi
    fi
  done
  if [ -n "$pid" ]; then
    echo "  PID $pid — running"
  else
    echo "  NOT running"
  fi
  tail -3 ~/.hermes/profiles/$name/logs/agent.log 2>/dev/null | grep -i "telegram\|connected\|error" || echo "  (no recent log entries)"
  echo ""
done
```

### Verify Bot Tokens

Test each bot token against the Telegram API (one at a time, no sourcing .env):
```bash
curl -s "https://api.telegram.org/bot<PASTE_TOKEN_HERE>/getMe"
# Check for "ok":true and the bot username in the response
```

### Common Issues When Agents Won't Start

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Provider authentication failed" | Missing `auth.json` | `cp ~/.hermes/auth.json ~/.hermes/profiles/<name>/auth.json` |
| Model 404 error in logs | Wrong model name in `config.yaml` | Update `model.default` to valid provider model |
| Gateway starts but no Telegram | Wrong/missing bot token | Verify token, regenerate via @BotFather if needed |
| Messages go to wrong group | `TELEGRAM_HOME_CHANNEL` wrong in `.env` | Set to specialist group ID, not HQ |
| tmux shows "Starting..." frozen | Display freeze, gateway IS running | Check `logs/agent.log` for "✓ telegram connected" |
| **"PID file race lost to another gateway instance"** | Stale `.pid` file from a previous crash | Delete stale PID files: `find ~/.hermes/profiles -name "*.pid" -delete`, then restart |

### Stale PID File Recovery

When all agents go down simultaneously (server restart, crash), leftover `.pid` files prevent restarts with "PID file race" errors. Clear before restarting:

```bash
# Clear stale PID files across all profiles
find ~/.hermes/profiles -name "*.pid" -delete

# Then restart gateways
for name in yoyo dmob desmond; do
  profile_home="$HOME/.hermes/profiles/$name"
  tmux new-session -d -s "bot-$name" -x 120 -y 40 \
    "HERMES_HOME=$profile_home hermes gateway run"
done

### Restart All Agents

```bash
# Kill existing gateway processes (tmux sessions if they exist)
for name in yoyo dmob desmond; do
  tmux kill-session -t "bot-$name" 2>/dev/null
  # Also kill any lingering gateway processes for this profile
  for pid_dir in /proc/[0-9]*; do
    p=$(basename "$pid_dir")
    h=$(cat "$pid_dir/environ" 2>/dev/null | tr '\0' '\n' | grep "^HERMES_HOME=" | cut -d= -f2)
    if [ "$h" = "$HOME/.hermes/profiles/$name" ]; then
      if cat "$pid_dir/cmdline" 2>/dev/null | tr '\0' ' ' | grep -q "gateway run"; then
        kill "$p" 2>/dev/null
      fi
    fi
  done
done

# CRITICAL: Clear stale PID files or gateways refuse to start
find ~/.hermes/profiles -name "*.pid" -delete

# Verify auth.json exists for all profiles
for name in yoyo dmob desmond; do
  [ -s ~/.hermes/profiles/$name/auth.json ] || cp ~/.hermes/auth.json ~/.hermes/profiles/$name/auth.json
done

# Start fresh (nohup background — works with or without tmux)
for name in yoyo dmob desmond; do
  profile_home="$HOME/.hermes/profiles/$name"
  cd "$profile_home" && HERMES_HOME="$profile_home" nohup /root/.hermes/hermes-agent/venv/bin/python3 /root/.local/bin/hermes gateway run >> "$profile_home/logs/gateway.out" 2>&1 &
done

# Wait and verify
sleep 8
for name in yoyo dmob desmond; do
  echo "=== $name ==="
  tail -3 ~/.hermes/profiles/$name/logs/agent.log 2>/dev/null
done
```

## Agent Watchdog & Auto-Restart

Agents can crash or go down without tmux. The reliable way to detect each agent is by matching **both** the `HERMES_HOME` environment variable AND the `gateway run` command in `/proc` — child processes (like the browser daemon) also inherit `HERMES_HOME`, so env-only matching gives false positives. PID files in the profile directories may not exist or be stale.

### Reliable Detection Method

```bash
# Find gateway PID by matching HERMES_HOME env + "gateway run" in cmdline
get_agent_pid() {
    local name="$1"
    local profile_home="$HOME/.hermes/profiles/$name"
    for pid_dir in /proc/[0-9]*; do
        local pid=$(basename "$pid_dir")
        local hermes_home=$(cat "$pid_dir/environ" 2>/dev/null | tr '\0' '\n' | grep "^HERMES_HOME=" | cut -d= -f2)
        if [ "$hermes_home" != "$profile_home" ]; then continue; fi
        local cmdline=$(cat "$pid_dir/cmdline" 2>/dev/null | tr '\0' ' ')
        if echo "$cmdline" | grep -q "gateway run"; then
            echo "$pid"; return 0
        fi
    done
    return 1
}
```

### Watchdog Script + Cron

Place at `~/.hermes/scripts/agent-watchdog.sh`:

```bash
#!/bin/bash
PROFILES=("yoyo" "dmob" "desmond")
HERMES_BASE="$HOME/.hermes/profiles"
LOG="/tmp/agent-watchdog.log"

get_agent_pid() {
    local name="$1"
    for pid_dir in /proc/[0-9]*; do
        local pid=$(basename "$pid_dir")
        local hermes_home=$(cat "$pid_dir/environ" 2>/dev/null | tr '\0' '\n' | grep "^HERMES_HOME=" | cut -d= -f2)
        if [ "$hermes_home" != "$HERMES_BASE/$name" ]; then continue; fi
        if cat "$pid_dir/cmdline" 2>/dev/null | tr '\0' ' ' | grep -q "gateway run"; then
            echo "$pid"; return 0
        fi
    done
    return 1
}

restart_agent() {
    local name="$1"
    local profile_home="$HERMES_BASE/$name"
    rm -f "$profile_home/gateway.pid" "$profile_home/gateway.json"
    [ -s "$profile_home/auth.json" ] || cp "$HOME/.hermes/auth.json" "$profile_home/auth.json"
    cd "$profile_home" && HERMES_HOME="$profile_home" nohup /root/.hermes/hermes-agent/venv/bin/python3 /root/.local/bin/hermes gateway run >> "$profile_home/logs/gateway.out" 2>&1 &
    sleep 8
    local new_pid=$(get_agent_pid "$name")
    if [ -n "$new_pid" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') [$name] ✅ Restarted (PID $new_pid)" | tee -a "$LOG"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') [$name] ❌ Restart failed" | tee -a "$LOG"
    fi
}

for name in "${PROFILES[@]}"; do
    pid=$(get_agent_pid "$name")
    if [ -z "$pid" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') [$name] ❌ Not running — restarting" | tee -a "$LOG"
        restart_agent "$name"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') [$name] ✅ Running (PID $pid)" | tee -a "$LOG"
    fi
done
```

Set up the cron job:

```bash
hermes cron create "every 15m" \
  --name "Agent Watchdog" \
  --prompt "Run /root/.hermes/scripts/agent-watchdog.sh and report the output summary. Flag urgently if any agent failed to restart."
```

### Key Insight

Agents started with `hermes gateway run` run as standalone background processes (not necessarily in tmux). The browser daemon child process also has `HERMES_HOME` set, so **always verify the cmdline contains "gateway run"** to avoid false positives when detecting running agents.

### Home Channel Mapping

Each agent's `.env` should have their specialist group as home:
```bash
# YoYo → Strategies
TELEGRAM_HOME_CHANNEL=-1002916759037

# DMOB → Labs
TELEGRAM_HOME_CHANNEL=-1003872552815

# Desmond → Creative/Entertainment
TELEGRAM_HOME_CHANNEL=-1003893562036
```

Update with:
```bash
sed -i 's/TELEGRAM_HOME_CHANNEL=.*/TELEGRAM_HOME_CHANNEL=<group-id>/' ~/.hermes/profiles/<name>/.env
```

12. **Channel directory missing a group** — Even if a bot is admin in a Telegram group, the group may not appear in `channel_directory.json`. The directory is cached and rebuilt on gateway start. If a group is missing, the agent can send messages there but won't receive/process incoming messages from that group. Fix: restart the gateway. To diagnose: check `channel_directory.json` for the group ID. Send a message in the group as the bot to trigger discovery if restart doesn't fix it.

13. **Verify capabilities before reporting them missing** — Always check the profile's `config.yaml` auxiliary section before telling Jordan a feature isn't configured. Vision, TTS, and other subsystems may already be active. Reporting a missing feature that's already set up erodes trust.

## Boot-Up Recovery Protocol (SOUL.md Addition)

Add this section to each agent's SOUL.md so they never start cold. When agents restart, they should arrive with context and greet Jordan proactively.

```markdown
## 🚀 Boot-Up Recovery Protocol
**Run this EVERY time you start up or come back online.** Do NOT wait for Jordan to message you first.

### Step 1: Check Your Memory
- Read your `memory.md` and scan `memories/` for recent context
- Look at `session_search` for your last 3 sessions — what were you working on?

### Step 2: Check the Vault
- Read the latest Mess Hall notes (`11-Mess Hall/`) — what was the last status?
- Check Green Room (`09-Green Room/`) for any pending handoffs addressed to you
- Scan your domain folders for recent changes

### Step 3: Check GitHub
- Run `gh notification` or check your repos for recent activity
- Any PRs, issues, or commits since you were last online?

### Step 4: Greet Jordan
After gathering context, send a message in your group:
- "I'm back. Last thing I was working on: [summary]"
- "Anything pending from before: [list]"
- "What should we focus on next?"

**Never start a session cold.** Always arrive with context.
```

Telegram naturally queues messages while a bot is offline — when it reconnects via polling, all missed messages are delivered. No extra queueing setup needed.
