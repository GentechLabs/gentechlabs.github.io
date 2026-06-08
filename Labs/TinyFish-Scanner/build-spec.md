# TinyFish Hackathon Scanner — Build Spec

**Date:** June 4, 2026
**Status:** Building now
**API:** TinyFish Agent API

## Concept

Automated hackathon scanner that scrapes Devpost, DoraHacks, and other platforms daily. Extracts: name, deadline, prizes, tracks, requirements. Auto-updates hackathon tracker in vault.

## Build Plan

### Phase 1: Test Agent API (15 min)
1. Test with simple goal: "Go to devpost.com and list all active hackathons"
2. Verify output format
3. Check latency and reliability

### Phase 2: Build Scanner Script (1-2 hours)
1. Python script using TinyFish Agent API
2. Scrape Devpost, DoraHacks, and other platforms
3. Extract structured data (name, deadline, prizes, tracks, requirements)
4. Save to vault: `Strategies/hackathon-scans/`

### Phase 3: Cron Job (30 min)
1. Daily cron job at 10 AM ET
2. Run scanner script
3. Compare with existing tracker
4. Flag new opportunities
5. Deliver summary to HQ

### Phase 4: Polish (1 hour)
1. Error handling
2. Deduplication
3. Scoring system (star rating based on fit)
4. Integration with existing hackathon tracker

**Total estimate:** 3-4 hours

## Success Criteria

- [ ] Scanner runs daily via cron
- [ ] Extracts structured hackathon data
- [ ] Compares with existing tracker
- [ ] Flags new opportunities
- [ ] Delivers summary to HQ
- [ ] Saves data to vault

## API Usage

```python
from tinyfish import TinyFish
client = TinyFish()

# Scrape Devpost
result = client.agent.run(
    "Go to https://devpost.com/hackathons and list all active hackathons. "
    "For each, extract: name, deadline, prizes, tracks, requirements. "
    "Return as JSON array."
)
```

## Output Format

```json
[
  {
    "name": "Slack Agent Builder Challenge",
    "platform": "Devpost",
    "deadline": "2026-07-13",
    "prizes": "$42,000",
    "tracks": ["New Agent", "Agent for Good", "Agent for Organizations"],
    "requirements": ["Slack AI", "MCP integration", "Real-Time Search API"],
    "url": "https://devpost.com/...",
    "fit_score": 4
  }
]
```
