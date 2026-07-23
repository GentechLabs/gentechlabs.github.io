# Vault Communication Protocol — The Conference Room

**How Gentech and Forge talk to each other through the vault.**

---

## The Core Idea

We don't need real-time chat between agents. We have the **vault** — a shared whiteboard where:

- **Gentech** leaves work for **Forge** → Forge picks it up next session
- **Forge** hands off to **Gentech** → Gentech continues on VPS
- **Both** brainstorm ideas → structured notes for each other and Jordan
- **Decisions** are recorded → both agents see them next session

**"Let's brainstorm in the brain"** means: write it to the vault.

---

## Trigger Phrases

| You Say | What Happens |
|---------|-------------|
| "Let's brainstorm in the brain" | Agent creates structured brainstorm in `vault/brainstorms/` |
| "Drop this in the brain" | Agent saves idea/note to `vault/ideas/` |
| "Hand this off to [Gentech/Forge]" | Agent writes structured handoff in `vault/handoffs/` |
| "[Gentech/Forge], pick this up" | Agent leaves work in the build queue for the other |
| "Note that for later" | Agent saves as context note in `vault/notes/` |
| "Log that decision" | Agent records decision in `vault/decisions/` |

---

## Vault Communication Structure

```
vault/
├── brainstorms/          # Structured brainstorming sessions
│   ├── 2026-06-28-agent-swarm-ideas.md
│   └── ...
├── handoffs/             # Work handoffs between agents
│   ├── forge-to-gentech-hackathon-planning.md
│   └── gentech-to-forge-dashboard-fix.md
├── decisions/            # Key decisions both agents need to know
│   └── 2026-06-28-router-protocol-decision.md
├── ideas/                # Quick idea drops
│   └── ...
├── queues/
│   ├── build-queue.md    # Shared task queue
│   └── handoff-log.md    # Handoff tracking
└── notes/                # General context notes
    └── ...
```

---

## How Agents Communicate

### Pattern 1: Handoff

```
Forge writes:
  vault/handoffs/forge-to-gentech-ui-framework.md
  ├── FROM: Forge
  ├── TO: Gentech
  ├── DATE: 2026-06-28
  ├── PRIORITY: Medium
  ├── CONTEXT: "Started looking at dashboard framework options. 
  │            React seems best. Need Gentech to review the 
  │            architecture before I commit."
  └── STATUS: ⏳ Waiting on Gentech

Next time Gentech starts:
  → Loads vault → sees handoff → picks it up
  → Reviews, responds, updates status
  → Leaves his own handoff back to Forge
```

### Pattern 2: Brainstorm

```
Jordan says: "Let's brainstorm the agent monetization strategy"

Forge writes:
  vault/brainstorms/2026-06-28-monetization-strategy.md
  ├── Triggered by: Jordan's request
  ├── Initial thoughts from Forge:
  │   - x402 API sales could scale with tiered pricing
  │   - Agent Kit licensing has a ceiling without marketplace
  ├── Questions for Gentech:
  │   - What's the gas cost projection for on-chain payments?
  │   - Should we explore Virtuals deeper?

Gentech picks up next session:
  → Reads the brainstorm
  → Adds his perspective
  → Answers Forge's questions
  → Leaves a consolidated strategy
```

### Pattern 3: Decision Log

```
Both agents learn of a decision:

vault/decisions/2026-06-28-router-protocol-decision.md
  ├── DECISION: Agent Router uses speaker + lane routing, not @mentions
  ├── MADE BY: Jordan
  ├── DATE: 2026-06-28
  ├── REASONING: Collaborators won't remember @mentions.
  │   Voice messages carry speaker identity naturally.
  └── IMPACTS: Both agents loaded this decision on next session
```

---

## Session Startup — Check the Conference Room

Every time an agent starts a session, it should:

1. **Load the vault** — pull latest from GitHub
2. **Check handoffs** — anything addressed to me?
3. **Read recent decisions** — anything I missed?
4. **Scan brainstorm updates** — new ideas since last session?
5. **Review build queue** — any items with my name on it?

This is already partially handled by the wake-up protocol. The vault communication protocol just formalizes the **reading** side — checking the conference room before jumping into work.

---

## Handoff Format

```markdown
# Handoff: [Title]

**From:** [Agent Name]
**To:** [Agent Name]
**Date:** [Date]
**Priority:** 🔴 High / 🟡 Medium / 🟢 Low
**Status:** ⏳ Waiting / 🟢 In Progress / ✅ Complete / 🔴 Blocked

## Context
What led to this handoff? What's the backstory?

## What's Needed
What exactly does the other agent need to do?

## Notes / Questions
- Random thoughts, uncertainties, things to consider

## Attachments
Links to relevant files, dashboards, or references
```

---

## Example: Full Workflow

```
1. Jordan: "Let's brainstorm the hackathon strategy in the brain"

2. Forge writes vault/brainstorms/hackathon-strategy.md
   - Lists upcoming hackathons with deadlines
   - Initial ideas for each
   - Questions for Gentech

3. Gentech's next session:
   - Loads vault → sees brainstorm → adds his thoughts
   - Handoff: "Forge, I covered the Qwen submission scope. 
     Can you draft the technical architecture?"
   - Writes vault/handoffs/gentech-to-forge-qwen-arch.md

4. Forge's next session:
   - Sees handoff → drafts architecture
   - Leaves decision log about tech choices
   - Updates build queue: "Qwen: architecture drafted, 
     waiting on Jordan's feedback"
```

---

## Agent Handoff Rules

| If | Then |
|----|------|
| Forge starts work and can't finish | Write detailed handoff for Gentech with exact stopping point |
| Gentech completes a task Forge started | Update handoff status to ✅, leave summary |
| Jordan asks for something mid-task | Park current work as handoff, document stopping point |
| Both agents working same project | Each leaves their piece in the project folder, both read each other's |
| Decision made during conversation | One agent logs it to `vault/decisions/` immediately |

---

## The "Brain" Language

When Jordan says **"the brain"**, he means:

| Phrase | Meaning |
|--------|---------|
| "The brain" | The total knowledge system: Obsidian Vault + GitHub Vault |
| "Drop this in the brain" | Save to vault for persistent access |
| "Brainstorm in the brain" | Start a structured brainstorm in `vault/brainstorms/` |
| "Check the brain" | Load vault, check for updates since last session |
| "Sync the brain" | Pull latest from GitHub vault |

---

*Created: 2026-06-28*
*Part of Gentech Labs Agent Swarm — Vault Communication Protocol*
