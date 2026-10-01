#!/usr/bin/env python3
"""buylist-yield-rails.py — for every asset on the buy list, find WHERE it can actually earn.

Jordan (2026-09-18): "let's look for yield rails for all of the coins or tokens on the buy list.
And let's update the buy list so that, you know, we know for sure where there's yield, there could
be yield somewhere."

The buy list carried hand-written yield notes that had drifted: AVAX still read "Blackhole CL
(216% APR, ~27% fee core)" when our own measurements now say Blackhole ~47% fee core and LFJ
ahead of it. So this does not restate the notes — it goes and measures.

Method: pull the whole DefiLlama yield universe once, then for each asset report the pools that
actually exist, separating FEE income from EMISSIONS, and flagging IL exposure. TVL floors so a
$400 pool does not masquerade as a venue.

READ-ONLY. Writes a report to the vault, changes no position.
"""
from __future__ import annotations

import json
import time
import urllib.request
from collections import defaultdict

# ── the buy list, verbatim from steward-buylist.py ──────────────────────────
ASSETS = [
    ("BTC",  "Coin · L1",              "bitcoin"),
    ("SOL",  "Coin · L1",              "solana"),
    ("LINK", "Coin · Oracle infra",    "chainlink"),
    ("AVAX", "Coin · L1",              "avalanche-2"),
    ("TAO",  "Coin · AI infra",        "bittensor"),
    ("XAUt", "RWA · Commodity gold",   "tether-gold"),
    # ONDO restored 2026-09-29 as a TRADE (perp) rail — see steward-buylist.py. Spot token is
    # Ethereum-only; the reachable rail is Orderly's PERP_ONDO_USDC on Avalanche.
    ("ONDO", "RWA · Treasury yield",   "ondo-finance"),
    ("COQ",  "Coin · Memecoin",        "coq-inu"),
]

# symbols that mean the same asset across venues
ALIASES = {
    "BTC": ["BTC", "WBTC", "BTC.B", "CBBTC", "TBTC", "BTCB", "SBTC"],
    "SOL": ["SOL", "JUPSOL", "MSOL", "JITOSOL", "BSOL", "INF", "HSOL", "VSOL"],
    "LINK": ["LINK"],
    "AVAX": ["AVAX", "WAVAX", "SAVAX", "GGAVAX", "YYAVAX"],
    "TAO": ["TAO", "WTAO"],
    "XAUt": ["XAUT", "PAXG", "XAUT0"],
    # ONDO aliases: ONDO ONLY. The old list was ["ONDO","USDY","OUSG"] — but USDY and OUSG are
    # DIFFERENT TOKENS (Ondo Finance products, not ONDO itself). Keeping them here would attribute
    # their yield to ONDO — the precise defect that made the old entry claim "USDY 3.58%" as ONDO's
    # yield. An alias map may only contain things that ARE the asset.
    "ONDO": ["ONDO"],
    "COQ": ["COQ"],
}

TVL_FLOOR = 50_000          # a pool smaller than this is not a venue
TOP_N = 6


def fetch_pools():
    url = "https://yields.llama.fi/pools"
    req = urllib.request.Request(url, headers={"User-Agent": "GenTech-Steward/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)["data"]


def main():
    print("fetching the DefiLlama yield universe...")
    pools = fetch_pools()
    print(f"  {len(pools):,} pools total")

    by_chain = defaultdict(int)
    for p in pools:
        by_chain[p.get("chain")] += 1

    print("\n" + "=" * 104)
    print("  YIELD RAILS BY ASSET — where each buy-list asset can actually earn")
    print("=" * 104)

    report = {}
    for sym, cls, cg in ASSETS:
        names = ALIASES.get(sym, [sym])
        hits = []
        for p in pools:
            if (p.get("tvlUsd") or 0) < TVL_FLOOR:
                continue
            s = (p.get("symbol") or "").upper()
            # split "WAVAX-USDC" style pairs into legs
            legs = [x.strip() for x in s.replace("/", "-").split("-") if x.strip()]
            if not any(leg in names for leg in legs):
                continue
            hits.append(p)

        hits.sort(key=lambda p: -(p.get("tvlUsd") or 0))
        report[sym] = hits[:TOP_N]

        print(f"\n{'─'*104}")
        print(f"  {sym}  ({cls})   —  {len(hits)} pools above ${TVL_FLOOR:,} TVL")
        if not hits:
            print("     ⚠️  NOTHING FOUND above the TVL floor. Recorded as 'no measured rail' rather")
            print("         than left blank — a blank reads like we forgot to look.")
            continue
        print(f"     {'pool':<34}{'chain':<14}{'project':<20}{'TVL':>12}{'APY':>9}{'base':>8}{'rew':>8}  IL")
        for p in hits[:TOP_N]:
            name = (p.get("symbol") or "")[:32]
            apy = p.get("apy") or 0
            base = p.get("apyBase") or 0
            rew = p.get("apyReward") or 0
            ilr = p.get("ilRisk") or "?"
            flag = "⚠️" if (rew > base and apy > 0) else "  "
            print(f"     {name:<34}{(p.get('chain') or '')[:12]:<14}{(p.get('project') or '')[:18]:<20}"
                  f"{(p.get('tvlUsd') or 0):>12,.0f}{apy:>8.2f}%{base:>7.2f}%{rew:>7.2f}% {flag}{ilr}")

    json.dump({k: [{"symbol": p.get("symbol"), "chain": p.get("chain"), "project": p.get("project"),
                    "tvl": p.get("tvlUsd"), "apy": p.get("apy"), "apyBase": p.get("apyBase"),
                    "apyReward": p.get("apyReward"), "ilRisk": p.get("ilRisk"),
                    "pool": p.get("pool")} for p in v] for k, v in report.items()},
              open("/tmp/yield-rails.json", "w"), indent=2)
    print(f"\n  saved -> /tmp/yield-rails.json")
    print("\n  ⚠️  = APY is majority EMISSIONS, not fees. Emissions are not durable income.")


if __name__ == "__main__":
    main()
