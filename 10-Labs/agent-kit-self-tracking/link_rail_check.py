#!/usr/bin/env python3
"""Does LINK have farmable pools on Blackhole? (Jordan, Sep 12 2026)

Jordan: "I know for a fact there's a LINK... put their LINK pools on black hole"

Verify on-chain, and measure whether it's worth farming vs our WAVAX/USDC core.
"""
import json
import urllib.request

from web3 import Web3
from eth_utils import keccak

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
LINK = "0x5947BB275c521040051D82396192181b413227A3"   # LINK on Avalanche
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"
FACTORY = "0x512eb749541b7cf294be882d636218c84a5e9e5f"
GAUGE_MGR = "0x59aa177312Ff6Bdf39C8Af6F46dAe217bf76CBf6"

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
GM = [{"inputs": [{"name": "", "type": "address"}], "name": "gauges",
       "outputs": [{"name": "", "type": "address"}],
       "stateMutability": "view", "type": "function"}]
GAUGE = [{"inputs": [], "name": "rewardToken",
          "outputs": [{"name": "", "type": "address"}],
          "stateMutability": "view", "type": "function"}]


def main():
    print("=" * 70)
    print("LINK ON BLACKHOLE — does it have farmable CL pools?")
    print("=" * 70)

    c = w3.eth.contract(address=Web3.to_checksum_address(LINK), abi=ERC20)
    try:
        print(f"  LINK {LINK}  symbol={c.functions.symbol().call()} "
              f"decimals={c.functions.decimals().call()}")
    except Exception as e:
        print(f"  ⚠️  LINK read failed ({str(e)[:50]}) — checking pairs anyway")

    # ── 1. Algebra CL pools ──
    print("\n  ── 1. Algebra CL LINK pools (factory.poolByPair) ──")
    f = w3.eth.contract(address=Web3.to_checksum_address(FACTORY), abi=FACT)
    gm = w3.eth.contract(address=Web3.to_checksum_address(GAUGE_MGR), abi=GM)
    found = []
    for qname, qaddr in (("WAVAX", WAVAX), ("USDC", USDC), ("BLACK", BLACK)):
        try:
            p = f.functions.poolByPair(Web3.to_checksum_address(LINK),
                                       Web3.to_checksum_address(qaddr)).call()
            if int(p, 16) == 0:
                print(f"    LINK/{qname:6} -> none")
                continue
            try:
                w3.eth.call({"to": p,
                             "data": "0x" + keccak(text="globalState()").hex()[:8]})
                kind = "Algebra CL ✅"
            except Exception:
                kind = "not-CL"
            print(f"    LINK/{qname:6} -> {p}  {kind}")
            found.append((qname, p))
            try:
                g = gm.functions.gauges(Web3.to_checksum_address(p)).call()
                if int(g, 16) != 0:
                    gc = w3.eth.contract(address=g, abi=GAUGE)
                    rt = gc.functions.rewardToken().call()
                    name = "BLACK" if rt.lower() == BLACK.lower() else rt
                    print(f"        gauge {g} ✅ emitting {name}")
                else:
                    print("        gauge: none")
            except Exception as e:
                print(f"        gauge lookup failed: {str(e)[:40]}")
        except Exception as e:
            print(f"    LINK/{qname:6} -> error {str(e)[:40]}")

    if not found:
        print("    ⛔ no LINK Algebra pools found via this factory")

    # ── 2. what does the market show? ──
    print("\n  ── 2. LINK pairs on Avalanche (DexScreener) ──")
    try:
        req = urllib.request.Request(
            f"https://api.dexscreener.com/latest/dex/tokens/{LINK}",
            headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        pairs = [p for p in (d.get("pairs") or [])
                 if (p.get("chainId") or "").lower() == "avalanche"]
        pairs.sort(key=lambda p: -(float((p.get("liquidity") or {}).get("usd") or 0)))
        for p in pairs[:8]:
            liq = float((p.get("liquidity") or {}).get("usd") or 0)
            vol = float((p.get("volume") or {}).get("h24") or 0)
            print(f"    {p.get('dexId'):14} {p.get('baseToken',{}).get('symbol','?'):8}/"
                  f"{p.get('quoteToken',{}).get('symbol','?'):7} "
                  f"liq ${liq:>11,.0f} vol24h ${vol:>10,.0f}")
    except Exception as e:
        print(f"    failed: {str(e)[:60]}")


if __name__ == "__main__":
    main()
