# AAE — Brain Layer: Agent Accountability

> **Insight from Jordan (Apr 18, 2026):**
> "Like how our watchdog makes sure things are being executed as conditions are met — the Brain Layer should do the same for agents."

## What Is the Brain Layer?

The Brain Layer is AAE's intelligence and oversight system. It has three functions:

### 1. Agent Memory & Evolution
- Agents remember past decisions and outcomes
- Strategies improve over time based on results
- Cross-agent knowledge sharing

### 2. Agent Handoff During Market Stress
- When one agent detects a crisis (crash, exploit, depeg), it triggers the next agent
- Chain reaction: Research detects → Strategy adjusts → Execution protects funds
- Human is alerted but not required to act

### 3. Agent Accountability (NEW)
- **The watchdog that watches the agents**
- Monitors: Are agents executing as conditions are met?
- Flags: Agent skipped a rebalance, ignored a threshold, failed to log
- Reports: Dashboard showing agent health, task completion, missed actions
- Auto-correction: If an agent fails, fallback agent picks up the slack

## How It Maps to Our Real System

| AAE Product Feature | Our Current System |
|---------------------|-------------------|
| Agent memory | Obsidian vault (Second Brain) |
| Agent handoff | Green Room coordination |
| Agent accountability | Desmond + watchdog cron |
| Agent evolution | Mess Hall retrospectives |

## Why This Matters for Users

Users don't just want AI agents that CAN do things. They want assurance that agents ARE doing things. The Brain Layer is the trust mechanism:

- "Did my agent rebalance when it said it would?"
- "Did my agent protect my funds during the crash?"
- "Is my agent actually learning or just repeating?"

**The Brain Layer turns AI agents from black boxes into accountable teammates.**

## Implementation Ideas

- On-chain proof of agent actions (verifiable)
- Agent performance score (visible on Arena leaderboard)
- Missed action alerts (push notifications)
- Agent health dashboard (online/offline, last action, next scheduled)
- Automatic failover (backup agent if primary goes silent)

## Status
- [ ] Needs to be added to AAE product vision doc
- [ ] Include in grant applications
- [ ] Feature spec TBD
