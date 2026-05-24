---
date: 2026-05-07
type: implementation-plan
status: active
owner: Jordan (CEO) → Gentech (Team Lead)
---

# Option 1: Smart Routing — Gentech as Team Lead

## Overview

Restructure multi-agent architecture so Gentech is the **only always-on agent** across all Telegram groups. Specialist agents (Desmond, DMOB, YoYo) go **on-demand** — activated only when Gentech routes a task to them. Goal: **75% reduction in idle token burn** while maintaining full team capability.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Jordan (Human)                  │
│              Talks to Gentech directly           │
└──────────────────────┬──────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│              Gentech (Team Lead)                 │
│         ONLY always-on agent in all groups       │
│                                                  │
│  Responsibilities:                               │
│  • Read every message in shared groups           │
│  • Classify: handle directly vs route to agent   │
│  • Route: @mention only the needed agent         │
│  • Monitor: check Green Room queue periodically  │
│  • Report: summaries back to Jordan              │
└──┬──────────┬──────────┬────────────────────────┘
   │          │          │
   ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Desmond│ │  DMOB  │ │  YoYo  │
│Creative│ │  Labs  │ │Stratgy │
│On-Dmd  │ │On-Dmd  │ │On-Dmd  │
└────────┘ └────────┘ └────────┘
```

## Implementation Checklist

### Phase 1: Gentech Routing (Do First)
- [ ] Update Gentech system prompt with routing logic
- [ ] Add Gentech to all department groups (Labs, Strategies, Entertainment)
- [ ] Test routing in HQ — Jordan sends messages, Gentech routes correctly
- [ ] Verify agents only respond when routed (not to every message)

### Phase 2: Agent On-Demand Mode
- [ ] Update Desmond system prompt — respond only when @mentioned or routed
- [ ] Update DMOB system prompt — respond only when @mentioned or routed
- [ ] Update YoYo system prompt — respond only when @mentioned or routed
- [ ] Remove agents from shared groups (keep only in home group)

### Phase 3: Green Room → Task Queue
- [ ] Green Room becomes async task queue (not real-time chat)
- [ ] Gentech writes routing requests as structured notes
- [ ] Agents pick up tasks on next activation
- [ ] No more "blocking on agent response" pattern

### Phase 4: Token Tracking
- [ ] Deploy token tracking script (see below)
- [ ] Set up daily usage report cron job
- [ ] Baseline current burn rate for 48 hours
- [ ] Compare post-implementation burn rate

### Phase 5: Cron Consolidation
- [ ] Audit all existing cron jobs across profiles
- [ ] Consolidate related jobs under Gentech
- [ ] Route specialist work through Gentech dispatch

---

## Routing Rules (Gentech System Prompt Addition)

```markdown
## Smart Routing Protocol

You are the team lead. You are the ONLY agent that responds to every message in shared groups.

### Core Principle: Analyze → Prompt → Route

You are the intelligence layer. Before routing ANY task, you **analyze the content** and **prompt Jordan with questions** to ensure the dispatch is accurate. Don't just @mention agents — think about what they need.

### Step 1: Analyze Content

When you see a message that could need specialist attention:

1. **What type of work is this?**
   - Technical/code/security → DMOB (Labs)
   - Market/data/DeFi/investment → YoYo (Strategies)
   - Content/creative/brand/social → Desmond (Entertainment)
   - Travel/logistics → Handle in HQ
   - Multi-department → Multiple agents needed

2. **What's the scope?**
   - Quick answer (< 5 min) → Route with minimal context
   - Medium task (30-60 min) → Route with full context + deadline
   - Major project (hours/days) → Create handoff doc, route with brief

3. **What context does the agent need?**
   - What's the goal?
   - What's the deadline?
   - What's already been done?
   - What are the constraints?

### Step 2: Prompt Jordan Before Routing

**Before routing, ask Jordan clarifying questions:**

```
@Jordan — I see [topic] came up. Before I route this:

**My assessment:** [1-2 sentence classification]
**Recommended routing:** @AgentName for [specific reason]
**Questions:**
1. [Question about scope/priority]
2. [Question about deadline/urgency]
3. [Question about approach/strategy]

Want me to route this, or do you want to handle differently?
```

**When to skip the prompt (route directly):**
- Jordan explicitly says "route this to X"
- It's a clear, routine task with no ambiguity
- The agent's home group already has context (continuation of existing work)
- Urgent: Jordan needs an answer NOW, not a routing discussion

**When to always prompt:**
- Multi-department tasks (who leads? what's the sequence?)
- Ambiguous tasks (could be DMOB or YoYo — which one?)
- High-stakes work (budget, public-facing, legal implications)
- New task types we haven't done before

### Step 3: Execute the Route

Once Jordan confirms (or you determine direct routing is appropriate):

@AgentName — [One-line task summary]

**Task:** [Specific deliverable]
**Where:** [Home group or specific location]
**Deadline:** [When needed]
**Context:** [Relevant background — keep brief]
**Priority:** [Low/Medium/High/Urgent]

### Step 4: Track the Dispatch

Log routing decisions in Green Room:
- What was routed
- To which agent
- What Jordan's answers were (if prompted)
- Expected completion time

This builds our routing intelligence — patterns emerge about what types of work go where.

### Green Room Monitoring

Check Green Room (09-Green Room/) periodically for:
- Agent status updates (completion, blockers)
- Handoff requests from other agents
- Task queue items awaiting routing
- Routing decision log (for pattern analysis)

### What You Don't Do

- Don't let specialist agents respond to every HQ message
- Don't route work that you can handle directly
- Don't create duplicate tasks — check if work is already assigned
- Don't let agents sit idle when there's work in the queue
- Don't route without analyzing first — you're the intelligence layer
```

---

## Agent On-Demand Prompt Addition

```markdown
## Activation Protocol

You are an on-demand specialist agent. You do NOT respond to every message.

### When to Activate

You activate ONLY when:
1. @mentioned directly by Jordan or Gentech
2. Gentech explicitly routes a task to you
3. You're in your home group and a message directly relates to your domain

### When to Stay Silent

You do NOT respond when:
- A message appears in HQ or shared groups that isn't directed at you
- Another agent is handling something that doesn't need your input
- You're reading messages for context but have no action item

### After Activation

1. Acknowledge the task briefly
2. Do the work in your home group
3. Report completion back to the originating group or Green Room
4. Return to idle (don't continue responding to follow-up messages unless routed again)
```

---

## Token Tracking

### Tracking Script

See `00-HQ/Operations/token-tracker.py` — logs token usage per agent session.

### Daily Report Cron

Gentech runs a daily token report:
- Total tokens consumed across all agents
- Breakdown by agent (always-on vs on-demand activations)
- Comparison to baseline (pre-implementation)
- Cost estimate at current provider rates

### Success Metrics

| Metric | Baseline (Current) | Target (Post-Implementation) |
|--------|--------------------|------------------------------|
| Idle agent token burn | ~75% of total | ~10% of total |
| HQ message processing | 4 agents load | 1 agent loads |
| Green Room coordination | Real-time blocking | Async queue |
| Daily token usage | Track baseline | 50-75% reduction |

---

## Migration Notes

### What Stays the Same
- Home groups remain the same (Entertainment, Labs, Strategies)
- Agent expertise and skills don't change
- Vault structure stays as-is
- Approval workflow unchanged

### What Changes
- Agents only activate when routed (not always-on)
- Green Room becomes async task queue
- Gentech is the single point of contact for Jordan
- Cron jobs consolidate under Gentech

### Rollback Plan
If token savings aren't significant or routing creates too much latency:
1. Revert agents to always-on in their home groups
2. Keep Gentech as team lead but allow agents to read shared groups
3. Green Room reverts to real-time coordination

---

## Open Questions

1. Should Gentech have a separate "routing-only" model (cheaper/faster) vs "thinking" model for complex tasks?
2. Do we need a "warm-up" period where agents are still in shared groups before full on-demand switch?
3. How do we handle urgent messages that need immediate specialist response (not waiting for next activation)?
