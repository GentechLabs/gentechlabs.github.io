#!/usr/bin/env python3
"""
CachedAdapter — Base class for all public API adapters.

Provides:
- Unified Redis caching with tiered TTLs
- HTTP session reuse (keep-alive)
- Normalized error handling
- Cache-key generation from method name + args
"""

import os
import json
import redis
import requests
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class CachedAdapter(ABC):
    """Base class for all travel API adapters with unified caching."""

    # Default TTLs per data volatility — override in subclass if needed
    TTL = {
        'geocode': 86400,      # 24h — addresses rarely change
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
        """Generate deterministic Redis key: travel:v1:prefix:arg1::arg2::..."""
        normalized = [str(arg).lower().strip() for arg in args]
        return f"travel:v1:{prefix}:{'::'.join(normalized)}"

    def cached(self, prefix: str, ttl_name: str, fetch_fn, *args) -> Dict[str, Any]:
        """
        Get from Redis or call fetch_fn and cache result.

        Example:
            return self.cached(
                prefix='geocode',
                ttl_name='geocode',
                fetch_fn=self._fetch,
                address=address
            )
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
        """Return True if adapter is configured (API key present if required)."""
        pass
