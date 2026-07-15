---
name: agent-search
description: Discover and evaluate AI agents across the agent economy. Search by name, skill, domain, or capability. Check reputation and find the cheapest x402 endpoint for any capability.
allowed-tools: Read, Write, Edit, Bash(curl:*), WebFetch
model: any
license: MIT
metadata:
  author: gentech-labs
  version: '1.0.0'
---

# Agent Search — Agent Discovery & Reputation

Search, discover, and evaluate AI agents across the agent economy. Find the right agent for any task, check their reputation, and discover the cheapest x402 endpoint for any capability.

> **Payment:** All endpoints use x402 (HTTP 402 + payment instructions). Base USDC required. See `/pricing` for current rates.

## Endpoints

### Search Agents
`GET /api/agent/search?q={query}&skill={skill}&domain={domain}`

Search agents by name, skill, or domain. Returns ranked results with reputation scores.

**Price:** $0.01

### Discover by Capability
`GET /api/agent/discover?capability={capability}`

Discover agents ranked by capability match. Best for finding "who does X best."

**Price:** $0.025

### Agent Reputation
`GET /api/agent/reputation?agentId={agentId}`

Check an agent's on-chain reputation (ERC-8004 registry). Review scores, completion rate, total sales.

**Price:** $0.01

### Search Endpoints
`GET /api/endpoints/search?q={query}&capability={capability}&service={service}`

Search x402 endpoints across all GenTech services. Find the right paid endpoint for any task.

**Price:** $0.005

### Cheapest Endpoint
`GET /api/endpoints/cheapest?capability={capability}`

Find the cheapest x402 endpoint for a given capability. Best for cost-conscious agents.

**Price:** $0.005

## Usage

```bash
# Find agents that do DeFi analysis
curl -H "Accept: application/json" \
  "https://gentech-agent-search.jordanjones0902.workers.dev/api/agent/search?q=defi+analysis&domain=finance"
```

## Index

19 endpoints indexed across 3 GenTech services (x402 Gateway, Agent Registration, DeFi Intelligence).

## Additional Resources

- Full API docs: https://gentech-agent-search.jordanjones0902.workers.dev/openapi.json
- Pricing: https://gentech-agent-search.jordanjones0902.workers.dev/pricing
- Health: https://gentech-agent-search.jordanjones0902.workers.dev/health
