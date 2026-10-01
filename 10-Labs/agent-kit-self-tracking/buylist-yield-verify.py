#!/usr/bin/env python3
"""buylist-yield-verify.py — is that APY real, or one good day annualized?

Reading the raw pool list showed TAO at 147% and 191% and LINK at 62% — numbers that would rewrite
the buy list if true and mislead it if they are artifacts. DefiLlama publishes apyPct1D / 7D / 30D
alongside the spot APY; if the spot number is 147% while the 7d is 12%, the headline is a spike, not
a yield. That test costs nothing and it is exactly the difference between a claim and a measurement.

READ-ONLY.
"""
from __future__ import annotations

import json
import urllib.request

WATCH = ["WTAO-WETH", "WTAO-USDC", "USDC-TAO", "ETH-WTAO", "SOL-TAO",
         "ETH-LINK", "LINK-WETH", "XAUT-PAXG"]

MIN_TVL = 50_000


def main():
    req = urllib.request.Request("https://yields.llama.fi/pools",
                                 headers={"User-Agent": "GenTech-Steward/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        pools = json.load(r)["data"]

    print("=" * 118)
    print("  IS THAT APY REAL? — spot vs 7d vs 30d, and what the pool actually earns")
    print("=" * 118)
    print(f"  {'pool':<22}{'chain':<12}{'project':<20}{'TVL':>11}{'spot':>9}{'7d':>9}{'30d':>9}"
          f"{'base':>8}{'rew':>8}  verdict")
    print("  " + "-" * 114)

    rows = []
    for p in pools:
        s = (p.get("symbol") or "")
        if s not in WATCH and s.upper() not in [w.upper() for w in WATCH]:
            continue
        if (p.get("tvlUsd") or 0) < MIN_TVL:
            continue
        spot = p.get("apy") or 0
        d7 = p.get("apyPct7D")
        d30 = p.get("apyPct30D")
        base = p.get("apyBase") or 0
        rew = p.get("apyReward") or 0
        rows.append((s, p, spot, d7, d30, base, rew))

    # sort: stable-looking first
    def stable(r):
        s, p, spot, d7, d30, base, rew = r
        vals = [v for v in (d7, d30) if v is not None]
        if not vals or spot <= 0:
            return 999
        return abs(spot - sum(vals) / len(vals))

    for s, p, spot, d7, d30, base, rew in sorted(rows, key=stable):
        v = stable((s, p, spot, d7, d30, base, rew))
        if v == 999:
            verdict = "no history — UNVERIFIED"
        elif v > spot * 2:
            verdict = "⚠️ SPIKE — history is a fraction of the headline"
        elif v > spot * 0.5:
            verdict = "⚠️ inconsistent"
        else:
            verdict = "✅ consistent with history"
        print(f"  {s[:20]:<22}{(p.get('chain') or '')[:10]:<12}{(p.get('project') or '')[:18]:<20}"
              f"{(p.get('tvlUsd') or 0):>11,.0f}{spot:>8.2f}%"
              f"{(f'{d7:.2f}%' if d7 is not None else 'n/a'):>9}"
              f"{(f'{d30:.2f}%' if d30 is not None else 'n/a'):>9}"
              f"{base:>7.2f}%{rew:>7.2f}%  {verdict}")

    print("\n  NOTE: 'base' is the fee leg and 'rew' is emissions. An APY that is mostly 'rew' is not")
    print("  durable income — it is a token we would have to sell, at a price we do not set.")


if __name__ == "__main__":
    main()
