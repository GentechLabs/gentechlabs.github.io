"""
LP Monitor Signal Engine
Detects impermanent loss drift, efficiency degradation, and rebalance opportunities
for concentrated liquidity positions (LFJ, Uniswap V3).

Built for: Swarms ACM Hackathon — Finance & Market Analysis track
"""

import json
import urllib.request
from datetime import datetime, timezone
from typing import Optional


# ── Signal: Fetch Token Prices ────────────────────────────────────────────

def fetch_token_prices(symbols: str = "AVAX,USDC") -> dict:
    """Fetch current token prices from CoinGecko with DexScreener fallback."""
    coin_ids = {
        "AVAX": "avalanche-2",
        "USDC": "usd-coin",
        "ETH": "ethereum",
        "SOL": "solana",
        "BTC": "bitcoin",
        "JOE": "joe-2",
    }

    results = {}
    primary_failed = False

    for symbol in symbols.split(","):
        symbol = symbol.strip().upper()
        coin_id = coin_ids.get(symbol)
        if not coin_id:
            results[symbol] = {"error": f"Unknown symbol: {symbol}"}
            continue

        if not primary_failed:
            try:
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
                req = urllib.request.Request(url, headers={"User-Agent": "Gentech-DeFi/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                    price_data = data.get(coin_id, {})
                    results[symbol] = {
                        "price_usd": price_data.get("usd", 0),
                        "change_24h_pct": round(price_data.get("usd_24h_change", 0), 2),
                    }
                    continue
            except Exception:
                primary_failed = True

        # Fallback: DexScreener
        try:
            results[symbol] = _dexscreener_fallback(symbol)
        except Exception as e:
            results[symbol] = {"error": f"All sources failed: {e}"}

    return results


def _dexscreener_fallback(symbol: str) -> dict:
    """Try DexScreener for a known pool."""
    url = "https://api.dexscreener.com/latest/dex/pairs/avalanche/0x864d4e5ee7318e97483db7eb0912e09f161516ea"
    req = urllib.request.Request(url, headers={"User-Agent": "Gentech-DeFi/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        pairs = data.get("pairs", [])
        if not pairs:
            return {"error": "No pool data"}
        pair = pairs[0]
        if symbol in ("AVAX", pair.get("baseToken", {}).get("symbol", "").upper()):
            return {
                "price_usd": float(pair.get("priceUsd", 0)),
                "change_24h_pct": float(pair.get("priceChange", {}).get("h24", 0)),
                "source": "dexscreener",
            }
        elif symbol in ("USDC", pair.get("quoteToken", {}).get("symbol", "").upper()):
            return {"price_usd": 1.0, "change_24h_pct": 0.0, "source": "dexscreener"}
        return {"error": f"No fallback for {symbol}"}


# ── Signal: Read Pool State ──────────────────────────────────────────────

def read_pool_state(
    pool_address: str = "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
    chain: str = "avalanche",
) -> dict:
    """Read LP pool state from DexScreener API."""
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}"
        req = urllib.request.Request(url, headers={"User-Agent": "Gentech-DeFi/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            pairs = data.get("pairs", [])
            if not pairs:
                return {"error": "No pairs found for this address"}

            pair = pairs[0]
            fee = pair.get("fee", 0)
            volume_24h = pair.get("volume", {}).get("h24", 0)
            return {
                "pool_address": pool_address,
                "chain": chain,
                "base_token": pair.get("baseToken", {}).get("symbol", "?"),
                "quote_token": pair.get("quoteToken", {}).get("symbol", "?"),
                "price_usd": float(pair.get("priceUsd", 0)),
                "price_native": float(pair.get("priceNative", 0)),
                "tvl_usd": pair.get("liquidity", {}).get("usd", 0),
                "volume_24h": volume_24h,
                "fees_24h": fee if fee else volume_24h * 0.003,
                "apr_7d": pair.get("apy", {}).get("total", 0) if pair.get("apy") else 0,
                "price_change_24h": pair.get("priceChange", {}).get("h24", 0),
            }
    except Exception as e:
        return {"error": str(e)}


# ── Signal: Calculate Impermanent Loss ────────────────────────────────────

def calculate_il(
    entry_price: float,
    current_price: float,
    range_low: float,
    range_high: float,
    initial_value_usd: float = 100.0,
    shape: str = "curve",
) -> dict:
    """
    Calculate impermanent loss for a concentrated liquidity position.
    Returns IL metrics, HODL comparison, and position status.
    """
    if current_price <= 0 or entry_price <= 0:
        return {"error": "Prices must be positive"}

    price_ratio = current_price / entry_price
    hodl_value = initial_value_usd * price_ratio
    in_range = range_low <= current_price <= range_high
    range_width_pct = ((range_high - range_low) / range_low) * 100 if range_low > 0 else 0

    # Concentrated IL multiplier (tighter range = more IL)
    concentration_factor = 1.0
    if range_width_pct > 0:
        concentration_factor = max(1.0, 10.0 / range_width_pct)

    # Base IL: 2*sqrt(r)/(1+r) - 1
    base_il = (2 * (price_ratio ** 0.5) / (1 + price_ratio)) - 1 if price_ratio > 0 else -1.0
    adjusted_il_pct = base_il * concentration_factor * 100

    # Status
    if current_price < range_low:
        status = "BELOW_RANGE — 100% quote token, earning zero fees"
    elif current_price > range_high:
        status = "ABOVE_RANGE — 100% base token, earning zero fees"
    else:
        status = "IN_RANGE — earning fees"

    fee_efficiency = 100.0 if in_range else 0.0
    dist_to_low = ((current_price - range_low) / range_low) * 100 if range_low > 0 else 0
    dist_to_high = ((range_high - current_price) / range_high) * 100 if range_high > 0 else 0

    return {
        "current_price": round(current_price, 4),
        "entry_price": entry_price,
        "range_low": range_low,
        "range_high": range_high,
        "range_width_pct": round(range_width_pct, 2),
        "in_range": in_range,
        "status": status,
        "impermanent_loss_pct": round(adjusted_il_pct, 2),
        "hodl_value_usd": round(hodl_value, 2),
        "position_value_usd": round(initial_value_usd * (1 + base_il), 2),
        "fee_efficiency_pct": fee_efficiency,
        "distance_to_low_pct": round(dist_to_low, 2),
        "distance_to_high_pct": round(dist_to_high, 2),
        "shape": shape,
        "concentration_factor": round(concentration_factor, 2),
    }


# ── Signal: Generate Rebalance Recommendation ─────────────────────────────

def get_recommendation(il_data: dict) -> str:
    """Generate rebalance recommendation based on position data."""
    if il_data.get("error"):
        return "Insufficient data for recommendation"

    in_range = il_data.get("in_range", False)
    dist_to_low = il_data.get("distance_to_low_pct", 0)
    dist_to_high = il_data.get("distance_to_high_pct", 0)
    il_pct = abs(il_data.get("impermanent_loss_pct", 0))

    if not in_range:
        current = il_data.get("current_price", 0)
        new_low = round(current * 0.97, 2)
        new_high = round(current * 1.03, 2)
        direction = "below" if current < il_data.get("range_low", 0) else "above"
        return f"🚨 OUT OF RANGE ({direction}). Rebalance suggested: ${new_low}–${new_high} (±3% around ${current})"

    if dist_to_low < 1.0:
        return "⚠️ WARNING: Price near lower bound. Consider widening range or rebalancing down."
    if dist_to_high < 1.0:
        return "⚠️ WARNING: Price near upper bound. Consider widening range or rebalancing up."
    if il_pct >= 2.0:
        return f"⚠️ IL at {il_pct:.1f}% — review position health and consider rebalancing."
    if il_data.get("fee_efficiency_pct", 0) < 50:
        return "⚠️ Low fee efficiency — consider shape change (Curve → Bidirectional or vice versa)."

    return "✅ Position healthy. No immediate action needed."


# ── Signal: Full LP Position Report ───────────────────────────────────────

def lp_position_report(
    pool_address: str = "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
    chain: str = "avalanche",
    range_low: float = 10.15,
    range_high: float = 10.38,
    entry_price: float = 9.95,
    initial_value_usd: float = 134.94,
    shape: str = "curve",
) -> dict:
    """Generate a complete LP position report with recommendations."""
    prices = fetch_token_prices("AVAX,USDC")
    pool = read_pool_state(pool_address, chain)

    current_price = prices.get("AVAX", {}).get("price_usd", 0)
    if current_price == 0:
        current_price = pool.get("price_native", 0)
    if current_price == 0:
        return {"error": "Could not fetch current price"}

    il_data = calculate_il(
        entry_price=entry_price,
        current_price=current_price,
        range_low=range_low,
        range_high=range_high,
        initial_value_usd=initial_value_usd,
        shape=shape,
    )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pool": {
            "address": pool_address,
            "chain": chain,
            "tokens": f"{pool.get('base_token', 'AVAX')}/{pool.get('quote_token', 'USDC')}",
            "tvl_usd": pool.get("tvl_usd", 0),
            "volume_24h": pool.get("volume_24h", 0),
            "apr_7d": pool.get("apr_7d", 0),
        },
        "position": il_data,
        "market": {
            "avax_price_usd": current_price,
            "avax_24h_change": prices.get("AVAX", {}).get("change_24h_pct", 0),
        },
        "recommendation": get_recommendation(il_data),
    }


# ── Signal: Whale Watch (bonus signal) ────────────────────────────────────

def whale_watch(
    pool_address: str = "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
    chain: str = "avalanche",
    threshold_usd: float = 50_000,
) -> dict:
    """
    Monitor pool for large liquidity events (adds/removes) above threshold.
    Uses DexScreener pair data as proxy for pool activity.
    """
    pool = read_pool_state(pool_address, chain)
    if "error" in pool:
        return {"error": pool["error"]}

    volume_24h = pool.get("volume_24h", 0)
    tvl = pool.get("tvl_usd", 0)
    volume_to_tvl_ratio = (volume_24h / tvl * 100) if tvl > 0 else 0

    signal = "NORMAL"
    if volume_to_tvl_ratio > 100:
        signal = "HIGH_ACTIVITY — Volume exceeds TVL, possible whale repositioning"
    elif volume_to_tvl_ratio > 50:
        signal = "ELEVATED — Unusual volume detected"

    return {
        "pool_address": pool_address,
        "volume_24h_usd": volume_24h,
        "tvl_usd": tvl,
        "volume_to_tvl_pct": round(volume_to_tvl_ratio, 2),
        "signal": signal,
        "threshold_usd": threshold_usd,
    }


# ── Signal: Yield Opportunity Scanner ─────────────────────────────────────

def scan_yield_opportunities(pools: list[dict]) -> list[dict]:
    """
    Scan multiple pools for yield opportunities.
    Each pool dict: {address, chain, name}
    Returns ranked list by APR.
    """
    results = []
    for pool in pools:
        data = read_pool_state(pool["address"], pool.get("chain", "avalanche"))
        if "error" not in data:
            results.append({
                "name": pool.get("name", pool["address"][:8]),
                "apr_7d": data.get("apr_7d", 0),
                "tvl_usd": data.get("tvl_usd", 0),
                "volume_24h": data.get("volume_24h", 0),
                "price_usd": data.get("price_usd", 0),
            })

    return sorted(results, key=lambda x: x.get("apr_7d", 0), reverse=True)
