"""
Deal Tracker — Game Price Comparison Engine

Compares prices across 35+ stores using CheapShark API (free, no key).
Features: game search, deal comparison, price history, wishlist monitoring.

Revenue: freemium SaaS + x402 micropayments per query.
"""

import json
import logging
import time
import urllib.request
import urllib.parse
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Optional, Union
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ── API Config ──────────────────────────────────────────────────────────
CHEAPSHARK_BASE = "https://www.cheapshark.com/api/1.0"
REQUEST_TIMEOUT = 10
CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
CACHE_TTL = 3600  # 1 hour
REQUEST_DELAY = 1.5  # seconds between requests (CheapShark rate limit ~1/sec)


# ── Data Models ─────────────────────────────────────────────────────────

@dataclass
class Store:
    store_id: int
    name: str
    is_active: bool
    icon_url: str = ""

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Store":
        return cls(
            store_id=int(data.get("storeID", 0)),
            name=data.get("storeName", "Unknown"),
            is_active=bool(data.get("isActive", False)),
            icon_url=data.get("images", {}).get("banner", ""),
        )


@dataclass
class Deal:
    deal_id: str
    title: str
    sale_price: float
    normal_price: float
    savings: float
    store_id: int
    store_name: str = ""
    metacritic_score: int = 0
    steam_rating: int = 0
    steam_app_id: Optional[int] = None
    deal_rating: float = 0.0
    thumb: str = ""

    @property
    def discount_pct(self) -> float:
        return round(self.savings, 1)

    @property
    def is_good_deal(self) -> bool:
        return self.savings >= 50 or self.deal_rating >= 8.0

    @property
    def is_great_deal(self) -> bool:
        return self.savings >= 75 or self.deal_rating >= 9.0

    @property
    def discount_tier(self) -> str:
        """Classify deal into discount depth tiers (yield rainbow style)."""
        if self.savings >= 50:
            return "deep_cut"
        elif self.savings >= 25:
            return "solid_sale"
        elif self.savings >= 10:
            return "light_mark"
        else:
            return "barely"

    @property
    def discount_tier_emoji(self) -> str:
        """Emoji for discount tier."""
        tiers = {
            "deep_cut": "🔥",
            "solid_sale": "💰",
            "light_mark": "🏷️",
            "barely": "📉"
        }
        return tiers.get(self.discount_tier, "🎮")

    @property
    def discount_tier_label(self) -> str:
        """Human-readable tier label."""
        labels = {
            "deep_cut": "DEEP CUT",
            "solid_sale": "SOLID SALE",
            "light_mark": "LIGHT MARK",
            "barely": "BARELY TOUCHING IT"
        }
        return labels.get(self.discount_tier, "UNKNOWN")

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Deal":
        return cls(
            deal_id=data.get("dealID", ""),
            title=data.get("title", "Unknown"),
            sale_price=float(data.get("salePrice", 0)),
            normal_price=float(data.get("normalPrice", 0)),
            savings=float(data.get("savings", 0)),
            store_id=int(data.get("storeID", 0)),
            metacritic_score=int(data.get("metacriticScore", 0) or 0),
            steam_rating=int(data.get("steamRatingPercent", 0) or 0),
            steam_app_id=int(data["steamAppID"]) if data.get("steamAppID") else None,
            deal_rating=float(data.get("dealRating", 0) or 0),
            thumb=data.get("thumb", ""),
        )


@dataclass
class GameInfo:
    game_id: str
    title: str
    steam_app_id: Optional[int] = None
    cheapest_price: float = 0
    cheapest_deal_id: str = ""

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "GameInfo":
        return cls(
            game_id=data.get("gameID", ""),
            title=data.get("external", "Unknown"),
            steam_app_id=int(data["steamAppID"]) if data.get("steamAppID") else None,
            cheapest_price=float(data.get("cheapestPrice", 0)),
            cheapest_deal_id=data.get("cheapestDealID", ""),
        )


@dataclass
class PriceAlert:
    game_title: str
    current_price: float
    lowest_price: float
    store: str
    url: str
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def message(self) -> str:
        return (
            f"🎮 Price Alert: {self.game_title}\n"
            f"💰 ${self.current_price:.2f} at {self.store}\n"
            f"📉 Lowest recorded: ${self.lowest_price:.2f}\n"
            f"🔗 {self.url}"
        )


# ── API Client ──────────────────────────────────────────────────────────

class CheapSharkClient:
    """Free game deals API — no key required."""

    def __init__(self, cache_enabled: bool = True) -> None:
        self.cache_enabled = cache_enabled
        self._stores: dict[int, Store] = {}
        self._cache: dict[str, tuple[float, Any]] = {}
        self._last_request_time: float = 0
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
        except OSError as e:
            logger.warning("Failed to create cache dir %s: %s", CACHE_DIR, e)

    def _get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
        """Make API request with caching and rate limiting."""
        url = f"{CHEAPSHARK_BASE}/{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)

        # Check cache
        cache_key = url
        if self.cache_enabled and cache_key in self._cache:
            ts, data = self._cache[cache_key]
            if time.time() - ts < CACHE_TTL:
                return data

        # Rate limit: wait between requests
        elapsed = time.time() - self._last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)

        req = urllib.request.Request(url, headers={"User-Agent": "GenTech-DealTracker/1.0"})
        max_retries = 3
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                    data = json.loads(resp.read())
                    self._last_request_time = time.time()
                    if self.cache_enabled:
                        self._cache[cache_key] = (time.time(), data)
                    return data
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < max_retries - 1:
                    wait = REQUEST_DELAY * (2 ** attempt)
                    logger.warning("Rate limited on %s, waiting %.1fs (attempt %d/%d)", endpoint, wait, attempt + 1, max_retries)
                    time.sleep(wait)
                    continue
                logger.error("CheapShark HTTP error on %s: %s", endpoint, e)
                raise APIError(f"CheapShark API error: HTTP {e.code}") from e
            except urllib.error.URLError as e:
                logger.error("CheapShark network error on %s: %s", endpoint, e)
                raise APIError(f"CheapShark API network error: {e.reason}") from e
            except json.JSONDecodeError as e:
                logger.error("CheapShark invalid JSON response on %s: %s", endpoint, e)
                raise APIError(f"CheapShark API returned invalid JSON: {e}") from e
            except OSError as e:
                logger.error("CheapShark I/O error on %s: %s", endpoint, e)
                raise APIError(f"CheapShark API I/O error: {e}") from e

    def get_stores(self) -> list[Store]:
        """Get all available stores."""
        if self._stores:
            return list(self._stores.values())
        data = self._get("stores")
        stores = [Store.from_api(s) for s in data]
        self._stores = {s.store_id: s for s in stores}
        return stores

    def get_store(self, store_id: int) -> Optional[Store]:
        """Get a specific store by ID."""
        if not self._stores:
            self.get_stores()
        return self._stores.get(store_id)

    def search_deals(
        self,
        title: str = "",
        store_id: int = 0,
        upper_price: float = 60,
        metacritic_min: int = 0,
        steam_rating_min: int = 0,
        page_size: int = 20,
        sort_by: str = "Deal Rating",
    ) -> list[Deal]:
        """Search for deals with filters."""
        params: dict[str, Any] = {
            "upperPrice": upper_price,
            "pageSize": page_size,
            "sortBy": sort_by,
        }
        if title:
            params["title"] = title
        if store_id:
            params["storeID"] = store_id
        if metacritic_min:
            params["metacritic"] = metacritic_min
        if steam_rating_min:
            params["steamRating"] = steam_rating_min

        data = self._get("deals", params)
        deals = [Deal.from_api(d) for d in data]

        # Enrich with store names
        for deal in deals:
            store = self.get_store(deal.store_id)
            if store:
                deal.store_name = store.name

        return deals

    def search_games(self, title: str, limit: int = 5, exact: bool = False) -> list[GameInfo]:
        """Search for games by title."""
        params: dict[str, Any] = {"title": title, "limit": limit, "exact": 1 if exact else 0}
        data = self._get("games", params)
        return [GameInfo.from_api(g) for g in data]

    def get_game_deals(self, game_id: str) -> list[Deal]:
        """Get all current deals for a specific game."""
        data = self._get("deals", {"gameID": game_id, "upperPrice": 60, "pageSize": 50})
        deals = [Deal.from_api(d) for d in data]
        for deal in deals:
            store = self.get_store(deal.store_id)
            if store:
                deal.store_name = store.name
        return deals

    def get_cheapest_price(self, game_id: str, title: str = "", steam_appid: Optional[int] = None) -> Optional[Deal]:
        """Get the cheapest current deal for a game.

        Uses Steam AppID as primary cross-reference (most reliable).
        For Steam-synced games, game_id IS the Steam AppID.
        Falls back to strict title matching when no AppID match found.
        """
        data = []

        # Determine Steam AppID for cross-reference
        # For Steam-synced games, game_id is the Steam AppID
        effective_appid = steam_appid or (int(game_id) if game_id.isdigit() else None)

        # Strategy 1: If we have a Steam AppID, search by title and filter by steamAppID
        if effective_appid and title:
            raw = self._get("deals", {"title": title, "upperPrice": 60, "pageSize": 50})
            app_matches = [d for d in raw if str(d.get("steamAppID", "")) == str(effective_appid)]
            if app_matches:
                data = app_matches
            elif effective_appid:
                # We have a Steam AppID but no deals match — game is unreleased or not on sale
                return None
        # Strategy 2: Fall back to strict title matching
        if not data and title:
            raw = self._get("deals", {"title": title, "upperPrice": 60, "pageSize": 50})
            title_lower = title.lower().strip()
            title_words = set(title_lower.split())
            num_words = len(title_words)

            filtered = []
            for d in raw:
                deal_title = d.get("title", "").lower().strip()
                deal_words = set(deal_title.split())

                # For single-word titles: require exact word match
                if num_words == 1:
                    if title_lower in deal_title.split():
                        filtered.append(d)
                else:
                    # Multi-word: require 70%+ overlap and deal title isn't drastically longer
                    matches = sum(1 for w in title_words if w in deal_words)
                    ratio = matches / num_words
                    title_len = len(title_lower)
                    deal_len = len(deal_title)
                    if ratio >= 0.7 and deal_len < title_len * 2.5:
                        filtered.append(d)

            if filtered:
                data = filtered
        elif not data and not title:
            data = self._get("deals", {"gameID": game_id, "upperPrice": 60, "pageSize": 50})

        if not data:
            return None

        cheapest = min(data, key=lambda d: float(d.get("salePrice", 999)))
        deal = Deal.from_api(cheapest)
        store = self.get_store(deal.store_id)
        if store:
            deal.store_name = store.name
        return deal


# ── Deal Analysis ───────────────────────────────────────────────────────

class DealAnalyzer:
    """Analyze and rank deals."""

    @staticmethod
    def rank_deals(deals: list[Deal], strategy: str = "value") -> list[Deal]:
        """Rank deals by strategy."""
        if strategy == "value":
            # Best discount + decent rating
            return sorted(
                deals,
                key=lambda d: (d.savings * 0.6 + d.deal_rating * 4 * 0.4),
                reverse=True,
            )
        elif strategy == "cheapest":
            return sorted(deals, key=lambda d: d.sale_price)
        elif strategy == "highest_rated":
            return sorted(deals, key=lambda d: (d.metacritic_score, d.steam_rating), reverse=True)
        elif strategy == "biggest_discount":
            return sorted(deals, key=lambda d: d.savings, reverse=True)
        return deals

    @staticmethod
    def filter_quality(deals: list[Deal], min_rating: int = 0, min_metacritic: int = 0) -> list[Deal]:
        """Filter deals by quality thresholds."""
        return [
            d for d in deals
            if d.metacritic_score >= min_metacritic
            and d.steam_rating >= min_rating
        ]

    @staticmethod
    def find_best_deal(deals: list[Deal]) -> Optional[Deal]:
        """Find the single best deal."""
        if not deals:
            return None
        return max(deals, key=lambda d: d.savings * 0.6 + d.deal_rating * 4 * 0.4)


# ── Wishlist Monitor ────────────────────────────────────────────────────

@dataclass
class WishlistItem:
    game_id: str
    title: str
    target_price: float
    steam_appid: Optional[int] = None
    added_at: str = ""
    last_checked: str = ""
    notified: bool = False

    def __post_init__(self) -> None:
        if not self.added_at:
            self.added_at = datetime.now(timezone.utc).isoformat()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WishlistItem":
        import dataclasses as _dc
        known = {f.name for f in _dc.fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


class WishlistMonitor:
    """Monitor wishlist for price drops."""

    def __init__(self, client: CheapSharkClient, state_file: str = "") -> None:
        self.client = client
        self.state_file = state_file or os.path.join(os.path.dirname(__file__), "wishlist.json")
        self.items: list[WishlistItem] = []
        self._load()

    def _load(self) -> None:
        """Load wishlist from file."""
        if not os.path.exists(self.state_file):
            return
        try:
            with open(self.state_file) as f:
                content = f.read().strip()
                if not content:
                    return
                data = json.loads(content)
                self.items = [WishlistItem.from_dict(item) for item in data.get("items", data.get("games", []))]
        except json.JSONDecodeError as e:
            logger.warning("Invalid JSON in wishlist file %s: %s", self.state_file, e)
            self.items = []
        except KeyError as e:
            logger.warning("Missing key in wishlist data: %s", e)
            self.items = []
        except OSError as e:
            logger.warning("Error reading wishlist file %s: %s", self.state_file, e)
            self.items = []

    def _save(self) -> None:
        """Save wishlist to file."""
        data = {
            "items": [asdict(item) for item in self.items],
            "updated": datetime.now(timezone.utc).isoformat(),
        }
        try:
            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            logger.error("Failed to save wishlist to %s: %s", self.state_file, e)
            raise DealTrackerError(f"Failed to save wishlist: {e}") from e

    def add(self, game_id: str, title: str, target_price: float) -> WishlistItem:
        """Add a game to the wishlist."""
        if not game_id or not isinstance(game_id, str):
            raise DealTrackerError("game_id must be a non-empty string")
        if not title or not isinstance(title, str):
            raise DealTrackerError("title must be a non-empty string")
        if not isinstance(target_price, (int, float)) or target_price < 0:
            raise DealTrackerError("target_price must be a non-negative number")

        # Check if already tracked
        for item in self.items:
            if item.game_id == game_id:
                item.target_price = target_price
                self._save()
                return item

        item = WishlistItem(game_id=game_id, title=title, target_price=target_price)
        self.items.append(item)
        self._save()
        return item

    def remove(self, game_id: str) -> bool:
        """Remove a game from the wishlist."""
        before = len(self.items)
        self.items = [i for i in self.items if i.game_id != game_id]
        if len(self.items) < before:
            self._save()
            return True
        return False

    def check_prices(self) -> list[PriceAlert]:
        """Check all wishlist items for price drops. Returns alerts."""
        alerts: list[PriceAlert] = []
        for item in self.items:
            try:
                deal = self.client.get_cheapest_price(item.game_id, title=item.title, steam_appid=item.steam_appid)
            except APIError as e:
                logger.warning("Failed to check price for %s: %s", item.game_id, e)
                continue
            if not deal:
                continue

            item.last_checked = datetime.now(timezone.utc).isoformat()

            if deal.sale_price <= item.target_price and not item.notified:
                alert = PriceAlert(
                    game_title=item.title,
                    current_price=deal.sale_price,
                    lowest_price=item.target_price,
                    store=deal.store_name,
                    url=f"https://www.cheapshark.com/redirect?dealID={deal.deal_id}",
                )
                alerts.append(alert)
                item.notified = True
            elif deal.sale_price > item.target_price:
                item.notified = False

        self._save()
        return alerts

    def get_status(self) -> list[dict[str, Any]]:
        """Get status of all tracked games."""
        status: list[dict[str, Any]] = []
        for item in self.items:
            try:
                deal = self.client.get_cheapest_price(item.game_id, title=item.title, steam_appid=item.steam_appid)
            except APIError as e:
                logger.warning("Failed to get price for %s: %s", item.game_id, e)
                deal = None
            status.append({
                "title": item.title,
                "target": item.target_price,
                "current": deal.sale_price if deal else None,
                "store": deal.store_name if deal else "N/A",
                "alert": deal.sale_price <= item.target_price if deal else False,
            })
        return status


# ── Price Comparison Report ─────────────────────────────────────────────

class DealReporter:
    """Generate human-readable deal reports with discount tiers."""

    @staticmethod
    def format_deal(deal: Deal) -> str:
        """Format a single deal for display."""
        emoji = deal.discount_tier_emoji
        rating = f" ⭐{deal.metacritic_score}" if deal.metacritic_score else ""
        steam = f" 👍{deal.steam_rating}%" if deal.steam_rating else ""

        return (
            f"{emoji} {deal.title}\n"
            f"   💵 ${deal.sale_price:.2f} (was ${deal.normal_price:.2f}) — {deal.savings:.0f}% off\n"
            f"   🏪 {deal.store_name}{rating}{steam}\n"
            f"   ⭐ Deal Rating: {deal.deal_rating:.1f}/10"
        )

    @staticmethod
    def format_tiered_report(deals: list[Deal], title: str = "Deal Report") -> str:
        """Format deals grouped by discount tier (yield rainbow style)."""
        if not deals:
            return f"❌ No deals found for '{title}'"

        # Group by tier
        tiers = {
            "deep_cut": {"emoji": "🔥", "label": "DEEP CUTS (50%+ off)", "deals": []},
            "solid_sale": {"emoji": "💰", "label": "SOLID SALES (25-49% off)", "deals": []},
            "light_mark": {"emoji": "🏷️", "label": "LIGHT MARKS (10-24% off)", "deals": []},
            "barely": {"emoji": "📉", "label": "BARELY TOUCHING IT (<10%)", "deals": []}
        }

        for deal in deals:
            tier = deal.discount_tier
            tiers[tier]["deals"].append(deal)

        lines: list[str] = [f"📊 {title}\n{'━' * 40}"]

        # Render each tier
        for tier_key in ["deep_cut", "solid_sale", "light_mark", "barely"]:
            tier = tiers[tier_key]
            if not tier["deals"]:
                continue
            lines.append(f"\n{tier['emoji']} {tier['label']}")
            lines.append(f"{'━' * 40}")
            for deal in tier["deals"][:5]:  # Cap at 5 per tier
                lines.append(f"\n{deal.title}")
                lines.append(f"   ${deal.sale_price:.2f} (was ${deal.normal_price:.2f}) {deal.savings:.0f}% off @ {deal.store_name}")

        # Summary
        best = DealAnalyzer.find_best_deal(deals)
        if best:
            lines.append(f"\n{'━' * 40}")
            lines.append(f"🏆 Best Deal: {best.title} — ${best.sale_price:.2f} ({best.savings:.0f}% off)")

        # Tier counts
        deep_count = len(tiers["deep_cut"]["deals"])
        solid_count = len(tiers["solid_sale"]["deals"])
        if deep_count or solid_count:
            lines.append(f"\n📈 {deep_count} deep cuts, {solid_count} solid sales across {len(deals)} total deals")

        return "\n".join(lines)

    @staticmethod
    def format_comparison(deals: list[Deal], title: str = "Deal Comparison") -> str:
        """Format a comparison report (legacy flat format)."""
        if not deals:
            return f"❌ No deals found for '{title}'"

        lines: list[str] = [f"📊 {title}\n{'━' * 40}"]
        for i, deal in enumerate(deals[:10], 1):
            lines.append(f"\n#{i}")
            lines.append(DealReporter.format_deal(deal))

        best = DealAnalyzer.find_best_deal(deals)
        if best:
            lines.append(f"\n{'━' * 40}")
            lines.append(f"🏆 Best Deal: {best.title} — ${best.sale_price:.2f} ({best.savings:.0f}% off)")

        return "\n".join(lines)

    @staticmethod
    def format_wishlist_alerts(alerts: list[PriceAlert]) -> str:
        """Format wishlist price alerts."""
        if not alerts:
            return "✅ No new price alerts."

        lines: list[str] = [f"🔔 {len(alerts)} Price Alert(s)\n{'━' * 40}"]
        for alert in alerts:
            lines.append(f"\n{alert.message}")
        return "\n".join(lines)


# ── Exceptions ──────────────────────────────────────────────────────────

class APIError(Exception):
    pass


class DealTrackerError(Exception):
    pass
