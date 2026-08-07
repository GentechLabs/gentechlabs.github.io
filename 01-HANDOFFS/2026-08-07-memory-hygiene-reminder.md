# 🧠 MEMORY HYGIENE REMINDER — All Groups (2026-08-07)

**From Jordan via Gentech HQ.** This applies to EVERY agent in EVERY Telegram group (HQ, Strategies, Labs, Entertainment, Treasury, Forge, Gizmo).

## The Problem
Agents keep filling up their context/memory mid-conversation and **forgetting to save + start fresh**. When memory hits ~85%+, the agent degrades, loses track, and drops work.

## The Fix — Save, Then /new
When you notice your memory/context getting full (or you're 25+ messages into a session):

1. **SAVE where you are** — run the context bridge save:
   ```bash
   python3 /root/.hermes/profiles/gentech/skills/gentech-ops/session-hygiene/scripts/context-save.py
   ```
   Then fill in the generated file at `09-Green Room/context-bridge/context-{timestamp}.md` with: what you were building, decisions made, blockers, next steps.

2. **COMPACT memory** — remove stale entries (>7 days), task-progress logs (PRs, commits, completed work), merge duplicates. Keep identity, preferences, environment facts.

3. **START NEW** — tell the user: *"Memory at [X]% — saved context to bridge. Ready for /new?"* Then `/new` to get a fresh session.

## The Rule (from session-hygiene skill)
- **≥80%** — Yellow. Start planning the save.
- **≥85%** — Orange. Save context snapshot, compact memory, suggest /new.
- **≥90%** — Red. Save NOW, suggest /new immediately. Do not add more memory.

## Don't Lose Work
The context bridge (`09-Green Room/context-bridge/latest-context.md`) is what wake-up reads after /new. If you save properly, nothing is lost — you resume exactly where you left off.

**Bottom line: Save where you are, then start new. Don't let memory fill up and drop the ball.**
