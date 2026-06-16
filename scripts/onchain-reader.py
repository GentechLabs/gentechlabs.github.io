#!/usr/bin/env python3
"""
On-Chain Position Reader
Reads live wallet + LP position data directly from blockchain RPC.
No MetaMask, no browser, no API keys — just public RPC + DexScreener.

Supports: LFJ (Trader Joe V2), extensible to Uniswap V3, Pangolin, etc.
Part of the GenTech Agent Kit — universal LP position template.
"""

import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

# ============================================================
# CONFIG — Set these for your position
# ============================================================

# Wallet to track (your MetaMask/public address)
WALLET = "0xYOUR_WALLET_ADDRESS"

# Chain RPC endpoints (free, no API key needed)
RPC_ENDPOINTS = {
    "avalanche": "https://api.avax.network/ext/bc/C/rpc",
    "base": "https://mainnet.base.org",
    "ethereum": "https://eth.llamarpc.com",
    "arbitrum": "https://arb1.arbitrum.io/rpc",
    "polygon": "https://polygon-rpc.com",
}

# Known token addresses (native = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE")
TOKENS = {
    "avalanche": {
        "WAVAX": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
        "USDC": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
        "USDC_e": "0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664",
        "USDT_e": "0xc719843557BEdA5456c80dBaE72586d552Ed731f",
    },
    "base": {
        "WETH": "0x4200000000000000000000000000000000000006",
        "USDC": "0x8335893CD6466cDe5427913FcB20460e08aBa077",
    },
}

# DEX configurations
DEX_CONFIGS = {
    "lfj": {
        "name": "LFJ (Trader Joe V2)",
        "chain": "avalanche",
        "pool_address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
        "dexscreener_chain": "avalanche",
        "tokenX": "WAVAX",
        "tokenY": "USDC",
        # ABI function selectors (4-byte)
        "getActiveId": "0x80afabfa",  # getActiveId()
        "getBin": "0x4f019328",       # getBin(uint24)
        "getReserves": "0x0902f1ac",  # getReserves()
    },
    "uniswap_v3": {
        "name": "Uniswap V3",
        "chain": "ethereum",
        "nft_manager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
        "dexscreener_chain": "ethereum",
        "factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
    },
    "pangolin": {
        "name": "Pangolin V2",
        "chain": "avalanche",
        "dexscreener_chain": "avalanche",
    },
}

# Output
DATA_PATH = "/root/vaults/gentech/defi-data.json"

# Milestones (from existing config)
MILESTONES = {
    "Scout": 5,
    "Raider": 20,
    "Warlord": 55,
    "Fisher": 100,
    "Sovereign": 200,
}


# ============================================================
# RPC HELPERS
# ============================================================

def rpc_call(chain, method, params=None):
    """Make a JSON-RPC call to a chain endpoint."""
    url = RPC_ENDPOINTS.get(chain)
    if not url:
        raise ValueError(f"No RPC endpoint for chain: {chain}")

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or [],
    }

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "GenTech/1.0"},
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
        if "error" in result:
            raise Exception(f"RPC error: {result['error']}")
        return result.get("result")


def eth_call(chain, to, data):
    """Execute eth_call on chain."""
    return rpc_call(chain, "eth_call", [{"to": to, "data": data}, "latest"])


def get_erc20_balance(chain, token_address, wallet):
    """Get ERC-20 balance for a wallet. Returns raw amount (needs decimals)."""
    # balanceOf(address) selector: 0x70a08231
    padded_wallet = wallet.lower().replace("0x", "").zfill(64)
    result = eth_call(chain, token_address, f"0x70a08231{padded_wallet}")
    if result and result != "0x":
        return int(result, 16)
    return 0


def get_native_balance(chain, wallet):
    """Get native token (ETH/AVAX) balance."""
    result = rpc_call(chain, "eth_getBalance", [wallet, "latest"])
    if result:
        return int(result, 16)
    return 0


# ============================================================
# PRICE DATA (DexScreener - Free)
# ============================================================

def fetch_dexscreener_price(chain, pool_address):
    """Fetch live price from DexScreener."""
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GenTech/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            pair = data.get("pairs", [{}])[0]
            return {
                "price": float(pair.get("priceNative", 0)),
                "priceUsd": float(pair.get("priceUsd", 0)),
                "change24h": float(pair.get("priceChange", {}).get("h24", 0)),
                "volume24h": float(pair.get("volume", {}).get("h24", 0)),
                "liquidity": float(pair.get("liquidity", {}).get("usd", 0)),
                "txns24h": pair.get("txns", {}).get("h24", {}),
            }
    except Exception as e:
        print(f"⚠ DexScreener fetch failed: {e}", file=sys.stderr)
        return None


def fetch_token_price(chain, symbol):
    """Fetch token price via DexScreener by symbol."""
    url = f"https://api.dexscreener.com/latest/dex/search?q={symbol}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GenTech/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            for pair in data.get("pairs", []):
                if pair.get("chainId") == chain:
                    return float(pair.get("priceUsd", 0))
    except Exception:
        pass
    return None


# ============================================================
# LFJ-SPECIFIC: LP Position Reader
# ============================================================

def get_lfj_position(wallet, pool_address):
    """
    Read LFJ LP position from on-chain data.
    
    Strategy:
    1. Scan DepositedToBins and WithdrawnFromBins events
    2. Calculate net liquidity per bin
    3. Query balanceOf(wallet, binId) for each active bin
    """
    chain = "avalanche"

    # Get active bin (current price point)
    active_result = eth_call(chain, pool_address, "0x80afabfa")
    active_bin = int(active_result, 16) if active_result and active_result != "0x" else None

    # Get reserves
    reserves_result = eth_call(chain, pool_address, "0x0902f1ac")
    reserve_x = 0
    reserve_y = 0
    if reserves_result and reserves_result != "0x":
        decoded = reserves_result[2:]  # strip 0x
        if len(decoded) >= 128:
            reserve_x = int(decoded[:64], 16)
            reserve_y = int(decoded[64:128], 16)

    # Try to get bin balances for a reasonable range of bins around active
    # LFJ bins span roughly activeId ± 80 bins for a typical position
    bin_balances = {}
    if active_bin:
        # Scan a range around active bin (most positions span ~40-80 bins)
        scan_range = range(max(0, active_bin - 100), active_bin + 100)
        for bin_id in scan_range:
            # balanceOf(address, uint256) selector: 0x016c0910
            padded_wallet = wallet.lower().replace("0x", "").zfill(64)
            padded_bin = hex(bin_id)[2:].zfill(64)
            result = eth_call(chain, pool_address, f"0x016c0910{padded_wallet}{padded_bin}")
            if result and result != "0x":
                balance = int(result, 16)
                if balance > 0:
                    bin_balances[bin_id] = balance

    return {
        "activeBin": active_bin,
        "reserveX": reserve_x,
        "reserveY": reserve_y,
        "binBalances": bin_balances,
        "totalBins": len(bin_balances),
    }


# ============================================================
# WALLET BALANCE READER
# ============================================================

def read_wallet_balances(wallet, chain="avalanche"):
    """Read all token balances for a wallet on a chain."""
    tokens = TOKENS.get(chain, {})
    balances = {}

    # Native token (AVAX/ETH)
    native = get_native_balance(chain, wallet)
    native_key = {"avalanche": "AVAX", "base": "ETH", "ethereum": "ETH"}.get(chain, "NATIVE")
    balances[native_key] = native  # raw, needs decimals

    # ERC-20 tokens
    decimals = {
        "WAVAX": 18, "WETH": 18, "USDC": 6, "USDC_e": 6,
        "USDT_e": 6, "USDT": 6, "DAI": 18,
    }

    for symbol, address in tokens.items():
        raw = get_erc20_balance(chain, address, wallet)
        dec = decimals.get(symbol, 18)
        balances[symbol] = raw / (10 ** dec) if raw > 0 else 0

    return balances


# ============================================================
# UNISWAP V3 POSITION READER (Template)
# ============================================================

def get_uniswap_v3_positions(wallet):
    """
    Template for Uniswap V3 NFT Position Manager.
    Each position is an NFT — reads positions() via contract call.
    
    NFT Manager: 0xC36442b4a4522E871399CD717aBDD847Ab11FE88
    - balanceOf(address) → number of positions
    - tokenOfOwnerByIndex(address, index) → tokenId
    - positions(tokenId) → (nonce, operator, token0, token1, fee, tickLower, tickUpper, liquidity, ...)
    """
    # TODO: Implement with eth_call to Uniswap NFT Manager
    # This is a placeholder template for the Agent Kit
    return {
        "dex": "uniswap_v3",
        "positions": [],
        "note": "Template — implement with Uniswap NonfungiblePositionManager"
    }


# ============================================================
# MAIN POSITION READER
# ============================================================

def read_position(wallet, dex="lfj"):
    """Read full position data for a wallet on a DEX."""
    config = DEX_CONFIGS.get(dex)
    if not config:
        raise ValueError(f"Unknown DEX: {dex}")

    chain = config["chain"]
    print(f"🔗 Reading position on {config['name']} ({chain})...")
    print(f"   Wallet: {wallet}")

    # 1. Read wallet balances
    print(f"💰 Reading token balances...")
    balances = read_wallet_balances(wallet, chain)
    for sym, val in balances.items():
        print(f"   {sym}: {val}")

    # 2. Fetch live price
    price_data = None
    pool = config.get("pool_address")
    dexscreener_chain = config.get("dexscreener_chain", chain)
    if pool:
        print(f"📈 Fetching live price...")
        price_data = fetch_dexscreener_price(dexscreener_chain, pool)
        if price_data:
            print(f"   Price: ${price_data['price']:.4f} ({price_data['change24h']:+.2f}%)")

    # 3. Read LP position (DEX-specific)
    lp_data = None
    if dex == "lfj" and pool:
        print(f"📊 Reading LP position...")
        lp_data = get_lfj_position(wallet, pool)
        if lp_data:
            print(f"   Active bin: {lp_data['activeBin']}")
            print(f"   Bins with liquidity: {lp_data['totalBins']}")
            print(f"   Pool reserves: {lp_data['reserveX']} / {lp_data['reserveY']}")
    elif dex == "uniswap_v3":
        print(f"📊 Reading Uniswap V3 positions...")
        lp_data = get_uniswap_v3_positions(wallet)

    return {
        "wallet": wallet,
        "chain": chain,
        "dex": dex,
        "balances": balances,
        "price": price_data,
        "lp": lp_data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================
# DASHBOARD DATA WRITER
# ============================================================

def write_dashboard_data(position_data, output_path=DATA_PATH):
    """Write position data to defi-data.json for dashboard consumption."""
    now = datetime.now(timezone.utc).isoformat()
    balances = position_data.get("balances", {})
    price = position_data.get("price", {}) or {}
    lp = position_data.get("lp", {}) or {}

    # Calculate total wallet value
    avax_price = price.get("priceUsd", 0)
    avax_balance = balances.get("AVAX", 0)
    usdc_balance = balances.get("USDC", 0)
    usdc_e_balance = balances.get("USDC_e", 0)
    total_usdc = usdc_balance + usdc_e_balance
    total_value = (avax_balance * avax_price) + total_usdc

    # Milestone check
    milestone = "None"
    for name, threshold in sorted(MILESTONES.items(), key=lambda x: x[1]):
        if total_value >= threshold:
            milestone = name

    data = {
        "lastUpdated": now,
        "dataSource": "onchain",
        "pool": "AVAX/USDC",
        "chain": "Avalanche",
        "dex": "LFJ",
        "wallet": position_data.get("wallet", ""),
        "currentPrice": avax_price,
        "priceChange24h": price.get("change24h", 0),
        "volume24h": price.get("volume24h", 0),
        "liquidity": price.get("liquidity", 0),
        "walletBalances": {
            "avax": avax_balance,
            "usdc": total_usdc,
            "totalUsd": round(total_value, 2),
        },
        "lpPosition": {
            "activeBin": lp.get("activeBin"),
            "totalBins": lp.get("totalBins", 0),
            "reserveX": lp.get("reserveX", 0),
            "reserveY": lp.get("reserveY", 0),
            "binBalances": lp.get("binBalances", {}),
            "totalValue": round(total_value, 2),
        },
        "milestone": milestone,
        "milestones": MILESTONES,
    }

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Dashboard data written to {output_path}")
    print(f"   Total value: ${total_value:.2f}")
    print(f"   Milestone: {milestone}")

    return data


# ============================================================
# CLI
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="On-Chain Position Reader")
    parser.add_argument("--wallet", "-w", help="Wallet address to track", default=WALLET)
    parser.add_argument("--dex", "-d", choices=["lfj", "uniswap_v3", "pangolin"], default="lfj")
    parser.add_argument("--chain", "-c", default="avalanche")
    parser.add_argument("--output", "-o", default=DATA_PATH)
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if args.wallet == "0xYOUR_WALLET_ADDRESS":
        print("❌ Set --wallet or update WALLET in script config")
        print("   Example: python onchain-reader.py --wallet 0xYourAddress")
        sys.exit(1)

    position = read_position(args.wallet, args.dex)

    if args.json:
        print(json.dumps(position, indent=2))
    else:
        write_dashboard_data(position, args.output)


if __name__ == "__main__":
    main()
