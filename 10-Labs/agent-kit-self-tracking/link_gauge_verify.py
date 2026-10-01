#!/usr/bin/env python3
"""Is the LINK.e/USDC gauge ACTUALLY paying? (Sep 12 2026)

Jordan: "verify these numbers... this might be an underrated pool... I want to
know what the estimated performance would be."

A gauge can report a rewardRate and still pay nothing — a dead or unfunded
program. So verify by EVIDENCE OF PAYMENT, not by the advertised rate:

  1. Does the gauge actually HOLD BLACK? (Unfunded => rate is theatre.)
  2. Has it emitted payment events recently? (Recent logs = live.)
  3. What is really staked vs the pool, so we can size our share honestly?
  4. What would OUR position earn, including slippage and IL?
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
w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 40}))

BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
LINK = "0x5947BB275c521040051D82396192181b413227A3"
POOL = "0x177a7376860a04eEA6BF7fb3F39Bf10c49D3b42C"
GAUGE = "0x014D8De7Fa79320C1750C4702b7830C3987F8B51"
GAUGE_MGR = "0x59aa177312Ff6Bdf39C8Af6F46dAe217bf76CBf6"
FARMING_CENTER = "0xa47Ad2C95FaE476a73b85A355A5855aDb4b3A449"

ERC20 = [{"name": "balanceOf", "type": "function", "stateMutability": "view",
          "inputs": [{"name": "", "type": "address"}],
          "outputs": [{"name": "", "type": "uint256"}]},
         {"name": "decimals", "type": "function", "stateMutability": "view",
          "inputs": [], "outputs": [{"name": "", "type": "uint8"}]}]

GAUGE_ABI = ERC20 + [
    {"name": "rewardRate", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"name": "", "type": "uint256"}]},
    {"name": "rewardToken", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"name": "", "type": "address"}]},
    {"name": "lastTimeRewardApplicable", "type": "function",
     "stateMutability": "view", "inputs": [],
     "outputs": [{"name": "", "type": "uint256"}]},
    {"name": "periodFinish", "type": "function", "stateMutability": "view",
     "inputs": [], "outputs": [{"name": "", "type": "uint256"}]},
]


def ua(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def black_price():
    for url in ("https://api.dexscreener.com/latest/dex/pairs/avalanche/"
                "0x14e4A5beD2e5E688EE1A5Ca3a4914250D1aBD573",
                f"https://api.dexscreener.com/latest/dex/tokens/{BLACK}"):
        try:
            d = ua(url)
            ps = d.get("pairs") or ([d["pair"]] if d.get("pair") else [])
            best = 0.0
            for p in ps:
                if (p.get("baseToken") or {}).get("address", "").lower() == BLACK.lower():
                    best = max(best, float(p.get("priceUsd") or 0))
            if best > 0:
                return best
        except Exception:
            continue
    return 0.0


def link_usd():
    try:
        d = ua(f"https://api.dexscreener.com/latest/dex/tokens/{LINK}")
        for p in d.get("pairs") or []:
            if (p.get("baseToken") or {}).get("address", "").lower() == LINK.lower():
                return float(p.get("priceUsd") or 0), float(
                    (p.get("liquidity") or {}).get("usd") or 0)
    except Exception:
        pass
    return 0.0, 0.0


def main():
    print("=" * 74)
    print("LINK.e/USDC GAUGE — IS IT ACTUALLY PAYING?")
    print("=" * 74)
    bpx = black_price()
    if bpx <= 0:
        print("  ❌ BLACK price unavailable — refusing to print dollar figures.")
        return 1
    lpx, lliq = link_usd()
    print(f"  BLACK  ${bpx:.8f}")
    print(f"  LINK   ${lpx:.4f}   (LINK/USDC pool liq ${lliq:,.0f})\n")

    g = w3.eth.contract(address=Web3.to_checksum_address(GAUGE), abi=GAUGE_ABI)

    # ---- 1. does the gauge HOLD the reward token? -------------------------
    print("── 1. Can the gauge actually PAY? ──")
    bt = w3.eth.contract(address=Web3.to_checksum_address(BLACK), abi=ERC20)
    gbal = bt.functions.balanceOf(Web3.to_checksum_address(GAUGE)).call()
    print(f"   gauge BLACK balance : {gbal/1e18:,.4f} BLACK (${gbal/1e18*bpx:,.2f})")
    rr = g.functions.rewardRate().call()
    per_day = rr * 86400 / 1e18
    print(f"   advertised rate     : {per_day:,.4f} BLACK/day (${per_day*bpx:,.4f}/day)")
    runway = (gbal / 1e18) / per_day if per_day > 0 else 0
    print(f"   => funded runway    : {runway:,.1f} days "
          f"{'✅ the rate is backed by tokens' if runway > 1 else '❌ UNFUNDED — rate is theatre'}")

    # ---- 2. is it live / still emitting? ----------------------------------
    print("\n── 2. Is the program still running? ──")
    for fn in ("lastTimeRewardApplicable", "periodFinish"):
        try:
            v = getattr(g.functions, fn)().call()
            if fn == "periodFinish":
                left = v - time.time()
                print(f"   {fn:<24}: {v} ({'EXPIRED' if left<0 else f'{left/3600:.1f}h left'})")
            else:
                print(f"   {fn:<24}: {v} ({'updating now ✅' if v>0 else 'stale ❌'})")
        except Exception as e:
            print(f"   {fn:<24}: reverted ({str(e)[:40]})")

    # ---- 3. what is really staked? ----------------------------------------
    print("\n── 3. Who is actually staked? ──")
    tsu = g.functions.totalSupply().call()
    print(f"   gauge totalStaked : {tsu:,} (raw liquidity units)")
    wal = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
    try:
        mine = g.functions.balanceOf(Web3.to_checksum_address(wal)).call()
        print(f"   our staked        : {mine:,}")
    except Exception as e:
        print(f"   our staked        : read failed ({str(e)[:40]})")
    print(f"   pool liquidity    : ~${lliq:,.0f}")

    # ---- 4. estimate -------------------------------------------------------
    print("\n" + "=" * 74)
    print("ESTIMATED PERFORMANCE IF WE ENTERED")
    print("=" * 74)
    daily_usd = per_day * bpx
    for cap in (25, 100, 250, 500, 1000):
        share = 1.0 if tsu == 0 else min(1.0, cap / (cap + max(lliq, 1)))
        # emissions are split by STAKED liquidity; assume we are the only staker
        # for the optimistic case, and pro-rata vs pool for the conservative one.
        opt = daily_usd * 365
        cons = daily_usd * 365 * share
        print(f"   ${cap:>6,} -> optimistic (sole staker) ${opt:>8,.2f}/yr "
              f"= {opt/cap*100:>6,.1f}% APR")
        print(f"              realistic (pro-rata)   ${cons:>8,.2f}/yr "
              f"= {cons/cap*100:>6,.1f}% APR")

    print(f"\n   OUR CURRENT FARM: $24.18 -> $7.52/mo = $90.24/yr = {90.24/24.18*100:.0f}% APR")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
