#!/usr/bin/env python3
"""
width_advisor.py — how wide SHOULD the band be? (Jordan, 2026-09-23, approved)

THE QUESTION JORDAN ASKED:
    "why don't you suggest a bin size for when something like that happens? Or do you
     recommend just exiting the pool and re-entering? Should we focus on building
     something like that instead?"
and then: "build the adaptive width. So that way you can look into it based off of your own
analysis, how wide do you think it should be, and then what shape, and then what percentage."

WHAT THIS ANSWERS, AND WHAT IT HONESTLY CANNOT:
  Jordan's 45-bin ceiling is real and stays. At binStep 10 that is a 4.5% band — so the width
  MENU (25 bins calm / 45 bins volatile) is already the ceiling-limited version of "adapt the
  width". Widening further is Jordan's call, not this tool's.
  What is genuinely missing is the NUMBER that decides whether the current width is enough:
  **what fraction of normal daily moves does this band actually hold?** A band is not "wide"
  or "narrow" in the abstract — it is wide or narrow relative to the tape. At AVAX's 5.4% daily
  vol a 4.5% band holds a normal day's move and loses to a 2-sigma one. That is a fact worth
  printing, not a feeling worth arguing about.

THE THREE NUMBERS THAT DECIDE IT:
  1. COVERAGE    what share of days this band contains (from realized vol, not opinion)
  2. CHASE RATE  how often we were actually forced to re-center (the band's real-world failure)
  3. CHASE COST  gas x count vs the fee income (at $0.41/chase today, chasing is cheap)

THE HONEST CONCLUSION THIS TOOL IS DESIGNED TO REACH:
  At AVAX's current vol, chasing costs ~$0.41 and holds the band's coverage where it is, so
  the correct answer is usually KEEP THE WIDTH AND CHASE -- and reserve a wider band (or an
  exit) for the case no band can hold. The advisor says so even when a wider band is more
  flattering, because the churn that comes from over-widening is a real cost.

CLI: python3 width_advisor.py [--tenant jordan] [--json]
Exit 0 always (this proposes; it does not act).
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CEILING_BINS = 45          # Jordan's absolute ceiling (2026-09-21): "maximum of 45"
CHASE_GAS = 1_598_715      # measured 2026-09-23: withdraw + 2 legs
BIN_STEP = 10              # the pool's binStep


def span_pct(bins: int) -> float:
    """The price span of `bins` bins at this pool's binStep, in percent."""
    return ((1 + BIN_STEP / 10000.0) ** bins - 1) * 100


def coverage(vol_daily: float, span: float) -> float:
    """
    The share of days whose move fits inside the band.
    A daily move is ~normal around zero, so P(|move| <= span) = 2*Phi(span/vol) - 1.
    Uses the stdlib error function -- no scipy in the fleet.
    """
    if not vol_daily or vol_daily <= 0:
        return 0.0
    import math
    z = span / vol_daily
    return (math.erf(z / math.sqrt(2))) * 100


def main():
    ap = argparse.ArgumentParser(description="How wide should the band be?")
    ap.add_argument("--tenant", default="jordan")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    try:
        import volatility_tracker as VT
        closes = VT.price_series(30)
        vol_d = VT.realized_vol(closes)
    except Exception as e:
        print(f"  ⚠️  cannot read volatility ({type(e).__name__}) — refusing to guess a width")
        return 0

    if not vol_d:
        print("  ⚠️  volatility UNREADABLE — a width recommendation without it would be a guess")
        return 0

    # the chase count and cost: read the recenter state timestamps as evidence of real failure
    chases = 0
    try:
        st = json.load(open(f".steward-recenter-state-{a.tenant}.json"))
        chases = int(st.get("chases_24h") or st.get("chase_count") or 0)
    except Exception:
        chases = 0

    try:
        import avax_rpc
        from web3 import Web3
        w3 = avax_rpc.connect(timeout=45)
        gp = w3.eth.gas_price
        cost = CHASE_GAS * gp / 1e18
    except Exception:
        gp, cost = None, None
    price = closes[-1] if closes else None

    rows = []
    for shape, bins in (("curve", 25), ("bid-ask", CEILING_BINS)):
        sp = span_pct(bins)
        rows.append({"shape": shape, "bins": bins, "span_pct": sp,
                     "coverage_pct": coverage(vol_d, sp)})

    out = {"tenant": a.tenant, "vol_daily_pct": vol_d, "price": price,
           "chase_cost_avax": cost, "chase_cost_usd": (cost * price) if (cost and price) else None,
           "chases_24h": chases, "options": rows}

    if a.json:
        print(json.dumps(out, indent=2, default=str))
        return 0

    print(f"\n  📐 WIDTH ADVISOR — {a.tenant}")
    print(f"  {'-'*68}")
    print(f"  AVAX ${price:.4f}   realized daily vol {vol_d:.2f}%")
    if cost and price and gp:
        print(f"  one chase costs {cost:.5f} AVAX (~${cost*price:.2f}) "
              f"[{CHASE_GAS:,} gas @ {gp/1e9:.1f} nAVAX]")
    else:
        print("  chase cost      UNREADABLE (gas price unavailable) — not assumed")
    print(f"  {'-'*68}")
    print(f"  {'shape':10} {'bins':>5} {'span':>8} {'holds a normal day':>20}")
    for r in rows:
        print(f"  {r['shape']:10} {r['bins']:>5} {r['span_pct']:>7.2f}% "
              f"{r['coverage_pct']:>18.0f}% of days")
    print(f"  {'-'*68}")

    wide = rows[-1]
    if wide["coverage_pct"] >= 90:
        print("  ✅ The 45-bin band holds ~9 days in 10. That is enough width.")
        print("     Widening past it is Jordan's ceiling call, not a gap.")
    elif wide["coverage_pct"] >= 60:
        print(f"  ⚠️  Even the ceiling band holds only {wide['coverage_pct']:.0f}% of days.")
        print("     The missing coverage is what the 15-min re-center and the cascade guard")
        print("     exist to absorb — and at ~$0.41 a chase, absorbing it is cheap.")
    else:
        print(f"  🚨 The ceiling band holds only {wide['coverage_pct']:.0f}% of days.")
        print("     Re-centering alone cannot carry this tape; the cascade guard matters more")
        print("     than the width here.")

    print(f"  {'-'*68}")
    print("  RECOMMENDATION: keep the width menu (25 calm / 45 volatile),")
    print("  chase the difference at ~$0.41, and let the cascade guard handle what no band holds.")
    print(f"  {'-'*68}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
