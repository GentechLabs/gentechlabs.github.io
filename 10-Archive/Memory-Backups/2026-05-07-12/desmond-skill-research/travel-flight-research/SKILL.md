---
name: travel-flight-research
description: Research flight prices, multi-city routing, layover analysis, and booking strategies for international travel.
tags: [travel, flights, research, booking]
related_skills: [obsidian]
when_to_use: User asks about flight prices, best time to visit a country, multi-city routing, layover comparison, or travel booking strategy. Triggers on phrases like "flight prices to X", "best month to visit", "cheapest way to get to X", "multi-city routing", "layover options".
---

# Travel Flight Research

Research flight options, compare routing strategies, and produce structured booking recommendations.

## Workflow

### 1. Gather Requirements
- **Origin airport** (don't assume — ask or check memory)
- **Destination(s)** — single city or multi-country trip
- **Date flexibility** — specific dates vs "which month is cheapest"
- **Preferences** — layover length, airline preference, budget ceiling
- **Travelers** — solo vs group affects pricing

### 2. Research Strategy — Compare These Routing Types

For ANY destination, always compare:

| Strategy | When It Wins | Example |
|----------|-------------|---------|
| **Direct round-trip** | Hub city with direct service | JFK→LHR RT |
| **Round-trip to secondary airport** | Closer to final destination, cheaper | CVG→CRK (in Angeles City) vs CVG→MNL (2hr bus away) |
| **Open-jaw (fly into A, out of B)** | Multi-city trip, no backtracking | CVG→BKK / CRK→CVG |
| **Creative hub routing** | Budget carriers connect through Asian/Middle East hubs | NYC→HKG→CRK via Cathay Pacific |
| **Separate one-ways** | Mixed airlines, budget carriers | Scoot BKK→CRK ($157) + Cathay CRK→CVG |

### 3. Price Benchmarking

Always include a "what's cheap" table for the route:

| Tier | US → SE Asia RT | US → Europe RT | Intra-Asia One-Way |
|------|----------------|----------------|-------------------|
| Great deal | Under $700 | Under $400 | Under $150 |
| Good | $700-1,000 | $400-600 | $150-250 |
| Average | $1,000-1,300 | $600-900 | $250-400 |
| Expensive | Over $1,300 | Over $900 | Over $400 |

Adjust based on origin airport size (CVG/medium hub = add 10-20% vs JFK).

### 4. Layover Analysis

Rate layovers on these factors:
- **Duration:** Under 3hrs = great, 3-6hrs = good, 6-12hrs = acceptable, 12hr+ = overnight/bad
- **Hub quality:** ICN/HKG/SIN = excellent (food, WiFi, lounges). DOH/AUH = good. Random domestic hubs = meh
- **Visa requirements:** Most hubs are transit-visa-free, but verify
- **Same-day connection:** Can you make it to destination the same day?

### 5. Direction Matters

**Key insight:** One-way prices are NOT symmetric. BKK→CRK might be $157 while CRK→BKK is $373. Always check both directions and factor into open-jaw strategy.

### 6. Output Format

Structure findings as:

```
## [Route] — [Month/Date Range]

### Best Options by Strategy
| Strategy | Price | Airlines | Layover | Total Time |
|----------|-------|----------|---------|------------|

### Price Benchmarks
[What's cheap/good/average for this route]

### Recommended Booking
[1-2 paragraphs: which strategy wins and why]

### Key Insights
- Bulleted findings about direction asymmetry, hub options, timing
```

## Search Tool: LetsFG

Use the `flight-search` skill for CLI commands, JSON parsing, and Python SDK details.

### Quick Reference
```bash
# Fast search (20-40s, ~25 connectors)
letsfg search <ORIGIN> <DEST> <DATE> [--return <DATE>] --mode fast --json 2>/dev/null

# Full search (2-6 min, 200+ connectors)
letsfg search <ORIGIN> <DEST> <DATE> --json 2>/dev/null

# Resolve airport codes
letsfg locations <query>
```

### Filtering for Layover Constraints
When user specifies layover preferences (e.g., "1hr 20min to 2hrs"), parse the JSON segments and calculate layover durations:
```python
from datetime import datetime
for j in range(len(segments) - 1):
    arr = datetime.fromisoformat(segments[j]['arrival'])
    dep = datetime.fromisoformat(segments[j+1]['departure'])
    layover_min = (dep - arr).total_seconds() / 60
```

### Fallback: Google Flights (Browser)
Only use if LetsFG is down or for price alerts. Navigate to google.com/travel/flights, switch to Multi-city mode for complex routing.

## Pitfalls

- **Don't assume the origin airport** — always confirm (e.g., CVG not NYC)
- **Google Flights calendar** — September 2026 is far out, prices may not be available yet
- **Multi-city UI** — Google Flights multi-city date picker requires scrolling through months, slow with browser automation
- **Subagent timeouts** — flight research is complex, use `delegate_task` for parallel route searches but allow sufficient time
- **Bot detection** — Google Flights may block headless browsers; Kayak/Skyscanner also block bots aggressively

## Vault Convention

Travel docs go in `00-HQ/Travel/{Country}/`:
- `README.md` — trip overview, quick links, budget summary
- `flights.md` — detailed flight research
- `{Year}-{Trip-Name}.md` — full trip plan (itinerary, weather, transport, activities)

## Example: Multi-Country Trip

For trips spanning 2 countries (e.g., Thailand + Philippines):

1. Research direct RT to each country from origin
2. Research intra-Asia hops (BKK↔CRK pricing)
3. Compare: RT to Country A + one-way hop vs open-jaw multi-city
4. Check direction asymmetry on the hop route
5. Factor in which country to visit first (routing logic + trip priority)
