---
name: vault-ecosystem-restore
description: Full restore of a multi-agent ecosystem from an Obsidian vault after system rebuild — cron jobs, team protocols, vault structure, skills inventory, and coordination setup.
tags: [vault, obsidian, multi-agent, restore, telegram, rebuild]
---

# Vault Ecosystem Restore

Use after a full system rebuild or migration to restore an entire multi-agent team from their Obsidian vault. Goes beyond cron jobs — covers team structure, protocols, vault reorganization, and skills inventory.

## When to Use
- VPS rebuild or migration
- Agent auth lost, need to reconnect everything
- User says "restore everything" or "get us back up"
- Vault is synced but no agents/cron/structure exist yet

## Phase 0: Vault Access
Ensure the vault is synced and readable:
```bash
ls /root/vaults/gentech/
```
If not synced, set up Obsidian Headless Sync (`npm install -g obsidian-headless && ob login`).

## Phase 1: Read the Brain (Source of Truth)
Read these files IN ORDER — each builds context on the next:

1. **`INDEX.md`** — Vault structure overview, agent roles
2. **`12-Skills/agents-protocol.md`** — Team communication rules, routing map, folder assignments
3. **`12-Skills/cron-registry.md`** — All cron job definitions with schedules and delivery targets
4. **`12-Skills/cron-routing.md`** — Which domain routes to which Telegram group
5. **`12-Skills/Skills-Tracker.md`** — Installed and pending skills inventory
6. **`00-Working-Memory.md`** — Active projects, open loops, recent decisions
7. **`GenTech-Channel-Map.md`** — Telegram group ↔ vault folder mapping

## Phase 2: Restore Cron Jobs
Use the `cron-job-restore` skill for this phase. Key rules:
- Read cron-registry.md for all job definitions
- Group jobs by delivery target (HQ, Strategies, Labs, Entertainment, Origin, Local)
- Batch create by group — don't mix groups in one batch
- Skip paused/disabled jobs unless user wants them
- **Job IDs will change** — update the vault registry after
- Update change log in cron-registry.md with timestamp and new IDs

## Phase 3: Vault Structure Audit & Repair
Check for common issues after rebuilds:

### Duplicate folders
- Multiple folders with same number prefix (e.g., two `03-` folders)
- Multiple Green Rooms (`09-Green Room/`, `13-Green Room/`, `green-room/`)
- Merge duplicates into one canonical location

### Root clutter
- Image files (.jpg, .png) sitting at root → move to `assets/`
- Loose .md files that belong in specific folders

### Recommended structure
```
vault/
├── 00-Inbox/          # Unsorted intake
├── 01-HQ/             # Business ops, LLC
├── 02-Labs/           # Dev projects (Dmob)
├── 03-Strategies/     # DeFi research (YoYo)
├── 04-Creative/       # Content, media (Desmond)
├── 05-Learning/       # Course notes
├── 06-Security/       # Audit findings
├── 07-Ideas/          # Raw brain dumps
├── 08-Daily/          # Agent states, daily logs
├── 09-Collaboration/  # Handoffs, active tasks (ONE Green Room)
├── 10-Mess Hall/      # Debriefs, opinions
├── 11-Skills/         # Protocols, cron registry
├── 12-Templates/      # Note templates
├── 13-Archive/        # Completed work
├── assets/            # Images, logos
└── references/        # External references
```

After restructuring: update `INDEX.md` and `agents-protocol.md` folder references.

## Phase 4: Skills Inventory
Review `12-Skills/Skills-Tracker.md`:
- Cross-reference with `skills_list()` to see what's built-in vs third-party
- Third-party skills need GitHub access to reinstall
- Create `Weekly Skills Update Check` cron (Sunday 9 AM) to keep skills current

### "Eat the meat, spit out the bones" evaluation
When reviewing skills (especially from awesome lists):
- **Meat**: Solves a real problem for the team, actively maintained, production-grade
- **Bones**: Experimental hacks, domain-irrelevant, cool-but-useless
- Don't install everything — curate based on team needs

## Phase 5: Team Communication Verification
Verify the multi-agent protocol is understood:
- **Gentech** receives messages → analyzes → routes to correct agent
- **YoYo** owns Strategies (DeFi, investing, research)
- **DMOB** owns Labs (smart contracts, dev, audits)
- **Desmond** owns Creative (content, media, design)
- Agents coordinate in **Green Room** before responding in Telegram
- **Mess Hall** is for afterthoughts/debriefs, not active work
- Rules: Don't duplicate responses, don't overtake other agents' domains

## Phase 6: Sync and Report
```bash
cd /root/vaults/gentech && ob sync
```
Post summary to Mess Hall (`11-Mess Hall/`) noting what was restored and what's still pending.

## Pitfalls
- **Job IDs change on recreation** — always update the vault registry
- **Don't assume vault is current** — check "Last Synced" timestamps in registry
- **Agent auth is per-instance** — each bot needs `hermes model` on their own server
- **ElevenLabs / GitHub tokens** — user provides these, don't ask for them in chat
- **Pause vs disable** — paused jobs can be resumed, disabled jobs need full recreation
- **Local delivery** means silent (no Telegram output) — use for internal scripts
