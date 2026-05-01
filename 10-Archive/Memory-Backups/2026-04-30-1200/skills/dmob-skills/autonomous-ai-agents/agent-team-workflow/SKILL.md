---
name: agent-team-workflow
description: "Multi-agent team conventions in a shared Obsidian vault: communication channels, approval workflows, stopping point protocols, and folder organization."
version: 1.0.0
author: DMOB
license: MIT
metadata:
  hermes:
    tags: [multi-agent, team, workflow, vault-organization, approvals]
---

# Agent Team Workflow

Conventions for running multiple Hermes agents sharing a single Obsidian vault. Applies when you have distinct agent profiles (e.g., one per department/role) that need to coordinate, escalate decisions, and stay organized.

## When to Use

- Setting up a new multi-agent team with shared vault
- Onboarding a new agent to an existing team
- Restructuring communication or approval flows
- Agents are stepping on each other or creating clutter

## Communication Channels

Map each communication PURPOSE to a dedicated vault folder. Agents must know which folder fits which conversation type.

### Pattern

| Purpose | Folder | When to Use |
|---------|--------|-------------|
| Active work coordination | `09-Green Room/` | During task execution, handoffs, debates between agents |
| Social / non-work chat | `11-Mess Hall/` | Outside of tasks, general discussion, idle chatter |
| Human approval requests | `00-HQ/Approvals/` | When agents need Jordan/operator sign-off |
| Task status & todo lists | `00-HQ/` or root-level board | Living documents tracking what's next |

### Rules

1. **Work conversations stay in the work channel.** Don't pollute social space with task debate.
2. **Social conversations stay in the social channel.** Don't clutter work channels with off-topic chat.
3. **Never skip the inter-agent channel.** Agents talk to each other first (Green Room), then report to human (HQ) when done or blocked.
4. **Don't ask the human questions directly from agent channels.** Post in Green Room, coordinate, then escalate via approval or summary.

## Approval Workflow

When agents need human sign-off on a decision, use a structured approval request.

### Setup

Create `00-HQ/Approvals/` with:
- `README.md` — documents the workflow
- `template.md` — standardized format for requests

### Template Structure

```markdown
# Approval: [Topic]

**Submitted by:** [Agent/Department]
**Date:** YYYY-MM-DD
**Priority:** [Low/Medium/High/Urgent]

## Summary
[1-2 sentence overview]

## Details
[Full context, rationale, data]

## What We Need
- [ ] Approval to proceed with [action]
- [ ] Budget allocation: $[amount]
- [ ] Timeline confirmation: [dates]

## Alternatives Considered
1. [Option A] — pros/cons
2. [Option B] — pros/cons

## Recommendation
[Agent team's recommended course of action]

## Decision
- [ ] Approved
- [ ] Approved with modifications: _______________
- [ ] Rejected — Feedback: _______________
```

### Flow

1. Agents debate in Green Room
2. Create approval note using template
3. Human reviews and checks boxes
4. Agents proceed based on decision

## Stopping Point Protocol

When an agent hits a stopping point (task complete, blocked, waiting):

1. **First**: Ask Jordan/human what to do next, OR check the to-do list for next task
2. **If no reply in 10-20 minutes**: Self-direct
   - Go back to the vault and audit current work
   - Review code quality
   - Start extended discussions in Mess Hall
   - Look for optimization opportunities
3. **Don't sit idle.** Use downtime productively.

## Vault Organization

### Time-Based Folders

For conversation logs, status updates, and daily artifacts, organize by time period:

```
11-Mess Hall/
├── 2026/
│   ├── W17/
│   │   ├── 2026-04-21/
│   │   ├── 2026-04-22/
│   │   └── ...
│   └── W18/
│       └── 2026-04-27/
├── archive/
│   └── 2026-04/
└── task-board.md
```

### Organization Rules

- **Weekly folders** (`W01`-`W52`) group daily folders
- **Monthly archives** hold older content that's no longer active
- **Root-level files** are living documents (task boards, handoff boards)
- **Clean up empty folders** during maintenance — don't leave stale structure

### Folder Purpose Mapping

| Folder | Purpose | Contents |
|--------|---------|----------|
| `00-HQ/` | Human-facing commands & approvals | Approval requests, top-level plans |
| `02-Labs/` (or dept folder) | Agent's own work domain | Code, specs, audit reports |
| `09-Green Room/` | Inter-agent work coordination | Debates, handoffs, technical discussions |
| `11-Mess Hall/` | Social & status updates | Daily logs, general chat, status boards |

## Pitfalls

- **Don't create new purpose-built folders without discussion.** Adding random folders creates confusion about where things go.
- **Don't put approval requests in Mess Hall.** They need to be in the approval folder where the human expects them.
- **Don't let daily folders accumulate at root level.** Always nest under weekly/monthly.
- **Don't skip the template.** Consistent formatting makes scanning approval requests fast.
