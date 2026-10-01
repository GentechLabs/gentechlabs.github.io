#!/usr/bin/env python3
"""Can we farm COQ — and compound rewards back into COQ? (Jordan, Sep 11 2026)

Jordan: "there's no point in COQ, not even the black hole pool? What if we use it
as a way of compounding COQ and using it to buy COQ — would that work?"

Answers with chain data, not opinion:
  1. Where does COQ liquidity ACTUALLY live on Avalanche? (DexScreener survey)
  2. Does Blackhole have a COQ pool at all? Does it have a gauge/emissions?
  3. Is there any venue where a COQ farm + compound loop is real?
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
COQ = "0x420FcA0121DC28039145009570975747295f2329"
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"

# Algebra-fork factories on Avalanche (Blackhole + siblings)
FACTORIES = {
    "Blackhole": "0x512eb749541b7cf294be882d636218c84a5e9e5f",
}
GAUGE_MGR = "0xF0274C793D16713338AF4b8BF2BEf64BA2485B99"

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))

ERC20 = [{"constant": True, "inputs": [], "name": "symbol",
          "outputs": [{"name": "", "type": "string"}],
          "stateMutability": "view", "type": "function"},
         {"constant": True, "inputs": [], "name": "decimals",
          "outputs": [{"name": "", "type": "uint8"}],
          "stateMutability": "view", "type": "function"}]
FACT = [{"inputs": [{"name": "", "type": "address"}, {"name": "", "type": "address"}],
         "name": "poolByPair", "outputs": [{"name": "", "type": "address"}],
         "stateMutability": "view", "type": "function"}]
POOL_LIQ = [{"inputs": [], "name": "liquidity",
             "outputs": [{"name": "", "type": "uint128"}],
             "stateMutability": "view", "type": "function"}]
GAUGE_MGR_ABI = [{"inputs": [{"name": "", "type": "address"}], "name": "gauges",
                  "outputs": [{"name": "", "type": "address"}],
                  "stateMutability": "view", "type": "function"}]


def dexscreener(token):
    u = f"https://api.dexscreener.com/latest/dex/tokens/{token}"
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())


def main():
    print("=" * 68)
    print("COQ RAIL CHECK — is there any farm / compound loop?")
    print("=" * 68)

    c = w3.eth.contract(address=Web3.to_checksum_address(COQ), abi=ERC20)
    try:
        print(f"  COQ {COQ}")
        print(f"    symbol={c.functions.symbol().call()}  "
              f"decimals={c.functions.decimals().call()}")
    except Exception as e:
        print(f"  ❌ cannot read COQ: {str(e)[:70]}")
        return

    # ── 1. where does COQ liquidity live? ──
    print("\n  ── 1. COQ pairs on Avalanche (DexScreener) ──")
    try:
        d = dexscreener(COQ)
        pairs = [p for p in (d.get("pairs") or [])
                 if (p.get("chainId") or "").lower() == "avalanche"]
        pairs.sort(key=lambda p: -(float((p.get("liquidity") or {}).get("usd") or 0)))
        if not pairs:
            print("    no Avalanche pairs returned")
        for p in pairs[:10]:
            liq = float((p.get("liquidity") or {}).get("usd") or 0)
            vol = float((p.get("volume") or {}).get("h24") or 0)
            print(f"    {p.get('dexId'):14} {p.get('baseToken',{}).get('symbol','?'):6}/"
                  f"{p.get('quoteToken',{}).get('symbol','?'):7} "
                  f"liq ${liq:>12,.0f}  vol24h ${vol:>11,.0f}")
            print(f"        pair {p.get('pairAddress')}")
    except Exception as e:
        print(f"    ❌ dexscreener failed: {type(e).__name__} {str(e)[:60]}")

    # ── 2. does BLACKHOLE have a COQ pool? ──
    print("\n  ── 2. Blackhole (Algebra) COQ pools ──")
    for fname, faddr in FACTORIES.items():
        f = w3.eth.contract(address=Web3.to_checksum_address(faddr), abi=FACT)
        for qname, qaddr in (("WAVAX", WAVAX), ("USDC", USDC), ("BLACK", BLACK)):
            try:
                pool = f.functions.poolByPair(
                    Web3.to_checksum_address(COQ),
                    Web3.to_checksum_address(qaddr)).call()
                if int(pool, 16) == 0:
                    print(f"    {fname} COQ/{qname:6} -> none")
                    continue
                pc = w3.eth.contract(address=Web3.to_checksum_address(pool),
                                     abi=POOL_LIQ)
                try:
                    liq = pc.functions.liquidity().call()
                except Exception:
                    liq = -1
                print(f"    {fname} COQ/{qname:6} -> {pool}  liquidity={liq:,}")
                # gauge?
                gm = w3.eth.contract(address=Web3.to_checksum_address(GAUGE_MGR),
                                     abi=GAUGE_MGR_ABI)
                try:
                    g = gm.functions.gauges(Web3.to_checksum_address(pool)).call()
                    print(f"        gauge: {g}  {'✅ FARM EXISTS' if int(g,16)!=0 else '❌ no gauge (no emissions)'}")
                except Exception as e:
                    print(f"        gauge lookup failed: {str(e)[:60]}")
            except Exception as e:
                print(f"    {fname} COQ/{qname:6} -> revert ({str(e)[:40]})")


if __name__ == "__main__":
    main()
