# Option 1 — Gentech as Team Leader
**Effective:** 2026-05-07
**Approved by:** Jordan
**Status:** ACTIVE

## What Changed

### 1. Cron Job Consolidation
All specialist cron jobs rerouted to HQ (`telegram:-1003863540828`). No more duplicate reports across specialist groups.

**Rerouted jobs (10 total):**
- DeFi Milestones (was YoYo's group)
- Protocol Due Diligence Chain (was YoYo's group)
- Hermes Agent Daily Sync Check (was DMOB's group)
- Kite AI Hackathon Submission Check (was DMOB's group)
- Security → Content Pipeline (was Desmond's group)
- Gentech X Content Extractor (was Desmond's group)
- hackathon-bounty-monitor (was DMOB's group)
- social-briefing (was YoYo's group)
- LayerZero DVN Monitor (was YoYo's group)
- x402 Ecosystem Monitor (was YoYo's group)

### 2. New Cron Job
- **Token Usage Weekly Audit** — Sundays 8 AM UTC, delivers to HQ. Tracks token consumption week-over-week, flags anomalies, recommends optimizations.

### 3. Agent Behavior Changes
- Specialists (YoYo, DMOB, Desmond) go **on-demand only** in shared spaces
- They only activate when @mentioned or when Gentech routes a task
- Home groups still exist for deep specialist work
- Green Room becomes Gentech-only for routing decisions

### 4. Fail-Safe Protocol
If Gentech is unresponsive >10 minutes, specialists auto-activate in their home groups.

## Token Impact
- Before: 4 agents × N messages = 4× context loading per message
- After: 1 agent (Gentech) loads once, specialist calls are burst-on-demand
- Expected savings: 50-70% reduction in idle token consumption

## Monitoring
- Weekly token audit cron (Sundays 8 AM UTC)
- Compare week-over-week usage
- Track by agent profile if possible
- Flag error-driven token waste

## Architecture
```
Jordan → Gentech (HQ) → Routes to specialist capabilities on-demand
         ↓
    [Gentech loads specialist skills as needed]
    - DeFi questions → YoYo's skills
    - Dev tasks → DMOB's skills
    - Content → Desmond's skills
```

## Notes
- Jordan switching to OpenCode sub in 2 days to balance costs
- Jordan loves mimo v2.5, wants to maximize value before considering cheaper model
- This change is permanent unless Jordan reverts
