#!/usr/bin/env python3
"""Blackhole LINK.e/USDC CL pool — gauge, emissions, real economics.

Jordan: "I know for a fact there's a LINK... put their LINK pools on black hole"

Confirmed on-chain: pool 0x177a7376860a04eEA6BF7fb3F39Bf10c49D3b42C is a genuine
Algebra CL pool (globalState() answers). Liquidity is small ($465) but turnover
is high ($116/24h ≈ 25% of TVL/day). Now: does its gauge emit BLACK, and what
would we actually earn?
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
POOL = "0x177a7376860a04eEA6BF7fb3F39Bf10c49D3b42C"
GAUGE_MGR = "0x59aa177312Ff6Bdf39C8Af6F46dAe217bf76CBf6"
BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"
OUR_POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7"

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))


def main():
    print("=" * 70)
    print("BLACKHOLE LINK.e/USDC — farmable? economics?")
    print("=" * 70)

    # pool identity
    raw = w3.eth.call({"to": Web3.to_checksum_address(POOL),
                       "data": "0x" + keccak(text="globalState()").hex()[:8]})
    price = int.from_bytes(raw[0:32], "big")
    tick = int.from_bytes(raw[32:64][29:32], "big", signed=True)
    fee = int.from_bytes(raw[64:96][30:32], "big")
    print(f"  pool {POOL}")
    print(f"    globalState: price={price}  tick={tick}  fee={fee} ({fee/10000:.2f}%)")

    # gauge
    gm = Web3.to_checksum_address(GAUGE_MGR)
    data = "0x" + keccak(text="gauges(address)").hex()[:8] + "0" * 24 + POOL[2:].lower()
    try:
        r = w3.eth.call({"to": gm, "data": data})
        g = Web3.to_checksum_address("0x" + r.hex()[-40:])
        if int(g, 16) == 0:
            print("    gauge: none ❌ (no emissions possible)")
        else:
            print(f"    gauge: {g} ✅")
            rt_data = "0x" + keccak(text="rewardToken()").hex()[:8]
            rt = w3.eth.call({"to": g, "data": rt_data})
            rta = Web3.to_checksum_address("0x" + rt.hex()[-40:])
            print(f"    rewardToken: {rta} "
                  f"({'BLACK' if rta.lower()==BLACK.lower() else 'other'})")
    except Exception as e:
        print(f"    gauge lookup failed: {str(e)[:70]}")

    # stats
    print("\n  ── market ──")
    try:
        req = urllib.request.Request(
            "https://api.dexscreener.com/latest/dex/pairs/avalanche/" + POOL,
            headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        p = (d.get("pairs") or [{}])[0]
        liq = float((p.get("liquidity") or {}).get("usd") or 0)
        v24 = float((p.get("volume") or {}).get("h24") or 0)
        v6 = float((p.get("volume") or {}).get("h6") or 0)
        print(f"    liquidity ${liq:,.0f} | vol24h ${v24:,.0f} | vol6h ${v6:,.0f}")
        turnover = (v24 / liq * 100) if liq else 0
        print(f"    daily turnover: {turnover:.1f}% of TVL")

        fee_rate = 0.0025
        pool_fees = v24 * fee_rate
        print(f"\n  ── fee economics (whole pool) ──")
        print(f"    pool fee revenue/day : ${pool_fees:,.4f}")
        print(f"    pool fee APR on TVL  : {pool_fees*365/liq*100 if liq else 0:.1f}%")

        for usd in (11, 25, 50):
            share = usd / (liq + usd) if liq else 0
            day = pool_fees * share
            print(f"    our ${usd:>3} → {share*100:>5.2f}% share → ${day:.4f}/day "
                  f"= ${day*30:.2f}/mo = ${day*365:.2f}/yr")
    except Exception as e:
        print(f"    failed: {str(e)[:60]}")

    # comparison
    print("\n  ── vs our current core farm ──")
    print("    WAVAX/USDC CL (ours): ~100.7 BLACK/day + fees = ~$7.52/mo on ~$25")
    print("    LINK.e/USDC          : tiny TVL; check emission question above")


if __name__ == "__main__":
    main()
