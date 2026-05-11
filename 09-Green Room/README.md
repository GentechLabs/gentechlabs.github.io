# Green Room — Agent Coordination Hub

**Purpose:** Lightweight, file-based coordination between agents. Drop handoffs here before starting work. Check before you begin.

**Rule:** If it's not in the Green Room, it didn't happen.

---

## How It Works

1. **Before starting work** → Check `active-handoffs/` for anything tagged to you
2. **When finishing work** → Drop a handoff file for the next agent
3. **When blocked** → Write a blocker note so Gentech can escalate

## Structure

```
09-Green Room/
├── README.md                 # This file
├── active-handoffs/          # Live handoffs between agents
│   └── {from}-to-{to}-{topic}.md
├── block/                   # Blockers needing Jordan's attention
│   └── {project}-blocker.md
└── completed/               # Archived handoffs (moved after completion)
    └── {from}-to-{to}-{topic}.md
```

## Handoff Format

Every handoff file uses this template:

```markdown
## Handoff: [Topic]
- **From:** [Agent]
- **To:** [Agent]
- **Status:** ready | in-progress | blocked
- **Priority:** P0 | P1 | P2
- **Created:** [YYYY-MM-DD HH:MM UTC]
- **Deadline:** [If applicable]

### What's Done
- [Specific accomplishments]

### What's Next
- [Concrete next steps the recipient should take]

### Context
- [Any relevant vault paths, decisions made, blockers encountered]

### Blockers
- [List any blockers preventing progress]
```

## Enforcement

- **ACK within 2 hours** of receiving a handoff
- **Update status** as you work (ready → in-progress → completed)
- **Move to `completed/`** when done
- **Escalation:** No ACK in 4h → Gentech nudges. 12h → Jordan.

---

**Last updated:** 2026-05-10 23:26 UTC
**Established by:** Jordan (Option B — Lightweight Coordination)
