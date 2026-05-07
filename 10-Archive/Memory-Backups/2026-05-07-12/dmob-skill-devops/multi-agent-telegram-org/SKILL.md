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
```
User → HQ (Orchestrator) → Analyze → Route to specialist group → Agent works → Summary back to HQ
```

### Department Groups Are Work Channels (Jordan Directive, May 2026)

The three department groups exist for **work output**, not side conversations:
- **Strategies** → investment & research work
- **Labs** → development & contracts work
- **Entertainment** → content & social work

Side conversations are fine, but the primary purpose is work. When a cron job or agent produces results, deliver to the department that owns the work type — not where the job was created.

### Agent SOUL.md Rules:
1. Agents do NOT respond in HQ unless explicitly asked
2. Agents do NOT ask the user questions in HQ — route to your group first
3. Report summaries to HQ when work is done or blocked
4. Need another agent? Post in shared coordination space
5. Department groups are for work — keep side conversations brief, don't derail the work channel

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

### Routing Rule (Jordan Directive)
Cron job results must deliver to the **department group that owns the work type**, not where the job was created. Config work happens in HQ, but results go to the specialist group.

| Work Type | Delivers To |
|-----------|-------------|
| DeFi research, LP data, market analysis | Strategies |
| Smart contract scanning, security contests, hackathon opportunities | Labs |
| Content, social media, X posts | Entertainment |
| System admin, backups, coordination | HQ |

### Routing Audit Protocol
Run quarterly or when Jordan says "check the cron routing":

```bash
# Pull all cron jobs across all profiles
for profile in /root/.hermes/profiles/*/; do
  name=$(basename "$profile")
  if [ -f "$profile/cron/jobs.json" ]; then
    echo "=== $name ==="
    python3 -c "
import json
with open('$profile/cron/jobs.json') as f:
    data = json.load(f)
jobs = data if isinstance(data, list) else data.get('jobs', [])
for j in jobs:
    print(f'  {j.get(\"name\",\"?\")} → {j.get(\"deliver\",\"origin\")}')
" 2>/dev/null
  fi
done
```

### Channel ID Reference
Keep current IDs in `channel_directory.json` per profile. Map:
- `origin` = wherever the job was created (may be wrong!)
- `telegram:<ID>` = explicit routing (correct)

### Red Flags
- Job delivering to `origin` but created in HQ while results belong to Strategies
- Truncated channel IDs (missing digits → delivery fails silently)
- Jobs delivering to wrong department (e.g., DeFi data going to Labs)

### Keep a Cron Registry
Maintain `cron-registry.md` in vault tracking all jobs, IDs, schedules, and correct delivery targets.

```bash
hermes cron create "0 6,10,14,18 * * *" \
  --name "YoYo — LP Watchlist Check" \
  --deliver "telegram:<strategies-group-id>" \
  --prompt "Check LP positions, report APR/IL..."
```

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

6. **Duplicate .env tokens cause collisions** — If a profile's `.env` accidentally contains ALL agent tokens (from a copy/paste), the gateway loads every `TELEGRAM_BOT_TOKEN*` entry. At startup it tries to register each token with Telegram; if multiple profiles have the same tokens this creates \"token already in use\" or 401 race conditions. **Fix**: Each profile's `.env` must contain **exactly one** active token — either `TELEGRAM_BOT_TOKEN=<agent's_token>` on line 402, or `TELEGRAM_BOT_TOKEN_<NAME>=<agent's_token>` if used. Delete all other agent tokens from that profile's .env.

7. **Profile config.yaml must set model** — Cloned profiles inherit model config, but if it references a provider that needs auth (like `nous`), you MUST copy auth.json too.

8. **Skills installed via hub don't carry to profiles** — Each profile has its own `HERMES_HOME`. Hub-installed skills go to the main `~/.hermes/skills/`, not profiles. If you want agents to have skills, either:
   - Install in main and symlink: `ln -s ~/.hermes/skills ~/.hermes/profiles/<name>/skills`
   - Or clone per profile (wastes disk but fully isolated)

9. **Vault sync with E2E encryption** — `ob sync-setup` requires `--password` flag if the vault has encryption. Without it you get "Failed to validate password." The encryption password is separate from the login password.

## Token Recovery & 401 Troubleshooting

When all bots return HTTP 401 Unauthorized:

**Diagnostic workflow:**
1. Extract raw tokens bypassing LLM masking: `sed -n 402p ~/.hermes/.env` (or per-profile path). Note: tokens redacted in this interface show as `***` but raw bytes contain full values.
2. Test each token via Telegram API: `curl "https://api.telegram.org/bot<token>/getMe"`. Valid tokens return bot info; invalid return 401.
3. Check vault `agent-ping-system.md` and memory backups under `10-Archive/Memory-Backups/` for bot ID → username mappings and any "TOKEN REFRESHED" notes (bot IDs never change, only the token part does).
4. Profile's .env may contain both a base token (`TELEGRAM_BOT_TOKEN` on line 402) and an agent-specific override (`TELEGRAM_BOT_TOKEN_<NAME>` on lines 421–423). Agent-specific lines often hold the rotated/new token while the base line is stale.
5. Confirm no duplicate tokens exist across profiles (shared tokens cause instantaneous 401s when multiple profiles try to register them).

**Order of recovery:**
- If an agent-specific token (e.g., `TELEGRAM_BOT_TOKEN_YOYO`) validates, use that and clear the base line (or comment it) to avoid confusion.
- If no valid token exists, regenerate via @BotFather for `@ProtoJaybot`, `@JetsetRadiobot`, `@FollowTheCodebot`, `@Redhotforgebot` using the documented bot IDs (8710327768, 8727765280, 8744130315, 8640344678).
- Update only that agent's profile `.env` with the fresh token and restart its gateway.

**Post-fix verification:**
- Gateway log should show `✓ telegram connected`
- `sendMessage` to the agent's group should succeed
- Channel cache directory (`.hermes/channels/<platform>/`) should populate with group metadata
