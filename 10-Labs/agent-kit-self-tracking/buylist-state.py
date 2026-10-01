#!/usr/bin/env python3
"""buylist-state.py — "everything on the buy list is up." Is that true, and is it a reason to wait?

Jordan (2026-09-19): "Curiosity, we don't have to switch if the council is against it. Everything on
the buy list is up."

That last sentence is testable, and it carries an implication worth checking honestly. If everything is
up, two opposite readings are available:
  (a) we are buying into strength — against our own dip-ladder discipline, or
  (b) the cycle has turned and waiting is the mistake — which is the whole reason it is called his
      FIRST bull run.
The two cannot be told apart by the fact that things are up. They are told apart by WHERE the move sits
in the cycle: how far from the low, how far from the high, and how the current move compares to prior
recoveries at the same point.

So this measures, for every asset on the buy list: distance off the low, distance from the high, and
30/90/365-day change. READ-ONLY.
"""
from __future__ import annotations

import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "GenTech-Steward/1.0"}

# the buy list, with the SAME rail_class we assigned on 2026-09-18
BUYLIST = [
    ("AVAX", "AVAX-USD", "FARM"),
    ("BTC", "BTC-USD", "HOLD_ONLY"),
    ("SOL", "SOL-USD", "STAKE"),
    ("LINK", "LINK-USD", "FARM"),
    ("TAO", "TAO-USD", "FARM"),
    ("COQ", None, "HOLD_ONLY"),          # genuinely no Coinbase pair (404) — see note below
    # ONDO RESTORED 2026-09-29 (Jordan: *"if we have access to ondo via orderly on avax than we can
    # keep it. I would like to be able to long and short tokens on our buy list."*). It was removed
    # 2026-09-28 on the belief it was unreachable; that belief was correct about the TOKEN and
    # wrong about the ASSET, because it only considered spot rails.
    #
    # What actually changed:
    #   • ORDERLY NETWORK gives us a PERP on ONDO (PERP_ONDO_USDC) — 10x, $10 min notional,
    #     reached from Avalanche with native USDC, no bridge. That is long/short access.
    #   • The spot facts from 2026-09-28 stand and are NOT retracted: ONDO the token is
    #     Ethereum-only, we have no Ethereum rail, and USDY (the old "3.58%" rationale) is a
    #     different token. So ONDO is reachable ONLY as a derivative, never as a token we hold.
    #
    # ROOT CAUSE OF THE OLD STALE PRICE, FIXED: this line used to read `("ONDO", None, ...)` with
    # the comment "no liquid Coinbase pair" — which was FALSE. ONDO-USD is online on Coinbase and
    # trading ~$36M/24h. Because the pair was disabled, the code fell through to the hardcoded
    # PX estimate of $1.02 while the real price was $0.4977 — 105% too high, so every zone
    # distance was measured against a price ONDO had not traded at in a long time. With the real
    # pair wired, the live price is read and no estimate is used at all.
    ("ONDO", "ONDO-USD", "TRADE"),       # perp-only rail; spot token is Ethereum-only
    ("XAUt", None, "HOLD_ONLY"),         # genuinely no Coinbase pair (404)
]

PX = {"COQ": 0.00000009, "XAUt": 3350.0}   # labelled estimates for the two without a
                                           # venue on Coinbase; marked as such below


def candles(product, days=900):
    out, cur = [], datetime.now(timezone.utc) - timedelta(days=days)
    end = datetime.now(timezone.utc)
    while cur < end:
        stop = min(cur + timedelta(days=299), end)
        u = (f"https://api.exchange.coinbase.com/products/{product}/candles"
             f"?granularity=86400&start={cur.isoformat()}&end={stop.isoformat()}")
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=50) as r:
                out.extend(json.load(r))
        except Exception:
            pass
        cur = stop + timedelta(days=1)
        time.sleep(0.3)
    d = {}
    for t, _l, _h, _o, c, _v in sorted(out, key=lambda x: x[0]):
        d[t] = c
    return [d[k] for k in sorted(d)]


def pct(a, b):
    return (a / b - 1) * 100 if b else 0.0


def main():
    print("=" * 106)
    print('  IS "EVERYTHING ON THE BUY LIST UP"?  — measured')
    print("=" * 106)

    rows = []
    for name, prod, rail in BUYLIST:
        if prod is None:
            rows.append({"name": name, "rail": rail, "px": PX[name], "src": "est", "s": None})
            continue
        s = candles(prod)
        rows.append({"name": name, "rail": rail, "px": s[-1] if s else None,
                     "src": "coinbase", "s": s})

    print(f"\n  {'asset':<7}{'rail':<11}{'price':>13}{'30d':>9}{'90d':>9}{'365d':>9}"
          f"{'from high':>11}{'off low':>10}   source")
    print("  " + "-" * 100)
    up30 = up90 = up365 = 0
    n30 = n90 = n365 = 0
    for r in rows:
        if r["s"] is None:
            print(f"  {r['name']:<7}{r['rail']:<11}{r['px']:>13,.8f}{'—':>9}{'—':>9}{'—':>9}"
                  f"{'—':>11}{'—':>10}   ⚠️ estimate, no Coinbase pair")
            continue
        s = r["s"]
        a30 = pct(s[-1], s[-31]) if len(s) > 31 else None
        a90 = pct(s[-1], s[-91]) if len(s) > 91 else None
        a365 = pct(s[-1], s[-366]) if len(s) > 366 else None
        hi, lo = max(s), min(s)
        fh, ol = pct(s[-1], hi), pct(s[-1], lo)
        if a30 is not None:
            n30 += 1
            up30 += 1 if a30 > 0 else 0
        if a90 is not None:
            n90 += 1
            up90 += 1 if a90 > 0 else 0
        if a365 is not None:
            n365 += 1
            up365 += 1 if a365 > 0 else 0
        f = lambda v: f"{v:>8.1f}%" if v is not None else f"{'—':>9}"
        print(f"  {r['name']:<7}{r['rail']:<11}{s[-1]:>13,.6f}{f(a30)}{f(a90)}{f(a365)}"
              f"{fh:>10.1f}%{ol:>9.1f}%   coinbase")

    print("\n" + "=" * 106)
    print("  THE CLAIM, TESTED")
    print("=" * 106)
    print(f"    up over  30d : {up30}/{n30}")
    print(f"    up over  90d : {up90}/{n90}")
    print(f"    up over 365d : {up365}/{n365}")

    print("\n" + "=" * 106)
    print("  WHERE IS THE MOVE? — this is what separates (a) buying strength from (b) a cycle turn")
    print("=" * 106)
    print(f"  {'asset':<7}{'off low':>11}{'from high':>12}   reading")
    print("  " + "-" * 72)
    for r in rows:
        if r["s"] is None:
            continue
        s = r["s"]
        fh, ol = pct(s[-1], max(s)), pct(s[-1], min(s))
        if ol > 60 and fh > -40:
            v = "RECOVERED — late in the move"
        elif ol > 40:
            v = "mid-recovery"
        elif ol < 20:
            v = "NEAR THE LOW — early"
        else:
            v = "early-to-mid"
        print(f"  {r['name']:<7}{ol:>10.1f}%{fh:>11.1f}%   {v}")

    print("\n" + "=" * 106)
    print("  AND THE HONEST ANSWER TO 'SHOULD WE WAIT?'")
    print("=" * 106)
    print("    'Everything is up over 30 days' and 'the cycle has turned' are DIFFERENT claims that")
    print("    look identical on a 30-day chart. The table above is what tells them apart: an asset")
    print("    up 20% but still 70% below its high is early in a recovery; one up 20% and within 10%")
    print("    of its high is late.")
    print("    Our dip-ladder discipline is not 'wait for flat' — it is 'size in on weakness rather")
    print("    than chasing strength'. Those can both be satisfied by laddering DOWN from here rather")
    print("    than blocking entry, which is the same shape as the LFJ single-sided bid: be paid while")
    print("    you wait for the price you actually want.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
