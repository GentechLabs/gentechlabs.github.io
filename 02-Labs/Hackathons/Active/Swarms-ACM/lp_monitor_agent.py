#!/usr/bin/env python3
"""
DeFi LP Monitor — Swarms Marketplace Agent
Monitors concentrated liquidity LP positions with IL tracking, efficiency scoring, and rebalance alerts.

Built for: Swarms ACM Hackathon (May 27, 2026)
Category: Finance & Market Analysis
"""

import os
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from typing import Optional

# ── Tool: Fetch Token Prices ──────────────────────────────────────────────

def fetch_token_prices(symbols: str = "AVAX,USDC", pool_address: str = "0x864d4e5ee7318e97483db7eb0912e09f161516ea", chain: str = "avalanche") -> dict:
    """
    Fetch current token prices from CoinGecko with DexScreener fallback.
    
    Args:
        symbols: Comma-separated token symbols (e.g., "AVAX,USDC")
        pool_address: Pool address for DexScreener fallback price
        chain: Chain for DexScreener fallback
    
    Returns:
        Dict with token prices and 24h changes
    """
    coin_ids = {
        "AVAX": "avalanche-2",
        "USDC": "usd-coin",
        "ETH": "ethereum",
        "SOL": "solana",
        "BTC": "bitcoin",
    }
    
    results = {}
    primary_failed = False
    
    for symbol in symbols.split(","):
        symbol = symbol.strip().upper()
        coin_id = coin_ids.get(symbol)
        if not coin_id:
            results[symbol] = {"error": f"Unknown symbol: {symbol}"}
            continue
        
        # Try CoinGecko first (unless already failed)
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
        
        # Fallback: DexScreener pool data
        try:
            url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}"
            req = urllib.request.Request(url, headers={"User-Agent": "Gentech-DeFi/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                pairs = data.get("pairs", [])
                if pairs:
                    pair = pairs[0]
                    if symbol == "AVAX" or symbol == pair.get("baseToken", {}).get("symbol", "").upper():
                        results[symbol] = {
                            "price_usd": float(pair.get("priceNative", 0) or pair.get("priceUsd", 0)),
                            "change_24h_pct": float(pair.get("priceChange", {}).get("h24", 0)),
                            "source": "dexscreener",
                        }
                    elif symbol == "USDC" or symbol == pair.get("quoteToken", {}).get("symbol", "").upper():
                        results[symbol] = {
                            "price_usd": 1.0,  # USDC peg
                            "change_24h_pct": 0.0,
                            "source": "dexscreener",
                        }
                    else:
                        results[symbol] = {"error": f"No DexScreener fallback for {symbol}"}
                else:
                    results[symbol] = {"error": f"No pool data for {symbol}"}
        except Exception as e:
            results[symbol] = {"error": f"All sources failed: {e}"}
    
    return results


# ── Tool: Read Pool State ─────────────────────────────────────────────────

def read_pool_state(pool_address: str = "0x864d4e5ee7318e97483db7eb0912e09f161516ea", chain: str = "avalanche") -> dict:
    """
    Read LP pool state from DexScreener API.
    
    Args:
        pool_address: The pool/pair contract address
        chain: Blockchain name (avalanche, ethereum, solana, etc.)
    
    Returns:
        Dict with pool TVL, volume, fees, APR, and price data
    """
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}"
        req = urllib.request.Request(url, headers={"User-Agent": "Gentech-DeFi/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            pairs = data.get("pairs", [])
            if not pairs:
                return {"error": "No pairs found for this address"}
            
            pair = pairs[0]
            return {
                "pool_address": pool_address,
                "chain": chain,
                "base_token": pair.get("baseToken", {}).get("symbol", "?"),
                "quote_token": pair.get("quoteToken", {}).get("symbol", "?"),
                "price_usd": float(pair.get("priceUsd", 0)),
                "price_native": float(pair.get("priceNative", 0)),
                "tvl_usd": pair.get("liquidity", {}).get("usd", 0),
                "volume_24h": pair.get("volume", {}).get("h24", 0),
                "fees_24h": pair.get("fee", 0) if pair.get("fee") else pair.get("volume", {}).get("h24", 0) * 0.003,
                "apr_7d": pair.get("apy", {}).get("total", 0) if pair.get("apy") else 0,
                "price_change_24h": pair.get("priceChange", {}).get("h24", 0),
                "pair_created_at": pair.get("pairCreatedAt"),
            }
    except Exception as e:
        return {"error": str(e)}


# ── Tool: Calculate Impermanent Loss ──────────────────────────────────────

def calculate_il(
    entry_price: float,
    current_price: float,
    range_low: float,
    range_high: float,
    initial_value_usd: float = 100.0,
    shape: str = "curve"
) -> dict:
    """
    Calculate impermanent loss for a concentrated liquidity position.
    
    Args:
        entry_price: Price when position was opened
        current_price: Current token price
        range_low: Lower bound of LP range
        range_high: Upper bound of LP range
        initial_value_usd: Initial position value in USD
        shape: Liquidity shape (curve, spot, bid-ask)
    
    Returns:
        Dict with IL metrics, HODL comparison, and position status
    """
    # Simple IL approximation for concentrated liquidity
    # Full range IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1
    # Concentrated IL is amplified by range tightness
    
    if current_price <= 0 or entry_price <= 0:
        return {"error": "Prices must be positive"}
    
    price_ratio = current_price / entry_price
    
    # HODL value (no IL)
    hodl_value = initial_value_usd * price_ratio
    
    # Range status
    in_range = range_low <= current_price <= range_high
    range_width_pct = ((range_high - range_low) / range_low) * 100 if range_low > 0 else 0
    
    # Concentrated IL multiplier (tighter range = more IL)
    concentration_factor = 1.0
    if range_width_pct > 0:
        concentration_factor = max(1.0, 10.0 / range_width_pct)  # Baseline: 10% range
    
    # Base IL calculation
    if price_ratio > 0:
        base_il = (2 * (price_ratio ** 0.5) / (1 + price_ratio)) - 1
    else:
        base_il = -1.0
    
    # Adjusted IL for concentrated liquidity
    adjusted_il_pct = base_il * concentration_factor * 100
    
    # Position status
    if current_price < range_low:
        status = "BELOW_RANGE — 100% quote token, earning zero fees"
    elif current_price > range_high:
        status = "ABOVE_RANGE — 100% base token, earning zero fees"
    else:
        status = "IN_RANGE — earning fees"
    
    # Fee efficiency estimate (simplified)
    # In range = earning, out of range = 0
    fee_efficiency = 100.0 if in_range else 0.0
    
    # Distance from range edges
    dist_to_low = ((current_price - range_low) / range_low) * 100 if range_low > 0 else 0
    dist_to_high = ((range_high - current_price) / range_high) * 100 if range_high > 0 else 0
    
    return {
        "current_price": current_price,
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


# ── Tool: Full LP Position Report ─────────────────────────────────────────

def lp_position_report(
    pool_address: str = "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
    chain: str = "avalanche",
    range_low: float = 10.15,
    range_high: float = 10.38,
    entry_price: float = 9.95,
    initial_value_usd: float = 134.94,
    shape: str = "curve"
) -> dict:
    """
    Generate a complete LP position report with price data, IL calculation, and rebalance recommendations.
    
    Args:
        pool_address: LFJ pool address
        chain: Blockchain name
        range_low: Lower bound of LP range
        range_high: Upper bound of LP range
        entry_price: Price when position was opened
        initial_value_usd: Initial position value
        shape: Liquidity shape
    
    Returns:
        Complete position report with recommendations
    """
    # Fetch live data
    prices = fetch_token_prices("AVAX,USDC")
    pool = read_pool_state(pool_address, chain)
    
    current_price = prices.get("AVAX", {}).get("price_usd", 0)
    if current_price == 0:
        current_price = pool.get("price_native", 0)
    
    if current_price == 0:
        return {"error": "Could not fetch current price"}
    
    # Calculate IL
    il_data = calculate_il(
        entry_price=entry_price,
        current_price=current_price,
        range_low=range_low,
        range_high=range_high,
        initial_value_usd=initial_value_usd,
        shape=shape,
    )
    
    # Build report
    report = {
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
        "recommendation": _get_recommendation(il_data),
    }
    
    return report


def _get_recommendation(il_data: dict) -> str:
    """Generate rebalance recommendation based on position data."""
    if il_data.get("error"):
        return "Insufficient data for recommendation"
    
    in_range = il_data.get("in_range", False)
    dist_to_low = il_data.get("distance_to_low_pct", 0)
    dist_to_high = il_data.get("distance_to_high_pct", 0)
    
    if in_range:
        if dist_to_low < 1.0:
            return "WARNING: Price near lower bound. Consider widening range or rebalancing down."
        elif dist_to_high < 1.0:
            return "WARNING: Price near upper bound. Consider widening range or rebalancing up."
        else:
            return "Position healthy. No immediate action needed."
    else:
        current = il_data.get("current_price", 0)
        range_low = il_data.get("range_low", 0)
        range_high = il_data.get("range_high", 0)
        
        if current < range_low:
            new_low = round(current * 0.97, 2)
            new_high = round(current * 1.03, 2)
            return f"OUT OF RANGE (below). Rebalance suggested: {new_low}–{new_high} (±3% around ${current})"
        else:
            new_low = round(current * 0.97, 2)
            new_high = round(current * 1.03, 2)
            return f"OUT OF RANGE (above). Rebalance suggested: {new_low}–{new_high} (±3% around ${current})"


# ── Main: Swarms Agent Setup ──────────────────────────────────────────────

def create_agent(model_name: str = None, api_key: str = None):
    """
    Create the LP Monitor agent with specified model.
    
    Args:
        model_name: LiteLLM model identifier (e.g., "openrouter/google/gemini-2.0-flash-001")
        api_key: API key for the model provider
    """
    from swarms import Agent
    
    # Resolve model: env var > parameter > default
    if not model_name:
        model_name = os.getenv("LP_MONITOR_MODEL", "openrouter/google/gemini-2.0-flash-001")
    
    # Resolve API key: env var > parameter
    if not api_key:
        # For OpenRouter, check OPENROUTER_API_KEY
        if "openrouter" in model_name.lower():
            api_key = os.getenv("OPENROUTER_API_KEY")
        else:
            api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("ERROR: No API key found. Set OPENROUTER_API_KEY or OPENAI_API_KEY.")
        print("For OpenRouter: export OPENROUTER_API_KEY=your_key")
        print("For OpenAI: export OPENAI_API_KEY=your_key")
        exit(1)
    
    # Set the key in env for LiteLLM
    if "openrouter" in model_name.lower():
        os.environ["OPENROUTER_API_KEY"] = api_key
    else:
        os.environ["OPENAI_API_KEY"] = api_key
    
    lp_agent = Agent(
        agent_name="DeFi LP Monitor",
        agent_description="Monitors concentrated liquidity LP positions with IL tracking, efficiency scoring, and rebalance alerts. Supports LFJ (Avalanche), Uniswap V3 (Ethereum/Base), and other CL protocols.",
        system_prompt="""You are a DeFi LP Position Monitor. You help liquidity providers track their concentrated liquidity positions.

When a user asks about their LP position, use the available tools to:
1. Fetch current token prices
2. Read pool state data
3. Calculate impermanent loss
4. Generate a complete position report

Always provide:
- Current price vs range position
- Impermanent loss calculation
- Fee efficiency status
- Clear rebalance recommendation if needed

Be concise and actionable. Focus on numbers and decisions, not fluff.""",
        model_name=model_name,
        tools=[fetch_token_prices, read_pool_state, calculate_il, lp_position_report],
        max_loops="auto",
        temperature=0.3,
        max_tokens=4096,
    )
    
    return lp_agent


if __name__ == "__main__":
    import sys
    
    # Allow model override via CLI arg
    model = sys.argv[1] if len(sys.argv) > 1 else None
    
    lp_agent = create_agent(model_name=model)
    
    print("LP Monitor Agent created successfully!")
    print(f"Agent name: {lp_agent.agent_name}")
    print(f"Model: {lp_agent.model_name}")
    print(f"Tools: {len(lp_agent.tools)}")
    
    # Test with a simple query
    print("\n--- Test Run ---")
    result = lp_agent.run("Check my AVAX/USDC LP position. Range: $10.15-$10.38, entry price: $9.95, initial value: $134.94, shape: curve.")
    print(result)
