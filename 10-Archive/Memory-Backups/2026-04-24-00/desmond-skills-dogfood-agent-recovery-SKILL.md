---
name: agent-recovery
description: Recovery protocol when agents come back online — check sessions, memory, vault, cron health, then report to user.
version: 1.0
triggers:
  - "agent comes back online after downtime"
  - "session restart or reinstall"
  - "where were we / what were we doing"
  - "first message in new session"
---

# Agent Recovery Protocol

When you come back online after being offline, follow this protocol BEFORE responding to any user message.

## Recovery Steps (In Order)

### 1. Check Recent Sessions
Call `session_search()` with no arguments to see recent session titles and timestamps. This tells you what was being worked on.

### 2. Read Your Memory
Read all files in your memory directory:
- `/root/.hermes/profiles/desmond/memory/` (if you're Desmond)
- `/root/.hermes/profiles/yoyo/memory/` (if you're YoYo)
- `/root/.hermes/profiles/dmob/memory/` (if you're DMOB)

### 3. Check Vault for Active Work
Read these files in order:
1. `/root/vaults/gentech/INDEX.md` — master vault index
2. `/root/vaults/gentech/09-Green Room/` — active handoffs between agents
3. `/root/vaults/gentech/11-Mess Hall/` — recent discussions and decisions
4. `/root/vaults/gentech/10-Archive/Memory-Backups/` — latest dated backup folder

### 4. Check Cron Health
Call `cronjob(action='list')` to see all jobs. Look for:
- Any jobs with `last_status: "error"` — flag these
- Jobs that haven't run (null last_run_at) — may indicate downtime

### 5. Read Telegram Queue
The user may have sent messages while you were offline. These naturally appear in your conversation. Read them in order (oldest first), don't skip any.

### 6. Send Recovery Report
After gathering context, send a brief recovery message:

```
I'm back. Here's where we left off:
- **Last task:** [summary]
- **Status:** [done/in-progress/blocked]
- **While I was away:** [any queued messages]
- **Next up:** [what to work on]
```

## If Memory Is Completely Empty
1. Read `/root/vaults/gentech/INDEX.md`
2. Read the latest backup in `10-Archive/Memory-Backups/`
3. Read `/root/vaults/gentech/00-Working-Memory.md`
4. Check `/root/.hermes/.env` for identity confirmation
5. Tell the user: "I had a full reset — rebuilt context from vault backup"

## Pitfalls
- Don't skip recovery steps to "save time" — you'll miss context and repeat work
- Don't assume what the user wants — check the queue first, THEN ask
- The vault is the source of truth, not Telegram copy-paste
