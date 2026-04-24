# 🐕 Agent Watchdog System

**Status:** Design phase
**Created:** 2026-04-17

## Purpose
Monitor agent activity. If an agent goes silent or stops responding, other agents check on them and pick up the slack.

## How It Works

### 1. Activity Tracking
Each agent writes a timestamped entry when active:
- Green room: perspective written with timestamp
- Mess hall: coordination with timestamp
- Handoff board: task updates with timestamp

### 2. Health Check (Cron Job — runs every 3 hours)
Check the vault for agent activity:
- Green room: who wrote in the last 6 hours?
- Mess hall: who posted in the last 6 hours?
- Handoff board: who updated a task in the last 6 hours?

### 3. Alert Triggers

| Condition | Action |
|-----------|--------|
| Agent silent 6+ hours during active work | Flag on handoff board: "Check on [Agent]" |
| Agent silent 12+ hours | Alert Jordan: "[Agent] hasn't been active — want me to pick up their tasks?" |
| Agent mid-task but stopped | Post to mess hall: "[Agent] was working on [Task] — stalled. Need backup?" |

### 4. Coverage Rules
- If YoYo is down → Desmond can do light research, flag for Jordan
- If Dmob is down → No one covers code (don't pretend we can)
- If Desmond is down → YoYo or Dmob can draft simple updates, flag for Jordan
- NEVER pretend to be another agent — just cover the work, keep your voice

### 5. Recovery
When the agent comes back:
- Check handoff board for any coverage tasks
- Pick up where you left off
- Post to mess hall: "[Agent] back online"

## Implementation
- Cron job checks vault activity every 3 hours
- Posts alerts to handoff board if agent is silent
- Jordan gets Telegram alert if 12+ hours silent
- All agents check handoff board during Second Brain activity

## Anti-Patterns
- Don't panic if an agent is quiet during off-hours
- Don't flag Jordan for every small gap — only real silence
- Don't do another agent's specialized work (code, deep research)
- Don't assume the worst — maybe they just completed their tasks
