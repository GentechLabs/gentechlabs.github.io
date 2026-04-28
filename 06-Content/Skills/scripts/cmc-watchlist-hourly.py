#!/usr/bin/env python3
"""
Crypto Watchlist — Hourly Price Monitor
Fetches prices via CMC, compares to last check, outputs only if meaningful movement.
Designed to be run by cron agent via script= parameter.
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

# Config
CMC_CONFIG = "/root/.hermes/scripts/cmc_config.json"
STATE_FILE = os.path.expanduser("~/.hermes/scripts/.cmc-watchlist-hourly-state.json")
MOVEMENT_THRESHOLD = 1.5  # % change to trigger report

# Watchlist from vault config
COINS = [
    {"symbol": "BTC",  "cmc_id": "1"},
    {"symbol": "SOL",  "cmc_id": "5426"},
    {"symbol": "LINK", "cmc_id": "1975"},
    {"symbol": "AVAX", "cmc_id": "5805"},
    {"symbol": "TAO",  "cmc_id": "22974"},
    {"symbol": "XAUt", "cmc_id": "5176"},
    {"symbol": "BEAM", "cmc_id": "28298"},
]

# CoinGecko fallback IDs
CG_IDS = {
    "BTC": "bitcoin", "SOL": "solana", "LINK": "chainlink",
    "AVAX": "avalanche-2", "TAO": "bittensor", "XAUt": "tether-gold",
    "BEAM": "beam-2",
}


def load_cmc_key():
    if os.path.exists(CMC_CONFIG):
        with open(CMC_CONFIG) as f:
            return json.load(f).get("coinmarketcap_api_key", "")
    return os.environ.get("CMC_API_KEY", "")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_prices": {}, "last_run": None}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_cmc(api_key):
    ids = ",".join(c["cmc_id"] for c in COINS)
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?id={ids}&convert=USD"
    req = urllib.request.Request(url, headers={"X-CMC_PRO_API_KEY": api_key})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_coingecko():
    ids = ",".join(CG_IDS.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def format_price(symbol, price):
    if price >= 1000:
        return f"${price:,.0f}"
    elif price >= 1:
        return f"${price:.2f}"
    elif price >= 0.01:
        return f"${price:.4f}"
    else:
        return f"${price:.6f}"


def main():
    state = load_state()
    last_prices = state.get("last_prices", {})
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%Y-%m-%d %H:%M UTC")

    # Try CMC first, fallback to CoinGecko
    prices = {}
    source = ""
    api_key = load_cmc_key()

    if api_key:
        try:
            data = fetch_cmc(api_key)
            for coin in COINS:
                q = data.get("data", {}).get(coin["cmc_id"], {}).get("quote", {}).get("USD", {})
                if q:
                    prices[coin["symbol"]] = {
                        "price": q.get("price", 0),
                        "change_1h": q.get("percent_change_1h", 0),
                        "change_24h": q.get("percent_change_24h", 0),
                        "change_7d": q.get("percent_change_7d", 0),
                        "volume_24h": q.get("volume_24h", 0),
                        "market_cap": q.get("market_cap", 0),
                    }
            source = "CMC"
        except Exception as e:
            print(f"CMC error: {e}", file=sys.stderr)

    if not prices:
        try:
            data = fetch_coingecko()
            for coin in COINS:
                cg_id = CG_IDS.get(coin["symbol"], coin["symbol"].lower())
                if cg_id in data:
                    d = data[cg_id]
                    prices[coin["symbol"]] = {
                        "price": d.get("usd", 0),
                        "change_1h": 0,
                        "change_24h": d.get("usd_24h_change", 0),
                        "change_7d": 0,
                        "volume_24h": 0,
                        "market_cap": 0,
                    }
            source = "CoinGecko"
        except Exception as e:
            print(json.dumps({"error": f"All APIs failed: {e}", "time": now_str}))
            return

    if not prices:
        print(json.dumps({"error": "No price data retrieved", "time": now_str}))
        return

    # Calculate movement since last check
    max_change = 0
    movements = {}
    for sym, data in prices.items():
        prev = last_prices.get(sym, {}).get("price", 0)
        if prev > 0:
            pct = abs((data["price"] - prev) / prev) * 100
            movements[sym] = round(pct, 2)
            max_change = max(max_change, pct)
        else:
            movements[sym] = 0

    # Save state
    state["last_prices"] = {sym: {"price": d["price"]} for sym, d in prices.items()}
    state["last_run"] = now_str
    save_state(state)

    # Determine if we should report
    significant = max_change >= MOVEMENT_THRESHOLD

    # Build output
    output = {
        "time": now_str,
        "source": source,
        "significant_movement": significant,
        "max_change_since_last": f"{max_change:.2f}%",
        "threshold": f"{MOVEMENT_THRESHOLD}%",
        "coins": {},
    }

    for coin in COINS:
        sym = coin["symbol"]
        if sym in prices:
            d = prices[sym]
            output["coins"][sym] = {
                "price": format_price(sym, d["price"]),
                "change_1h": f"{d['change_1h']:+.2f}%",
                "change_24h": f"{d['change_24h']:+.2f}%",
                "movement_since_last": f"{movements.get(sym, 0):.2f}%",
            }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
