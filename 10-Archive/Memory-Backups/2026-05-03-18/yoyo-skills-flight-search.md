---
name: flight-search
description: "Search flight prices across multiple routes, compare ticketing strategies (round-trip vs open-jaw vs separate one-ways), optimize layovers, and benchmark prices."
category: productivity
tags: [travel, flights, price-comparison, routing]
---

# Flight Search & Travel Routing

Systematic flight price research — find the cheapest routing for any trip, including multi-country itineraries.

## Use Cases

- **Single route search**: "What's the cheapest flight from CVG to Manila?"
- **Multi-city routing**: "I want to visit Thailand AND Philippines — what's the best way to ticket this?"
- **Price benchmarking**: "Is $800 good for this route? What should I expect to pay?"
- **Layover optimization**: "I only want 2-3 hour layovers, not all-day connections"
- **Seasonal timing**: "When's the cheapest month to fly to SE Asia?"

## Tool Chain (in priority order)

### 1. Google Flights (Primary)

**Direct URL pattern** — bypasses the calendar picker UI issues:
```
https://www.google.com/travel/flights/search?tfs=CBwQAhooEgoyMDI2LTA5LTAxagwIAhIIL20vMGYydjByDAgCEggvbS8wZnRreRooEgoyMDI2LTA5LTA4agwIAhIIL20vMGZ0a3lyDAgCEggvbS8wZjJ2MHABggELCP___________wFAAUgBmAEC&hl=en
```

**Airport code lookup** (use these in URLs):
- CVG = Cincinnati/Northern Kentucky
- LAX = Los Angeles
- SFO = San Francisco
- JFK/EWR = New York
- MNL = Manila (Ninoy Aquino)
- CRK = Clark International (Angeles City/Pampanga)
- BKK = Bangkok (Suvarnabhumi)
- NRT = Tokyo Narita
- ICN = Seoul Incheon
- TPE = Taipei Taoyuan
- HKG = Hong Kong
- SIN = Singapore

**Browser workflow:**
1. Navigate to `google.com/travel/flights`
2. Select "One way" or "Multi-city"
3. Enter origin/destination airport codes
4. Set dates (if calendar picker fails, try typing date directly: "Sep 1, 2026")
5. Search and capture: price, airlines, duration, stops, layover cities/times

### 2. Kiwi.com (Fallback)

**Direct URL pattern:**
```
https://www.kiwi.com/en/search/results/cincinnati-united-states-of-america/bangkok-thailand/2026-09-01
```

Kiwi.com is more automation-friendly than Google Flights — fewer bot detection issues.

### 3. Skyscanner / Kayak (Last Resort)

These often block automation with CAPTCHAs. Only try if Google Flights and Kiwi both fail.

## Multi-City Routing Strategies

### Open-Jaw Ticket
Fly into one city, out of another. Example: CVG → Bangkok, Clark → CVG.

### Separate One-Ways
Book each leg independently. Often cheapest for multi-country trips.

### Round-Trip + Extra Leg
RT to main destination + cheap budget airline hop. Example: RT CVG ↔ Manila + Cebu Pacific Manila ↔ Bangkok.

## Price Benchmarks (September 2026 data)

### US to Southeast Asia (one-way, economy)

| Route | Great Deal | Good | Average | Expensive |
|-------|-----------|------|---------|-----------|
| US West Coast → Manila | <$300 | $300-450 | $450-600 | >$600 |
| US East Coast → Manila | <$400 | $400-550 | $550-750 | >$750 |
| CVG → Manila | <$450 | $450-600 | $600-800 | >$800 |
| US → Bangkok | <$350 | $350-500 | $500-700 | >$700 |
| CVG → Bangkok | <$500 | $500-650 | $650-850 | >$850 |
| Bangkok ↔ Clark | <$150 | $150-250 | $250-350 | >$350 |

### Multi-City Totals (US → SE Asia → US)

| Strategy | Estimated Total |
|----------|----------------|
| Separate one-ways (cheapest) | $1,000-$1,400 |
| Open-jaw ticket | $1,200-$1,600 |
| Round-trip + extra leg | $1,400-$1,800 |

### CVG-Specific Pricing (September 2026, real data)

| Segment | Cheapest | Layover | Notes |
|---------|----------|---------|-------|
| CVG → CRK | $653 | 2 stops (SEA/TPE or YYZ/ICN) | Alaska/EVA or Air Canada/Asiana |
| CVG → BKK | $650-800 | 2 stops | Via Seoul, Tokyo, or Hong Kong |
| CRK → BKK | $104 | 1 stop | Kiwi.com price |
| BKK → CRK | $157 | 1 stop (SIN) | Scoot, 9hr |
| BKK → CVG | $522 | 1 stop (ICN/TPE) | Asiana or China Airlines |

## Layover Optimization

### Sweet Spots
- **Under 1.5 hrs**: Risky for international connections
- **2-3 hrs**: Ideal — enough buffer, not sitting around
- **3-4 hrs**: Good — comfortable without wasting time
- **5+ hrs**: Avoid unless overnight layover has a purpose

### Best Hub Cities for Short Layovers to SE Asia
| Hub | Typical Connection | Airlines |
|-----|-------------------|----------|
| Tokyo (NRT/HND) | 2-3 hrs | ANA, JAL |
| Seoul (ICN) | 2-3 hrs | Korean Air, Asiana |
| Taipei (TPE) | 2-3 hrs | EVA Air, China Airlines |
| Hong Kong (HKG) | 2.5-3.5 hrs | Cathay Pacific |
| Singapore (SIN) | 2-4 hrs | Singapore Airlines |

### Airlines with Best Connection Reputation
- **ANA** (Tokyo hub) — consistently tight connections
- **Korean Air** (Seoul hub) — reliable 2-3 hr windows
- **Cathay Pacific** (Hong Kong hub) — smooth transfers
- **EVA Air** (Taipei hub) — efficient connections

## Fuel Price Impact

Track jet fuel prices to understand fare trends:
- **Yahoo Finance**: `finance.yahoo.com/quote/CL=F` (WTI crude)
- Jet fuel typically trades at $0.20-0.60 premium over crude per gallon
- When fuel spikes >15% YoY, expect fare increases across the board
- Budget carriers (Cebu Pacific, AirAsia, Scoot) absorb fuel better via young fleets and unbundled pricing

## Seasonal Pricing Patterns

### Southeast Asia
- **Cheapest**: June-September (rainy season, off-peak)
- **Most expensive**: December-March (dry season, holidays)
- **Sweet spot**: Late October-November (end of rain, before holiday surge)
- **Typhoon risk**: August-September (higher disruption chance)

### General Rule
- Book 6-8 weeks out for best fares
- Fly Tue-Thu for 15-30% savings vs weekends
- Off-season saves 20-30% vs peak season

## Direction Price Asymmetry

Intra-SE Asia hops can have significant price differences depending on direction:
- **BKK → CRK**: ~$157 (Scoot, Cebu Pacific)
- **CRK → BKK**: ~$373 (same route, reverse direction)
- **Lesson**: Always search both directions — the price gap can be $200+ for the same route

This affects multi-city planning: flying BKK first → CRK second is cheaper than the reverse.

## Pitfalls

- **Google Flights calendar picker** fights automation — try typing dates directly or using URL parameters
- **Skyscanner/Kayak** block bots with CAPTCHAs — skip these, use Google Flights + Kiwi.com
- **Search engines return stale flight data** — always go to the airline/booking site directly
- **One-way international flights ARE cheap** for intra-SE Asia (BKK ↔ CRK = $100-200) — the expensive leg is always trans-Pacific
- **"Flight restricted" warnings** on Google Flights are often outdated — verify with the airline directly
- **Clark (CRK) vs Manila (MNL)**: Clark is IN Angeles City/Pampanga — no ground transport needed. Manila requires 2-3hr bus/van ($3-12)

## Workflow Example

User: "I want to visit Thailand and Philippines in September, flying out of CVG"

1. Search CVG → BKK one-way (Sep 1)
2. Search CRK → CVG one-way (Sep 8)
3. Search BKK → CRK one-way (Sep 4-5)
4. Compare total vs round-trip alternatives
5. Present 2-3 options with total cost, layover times, and recommendation
6. Note price benchmarks ("this is a good deal because...")
