#!/usr/bin/env python3
"""LINK gauges on Blackhole — what do they ACTUALLY pay? (Sep 12 2026)

CORRECTION CONTEXT: my earlier verdict said Blackhole had no LINK Algebra pools.
That was WRONG. `poolByPair` REVERTS for these pairs (it does not return 0x0),
and I read a revert as "the pool does not exist". Both pools exist and BOTH
gauges are live. Jordan's memory was right; my check produced a false negative.

  LINK.e/USDC  pool 0x177a7376860a04eEA6BF7fb3F39Bf10c49D3b42C
               gauge 0x014D8De7Fa79320C1750C4702b7830C3987F8B51
  LINK.e/BLACK pool 0x852B285DE2CB28d7162583B5C672B8d5be8f3de3
               gauge 0x8e6a5b139c8bce33241437355569AB2C50f77443

Measures real emissions (chain truth) rather than guessing from pool size.
"""
import json
import time
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

BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"
PAIRS = [
    ("LINK.e/USDC", "0x177a7376860a04eEA6BF7fb3F39Bf10c49D3b42C",
     "0x014D8De7Fa79320C1750C4702b7830C3987F8B51", 465.0),
    ("LINK.e/BLACK", "0x852B285DE2CB28d7162583B5C672B8d5be8f3de3",
     "0x8e6a5b139c8bce33241437355569AB2C50f77443", 25.0),
]

CURRENT_VALUE, CURRENT_MONTHLY = 24.18, 7.52

GAUGE_ABI = [
    {"name": "rewardRate", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"name": "", "type": "uint256"}]},
    {"name": "totalSupply", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"name": "", "type": "uint256"}]},
    {"name": "rewardToken", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"name": "", "type": "address"}]},
    {"name": "periodFinish", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"name": "", "type": "uint256"}]},
]


def black_price():
    """BLACK price in USD.

    DexScreener's token endpoint filters unreliably by chainId, so query the
    KNOWN deep BLACK/WAVAX pool directly instead of scanning and hoping. A
    silent 0.0 here zeroes every dollar figure in the report — which is exactly
    how a "measured" report ends up quietly telling you nothing.
    """
    tries = [
        "https://api.dexscreener.com/latest/dex/pairs/avalanche/"
        "0x14e4A5beD2e5E688EE1A5Ca3a4914250D1aBD573",
        f"https://api.dexscreener.com/latest/dex/tokens/{BLACK}",
    ]
    for url in tries:
        try:
            # DexScreener rejects requests without a UA (403), and my bare
            # `except: continue` made that look identical to "no data" — the
            # exception was swallowed and the function returned a silent 0.0.
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                d = json.load(r)
            pairs = d.get("pairs") or ([d["pair"]] if d.get("pair") else [])
            best = 0.0
            for p in pairs:
                if (p.get("baseToken") or {}).get("address", "").lower() == BLACK.lower():
                    best = max(best, float(p.get("priceUsd") or 0))
                elif (p.get("quoteToken") or {}).get("address", "").lower() == BLACK.lower():
                    # BLACK is the quote side: price of BLACK = 1 / price of base
                    bp = float(p.get("priceUsd") or 0)
                    if bp > 0 and p.get("priceNative"):
                        best = max(best, bp / float(p["priceNative"]))
            if best > 0:
                return best
        except Exception:
            continue
    return 0.0


def main():
    print("=" * 72)
    print("BLACKHOLE LINK GAUGES — MEASURED")
    print("=" * 72)
    bpx = black_price()
    if bpx <= 0:
        print("  ❌ BLACK price could not be measured — refusing to print dollar "
              "figures.\n     A zero price would silently make every number below "
              "$0.00 and look like a real answer.")
        return 1
    print(f"  BLACK price (measured): ${bpx:.8f}\n")

    results = []
    for name, pool, gauge, liq in PAIRS:
        print(f"── {name} ──")
        print(f"   pool  {pool}")
        print(f"   gauge {gauge}")
        g = w3.eth.contract(address=Web3.to_checksum_address(gauge), abi=GAUGE_ABI)
        rr = ts = None
        for fn in ("rewardRate", "totalSupply", "rewardToken", "periodFinish"):
            try:
                val = getattr(g.functions, fn)().call()
            except Exception as e:
                print(f"   {fn}: FAILED ({str(e)[:50]})")
                continue
            if fn == "rewardRate":
                rr = val
                print(f"   rewardRate  -> {val*86400/1e18:,.4f} BLACK/day (WHOLE pool)")
            elif fn == "totalSupply":
                ts = val
                print(f"   totalStaked -> {val/1e18:,.6f}")
            elif fn == "rewardToken":
                print(f"   rewardToken -> {val} "
                      f"{'✅ BLACK' if val.lower()==BLACK.lower() else '⚠️ not BLACK'}")
            elif fn == "periodFinish":
                left = val - time.time()
                print(f"   periodFinish-> {val} "
                      f"({'EXPIRED' if left < 0 else f'{left/3600:.1f}h left'})")
        per_day_usd = (rr or 0) * 86400 / 1e18 * bpx
        results.append((name, liq, per_day_usd))
        print(f"   => ${per_day_usd:,.4f}/day to the whole pool\n")

    print("=" * 72)
    print("VERDICT — is LINK a better rail than our WAVAX/USDC farm?")
    print("=" * 72)
    for name, liq, per_day_usd in results:
        print(f"\n  {name}  (pool liq ~${liq:,.0f}, ${per_day_usd:,.4f}/day total)")
        for cap in (24.18, 100, 500, 2000):
            share = cap / (liq + cap)
            yr = per_day_usd * 365 * share
            print(f"    ${cap:>7,.2f} -> {share*100:6.2f}% share -> "
                  f"${yr:>8,.2f}/yr  (${yr/12:,.2f}/mo)")
    print()
    print(f"  OUR LIVE FARM: ${CURRENT_VALUE:,.2f} -> ${CURRENT_MONTHLY:,.2f}/mo "
          f"= ${CURRENT_MONTHLY*12:,.2f}/yr")
    print()
    print("  ⚠️  Thin pools: our own entry slippage can exceed a year of emissions.")


if __name__ == "__main__":
    main()
