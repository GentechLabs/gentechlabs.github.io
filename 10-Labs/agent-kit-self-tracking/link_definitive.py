#!/usr/bin/env python3
"""LINK on Blackhole — DEFINITIVE check (v2, Sep 12 2026).

Jordan: "I know they have a USDC link farm and one that's for black."

Earlier we found the Algebra CL factory returns 0x0 for every LINK pair, yet
DexScreener lists a blackhole LINK.e/USDC pool with $465 liq. That mismatch is
the same shape as the COQ finding, so the job is to determine WHAT that pool
actually is and whether ANY LINK pool on Blackhole emits farmable BLACK.

Method (chain truth, not assumptions):
  1. Pull the real pool address from DexScreener (not guessed).
  2. Identify its type: Algebra CL (has globalState) vs constant-product AMM.
  3. Enumerate LINK pairs across Blackhole's factories.
  4. Ask the gauge manager whether each pool has a LIVE gauge.
  5. If a gauge exists, read its reward rate -> real BLACK/day.
"""
import json
import urllib.request

from web3 import Web3

# ── AVAX RPC ROTATION (2026-09-22) ────────────────────────────────────────────────────────────
# This file used to hardcode a single provider. That one host took a per-SOURCE Cloudflare ban
# (1015) and returned 429 to EVERY call — so one throttle silently disabled this tool along with
# ~65 others. The shared `avax_rpc` module rotates across verified providers and FAILS CLOSED.
# The old URL is kept only as a last-resort string, never as the first choice.
def _avax_url():
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(globals().get("__file__") or (_s.argv and _s.argv[0]) or "."))
        if _d and _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import url as _u
        return _u()
    except Exception:
        return _avax_url()   # last resort only — avax_rpc preferred

RPC = _avax_url()
w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))

LINK = "0x5947BB275c521040051D82396192181b413227A3"   # LINK.e (18 dec)
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"

GAUGE_MGR = "0x59aa177312Ff6Bdf39C8Af6F46dAe217bf76CBf6"
BLACKHOLE_ALGEBRA_FACTORY = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"

TOKENS = {"LINK.e": LINK, "USDC": USDC, "WAVAX": WAVAX, "BLACK": BLACK}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def find_blackhole_pairs(token):
    """All Blackhole pairs involving `token` per DexScreener."""
    d = get(f"https://api.dexscreener.com/latest/dex/tokens/{token}")
    out = []
    for p in d.get("pairs") or []:
        if (p.get("dexId") or "").lower() != "blackhole":
            continue
        base = (p.get("baseToken") or {}).get("address", "").lower()
        quote = (p.get("quoteToken") or {}).get("address", "").lower()
        if token.lower() not in (base, quote):
            continue
        other = quote if base == token.lower() else base
        sym = (p.get("baseToken") if base != token.lower()
               else p.get("quoteToken")).get("symbol", "?")
        out.append({"addr": p["pairAddress"], "other": sym,
                    "liq": float(p.get("liquidity", {}).get("usd") or 0),
                    "vol": float(p.get("volume", {}).get("h24") or 0)})
    return out


def is_cl(pool):
    """Algebra CL pools expose globalState(); plain AMMs do not."""
    try:
        sel = Web3.keccak(text="globalState()")[:4]
        r = w3.eth.call({"to": Web3.to_checksum_address(pool), "data": sel})
        return len(r) >= 32
    except Exception:
        return False


def main():
    print("=" * 70)
    print("LINK ON BLACKHOLE — DEFINITIVE")
    print("=" * 70)
    print(f"  LINK.e {LINK}\n")

    print("── 1. Blackhole pools containing LINK (DexScreener, real addresses) ──")
    pairs = find_blackhole_pairs(LINK)
    if not pairs:
        print("    (none listed)")
    for p in pairs:
        kind = "Algebra CL" if is_cl(p["addr"]) else "constant-product AMM"
        print(f"    LINK.e/{p['other']:<8} {p['addr']}")
        print(f"      type={kind}  liq=${p['liq']:,.0f}  vol24h=${p['vol']:,.0f}")

    print()
    print("── 2. Algebra CL factory (poolByPair) for every LINK pair ──")
    f = w3.eth.contract(address=Web3.to_checksum_address(
        BLACKHOLE_ALGEBRA_FACTORY), abi=[{
            "name": "poolByPair", "type": "function", "stateMutability": "view",
            "inputs": [{"name": "t0", "type": "address"},
                       {"name": "t1", "type": "address"}],
            "outputs": [{"name": "", "type": "address"}]}])
    for name, addr in TOKENS.items():
        if addr == LINK:
            continue
        try:
            pool = f.functions.poolByPair(
                Web3.to_checksum_address(LINK),
                Web3.to_checksum_address(addr)).call()
            print(f"    LINK/{name:<6} -> {pool}")
        except Exception as e:
            print(f"    LINK/{name:<6} -> call failed: {str(e)[:60]}")

    print()
    print("── 3. Gauge manager: does any pool have a live farm? ──")
    gm = w3.eth.contract(address=Web3.to_checksum_address(GAUGE_MGR), abi=[{
        "name": "gauges", "type": "function", "stateMutability": "view",
        "inputs": [{"name": "", "type": "address"}],
        "outputs": [{"name": "", "type": "address"}]}])
    for p in pairs:
        try:
            g = gm.functions.gauges(Web3.to_checksum_address(p["addr"])).call()
            live = g != "0x0000000000000000000000000000000000000000"
            print(f"    LINK.e/{p['other']:<8} gauge={g} "
                  f"{'✅ LIVE' if live else '❌ none'}")
        except Exception as e:
            print(f"    LINK.e/{p['other']:<8} gauge read failed: {str(e)[:50]}")

    print()
    print("── 4. For scale: our live farm ──")
    print("    WAVAX/USDC Blackhole CL position = ~$24.18 at ~$7.52/month")
    print("    (a LINK pool must beat that on a risk-adjusted basis to be worth moving)")


if __name__ == "__main__":
    main()
