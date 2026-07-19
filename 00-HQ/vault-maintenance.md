# Vault Maintenance Convention

**Rule:** Files get updated or archived. Never left to rot.

## Cleanup Triggers

- **Files older than 30 days** without modification → archive or delete
- **Stale strategy docs** → archive to `11-Mess Hall/archive/`
- **Completed builds** → update `build_queue.json` status immediately
- **Old context snapshots** → archive after new session starts
- **node_modules / build artifacts** → never commit to vault

## Vault Structure

```
00-HQ/              — Coordination, decisions, blockers, status
01-HANDOFFS/        → Gentech → Forge
02-HANDOFFS/        ← Forge → Gentech (Forge writes here)
09-Green Room/      — Active ideas, drafts, build logs
10-Labs/            — Active build specs, PR portfolio, architecture
11-Mess Hall/       — Active considerations, references, agent-brain
  archive/          — Stale files moved here, never deleted
```

## Agent-to-Agent Handoff Rule

1. Any agent that ships a build → updates `build_queue.json` + drops a note in the handoff folder
2. Any agent that hits a blocker → same
3. Gentech checks `02-HANDOFFS/forge-to-gentech/` at session start
4. Forge checks `01-HANDOFFS/gentech-to-forge/` at session start

## No Separate Lists

All priorities live in `scripts/build_queue.json`. Owner field tracks who owns each item. One source of truth.
