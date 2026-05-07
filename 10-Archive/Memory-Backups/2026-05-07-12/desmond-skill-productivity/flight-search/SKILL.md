---
name: flight-search
description: "Search flights using LetsFG - 400+ airlines, real prices, zero markup. CLI and Python SDK."
version: "1.0.0"
triggers:
  - flight
  - flights
  - airline
  - fly
  - airport
  - trip
  - travel
  - booking
  - cheapest flight
  - round trip
  - one way
tags: [productivity, travel, flights, letsfg]
related_skills: ["travel-flight-research"]
---

# Flight Search - LetsFG

Agent-native flight search tool. 400+ airlines, 200+ connectors, real-time prices, zero markup.

## Install

```bash
pip install letsfg --break-system-packages
playwright install chromium
```

## CLI Usage

### Basic Search
```bash
letsfg search <ORIGIN> <DEST> <DATE> [--return <DATE>] [--mode fast] [--json]
```

### Examples
```bash
# One-way
letsfg search CVG PUJ 2026-06-01

# Round-trip
letsfg search CVG BKK 2026-09-01 --return 2026-09-15

# Fast mode (20-40s instead of 6+ min)
letsfg search LHR JFK 2026-06-15 --mode fast

# JSON output for parsing
letsfg search CVG MNL 2026-09-01 --json

# Business/First class
letsfg search LHR JFK 2026-06-15 --cabin C  # business
letsfg search LHR JFK 2026-06-15 --cabin F  # first
```

### Airport Codes
- Use IATA codes: CVG (Cincinnati), LHR (London Heathrow), JFK, BKK, CRK, PUJ, MNL
- City codes auto-expand: LON to LHR+LGW+STN+LTN+SEN+LCY, NYC to JFK+EWR+LGA
- Run `letsfg locations <query>` to resolve city/airport names to codes

### Other Commands
```bash
letsfg locations <query>    # Find airport codes
letsfg star --github <user> # Verify GitHub star (needed for unlock/book)
letsfg unlock <offer_id>    # Confirm live price, hold 30 min
letsfg book <offer_id>      # Book the flight
```

## Python SDK

### Local Search (no API key)
```python
import asyncio
from letsfg.local import search_local

async def search():
    result = await search_local("CVG", "BKK", "2026-09-01", mode="fast")
    for offer in result.offers[:5]:
        print(f"{offer.airlines}: {offer.currency} {offer.price}")

asyncio.run(search())
```

### With API Key (for unlock/book)
```python
from letsfg import LetsFG

bt = LetsFG()  # reads LETSFG_API_KEY from env
flights = bt.search("CVG", "BKK", "2026-09-01")
print(f"{flights.total_results} offers, cheapest: {flights.cheapest.summary()}")
```

## Parsing JSON Output

When using `--json`, the output structure is:
```json
{
  "offers": [
    {
      "price": 1086.09,
      "currency": "USD",
      "airlines": ["AA", "PR"],
      "outbound": {
        "total_duration_seconds": 68040,
        "stopovers": 2,
        "segments": []
      },
      "inbound": {},
      "source": "kiwi_connector"
    }
  ]
}
```

To parse in bash:
```bash
letsfg search CVG BKK 2026-09-01 --mode fast --json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for o in data['offers'][:5]:
    print(f\"\${o['price']} | {', '.join(o['airlines'])} | {o['outbound']['stopovers']} stops\")
"
```

## Performance Tips

- **`--mode fast`**: Searches ~25 connectors (OTAs + key airlines) in 20-40s. Use this for quick lookups.
- **Default mode**: Searches all 200+ connectors in 2-6 minutes. Use for comprehensive price comparison.
- **2>/dev/null**: Suppress connector error messages (normal - some connectors fail gracefully).

## Pitfalls

1. **First run is slow** - Playwright downloads browser binaries on first search
2. **Some connectors fail** - This is normal. LetsFG continues searching other connectors.
3. **Errors go to stderr** - Always use `2>/dev/null` when piping to avoid noise
4. **Headless server** - Works fine on servers without display. Playwright runs headless by default.
5. **Prices are live** - They change. Re-run searches to get current prices.
6. **GitHub star required** for unlock/book operations. Search is always free.

## Typical Workflow

1. Search multiple dates to find cheapest: `letsfg search CVG PUJ 2026-05-25 --mode fast --json`
2. Compare results across dates
3. Pick best option and set price alert (via Google Flights or manually re-check)
4. When ready to book: `letsfg star --github <username>` then `letsfg unlock` + `letsfg book`

## Filtering by Layover Duration

When user specifies layover constraints (e.g., "1hr 20min to 2hrs, under 9hrs total"), parse JSON segments:

```python
import json
from datetime import datetime

with open('/tmp/results.json') as f:
    data = json.load(f)

for offer in data['offers']:
    duration = offer['outbound']['total_duration_seconds']
    if duration > 9 * 3600:
        continue  # skip if over 9 hours

    segs = offer['outbound']['segments']
    layovers_ok = True
    for j in range(len(segs) - 1):
        arr = datetime.fromisoformat(segs[j]['arrival'])
        dep = datetime.fromisoformat(segs[j+1]['departure'])
        layover_min = (dep - arr).total_seconds() / 60
        if layover_min < 80 or layover_min > 120:
            layovers_ok = False
            break

    if layovers_ok:
        print(f"${offer['price']} | {', '.join(offer['airlines'])}")
```
