"""GenTech Shop — CheapShark deal tracker (standalone module)."""
import json, time, re, sys
from dataclasses import dataclass, fields
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError

CHEAPSHARK_BASE = "https://www.cheapshark.com/api/1.0"
REQUEST_DELAY = 1.0  # seconds between calls

@dataclass
class DealResult:
    title: str
    sale_price: float
    normal_price: float
    savings: float
    store_name: str
    steam_appid: Optional[int] = None
    deal_id: str = ""

class CheapSharkClient:
    def __init__(self, cache_enabled=True):
        self._last_call = 0.0
        self._cache = {} if cache_enabled else None
        self._store_map = None

    def _rate_limit(self):
        elapsed = time.time() - self._last_call
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self._last_call = time.time()

    def _get(self, url: str) -> dict:
        self._rate_limit()
        if self._cache and url in self._cache:
            return self._cache[url]
        req = Request(url, headers={"User-Agent": "GenTech-Shop/1.0"})
        try:
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
        except HTTPError as e:
            if e.code == 429:
                time.sleep(5)
                return self._get(url)
            raise
        if self._cache is not None:
            self._cache[url] = data
        return data

    def search_deals(self, title: str, upper_price: float = 9999) -> list[DealResult]:
        """Search CheapShark deals by title. Returns sorted by savings desc."""
        url = f"{CHEAPSHARK_BASE}/deals?title={title.replace(' ', '%20')}&upperPrice={upper_price}"
        raw = self._get(url)
        if not raw or not isinstance(raw, list):
            return []

        results = []
        for d in raw:
            try:
                savings = float(d.get("savings", 0))
                sale_price = float(d.get("salePrice", 0))
                normal_price = float(d.get("normalPrice", 0))
                store_id = d.get("storeID", "0")
                store_name = self._resolve_store_name(store_id) if hasattr(self, '_store_map') else store_id
                deal_title = d.get("title", title)
                steam_appid = d.get("steamAppID")
                if steam_appid:
                    steam_appid = int(steam_appid)

                # Title similarity filter: >50% of search words must appear
                search_words = set(title.lower().split())
                deal_words = set(deal_title.lower().split())
                if search_words and len(search_words & deal_words) / len(search_words) < 0.5:
                    continue

                results.append(DealResult(
                    title=deal_title,
                    sale_price=sale_price,
                    normal_price=normal_price,
                    savings=savings,
                    store_name=store_name,
                    steam_appid=steam_appid,
                    deal_id=d.get("dealID", ""),
                ))
            except (ValueError, KeyError, TypeError):
                continue

        results.sort(key=lambda x: x.savings, reverse=True)
        return results

    def get_stores(self) -> dict:
        """Returns {storeID: storeName} mapping."""
        url = f"{CHEAPSHARK_BASE}/stores"
        raw = self._get(url)
        return {str(s["storeID"]): s["storeName"] for s in raw} if isinstance(raw, list) else {}

    def _resolve_store_name(self, store_id) -> str:
        """Resolve store ID to name, caching the store list."""
        if self._store_map is None:
            self._store_map = self.get_stores()
        return self._store_map.get(str(store_id), f"Store {store_id}")
