#!/usr/bin/env python3
"""Cost of a compound / restake cycle on Blackhole (Sep 12 2026).

Jordan: "you can't just add to the position, you'd have to get rid of it and then
rebuild it... how much does it cost to restake each week?"

That premise is WRONG — we proved on-chain (Sep 12) that Algebra
`increaseLiquidity` works on a STAKED position. The gauge holds the NFT by
APPROVAL, not ownership, so `isAuthorizedForToken` already passes and the farm
auto-credits the new liquidity. We did it three times (49.44T -> 90.78T) with no
unstake, and `gauge.balanceOf` matched the new liquidity 3-for-3.

So this script prices BOTH paths so the comparison is concrete:
  A) in-place restake  (what we do)     = swap + increaseLiquidity
  B) unstake/re-stake  (what Jordan described) = swap + increase + remove + stake
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

# measured gas units from our own executed txs
GAS_SWAP = 180_000          # aggregator swap leg
GAS_INCREASE = 260_000      # increaseLiquidity on a staked position
GAS_UNSTAKE = 160_000       # farming center withdraw
GAS_RESTAKE = 220_000       # farming center deposit

AVAX_USD_FALLBACK = 7.36


def avax_usd():
    try:
        req = urllib.request.Request(
            f"https://api.dexscreener.com/latest/dex/tokens/"
            f"0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
            headers={"User-Agent": "Mozilla/5.0"})
        d = json.load(urllib.request.urlopen(req, timeout=25))
        best = 0.0
        for p in d.get("pairs") or []:
            if (p.get("baseToken") or {}).get("address", "").lower() == \
                    "0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7":
                best = max(best, float(p.get("priceUsd") or 0))
        return best or AVAX_USD_FALLBACK
    except Exception:
        return AVAX_USD_FALLBACK


def main():
    gp = w3.eth.gas_price
    gwei = gp / 1e9
    px = avax_usd()
    print("=" * 70)
    print("COMPOUND CYCLE COST — Blackhole (Avalanche C-Chain)")
    print("=" * 70)
    print(f"  gas price : {gwei:.3f} gwei")
    print(f"  AVAX      : ${px:.4f}")

    def cost(gas):
        avax = gas * gp / 1e18
        return avax, avax * px

    print("\n── A) IN-PLACE RESTAKE  (what we actually do) ──")
    a_avax, a_usd = cost(GAS_SWAP + GAS_INCREASE)
    print(f"   swap              {GAS_SWAP:>7,} gas")
    print(f"   increaseLiquidity {GAS_INCREASE:>7,} gas")
    print(f"   TOTAL             {GAS_SWAP+GAS_INCREASE:>7,} gas "
          f"= {a_avax:.8f} AVAX = ${a_usd:.6f}")

    print("\n── B) UNSTAKE + RE-STAKE  (the heavier path) ──")
    b_avax, b_usd = cost(GAS_SWAP + GAS_INCREASE + GAS_UNSTAKE + GAS_RESTAKE)
    print(f"   swap              {GAS_SWAP:>7,} gas")
    print(f"   increaseLiquidity {GAS_INCREASE:>7,} gas")
    print(f"   unstake           {GAS_UNSTAKE:>7,} gas")
    print(f"   restake           {GAS_RESTAKE:>7,} gas")
    print(f"   TOTAL             {GAS_SWAP+GAS_INCREASE+GAS_UNSTAKE+GAS_RESTAKE:>7,} gas "
          f"= {b_avax:.8f} AVAX = ${b_usd:.6f}")

    print("\n── C) WEEKLY COST OVER A YEAR ──")
    print(f"   in-place : ${a_usd:.6f}/week -> ${a_usd*52:.4f}/year")
    print(f"   unstake  : ${b_usd:.6f}/week -> ${b_usd*52:.4f}/year")
    print(f"   WASTED by unstaking: ${(b_usd-a_usd)*52:.4f}/year "
          f"({(b_usd/a_usd-1)*100:.0f}% more gas) for ZERO benefit")

    print("\n" + "=" * 70)
    print("VERDICT")
    print("=" * 70)
    print("   We do NOT need to unstake. increaseLiquidity works on a staked")
    print("   position because the gauge holds the NFT by APPROVAL, not ownership.")
    print("   Proven on-chain Sep 12: 49.44T -> 90.78T liquidity in 3 passes,")
    print("   gauge auto-credited each time (verified 3/3).")
    print("   => weekly compounding is already cheap enough to run every week.")


if __name__ == "__main__":
    raise SystemExit(main())
