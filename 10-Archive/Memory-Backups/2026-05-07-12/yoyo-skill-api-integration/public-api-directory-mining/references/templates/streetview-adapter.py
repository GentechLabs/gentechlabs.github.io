#!/usr/bin/env python3
"""
Street View Adapter — hierarchical fallback cascade.

Maps imagery sources by cost/coverage:
1. Mapillary (primary) — crowdsourced 360° photos, freemium keyed
2. OpenStreetCam (secondary) — open-source, no auth
3. Screenshotlayer (fallback) — paid screenshots, $0.002/req

Usage:
    adapter = get_adapter('streetview', 'primary')()
    result = adapter.get_sequence(lat, lng, radius_m=100)

Result schema:
{
  'images': [urls...],
  'coverage_score': 0.0-1.0,
  'count': N,
  'provider': 'mapillary' | 'openstreetcam' | 'screenshotlayer',
  'error': str (only if failed)
}
"""

from .adapter-base import CachedAdapter
import requests
import os


class MapillaryAdapter(CachedAdapter):
    """
    Mapillary — crowdsourced street-level imagery (360° panoramas).

    - Auth: API key (env: MAPILLARY_ACCESS_TOKEN)
    - Free tier: 10,000 images/month
    - Coverage: Global but sparse outside major urban centers
    - Quality: User-uploaded (variable resolution, lighting)
    - Rate limit: 12,500/day free tier
    API: https://www.mapillary.com/developer
    """

    BASE_URL = "https://graph.mapillary.com"
    API_KEY = None

    def __init__(self):
        super().__init__()
        self.API_KEY = os.getenv('MAPILLARY_ACCESS_TOKEN')
        self.session.headers.update({'Authorization': f"OAuth {self.API_KEY}"})

    def get_sequence(self, lat: float, lng: float, radius_m: int = 100) -> dict:
        """
        Retrieve image sequence near coordinates.

        Args:
            lat, lng: Center point
            radius_m: Search radius in meters

        Returns:
            {
                'images': [image URLs],
                'coverage_score': 0.0-1.0,
                'count': N,
                'provider': 'mapillary'
            }
        """
        return self.cached(
            prefix='streetview',
            ttl_name='streetview',
            fetch_fn=self._fetch,
            lat=lat, lng=lng, r=radius_m
        )

    def _fetch(self, lat: float, lng: float, r: int) -> dict:
        params = {
            'fields': 'id,thumb_2048_url,geometry',
            'geometry': f'point({lng} {lat})',
            'radius': r,
            'limit': 20,
            'access_token': self.API_KEY
        }
        resp = self.session.get(f"{self.BASE_URL}/images", params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        images = [img['thumb_2048_url'] for img in data.get('data', []) if img.get('thumb_2048_url')]
        coverage = min(1.0, len(images) / 10.0)  # heuristic: 10 images = full coverage

        return {
            'images': images,
            'coverage_score': coverage,
            'count': len(images),
            'provider': 'mapillary'
        }

    def validate(self) -> bool:
        return bool(self.API_KEY)


class OpenStreetCamAdapter(CachedAdapter):
    """
    OpenStreetCam — open-source 360° street imagery, no auth.

    - Auth: None
    - Coverage: Growing, particularly strong in Europe + US cities
    - Quality: Variable (depends on uploader equipment)
    - Rate limit: Unknown, be respectful
    API: https://openstreetcam.org/api
    """

    BASE_URL = "https://openstreetcam.org"

    def get_sequence(self, lat: float, lng: float, radius_m: int = 100) -> dict:
        return self.cached(
            prefix='streetview',
            ttl_name='streetview',
            fetch_fn=self._fetch,
            lat=lat, lng=lng, r=radius_m
        )

    def _fetch(self, lat: float, lng: float, r: int) -> dict:
        params = {
            'lat': lat,
            'lon': lng,
            'radius': r,
            'format': 'json'
        }
        resp = self.session.get(f"{self.BASE_URL}/api/getSequences", params=params, timeout=10)

        if resp.status_code == 404:
            return {'images': [], 'coverage_score': 0.0, 'provider': 'openstreetcam'}

        resp.raise_for_status()
        data = resp.json()

        sequences = data.get('seq', [])
        images = []
        for seq in sequences[:10]:
            images.extend(seq.get('images', []))

        coverage = min(1.0, len(images) / 10.0)

        return {
            'images': images[:20],
            'coverage_score': coverage,
            'count': len(images),
            'provider': 'openstreetcam'
        }

    def validate(self) -> bool:
        return True  # no auth needed


class ScreenshotlayerAdapter(CachedAdapter):
    """
    Screenshotlayer — webpage screenshot API (paid fallback).

    - Auth: API key (env: SCREENSHOTLAYER_API_KEY)
    - Cost: ~$0.002 per screenshot (volume discounts)
    - Use: Only when no crowd-sourced imagery available
    - Coverage: Universal — captures any URL
    API: https://screenshotlayer.com/api
    """

    BASE_URL = "https://api.screenshotlayer.com/api/capture"
    API_KEY = None

    def __init__(self):
        super().__init__()
        self.API_KEY = os.getenv('SCREENSHOTLAYER_API_KEY')

    def capture(self, url: str, viewport: str = "1920x1080") -> dict:
        """
        Capture screenshot of arbitrary URL.

        WARNING: Paid API — use only as fallback.
        """
        return self.cached(
            prefix='screenshot',
            ttl_name='streetview',  # screenshots static cached long-term
            fetch_fn=self._fetch,
            url=url, viewport=viewport
        )

    def _fetch(self, url: str, viewport: str) -> dict:
        params = {
            'access_key': self.API_KEY,
            'url': url,
            'viewport': viewport,
            'format': 'JSON'
        }
        resp = self.session.get(self.BASE_URL, params=params, timeout=15)
        resp.raise_for_status()
        return {
            'url': resp.json().get('url'),
            'provider': 'screenshotlayer',
            'screenshot': True
        }

    def validate(self) -> bool:
        return bool(self.API_KEY)
