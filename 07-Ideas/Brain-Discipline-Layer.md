# 🧠 Brain Discipline Layer — Agent Accountability

**Status:** Idea / Roadmap
**Added:** 2026-04-18
**Origin:** Jordan (voice) — "Like a watchdog, but for quality"

## Concept

The existing watchdog checks if agents are alive (heartbeat). This layer checks if agents are doing it *right*.

## What It Monitors

| Check | Question | How |
|-------|----------|-----|
| **Vault sync** | Did they log the change? | Compare cron actions vs cron-changes/ files |
| **Handoff ack** | Did they acknowledge? | Check Green Room for response |
| **Queue discipline** | Did they finish before pivoting? | Track task completion vs new task starts |
| **Memory updates** | Did they update memory when things changed? | Diff memory entries |
| **Mess Hall presence** | Did they debrief? | Check Mess Hall chat for agent contributions |

## Scoring (lightweight)

- 🟢 **Green:** All checks passed, vault is current
- 🟡 **Yellow:** Minor gaps (missed a log, handoff unacknowledged)
- 🔴 **Red:** Repeated pattern of gaps, needs attention

## Implementation

- Runs on the existing watchdog cron (or a separate daily sync)
- Outputs to Mess Hall or Green Room
- Gentle nudges, not punishment — "Hey, that cron change didn't make it to the vault"

## Where It Lives in AgentEscrow

This fits as a **Layer 2 utility** — a "vault health" module that all agents plug into. The agent layer already has memory + handoffs + alerts. This adds *accountability* to that stack.

Layer 1: Vault contracts + rule engine
Layer 2: AI agents + memory + handoffs + **brain discipline** ← NEW
Layer 3: Arena (social competition, strategy marketplace)

## Why It Matters

Jordan's brain is the team's brain. If one agent forgets to write it down, the next agent (or next session) is flying blind. This layer ensures the brain stays accurate, current, and trustworthy.
