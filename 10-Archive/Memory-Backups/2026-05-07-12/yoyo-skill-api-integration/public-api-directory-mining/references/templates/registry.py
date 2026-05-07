#!/usr/bin/env python3
"""
Adapter Registry — fallback orchestration + provider lookup.

Maps abstract categories ('geocode', 'weather', 'streetview') to concrete
adapter classes, organized by tier (primary/fallback/secondary).

Usage:
    from API-Adapters.registry import get_adapter, try_with_fallback

    # Single adapter
    geocoder = get_adapter('geocode')()
    coords = geocoder.geocode("Paris")

    # Automatic fallback chain
    result = try_with_fallback('geocode', 'geocode', "Paris")
    # Tries primary → if error → fallback → if error → secondary → returns first success
"""

from .geocoding import NominatimAdapter, GeocodeXYZAdapter
from .weather import SevenTimerAdapter, OpenWeatherMapAdapter
from .streetview import MapillaryAdapter, OpenStreetCamAdapter, ScreenshotlayerAdapter
from .currency import ExchangeRateHostAdapter

# Registry maps category → provider tiers in fallback order
ADAPTER_REGISTRY = {
    'geocode': {
        'primary': NominatimAdapter,       # free, reliable, global
        'fallback': GeocodeXYZAdapter,     # free, complementary coverage
    },
    'weather': {
        'primary': SevenTimerAdapter,      # free, unlimited, global
        'fallback': OpenWeatherMapAdapter, # keyed, more accurate/hourly
    },
    'streetview': {
        'primary': MapillaryAdapter,       # freemium, best quality (crowd photos)
        'secondary': OpenStreetCamAdapter, # free, open-source coverage
        'fallback': ScreenshotlayerAdapter # paid, universal (use sparingly)
    },
    'currency': {
        'primary': ExchangeRateHostAdapter,  # free, unlimited, ECB-backed
    }
}


def get_adapter(category: str, tier: str = 'primary'):
    """
    Retrieve adapter class by category and tier.

    Args:
        category: One of 'geocode', 'weather', 'streetview', 'currency'
        tier: One of 'primary', 'fallback', 'secondary' (defines fallback order)

    Returns:
        Adapter class (not instance)

    Raises:
        ValueError: If category/tier not found
    """
    adapter_class = ADAPTER_REGISTRY.get(category, {}).get(tier)
    if not adapter_class:
        raise ValueError(f"No adapter for category='{category}', tier='{tier}'")
    return adapter_class()


def try_with_fallback(category: str, method: str, *args, **kwargs):
    """
    Try each adapter tier in order until one succeeds (no 'error' key).

    Example:
        coords = try_with_fallback('geocode', 'geocode', "Tokyo")
        # Tries Nominatim → if error, GeocodeXYZ → returns first result without 'error'

    Returns:
        dict — First successful result or final error dict
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
                continue  # Skip invalid (missing API key, etc.)
            result = getattr(adapter, method)(*args, **kwargs)
            if 'error' not in result:
                return result
            last_error = result.get('error')
        except Exception as e:
            last_error = str(e)

    return {
        'error': last_error or 'all_adapters_failed',
        'category': category,
        'method': method
    }


def list_adapters() -> dict:
    """Return human-readable catalog of all registered adapters."""
    return {
        cat: {
            tier: cls.__name__
            for tier, cls in tiers.items()
        }
        for cat, tiers in ADAPTER_REGISTRY.items()
    }
