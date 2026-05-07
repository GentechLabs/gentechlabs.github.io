---
name: shared-workspace-sync
description: Synchronize shared workspaces (Obsidian vaults, git repos, knowledge bases) across multi-agent teams — enabling agents to read/write context, hand off via shared brain, and maintain persistent memory across independent Hermes profiles.
version: 0.1.0
author: Gentech Labs
license: MIT
metadata:
  hermes:
    tags: [obsidian, sync, vault, multi-agent, shared-memory, coordination]
    homepage: https://github.com/obsidianmd/obsidian-headless
---

# Shared Workspace Sync for Multi-Agent Teams

**Why this matters:** When multiple Hermes agents work in parallel (via Kanban or independent profiles), they need a shared context layer. Obsidian vaults with headless sync act as a "collective brain" — agents write findings, other agents read full history, decisions are preserved across sessions.

Supported backends:
- **Obsidian Headless** (primary) — real-time vault sync via obsidian.md cloud
- **Git** (fallback) — simple push/pull with vault as git repo
- **Local shared directory** (development) — direct filesystem access (no network)

## Quick Start (Obsidian Headless)

### Prerequisites
- Node.js >= 20 (v22 LTS recommended) — includes WebCrypto required by obsidian-headless
- npm (comes with Node)
- Obsidian account (email + password) for cloud vault hosting

### Installation
```bash
# 1. Install Node.js from official binaries if apt fails
# (See scripts/install-node.sh for automated install from nodejs.org)

# 2. Install obsidian-headless globally
npm install -g obsidian-headless

# 3. Link binary if not in PATH (check with: which ob)
# Usually automatic, but if 'ob' command not found:
ln -sf /usr/local/node/bin/ob /usr/local/bin/ob

# 4. Verify
ob --version  # should print '0.0.8'
ob --help     # should show commands
```

Note: Package name is `obsidian-headless` (not `obsidian-headless-sync`). Binary is `ob`.

### Configuration
```bash
# Log in to Obsidian (opens browser for device code flow, or prompts for email/password)
ob login

# List available remote vaults
ob sync-list-remote

# List locally configured vaults (empty first time)
ob sync-list-local

# Set up sync: link local vault path to a remote vault
ob sync-setup --vault "GenTech-Brain" --path /root/vaults/gentech

# Or create a new remote vault if needed
ob sync-create-remote --name "GenTech-Brain"

# Check sync status
ob sync-status
```

### Running as a Daemon
```bash
# One-way sync (local → remote) every 30 seconds
watch -n 30 'ob sync'

# Or use cron for scheduled sync
hermes cron create "every 1m" --prompt "Run 'ob sync' to push vault changes" --name "Vault Sync Push"

# For continuous bidirectional sync, run in background:
ob sync --watch &  # if supported, otherwise use cron + pull jobs
```

## Integration with Hermes Multi-Agent Workflows

### Agent Writing to Vault
```python
# In an agent task, use the file tool to write findings:
# File: 03-Projects/ActiveProject/agent-notes/2026-05-03-yoyo-morning-sync.md
---
agent: YoYo
role: DeFi Strategist
timestamp: 2026-05-03T09:00:00Z
tags: [lff, lp, monitoring]
---
Today's LFJ pool rebalance detected at block #2345678.
New range: $9.00-$9.45 (was $8.70-$9.20).
Position size increased by 12%.

Recommendation: monitor for volatility spike in the next 4 hours.
```

**Rule:** Agents must write to the vault after every meaningful sub-step. The vault is the single source of truth — if an agent crashes or gets cancelled, its partial progress remains readable.

### Agent Reading from Vault
**Before starting ANY task:**
1. Sync latest: `ob sync --pull` (or `git pull` if git backend)
2. Read relevant files in `00-HQ/`, `03-Projects/`, `01-Agency/`
3. Check `02-Labs/Hackathons/Active/` for in-progress work
4. Search recent daily notes for context (`grep -r "keyword" .` if needed)
5. Summarize what you found in your first message to the user (or in the Kanban comment thread)

**After reading:** Update the task's Kanban card with links to specific vault pages you consulted. This creates an audit trail.

### Green Room Coordination
Use the vault as the "collective brain" during cross-department syncs:
- Gentech (CEO) writes strategic decisions to `00-HQ/Decisions/`
- YoYo (Strategist) logs market findings to `03-Strategies/Market-Intel/`
- DMOB (Trading) posts trade rationales to `03-Strategies/Trade-Journal/`
- Desmond (Content) drafts announcements in `06-Content/Drafts/`

Agents hand off by:
1. Writing a summary note in the vault
2. Updating the Kanban task with a `[[vault-link]]` to that note
3. The next agent clicks the link (or reads the file) to get full context

**Never rely on chat history alone** — vault files survive process crashes and gateway restarts.

### Green Room Coordination
Use the vault as the "single source of truth" during cross-department syncs:
- Gentech (CEO) writes strategic decisions to `00-HQ/Decisions/`
- YoYo (Strategist) logs market findings to `03-Strategies/Market-Intel/`
- DMOB (Trading) posts trade rationales to `03-Strategies/Trade-Journal/`
- Desmond (Content) drafts announcements in `06-Content/Drafts/`

Agents hand off by updating the Kanban task with vault links; next agent reads those links.

## Fallback: Git-Based Sync (No External Service)

If Obsidian cloud is unavailable or you prefer zero-cost:
```bash
# Initialize vault as git repo (one-time)
cd /root/vaults/gentech
git init
git remote add origin git@github.com:Gentech-Labs/gentech-vault.git

# Agent workflow:
git pull origin main   # before starting work
# ... make changes ...
git add .
git commit -m "Agent [name]: [brief description]"
git push origin main

# Cron for auto-sync (every 5 min)
hermes cron create "every 5m" --prompt "git -C /root/vaults/gentech pull --rebase origin main" --name "Vault Git Pull"
```

Git is simpler but lacks real-time conflict resolution. Use for backup; prefer Obsidian headless for active team sync.

## Pitfalls & Troubleshooting

### Node.js Installation Failures
- **Symptom:** `apt-get install nodejs` fails with dpkg errors
- **Fix:** Run `dpkg --configure -a` first, then retry. Or bypass apt entirely — download official binaries from nodejs.org (see `scripts/install-node.sh`)

### npm Global Binaries Not in PATH
- **Symptom:** `ob: command not found` after `npm install -g obsidian-headless`
- **Diagnosis:** `npm root -g` shows `/usr/local/node/lib/node_modules`, but `/usr/local/node/bin` may not be symlinked to `/usr/local/bin`
- **Fix:** `ln -sf /usr/local/node/bin/ob /usr/local/bin/ob`

### WebCrypto Not Available
- **Symptom:** `ReferenceError: crypto is not defined` when running `ob`
- **Cause:** Node.js < 20 or custom build without WebCrypto
- **Fix:** Use Node >= 20 (v22 LTS recommended). Verify: `node -e "console.log('webcrypto' in globalThis)"` must print `YES`

### Wrong Package Name
- **Do NOT:** `npm install -g obsidian-headless-sync` (doesn't exist)
- **DO:** `npm install -g obsidian-headless`

### OAuth Token Revocation (Nous Portal)
- **Symptom:** `RuntimeError: Refresh session has been revoked` across all Hermes profiles
- **Impact:** LLM API calls fail; cron jobs stop
- **Fix:** On each profile, run `hermes model` → re-authenticate via OAuth → `hermes gateway restart --profile <name>`
- **See:** `hermes-agent` skill section "OAuth session revocation (fleet-wide)"

### Cron Jobs Stuck with Past-Due `next_run_at`
After gateway restarts, scheduled jobs may have `next_run_at` in the past and never fire.
- **Fix:** Run the timestamp recalculation script in `scripts/fix-cron-timestamps.py`

## Support Files

- `scripts/install-node.sh` — Automated Node.js binary install from nodejs.org (bypasses apt issues)
- `scripts/fix-cron-timestamps.py` — Recalculates stale cron `next_run_at` timestamps across all profiles
- `scripts/vault-sync-daemon.sh` — Runs `ob sync` in a loop with exponential backoff
- `references/installation-session-2026-05-03.md` — Full install session log, error messages, and exact versions used

## Related Skills

- `hermes-agent` — Hermes configuration, OAuth recovery, multi-agent Kanban workflows
- `note-taking` — Obsidian vault structure conventions, daily note format, tag taxonomy
- `agent-coordination` — Green Room protocols, task handoff patterns, delegation rules

---

## Changelog

**2026-05-03** — v0.1.0: Initial skill. Captures Node 22 + obsidian-headless setup, PATH linking fix, WebCrypto requirement, fallback git sync pattern.