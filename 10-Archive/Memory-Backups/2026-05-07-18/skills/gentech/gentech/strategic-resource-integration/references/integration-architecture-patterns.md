# Integration Architecture Patterns — Reference

**Source:** Travel-Agent API Integration session (May 3, 2026)  
**Skill:** `strategic-resource-integration`  
**Purpose:** Condensed patterns for integrating external APIs into GenTech agents

---

## 6-Layer Integration Stack (Travel Use Case)

When building a travel intelligence agent, stack the integrations in this order:

```
Layer 1: SEARCH — Flight/hotel search APIs
  APIs: Skyscanner RPM, Amadeus, Booking.com
  Purpose: Discover available options
  Free tier: Skyscanner 100K/mo, Amadeus 2K/mo

Layer 2: LOCATION — Geocoding + reverse geocoding
  APIs: Google Maps Geocoding, OpenStreetMap Nominatim
  Purpose: Address ↔ coordinates
  Free tier: OSM completely free, Google $200 credit/mo

Layer 3: STREET VIEW — Immersive location imagery
  APIs: Google Street View Image API, Mapillary
  Purpose: Visual verification of location
  Free tier: Google $200 credit covers ~40K images/mo

Layer 4: CONTEXT — Environmental enrichment
  APIs: OpenWeatherMap, ExchangeRate-API, TripAdvisor, Eventbrite
  Purpose: Weather, currency, reviews, local events
  Free tier: Weather 60/day, Currency 1K/mo

Layer 5: TRANSPORT — Mobility options
  APIs: TransitLand, Uber/Lyft (partner), Rome2Rio
  Purpose: Get from A to B
  Free tier: TransitLand open data, others require partnership

Layer 6: SUPPORT — Fulfillment layer
  APIs: Twilio SendGrid, Stripe, PDF.co
  Purpose: Email confirmations, payments, itinerary generation
  Free tier: SendGrid 100/day, Stripe payment processing
```

**Rationale:** Lower layers (1–3) are core to the user's mental model (search → locate → preview). Layers 4–6 enrich the experience but aren't blockers for MVP.

---

## Adapter Pattern with Provider Fallback

**Problem:** You need to call multiple providers for same capability (e.g., geocoding via Google + OSM). You want:
- Single interface for agent code
- Automatic fallback on rate-limit/failure
- Centralized caching
- Provider-agnostic logging

**Solution:** Adapter pattern with primary/secondary provider support.

**Skeleton:**
```python
class ProviderAdapter:
    def __init__(self, primary: str, secondary: str = None, cache_ttl: int = 3600):
        self.primary = self._init_client(primary)
        self.secondary = self._init_client(secondary) if secondary else None
        self.cache = RedisCache()

    async def execute(self, method: str, params: dict):
        # 1. Check cache
        cache_key = self._cache_key(method, params)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # 2. Try primary
        try:
            result = await getattr(self.primary, method)(**params)
            await self.cache.setex(cache_key, self.cache_ttl, result)
            return result
        except (RateLimitError, ServerError) as e:
            if self.secondary:
                result = await getattr(self.secondary, method)(**params)
                await self.cache.setex(cache_key, self.cache_ttl, result)
                return result
            raise

    def _cache_key(self, method, params):
        normalized = json.dumps(params, sort_keys=True)
        return f"api:{self.primary.provider}:{method}:{hash(normalized)}"
```

**Key decisions:**
- Cache TTL varies by data volatility: geocoding = 24h, street view = 1h, flights = 15min
- Circuit breaker after 5 consecutive failures → stop calling that provider for 5min
- Exponential backoff: 1s → 2s → 4s → 8s → 16s max
- Log structured JSON: `{timestamp, provider, method, latency_ms, status, error_type}`

---

## Rate Limit Handling

**Detection:**
- HTTP 429 → Too Many Requests
- HTTP 403 with `"quota exceeded"` message
- Response headers: `X-RateLimit-Remaining`, `Retry-After`

**Strategy:**
1. Read `Retry-After` header if present → sleep exactly that many seconds
2. If no header, exponential backoff starting at 1 second
3. Track per-provider failure count → circuit break after 5 failures in 60s
4. Cache negative responses (failed lookups) for 60s to avoid hammering

**Implementation:**
```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=16),
    stop=stop_after_attempt(5),
    retry=(RateLimitError | ServerError)
)
async def call_with_retry(adapter, method, params):
    return await adapter.execute(method, params)
```

---

## Schema Normalization

Never leak provider-specific fields into agent logic.

**Example: Flight results**
```python
# Skyscanner raw:
{
  "Itineraries": [{"OutboundLeg": {"OriginCode": "NYC", ...}}],
  "Legs": [{...}]
}

# Normalized GenTech schema:
{
  "flights": [
    {
      "origin": "NYC",
      "destination": "LAX",
      "departure": "2026-05-20T14:30:00Z",
      "arrival": "2026-05-20T17:45:00Z",
      "carrier": "UA",
      "flight_number": "UA 207",
      "price": 287.50,
      "currency": "USD"
    }
  ],
  "meta": {
    "provider": "skyscanner",
    "query_id": "req_abc123",
    "cached": false
  }
}
```

**Rationale:** Agent logic sees consistent schema regardless of provider swaps, A/B tests, or fallbacks.

---

## Caching Strategy

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Geocoding (address → coords) | 24h | Addresses rarely change coordinates |
| Reverse geocoding (coords → address) | 24h | Inverse of above |
| Street View metadata | 1h | Imagery updates occasionally |
| Flight search results | 15min | Flights change prices/availability quickly |
| Currency rates | 10min | FX moves fast |
| Weather current | 30min | Updates hourly typically |
| Weather forecast | 1h | Forecasts update ~hourly |

**Cache key composition:** `api:<provider>:<method>:<sorted_json_params_hash>`

**Storage:** Redis with TTL. L1 = in-memory dict (LRU, 1000 entries), L2 = Redis.

---

## Monitoring & Metrics

Instrument every adapter:

```json
{
  "timestamp": "2026-05-03T14:32:10Z",
  "provider": "google_maps",
  "method": "geocode",
  "latency_ms": 142,
  "status": "success",
  "cache_hit": false,
  "fallback_used": false
}
```

**Aggregate metrics (Prometheus-style):**
- `api_requests_total{provider, method, status}`
- `api_latency_seconds_bucket{provider, method, le}`
- `api_cache_hit_ratio{provider}`
- `api_fallback_activations_total{primary, secondary}`

**Alerts:**
- Error rate > 5% over 5min → page
- Latency P95 > 2s → warn
- Cache hit ratio < 30% → investigate (maybe TTL too short)

---

## Provider Selection Heuristics

**When to use Google Maps vs OSM:**
- Google: Higher accuracy, better coverage, but rate-limited and billed
- OSM: 100% free, community-maintained, slightly less accurate in some regions
- Default: Google primary, OSM fallback. Switch to OSM-only if Google spend exceeds $150/mo.

**When to use Street View vs Mapillary:**
- Street View: Google's imagery, higher quality, global coverage
- Mapillary: Crowdsourced, sometimes more up-to-date in dense urban areas
- Fallback chain: Google → Mapillary → "No imagery available" message

---

**Attach this reference to any API integration project. Patterns are reusable across domains (not just travel).**
