#!/usr/bin/env python3
"""vfat Blackhole pool helper — fetch live WAVAX/USDC pool APR from vfat.

vfat's search matches TOKEN/pool names, not protocol names. "Blackhole" as a
protocol filter returns nothing; searching "WAVAX" on Avalanche (concentrated)
returns the pool. This helper queries vfat's public API directly (HTTP, more
reliable than the flaky MCP) and returns the live fee/emissions APR split.

Pool: Blackhole WAVAX/USDC CL (Algebra V3) — 0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7
Gauge: 0x3ade52f9779c07471f4b6d5997444c3c2124c1c0 (THENA_V3)

Usage:
  python3 vfat_blackhole.py            # print human summary
  python3 vfat_blackhole.py --json     # machine-readable
"""
import json
import sys
import urllib.request

POOL = "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7".lower()
GAUGE = "0x3ade52f9779c07471f4b6d5997444c3c2124c1c0".lower()
API = "https://api.vfat.io/v4/yield-opportunities"
# DefiLlama yield pool id for Blackhole WAVAX-USDC (blackhole-clmm)
DEFILLAMA_POOL_ID = "2b42e1cd-5e65-4e1a-9df4-fb324a41e3cd"
DEFILLAMA_API = "https://yields.llama.fi/pools"


def fetch_defillama() -> dict:
    """Query DefiLlama for the Blackhole WAVAX-USDC pool. DefiLlama attributes
    ALL APR to rewards (apyBase=0 for this CL pool) — it does NOT split the
    swap-fee component like vfat does. So this is a DISCOVERY + TVL source,
    not a fee/emissions split. Returns the raw DefiLlama numbers."""
    try:
        req = urllib.request.Request(DEFILLAMA_API, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode())
        for p in data.get("data", []):
            if p.get("pool") == DEFILLAMA_POOL_ID:
                return {
                    "pool": p.get("pool"),
                    "project": p.get("project"),
                    "symbol": p.get("symbol"),
                    "chain": p.get("chain"),
                    "apy": p.get("apy"),
                    "apyBase": p.get("apyBase"),
                    "apyReward": p.get("apyReward"),
                    "tvl_usd": p.get("tvlUsd"),
                    "reward_tokens": p.get("rewardTokens"),
                    "source": "defillama",
                }
        return {"error": "pool not found in DefiLlama"}
    except Exception as e:
        return {"error": f"defillama down ({e})"}


def fetch() -> dict:
    """Query vfat for the Blackhole WAVAX/USDC pool, return the live APR split.
    Falls back to last-known-good (verified Sep 9 2026) when vfat is down,
    clearly labeled as cached — never a fabricated number."""
    # vfat search matches token names — search "WAVAX" on Avalanche concentrated.
    params = "?chainIds=43114&farmTypes=concentrated&search=WAVAX&pageSize=20"
    try:
        req = urllib.request.Request(API + params, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        # vfat down (transient 500) — fall back to last-known-good, labeled cached
        return {
            "pool": POOL,
            "gauge": GAUGE,
            "fee_apr": 26.9,
            "emis_apr": 189.6,
            "total_apr": 216.5,
            "tvl_usd": 710326.30,
            "in_range_usd": 105396.40,
            "rewards_per_week": 14690.82,
            "source": "vfat-cached (Sep 9 2026)",
            "error": f"vfat down ({e}) — using cached verified numbers",
        }
    items = data.get("items", data.get("data", {}).get("items", []))
    # Find our pool by address
    for it in items:
        pool = it.get("pool", {})
        if pool.get("address", "").lower() == POOL:
            # options[0] is the lp-stake (gauge) — has the APR split
            for opt in it.get("options", []):
                if opt.get("address", "").lower() == GAUGE:
                    comps = opt.get("aprBasis", {}).get("components", [])
                    fee_apr = 0.0
                    emis_apr = 0.0
                    for c in comps:
                        if c.get("kind") == "swapFees":
                            fee_apr = c.get("aprPercent", 0.0)
                        elif c.get("kind") == "staking":
                            emis_apr = c.get("aprPercent", 0.0)
                    return {
                        "pool": POOL,
                        "gauge": GAUGE,
                        "fee_apr": round(fee_apr, 1),
                        "emis_apr": round(emis_apr, 1),
                        "total_apr": round(fee_apr + emis_apr, 1),
                        "tvl_usd": opt.get("totalLiquidity"),
                        "in_range_usd": opt.get("inRangeLiquidity"),
                        "rewards_per_week": opt.get("rewardsPerWeek"),
                        "source": "vfat",
                    }
    return {"error": "pool not found in vfat results"}


if __name__ == "__main__":
    res = fetch()
    if "--json" in sys.argv:
        print(json.dumps(res, indent=2))
    else:
        if "error" in res:
            print(f"❌ {res['error']}")
        else:
            print(f"🕳️  Blackhole WAVAX/USDC (vfat live)")
            print(f"  Swap fees: {res['fee_apr']}% APR · BLACK emis: {res['emis_apr']}% APR")
            print(f"  Total: {res['total_apr']}% APR")
            print(f"  TVL: ${res['tvl_usd']:,.0f} · in-range: ${res['in_range_usd']:,.0f}")
