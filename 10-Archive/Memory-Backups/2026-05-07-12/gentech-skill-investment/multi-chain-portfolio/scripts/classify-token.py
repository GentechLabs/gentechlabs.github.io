#!/usr/bin/env python3
"""
Token Classification — Multi-Channel Data Fetcher
Given a token symbol, fetches:
- Chain(s) and contract addresses
- TVL and volume
- Classification (Core / RWA / Cycle based on thresholds)
Outputs JSON for downstream portfolio decisions.

Usage:
  python3 classify-token.py PROPS
  python3 classify-token.py LAND
  python3 classify-token.py SOL

Environment:
  Requires CMC API key at ~/.hermes/scripts/cmc_config.json
  Format: {"coinmarketcap_api_key": "YOUR_KEY"}
"""

import json
import os
import sys
import time
import urllib.request

CONFIG_PATH = os.path.expanduser("~/.hermes/scripts/cmc_config.json")
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.token-classify-cache.json")
CACHE_TTL = 3600  # 1 hour

# Thresholds for classification
THRESHOLDS = {
    "core_tvl_usd": 5_000_000,      # > $5M TVL → Core
    "rwa_tvl_usd_min": 1_000_000,   # $1–5M → RWA
    "rwa_tvl_usd_max": 5_000_000,
    "cycle_tvl_usd_max": 1_000_000, # < $1M → spot-only / avoid LP
    "healthy_volume_min": 100_000,  # Minimum 24h volume to consider LP
}

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

def fetch_cmc_info(symbol, api_key):
    """Get token info: chains, contracts, basic data."""
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/info?symbol={symbol}"
    req = urllib.request.Request(url, headers={'X-CMC_PRO_API_KEY': api_key})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

def fetch_cmc_quotes(symbol, api_key):
    """Get price, volume, market cap, TVL."""
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&convert=USD"
    req = urllib.request.Request(url, headers={'X-CMC_PRO_API_KEY': api_key})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

def classify(tvl, volume_24h):
    """Return bucket based on liquidity metrics."""
    if tvl >= THRESHOLDS["core_tvl_usd"]:
        return "Core DeFi"
    elif THRESHOLDS["rwa_tvl_usd_min"] <= tvl < THRESHOLDS["rwa_tvl_usd_max"]:
        return "RWA / Thesis"
    elif tvl < THRESHOLDS["cycle_tvl_usd_max"]:
        return "Speculative / Cycle Adjacent"
    else:
        return "Unknown"

def extract_tvl_from_quotes(data, symbol):
    """CMC doesn't directly return TVL in quotes; infer from platform data or use 0 if unavailable."""
    # For now, return 0; TVL often comes from DeFiLlama or separate endpoint
    # Caller may need DeFiLlama: https://api.llama.fi/tvl/{slug}
    return 0

def main():
    if len(sys.argv) != 2:
        print("Usage: classify-token.py SYMBOL")
        sys.exit(1)
    symbol = sys.argv[1].upper()

    cfg = load_config()
    api_key = cfg["coinmarketcap_api_key"]

    # Cache check
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            cache = json.load(f)
        if symbol in cache and time.time() - cache[symbol]["ts"] < CACHE_TTL:
            print(f"✅ Cached result for {symbol}: {json.dumps(cache[symbol]['result'], indent=2)}")
            sys.exit(0)

    # Fetch
    try:
        info = fetch_cmc_info(symbol, api_key)
        quotes = fetch_cmc_quotes(symbol, api_key)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("⏳ Rate limited — try again in 30s")
            sys.exit(1)
        raise

    data = quotes["data"][symbol]
    quote = data["quote"]["USD"]

    # Extract platform info (chains)
    platform = info["data"][symbol].get("platform", {})
    chains = []
    if isinstance(platform, dict):
        chains.append({
            "chain": platform.get("name", "Unknown"),
            "address": platform.get("token_address", "N/A")
        })
    else:
        # Some tokens show contract_address array
        contracts = info["data"][symbol].get("contract_address", [])
        for c in contracts:
            chains.append({
                "chain": c.get("platform", {}).get("name", "Unknown"),
                "address": c.get("contract_address", "N/A")
            })

    # Classify (TVL currently 0 — placeholder)
    tvl = extract_tvl_from_quotes(quotes, symbol)  # TODO: add DeFiLlama call
    volume = quote["volume_24h"]
    bucket = classify(tvl, volume)

    result = {
        "symbol": symbol,
        "name": data["name"],
        "price_usd": quote["price"],
        "volume_24h_usd": volume,
        "market_cap_usd": quote["market_cap"],
        "tvl_usd": tvl,  # Filled via DeFiLlama in v2
        "classification": bucket,
        "chains": chains,
        "lp_viable": volume >= THRESHOLDS["healthy_volume_min"] and tvl >= THRESHOLDS["rwa_tvl_usd_min"],
        "source": "cmc_pro_api",
        "timestamp": time.time()
    }

    # Cache
    cache = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            cache = json.load(f)
    cache[symbol] = {"ts": time.time(), "result": result}
    with open(STATE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
