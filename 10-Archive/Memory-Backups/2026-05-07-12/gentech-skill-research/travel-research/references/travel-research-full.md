---
name: travel-research
description: Research travel destinations — weather/climate by season, price trends, best time to visit, and save findings to Obsidian vault.
tags:
  - travel
  - research
  - weather
  - planning
---

# Travel Research

Research destinations for optimal travel timing, weather, and budget. Save structured findings to Obsidian vault.

## When to Use

- User asks about best time to visit a destination
- User wants to compare travel months for weather or prices
- User asks about seasonal tourism (rainy/dry season, peak/off-peak)
- User is planning a trip and needs destination intel
- User asks about flight prices or routing options
- User wants multi-city or multi-country trip planning

## Workflow

### 1. Identify the destination and climate zone

- Determine the country/region and its climate type (tropical, temperate, etc.)
- Note the hemisphere (seasons are reversed in Southern Hemisphere)
- Find the nearest major airport(s)

### 2. Research weather by season

Use these sources (prefer climatestotravel.com for structured monthly data):
- `climatestotravel.com/climate/{country}/{city}` — temperature tables, rainfall, "best time" section
- `lonelyplanet.com/articles/best-time-to-visit-{country}` — tourist-season guidance
- `weatherspark.com` — visual climate comparisons

Collect for each candidate month:
- Average high/low temperature (°F and °C)
- Rainfall level and rainy season status
- Typhoon/hurricane/cyclone risk (if applicable)
- Humidity and comfort level

### 3. Research price trends

- **Peak vs off-peak season**: Dry/best-weather months = peak prices (30–50% higher)
- **Rainy/off-season**: Lower hotel and flight prices, fewer crowds
- **Festivals/holidays**: Local events can spike prices (Holy Week, Chinese New Year, etc.)
- **Source sites**: Kayak, Skyscanner, Google Flights for flight trends; Booking.com/Agoda for hotels

### 3b. Flight price research

For actual flight prices (not just trends), use the `letsfg-flights` skill:
- **LetsFG CLI**: `letsfg search ORIG DEST DATE --mode fast` — searches 25+ connectors in 20-40s
- Free, no API key needed for search
- Returns real airline prices, $20-50 cheaper than OTAs
- See `letsfg-flights` skill for full command reference and output parsing

For trend/benchmark data, also check:
- Google Flights calendar (may hit captchas — use browser_vision to navigate)
- Kayak, Skyscanner for price history
- Secret Flying, Scott's Cheap Flights for flash sales

### 3c. Creative flight routing analysis

When the user is price-conscious, compare multiple routing strategies — not just direct flights:

1. **Direct route**: US city → destination airport (baseline price)
2. **Open-jaw multi-city**: Fly INTO city A, fly OUT of city B
   - Often priced same as round trip — no penalty for mixing cities
   - Connect the two cities with a cheap budget carrier hop
   - Example: LAX→BKK + MNL→LAX open-jaw + BKK→MNL on Scoot ($92)
3. **Transit hub route**: US → major Asian hub (Bangkok, Kuala Lumpur, Singapore) → destination on budget carrier
   - Calculate total cost including the second leg
   - Note: often more expensive, but offers a stopover city to explore
4. **Budget carrier hack**: Check Cebu Pacific, AirAsia, Scoot for sale fares
   - Flash sales can drop prices 30–50% below normal
   - Set fare alerts on Google Flights, Secret Flying, Scott's Cheap Flights
5. **Bus/ground transport combo**: Fly into nearest major hub, take bus/train to final destination
   - Example: Manila → Angeles City bus ($5–15, 2.5 hrs) vs flying into smaller airport
   - Often the cheapest option, especially in Southeast Asia
6. **Multi-country trip**: For 2+ country trips, route to maximize overlap
   - Fly into Country A, overland/budget flight to Country B, fly home from Country B
   - Avoids backtracking and often cheaper than separate round trips

**Airport considerations:**
- Mid-size airports (CVG, IND, etc.) rarely have direct international flights to Asia
- May need domestic connection (CVG→LAX, CVG→ORD) before international leg
- Check if separate domestic + international bookings are cheaper than single itinerary
- Single itinerary = protected connections (airline rebooks if delayed); separate = your risk

**Price benchmarking** — include what's "good" for the route:
- 🔥 **Steal**: Under 40% of average fare
- ✅ **Good deal**: 40–70% of average
- 😐 **Average**: 70–100%
- 💸 **Overpaying**: 100%+

### 4. Synthesize recommendation

Structure the output as a comparison table or bullet points:
- Month-by-month weather summary
- Price relative indicator (💰 = cheapest, 💰💰 = moderate, 💰💰💰 = peak)
- Typhoon/storm risk level (if applicable)
- Clear recommendation with reasoning

### 5. Save to Obsidian vault

**Convention:** All travel goes in `00-HQ/Travel/{Country}/` with country subfolders.

```bash
VAULT="${OBSIDIAN_VAULT_PATH:-/root/vaults/gentech}"
COUNTRY="{Country}"  # e.g. Philippines, Thailand, Japan
mkdir -p "$VAULT/00-HQ/Travel/$COUNTRY"
cat > "$VAULT/00-HQ/Travel/$COUNTRY/{Year}-{Trip-Name}.md" << EOF
# {Destination} Trip — {Year}

**Date:** {today}
**Status:** Research Phase
**Travelers:** {who}
**Home airport:** {airport code}
**Months Under Consideration:** {months}

## Itinerary Draft
1. {leg 1}
2. {leg 2}

## Weather Summary
{month-by-month data}

## Flight Research
{routing options with prices}

## Price Insights
{peak/off-peak analysis}

## Accommodation
{options and pricing}

## Estimated Budget
{table of costs}

## Recommendation
{your pick with reasoning}

## Next Steps
- [ ] Finalize dates
- [ ] Set fare alerts
- [ ] Book accommodation
- [ ] Research activities
- [ ] Visa requirements
- [ ] Travel insurance
EOF
```

If the country folder already exists, create/update the trip file inside it — don't create duplicates.

## Research Sources (ranked by reliability)

1. **climatestotravel.com** — Best for structured monthly climate data (temp, rainfall, "when to go")
2. **lonelyplanet.com** — Best for tourist-season guidance and festival calendars
3. **weatherspark.com** — Good visual comparisons, sometimes redirects oddly
4. **Google Flights / Kayak / Skyscanner** — Flight price trends (may hit captchas)
5. **Booking.com / Agoda** — Hotel pricing by month

## Output format for routing comparison

Structure creative routing options as:

```
**Option 1: Direct (CHEAPEST/SIMPLEST)**
- Flight: $X–$Y RT
- Ground transport: $Z
- Total: ~$A–$B RT

**Option 2: Transit hub**
- Leg 1: $X–$Y
- Leg 2: $Z–$W
- Total: ~$A–$B RT
- Note: stopover bonus or extra hassle?

**Option 3: Budget carrier hack**
- Sale price: $X–$Y RT
- How to find: [specific sites/alerts]
```

End with price benchmarks: what's a steal vs overpaying for that specific route.

### 3c. Layover and connection preferences

When recommending routes, consider user's layover tolerance:

**Short layover hubs (2-4hr, ideal for connection-averse travelers):**
- **Tokyo (NRT/HND)**: ANA, JAL — efficient connections, 2-3hr typical
- **Seoul (ICN)**: Korean Air, Asiana — fastest hub, 1.5-3hr, immigration-free transit
- **Taipei (TPE)**: EVA Air, China Airlines — 2-4hr, clean and efficient

**Avoid for short layovers:**
- Middle East hubs (DXB, DOH, IST) — almost always 5-8hr layovers
- Any routing requiring re-checking bags (separate tickets on budget carriers)

**Connection protection:** Single-ticket itineraries = airline rebooks if delayed. Separate bookings = your problem. Worth the premium for tight connections.

## Pitfalls

- **Bot detection**: Google, Skyscanner, and Kayak often block automated browsers. Use DuckDuckGo (`html.duckduckgo.com/html/`) or direct site navigation as fallbacks
- **Google Flights calendar**: Prices may not load for distant months until you scroll within the calendar dialog — use `browser_vision` to find navigation arrows. Extract prices via `browser_console` searching for "September" + "dollar" in page text
- **Captcha walls**: Skyscanner and some sites will block headless browsers entirely — fall back to CheapFlights, Google Flights, or manual searches
- **Wrong location redirects**: WeathersSpark sometimes serves wrong locations — always verify the city name in the heading
- **Season reversal**: Southern Hemisphere destinations (Australia, Argentina, South Africa) have reversed seasons — don't assume June = summer
- **Typhoon/hurricane seasons vary by basin**: Atlantic (Jun–Nov), Western Pacific (year-round, peak Aug–Oct), Indian (Apr–Dec)
- **Off-peak ≠ bad**: Rainy season often means daily afternoon showers, not constant rain — mornings can be clear
- **Google Flights URL patterns**: Use `/m/` codes for cities: `/m/0f4vj` = BKK, `/m/017fl` = MNL, `/m/0hzl` = CVG. Multi-city URLs need `tfs=CBwQAhop` prefix
- **One-way long-haul from SE Asia**: Often $500+ solo. Open-jaw tickets avoid this entirely

## User Preferences (check memory before research)

Before starting travel research, check memory for:
- **Home airport** (affects routing and pricing significantly)
- **Layover preference** (short 2-4hr vs long cheap layovers)
- **Travel companions** (solo, couple, group affects accommodation)
- **Budget sensitivity** (affects how creative to get with routing)
- **Trip purpose** (birthday, vacation, work + leisure affects flexibility)

## Verification

After research, confirm:
- [ ] Weather data sourced from at least 1 reliable climate site
- [ ] Price trends mentioned (even if general peak/off-peak)
- [ ] Clear recommendation given with reasoning
- [ ] Research saved to Obsidian vault at `00-HQ/Travel/`
