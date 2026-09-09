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


def _batch_eth_call(chain: str, to: str, bal_sel: str, addr_hex: str,
                    bin_ids: list) -> list:
    """Batch many balanceOf(addr, bin) reads into ONE JSON-RPC request.

    Returns a list of int balances aligned with bin_ids. On any failure returns
    all zeros (caller treats as 'no liquidity' — safe, never blocks discovery).
    """
    url = RPC_ENDPOINTS.get(chain)
    if not url:
        return [0] * len(bin_ids)
    payload = [
        {"jsonrpc": "2.0", "id": i, "method": "eth_call",
         "params": [{"to": to, "data": bal_sel + addr_hex.zfill(64) + hex(b)[2:].zfill(64)}, "latest"]}
        for i, b in enumerate(bin_ids)
    ]
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "GenTech/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            results = json.loads(resp.read())
        by_id = {r.get("id"): r.get("result") for r in results}
        out = []
        for i in range(len(bin_ids)):
            raw = by_id.get(i)
            try:
                out.append(int(raw, 16) if raw and raw != "0x" else 0)
            except Exception:
                out.append(0)
        return out
    except Exception:
        return [0] * len(bin_ids)


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

    active = None
    try:
        active_raw = eth_call(chain, pair, "0xdbe65edc")  # getActiveId()
        active = int(active_raw, 16) if active_raw and active_raw != "0x" else None
    except Exception:
        pass

    # When the pair contract is dead on-chain (reverts on public RPCs),
    # fall back to DexScreener to derive the active bin from the price.
    if active is None:
        try:
            import urllib.request, math
            req = urllib.request.Request(
                f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{pair}",
                headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                d = json.loads(resp.read())
                if d.get("pairs"):
                    ds_price = float(d["pairs"][0].get("priceUsd") or 0)
                    if ds_price > 0:
                        ratio = ds_price / 10**12
                        base = 1 + bin_step / 10000
                        active = round(math.log(ratio, base)) + LFJ_SHIFT
        except Exception:
            pass

    if active is None:
        return {"error": "could not read active bin", "name": pool.get("name"),
                "livePriceUsd": fetch_asset_price(tokenX)}

    try:
        bal_sel = "0x00fdd58e"  # balanceOf(address,uint256)
        addr_hex = wallet.lower().replace("0x", "")
        bins_with_liquidity = 0
        low = high = None
        # Auto-discovery must tolerate price drift: positions can sit far from
        # the current active bin. Start at ±20; if empty, widen to ±256.
        # BATCH the bin reads into ONE JSON-RPC request (Sep 7 2026): a flat
        # pool previously did 554 sequential eth_calls (41 + 513 bins) which
        # hung past the watchdog's 180s timeout — so the auto-deploy never
        # fired and the pool stayed flat. Batching turns that into 1 request.
        half_width = 20
        while True:
            bin_ids = [active + offset for offset in range(-half_width, half_width + 1)]
            reads = _batch_eth_call(chain, pair, bal_sel, addr_hex, bin_ids)
            for bin_id, b in zip(bin_ids, reads):
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


# ── Algebra V3 (Blackhole) CL position reader ─────────────────────────
# Blackhole's WAVAX/USDC pool is an Algebra V3 concentrated-liquidity pool.
# Positions are ERC-721 NFTs held by the wallet via the NFPM. We read the
# wallet's NFT balance + tokenOfOwnerByIndex + positions(tokenId) to find
# live CL positions, and globalState() for the current tick/price.

BLACKHOLE_NFPM = "0x3fED017EC0f5517Cdf2E8a9a4156c64d74252146"  # LEGACY NFPM (our pool's deployer)
BLACKHOLE_POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"  # WAVAX/USDC Algebra V3
_WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
_USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"


def _erc721_balance(chain: str, nfpm: str, wallet: str) -> int:
    padded = wallet.lower().replace("0x", "").zfill(64)
    try:
        r = eth_call(chain, nfpm, f"0x70a08231{padded}")  # balanceOf(address)
        return int(r, 16) if r and r != "0x" else 0
    except Exception:
        return 0


def _erc721_token_of_owner(chain: str, nfpm: str, wallet: str, index: int) -> Optional[int]:
    padded = wallet.lower().replace("0x", "").zfill(64)
    idx = hex(index)[2:].zfill(64)
    try:
        r = eth_call(chain, nfpm, f"0x2f745c59{padded}{idx}")  # tokenOfOwnerByIndex(address,uint256)
        return int(r, 16) if r and r != "0x" else None
    except Exception:
        return None


def _nfpm_position(chain: str, nfpm: str, token_id: int) -> Optional[Dict[str, Any]]:
    """NFPM.positions(tokenId) -> {token0, token1, tickLower, tickUpper, liquidity}."""
    tid = hex(token_id)[2:].zfill(64)
    try:
        r = eth_call(chain, nfpm, f"0x99fbab88{tid}")  # positions(uint256)
        if not r or r == "0x":
            return None
        b = bytes.fromhex(r[2:])
        # ABI decode: nonce(uint88) operator(160) token0(160) token1(160)
        # deployer(160) tickLower(int24) tickUpper(int24) liquidity(uint128) ...
        # Each is a 32-byte word in the return.
        def _w(i):
            return int.from_bytes(b[i*32:(i+1)*32], "big")
        def _addr(i):
            return "0x" + b[i*32+12:(i+1)*32].hex()
        def _int24(i):
            v = int.from_bytes(b[i*32+29:(i+1)*32], "big", signed=True)
            return v
        return {
            "token0": _addr(2), "token1": _addr(3),
            "tickLower": _int24(5), "tickUpper": _int24(6),
            "liquidity": _w(7),
        }
    except Exception:
        return None


def _pool_global_state(chain: str, pool: str) -> Optional[Dict[str, Any]]:
    """Algebra pool globalState() -> {price, tick, fee}. Decodes the packed struct."""
    try:
        r = eth_call(chain, pool, "0xe76c01e4")  # globalState()
        if not r or r == "0x":
            return None
        b = bytes.fromhex(r[2:])
        # ABI tuple: price(uint160) tick(int24) fee(uint16) timepointIndex(uint16)
        # communityFeeToken0(uint8) communityFeeToken1(uint8) unlocked(bool)
        price = int.from_bytes(b[0:32], "big")
        tick = int.from_bytes(b[32:64][29:32], "big", signed=True)
        fee = int.from_bytes(b[64:96][30:32], "big")
        return {"price": price, "tick": tick, "fee": fee}
    except Exception:
        return None


def read_blackhole_cl_position(wallet: str, pool: Dict[str, Any], chain: str = "avalanche") -> Dict[str, Any]:
    """Live Blackhole Algebra-V3 CL position read (NFPM NFT-based).

    Returns a normalized position dict (same shape as LFJ reader) or
    {'error': ...}. Never raises. Reads the wallet's CL NFTs, finds the one
    on the WAVAX/USDC pool, and reports liquidity + in-range vs the pool's
    current tick.
    """
    nfpm = pool.get("nfpm", BLACKHOLE_NFPM)
    pair = pool.get("address", BLACKHOLE_POOL)
    tokenX = pool.get("tokenX", "WAVAX")
    tokenY = pool.get("tokenY", "USDC")

    if not _is_checksum_or_valid(wallet) or not _is_checksum_or_valid(nfpm):
        return {"error": "invalid address", "name": pool.get("name")}

    n = _erc721_balance(chain, nfpm, wallet)
    if n == 0:
        return {"error": "no position", "name": pool.get("name"), "bins": 0}

    # Find the CL NFT on this pool
    for i in range(n):
        tid = _erc721_token_of_owner(chain, nfpm, wallet, i)
        if tid is None:
            continue
        pos = _nfpm_position(chain, nfpm, tid)
        if not pos:
            continue
        # Match pool tokens (WAVAX/USDC)
        if (pos["token0"].lower() == _WAVAX.lower() and pos["token1"].lower() == _USDC.lower()) or \
           (pos["token0"].lower() == _USDC.lower() and pos["token1"].lower() == _WAVAX.lower()):
            gs = _pool_global_state(chain, pair)
            cur_tick = gs["tick"] if gs else None
            in_range = (pos["tickLower"] <= cur_tick <= pos["tickUpper"]) if cur_tick is not None else None
            price_x = fetch_asset_price(tokenX)
            # USD range from ticks: price = 1.0001^tick * 10^(dec0-dec1)
            # WAVAX(18) / USDC(6) -> * 1e12
            def _tick_usd(t):
                return 1.0001 ** t * (10 ** (18 - 6))
            range_lo = _tick_usd(pos["tickLower"]) if pos["tickLower"] is not None else None
            range_hi = _tick_usd(pos["tickUpper"]) if pos["tickUpper"] is not None else None
            # Position value: funded_usd - loose wallet (same honest method as LFJ)
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
                    wb = discover_wallet_balances(chain, wallet)
                    loose_usd = 0.0
                    for sym, amt in wb.items():
                        if sym in ("AVAX", "WAVAX"):
                            loose_usd += amt * price_x
                        elif sym in ("USDC", "USDC_e", "USDT_e"):
                            loose_usd += amt
                    position_usd = round(max(cfg_funded - loose_usd, 0.0), 2)
            except Exception:
                position_usd = None
            return {
                "name": pool.get("name"),
                "type": "blackhole_cl",
                "chain": chain,
                "wallet": wallet,
                "pool": pair,
                "tokenId": tid,
                "bins": 1 if pos["liquidity"] > 0 else 0,
                "liquidity": pos["liquidity"],
                "tickLower": pos["tickLower"],
                "tickUpper": pos["tickUpper"],
                "rangeLow": round(range_lo, 6) if range_lo else None,
                "rangeHigh": round(range_hi, 6) if range_hi else None,
                "inRange": in_range,
                "livePriceUsd": round(price_x, 6) if price_x else None,
                "positionUsd": position_usd,
                "read": (f"CL position #{tid} · {'IN' if in_range else 'OUT'} · "
                         f"${price_x:.4f} Y/X" if price_x else f"CL position #{tid}"),
            }
    return {"error": "no position on this pool", "name": pool.get("name"), "bins": 0}


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
            elif ptype == "blackhole_cl":
                pos = read_blackhole_cl_position(wallet, pool, chain)
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
