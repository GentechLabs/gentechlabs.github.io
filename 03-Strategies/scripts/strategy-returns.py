#!/usr/bin/env python3
"""
Strategy Returns Tracker — AAE Hybrid Strategy Engine
Tracks and compares returns across LP, HODL, Staking, and Lending strategies.

Data Sources:
  - DexScreener: price, volume, LP pool data
  - DeFiLlama: staking APR, lending APY (Benqi on Avalanche)
  - On-chain: wallet balances, LP position
  - Computed: HODL returns, LP net returns (fees - IL)
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

# ── Config ──────────────────────────────────────────────────────────────────

STATE_DIR = os.path.expanduser("~/.hermes/scripts")
RETURNS_STATE_FILE = os.path.join(STATE_DIR, ".aae-strategy-returns.json")

WALLET = "0x7ebff188f2Eba16518C02864589b1403a5d1296a"
POOL_ADDRESS = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"

# Avalanche contract addresses
SAVAX_ADDRESS = "0x2b2c81e08f1af8835a78bb2a90ae924ace0fa45e"
QIUSDC_ADDRESS = "0xB717Dc8961e741eB4351A1e7e9b500fC26e23afA"

# DeFiLlama protocol filter
DEFILLAMA_PROTOCOL = "benqi"
DEFILLAMA_CHAIN = "Avalanche"


def fetch_json(url: str, headers: Optional[Dict] = None, timeout: int = 15) -> Optional[Dict]:
    """Fetch JSON from URL with error handling."""
    default_headers = {"User-Agent": "Mozilla/5.0 (AAE-Hybrid/1.0)"}
    if headers:
        default_headers.update(headers)
    try:
        req = urllib.request.Request(url, headers=default_headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[returns] fetch error: {e}", flush=True)
        return None


# ── Price Data ──────────────────────────────────────────────────────────────

def fetch_avax_price() -> Optional[float]:
    """Fetch current AVAX price from DexScreener."""
    url = f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{POOL_ADDRESS}"
    data = fetch_json(url)
    if data and "pairs" in data and data["pairs"]:
        return float(data["pairs"][0].get("priceUsd", 0))
    return None


def fetch_avax_price_coingecko() -> Optional[float]:
    """Fallback: AVAX price from CoinGecko."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2&vs_currencies=usd"
    data = fetch_json(url)
    if data and "avalanche-2" in data:
        return data["avalanche-2"].get("usd")
    return None


# ── DeFiLlama Staking/Lending Rates ────────────────────────────────────────

def fetch_defillama_pools() -> List[Dict]:
    """Fetch all Avalanche pools from DeFiLlama Yields API."""
    url = "https://yields.llama.fi/pools"
    data = fetch_json(url)
    if not data or "data" not in data:
        return []

    # Filter for Benqi on Avalanche
    benqi_pools = []
    for pool in data["data"]:
        if (pool.get("project", "").lower() == DEFILLAMA_PROTOCOL.lower() and
            pool.get("chain", "").lower() == DEFILLAMA_CHAIN.lower()):
            benqi_pools.append({
                "pool_id": pool.get("pool", ""),
                "symbol": pool.get("symbol", ""),
                "apy": pool.get("apy", 0) or 0,
                "apy_base": pool.get("apyBase", 0) or 0,
                "apy_reward": pool.get("apyReward", 0) or 0,
                "tvl_usd": pool.get("tvlUsd", 0) or 0,
                "stablecoin": pool.get("stablecoin", False),
                "il_risk": pool.get("ilRisk", "unknown"),
                "exposure": pool.get("exposure", "unknown"),
                "pool_meta": pool.get("poolMeta", ""),
            })
    return benqi_pools


def get_staking_apr(pools: List[Dict]) -> Optional[Dict]:
    """Extract sAVAX staking APR from Benqi pools."""
    for pool in pools:
        sym = pool["symbol"].upper()
        if "SAVAX" in sym or "SAVAX" in sym.replace(".", "").replace("-", ""):
            return {
                "apr": pool["apy"],
                "apy_base": pool["apy_base"],
                "apy_reward": pool["apy_reward"],
                "tvl_usd": pool["tvl_usd"],
                "symbol": pool["symbol"],
            }
    # Fallback: look for AVAX staking
    for pool in pools:
        if "AVAX" in pool["symbol"].upper() and pool["exposure"] == "native":
            return {
                "apr": pool["apy"],
                "apy_base": pool["apy_base"],
                "apy_reward": pool["apy_reward"],
                "tvl_usd": pool["tvl_usd"],
                "symbol": pool["symbol"],
            }
    return None


def get_lending_rates(pools: List[Dict]) -> Dict[str, Dict]:
    """Extract lending supply APY for major assets."""
    results = {}
    target_symbols = ["USDC", "AVAX", "USDT", "WETH"]

    for pool in pools:
        sym = pool["symbol"].upper()
        for target in target_symbols:
            if target in sym and target not in results:
                results[target] = {
                    "supply_apy": pool["apy"],
                    "apy_base": pool["apy_base"],
                    "tvl_usd": pool["tvl_usd"],
                    "symbol": pool["symbol"],
                }
    return results


# ── LP Return Estimation ───────────────────────────────────────────────────

def estimate_lp_returns(
    position_value: float,
    fees_24h: float,
    price_change_24h: float,
    range_width_pct: float = 0.05,  # 5% range width
) -> Dict[str, float]:
    """
    Estimate LP net return (fees - impermanent loss).

    IL approximation for concentrated liquidity:
    IL ≈ (price_change)^2 / (8 * range_width^2) for narrow ranges
    """
    # Impermanent loss approximation
    il_pct = (price_change_24h / 100) ** 2 / (8 * range_width_pct ** 2) if range_width_pct > 0 else 0
    il_usd = position_value * il_pct

    # Net return
    net_return_24h = fees_24h - il_usd
    net_apr = (net_return_24h / position_value * 365 * 100) if position_value > 0 else 0
    gross_apr = (fees_24h / position_value * 365 * 100) if position_value > 0 else 0

    return {
        "fees_24h": round(fees_24h, 4),
        "il_24h": round(il_usd, 4),
        "il_pct": round(il_pct * 100, 4),
        "net_return_24h": round(net_return_24h, 4),
        "gross_apr": round(gross_apr, 2),
        "net_apr": round(net_apr, 2),
        "position_value": round(position_value, 2),
    }


# ── HODL Return Estimation ─────────────────────────────────────────────────

def estimate_hodl_returns(
    spot_value: float,
    price_change_24h_pct: float,
    price_change_7d_pct: Optional[float] = None,
) -> Dict[str, float]:
    """Calculate HODL returns from price appreciation."""
    daily_return = spot_value * (price_change_24h_pct / 100)
    daily_apr_equiv = price_change_24h_pct * 365  # annualized

    weekly_return = spot_value * ((price_change_7d_pct or 0) / 100) if price_change_7d_pct else None

    return {
        "spot_value": round(spot_value, 2),
        "return_24h": round(daily_return, 4),
        "return_24h_pct": round(price_change_24h_pct, 2),
        "apr_equivalent": round(daily_apr_equiv, 1),
        "return_7d": round(weekly_return, 4) if weekly_return is not None else None,
        "return_7d_pct": price_change_7d_pct,
    }


# ── Main Comparison Pipeline ───────────────────────────────────────────────

def run_strategy_comparison(
    position_value: float = 134.94,
    spot_value: float = 0.0961,  # AVAX in wallet
    fees_24h: float = 0.0,
    price_change_24h_pct: float = 0.5,
) -> Dict[str, Any]:
    """
    Run full strategy comparison.
    Returns structured data with per-strategy returns + leaderboard.
    """
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "strategies": {},
        "leaderboard": [],
        "recommendation": None,
    }

    # 1. Fetch current price
    avax_price = fetch_avax_price() or fetch_avax_price_coingecko()
    if not avax_price:
        result["error"] = "Failed to fetch AVAX price"
        return result

    result["avax_price"] = avax_price

    # 2. Fetch DeFiLlama rates
    pools = fetch_defillama_pools()
    staking = get_staking_apr(pools)
    lending = get_lending_rates(pools)

    # 3. LP Returns
    lp = estimate_lp_returns(
        position_value=position_value,
        fees_24h=fees_24h,
        price_change_24h=price_change_24h_pct,
    )
    result["strategies"]["lp"] = lp

    # 4. HODL Returns
    spot_usd = spot_value * avax_price
    hodl = estimate_hodl_returns(
        spot_value=spot_usd,
        price_change_24h_pct=price_change_24h_pct,
    )
    result["strategies"]["hodl"] = hodl

    # 5. Staking Returns
    if staking:
        staking_value = spot_usd  # assuming we'd stake our AVAX
        daily_staking = staking_value * (staking["apr"] / 100 / 365)
        result["strategies"]["staking"] = {
            "apr": round(staking["apr"], 2),
            "daily_return": round(daily_staking, 4),
            "value": round(staking_value, 2),
            "tvl_usd": staking["tvl_usd"],
            "symbol": staking["symbol"],
        }
    else:
        result["strategies"]["staking"] = {"apr": 0, "daily_return": 0, "value": 0, "error": "no data"}

    # 6. Lending Returns
    if lending:
        # Use USDC rate as primary (stablecoin lending)
        usdc_lending = lending.get("USDC", {})
        if usdc_lending:
            lending_value = 103.38  # from config - USDC in LP
            daily_lending = lending_value * (usdc_lending["supply_apy"] / 100 / 365)
            result["strategies"]["lending"] = {
                "supply_apy": round(usdc_lending["supply_apy"], 2),
                "daily_return": round(daily_lending, 4),
                "value": round(lending_value, 2),
                "symbol": usdc_lending["symbol"],
            }
        else:
            result["strategies"]["lending"] = {"supply_apy": 0, "daily_return": 0, "value": 0, "error": "no USDC rate"}
    else:
        result["strategies"]["lending"] = {"supply_apy": 0, "daily_return": 0, "value": 0, "error": "no data"}

    # 7. Build leaderboard (sorted by daily return)
    leaderboard = []
    for name, data in result["strategies"].items():
        daily = data.get("daily_return", 0) or data.get("net_return_24h", 0) or data.get("return_24h", 0)
        leaderboard.append({
            "strategy": name.upper(),
            "daily_return": round(daily, 4),
            "apr": round(data.get("net_apr") or data.get("apr") or data.get("apr_equivalent") or data.get("supply_apy") or 0, 1),
            "risk": {"LP": "Medium", "HODL": "Market", "STAKING": "Low", "LENDING": "Low-Medium"}.get(name.upper(), "Unknown"),
        })

    leaderboard.sort(key=lambda x: x["daily_return"], reverse=True)
    result["leaderboard"] = leaderboard

    # 8. Simple recommendation
    if leaderboard:
        winner = leaderboard[0]
        result["recommendation"] = {
            "winner": winner["strategy"],
            "daily_return": winner["daily_return"],
            "apr": winner["apr"],
            "note": f"{winner['strategy']} is currently the best performer with {winner['apr']:.1f}% APR",
        }

    # 9. Save state
    os.makedirs(os.path.dirname(RETURNS_STATE_FILE), exist_ok=True)
    with open(RETURNS_STATE_FILE, "w") as f:
        json.dump(result, f, indent=2)

    return result


# ── Human-Readable Output ──────────────────────────────────────────────────

def format_leaderboard(result: Dict[str, Any]) -> str:
    """Format strategy leaderboard as human-readable text."""
    lines = []
    lines.append("📊 STRATEGY LEADERBOARD")
    lines.append(f"   AVAX: ${result.get('avax_price', 0):.2f}")
    lines.append("")

    for i, entry in enumerate(result.get("leaderboard", []), 1):
        medal = ["🥇", "🥈", "🥉", "4."][i-1] if i <= 4 else f"{i}."
        daily = entry["daily_return"]
        sign = "+" if daily >= 0 else ""
        lines.append(f"   {medal} {entry['strategy']:10s} {sign}${daily:.4f}/day  ({entry['apr']:.1f}% APR)  Risk: {entry['risk']}")

    lines.append("")
    rec = result.get("recommendation")
    if rec:
        lines.append(f"💡 RECOMMENDATION: {rec['note']}")

    return "\n".join(lines)


# ── CLI Entry Point ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    result = run_strategy_comparison()

    # Print human-readable
    print(format_leaderboard(result))
    print("\n--- JSON ---")
    print(json.dumps(result, indent=2))
