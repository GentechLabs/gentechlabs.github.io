# Agent Node Dashboard — Visual Design Concept

**Date:** 2026-06-14
**Status:** Brainstorm — needs Labs session

## Core Concept

Blockchain explorer but for agent work. Real-time visualization of agent validation activity.

## Dashboard Sections

### 1. Activity Feed (Live)
- Block-like cards appearing in real-time
- Each card = one verification task
- Color coding: 🟢 success, 🔴 caught failure, 🟡 in-progress
- Shows: task type, target, result, timestamp, time taken

### 2. Uptime Monitor
- Large uptime percentage (99.97%)
- Days running counter
- Heartbeat pulse animation
- Last heartbeat timestamp
- History graph (24h, 7d, 30d)

### 3. Earnings Tracker
- Today's earnings (from verification fees)
- Total accumulated
- Earnings per task type
- Projected monthly (based on current rate)

### 4. Reputation Score
- Trust rating (0-100)
- Based on: accuracy, uptime, response time
- Verified vs failed ratio
- Peer validation count

### 5. Network View (Multi-Agent)
- Map of connected agents
- Each agent's status and activity
- Network health overall
- Task distribution

## Visual Style

- Dark theme (matching GenTech brand)
- Animated blocks (not static)
- Real-time data updates (WebSocket or polling)
- Mobile-first (phone dashboard)
- Minimal text, maximum visual signal

## Tech Stack

- Dashboard engine (existing)
- WebSocket for live updates
- Cron job for data collection
- JSON data files (existing pattern)

## Demo Flow

1. User opens dashboard
2. Sees agent heartbeat pulsing
3. Blocks start appearing as agent works
4. Earnings tick up in real-time
5. User sees: "My agent is alive and earning"

## Next Steps

- [ ] Labs architecture session
- [ ] Sketch dashboard wireframes
- [ ] Design block card component
- [ ] Plan WebSocket data flow
- [ ] Prototype with existing dashboard engine
