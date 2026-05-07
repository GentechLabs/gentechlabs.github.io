#!/usr/bin/env python3
"""
Geocoding Adapters — address → lat/lng

Provides:
- NominatimAdapter (OSM) — primary, free, 1 req/sec limit
- GeocodeXYZAdapter — fallback, free, simpler coverage
"""

from .adapter-base import CachedAdapter
import requests


class NominatimAdapter(CachedAdapter):
    """
    OpenStreetMap Nominatim geocoder.

    - Auth: None (free)
    - Rate limit: 1 request/second per IP
    - Policy: https://operations.osmfoundation.org/policies/nominatim/
    - Coverage: Global (best in mapped areas)
    """

    BASE_URL = "https://nominatim.openstreetmap.org"

    def geocode(self, address: str) -> dict:
        """Convert address string → lat/lng + formatted address."""
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
        resp = self.session.get(
            f"{self.BASE_URL}/search",
            params=params,
            timeout=10
        )
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
            'raw': result  # keep original for debugging; strip in production
        }

    def validate(self) -> bool:
        """Nominatim requires no key — always valid."""
        return True


class GeocodeXYZAdapter(CachedAdapter):
    """
    Geocode.xyz — free text geocoding fallback.

    - Auth: None
    - Rate limit: 1 req/sec
    - Coverage: Global (complementary to Nominatim)
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
        resp = self.session.get(self.BASE_URL, params=params, timeout=10)
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
