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

## Department Groups (Work-First)

### Principle
Department groups are **workspaces**, not social spaces. Side conversations are fine, but the primary purpose is productive output.

### Department Mapping

| Group | Department | Agent | Purpose |
|-------|-----------|-------|---------|
| **Strategies** | Investment | YoYo | Market research, DeFi analysis, investment decisions |
| **Labs** | Development | DMOB | Smart contracts, hackathons, technical audits, builds |
| **Entertainment** | Content | Desmond | Social media, brand storytelling, creative work, demo videos |
| **HQ** | Central Command | Gentech | Summaries, portfolio, cross-group decisions, Jordan conversations |

### Rules
- Work output goes to your home department group
- Cross-department coordination goes through Green Room first, then report to HQ
- All summaries, portfolio updates, and cross-group items route to **HQ**
- Don't post in another agent's department unless explicitly tagged

## Cron Job Routing

### Principle
Cron jobs should deliver to the **correct department** — not all over the place.

### Routing Rules

| Job Type | Deliver To | Rationale |
|----------|-----------|-----------|
| Department-specific work (DeFi monitoring, hackathon scouting) | Home department | Keeps noise in the right channel |
| Cross-group summaries (Omni-Summary, daily digest) | HQ | Central rollup belongs in central command |
| Portfolio/recruiting (College.xyz, portfolio site) | HQ | These are HQ-level concerns |
| Operational (watchdog, vault maintenance, brain backup) | HQ or local | Infrastructure, not department-specific |
| Content (social threads, demo videos, submission docs) | Entertainment | Creative output |

### Anti-Patterns
- ❌ Desmond delivering DeFi monitoring (that's YoYo's job)
- ❌ Multiple profiles running the same cron job (deduplicate!)
- ❌ Delivering cross-group summaries to a department instead of HQ
- ❌ A job with a truncated/broken chat ID silently failing

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

## Pre-Work Audit Protocol

### Principle
**Before starting ANY work, always audit first.** Never assume state — verify it. Jordan: "before starting work always do a clean audit of what we have, check the GitHub and the Obsidian."

### Audit Checklist
1. **Check the vault (Obsidian)** — what docs, handoffs, status updates, sprint plans exist for this project?
2. **Check GitHub** — what code is actually committed and pushed? What's the latest commit?
3. **Compare the two** — identify gaps between what's documented vs what's built. The vault may have more complete code than the repo (or vice versa).
4. **Check recent handoffs** — look in `09-Green Room/active-handoffs/` for the latest status from other agents.
5. **Report findings** — tell the team what you found before diving into work.

### Why This Matters
During the Solana Frontier session (May 5), I started working without auditing first. Result: I reported the workspace repo's status (1 program) when the vault actually had all 4 programs (2,075 lines, 53/53 tests). The audit would have caught this immediately.

### Quick Audit Commands
```bash
# Vault state
find "$VAULT/02-Labs/Hackathons/Active/[project]/" -name "*.rs" -o -name "*.sol" | wc -l

# GitHub state
cd /root/workspace/[repo] && git log --oneline -3 && git diff --stat

# Compare
diff <(find [vault-path] -name "*.rs" -exec md5sum {} \;) <(find [repo-path] -name "*.rs" -exec md5sum {} \;)
```

## Provider Subscription Awareness

### Principle
Know which AI providers are active, what they cost, and what their constraints are. Provider issues (auth expiry, billing surprises, model availability) directly impact agent uptime.

### Current Provider Stack (as of May 2026)

| Provider | Model | Role | Billing | Notes |
|----------|-------|------|---------|-------|
| **Xiaomi MiMo** | mimo-v2.5 | Primary | Token plan (credit-based) | Dashboard at platform.xiaomimimo.com. No public usage API. |
| **OpenCode Go** | MiMo + others | Secondary/Fallback | $10/month subscription | Rolling daily + weekly usage limits. Dashboard at opencode.ai/workspace. |
| **Nous Research** | Various | Emergency backup | OAuth (15-min token expiry) | Auth expires every ~15 min, requires cron refresh. Consider deprioritizing. |

### Provider Constraints to Watch
- **Xiaomi MiMo**: Credits consumed at 1:2 ratio (Pro vs standard). TTS models currently free (limited time). Check dashboard for remaining credits.
- **OpenCode Go**: Rolling usage resets every ~24hrs. Weekly usage cap. No public API — dashboard-only monitoring.
- **Nous Research**: OAuth tokens expire ~15 min. If using as provider, needs auth refresh cron job. Jordan: "I should only have a watchdog if the agents go down, not for auth refresh."

### Usage Monitoring
- Neither Xiaomi nor OpenCode has a public usage API
- Best approach: track token counts locally from API responses
- Set up daily cron to report estimated consumption to HQ
- Manual dashboard checks as backup

### When Provider Issues Hit
1. Check if it's auth (token expired) vs billing (credits exhausted) vs model availability
2. If auth: refresh token or switch to fallback provider
3. If billing: alert Jordan immediately — don't guess
4. If model: check if alternative model is available on same provider

## Option 1: Smart Routing (Gentech as Team Lead)

### Overview
Gentech becomes the **only always-on agent** across all Telegram groups. Specialist agents go **on-demand** — activated only when Gentech routes a task. Goal: 75% reduction in idle token burn.

### Architecture
- **Gentech** is in every group, reads every message, classifies and routes
- **Desmond, DMOB, YoYo** stay in home groups, activate only when @mentioned or routed
- **Green Room** becomes async task queue (not real-time chat)
- **Jordan** talks to Gentech directly; Gentech routes internally

### Routing Rules (Gentech)
1. Is this directed at me? → Respond directly
2. Does this need a specialist? → Route to correct agent with context
3. Before routing, verify: no duplicate work, agent has needed context, urgency appropriate

### Agent On-Demand Rules
- Activate ONLY when @mentioned or Gentech routes a task
- Stay silent in shared groups unless directly addressed
- After activation: acknowledge → do work in home group → report → return to idle

### Token Tracking
- Script: `00-HQ/Operations/token-tracker.py`
- Daily report cron under Gentech
- Baseline comparison to measure savings

### Full Implementation Plan
- Doc: `00-HQ/Operations/Option1-Smart-Routing-Implementation.md`
- Phased rollout: routing → on-demand → queue → tracking → consolidation

## Token Burn Optimization Patterns

### Context
Jordan raised a critical question (May 6, 2026): "Is this why I burn through tokens so fast? Do you guys actually need to be working at the same time?"

### The Problem
Per agent, per turn overhead:
- System prompt + personality (~2-3K tokens)
- Memory injection (~1-2K tokens)
- Skills list + loaded skills (~1-3K tokens)
- Vault context reads (~2-5K tokens)
- Conversation history (~varies)

**If 3 agents run simultaneously:** 3x the overhead before any real work happens.

### Optimization Strategies

#### 1. Sequential Specialist Model (Recommended)
Instead of 3 agents always running:
- **Single coordinator** (lightweight) handles routing
- **Specialists** only spin up when needed for specific tasks
- Coordinator does the context loading, specialist does the work

**Savings:** ~60-70% reduction in idle token burn

#### 2. Task-Based Batching
- Queue tasks throughout the day
- Run batch processing at specific times (e.g., 2x daily)
- Avoid real-time coordination overhead

**Savings:** ~40-50% reduction

#### 3. Shared Context Layer
- Single "brain" agent maintains project context
- Specialists receive only relevant context slices
- Avoid duplicate context loading across agents

**Savings:** ~30-40% reduction

#### 4. Skill-On-Demand
- Only load skills when task requires them
- Don't preload full skill library every turn

**Savings:** ~20-30% reduction

### Implementation: Hybrid Approach
1. **Jordan-facing layer**: Single agent handles all direct communication
2. **Specialist delegation**: Spawn specialists only for specific tasks, not always-on
3. **Batch coordination**: Green Room posts become daily digests, not real-time chat
4. **Cron for monitoring**: Use scheduled jobs for routine checks instead of agent loops

**Estimated savings:** 50-60% reduction in token burn while maintaining quality.

## Common Pitfalls

1. **No sync before posting** — agents speak independently, human gets contradictory messages
2. **Unclear approval format** — human has to parse paragraphs instead of checking boxes
3. **Agents sit idle** — waiting for human instead of self-directing
4. **Flat file structure** — communication logs pile up without organization
5. **No stopping point protocol** — agents don't know what to do when blocked
6. **Writing brainstorms without vault research** — missing what's already built, duplicating work
7. **Handoffs without specific questions** — receiving agent has to guess what's needed
8. **Re-sharing private content to other groups** — images, screenshots, tokens, emails from HQ stay in HQ. Only summaries go to other groups. Jordan: "Private photos, screenshots, emails, tokens stay in HQ only."
9. **Cron jobs delivering to wrong department** — each agent's cron should deliver to their home department or HQ, not cross-department. Causes noise in the wrong channel.
10. **Duplicate cron jobs across profiles** — same job in Desmond + DMOB + Gentech + YoYo. Pick one owner, pause the rest.
11. **Skipping the pre-work audit** — starting work without checking vault + GitHub first. Always audit before building. (Jordan, May 2026)
12. **Spreading across too many hackathons** — scope creep kills submissions. One hackathon at a time, go deep. (Jordan, May 2026)

## Verification

After setup, verify:
1. Agents sync in Active Work Space before group posts ✓
2. Approval requests use checkbox format ✓
3. Stopping points trigger self-direction ✓
4. Communication logs are organized by time ✓
5. Human can easily find past discussions ✓
