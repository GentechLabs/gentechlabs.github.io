---
name: travel-planning
description: "Trip planning workflow: flight price research across multiple airports, routing comparison (open-jaw, multi-city, RT), weather/cost research, and vault organization under 00-HQ/Travel/[Country]/."
version: 1.0.0
author: DMOB
tags: [travel, flights, trip-planning, research]
triggers:
  - "plan a trip"
  - "flight prices to [country]"
  - "best time to visit [country]"
  - "compare flights from [airport]"
  - "trip planning"
  - "when is cheapest to fly to"
---

# ✈️ Travel Planning Workflow

## When to Use
- User asks about visiting a country/city
- User wants to compare flight prices or routing options
- User mentions a trip, vacation, or travel dates
- Creating or updating trip docs in the vault

## Prerequisites
- Browser tool (Google Flights) — **primary method** on headless servers
- `letsfg` CLI (optional, may be broken on headless servers — see Pitfalls)
- `maps` skill for geocoding/distance if needed
- `delegate_task` for parallel research across multiple routes

## Workflow

## Workflow

### 1. Clarify Origin Airport(s)
- Get user's home airport (e.g., CVG)
- Ask about nearby alternatives (e.g., ORD 4hr, IND 2hr) — sometimes worth driving
- Check if they have airline loyalty / points
- Note any conflict zone concerns (e.g., AUH/DOH layovers)

### 2. Research Flight Routes (Google Flights primary, LetsFG if available)

**Step 2a: Google Flights via browser (recommended)**
Navigate to: `https://www.google.com/travel/flights?q=flights+from+[ORIGIN]+to+[DESTINATION]+[MONTH]+[YEAR]&curr=USD`
- Results load with cheapest/shortest options automatically
- Use the date pickers to adjust trip length
- For multi-month comparisons: navigate to each month separately, note the cheapest price
- For multi-leg trips: run each leg in parallel (CVG→BKK, BKK→CRK, CRK→MNL)
- Parse the snapshot for: Price, Airline, Stops, Duration, Layover cities + durations

**Step 2a-alt: Resolve IATA codes with LetsFG (if available)**
```bash
letsfg locations "City Name"
```
Returns IATA codes (e.g., CVG, BKK, CRK, POP). For destinations not in LetsFG database, use Google.

**Step 2b: Search flights (Google Flights URL patterns)**
```
# Specific dates
?q=flights+from+CVG+to+POP+June+15+2026+return+June+19+2026

# Month-wide search (slower, may time out)
?q=flights+from+CVG+to+POP+August+2026
```
For multi-month comparisons, use the same mid-month dates across months (e.g., 15-19) for fair comparison.

**Step 2c: Parallel research (delegate_task)**
For context around the flights:
1. **Weather + timing**: Best months, rainy season, typhoon risk, festivals
2. **On-the-ground costs**: Hotels, food, transport, daily budget
3. **Creative routing**: Open-jaw, multi-city, budget carrier hops (compare with LetsFG results)

For each route, find:
- Price ranges (great/good/fair/expensive)
- Airlines and layover cities
- Layover durations (user prefers <4hr layovers)
- Directional pricing differences (BKK→CRK ≠ CRK→BKK)

### 3. Compare Routing Strategies
Common patterns to evaluate:
- **RT from home airport** — simplest, often not cheapest
- **Open-jaw** — fly into city A, out of city B (often same price as RT)
- **Multi-leg** — multiple stops (e.g., CVG→BKK→CRK→MNL) — often cheaper than separate tickets, but higher delay risk
- **Budget hop** — full-service to hub + Cebu Pacific/AirAsia/Scoot for SEA legs ($50-150 per hop)
- **Hub hop** — drive to larger airport (ORD, LAX) for $100-300 savings
- **Separate tickets** — almost always cheaper than single multi-city booking, but no protection if first flight delayed

**Key insights for multi-leg trips:**
- **Directional pricing:** BKK→CRK can be 2-3x cheaper than CRK→BKK — always check both directions
- **Layover risk:** AUH/DOH are stable but high-security (add +60-90 mins) — avoid overnight layovers
- **Budget carriers:** Cebu Pacific, Scoot, AirAsia are dirt cheap for inter-Asia hops — the transpacific leg is the expensive part
- **Parallel research:** Run all legs simultaneously (CVG→BKK, BKK→CRK, CRK→MNL) to compare total cost and travel time

**Key insight for SEA:** Budget carriers (Cebu Pacific, Scoot, AirAsia) are dirt cheap for inter-Asia hops ($50-150). The transpacific leg is the expensive part.

### 4. Present Recommendations
Format as:
- Best value option with total price
- Best convenience option (fewer stops, shorter layovers)
- Price benchmarks table (what's "good" vs "expensive")
- On-the-ground daily budget for each city
- Total trip budget estimate

### 5. Organize in Vault
Under `00-HQ/Travel/[Country]/`:
- `README.md` — Trip overview, itinerary, key decisions
- `2026-TripName.md` — Main consolidated trip doc
- `flights.md` — Detailed flight pricing research

**Never leave duplicate trip docs.** If consolidating, merge into one main doc and delete extras.

### 6. Save to Memory
After planning, save:
- User's home airport
- Any travel preferences (layover length, budget tier, airline preferences)
- Country folder convention

## Pitfalls
- **LetsFG works but is noisy:** Browser connectors fail on headless servers (no X display, Playwright errors), but API connectors still return results. Use `--mode fast` to minimize browser noise. Google Flights via browser is still more reliable for full comparison.
- **Trip value comparison:** When user can only afford one trip, calculate $/day (total flights ÷ trip duration) to show which gives better value per dollar.
- **Google Flights URL encoding:** Direct URL params for dates don't always work — navigate to the search page and let it auto-fill from the query string.
- **Multi-month comparison:** Use consistent mid-month dates (e.g., 15-19) across months for fair price comparison. Wide date ranges (Jun 1-30) may time out.
- **Multi-month comparison:** Use consistent mid-month dates (e.g., 15-19) across months for fair price comparison. Wide date ranges (Jun 1-30) may time out.
- **Directional pricing:** BKK→CRK can be 2-3x cheaper than CRK→BKK — always check both directions
- **Multi-leg routing:** Separate tickets are often cheaper, but no protection if first flight delayed
- **Layover risk:** AUH/DOH are stable but high-security (add +60-90 mins) — avoid overnight layovers
- **CVG/mid-size airports:** No direct Asia flights, always 1-2 stops — compare nearby hubs
- **Open-jaw often same as RT:** Many airlines price open-jaw same as round-trip
- **Separate tickets risk:** If first flight delayed, second booking has no protection
- **LetsFG mode:** Use `--mode fast` for quick results (20-40s). Full scan takes 6+ min and produces more browser errors.
- **September is cheapest** for most SE Asia destinations (rainy season discount)
- **Cebu Pacific Piso Fare sales** happen monthly — worth checking their Facebook page
- **POP (Puerto Plata)** is smaller airport = higher prices. Check STI (Santiago) or SDQ (Santo Domingo) for DR trips.

## Price Benchmark Template
| Route | Great Deal | Good | Average | Expensive |
|-------|-----------|------|---------|-----------|
| US → [City] | Under $X | $X-Y | $Y-Z | Over $Z |

## On-the-Ground Budget Template
| Category | Budget | Mid-Range | Upscale |
|----------|--------|-----------|---------|
| Hotel/night | $15-30 | $40-80 | $80-150 |
| Meals/day | $5-10 | $10-20 | $20-40 |
| Transport/day | $5-10 | $10-20 | $20-40 |

## Future Enhancement
- LetsFG GitHub star unlock (free unlock + book with `letsfg star --github <username>`)
- Price alert cron jobs (Google Flights or LetsFG)
- Automated fare tracking in vault

## LetsFG Quick Reference
```bash
# Install (one-time)
pip install --break-system-packages --ignore-installed typing-extensions letsfg

# Resolve city to IATA
letsfg locations "Bangkok"

# Search round trip
letsfg search CVG BKK 2026-09-01 --return 2026-09-12 --sort price --limit 5 --currency USD

# Search one-way
letsfg search BKK CRK 2026-09-05 --sort price --limit 3 --currency USD

# Fast mode (OTAs + key airlines only, ~25 connectors)
letsfg search LAX MNL 2026-09-01 --mode fast

# Multi-passenger
letsfg search CVG BKK 2026-09-01 --adults 2 --cabin M

# JSON output (for programmatic parsing)
letsfg search CVG BKK 2026-09-01 --json
```
