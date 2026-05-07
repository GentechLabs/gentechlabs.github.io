---
name: external-api-ecosystem-mapping
description: "Systematically discover, evaluate, and plan integration of third-party public APIs for agent capabilities. Covers repository parsing, category filtering, free-tier analysis, phased rollout planning, skill skeleton authoring, and cost-aware architecture. Reusable across domains (travel, finance, blockchain, media)."
version: 1.0.0
author: DMOB
tags: [api-research, integration, cost-optimization, capability-planning, third-party]
trigger:
  - "map out [service] APIs"
  - "discover APIs for [domain]"
  - "integrate [domain] functionality via public APIs"
  - "research free APIs for [domain]"
  - "build [feature] using existing APIs"
  - "public-apis toolkit"
---

# 🔍 External API Ecosystem Mapping & Integration Planning

## When to Use

You need to add a new capability to an agent (Hermes, Colosseum, etc.) and want to:
- **Avoid building from scratch** — leverage existing battle-tested APIs
- **Minimize cost** — use free tiers where possible
- **Move fast** — ship in days not months
- **Plan architecture** — understand auth patterns, rate limits, fallback chains

**Typical prompts:**
- "Map out APIs for travel agent functionality"
- "What free APIs exist for [X] domain?"
- "Build [feature] using third-party services"
- "Research public APIs for [fintech, blockchain, media, etc.]"

## What This Skill Produces

| Artifact | Purpose | Format |
|-----------|---------|--------|
| **Integration Plan** | Architecture, tiering, cost analysis, skill blueprint | `00-AAE/[domain]/public-apis-integration.md` |
| **API Catalog** | Machine-readable inventory by category | `00-AAE/[domain]/api-catalog.json` |
| **Quickstart Guide** | Actionable setup checklist for implementers | `00-AAE/[domain]/quickstart-checklist.md` |
| **Skill Skeleton** | Code outline showing how to call the APIs | Embedded in plan |

## Workflow

### Phase 1 — Source Discovery
1. Identify authoritative API directory for domain:
   - Primary: `public-apis/public-apis` GitHub repo (curated, categories, free-tier info)
   - Alternatives: RapidAPI directory, domain-specific registries (e.g., aviationstack for flights)
2. Clone/fetch source to local workspace
3. Verify structure (README index, category sections, table format)

### Phase 2 — Extraction & Categorization
4. Parse readme to extract all API entries in relevant sections
   - Read markdown line-by-line
   - Match section headers by anchor: `^### [Category]`
   - Extract table rows with pattern `| [Name](url) | Description | Auth | HTTPS | CORS |`
5. For each API, capture:
   - `name`, `url`, `description`
   - `auth`: `No`, `apiKey`, `OAuth`, `User-Agent`
   - `https`: `Yes` / `No` (security gate)
   - `cors`: `Yes` / `No` / `Unknown`
   - `free_tier` (if mentioned in description or known from docs)
   - `use_case`: match to your agent's needs

### Phase 3 — Filtering & Prioritization
6. Filter criteria:
   - **Security first:** Require HTTPS (reject HTTP-only except internal/trusted)
   - **Free tier preferred:** Prioritize unlimited/no-auth or generous free tier
   - **CORS friendly:** `Yes` preferred for browser-based agents, `Unknown` acceptable
   - **Auth simplicity:** `No` > `apiKey` > `OAuth` (complexity cost)
7. Tier into phases:
   - **Tier 1 (Phase 1):** Free, simple, core functionality — ship immediately
   - **Tier 2 (Phase 2):** Paid but essential, or limited free tier — add after MVP
   - **Tier 3 (Phase 3+):** Nice-to-have, expensive — backlog

### Phase 4 — Architecture & Cost
8. Build integration diagram showing agent → API skill layer → external services
9. Create cost table:
   | API | Free Tier | Cost After | Monthly Est. | Priority |
10. Identify **fallback chains** (primary + backup API per service)
11. Plan credential storage (Hermes vault, env vars, secret rotation)

### Phase 5 — Output Generation
12. Write integration plan (markdown) including:
    - Purpose + source
    - Architecture diagram (ASCII or mermaid)
    - Tiered API table with rationale
    - Skill blueprint (Python class outline with `@skill` methods)
    - Credential storage pattern
    - Monitoring/quota tracking plan
    - Next steps checklist
13. Generate `api-catalog.json` structured as:
    ```json
    {
      "categories": {
        "CATEGORY": [
          { "name": "...", "url": "...", "auth": "...", "free_tier": "...", "use_case": "..." }
        ]
      },
      "source": "...",
      "pull_date": "..."
    }
    ```
14. Write quickstart checklist (apply for keys, set env, test, deploy)

## Skill Skeleton Template

```python
from hermes.skills import SkillBase
import httpx
import os

class DomainAgentSkill(SkillBase):
    """Agent capability using public APIs."""
    
    def __init__(self):
        # Credentials from Hermes vault / env
        self.api_key = os.getenv('API_KEY_NAME')
    
    @skill(priority=TIER)
    async def core_capability(self, ...):
        """Primary method — calls Tier-1 API."""
        url = "https://api.example.com/endpoint"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params={...}, headers={"Authorization": f"Bearer {self.api_key}"})
            return self._parse(resp.json())
    
    async def _fallback_method(self, ...):
        """Backup API if primary fails."""
        pass
    
    def _parse(self, data):
        """Transform API response into agent-friendly format."""
        pass
```

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| **Assuming free tier is permanent** | Check API docs for "free forever" vs "promotional period" — note expiry in plan |
| **HTTPS not guaranteed** | Reject HTTP-only for external calls; if unavoidable, add proxy/ tunnel warning |
| **OAuth complexity underestimated** | OAuth needs token refresh + webhook/callback handling — prefer apiKey for MVP |
| **Rate limits not tracked** | Build quota tracker script (cron + vault cache) before hitting limits |
| **No fallback chain** | Single-point-of-failure APIs cause outages — always identify 2+ providers per service |
| **Credentials in code** | Never hardcode keys — use Hermes secret store or env vars only |
| **Over-filtering** | Don't exclude APIs with `CORS: Unknown` — they may still work server-side |
| **Parsing markdown tables manually** | Use robust regex: `\| (.+?) \[(.*?)\]\((.*?)\) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|` |
| **Missing category boundaries** | README sections can shift — locate headers by `^### [Category]` anchor, not line number |
| **Outdated info** | Public-apis repo is community-maintained — verify each API's current pricing before use |

## Decision Matrix: API Selection

| Factor | Weight | Questions to Ask |
|--------|--------|-----------------|
| **Cost** | High | Is it truly free? Any rate limits? When does Paid kick in? |
| **Auth Simplicity** | High | No auth > apiKey > OAuth. Can Hermes handle OAuth flows? |
| **Reliability** | Medium | Uptime history? SLA? Community backing? |
| **Data Freshness** | Medium | Real-time vs daily vs monthly updates? |
| **Coverage** | Medium | Global vs regional? Multi-language? |
| **Terms of Use** | Low | Commercial restrictions? Attribution required? |
| **Sunset Risk** | Low | Actively maintained? Last commit? |

Score each API 1–5, sum to prioritize.

## Output Structure

```
02-AAE/[domain]/
├── SKILL.md                    # This high-level workflow
├── references/
│   ├── public-apis-extract-YYYY-MM-DD.md  # Session-specific data extraction notes
│   ├── cost-analysis-YYYY-MM-DD.md        # Quota calculations, billing thresholds
│   └── provider-quirks.md                 # OAuth flow details, webhook endpoints, etc.
├── templates/
│   ├── integration-plan-template.md       # Starter doc for new domains
│   ├── api-catalog.json-template          # JSON schema with example entry
│   └── skill-skeleton-template.py         # Python class with @skill decorators
├── scripts/
│   ├── parse-public-apis.py               # Extractor: README → JSON catalog
│   ├── check_quotas.py                    # Cron script to monitor usage
│   └── generate_plan.py                   # Scaffold integration plan from catalog
└── [domain]-integration/
    ├── public-apis-integration.md         # Full plan for this domain
    ├── api-catalog.json                   # Domain-specific catalog
    └── quickstart-checklist.md            # Actionable steps
```

## Example Session Walkthrough (Travel Agent)

**Task:** "Map out APIs for Hermes Travel Agent"

1. Clone `public-apis/public-apis` to `/tmp/public-apis`
2. Identify relevant sections: Transportation, Geocoding, Weather, Currency Exchange, Events, Photography
3. Extract table rows via regex from each section
4. Filter: HTTPS=Yes, Free tier preferred → keep 30+ APIs
5. Tier:
   - Tier 1: Amadeus (flights), GraphHopper (routing), Open-Meteo (weather), Frankfurter (currency), Google Maps (geocoding), Unsplash (imagery)
   - Tier 2: Tripadvisor (reviews), Impala (hotel inventory), Eventbrite (events)
6. Architecture diagram: Hermes Travel Skill → Public API layer → External services
7. Cost table: $0–$50/mo estimated
8. Output:
   - `travel-agent/public-apis-integration.md` (13KB)
   - `travel-agent/api-catalog.json` (structured list)
   - `travel-agent/quickstart-checklist.md` (8 steps)
   - Skill skeleton `travel_agent_v1.py` with `@skill` methods

**Result:** Ready-to-implement blueprint with fallback chains, credential plan, and phased rollout.

## Tracing to Other Domains

This pattern generalizes:

| Domain | Public-APIs Sections | Key APIs | Tier-1 Candidates |
|--------|---------------------|-----------|-------------------|
| **Travel** | Transportation, Geocoding, Weather, Currency | Amadeus, GraphHopper, Open-Meteo | ✓ Done |
| **Finance** | Finance, Currency Exchange, Blockchain | Plaid, Polygon, Finnhub, Alpha Vantage | Next |
| **Blockchain** | Blockchain, Cryptocurrency | Alchemy, QuickNode, Moralis, Etherscan | Use blockchain-operations skill |
| **Media** | Photography, Video, Music | Unsplash, Pexels, Giphy, YouTube | Next |
| **News** | News, Open Data | NewsAPI, Guardian, NYTimes | Quick |

To apply: change section filter, re-run extraction, rebuild plan.

## Related Skills

- `travel-planning` — Uses this skill's output to actually book trips; applies manual research where APIs lack
- `blockchain-operations` — Domain-specific integration pattern for on-chain data + DeFi protocols
- `hackathon-prep` — Uses API discovery to scope project feasibility
- `external-ai-integration-assessment` — Specialized variant for AI/voice/model APIs (LLM, TTS, STT)

## Quick Reference: API Auth Patterns

| Auth Type | Hermes Handling | Complexity |
|-----------|----------------|------------|
| `No` | Direct GET request | Trivial |
| `apiKey` | Load from env/secret store, add header `?key=` or `X-API-Key` | Easy |
| `OAuth` | Need `client_id` + `client_secret` → token endpoint → `Bearer` token + refresh logic | Medium–Hard |
| `User-Agent` | Set custom header | Trivial |

**Rule:** Prefer `No` or `apiKey` for MVP; reserve `OAuth` for essential features only.

## Monitoring & Quota Tracking

Create cron script (`scripts/check_quotas.py`):

```python
import json, httpx
from pathlib import Path

quotas_file = Path("cache/api_quotas.json")
data = json.loads(quotas_file.read_text())

for api, stats in data.items():
    used = stats["monthly_used"]
    limit = stats["free_tier_limit"]
    if used / limit > 0.8:
        send_telegram_alert(f"⚠️ {api} quota at {used}/{limit}")
```

Store per-API counters in vault; reset monthly. Alert at 80%, auto-rotate credentials at 100%.

---

*End of SKILL.md*
