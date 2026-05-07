---
name: public-api-integration-strategy
description: Systematically evaluate, select, and integrate public APIs (free/cheap SaaS alternatives) into an agent feature stack. Covers provider research, tier comparison, cost modeling, phased rollout, fallback chains, and licensing attribution.
tags: [api, integration, free-tier, cost-optimization, research, evaluation]
related_skills:
  - hackathon-tech-stack-evaluation  # similar scope-doc pattern but for frameworks not APIs
  - travel-flight-research          # domain-specific application example
  - defi-lp-monitoring              # cost monitoring pattern reuse
---

# Public API Integration Strategy

Evaluate and integrate external API services (REST/GraphQL) into agent features, prioritizing free/cheap tiers, planning phased rollout with fallbacks, and documenting cost/attribution/licensing requirements.

## When to Use

- Building an agent feature that needs external data/services (maps, weather, photos, POI, flights, etc.)
- Wanting to avoid paid SaaS where free/cheap alternatives exist
- Planning multi-phase integration with cost-aware scaling
- Need to document provider comparison, rate limits, and fallback chains
- Building on public-apis.github.io/public-apis curated directory

## Output Deliverables

1. **API Integration Map** — structured markdown with:
   - Category breakdown (flights, maps, weather, etc.)
   - Provider comparison tables (free tier vs paid, cost at scale)
   - Priority tiers (P0/P1/P2) for implementation phases
   - Fallback provider chains per category
   - Licensing/attribution requirements
   - Cost monitoring plan and budget estimates

2. **Implementation Roadmap** — phased plan:
   - Phase 1 (MVP): Minimal free-tier set sufficient for usable feature
   - Phase 2 (Enhanced): Add richer data, moderate cost if needed
   - Phase 3 (Premium/Scale): Commercial providers, scale cost modeling

3. **Hermes Skill Plan** (if needed) — which MCP servers vs REST API wrappers

## Research & Evaluation Framework

### Step 1: Scope API Requirements by Feature
Break down the agent feature into data/service needs:

```
Example — Travel Agent:
├── Flight search & pricing           → flight API (LetsFG already MCP)
├── Geocoding (address → coords)      → geocoding API
├── Map display + routing             → map tiles + directions API
├── Weather at destination            → weather API
├── Destination photos                → photo API (Unsplash)
├── Points of interest (restaurants)  → places/POI API
├── Local events                      → events API
└── Currency conversion               → exchange rates API
```

### Step 2: Systematic Provider Discovery
Use these sources, in order:

1. **public-apis/public-apis** GitHub — curated directory by category
   - Filter by `Category: Travel`, `Category: Maps`, `Category: Weather`, etc.
   - Check `Cors` column (important for browser demos)
   - Check `Auth` column (API key vs OAuth vs none)

2. **Awesome-XXXX lists** — e.g., `awesome-c Travel`, `awesome-maps`
   - Broader ecosystem beyond public-apis

3. **Direct provider docs** — once candidate list built, deep-dive:
   - Free tier limits (req/day or req/month)
   - Rate limits (per second/minute)
   - Pricing page for paid tiers
   - Terms of Service / attribution requirements
   - API stability (last update, GitHub activity)

### Step 3: Comparison Table Template
For each category (flights, maps, etc.), build table:

| Provider | Free Tier | Auth | Rate Limit | Cost at Scale | License/Attribution | Notes |
|----------|-----------|------|------------|---------------|---------------------|-------|
| Option A | 1k req/mo | API key | 10/sec | $0.001/req | CC-BY needed | ✅ Best free |
| Option B | 50k req/mo | OAuth | 100/sec | $10/mo 100k | No attribution | 🔄 fallback |
| Option C | Free self-host | None | self-determined | $VPS cost | Open source | ⚠️ ops overhead |

**Columns matter:**
- `Free Tier` — quantitative limit (note if "free tier" means self-host)
- `Auth` — simplicity: none > API key > OAuth > signed requests
- `Rate Limit` — affects UX responsiveness
- `Cost at Scale` — model 10k/day or 100k/month usage
- `License/Attribution` — UI/legal obligations
- `Notes` — flags: ✅ primary, 🔄 fallback, ⚠️ caveat

### Step 4: Priority Tiering
- **P0 (MVP):** Free tier sufficient for basic usable feature
- **P1 (Post-MVP):** Nice-to-have, moderate cost if needed
- **P2 (Commercial/Scale):** Premium features, paid services

Guideline: MVP should stay entirely within free tiers if possible (to validate).

### Step 5: Fallback Chain Design
For each category, choose primary + alternates:

```
Geocoding:
1. OpenCage (primary — easy, 2.5k/day free)
2. Nominatim self-host (fallback — unlimited but ops overhead)
3. Mapbox (paid fallback — if already have Mapbox account)
```

Encode in code: try provider 1, if fails/rate-limited → provider 2 → provider 3.

### Step 6: Cost Monitoring Plan
Even free APIs have hidden costs:
- **Self-hosted tile servers:** bandwidth + disk + RAM
- **Commercial free tier exhaustion:** monitor daily call count
- **Credit-based APIs:** track credit expiration (e.g., Google $200/mo)

Implement: cron job → daily usage log → alert at 80% threshold.

### Step 7: Licensing & Attribution Audit
Must-have:
- **Mapillary:** CC-BY-SA → show "© Mapillary contributors" in UI
- **OpenStreetMap:** ODbL → attribution required
- **Unsplash:** varies per photo (check API `photo.attribution` field)
- **Google/Mapbox:** standard attribution already handled by SDK

Create an `ATTRIBUTIONS.md` file in the project to document required credits.

### Step 8: Integration Architecture Decision
How will the agent call these APIs?

| Approach | When to Use | Example |
|----------|-------------|---------|
| **MCP Server** | API has community MCP or you can build one | LetsFG MCP already exists |
| **Direct REST wrapper skill** | Simple API, low friction | WeatherAPI → skill-weather.py |
| **Cache layer** | Expensive/repeated data | Geocode results cached SQLite |
| **Batch processing** | Non-real-time | Pre-fetch hospital POIs for 5 cities |

Prefer MCP when available (agent-native). Otherwise, wrap as Hermes skill.

## Known Pitfalls

- **Free tier vanish** — provider may shut down free tier; have 2 fallbacks
- **Rate limit surprises** — per-second vs per-day limits both matter; implement backoff
- **Attribution lawsuits** — some licenses require specific UI placement; document early
- **Self-hosting ops burden** — OSM tile server needs ~100GB disk, regular updates
- **Data staleness** — free APIs may have stale data (e.g., flight status delays)
- **CORS restrictions** — some APIs block browser calls; need proxy or server-side
- **API key leakage** — never commit keys; use env files and vault config
- **Credit expiration** — Google Cloud $200/mo promo disappears after 90 days; plan ahead

## Output Template

See `references/template-integration-map.md` for full markdown template.

## Related Skills References

- `hackathon-tech-stack-evaluation` — similar structured comparison, but for frameworks not APIs
- `travel-flight-research` — domain-specific instance of this methodology applied to flights
- `defi-lp-monitoring` — cost monitoring and threshold alerts pattern reuse
