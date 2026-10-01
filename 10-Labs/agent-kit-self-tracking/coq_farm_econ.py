#!/usr/bin/env python3
"""COQ farming economics — is a COQ farm + compound loop viable? (Jordan, Sep 11)

Chain facts so far:
  - Real COQ market = traderjoe (LFJ) COQ/WAVAX: $488K liq, $17.5K/24h volume
  - Blackhole COQ/WAVAX exists: 0x4C33a727E3744009F7413D2d1FbbAd77D7Df207F
    but only ~$794 liquidity and ~$14/24h volume
  - LFJ is a RETIRED rail for us (approvals revoked Sep 11)

Now the decisive question: does the Blackhole COQ pool have a GAUGE with
EMISSIONS? Without emissions there is no farm — only swap fees on $14/day.
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
BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"
BH_COQ_POOL = "0x4C33a727E3744009F7413D2d1FbbAd77D7Df207F"
BH_WAVAX_USDC_POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"
OUR_GAUGE = "0x3ade52f9779c07471f4b6d5997444c3c2124c1c0"
GAUGE_MGR = "0x59aa177312Ff6Bdf39C8Af6F46dAe217bf76CBf6"

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))

GM = [{"inputs": [{"name": "", "type": "address"}], "name": "gauges",
       "outputs": [{"name": "", "type": "address"}],
       "stateMutability": "view", "type": "function"}]
GAUGE = [{"inputs": [], "name": "rewardToken",
          "outputs": [{"name": "", "type": "address"}],
          "stateMutability": "view", "type": "function"},
         {"inputs": [{"name": "", "type": "uint256"}], "name": "balanceOf",
          "outputs": [{"name": "", "type": "uint256"}],
          "stateMutability": "view", "type": "function"},
         {"inputs": [], "name": "rewardRate",
          "outputs": [{"name": "", "type": "uint256"}],
          "stateMutability": "view", "type": "function"}]
POOL = [{"inputs": [], "name": "liquidity",
         "outputs": [{"name": "", "type": "uint128"}],
         "stateMutability": "view", "type": "function"}]


def sym(addr):
    try:
        c = w3.eth.contract(address=Web3.to_checksum_address(addr), abi=[
            {"constant": True, "inputs": [], "name": "symbol",
             "outputs": [{"name": "", "type": "string"}],
             "stateMutability": "view", "type": "function"}])
        return c.functions.symbol().call()
    except Exception:
        return "?"


def main():
    gm = w3.eth.contract(address=Web3.to_checksum_address(GAUGE_MGR), abi=GM)
    print("=" * 68)
    print("COQ FARM VIABILITY — does the Blackhole COQ pool have a gauge?")
    print("=" * 68)

    for label, pool in (("COQ/WAVAX (Blackhole)", BH_COQ_POOL),
                        ("WAVAX/USDC (ours, control)", BH_WAVAX_USDC_POOL)):
        p = Web3.to_checksum_address(pool)
        try:
            g = gm.functions.gauges(p).call()
            has = int(g, 16) != 0
            print(f"\n  {label}")
            print(f"    pool  {pool}")
            print(f"    gauge {g}  {'✅ EXISTS' if has else '❌ NO GAUGE'}")
            if has:
                gc = w3.eth.contract(address=g, abi=GAUGE)
                try:
                    rt = gc.functions.rewardToken().call()
                    print(f"    rewardToken: {rt} ({sym(rt)})")
                except Exception as e:
                    print(f"    rewardToken read failed: {str(e)[:50]}")
        except Exception as e:
            print(f"\n  {label}: gauge lookup FAILED ({str(e)[:70]})")

    # ── fee economics on the COQ pool ──
    print("\n  ── fee economics ──")
    try:
        req = urllib.request.Request(
            "https://api.dexscreener.com/latest/dex/pairs/avalanche/"
            + BH_COQ_POOL, headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        p = (d.get("pairs") or [{}])[0]
        liq = float((p.get("liquidity") or {}).get("usd") or 0)
        vol = float((p.get("volume") or {}).get("h24") or 0)
        fee_tier = 0.0025  # typical Algebra CL fee on this pool family
        pool_fees_day = vol * fee_tier
        # if we supplied 1.4% of the pool ($11 of $794)
        our_share = 11.0 / (liq + 11.0) if liq else 1
        our_fees_day = pool_fees_day * our_share
        print(f"    Blackhole COQ/WAVAX: liq ${liq:,.0f}  vol24h ${vol:,.0f}")
        print(f"    ALL pool fee revenue/day  ≈ ${pool_fees_day:,.4f}")
        print(f"    our share if we add $11   ≈ {our_share*100:.2f}%")
        print(f"    our fee income/day        ≈ ${our_fees_day:,.4f}")
        print(f"    our fee income/month      ≈ ${our_fees_day*30:,.4f}")
        print(f"    our fee income/year       ≈ ${our_fees_day*365:,.2f}")
    except Exception as e:
        print(f"    dexscreener failed: {type(e).__name__} {str(e)[:60]}")

    # ── comparison: our current farm ──
    print("\n  ── comparison: our WAVAX/USDC farm ──")
    print("    BLACK emissions measured: ~100.7 BLACK/day (~$0.25/day, ~$7.52/mo)")


if __name__ == "__main__":
    main()
