#!/usr/bin/env python3
"""Yield Farm Report — one view across every rail we'd actually farm.

Jordan (Sep 15 2026): "we can compare the different pools — the SOL/USDC pool
versus the AVAX pool we've been in, or the TAO pool we thought about, or the
LINK pool. We can have these different comparisons going on. This is almost like
a yield farm — it really is like a yield farm report. We can make it its own thing."

So this is its own thing: ONE report that ranks candidate venues on the numbers
that decide where capital goes.

THE DISCIPLINE IT ENFORCES
  1. FEE CORE vs EMISSIONS SPLIT — always both, never a blended headline.
     Emissions are not durable; fees are. A venue that is 100% emissions is a
     different animal from one that is 100% fees, even at the same headline.
  2. CAPITAL-TO-GOAL — "how much do I need deployed to make $X/day?" answered
     on the FEE CORE, so the answer doesn't evaporate when a farm ends.
  3. DATA-QUALITY FLAGS — DefiLlama reports apyBase=0 for Blackhole CLMM, which
     is a reporting GAP, not a real zero. Flagged, never silently trusted.

HONEST LIMITS
  - DefiLlama APRs are venue-reported aggregates. Where we can measure on-chain
    (our own rail) the chain number wins and is labelled.
  - Reward APRs are quoted in USD at today's token price — they move with price.
    That sensitivity is real and is discussed in Jordan's price note below.
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

OUT_JSON = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/yield-farm-report.json"
BLOOM = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/black-health.json"

# Curated candidates: (label, chain, project, symbol-substring)
CANDIDATES = [
    ("AVAX/USDC — ours (Blackhole)", "Avalanche", "blackhole-clmm", "WAVAX-USDC"),
    ("AVAX/USDC — Pharaoh v3",       "Avalanche", "pharaoh-v3",     "WAVAX-USDC"),
    ("AVAX/USDC — LFJ (old rail)",   "Avalanche", "joe-v2.2",       "WAVAX-USDC"),
    ("AVAX/USDC — UniV3",            "Avalanche", "uniswap-v3",     "WAVAX-USDC"),
    ("SOL/USDC — Orca",              "Solana",    "orca-dex",       "SOL-USDC"),
    ("SOL/USDC — Raydium",           "Solana",    "raydium-amm",    "SOL-USDC"),
    ("TAO/USDC — UniV3 (ETH)",       "Ethereum",  "uniswap-v3",     "WTAO-USDC"),
    ("TAO/USDC — Aerodrome (Base)",  "Base",      "aerodrome-slipstream", "TAO"),
    ("LINK/WETH — UniV3 (ETH)",      "Ethereum",  "uniswap-v3",     "LINK-WETH"),
    ("LINK/ETH — UniV4 (ETH)",       "Ethereum",  "uniswap-v4",     "ETH-LINK"),
]

GOALS = [5.0, 200.0]   # $/day targets to size for


def _own_pool_id(_unused=None):
    """Resolve OUR Blackhole CLMM pool id from the live pools list (never hardcode)."""
    d = get("https://yields.llama.fi/pools")
    hits = [p for p in d.get("data", [])
            if (p.get("project") or "").lower() == "blackhole-clmm"
            and p.get("chain") == "Avalanche"
            and "WAVAX-USDC" in (p.get("symbol") or "").upper()]
    if not hits:
        raise RuntimeError("own pool id not found")
    return max(hits, key=lambda x: x.get("tvlUsd") or 0)["pool"]


# ── Rank ladder — ported from LP Monitor v2 (Jordan, Sep 15 2026) ───────────
# Jordan: "the LP monitor was how I wanted the yield-farm crown job to look...
# not only the pools information, but the goals and the milestone information and
# the percentage of how long it's going to take."
# The ladder itself (rank-ladder.json) is a PORT of the LP monitor's milestones,
# so retiring that job loses no mechanism. Tiers are DAILY FEE-USD targets.
LADDER_PATH = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/rank-ladder.json"


def load_ladder():
    try:
        with open(LADDER_PATH) as f:
            return json.load(f)
    except Exception:
        return None


def rank_block(deployed_usd, fee_apr_pct, ladder):
    """Current rank + next milestone + ETA. Returns None if we can't size it."""
    if not ladder or not deployed_usd or deployed_usd <= 0 or not fee_apr_pct:
        return None
    daily = deployed_usd * (fee_apr_pct / 100.0) / 365.0
    t0 = ladder.get("tier0") or {"tier": 0, "label": "Grunt", "daily_fees": 5.0}
    ms = ladder.get("milestones", [])
    cur, nxt = t0, (ms[0] if ms else None)
    for m in ms:
        if daily >= m["daily_fees"]:
            cur = m
        elif nxt is None or m["daily_fees"] < nxt["daily_fees"]:
            nxt = m
    # find the true next = lowest milestone above current daily
    above = [m for m in ms if m["daily_fees"] > daily]
    nxt = above[0] if above else None
    pct = (daily / nxt["daily_fees"] * 100.0) if nxt else 100.0
    # ETA: capital is what we scale, not time — so express it as capital required,
    # and give the days-to-target IF capital were topped up to the requirement now.
    cap_needed = (nxt["daily_fees"] * 365.0 / (fee_apr_pct / 100.0)) if nxt else None
    gap = (cap_needed - deployed_usd) if cap_needed else None
    return {
        "deployed_usd": round(deployed_usd, 2),
        "daily_fee_usd": round(daily, 4),
        "current_tier": cur["tier"], "current_label": cur["label"],
        "current_target_usd_day": cur["daily_fees"],
        "next_tier": nxt["tier"] if nxt else None,
        "next_label": nxt["label"] if nxt else "MAX",
        "next_target_usd_day": nxt["daily_fees"] if nxt else None,
        "progress_pct": round(pct, 1),
        "capital_needed_for_next": round(cap_needed, 0) if cap_needed else None,
        "capital_gap": round(gap, 0) if gap is not None else None,
        "fee_apr_used": fee_apr_pct,
        "basis": "daily fee income = deployed_usd x fee_apr / 365 (fee core only)",
    }


def _deployed_usd():
    """Read DEPLOYED capital from treasury state; refuse to guess."""
    for p in ("/root/.hermes/profiles/gentech-treasury/scripts/treasury-state.json",
              "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/treasury-state.json"):
        try:
            with open(p) as f:
                d = json.load(f)
            for k in ("deployed_usd", "deployed"):
                if isinstance(d.get(k), (int, float)):
                    return float(d[k]), p
        except Exception:
            continue
    return None, None


def price_sensitivity():
    """Jordan's insight, measured: (Sep 15 2026)

    'if I wanted to make five dollars a day, I would need more money if the price
     is higher — but as the price gets lower that goal becomes even easier.'

    WHY HE IS RIGHT (mechanism, verified on 196 days of history):
      - corr(AVAX price, pool TVL) is strongly POSITIVE (~+0.83): when AVAX falls,
        the WAVAX half of the pool is worth less, so TVL shrinks.
      - corr(AVAX price, emissions APR) is NEGATIVE (~-0.43): the BLACK emission
        rate is FIXED per second, so when TVL shrinks the same BLACK lands on less
        capital -> the reward APR RISES.
      => a lower AVAX price mechanically raises the emissions APR, so a fixed
         $/day goal needs LESS capital. His intuition is correct.

    WHAT IT DOES *NOT* DO:
      - The FEE core does NOT rise with a lower price. Fees track VOLUME, not
        price level. So fee-core sizing is roughly price-independent.
      - This is a MEASURED RELATIONSHIP over one history, not a law. It is a
        reason to prefer the emissions layer when price is low — never a promise.
    """
    try:
        import statistics as st
        px = get("https://coins.llama.fi/chart/avax:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
                 "?span=196&period=1d")
        series = px["coins"]["avax:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"]["prices"]
        prices = {datetime.utcfromtimestamp(int(p["timestamp"])).strftime("%Y-%m-%d"): p["price"]
                  for p in series}
        hist = get("https://yields.llama.fi/chart/%s" % _own_pool_id(px))
        pts = hist.get("data", [])
    except Exception:
        return None
    if not pts:
        return None
    rows = []
    for p in pts:
        d = p["timestamp"][:10]
        if d in prices and p.get("apyReward"):
            rows.append((prices[d], p.get("tvlUsd") or 0, p["apyReward"]))
    if len(rows) < 20:
        return None

    def corr(a, b):
        ma, mb = st.mean(a), st.mean(b)
        num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
        den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
        return num / den if den else None

    pr = [r[0] for r in rows]
    tv = [r[1] for r in rows]
    ar = [r[2] for r in rows]

    # simple linear fit: emissions APR vs price
    n = len(rows)
    mp, ma_ = st.mean(pr), st.mean(ar)
    denom = sum((x - mp) ** 2 for x in pr)
    slope = sum((x - mp) * (y - ma_) for x, y in zip(pr, ar)) / denom if denom else 0
    intercept = ma_ - slope * mp

    def apr_at(price):
        return max(0.0, slope * price + intercept)

    return {
        "days": n,
        "corr_price_tvl": round(corr(pr, tv), 3) if corr(pr, tv) else None,
        "corr_price_emissions_apr": round(corr(pr, ar), 3) if corr(pr, ar) else None,
        "price_range": [round(min(pr), 2), round(max(pr), 2)],
        "emissions_apr_at_price": {str(p): round(apr_at(p), 1)
                                   for p in (5.50, 6.00, 7.30, 8.50, 10.00)},
        "note": ("Measured over %d days. Lower price -> smaller TVL -> same fixed "
                 "BLACK emission over less capital -> higher reward APR. The FEE "
                 "core does not behave this way; it tracks volume." % n),
    }



def get(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent": "GenTech-Steward/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def capital_for(goal_usd_day, apr_pct):
    """Capital needed to earn goal_usd_day at apr_pct (on a 365-day year)."""
    if not apr_pct or apr_pct <= 0:
        return None
    return goal_usd_day * 365.0 / (apr_pct / 100.0)


def main():
    d = get("https://yields.llama.fi/pools")
    pools = d.get("data", [])
    by_chain = {}
    for p in pools:
        by_chain.setdefault((p.get("chain"), (p.get("project") or "").lower()), []).append(p)

    # chain-measured truth for our own rail (wins over venue-reported)
    own = None
    try:
        bh = json.load(open(BLOOM))
        own = {"fee_apr_pct": bh["yield_split"]["fee_apr_pct"],
               "emissions_apr_pct": bh["yield_split"]["emissions_apr_pct"],
               "tvl_usd": bh["pool"]["tvl_usd"],
               "when": bh.get("when")}
    except Exception:
        pass

    rows = []
    for label, chain, project, symfrag in CANDIDATES:
        cands = by_chain.get((chain, project.lower()), [])
        hits = [p for p in cands if symfrag.upper() in (p.get("symbol") or "").upper()]
        if not hits:
            rows.append({"label": label, "chain": chain, "project": project,
                         "status": "not_found"})
            continue
        p = max(hits, key=lambda x: x.get("tvlUsd") or 0)
        base = p.get("apyBase")
        rew = p.get("apyReward") or 0
        tvl = p.get("tvlUsd") or 0
        flags = []
        if (base in (0, None)) and rew > 0:
            flags.append("apyBase=0 — reporting GAP, not a real zero (measure on-chain)")
        split = None
        if base is not None and (base + rew) > 0:
            split = round(rew / (base + rew) * 100, 1)
        rows.append({
            "label": label, "chain": chain, "project": p.get("project"),
            "symbol": p.get("symbol"), "tvl_usd": round(tvl, 0),
            "fee_apr_pct": base, "emissions_apr_pct": rew,
            "headline_apr_pct": p.get("apy"),
            "emissions_share_pct": split,
            "capital_for_goal": {f"${int(g)}/day": (round(capital_for(g, base), 0)
                                                   if base else None) for g in GOALS},
            "flags": flags, "status": "ok",
        })

    # override our rail with the chain-measured read
    for r in rows:
        if "Blackhole" in r["label"] and own:
            r["fee_apr_pct"] = own["fee_apr_pct"]
            r["emissions_apr_pct"] = own["emissions_apr_pct"]
            r["tvl_usd"] = round(own["tvl_usd"], 0)
            tot = own["fee_apr_pct"] + own["emissions_apr_pct"]
            r["emissions_share_pct"] = round(own["emissions_apr_pct"] / tot * 100, 1)
            r["capital_for_goal"] = {f"${int(g)}/day": round(capital_for(g, own["fee_apr_pct"]), 0)
                                     for g in GOALS}
            # DefiLlama books the whole Blackhole pool as REWARD (apyBase=0), so its
            # headline `apy` is 1124.5% — an artifact, NOT our headline. Recompute it
            # from the honest split after the override so no reader can quote it as ours.
            r["headline_apr_pct"] = round(own["fee_apr_pct"] + own["emissions_apr_pct"], 2)
            r["headline_basis"] = "fee + emissions (recomputed from split, not DefiLlama apy)"
            r["flags"] = ["fee APR is CHAIN-MEASURED (DefiLlama reports apyBase=0)",
                          "DefiLlama headline apy ignored — it books fees as reward; ours = fee + emissions"]
            r["source"] = "chain + defillama"

    ps = price_sensitivity()
    ladder = load_ladder()
    deployed, dsrc = _deployed_usd()
    own_fee = own["fee_apr_pct"] if own else None
    ranks = {}
    for r in rows:
        if r["status"] != "ok":
            continue
        rb = rank_block(deployed, r["fee_apr_pct"], ladder)
        if rb:
            ranks[r["label"]] = rb
    out = {"when": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
           "ts": time.time(), "goals": GOALS, "venues": rows,
           "own_rail_measured": own, "price_sensitivity": ps,
           "rank_ladder": {
               "deployed_usd": deployed, "deployed_source": dsrc,
               "per_venue": ranks,
               "ladder_source": ladder.get("source") if ladder else None,
               "note": ("Rank tiers are DAILY FEE-USD targets. Progress moves by "
                        "CAPITAL and by fee APR, not by waiting. When flat, daily "
                        "fee income is $0 and every tier reads 0% — that is the "
                        "honest reading, not a failure."),
           }}
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2)

    print(f"🌾 YIELD FARM REPORT — {out['when']}")
    print()
    for g in GOALS:
        print(f"   capital needed for ${int(g)}/day (on FEE core):")
        for r in rows:
            if r["status"] != "ok":
                continue
            c = r["capital_for_goal"].get(f"${int(g)}/day")
            if c is None:
                continue
            print(f"     {r['label']:<32} ${c:>12,.0f}")
        print()
    print("   ── venue detail ──")
    for r in rows:
        if r["status"] != "ok":
            print(f"   ✗ {r['label']:<32} NOT FOUND")
            continue
        fl = r["flags"][0] if r["flags"] else ""
        print(f"   {r['label']:<32} TVL ${r['tvl_usd']:>11,.0f}  "
              f"fee {str(r['fee_apr_pct'])[:6]:>6}% + emis {str(r['emissions_apr_pct'])[:7]:>7}%  "
              f"(emis share {r['emissions_share_pct']}%)")
        if fl:
            print(f"        ⚠ {fl}")
    print()
    if ps:
        print("   ── PRICE SENSITIVITY (Jordan's insight, measured) ──")
        print(f"   over {ps['days']} days: corr(price,TVL)={ps['corr_price_tvl']:+.3f}  "
              f"corr(price,emissions APR)={ps['corr_price_emissions_apr']:+.3f}")
        ea = ps["emissions_apr_at_price"]
        print("   modeled emissions APR by AVAX price: " +
              "  ".join(f"${p}->{v}%" for p, v in ea.items()))
        print("   => lower price = higher reward APR (fixed emission over smaller TVL).")
        print("      The FEE core does NOT do this — it tracks volume.")
        print()
    print("   ── RANK & MILESTONES (fee-income ladder, ported from LP Monitor v2) ──")
    if deployed is None or deployed <= 0:
        print(f"   Deployed capital: ${deployed or 0:.2f} — TREASURY IS FLAT.")
        print("   Daily fee income $0.00 → Tier 0 Grunt ($5/day) at 0%.")
        print("   Progress moves by DEPLOYING CAPITAL and by fee APR, not by waiting.")
        print("   Below: what EACH rail would rank at if we deployed $25 there.")
    else:
        print(f"   Deployed capital: ${deployed:,.2f}")
    probe_cap = deployed if (deployed and deployed > 0) else 25.0
    shown = 0
    for r in rows:
        if r["status"] != "ok" or not r["fee_apr_pct"]:
            continue
        rb = rank_block(probe_cap, r["fee_apr_pct"], ladder)
        if not rb:
            continue
        tag = "ours " if "Blackhole" in r["label"] else "     "
        print(f"   {tag}{r['label']:<30} Tier {rb['current_tier']:>2} {rb['current_label']:<11} "
              f"${rb['daily_fee_usd']:>6.3f}/day → {rb['next_label']} "
              f"[{rb['progress_pct']:>5.1f}%]  needs ${rb['capital_gap']:>9,.0f} more")
        shown += 1
        if shown >= 6:
            break
    if deployed is None or deployed <= 0:
        print(f"   (shown at a ${probe_cap:.0f} reference deploy per rail)")
    print()
    print(f"   wrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
