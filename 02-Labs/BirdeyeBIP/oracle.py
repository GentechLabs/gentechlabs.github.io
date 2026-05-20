"""
Birdeye Oracle — Feeds Birdeye market data on-chain via x402 pay-per-request
Part of the AAE (Agent Economy) BirdeyeAdapter BIP submission

Usage:
    python oracle.py --rpc <RPC_URL> --adapter <ADAPTER_ADDRESS> --key <PRIVATE_KEY>

Flow:
    1. Poll Birdeye x402 API for token data (price, volume, liquidity)
    2. Encode data for on-chain push
    3. Call BirdeyeAdapter.pushTokenData() or processData()
    4. Monitor for LPRangeBreached events → alert

Birdeye x402: $0.003/request, USDC on Base or Solana
"""

import json
import time
import hashlib
import argparse
from typing import Optional

try:
    import requests
except ImportError:
    print("pip install requests web3")
    exit(1)

try:
    from web3 import Web3
except ImportError:
    print("pip install web3")
    exit(1)


# ═══════════════════════════════════════════
#              BIRDEYE x402 CLIENT
# ═══════════════════════════════════════════

class BirdeyeClient:
    """Client for Birdeye Data Services x402 pay-per-request API."""

    BASE_URL = "https://public-api.birdeye.so"

    # Solana token addresses → names
    WATCHLIST = {
        "So11111111111111111111111111111111111111112": {"symbol": "SOL", "decimals": 9},
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": {"symbol": "USDC", "decimals": 6},
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": {"symbol": "USDT", "decimals": 6},
        "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs": {"symbol": "ETH", "decimals": 8},
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": {"symbol": "BONK", "decimals": 5},
        "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3": {"symbol": "PYTH", "decimals": 6},
    }

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.cost_per_request = 0.003  # USD
        self.total_cost = 0.0
        self.request_count = 0

    def _headers(self) -> dict:
        headers = {
            "accept": "application/json",
            "x-chain": "solana",
        }
        if self.api_key:
            headers["X-API-KEY"] = self.api_key
        return headers

    def _request(self, endpoint: str, params: dict = None) -> dict:
        """Make API request with cost tracking."""
        url = f"{self.BASE_URL}{endpoint}"
        resp = self.session.get(url, headers=self._headers(), params=params, timeout=10)
        self.request_count += 1
        self.total_cost += self.cost_per_request

        if resp.status_code == 402:
            print(f"[402] Payment required — x402 flow needed for {endpoint}")
            # In production: handle x402 payment via USDC on Base/Solana
            # For now: log and retry with API key
            return {"error": "payment_required", "status": 402}

        resp.raise_for_status()
        return resp.json()

    def get_token_price(self, address: str) -> dict:
        """Get single token price."""
        return self._request("/defi/price", {"address": address})

    def get_multi_price(self, addresses: list[str]) -> dict:
        """Get prices for multiple tokens in one call (cost-efficient)."""
        return self._request("/defi/multi_price", {"list_address": ",".join(addresses)})

    def get_token_overview(self, address: str) -> dict:
        """Get full token overview: price, volume, liquidity, market cap."""
        return self._request("/defi/token_overview", {"address": address})

    def get_token_security(self, address: str) -> dict:
        """Get token security info (top holders, freeze authority, etc.)."""
        return self._request("/defi/token_security", {"address": address})

    def get_ohlcv(self, address: str, timeframe: str = "1H") -> dict:
        """Get OHLCV candle data."""
        return self._request("/defi/ohlcv", {
            "address": address,
            "type": timeframe,
            "time_from": int(time.time()) - 86400,  # Last 24h
        })

    def get_all_watchlist_data(self) -> list[dict]:
        """Batch-fetch all watchlist tokens. Most cost-efficient approach."""
        addresses = list(self.WATCHLIST.keys())

        # Multi-price: 1 request for all tokens
        multi = self.get_multi_price(addresses)

        results = []
        if "data" in multi:
            for addr, data in multi["data"].items():
                info = self.WATCHLIST.get(addr, {})
                results.append({
                    "address": addr,
                    "symbol": info.get("symbol", "???"),
                    "decimals": info.get("decimals", 8),
                    "price": data.get("value", 0),
                    "price_change_24h": data.get("priceChange24h", 0),
                    "volume_24h": data.get("volume24h", 0),
                    "liquidity": data.get("liquidity", 0),
                    "updated_at": int(time.time()),
                })

        print(f"[Birdeye] {self.request_count} requests, ${self.total_cost:.4f} total cost")
        return results


# ═══════════════════════════════════════════
#              ON-CHAIN PUSHER
# ═══════════════════════════════════════════

# BirdeyeAdapter ABI (minimal — just the functions we need)
ADAPTER_ABI = json.loads("""[
    {
        "name": "pushTokenData",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "_token", "type": "address"},
            {"name": "_price", "type": "uint256"},
            {"name": "_volume24h", "type": "uint256"},
            {"name": "_liquidity", "type": "uint256"}
        ],
        "outputs": []
    },
    {
        "name": "totalDataPushes",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"type": "uint256"}]
    },
    {
        "name": "totalBreachesDetected",
        "type": "function",
        "stateMutability": "view",
        "inputs": [],
        "outputs": [{"type": "uint256"}]
    },
    {
        "anonymous": false,
        "name": "TokenDataUpdated",
        "type": "event",
        "inputs": [
            {"indexed": true, "name": "token", "type": "address"},
            {"indexed": false, "name": "price", "type": "uint256"},
            {"indexed": false, "name": "volume24h", "type": "uint256"},
            {"indexed": false, "name": "liquidity", "type": "uint256"},
            {"indexed": false, "name": "timestamp", "type": "uint256"}
        ]
    },
    {
        "anonymous": false,
        "name": "LPRangeBreached",
        "type": "event",
        "inputs": [
            {"indexed": true, "name": "agent", "type": "address"},
            {"indexed": true, "name": "token", "type": "address"},
            {"indexed": false, "name": "currentPrice", "type": "uint256"},
            {"indexed": false, "name": "lowerBound", "type": "uint256"},
            {"indexed": false, "name": "upperBound", "type": "uint256"}
        ]
    }
]""")


def solana_to_evm(solana_addr: str) -> str:
    """Map Solana base58 address to EVM address for on-chain storage.

    Uses first 20 bytes of SHA-256 hash — deterministic, reversible via mapping.
    """
    digest = hashlib.sha256(solana_addr.encode()).digest()
    return Web3.to_checksum_address("0x" + digest[:20].hex())


def push_data_onchain(
    w3: Web3,
    adapter_address: str,
    private_key: str,
    token_data: list[dict],
):
    """Push Birdeye token data to BirdeyeAdapter on-chain."""
    account = w3.eth.account.from_key(private_key)
    adapter = w3.eth.contract(
        address=Web3.to_checksum_address(adapter_address),
        abi=ADAPTER_ABI,
    )

    for token in token_data:
        evm_addr = solana_to_evm(token["address"])
        price = int(token["price"] * 1e8)           # 8 decimals
        volume = int(token.get("volume_24h", 0) * 1e8)
        liquidity = int(token.get("liquidity", 0) * 1e8)

        print(f"  Pushing {token['symbol']}: ${token['price']:.2f}")

        tx = adapter.functions.pushTokenData(
            evm_addr,
            price,
            volume,
            liquidity,
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 150_000,
            "maxFeePerGas": w3.eth.gas_price * 2,
            "maxPriorityFeePerGas": w3.eth.gas_price,
        })

        signed = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"    tx: {receipt.transactionHash.hex()[:18]}... status={receipt['status']}")


# ═══════════════════════════════════════════
#              MAIN LOOP
# ═══════════════════════════════════════════

def run_oracle(args):
    """Main oracle loop: poll Birdeye → push on-chain → repeat."""
    client = BirdeyeClient(api_key=args.api_key)
    w3 = Web3(Web3.HTTPProvider(args.rpc)) if args.rpc else None

    if w3 and not w3.is_connected():
        print(f"[ERROR] Cannot connect to {args.rpc}")
        return

    print(f"""
╔══════════════════════════════════════════╗
║     🦉 Birdeye Oracle — AAE Adapter     ║
╠══════════════════════════════════════════╣
║  Interval:  {args.interval}s                     
║  Watchlist: {len(client.WATCHLIST)} tokens                   
║  Chain:     {'solana → EVM' if w3 else 'data-only (no chain)'}        
║  x402 cost: $0.003/request               
╚══════════════════════════════════════════╝
    """)

    while True:
        try:
            print(f"\n[{time.strftime('%H:%M:%S')}] Fetching Birdeye data...")
            data = client.get_all_watchlist_data()

            for token in data:
                symbol = token["symbol"]
                price = token["price"]
                change = token.get("price_change_24h", 0)
                arrow = "🔴" if change < 0 else "🟢"
                print(f"  {arrow} {symbol}: ${price:,.2f} ({change:+.1f}% 24h)")

            if w3 and args.adapter and args.key:
                print("\n  Pushing to chain...")
                push_data_onchain(w3, args.adapter, args.key, data)

            print(f"\n  💰 Cumulative cost: ${client.total_cost:.4f} ({client.request_count} requests)")

        except Exception as e:
            print(f"  [ERROR] {e}")

        time.sleep(args.interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Birdeye Oracle for AAE BirdeyeAdapter")
    parser.add_argument("--rpc", help="EVM RPC URL (optional — skip for data-only mode)")
    parser.add_argument("--adapter", help="BirdeyeAdapter contract address")
    parser.add_argument("--key", help="Private key for on-chain transactions")
    parser.add_argument("--api-key", help="Birdeye API key (optional for x402)")
    parser.add_argument("--interval", type=int, default=60, help="Poll interval in seconds")
    args = parser.parse_args()

    run_oracle(args)
