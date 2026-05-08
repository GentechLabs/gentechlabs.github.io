---
name: travel-research
description: "Research travel destinations, timing, weather, flights, budgets, and save findings to Obsidian vault. Covers seasonal climate analysis, multi-city routing strategies, LetsFG flight search, Google Flights fallback, price benchmarking, and trip planning templates."
tags: [travel, research, weather, flights, planning, budget]
trigger: "When the user is planning travel — researching destinations, comparing timing/weather, searching flights (LetsFG/Google Flights), optimizing multi-city routing, or saving trip plans to Obsidian. Load this umbrella to access both weather research and flight-search skill modules."
related_skills:
  - defi
version: 1.0.0
author: Gentech
---

# Travel Research (Umbrella)

This umbrella covers the full travel-planning research workflow: destination weather & climate analysis by season; flight search, comparison, and price benchmarking (LetsFG + Google Flights fallback); multi-city/open-jaw routing optimization; and saving structured findings to the Obsidian vault.

> **Consolidated skills:** `travel-research`, `letsfg-flights`.

## Quick Decision Table

| User Intent | Go To Section |
|-------------|---------------|
| "When should I visit X? What's the weather?" | [1. Destination & Climate Research](#1-destination--climate-research) |
| "Find flights, compare prices/routing options" | [2. Flight Search — 2a. LetsFG](#2a-letsfg-search) • [2b. Google Flights fallback](#2b-google-flights-fallback) |
| "What's the best time/cheapest month?" | [1. Destination & Climate Research](#1-destination--climate-research) — seasonal pricing |
| "Multi-city trip: how to route this?" | [3. Multi-City Routing Strategies](#3-multi-city-routing-strategies) |
| "Save this trip plan to Obsidian" | [4. Vault Template](#4-vault-template) |

---

## 1. Destination & Climate Research

**Original skill:** `travel-research`

Research destinations for optimal travel timing, weather, and budget. Core questions: best months to visit, rainy vs dry season, tourism peaks, and seasonal price trends.

### Workflow

1. Identify destination + climate zone
2. Research weather by month (climatestotravel.com, lonelyplanet.com)
3. Research price trends
4. Creative flight routing (open-jaw, transit hub, budget-carrier hacks, ground combos)
5. Synthesize recommendation
6. Save to Obsidian vault

### Sources (ranked)

| Rank | Source | What |
|------|--------|------|
| 1 | `climatestotravel.com/climate/{country}/{city}` | Monthly temp/rain + "best time" |
| 2 | `lonelyplanet.com/articles/best-time-to-visit-{country}` | Tourist-season + festivals |
| 3 | `weatherspark.com` | Visual climate |
| 4 | Google Flights/Kayak/Skyscanner | Flight price trends |
| 5 | Booking.com/Agoda | Hotel pricing by month |

### Pitfalls

- Bot detection (use DuckDuckGo or direct nav)
- Southern hemisphere season reversal
- Basin-specific typhoon/hurricane risk
- Off-peak ≠ bad (monsoon often = afternoon showers)
- Always verify city in page heading (WeatherSpark redirects)

> **Full original content** — extended routing-playbook detail, price benchmarking scales, Obsidian conventions, verification checklist, multi-airport comparison, extended pitfalls: `references/travel-research-full.md`

---

## 2. Flight Search

### 2a. LetsFG Search

**Original skill:** `letsfg-flights`

Search 400+ airlines (raw prices) via local CLI — zero markup, typically $20-50 cheaper than OTAs.

#### Core Commands

```bash
letsfg search <ORI> <DES> <DATE> [--return DATE] [--mode fast] [--cabin C|F] [--max-stops 0] [--sort price|duration] [--json]
```

- `--mode fast`: 20–40 s, ~25 connectors
- `--json`: parseable output

#### JSON parse pattern

```python
import json, subprocess
result = subprocess.run(['letsfg','search','CVG','BKK','2026-09-01','--mode','fast','--json'], capture_output=True, text=True)
data = json.loads(result.stdout)
for offer in data.get('offers', [])[:5]:
    print(f"${offer['price']} {offer['currency']} | {', '.join(offer['airlines'])} | {offer['total_stopovers']} stops")
```

#### First-Time Setup

```bash
pip install letsfg --break-system-packages
playwright install chromium  # REQUIRED
# If python version conflict:
/usr/bin/python3 -m pip install playwright --break-system-packages
/usr/bin/python3 -m playwright install chromium
```

#### Price benchmarks

| Benchmark | % avg | Action |
|-----------|-------|--------|
| 🔥 Steal | <40% | Book immediately |
| ✅ Good | 40–70% | Solid candidate |
| 😐 Average | 70–100% | Acceptable if dates fixed |
| 💸 Overpay | >100% | Keep searching |

#### Pitfalls

- Chromium install **required**
- Fails on headless servers (X-server) — all connectors timeout ~60s
- asyncio cleanup errors at EOL are noise → redirect `> file 2>/dev/null`
- Full search 2–10 min — always `--mode fast` first
- Some connectors fail — still get results from working ones

If LetsFG hangs >60s on headless, abort and use Google Flights fallback.

> **Full original content** — IATA lookup table, multi-airport comparison, booking flow, fallback snippet: `references/letsfg-flights-full.md`

---

### 2b. Google Flights Fallback

#### URL

```
https://www.google.com/travel/flights?q=flights+from+{ORIGIN}+to+{DEST}+on+{YYYY-MM-DD}+return+{YYYY-MM-DD}&curr=USD
```

#### Structured extraction (browser console)

```javascript
const items = document.querySelectorAll('li');
const results = []; items.forEach(li => { const t=li.textContent.replace(/\s+/g,' ').trim(); if(t.includes('round trip')||t.includes('$')) results.push(t.substring(0,400)); }); JSON.stringify(results.slice(0,10),null,2);
```

#### Calendar multi-month

Use vision to navigate date picker arrows; console-search "September" + "$" to surface prices.

#### Trade-offs

| | LetsFG | Google Flights |
|--|--------|----------------|
| Raw airline prices | ✅ | ❌ (OTA markup) |
| Headless friendliness | ❌ | ✅ |
| Parseable JSON | ✅ | ❌ (JS extraction) |
| Coverage | 400+ | Major carriers |

---

## 3. Multi-City Routing Strategies

1. **Direct** — baseline
2. **Open-jaw / multi-city** — Fly IN A, OUT B; connect via budget hop (Scoot/AirAsia/Cebu)
3. **Transit hub** — US → major Asian hub (BKK/KUL/SIN) → destination
4. **Budget flash-sale hack** — Secret Flying / Scott's Cheap Flights alerts
5. **Ground transport combo** — Fly into hub, bus/train to final (cheapest in SE Asia)
6. **Multi-country overlapping** — A → overland → B → fly home from B (avoid backtrack)

**Connection protection:** Single ticket = airline handles missed connections. Separate bookings = your problem. Premium connection usually worth it for tight layovers.

**Short-layover hubs** (2–4hr): Tokyo (NRT/HND), Seoul (ICN), Taipei (TPE). Avoid ME hubs (DXB/DOH/IST).

---

## 4. Vault Template

Location: `$OBSIDIAN_VAULT_PATH/00-HQ/Travel/{Country}/{Year}-{Trip-Name}.md`

```markdown
# {Destination} Trip — {Year}

**Date:** {today}
**Status:** Research Phase
**Travelers:** {who}
**Home airport:** {code}
**Months:** {months}

## Itinerary Draft
1. {leg 1}
2. {leg 2}

## Weather Summary
{data}

## Flight Research
{options}

## Price Insights
{peak/off-peak}

## Accommodation
{}

## Estimated Budget
{table}

## Recommendation
{reasoning}

## Next Steps
- [ ] Finalize dates
- [ ] Set fare alerts
- [ ] Book accommodation
- [ ] Research activities
- [ ] Visa requirements
- [ ] Travel insurance
```

---

## Price Benchmarking

| Benchmark | % avg | Action |
|-----------|-------|--------|
| 🔥 Steal | <40% | Book |
| ✅ Good | 40–70% | Candidate |
| 😐 Average | 70–100% | OK |
| 💸 Overpay | >100% | Search more |

---

## Related Umbrellas

- **`hackathon`** — event travel budgeting
- **`market-macro-monitor`** — currency/rate trends

---

## References (Session-Specific Detail)

- `references/travel-research-full.md`
- `references/letsfg-flights-full.md`
