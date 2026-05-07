#!/usr/bin/env python3
"""
Weather Adapters — forecasts for travel context.

Provides:
- SevenTimerAdapter — no-auth global meteorology (unlimited)
- OpenWeatherMapAdapter — keyed, more accurate (60/day free)
"""

from .adapter-base import CachedAdapter
import requests
import os


class SevenTimerAdapter(CachedAdapter):
    """
    7Timer! — free meteorology API.

    - Auth: None
    - Coverage: Global
    - Free tier: Unlimited
    - Best for: Daily trip outlooks (not hyperlocal hour-by-hour)
    - API: http://www.7timer.info/doc.php
    """

    BASE_URL = "https://www.7timer.info/api"

    def forecast(self, lat: float, lng: float, days: int = 5) -> dict:
        """Get daily weather forecast for (lat, lng)."""
        return self.cached(
            prefix='weather',
            ttl_name='weather',
            fetch_fn=self._fetch,
            lat=lat, lng=lng, days=days
        )

    def _fetch(self, lat: float, lng: float, days: int) -> dict:
        params = {
            'lon': lng,
            'lat': lat,
            'product': 'civil',
            'output': 'json'
        }
        resp = self.session.get(f"{self.BASE_URL}/api.aspx", params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Limit to requested days
        forecast = data.get('dataseries', [])[:days]
        return {
            'provider': '7timer',
            'location': {'lat': lat, 'lng': lng},
            'forecast': [
                {
                    'date': entry['datetime'],
                    'temp_c': entry['temp2m']['max'],
                    'conditions': entry['weather']
                }
                for entry in forecast
            ]
        }

    def validate(self) -> bool:
        return True


class OpenWeatherMapAdapter(CachedAdapter):
    """
    OpenWeatherMap — keyed forecasts with more granularity.

    - Auth: API key (env: OPENWEATHERMAP_API_KEY)
    - Free tier: 60 calls/day
    - Coverage: Global
    - Better for: Hourly forecasts, alerts, historical
    """

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
        return {
            'provider': 'openweathermap',
            'location': {
                'lat': raw['city']['coord']['lat'],
                'lng': raw['city']['coord']['lon']
            },
            'daily': raw.get('list', [])[:5]
        }

    def validate(self) -> bool:
        return bool(self.API_KEY)
