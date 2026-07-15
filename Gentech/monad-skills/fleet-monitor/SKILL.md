---
name: fleet-monitor
description: Monitor AI agent fleet health, spending, and uptime. Get AI-powered summaries of agent status, spending analytics, and active alerts across your entire agent fleet.
allowed-tools: Read, Write, Edit, Bash(curl:*), WebFetch
model: any
license: MIT
metadata:
  author: gentech-labs
  version: '1.0.0'
---

# Fleet Monitor — Agent Fleet Health & Analytics

Monitor your entire AI agent fleet in one place. AI-powered status summaries, spending analytics, uptime tracking, and alert management.

> **Payment:** All endpoints use x402 (HTTP 402 + payment instructions). Base USDC required. See `/pricing` for current rates.

## Endpoints

### Fleet Status
`GET /api/fleet/status`

AI-powered overview of all agents in your fleet. Health scores, recent activity, and anomaly detection.

**Price:** $0.01

### Agent Health
`GET /api/fleet/health/:agentId`

Individual agent health check. Response time, error rate, last active, resource usage.

**Price:** $0.005

### Spending Analytics
`GET /api/fleet/spending`

AI-powered spending breakdown across your fleet. Cost per agent, per service, trends, and anomaly alerts.

**Price:** $0.025

### Active Alerts
`GET /api/fleet/alerts`

All active alerts across your fleet. Severity, affected agents, recommended actions.

**Price:** $0.01

### Register Agent
`POST /api/fleet/register`

Register a new agent to your fleet. Requires agent name, endpoint URL, and webhook URL for alerts.

**Price:** $0.01

### Agent Uptime
`GET /api/fleet/uptime/:agentId`

Uptime statistics for a specific agent. 24h, 7d, 30d uptime percentages.

**Price:** $0.005

## Usage

```bash
# Get fleet status
curl -H "Accept: application/json" \
  "https://gentech-fleet-monitor.jordanjones0902.workers.dev/api/fleet/status"
```

## Additional Resources

- Full API docs: https://gentech-fleet-monitor.jordanjones0902.workers.dev/openapi.json
- Pricing: https://gentech-fleet-monitor.jordanjones0902.workers.dev/pricing
- Health: https://gentech-fleet-monitor.jordanjones0902.workers.dev/health
