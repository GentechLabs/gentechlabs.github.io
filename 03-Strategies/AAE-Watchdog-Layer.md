---
type: idea
title: "AAE Brain Layer — Watchdog & Agent Coordination"
created: 2026-04-18
tags: [AAE, brain, watchdog, agent-coordination, architecture]
status: idea
---

# 🧠 AAE Brain Layer — Watchdog & Agent Coordination

**Jordan's idea (Apr 18):** Add a watchdog layer to AAE that monitors agent responsiveness and coordination, similar to how LP monitor watches pool conditions.

## Where It Fits

AAE Architecture layers:
1. Fee LP auto-balance
2. Agent risk intel
3. Brain evolve/learn
4. Social leaderboards
5. **Cross-agent coordination (watchdog)** ← this one

## What It Does

- Monitors that all agents acknowledge tasks/handoffs
- Nudges silent agents (timeout → re-prompt or escalate)
- Confirms when handoffs are complete ("all good, waiting on X")
- Prevents Jordan from being the only one checking boxes
- Tracks agent health (responsive? executing? stuck?)

## Analogy

Like LP monitor watches pool efficiency → watchdog watches agent efficiency.
- LP out of range → alert
- Agent silent too long → alert
- Handoff dropped → alert

## Design Considerations

- Should be **passive** (just monitors, doesn't override agents)
- **Escalation ladder:** silent → nudge → flag to Jordan
- Tracks per-agent metrics (response time, completion rate)
- Integrates with Obsidian second brain for audit trail

## Next Steps

- [ ] Define timeout thresholds (when to nudge vs. escalate)
- [ ] Decide: single watchdog agent or built into GenTech's role?
- [ ] Prototype as cron job first, then build into AAE smart contracts
