---
name: letsfg-flights
description: "Search and compare flight prices using LetsFG — 400+ airlines, zero markup, $20-50 cheaper than OTAs. Use for any flight search, price comparison, or trip planning."
tags:
  - flights
  - travel
  - search
  - booking
---

# LetsFG Flight Search

Search 400+ airlines at raw airline prices using LetsFG. Runs locally, no API key needed for search.

## When to Use

- User asks about flight prices or wants to compare fares
- Planning a trip and need to check airfare
- User wants to find cheap flights between cities
- Comparing routing options (open-jaw, multi-city, etc.)

## Quick Reference

```bash
# Basic search (free, no API key)
letsfg search <ORIGIN> <DEST> <DATE>

# Round trip
letsfg search CVG BKK 2026-09-01 --return 2026-09-25

# Fast mode (~25 connectors, 20-40s instead of 6+ min)
letsfg search CVG BKK 2026-09-01 --mode fast

# Filter cabin class
letsfg search LHR JFK 2026-06-01 --cabin C    # business
letsfg search LHR JFK 2026-06-01 --cabin F    # first

# Limit stops
letsfg search JFK LHR 2026-05-01 --max-stops 0  # direct only

# Multiple passengers
letsfg search LHR SIN 2026-06-01 --adults 2 --children 1

# Sort by price or duration
letsfg search LON BCN 2026-04-01 --sort price
letsfg search LON BCN 2026-04-01 --sort duration

# JSON output for parsing
letsfg search CVG PUJ 2026-05-22 --json

# Resolve city name to IATA code
letsfg locations "Punta Cana"
letsfg locations "Sosua"
```

## IATA Code Lookup

Common airports for trips we're planning:
- **CVG** = Cincinnati/Northern Kentucky (home airport)
- **BKK** = Bangkok Suvarnabhumi
- **DMK** = Bangkok Don Mueang (budget carriers)
- **MNL** = Manila Ninoy Aquino
- **CRK** = Clark International (near Angeles City/Pampanga)
- **PUJ** = Punta Cana (closest to Sosua, Dominican Republic)
- **STI** = Santiago (Dominican Republic, alternative)
- **SDQ** = Santo Domingo

Use `letsfg locations "city name"` to find any airport.

## Output Parsing (JSON mode)

```bash
letsfg search CVG BKK 2026-09-01 --mode fast --limit 5 --json
```

Parse with Python:
```python
import json, subprocess
result = subprocess.run(['letsfg', 'search', 'CVG', 'BKK', '2026-09-01', '--mode', 'fast', '--json'], capture_output=True, text=True)
data = json.loads(result.stdout)
for offer in data.get('offers', [])[:5]:
    print(f"${offer['price']} {offer['currency']} | {', '.join(offer['airlines'])} | {offer['total_stopovers']} stops")
```

## Search Modes

| Mode | Connectors | Speed | Best For |
|------|-----------|-------|----------|
| `--mode fast` | ~25 (OTAs + key airlines) | 20-40s | Quick price checks |
| (default) | 200+ (all connectors) | 2-10 min | Thorough comparison |

**Always use `--mode fast` first** for quick estimates. Run full search when ready to book.

## Price Benchmarks

When reporting prices to user, use these scales:
- 🔥 **Steal**: Under 40% of average fare for route
- ✅ **Good deal**: 40-70% of average
- 😐 **Average**: 70-100%
- 💸 **Overpaying**: 100%+

## First-Time Setup

LetsFG needs Playwright browsers installed before first use:

```bash
# Install LetsFG
pip install letsfg --break-system-packages

# Install Playwright Chromium browser (required!)
playwright install chromium
```

**Python version conflict**: LetsFG installs with system python but Playwright may have version mismatches. If you see `chromium-1208` not found errors:
```bash
# Install playwright for system python
/usr/bin/python3 -m pip install playwright --break-system-packages
/usr/bin/python3 -m playwright install chromium
```

## When LetsFG Fails: Google Flights Fallback

LetsFG uses Playwright browsers that require an X server. On headless servers without a display, **all connectors timeout** — even `--max-browsers 0` doesn't help. If LetsFG hangs for >60s, switch to Google Flights via browser.

### Google Flights URL Pattern
```
https://www.google.com/travel/flights?q=flights+from+{ORIGIN}+to+{DEST}+on+{YYYY-MM-DD}+return+{YYYY-MM-DD}&curr=USD
```

### Extracting Flight Data
After navigating to the URL, use JavaScript console to pull structured data:
```javascript
const items = document.querySelectorAll('li');
const results = [];
items.forEach(li => {
  const text = li.textContent.replace(/\s+/g, ' ').trim();
  if (text.includes('round trip') || text.includes('$')) {
    results.push(text.substring(0, 400));
  }
});
JSON.stringify(results.slice(0, 10), null, 2);
```

### Multi-Month Comparison
For comparing prices across months, search each month individually via browser and compile results. Google Flights returns structured data including price, airline, stops, layover duration, and total flight time.

### Pros/Cons vs LetsFG
| | LetsFG | Google Flights |
|--|--------|----------------|
| Speed | 20-40s (fast mode) | ~10s per search |
| Coverage | 400+ airlines | Major airlines + OTAs |
| Headless server | ❌ Fails without X server | ✅ Works via browser |
| Output | JSON, parseable | Requires JS extraction |
| Price accuracy | Raw airline prices | Includes OTA markup |

## Pitfalls

- **Playwright browsers must be installed** — first run fails without them. Always run `playwright install chromium` after installing letsfg
- **LetsFG hangs on headless servers** — no X server = all connectors timeout. Detect: if no output after 60s in fast mode, abort and use Google Flights fallback above
- **Output to files for clean results** — CLI prints asyncio cleanup errors at the end. Redirect to file:
  ```bash
  letsfg search CVG BKK 2026-09-01 --mode fast > /tmp/results.txt 2>/dev/null
  ```
- **Full search is slow** (2-10 min) — always use `--mode fast` for quick checks
- **Some connectors will fail** — normal in fast mode. Results still come from working connectors
- **CVG is a mid-size hub** — fewer direct Asia routes, connections needed
- **Sosua is near Puerto Plata (POP)** not Punta Cana (PUJ) — but PUJ has more flights. Check both with `letsfg locations`
- **September = typhoon season** for Philippines — factor into planning
- **asyncio errors at end are noise** — ignore `Event loop is closed` tracebacks after results display

## Multi-Airport Comparison

When destination has multiple airports, search all viable options:

```bash
# Example: Sosua, DR — closest airports are POP, PUJ, SDQ
letsfg search CVG PUJ 2026-05-24 --return 2026-05-28 --mode fast --limit 5 > /tmp/puj.txt
letsfg search CVG POP 2026-05-24 --return 2026-05-28 --mode fast --limit 5 > /tmp/pop.txt
letsfg search CVG SDQ 2026-05-24 --return 2026-05-28 --mode fast --limit 5 > /tmp/sdq.txt
```

Then compare price vs ground transport time:
- **Closer airport** (POP) = shorter drive but often fewer flights = higher price
- **Busier airport** (PUJ) = more flights, cheaper, but longer ground transfer
- Calculate: flight price + rental car/transfer cost + travel time

Use `letsfg locations "city name"` to discover all nearby airports.

## Workflow for Trip Planning

1. **Resolve locations**: `letsfg locations "destination city"`
2. **Search multiple airports**: Run `--mode fast` on each viable airport
3. **Compare price + time**: Factor in ground transport to final destination
4. **Quick price check**: `letsfg search ORIG DEST DATE --mode fast`
5. **Compare routing**: Try open-jaw (fly into city A, out of city B)
6. **Full search**: Remove `--mode fast` for complete results when ready
7. **Save to Obsidian**: Update trip file in `00-HQ/Travel/{Country}/`

## Booking Flow (when ready)

```bash
# 1. Register (one time)
letsfg register --name "Gentech" --email "jordan@example.com"

# 2. Star GitHub repo (one time, for free unlock/book)
letsfg star --github <username>

# 3. Search → Unlock → Book
letsfg search CVG BKK 2026-09-01 --mode fast
letsfg unlock off_xxx
letsfg book off_xxx --passenger '{"id":"pas_0","given_name":"Jordan","family_name":"...","born_on":"...","gender":"m","title":"mr"}' --email jordan@example.com
```
