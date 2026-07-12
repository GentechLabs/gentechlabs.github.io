#!/usr/bin/env python3
"""
Birdeye x402 Client — Pay-per-request market data for AI agents.
Uses HTTP 402 payment protocol (USDC on Solana) or traditional API key.

Endpoints used:
  - /defi/v3/token/overview      — token metadata, price, liquidity
  - /defi/v3/token/security      — security score, holder distribution
  - /defi/v3/token/trade-data    — volume, txns, buy/sell pressure
  - /v2/tokens/new_listing       — new token launches (for radar)
  - /defi/v3/token/trending      — trending tokens
"""

import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import urlencode

import httpx

# ── Config ──────────────────────────────────────────────────────────────────
BASE_URL = "https://public-api.birdeye.so"
MCP_URL = "https://mcp.birdeye.so/mcp"
CONFIG_PATH = os.path.expanduser("~/.hermes/scripts/birdeye-config.json")

# Known token addresses (Solana)
TOKENS = {
    "SOL":  "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "WIF":  "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
}

# Chains supported by Birdeye
CHAINS = ["solana", "base", "bsc", "avalanche", "ethereum"]


@dataclass
class BirdeyeConfig:
    """Runtime config — loaded from birdeye-config.json."""
    api_key: str = ""
    chain: str = "solana"
    payment_mode: str = "api_key"  # "api_key" or "x402"
    x402_wallet: str = ""         # Solana wallet for x402 payments
    cache_ttl: int = 60           # seconds
    _cache: dict = field(default_factory=dict, repr=False)

    @classmethod
    def load(cls) -> "BirdeyeConfig":
        """Load config from disk, fall back to env vars."""
        # Try file first
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                data = json.load(f)
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

        # Fall back to env
        api_key = os.environ.get("BIRDEYE_API_KEY", "")
        return cls(api_key=api_key)

    def save(self):
        """Persist config to disk."""
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        data = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)

    @property
    def is_configured(self) -> bool:
        if self.payment_mode == "x402":
            return bool(self.x402_wallet)
        return bool(self.api_key)


class BirdeyeClient:
    """Birdeye API client with x402 and API key support."""

    def __init__(self, config: Optional[BirdeyeConfig] = None):
        self.config = config or BirdeyeConfig.load()
        self._client = httpx.Client(
            base_url=BASE_URL,
            timeout=15,
            headers=self._build_headers(),
        )

    def _build_headers(self) -> dict:
        h = {"User-Agent": "Gentech-Labs/Birdeye-Phase1"}
        if self.config.api_key:
            h["X-API-KEY"] = self.config.api_key
        if self.config.payment_mode == "x402":
            h["x402-payment"] = "true"
        return h

    def _get(self, path: str, params: dict = None) -> dict:
        """GET with caching and error handling."""
        cache_key = f"{path}?{urlencode(params or {})}"

        # Check cache
        cached = self.config._cache.get(cache_key)
        if cached and (time.time() - cached["ts"]) < self.config.cache_ttl:
            return cached["data"]

        try:
            resp = self._client.get(path, params=params)
            resp.raise_for_status()
            data = resp.json().get("data", resp.json())

            # Cache it
            self.config._cache[cache_key] = {"data": data, "ts": time.time()}
            return data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 402:
                return {"error": "PAYMENT_REQUIRED", "detail": "x402 payment needed — configure wallet or use API key"}
            elif e.response.status_code == 429:
                return {"error": "RATE_LIMITED", "detail": "Back off — Birdeye rate limit hit"}
            return {"error": f"HTTP_{e.response.status_code}", "detail": str(e)}
        except Exception as e:
            return {"error": "NETWORK_ERROR", "detail": str(e)}

    # ── Token Data ──────────────────────────────────────────────────────

    def token_overview(self, address: str, chain: str = None) -> dict:
        """Get token overview — price, liquidity, volume, metadata."""
        return self._get("/defi/v3/token/overview", {
            "address": address,
            "chain": chain or self.config.chain,
        })

    def token_security(self, address: str, chain: str = None) -> dict:
        """Get security analysis — score, holder distribution, risks."""
        return self._get("/defi/v3/token/security", {
            "address": address,
            "chain": chain or self.config.chain,
        })

    def token_trade_data(self, address: str, chain: str = None) -> dict:
        """Get trade data — volume, buy/sell counts, unique traders."""
        return self._get("/defi/v3/token/trade-data", {
            "address": address,
            "chain": chain or self.config.chain,
        })

    def new_listings(self, chain: str = None, limit: int = 20) -> dict:
        """Get recently listed tokens."""
        return self._get("/v2/tokens/new_listing", {
            "chain": chain or self.config.chain,
            "limit": limit,
        })

    def trending_tokens(self, chain: str = None, limit: int = 20) -> dict:
        """Get trending tokens by volume/activity."""
        return self._get("/defi/v3/token/trending", {
            "chain": chain or self.config.chain,
            "limit": limit,
        })

    # ── Aggregated Analysis ─────────────────────────────────────────────

    def full_token_report(self, address: str, chain: str = None) -> dict:
        """Aggregate overview + security + trade data into one report."""
        chain = chain or self.config.chain
        overview = self.token_overview(address, chain)
        security = self.token_security(address, chain)
        trades = self.token_trade_data(address, chain)

        # Check for errors
        errors = [v["error"] for v in [overview, security, trades] if isinstance(v, dict) and "error" in v]
        if errors:
            return {"error": "PARTIAL_FAILURE", "details": errors}

        return {
            "address": address,
            "chain": chain,
            "overview": overview,
            "security": security,
            "trades": trades,
            "fetched_at": time.time(),
        }

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    """Quick CLI for testing Birdeye endpoints."""
    import argparse
    parser = argparse.ArgumentParser(description="Birdeye x402 Client")
    parser.add_argument("command", choices=["overview", "security", "trades", "trending", "new", "report", "config"],
                        help="Command to run")
    parser.add_argument("--token", "-t", help="Token address or symbol (SOL, USDC, BONK, WIF)")
    parser.add_argument("--chain", "-c", default="solana", help="Chain (default: solana)")
    parser.add_argument("--limit", "-n", type=int, default=10, help="Limit for listing queries")
    parser.add_argument("--json", "-j", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    # Resolve token symbol → address
    token = args.token
    if token and token.upper() in TOKENS:
        token = TOKENS[token.upper()]

    config = BirdeyeConfig.load()

    if args.command == "config":
        print(f"API Key: {'set (' + config.api_key[:8] + '...)' if config.api_key else 'NOT SET'}")
        print(f"Chain: {config.chain}")
        print(f"Payment Mode: {config.payment_mode}")
        print(f"Config Path: {CONFIG_PATH}")
        sys.exit(0)

    if not config.is_configured:
        print("ERROR: No Birdeye API key or x402 wallet configured.", file=sys.stderr)
        print(f"  Option 1: Set BIRDEYE_API_KEY env var", file=sys.stderr)
        print(f"  Option 2: Create {CONFIG_PATH}", file=sys.stderr)
        print(f"  Option 3: Register at https://bds.birdeye.so", file=sys.stderr)
        sys.exit(1)

    with BirdeyeClient(config) as client:
        if args.command == "overview":
            data = client.token_overview(token, args.chain)
        elif args.command == "security":
            data = client.token_security(token, args.chain)
        elif args.command == "trades":
            data = client.token_trade_data(token, args.chain)
        elif args.command == "trending":
            data = client.trending_tokens(args.chain, args.limit)
        elif args.command == "new":
            data = client.new_listings(args.chain, args.limit)
        elif args.command == "report":
            if not token:
                print("ERROR: --token required for report", file=sys.stderr)
                sys.exit(1)
            data = client.full_token_report(token, args.chain)
        else:
            data = {"error": "UNKNOWN_COMMAND"}

        if args.json:
            print(json.dumps(data, indent=2, default=str))
        else:
            if "error" in data:
                print(f"❌ {data['error']}: {data.get('detail', 'unknown')}", file=sys.stderr)
                sys.exit(1)
            print(json.dumps(data, indent=2, default=str))


if __name__ == "__main__":
    main()
