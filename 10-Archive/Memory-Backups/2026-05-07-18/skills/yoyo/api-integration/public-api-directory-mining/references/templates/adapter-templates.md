# Adapter Templates — Public API Integration

> Boilerplate adapter classes following the `CachedAdapter` pattern.
> Copy these into `03-Projects/<Project>/API-Adapters/` and customize per provider.

---

## 📁 `templates/adapter-base.py`

**Purpose:** Base class providing Redis caching, HTTP session management, error handling, and unified response format for all API adapters.

```python
import os
import json
import redis
import requests
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class CachedAdapter(ABC):
    """
    Base adapter class — all public API adapters inherit from this.

    Features:
    - Redis caching with tiered TTLs (different per data type)
    - Unified error handling (returns {{"error": "...", "provider": "..."}} )
    - HTTP session reuse (keep-alive)
    - Cache-key normalization across providers
    """

    # Default TTLs per data volatility — override per-adapter if needed
    TTL = {
        'geocode': 86400,      # 24h — addresses static
        'weather': 3600,       # 1h — forecasts update hourly
        'flights': 300,        # 5min — prices change fast
        'streetview': 2592000, # 30d — imagery static for months
        'currency': 900,       # 15min — rates drift
        'airport': 86400,      # 24h — airport metadata static
        'transit': 600,        # 10min — schedules change
    }

    def __init__(self):
        self.redis = redis.from_url(
            os.getenv('REDIS_URL', 'redis://localhost:6379')
        )
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GenTech-Travel-Agent/1.0 (hermes-agent)'
        })

    def _cache_key(self, prefix: str, *args) -> str:
        """Generate deterministic Redis key for method + arguments."""
        normalized = [str(arg).lower().strip() for arg in args]
        return f"travel:v1:{prefix}:{'::'.join(normalized)}"

    def cached(self, prefix: str, ttl_name: str, fetch_fn, *args) -> Dict[str, Any]:
        """
        Get from Redis cache or call fetch_fn and cache result.

        Args:
            prefix: Cache key category (e.g., 'geocode', 'weather')
            ttl_name: TTL preset from self.TTL dict
            fetch_fn: Zero-arg lambda that fetches from API
            *args: Arguments passed to fetch_fn (also used in cache key)

        Returns:
            dict: Cached or fresh API result
        """
        key = self._cache_key(prefix, *args)
        ttl = self.TTL.get(ttl_name, 3600)

        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)

        try:
            result = fetch_fn(*args)
            self.redis.setex(key, ttl, json.dumps(result))
            return result
        except Exception as e:
            return {
                'error': str(e),
                'provider': self.__class__.__name__
            }

    @abstractmethod
    def validate(self) -> bool:
        """Check if adapter is properly configured (API key present if needed)."""
        pass
```

---

## 📁 `templates/geocoding-adapter.py`

**Example:** Two-provider fallback chain (Nominatim free → Geocode.xyz freemium)

```python
from .adapter-base import CachedAdapter
import requests


class NominatimAdapter(CachedAdapter):
    """
    OpenStreetMap Nominatim geocoder.
    - No auth required
    - Rate limit: 1 req/sec per IP
    - Policy: https://operations.osmfoundation.org/policies/nominatim/
    """

    BASE_URL = "https://nominatim.openstreetmap.org"

    def geocode(self, address: str) -> dict:
        return self.cached(
            prefix='geocode',
            ttl_name='geocode',
            fetch_fn=self._fetch,
            address=address
        )

    def _fetch(self, address: str) -> dict:
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'addressdetails': 1
        }
        resp = self.session.get(f"{self.BASE_URL}/search", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return {'error': 'not_found', 'provider': 'nominatim'}

        result = data[0]
        return {
            'lat': float(result['lat']),
            'lng': float(result['lon']),
            'formatted_address': result['display_name'],
            'bounding_box': result.get('boundingbox'),
            'provider': 'nominatim',
            'raw': result
        }

    def validate(self) -> bool:
        """Nominatim requires no key — always valid."""
        return True


class GeocodeXYZAdapter(CachedAdapter):
    """
    Geocode.xyz — free text geocoding.
    - No auth required
    - 1 req/sec limit
    - Good fallback for Nominatim rate-limit scenarios
    """

    BASE_URL = "https://geocode.xyz"

    def geocode(self, address: str) -> dict:
        return self.cached(
            prefix='geocode',
            ttl_name='geocode',
            fetch_fn=self._fetch,
            address=address
        )

    def _fetch(self, address: str) -> dict:
        params = {
            'q': address,
            'json': 1,
            'limit': 1
        }
        resp = self.session.get(f"{self.BASE_URL}/", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get('error'):
            return {'error': data['error'], 'provider': 'geocode.xyz'}

        return {
            'lat': float(data['latt']),
            'lng': float(data['longt']),
            'formatted_address': data.get('formatted_address', ''),
            'provider': 'geocode.xyz',
            'raw': data
        }

    def validate(self) -> bool:
        return True
```

---

## 📁 `templates/flights-adapter.py`

**Example:** Amadeus (keyed, OAuth) stub — shows auth pattern

```python
from .adapter-base import CachedAdapter
import requests
import os


class AmadeusAdapter(CachedAdapter):
    """
    Amadeus for Developers — comprehensive flight/hotel search.
    - Auth: OAuth 2.0 (client_id + client_secret)
    - Free tier: 2,000 calls/month
    - Requires: AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET in .env
    """

    BASE_URL = "https://test.api.amadeus.com"
    AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"

    def __init__(self):
        super().__init__()
        self.client_id = os.getenv('AMADEUS_CLIENT_ID')
        self.client_secret = os.getenv('AMADEUS_CLIENT_SECRET')
        self.access_token = None
        self.token_expires_at = 0

    def _ensure_token(self):
        """Refresh OAuth token if expired."""
        import time
        if not self.access_token or time.time() >= self.token_expires_at - 60:
            resp = self.session.post(
                self.AUTH_URL,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                },
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            self.access_token = data['access_token']
            self.token_expires_at = time.time() + data['expires_in']
            self.session.headers.update({'Authorization': f"Bearer {self.access_token}"})

    def search_flights(self, origin: str, dest: str, date: str) -> dict:
        def _fetch():
            self._ensure_token()
            params = {
                'originLocationCode': origin.upper(),
                'destinationLocationCode': dest.upper(),
                'departureDate': date,
                'adults': 1,
                'max': 5
            }
            resp = self.session.get(
                f"{self.BASE_URL}/v2/shopping/flight-offers",
                params=params,
                timeout=15
            )
            resp.raise_for_status()
            return self._normalize_flights(resp.json())

        return self.cached(
            prefix='flights',
            ttl_name='flights',
            fetch_fn=_fetch,
            origin=origin, dest=dest, date=date
        )

    def _normalize_flights(self, raw: dict) -> dict:
        """Convert Amadeus schema to GenTech schema."""
        # Simplified — expand as needed
        offers = raw.get('data', [])
        return {
            'count': len(offers),
            'flights': [
                {
                    'price': float(offer['price']['total']),
                    'currency': offer['price']['currency'],
                    'segments': [
                        {
                            'departure': seg['departure']['iataCode'],
                            'arrival': seg['arrival']['iataCode'],
                            'time': seg['departure']['at']
                        }
                        for seg in offer['itineraries'][0]['segments']
                    ]
                }
                for offer in offers
            ],
            'provider': 'amadeus'
        }

    def validate(self) -> bool:
        return bool(self.client_id and self.client_secret)
```

---

## 📁 `templates/weather-adapter.py`

**Example:** 7Timer! (no auth) + OpenWeatherMap (keyed fallback)

```python
from .adapter-base import CachedAdapter
import requests


class SevenTimerAdapter(CachedAdapter):
    """
    7Timer! — No-auth meteorology API.
    - Unlimited free calls
    - Coverage: Global
    - Best for: daily outlooks (not hyperlocal)
    """

    BASE_URL = "https://www.7timer.info/api"

    def forecast(self, lat: float, lng: float, days: int = 5) -> dict:
        return self.cached(
            prefix='weather',
            ttl_name='weather',
            fetch_fn=self._fetch,
            lat=lat, lng=lng, days=days
        )

    def _fetch(self, lat: float, lng: float, days: int) -> dict:
        # 7Timer uses different coordinate system — convert
        params = {
            'lon': lng,
            'lat': lat,
            'product': 'civil',
            'output': 'json'
        }
        resp = self.session.get(f"{self.BASE_URL}/api.aspx", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Normalize to common schema
        return {
            'provider': '7timer',
            'location': {'lat': lat, 'lng': lng},
            'forecast': [
                {
                    'date': entry['datetime'],
                    'temp_c': entry['temp2m']['max'],
                    'conditions': entry['weather']
                }
                for entry in data.get('dataseries', [])[:days]
            ]
        }

    def validate(self) -> bool:
        return True


class OpenWeatherMapAdapter(CachedAdapter):
    """OpenWeatherMap — keyed, more accurate local forecasts."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    API_KEY = None

    def __init__(self):
        super().__init__()
        self.API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

    def forecast(self, lat: float, lng: float, days: int = 5) -> dict:
        def _fetch():
            params = {
                'lat': lat,
                'lon': lng,
                'appid': self.API_KEY,
                'units': 'metric',
                'cnt': days * 8  # 3-hourly forecasts
            }
            resp = self.session.get(f"{self.BASE_URL}/forecast", params=params, timeout=10)
            resp.raise_for_status()
            return self._normalize(resp.json())

        return self.cached(
            prefix='weather',
            ttl_name='weather',
            fetch_fn=_fetch,
            lat=lat, lng=lng, days=days
        )

    def _normalize(self, raw: dict) -> dict:
        # Simplified — map OWM's list to daily aggregates
        return {'provider': 'openweathermap', 'raw': raw}

    def validate(self) -> bool:
        return bool(self.API_KEY)
```

---

## 📁 `templates/streetview-adapter.py`

**Example:** Mapillary → OpenStreetCam → Screenshotlayer fallback cascade

```python
from .adapter-base import CachedAdapter
import requests
import os


class MapillaryAdapter(CachedAdapter):
    """
    Mapillary — crowdsourced street-level imagery (360° panoramas).
    - Auth: API key (free tier up to 10,000 images/month)
    - Coverage: Global but sparse outside major cities
    - Quality: Variable (user-uploaded)
    """

    BASE_URL = "https://graph.mapillary.com"
    API_KEY = None

    def __init__(self):
        super().__init__()
        self.API_KEY = os.getenv('MAPILLARY_ACCESS_TOKEN')
        self.session.headers.update({'Authorization': f"OAuth {self.API_KEY}"})

    def get_sequence(self, lat: float, lng: float, radius_m: int = 100) -> dict:
        """
        Get image sequence near coordinates.

        Args:
            lat, lng: Center point
            radius_m: Search radius in meters

        Returns:
            { 'images': [image_urls], 'coverage_score': 0.0-1.0, 'provider': 'mapillary' }
        """
        def _fetch():
            params = {
                'fields': 'id,thumb_2048_url,geometry',
                'geometry': f'point({lng} {lat})',
                'radius': radius_m,
                'limit': 20,
                'access_token': self.API_KEY
            }
            resp = self.session.get(
                f"{self.BASE_URL}/images",
                params=params,
                timeout=15
            )
            resp.raise_for_status()
            return self._normalize(resp.json())

        return self.cached(
            prefix='streetview',
            ttl_name='streetview',
            fetch_fn=_fetch,
            lat=lat, lng=lng, r=radius_m
        )

    def _normalize(self, raw: dict) -> dict:
        data = raw.get('data', [])
        coverage = min(1.0, len(data) / 10.0)  # crude heuristic: 10 images = full coverage
        return {
            'images': [img['thumb_2048_url'] for img in data if img.get('thumb_2048_url')],
            'coverage_score': coverage,
            'count': len(data),
            'provider': 'mapillary'
        }

    def validate(self) -> bool:
        return bool(self.API_KEY)


class OpenStreetCamAdapter(CachedAdapter):
    """OpenStreetCam — open-source 360° imagery, no auth."""

    BASE_URL = "https://openstreetcam.org"

    def get_sequence(self, lat: float, lng: float, radius_m: int = 100) -> dict:
        def _fetch():
            params = {
                'lat': lat,
                'lon': lng,
                'radius': radius_m,
                'format': 'json'
            }
            resp = self.session.get(f"{self.BASE_URL}/api/getSequences", params=params, timeout=10)
            if resp.status_code == 404:
                return {'images': [], 'coverage_score': 0.0, 'provider': 'openstreetcam'}
            resp.raise_for_status()
            return self._normalize(resp.json())

        return self.cached(
            prefix='streetview',
            ttl_name='streetview',
            fetch_fn=_fetch,
            lat=lat, lng=lng, r=radius_m
        )

    def _normalize(self, raw: dict) -> dict:
        sequences = raw.get('seq', [])
        images = []
        for seq in sequences[:10]:
            images.extend(seq.get('images', []))
        return {
            'images': images[:20],
            'coverage_score': min(1.0, len(images) / 10.0),
            'count': len(images),
            'provider': 'openstreetcam'
        }

    def validate(self) -> bool:
        return True  # no auth needed


class ScreenshotlayerAdapter(CachedAdapter):
    """Screenshotlayer — webpage screenshots, paid fallback ($0.002/req)."""

    BASE_URL = "https://api.screenshotlayer.com/api/capture"
    API_KEY = None

    def __init__(self):
        super().__init__()
        self.API_KEY = os.getenv('SCREENSHOTLAYER_API_KEY')

    def capture(self, url: str, viewport: str = "1920x1080") -> dict:
        """Capture screenshot of arbitrary URL (use sparingly — paid)."""
        def _fetch():
            params = {
                'access_key': self.API_KEY,
                'url': url,
                'viewport': viewport,
                'format': 'JSON'
            }
            resp = self.session.get(self.BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            return resp.json()

        return self.cached(
            prefix='screenshot',
            ttl_name='streetview',  # screenshots static too
            fetch_fn=_fetch,
            url=url
        )

    def validate(self) -> bool:
        return bool(self.API_KEY)
```

---

## 📁 `templates/currency-adapter.py`

**Example:** exchangerate.host (no auth, unlimited)

```python
from .adapter-base import CachedAdapter
import requests


class ExchangeRateHostAdapter(CachedAdapter):
    """
    exchangerate.host — free, unlimited currency conversion.
    - No auth
    - Source: ECB European Central Bank
    - Ideal for: trip budget calculations
    """

    BASE_URL = "https://api.exchangerate.host"

    def convert(self, amount: float, from_curr: str, to_curr: str) -> dict:
        return self.cached(
            prefix='currency',
            ttl_name='currency',
            fetch_fn=self._fetch,
            amount=amount, from_curr=from_curr.upper(), to_curr=to_curr.upper()
        )

    def _fetch(self, amount: float, from_curr: str, to_curr: str) -> dict:
        params = {
            'from': from_curr,
            'to': to_curr,
            'amount': amount
        }
        resp = self.session.get(f"{self.BASE_URL}/convert", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        return {
            'amount': data['result'],
            'from': from_curr,
            'to': to_curr,
            'rate': data['info']['rate'],
            'date': data['date'],
            'provider': 'exchangerate.host'
        }

    def get_rates(self, base: str = 'USD') -> dict:
        """Get full rates table for a base currency."""
        return self.cached(
            prefix='currency_table',
            ttl_name='currency',
            fetch_fn=self._fetch_rates,
            base=base.upper()
        )

    def _fetch_rates(self, base: str) -> dict:
        resp = self.session.get(f"{self.BASE_URL}/latest", params={'base': base}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            'base': data['base'],
            'date': data['date'],
            'rates': data['rates'],
            'provider': 'exchangerate.host'
        }

    def validate(self) -> bool:
        return True  # no auth needed
```

---

## 📁 `templates/registry.py`

**Adapter lookup + fallback orchestration**

```python
from .geocoding import NominatimAdapter, GeocodeXYZAdapter
from .weather import SevenTimerAdapter, OpenWeatherMapAdapter
from .streetview import MapillaryAdapter, OpenStreetCamAdapter, ScreenshotlayerAdapter
from .currency import ExchangeRateHostAdapter

# Registry maps category → provider tiers
ADAPTER_REGISTRY = {
    'geocode': {
        'primary': NominatimAdapter,       # free, reliable
        'fallback': GeocodeXYZAdapter,     # free, backup
    },
    'weather': {
        'primary': SevenTimerAdapter,      # free, global
        'fallback': OpenWeatherMapAdapter, # keyed, more accurate
    },
    'streetview': {
        'primary': MapillaryAdapter,       # freemium, best quality
        'secondary': OpenStreetCamAdapter, # free, coverage varies
        'fallback': ScreenshotlayerAdapter # paid, universal (use sparingly)
    },
    'currency': {
        'primary': ExchangeRateHostAdapter,  # free, unlimited
    }
}


def get_adapter(category: str, tier: str = 'primary'):
    """
    Retrieve adapter instance by category and tier.

    Usage:
        geocoder = get_adapter('geocode')()
        coords = geocoder.geocode("Paris")

        # Explicit fallback
        if 'error' in coords:
            coords = get_adapter('geocode', 'fallback')().geocode("Paris")
    """
    adapter_class = ADAPTER_REGISTRY.get(category, {}).get(tier)
    if not adapter_class:
        raise ValueError(f"No adapter for category='{category}', tier='{tier}'")
    return adapter_class()


def try_with_fallback(category: str, method: str, *args, **kwargs):
    """
    Try primary adapter, fall back on error, then secondary if defined.
    Returns first successful result or final error dict.
    """
    tiers = ['primary', 'fallback', 'secondary']
    last_error = None

    for tier in tiers:
        try:
            adapter_cls = ADAPTER_REGISTRY.get(category, {}).get(tier)
            if not adapter_cls:
                continue
            adapter = adapter_cls()
            if not adapter.validate():
                continue  # skip invalid (missing key, etc.)
            result = getattr(adapter, method)(*args, **kwargs)
            if 'error' not in result:
                return result
            last_error = result.get('error')
        except Exception as e:
            last_error = str(e)

    return {'error': last_error or 'all_adapters_failed', 'category': category}
```

---

## 🧪 Template Usage

**Step 1 — Copy base adapter:**
```bash
cp references/skills/public-api-directory-mining/templates/adapter-base.py \
   03-Projects/Travel-Agent/API-Adapters/base.py
```

**Step 2 — Implement category adapter:**
```bash
cp references/skills/public-api-directory-mining/templates/geocoding-adapter.py \
   03-Projects/Travel-Agent/API-Adapters/geocoding.py
```

**Step 3 — Register in `registry.py`**

**Step 4 — Validate schema consistency:**
```python
# integration-tests/test_adapters.py
from API-Adapters.geocoding import NominatimAdapter

def test_geocode_normalized_schema():
    result = NominatimAdapter().geocode("Paris")
    assert 'lat' in result and 'lng' in result
    assert 'provider' in result
```

---

## 📝 Template Customization Checklist

Per adapter, update:
- [ ] `BASE_URL` — provider endpoint
- [ ] `API_KEY` env var name in `__init__`
- [ ] Rate limits in docstring
- [ ] `validate()` — check key presence if required
- [ ] Cache TTL in `TTL` dict override (if different from defaults)
- [ ] `_fetch()` — make HTTP call, raise on error
- [ ] `_normalize()` or method — convert provider-specific schema → GenTech schema
- [ ] Add to `ADAPTER_REGISTRY` in `registry.py` with appropriate tier (primary/fallback/secondary)

---

*Templates ensure all adapters behave identically — cache, error handling, schema.* 🛠️
