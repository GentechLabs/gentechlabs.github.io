"""Crypto Price API — Real-time crypto prices.

Fixed (Aug 3): was returning hardcoded placeholder price:0.0.
Now uses a CMC → CoinGecko fallback chain (see crypto-price-fetch skill).
Binance is geo-blocked from the VPS (HTTP 451), so it's not in the chain.
"""
import json
import os
import re
import time
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import urllib.request

app = FastAPI(title="Crypto Price API", version="1.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

TIMEOUT = 12


def _load_cmc_key() -> Optional[str]:
    """Load CMC API key from env or the config file used by GTA scripts."""
    key = os.environ.get("COINMARKETCAP_API_KEY") or os.environ.get("CMC_API_KEY")
    if key:
        return key
    for path in ("/root/.hermes/scripts/cmc_config.json", "/root/vaults/gentech/HQ/config/cmc-api-key.env"):
        try:
            with open(path) as f:
                if path.endswith(".json"):
                    d = json.load(f)
                    return d.get("coinmarketcap_api_key") or d.get("api_key") or next(iter(d.values()))
                # .env style
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        k, _, v = line.partition("=")
                        if "KEY" in k.upper():
                            return v.strip().strip('"').strip("'")
        except Exception:
            continue
    return None


# CoinGecko ID map (from crypto-price-fetch skill — IDs are inconsistent, maintain explicitly)
_COINGECKO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "AVAX": "avalanche-2",
    "MATIC": "matic-network", "LINK": "chainlink", "UNI": "uniswap", "AAVE": "aave",
    "ARB": "arbitrum", "OP": "optimism", "JOE": "joe", "USDC": "usd-coin",
    "USDT": "tether", "DAI": "dai", "PENGU": "pudgy-penguins", "PEPE": "pepe",
    "WIF": "dogwifcoin", "BONK": "bonk", "FET": "fetch-ai", "RENDER": "render-token",
    "TIA": "celestia", "SEI": "sei-network", "SUI": "sui", "XRP": "ripple",
    "ADA": "cardano", "DOT": "polkadot", "DOGE": "dogecoin", "BNB": "binancecoin",
}
_STABLECOINS = {"USDC", "USDT", "DAI", "USDE", "FDUSD", "PYUSD", "TUSD"}


def _fetch_cmc(symbol: str, key: str) -> Optional[float]:
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&convert=USD"
    req = urllib.request.Request(url, headers={"X-CMC_PRO_API_KEY": key, "Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        d = json.loads(resp.read())
    quote = d.get("data", {}).get(symbol, {})
    return float(quote.get("quote", {}).get("USD", {}).get("price")) if quote else None


def _fetch_coingecko(symbol: str) -> Optional[float]:
    if symbol in _STABLECOINS:
        return 1.00
    cg_id = _COINGECKO_IDS.get(symbol, symbol.lower())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        d = json.loads(resp.read())
    val = d.get(cg_id, {}).get("usd")
    return float(val) if val else None


def _get_price(symbol: str) -> dict:
    sym = symbol.upper()
    price = None
    source = None

    # Primary: CMC
    key = _load_cmc_key()
    if key:
        try:
            p = _fetch_cmc(sym, key)
            if p:
                price, source = p, "coinmarketcap"
        except Exception:
            pass

    # Fallback: CoinGecko
    if price is None:
        try:
            p = _fetch_coingecko(sym)
            if p:
                price, source = p, "coingecko"
        except Exception:
            pass

    # Stablecoin final fallback
    if price is None and sym in _STABLECOINS:
        price, source = 1.00, "peg"

    if price is None:
        return {"symbol": sym, "price": None, "source": None, "error": f"no data source returned a price for {sym}"}

    return {"symbol": sym, "price": price, "source": source}


@app.get("/v1/health")
async def health():
    return {"status": "ok", "version": "1.1.0", "service": "crypto-price"}


@app.get("/v1/price/{symbol}")
async def price(symbol: str):
    return _get_price(symbol)


@app.get("/v1/prices")
async def prices(symbols: str):
    """Batch price lookup — comma-separated symbols. e.g. ?symbols=BTC,ETH,SOL"""
    out = {"prices": []}
    for sym in symbols.split(","):
        sym = sym.strip()
        if sym:
            out["prices"].append(_get_price(sym))
    return out
