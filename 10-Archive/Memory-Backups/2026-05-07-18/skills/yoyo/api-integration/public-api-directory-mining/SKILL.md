---
name: public-api-directory-mining
description: "Systematically extract, categorize, and prioritize APIs from public directory listings (e.g., public-apis/public-apis) into project-ready integration roadmaps."
version: 1.0.0
author: YoYo (Strategies)
license: MIT
metadata:
  hermes:
    tags: [api, integration, research, strategy, public-apis]
    related_skills: [hermes-agent, strategies]
---

# Public API Directory Mining

**Purpose:** Turn a raw API directory (like `public-apis/public-apis`) into a structured, prioritized integration plan for your project.

**When to use:** You need to discover free/cheap APIs for a project (travel, finance, maps, etc.) and want to avoid paying for SaaS tools. This skill extracts all relevant endpoints, tiers them by cost/auth requirements, and produces an implementation-ready adapter plan.

---

## 📋 Trigger Conditions

- User asks to "map out" or "catalog" available APIs for a domain
- User references `public-apis` repository or wants free/cheap alternatives to paid SaaS
- You need to build an integration inventory before implementation
- You're scoping a project's data source requirements

---

## 🔄 Methodology (4 Phases)

### Phase 1: Repository Harvesting

```bash
# 1. Clone the source directory (or use existing local copy)
git clone --depth=1 https://github.com/public-apis/public-apis /tmp/public-apis

# 2. Locate the Index section (typically a giant markdown table)
#    File: /tmp/public-apis/README.md
#    Pattern: Look for "## Index" heading, then ### category subsections
```

**Output:** Raw markdown table with columns: API name, description, auth, HTTPS, CORS.

---

### Phase 2: Semantic Filtering

```python
# Parse ### subsections within Index
# Filter categories by project-relevant keywords

travel_keywords = ['travel', 'transport', 'geocod', 'weather', 'photo', 'image',
                   'flight', 'hotel', 'currency', 'finance', 'food', 'event',
                   'location', 'map', 'place', 'tourism', 'booking']

relevant_categories = [
    cat for cat in all_categories
    if any(kw in cat.lower() for kw in travel_keywords)
]
```

**Output:** List of matching category names (e.g., Transportation, Geocoding, Weather, Photography, Currency Exchange).

---

### Phase 3: Structured Extraction

For each matching category:

1. Find table separator line: `|:---|:---|:---|:---|:---|`
2. Parse rows until blank/non-table line
3. Extract fields via `split('|')`:
   - `parts[1]` → name + URL (regex: `\[(.*?)\]\((https?://.*?)\)`)
   - `parts[2]` → description
   - `parts[3]` → auth (`No`, `apiKey`, `OAuth`)
   - `parts[4]` → HTTPS (`Yes`/`No`)
   - `parts[5]` → CORS (`Yes`/`No`/`Unknown`)

4. Normalize auth to three tiers:
   - **FREE** — `auth == "No"` (zero setup)
   - **KEYED** — `auth in ["apiKey", "OAuth"]` (requires key, but free tier exists)
   - **PAID** — any other descriptor (skip unless strategic)

**Output:** Structured dictionary:
```json
{
  "Category Name": [
    {
      "name": "API Name",
      "url": "https://...",
      "description": "...",
      "auth": "No|apiKey|OAuth",
      "https": "Yes",
      "cors": "Yes|No|Unknown"
    }
  ]
}
```

---

### Phase 4: Prioritization Matrix

Sort APIs within each category into **implementation tiers**:

| Tier | Criteria | Example |
|------|----------|---------|
| **Tier 1 — Immediate** | `auth == "No"` AND `description` matches core use case | Nominatim (geocoding), exchangerate.host (currency), 7Timer! (weather) |
| **Tier 2 — Keyed but Free** | `auth != "No"` AND free quota sufficient for prototype | Amadeus (2K/mo), Mapillary (10K/mo), OpenWeatherMap (60/day) |
| **Tier 3 — Strategic/Partnership** | Requires commercial agreement or paid plan | Booking.com Affiliate, Uber API, Stripe |

**Map to project layers:**
- Location Layer → Geocoding APIs
- Search Layer → Transportation APIs
- Context Layer → Weather + Currency APIs
- Visual Layer → Photography APIs

---

## 🎯 Adapter Design Pattern

All public-API integrations should follow the **CachedAdapter** base class:

```python
# templates/adapter-base.py
import redis
import requests
import os
import json
from typing import Optional

class CachedAdapter:
    """Base class for all travel API adapters with unified caching."""

    # Tiered TTLs by data volatility
    TTL = {
        'geocode': 86400,     # 24h — addresses rarely change
        'weather': 3600,      # 1h — forecasts update hourly
        'flights': 300,       # 5min — prices change fast
        'streetview': 2592000,  # 30d — imagery static for months
        'currency': 900,      # 15min — rates drift
    }

    def __init__(self):
        self.redis = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        self.session = requests.Session()
        # Set default headers if needed
        self.session.headers.update({'User-Agent': 'GenTech-Travel-Agent/1.0'})

    def _cache_key(self, prefix: str, *args) -> str:
        """Generate deterministic cache key from method + args."""
        key_parts = [prefix] + [str(a) for a in args]
        return f"travel:v1:{'::'.join(key_parts)}"

    def cached(self, prefix: str, ttl_name: str, fetch_fn, *args):
        """Get from cache or fetch and cache."""
        key = self._cache_key(prefix, *args)
        ttl = self.TTL.get(ttl_name, 3600)

        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)

        result = fetch_fn(*args)
        self.redis.setex(key, ttl, json.dumps(result))
        return result

    def _get(self, url: str, params: dict = None) -> dict:
        """Standardized GET with error handling."""
        try:
            resp = self.session.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "provider": self.__class__.__name__}
```

**Concrete adapter example:**

```python
# templates/geocoding-adapter.py
from .adapter-base import CachedAdapter

class NominatimAdapter(CachedAdapter):
    """OpenStreetMap Nominatim — free geocoding, 1 req/sec limit."""

    BASE_URL = "https://nominatim.openstreetmap.org"

    def geocode(self, address: str) -> dict:
        return self.cached(
            prefix="geocode",
            ttl_name="geocode",
            fetch_fn=self._geocode_fetch,
            address=address
        )

    def _geocode_fetch(self, address: str) -> dict:
        params = {'q': address, 'format': 'json', 'limit': 1}
        data = self._get(f"{self.BASE_URL}/search", params)
        if data:
            item = data[0]
            return {
                "lat": float(item['lat']),
                "lng": float(item['lon']),
                "formatted_address": item['display_name'],
                "confidence": 0.9,  # Nominatim doesn't provide score
                "provider": "nominatim"
            }
        return {"error": "not_found"}

class GeocodeXYZAdapter(CachedAdapter):
    """Fallback geocoder — no auth, simpler coverage."""

    BASE_URL = "https://geocode.xyz"

    def geocode(self, address: str) -> dict:
        # Implementation...
        pass
```

**Registry pattern:**

```python
# templates/registry.py
from .geocoding import NominatimAdapter, GeocodeXYZAdapter
from .weather import OpenWeatherMapAdapter, SevenTimerAdapter

ADAPTER_REGISTRY = {
    'geocode': {
        'primary': NominatimAdapter,
        'fallback': GeocodeXYZAdapter,
    },
    'weather': {
        'primary': SevenTimerAdapter,  # free-first
        'fallback': OpenWeatherMapAdapter,  # keyed, more accurate
    },
    # ...
}

def get_adapter(category: str, tier: str = 'primary'):
    return ADAPTER_REGISTRY[category][tier]()
```

---

## 📁 Vault Structure (Template)

```
03-Projects/Travel-Agent/
├── API-Adapters/
│   ├── __init__.py
│   ├── base.py                    # CachedAdapter (copy from templates/adapter-base.py)
│   ├── geocoding.py               # Import NominatimAdapter, GeocodeXYZAdapter
│   ├── flights.py                 # Amadeus + aviationstack adapters
│   ├── weather.py                 # 7Timer! + OpenWeatherMap
│   ├── currency.py                # exchangerate.host
│   ├── streetview.py              # Mapillary + OpenStreetCam cascade
│   └── registry.py                # Adapter lookup table
├── Demos/
│   └── travel-demo.md            # Interactive demo script
└── Integration-Tests/
    └── test_adapters.py          # Validate all adapters return same schema
```

---

## ⚡ Quick-Start Checklist

- [ ] Clone public-apis to local workspace
- [ ] Identify project-relevant semantic categories
- [ ] Run extraction script → `extracted-<project>-apis.json`
- [ ] Tier APIs: Free → Keyed → Strategic
- [ ] Map to project architecture layers
- [ ] Build adapter skeletons for Tier 1 APIs (no-auth)
- [ ] Document key provisioning plan for Tier 2 (DMOB)
- [ ] Create cron monitoring for quota usage

---

## 🔐 Security + Cost Guardrails

**Security:**
- All keyed API credentials → `00-HQ/Integrations/<project>-keys/`
- Never commit `.env` or key files
- Screenshot/HTML rendering APIs → whitelist domains only (avoid SSRF)
- Rate-limit all outbound calls per-provider

**Cost:**
- Start with NO-AUTH APIs exclusively until prototype stable
- Cache aggressively: geocode 24h, streetview 30d, weather 1h, flights 5min
- Set up cron alert at 80% quota usage
- Multi-provider fallback prevents single-point over-limit

---

## 📊 Deliverables

Every public-API integration project should produce:

1. **`<project>-api-inventory.json`** — structured data extracted from directory
2. **`<project>-api-map.md`** — strategic prioritization + adapter plan
3. **`API-Adapters/`** — adapter skeleton for Tier 1 APIs
4. **Integration tests** — validate all adapters conform to project schema
5. **Monitoring dashboard** — track API health + quota usage

---

## 💡 Pro Tips

1. **Public-apis updates weekly** — re-run extraction monthly to catch new additions
2. **Check "Enterprise" column** in API lists — indicates commercial terms (avoid for free tier)
3. **GitHub stars ≠ quality** — sort by auth method + free tier instead
4. **CORS = "Unknown"** often means no CORS headers — may need proxy layer for browser use
5. **"No" auth** doesn't mean no rate limits — read the linked docs for usage policies

---

## 🔗 Reference Links

| Resource | Purpose |
|----------|---------|
| https://github.com/public-apis/public-apis | Master directory (clone this first) |
| https://github.com/public-apis/public-apis#readme | Readme with table of contents |
| Your project's `extracted-apis.json` | Canonical source of truth for your integrations |

---

## 🧩 Related Skills

- `strategies` — Portfolio strategy and risk management (overlap: prioritization matrix)
- `hermes-agent` — Hermes CLI and gateway (use to run extraction scripts via `hermes chat -q`)
- `cron-job-design` — Schedule quota monitoring for API keys

---

*This skill turns a 4-hour manual review into a 20-minute automated pipeline.* 🚀
