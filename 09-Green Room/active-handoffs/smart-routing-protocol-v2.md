---
date: 2026-05-07
type: routing-protocol
version: 2.0
status: active
---

# 🔀 Smart Routing Protocol — Analyze → Prompt → Route

## How It Works

Gentech is the intelligence layer. Every message in shared groups gets analyzed before routing.

## Flow

```
Message arrives
     │
     ▼
┌─────────────────┐
│  Analyze Content │ ← What type? What scope? What context?
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Prompt Jordan   │ ← Ask clarifying questions (if needed)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Execute Route   │ ← @mention agent with full context
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Track Dispatch  │ ← Log decision for pattern analysis
└─────────────────┘
```

## Decision Matrix

| Scenario | Action |
|----------|--------|
| Clear, routine task | Route directly (skip prompt) |
| Ambiguous scope | Prompt Jordan with assessment |
| Multi-department | Prompt Jordan for sequence/priority |
| High-stakes (budget, public) | Prompt Jordan with risk assessment |
| Urgent (needs answer NOW) | Route directly, note urgency |
| Jordan explicitly routes | Execute immediately |

## Prompt Template

```
@Jordan — I see [topic] came up. Before I route this:

**My assessment:** [1-2 sentence classification]
**Recommended routing:** @AgentName for [specific reason]
**Questions:**
1. [Scope/priority question]
2. [Deadline/urgency question]
3. [Approach/strategy question]

Want me to route this, or do you want to handle differently?
```

## Routing Log

Track decisions in Green Room for pattern analysis:
- What was routed
- To which agent
- Jordan's answers (if prompted)
- Completion time
- Quality of routing decision (retrospective)

This builds routing intelligence — over time, we learn what types of work go where and can route with fewer questions.

## Agent Specialists

| Agent | Domain | Home Group |
|-------|--------|------------|
| DMOB | Technical, code, security, smart contracts | Labs |
| YoYo | Market, data, DeFi, investment, strategy | Strategies |
| Desmond | Content, creative, brand, social, docs | Entertainment |
| Gentech | Everything else, routing, Jordan interface | HQ (all groups) |
