---
name: multi-agent-team-workflow
description: "Establish coordination protocols for multi-agent teams: communication routing, approval workflows, stopping point handling, and vault organization."
version: 1.0.0
author: Desmond
tags: [multi-agent, coordination, workflow, team, protocols]
triggers:
  - Setting up a new multi-agent team
  - Onboarding agents to coordination protocols
  - Refining team workflow after miscommunication
  - When asked "how should agents work together?"
  - Organizing agent communication channels
---

# Multi-Agent Team Workflow

Patterns for coordinating multiple AI agents working together under human oversight. Covers communication routing, approval workflows, stopping point protocols, and vault organization.

## When to Use

- New multi-agent team setup
- Agent onboarding (new agent joining existing team)
- Workflow friction (agents stepping on each other, unclear handoffs)
- Organizing scattered communication logs

## Communication Routing

### Principle
Agents need **two distinct spaces**: one for active work coordination, one for general communication.

### Pattern

| Space | Purpose | When |
|-------|---------|------|
| **Active Work Space** | Coordinate before speaking in groups, sync on tasks, handoffs | During active work sessions |
| **General Space** | Status updates, check-ins, extended discussions, off-topic | Outside active work, or while waiting for human response |

### Implementation

1. **Active Work Space** (e.g., Green Room, War Room, Standup Channel)
   - Agents MUST sync here before posting in any shared group
   - Hash out debates, align on one answer, then present to human
   - Use for real-time coordination during task execution

2. **General Space** (e.g., Mess Hall, Lounge, Break Room)
   - Casual conversation, extended discussions
   - Status updates when not actively working
   - Brainstorming and ideation without pressure
   - Where agents go when waiting for human response

### Rules
- Don't post in shared groups without syncing in Active Work Space first
- Keep replies to human short and consolidated (one answer, not three)
- Tag posts with agent name so everyone knows who's talking

## Approval Workflow

### Principle
When agents need human approval, present decisions as **checkboxes** — not paragraphs of text.

### Pattern

```
00-HQ/Approvals/
├── README.md          # Workflow documentation
├── template.md        # Standardized approval request format
└── [topic].md         # Individual approval requests
```

### Approval Request Template

```markdown
# Approval: [Topic]

**Submitted by:** [Agent/Department]
**Date:** YYYY-MM-DD
**Priority:** [Low/Medium/High/Urgent]

## Summary
[1-2 sentence overview]

## Decisions Needed
- [ ] Approval to proceed with [action]
- [ ] Budget allocation: $[amount]
- [ ] Timeline confirmation: [dates]

## Recommendation
[Agent team's recommended course of action]
```

### Workflow
1. Agents discuss in Active Work Space
2. When approval is needed → create note in Approvals folder
3. Human reviews and checks off approved items
4. Agent reads checked boxes and proceeds

## Stopping Point Protocol

### Principle
When an agent hits a stopping point, don't sit idle — self-direct.

### Pattern

1. **Hit a stopping point** (task complete, blocked, waiting for input)
2. **Ask human** "what's next?" OR check the to-do list for next task
3. **If no reply in 10-20 minutes:**
   - Go back into the vault and audit what was done
   - Review code quality, check for issues
   - Start extended discussions in General Space
   - Prep for next likely task
4. **Never sit idle** — always be productive while waiting

### Implementation
- Agents should have a shared to-do list or task board
- When human doesn't respond, agents can self-direct to:
  - Code review / audit
  - Documentation updates
  - Research for upcoming tasks
  - Extended brainstorming in General Space

## Vault Organization for Communication Logs

### Principle
Organize communication logs by **time** (year → week → day) for easy retrieval.

### Pattern

```
11-Mess Hall/
├── 2026/
│   ├── W16/
│   │   ├── 2026-04-16/
│   │   │   └── [topic].md
│   │   └── 2026-04-18/
│   │       └── [topic].md
│   ├── W17/
│   │   ├── 2026-04-21/
│   │   └── 2026-04-22/
│   └── W18/
│       └── 2026-04-27/
├── archive/
│   └── 2026-04/
├── daily/
│   └── README.md
└── README.md
```

### Rules
- Use ISO week numbers (W16, W17, etc.)
- Each day gets its own folder inside the week
- Archive old content monthly
- Keep README.md explaining the structure

## Quick Setup Checklist

When establishing a new multi-agent team:

- [ ] Define Active Work Space and General Space
- [ ] Create Approval folder with template and README
- [ ] Set up vault structure with time-based organization
- [ ] Document stopping point protocol
- [ ] Brief all agents on the workflow
- [ ] Test with a real task before going live

## Strategic Brainstorm Documentation Workflow

### When to Use
- Project owner gives high-level voice direction ("build X", "expand Y into Z")
- Need to translate abstract vision into structured, actionable doc
- Multiple agents need to scoping/input on different aspects

### Pipeline
1. **Vault Research** — Search existing docs for context before writing. Check Strategies/, Projects/, Green Room handoffs, and Mess Hall logs. Understand what's already built.
2. **Structured Brainstorm Doc** — Standard sections:
   - Owner's Vision (exact quotes)
   - Core Thesis (one-liner)
   - Architecture diagram (ASCII or code block)
   - Strategy/feature table with current status
   - Open Questions per team member
   - Phased roadmap (MVP → Full)
   - Existing assets that feed into this
3. **Cross-Agent Handoffs** — Create handoff docs in `09-Green Room/` for agents who need to scope or build. Include: context, specific questions, deliverable format, where to report back.
4. **Mess Hall Log** — Log completion with summary, file locations, and next steps.
5. **HQ Storage** — Brainstorm docs go in `00-HQ/`. They're reference material, not working docs.

### Template: Brainstorm Doc Frontmatter
```yaml
---
date: YYYY-MM-DD
type: brainstorm
source: Jordan (voice memo)
status: open — team brainstorm
---
```

### Template: Handoff Doc Frontmatter
```yaml
---
date: YYYY-MM-DD
type: handoff
from: Desmond (Creative)
to: [Agent Name] ([Department])
status: awaiting [deliverable]
priority: [high/medium/low]
---
```

## Common Pitfalls

1. **No sync before posting** — agents speak independently, human gets contradictory messages
2. **Unclear approval format** — human has to parse paragraphs instead of checking boxes
3. **Agents sit idle** — waiting for human instead of self-directing
4. **Flat file structure** — communication logs pile up without organization
5. **No stopping point protocol** — agents don't know what to do when blocked
6. **Writing brainstorms without vault research** — missing what's already built, duplicating work
7. **Handoffs without specific questions** — receiving agent has to guess what's needed

## Verification

After setup, verify:
1. Agents sync in Active Work Space before group posts ✓
2. Approval requests use checkbox format ✓
3. Stopping points trigger self-direction ✓
4. Communication logs are organized by time ✓
5. Human can easily find past discussions ✓
