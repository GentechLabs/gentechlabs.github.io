#!/usr/bin/env python3
"""
Currency Exchange Adapter — live rate conversion.

Provides:
- ExchangeRateHostAdapter — free, unlimited, ECB-backed
"""

from .adapter-base import CachedAdapter
import requests


class ExchangeRateHostAdapter(CachedAdapter):
    """
    exchangerate.host — free unlimited currency conversion.

    - Auth: None
    - Source: European Central Bank
    - Coverage: 150+ currencies
    - API: https://exchangerate.host/#/#docs
    """

    BASE_URL = "https://api.exchangerate.host"

    def convert(self, amount: float, from_curr: str, to_curr: str) -> dict:
        """Convert amount between currencies."""
        return self.cached(
            prefix='currency',
            ttl_name='currency',
            fetch_fn=self._fetch,
            amount=amount,
            from_curr=from_curr.upper(),
            to_curr=to_curr.upper()
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
        """Get full rates table for base currency."""
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
        return True  # No auth required
