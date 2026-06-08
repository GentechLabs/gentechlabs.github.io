# TinyFish Integration — Web Agent Platform

**Date:** June 4, 2026
**Status:** API key received, exploring integration
**API Key:** Saved to .env (TINYFISH_API_KEY)

## What TinyFish Is

Web agents platform — automate websites without APIs. Backed by $47M Series A (ICONIQ). Clients: Google, DoorDash.

## APIs Available

| API | Use Case | Latency |
|-----|----------|---------|
| **Agent** | Execute goals on real websites | 15-60s |
| **Search** | Ranked web results | 1-3s |
| **Fetch** | Extract page content from URLs | 1-20s |
| **Browser** | Remote browser sessions (Playwright/CDP) | 10-30s |

## Integration Options

### 1. MCP Server
- Connect TinyFish to Hermes via MCP
- Agent can browse websites, extract data, execute goals
- Install: `npx -y install-mcp@latest https://agent.tinyfish.ai/mcp --client claude-code`

### 2. Python SDK
```python
from tinyfish import TinyFish
client = TinyFish()
result = client.agent.run("Go to devpost.com and list all active hackathons")
```

### 3. API Direct
```bash
curl -N -X POST https://agent.tinyfish.ai/v1/automation/run-sse \
  -H "X-API-Key: $TINYFISH_API_KEY" \
  -H "Content-Type: application/json"
```

## Use Cases for GenTech

### 1. Hackathon Scanner (High Priority)
- Agent API scrapes Devpost, DoraHacks, etc.
- Extracts: name, deadline, prizes, tracks, requirements
- Auto-updates hackathon tracker in vault
- Cron job: daily scan

### 2. Market Monitoring
- Search API tracks DeFi protocols, yields, TVL
- Fetch API extracts data from DeFi dashboards
- Auto-updates strategies group

### 3. Content Pipeline
- Agent API browses X/Twitter for trends
- Extracts relevant content for GenTech brand
- Auto-generates content ideas

### 4. Competitor Intelligence
- Agent API monitors agentic finance landscape
- Tracks new projects, skills, integrations
- Auto-updates landscape file

### 5. Grant Research
- Agent API scans grant programs, deadlines
- Extracts requirements, eligibility
- Auto-updates grant tracker

## Next Steps

1. Test Agent API with a simple goal
2. Test Search API for hackathon data
3. Test Fetch API for page extraction
4. Decide on MCP vs SDK vs direct API
5. Build first integration (hackathon scanner)
