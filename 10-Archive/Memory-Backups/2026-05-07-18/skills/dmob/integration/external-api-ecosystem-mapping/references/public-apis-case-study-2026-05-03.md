# Session Reference: Public-APIs Toolkit — Travel Agent Integration

**Date:** 2026-05-03  
**Agent:** DMOB (Labs)  
**Vault:** `02-Labs/00-AAE/travel-agent/`  
**Deliverables:**
- `public-apis-integration.md` (13KB integration plan)
- `api-catalog.json` (machine-readable inventory)
- `quickstart-checklist.md` (8-step setup)

---

## Session Context

Jordan requested mapping the `public-apis/public-apis` GitHub repo onto the Hermes Travel Agent stack to avoid paying for SaaS tools. Goal: identify free/cheap APIs across domains relevant to travel (flights, routing, weather, currency, events, imagery) and produce a phased integration plan with cost estimates.

---

## Extraction Methodology

**Source:** Cloned `public-apis` repo to `/tmp/public-apis/` (README.md, 197KB, 1911 lines, 51 categories).

**Relevant categories identified:**
- `### Transportation` (line 1703)
- `### Geocoding` (line 924)
- `### Weather` (line 1869)
- `### Currency Exchange` (line 442)
- `### Events` (line 729)
- `### Tracking` (line 1687) — shipment tracking (secondary)
- `### Vehicle` (line 1806) — car data (secondary)
- `### Photography` (line 1386) — imagery

**Parsing technique:**
```python
import re
with open('README.md') as f:
    content = f.read()

# Locate section by header
section = re.search(r'^### Transportation\n(.*?)(?=\n### |\Z)', content, re.DOTALL)
if section:
    rows = section.group(1).strip().split('\n')
    for row in rows:
        if row.startswith('|') and '[' in row:
            # Split markdown table row
            parts = [p.strip() for p in row.split('|')]
            # parts[1]=Name, parts[2]=Description, parts[3]=Auth, parts[4]=HTTPS, parts[5]=CORS
```

**Table column mapping:**
| Column | Index (after split) | Value |
|--------|-------------------|-------|
| Name + URL | `parts[1]` | `[API Name](url)` |
| Description | `parts[2]` | Short description |
| Auth | `parts[3]` | `No`, `apiKey`, `OAuth`, `User-Agent` |
| HTTPS | `parts[4]` | `Yes` / `No` |
| CORS | `parts[5]` | `Yes` / `No` / `Unknown` |

**Total APIs extracted:** 40+ travel-relevant entries across categories.

---

## Tier-1 Selection Criteria

For **Phase 1 (ship immediately)**:
- ✅ Free tier ≥ 500 requests/month (or unlimited)
- ✅ HTTPS required (security gate)
- ✅ Auth: `No` or `apiKey` preferred; `OAuth` OK if essential
- ✅ CORS: `Yes` or `Unknown` (server-side calls OK)
- ✅ Directly maps to core travel agent features

**Final Tier-1 APIs:**

| Service | API | Free Tier | Auth | Use |
|---------|-----|-----------|------|-----|
| Flights | Amadeus for Developers | 2K req/mo | OAuth | Search + basic booking |
| Flights (backup) | Sabre for Developers | Limited | apiKey | Alternative search |
| Routing | GraphHopper | 500/day | apiKey | Turn-by-turn routes |
| Weather | Open-Meteo | Unlimited | No | Forecasts (default) |
| Weather (alt) | Weatherstack | 250/mo | apiKey | Backup with historical |
| Geocoding | Google Maps Geocoding | $200 credit | apiKey | Address → lat/lng |
| Geocoding (alt) | Mapbox | 50K/mo | apiKey | Vector maps |
| Currency | Frankfurter | Unlimited | No | Rate conversion |
| Currency (alt) | ExchangeRate.host | Unlimited | No | Crypto support |
| Transit (London) | TfL API | Open | No | Realtime Underground/Bus |
| Transit (Paris) | RATP Open Data | Open | No | Metro/RER |
| Transit (global) | TransitLand | Open | No | Multi-city normalization |
| Imagery | Unsplash | 50 req/hr | OAuth | Destination photos |
| Imagery (alt) | Pexels | 20K/mo | apiKey | Videos + photos |
| Reviews (Phase 2) | Tripadvisor | Limited | apiKey | Hotel/attraction ratings |
| Reviews (Phase 2) | Yelp | 500/day | OAuth | Local business reviews |

**Notable exclusions:**
- `HTTP`-only APIs rejected (security policy)
- `OAuth`-only with complex flows deferred to Phase 2 (Grab, Amadeus sandbox still included as essential)
- Regional-only APIs (e.g., Transport for Berlin) deferred to city-specific expansions

---

## Integration Architecture

```
Hermes Travel Agent (Telegram bot)
        ↓
  Skill Layer (Python @skill methods)
        ↓
  Public-API Gateway (httpx.AsyncClient + retry logic)
        ↓
  External Services (Amadeus, GraphHopper, Open-Meteo, …)
```

**Design principles:**
- Hermes is the **brain** (decision logic), not the data source
- Each external call wrapped with:
  - Timeout (10s default)
  - Retry with exponential backoff (3 attempts)
  - Fallback chain (primary → backup → cached → error message)
- All responses normalized to agent-friendly dicts before returning to LLM

---

## Cost Analysis (Monthly)

| API | Free Tier | Unit Cost Post-Free | Estimated Usage | Monthly Cost |
|-----|-----------|--------------------|-----------------|--------------|
| Amadeus | 2,000 req/mo | $0.0025/flight offer | 1,500 | $0 (within free) |
| GraphHopper | 500/day ≈ 15K/mo | $0.003/req | 5,000 | $0 (within free) |
| Open-Meteo | Unlimited | Free | 2,000 | $0 |
| Google Geocoding | $200 credit ≈ 28K loads | $0.005/1K | 10,000 | $0 (within credit) |
| Frankfurter | Unlimited | Free | 500 | $0 |
| Unsplash | 50/hr ≈ 36K/mo | Free (attribution) | 1,000 | $0 |
| **Total Phase 1** | | | | **$0** |

**Buffer for overages:** Budget $50/mo for occasional paid API use (e.g., Weatherstack backup, Yelp premium).

---

## Skill Skeleton (from plan)

Key methods to implement:

```python
class TravelAgentSkill(SkillBase):
    @skill(priority=1)
    async def weather_forecast(self, city: str, days: int = 7):
        """Open-Meteo primary, Weatherstack fallback."""

    @skill(priority=1)
    async def convert_currency(self, amount: float, from_cur: str, to_cur: str):
        """Frankfurter (free, no auth)."""

    @skill(priority=1)
    async def geocode(self, address: str):
        """Google Maps → Mapbox fallback."""

    @skill(priority=2)
    async def flight_search(self, origin: str, destination: str, date: str):
        """Amadeus OAuth2 token flow → Sabre backup."""

    @skill(priority=2)
    async def transit_route(self, origin: str, destination: str, city: str):
        """City-specific: TfL, RATP, TransitLand."""

    @skill(priority=3)
    async def hotel_search(self, city: str, check_in: str, check_out: str):
        """Amadeus hotel or Impala direct."""

    @skill(priority=3)
    async def find_events(self, city: str, date_range: str):
        """Eventbrite, SeatGeek."""
```

---

## Key Learnings & Reusable Patterns

1. **Public-APIs as capability inventory:** The curated list is a treasure map — each section gives you a free data source.
2. **Security gate:** Filter `HTTPS=Yes` first. No exceptions.
3. **Tiering by auth complexity:** `No` < `apiKey` < `OAuth`. Save OAuth for essential features.
4. **Fallback chains critical:** Never rely on single provider. Even free APIs can go down.
5. **Two-artifact output:** Markdown (human) + JSON (machine) ensures future agents can parse the catalog.
6. **Cost transparency:** Always table unit costs + free tier caps so budget is visible from day 1.
7. **Skill blueprint first:** Before writing code, sketch `@skill` methods to validate coverage.

---

## Pitfalls Encountered

| Pitfall | Resolution |
|---------|------------|
| README markdown table parsing tricky | Regex with careful `split('|')` and index offsets; skip header/footer rows |
| Section boundaries shifted in repo | Locate headers via `^### Category` anchor, not hard line numbers |
| `CORS: Unknown` ambiguous | Assume server-side OK; CORS only matters if calling from browser |
| Amadeus OAuth adds complexity | Still included (essential), but noted as Tier 2 priority for initial MVP |
| Street View missing | Identified Mapillary/KartaView as free alternatives |
| Tripadvisor not in Transportation | Found in Open Data section — needed broader search |

---

## Artifacts Created

**Vault:**
```
02-Labs/00-AAE/travel-agent/
├── public-apis-integration.md  (13,245 words)
├── api-catalog.json             (JSON with 40+ entries)
├── quickstart-checklist.md      (8 steps, credential setup)
└── references/
    └── public-apis-session-2026-05-03.md  (this file)
```

**Posted to HQ:** Summary with top 7 APIs, cost estimate, architecture principle.

---

## Next Actions (from plan)

- [ ] Review API selections with Jordan
- [ ] Create credential vault folder
- [ ] Apply for keys: GraphHopper (instant), Amadeus (2–3 d), Google Maps (needs billing)
- [ ] Build skill skeleton `travel_agent_v1.py`
- [ ] Test APIs individually with sandbox keys
- [ ] Set up quota monitoring cron
- [ ] Wire into Hermes Telegram bot

---

*This reference captures the session's data extraction logic, decision criteria, and template structure for replicating the workflow in other domains (finance, media, blockchain).*
