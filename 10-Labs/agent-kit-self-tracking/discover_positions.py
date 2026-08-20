#!/usr/bin/env python3
"""
Agent Kit — Self-Tracking Treasury: discover_positions()
===========================================================
Generalizes `agentic-treasury.py`'s `layer_lp_live()` (Aug 11, 2026) into a
chain-agnostic, wallet-driven position auto-discovery function.

Reads LIVE on-chain data (public RPC + CoinGecko/DexScreener for price) — no
stale feeds, no API keys, no browser. Given a wallet + a chain + optional
pools, it probes for deployed LP positions and returns a normalized report
line per position. The kit's cron layer picks these up automatically.

Reusable core pattern (the moat):
  read getActiveId -> scan balanceOf(addr, bin) window -> compute bin range +
  IN/OUT vs live price. Extends to any LB-style DEX (LFJ V2.2, Meteora DLMM,
  Monad/Trader Joe) + ERC-20 wallet balances on Base/Ethereum.

Design rules (from develop-and-verify / audit checklist):
  - Per-pool try/except: one broken pool degrades to an error entry, never
    blocks the rest of the discovery.
  - Input bounds: wallet must be a valid 0x address; chain must be known.
  - No hardcoded secrets. No error-detail leakage (generic messages).
  - Report honestly: bin-count + range + IN/OUT, never invent a precise USD
    value that wasn't actually measured.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ── Chain RPC endpoints (free, no API key) ─────────────────────────────
RPC_ENDPOINTS = {
    "avalanche": "https://api.avax.network/ext/bc/C/rpc",
    "base": "https://mainnet.base.org",
    "ethereum": "https://eth.llamarpc.com",
    "arbitrum": "https://arb1.arbitrum.io/rpc",
    "polygon": "https://polygon-rpc.com",
}

# CoinGecko id per asset (price fallback source)
_COINGECKO_ID = {
    "AVAX": "avalanche-2", "WAVAX": "avalanche-2",
    "WETH": "ethereum", "ETH": "ethereum",
    "BTC": "bitcoin", "SOL": "solana", "LINK": "chainlink",
    "USDC": "usd-coin", "USDT": "tether", "cbBTC": "coinbase-wrapped-btc",
    "PAXG": "pax-gold",
}

# ERC-20 token addresses per chain (wallet balance layer)
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
        "cbBTC": "0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf",
    },
    "ethereum": {
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    },
}

_DECIMALS = {
    "WAVAX": 18, "WETH": 18, "ETH": 18, "USDC": 6, "USDC_e": 6,
    "USDT": 6, "USDT_e": 6, "cbBTC": 8, "PAXG": 18, "BTC": 8,
}

# LFJ V2.2 bin price formula constants
LFJ_SHIFT = 2**23  # 8,388,608


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── RPC helpers ────────────────────────────────────────────────────────

def rpc_call(chain: str, method: str, params: Optional[list] = None) -> Any:
    """JSON-RPC call. Raises ValueError for unknown chain / RPC error."""
    url = RPC_ENDPOINTS.get(chain)
    if not url:
        raise ValueError(f"no RPC endpoint for chain: {chain}")
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "GenTech/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
        if "error" in result:
            raise RuntimeError(f"rpc error: {result['error']}")
        return result.get("result")


def eth_call(chain: str, to: str, data: str) -> str:
    return rpc_call(chain, "eth_call", [{"to": to, "data": data}, "latest"])


def _is_checksum_or_valid(addr: str) -> bool:
    if not addr or not isinstance(addr, str):
        return False
    return addr.lower().startswith("0x") and len(addr) == 42 and all(
        c in "0123456789abcdefABCDEF" for c in addr[2:])


# ── price helpers ──────────────────────────────────────────────────────

def fetch_asset_price(asset: str) -> Optional[float]:
    """CoinGecko USD price (fallback: DexScreener). None on failure."""
    cg_id = _COINGECKO_ID.get(asset.upper())
    if cg_id:
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
            with urllib.request.urlopen(url, timeout=8) as r:
                price = float(json.load(r)[cg_id]["usd"])
                if price:
                    return price
        except Exception:
            pass
    # DexScreener fallback
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={asset.upper()}"
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            pairs = json.load(r).get("pairs", [])
        for p in pairs:
            if p.get("baseToken", {}).get("symbol", "").upper() == asset.upper():
                price = float(p.get("priceUsd") or 0)
                if price:
                    return price
    except Exception:
        pass
    return None


# ── ERC-20 / native balance layer ─────────────────────────────────────

def get_native_balance(chain: str, wallet: str) -> int:
    try:
        r = rpc_call(chain, "eth_getBalance", [wallet, "latest"])
        return int(r, 16) if r else 0
    except Exception:
        return 0


def get_erc20_balance(chain: str, token_address: str, wallet: str) -> int:
    padded = wallet.lower().replace("0x", "").zfill(64)
    try:
        r = eth_call(chain, token_address, f"0x70a08231{padded}")
        return int(r, 16) if r and r != "0x" else 0
    except Exception:
        return 0


def discover_wallet_balances(chain: str, wallet: str) -> Dict[str, float]:
    """Wallet token balances (native + ERC-20) on a chain. Per-token isolation."""
    out: Dict[str, float] = {}
    native_key = {"avalanche": "AVAX", "base": "ETH",
                  "ethereum": "ETH", "arbitrum": "ETH", "polygon": "MATIC"}.get(chain, "NATIVE")
    raw_native = get_native_balance(chain, wallet)
    out[native_key] = raw_native / 10**18 if raw_native else 0.0
    for sym, addr in (TOKENS.get(chain) or {}).items():
        raw = get_erc20_balance(chain, addr, wallet)
        dec = _DECIMALS.get(sym, 18)
        out[sym] = round(raw / 10**dec, 6) if raw else 0.0
    return out


# ── LB-style bin position reader (the reusable core) ──────────────────

def _bin_price_lfj(bin_id: int, bin_step: int) -> float:
    """LFJ V2.2 price from a bin id. Returns price (tokenY per tokenX)."""
    return (1 + bin_step / 10000) ** (bin_id - LFJ_SHIFT) * 10**12


def read_lfj_v22_position(wallet: str, pool: Dict[str, Any], chain: str = "avalanche") -> Dict[str, Any]:
    """Live LFJ V2.2 LP position read. Generalizes layer_lp_live().

    Scans balanceOf(addr, bin) over a window around the active bin, computes
    the price range from bin ids, and marks IN/OUT vs the live token price.
    Returns a normalized position dict. Never raises — reports via 'error'.
    """
    pair = pool["address"]
    bin_step = int(pool.get("bin_step", 10))
    tokenX = pool.get("tokenX", "WAVAX")
    tokenY = pool.get("tokenY", "USDC")

    if not _is_checksum_or_valid(wallet) or not _is_checksum_or_valid(pair):
        return {"error": "invalid address", "name": pool.get("name")}

    try:
        active_raw = eth_call(chain, pair, "0xdbe65edc")  # getActiveId()
        active = int(active_raw, 16) if active_raw and active_raw != "0x" else None
        if active is None:
            return {"error": "could not read active bin", "name": pool.get("name")}

        bal_sel = "0x00fdd58e"  # balanceOf(address,uint256)
        addr_hex = wallet.lower().replace("0x", "")
        bins_with_liquidity = 0
        low = high = None
        # Auto-discovery must tolerate price drift: positions can sit far from
        # the current active bin. Start at ±20; if empty, widen to ±256.
        half_width = 20
        while True:
            for offset in range(-half_width, half_width + 1):
                bin_id = active + offset
                data = bal_sel + addr_hex.zfill(64) + hex(bin_id)[2:].zfill(64)
                try:
                    b = int(eth_call(chain, pair, data), 16)
                except Exception:
                    continue
                if b > 0:
                    bins_with_liquidity += 1
                    p = _bin_price_lfj(bin_id, bin_step)
                    if low is None or p < low:
                        low = p
                    if high is None or p > high:
                        high = p
            if bins_with_liquidity or half_width >= 256:
                break
            half_width = 256  # widen once, then stop

        if bins_with_liquidity == 0:
            return {"error": "no position", "name": pool.get("name"),
                    "activeBin": active, "bins": 0}

        # tokenX (e.g. WAVAX) price in USD
        price_x = fetch_asset_price(tokenX)
        # Live pair price (tokenX in tokenY): active bin price is the market rate
        market_price = _bin_price_lfj(active, bin_step)  # Y per X
        in_range = (low <= market_price <= high) if (low and high) else True

        # ── Deployed position value (USD) — honest accounting ─────────
        # LFJ V2.2 getBin returns tightly-packed uint128s that don't ABI-decode
        # cleanly, and pool-level getReserves() is pool-wide (30K+ AVAX), NOT
        # our share. So we value the position from the wallet ledger:
        #   deployed = known_funded_usd − loose_wallet_value − native_gas.
        # funded_usd comes from treasury_config ("funded_usd"), set at deposit.
        # If not set, report None (honest) rather than inventing a number.
        position_usd = None
        try:
            cfg_funded = None
            try:
                with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       "treasury_config.json")) as _cfgf:
                    cfg_funded = json.load(_cfgf).get("funded_usd")
            except Exception:
                cfg_funded = None
            if cfg_funded and price_x:
                # wallet loose value from discover_wallet_balances
                wb = discover_wallet_balances(chain, wallet)
                loose_usd = 0.0
                for sym, amt in wb.items():
                    if sym == "AVAX" or sym == "WAVAX":
                        loose_usd += amt * price_x
                    elif sym in ("USDC", "USDC_e", "USDT_e"):
                        loose_usd += amt  # ~1 USD stable
                position_usd = round(max(cfg_funded - loose_usd, 0.0), 2)
        except Exception:
            position_usd = None

        return {
            "name": pool.get("name"),
            "type": "lfj_v22",
            "chain": chain,
            "wallet": wallet,
            "pool": pair,
            "activeBin": active,
            "bins": bins_with_liquidity,
            "rangeLow": round(low, 6) if low else None,
            "rangeHigh": round(high, 6) if high else None,
            "inRange": in_range,
            "livePriceUsd": round(price_x, 6) if price_x else None,
            "positionUsd": position_usd,
            "read": (f"{bins_with_liquidity} bins · {'IN' if in_range else 'OUT'} · "
                     f"${market_price:.4f} Y/X"
                     + (f" [{low:.4f}–{high:.4f}]" if low and high else "")),
        }
    except Exception:
        return {"error": "position read failed", "name": pool.get("name")}


# ── top-level auto-discovery ───────────────────────────────────────────

def discover_positions(chain: str, wallet: str,
                       pools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Auto-discover a wallet's positions on a chain.

    Args:
        chain: 'avalanche' | 'base' | 'ethereum' | ...
        wallet: 0x address.
        pools: optional list of {name, type, address, tokenX, tokenY, bin_step}.
               If omitted, probes known LB pools on that chain via config.

    Returns:
        {chain, wallet, balances, positions: [...], discovered_at}.
        Each position is a normalized dict or {'error': ...}. Never raises.
    """
    if not _is_checksum_or_valid(wallet):
        raise ValueError("invalid wallet address")
    if chain not in RPC_ENDPOINTS:
        raise ValueError(f"unsupported chain: {chain}")

    result: Dict[str, Any] = {
        "chain": chain,
        "wallet": wallet,
        "balances": discover_wallet_balances(chain, wallet),
        "positions": [],
        "discovered_at": _now_iso(),
    }

    # If no pools given, load from the kit config next to this script.
    if not pools:
        cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "treasury_config.json")
        try:
            with open(cfg_path) as f:
                cfg = json.load(f)
            pools = (cfg.get("pools") or {}).get(chain) or []
        except Exception:
            pools = []

    pools = pools or []
    for pool in pools:
        ptype = pool.get("type", "")
        try:
            if ptype == "lfj_v22":
                pos = read_lfj_v22_position(wallet, pool, chain)
            else:
                pos = {"error": f"unsupported position type: {ptype}", "name": pool.get("name")}
        except Exception:
            pos = {"error": "discovery failed", "name": pool.get("name")}
        result["positions"].append(pos)

    return result


# ── CLI ────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Agent Kit — self-tracking position discovery")
    parser.add_argument("--wallet", required=True, help="0x wallet address")
    parser.add_argument("--chain", default="avalanche",
                        choices=sorted(RPC_ENDPOINTS.keys()))
    parser.add_argument("--json", action="store_true", help="pretty JSON output")
    args = parser.parse_args()

    try:
        data = discover_positions(args.chain, args.wallet)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(f"Chain: {data['chain']} | Wallet: {data['wallet']}")
        print("Balances:")
        for sym, val in data["balances"].items():
            if val:
                print(f"  {sym}: {val}")
        print("Positions:")
        for p in data["positions"]:
            if "error" in p:
                print(f"  - {p.get('name', '?')}: ⚠ {p['error']}")
            else:
                print(f"  - {p['name']}: {p['read']} (${p.get('livePriceUsd')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
