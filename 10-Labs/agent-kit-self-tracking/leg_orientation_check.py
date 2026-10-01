#!/usr/bin/env python3
"""
leg_orientation_check.py — is a tenant's ASK leg deployed the right way round?

Jordan, 2026-09-22: "By default check both of our pages for the same bug."

The bug (fixed in lfj_bid_deploy.py): the ask branch built its deltaIds ASCENDING while the bid
branch built them DESCENDING, and both feed one weights() that assumes the LAST entry is the bin
NEAREST spot. So the heaviest weight landed on the bin FURTHEST from spot — the ask leg deployed
INVERTED, stacking the bulk of the WAVAX at the far edge where it earns last.

This is a DEFAULT check, not a one-off: run it for EVERY active tenant, every time, because they
were all deployed by the same script and the bug is invisible in the headline numbers.

Exit 0 = all legs oriented correctly. Exit 1 = at least one inverted (or unreadable).
"""
import json
import os
import sys
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; GenTech/1.0)"}
BASE = "https://gentechlabs.net/DeFi/defi-data-{t}.json"
TENANTS = os.environ.get("STEWARD_CHECK_TENANTS", "jordan,dadrian").split(",")


def fetch(t):
    req = urllib.request.Request(BASE.format(t=t), headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def orientation(leg, act, label):
    """Return (ok, report). ok is None when the leg is absent/unreadable (NOT a pass)."""
    if not leg:
        return None, f"  {label}: NO BINS — cannot judge orientation (position may be one-sided)"
    leg = sorted(leg, key=lambda b: abs(b["bin"] - act))
    near, far = leg[0], leg[-1]
    if near["usd"] == 0 and far["usd"] == 0:
        return None, f"  {label}: all bins report $0 — cannot judge (do NOT read as healthy)"
    ratio = near["usd"] / far["usd"] if far["usd"] else float("inf")
    ok = near["usd"] > far["usd"]
    verdict = "toward spot  OK" if ok else "AWAY from spot  <-- INVERTED"
    return ok, (f"  {label}: nearest ${near['usd']:>7.2f} (bin {near['bin']})  "
                f"furthest ${far['usd']:>7.2f} (bin {far['bin']})  "
                f"ratio {ratio:>6.2f}  ->  {verdict}")


def main():
    all_ok = True
    for t in TENANTS:
        print(f"\n═══ {t.upper()} ═══")
        try:
            d = fetch(t)
        except Exception as e:
            print(f"  ❌ could not read page data: {type(e).__name__}: {e}")
            all_ok = False
            continue

        act = d.get("active_id")
        shape = d.get("shape") or []
        if act is None or not shape:
            print(f"  ❌ no active_id/shape in the feed — cannot judge (NOT a pass)")
            all_ok = False
            continue

        below = [b for b in shape if b["bin"] < act]
        above = [b for b in shape if b["bin"] > act]

        total = sum(b["usd"] for b in shape) or 0
        n3 = sum(b["usd"] for b in shape if abs(b["bin"] - act) <= 3)
        print(f"  capital ${total:,.2f} | spot at {d.get('spot_pos_in_range_pct')}% of range "
              f"| within 3 bins of spot: {n3/total*100 if total else 0:.1f}%")

        for leg, label in ((below, "BID leg (below spot)"), (above, "ASK leg (above spot)")):
            ok, rep = orientation(leg, act, label)
            print(rep)
            if ok is False:
                all_ok = False
                print("     ⚠️  This is the inverted-ask bug. Re-deploying it correctly is a "
                      "CAPITAL ACTION — flag to Jordan, do not move funds autonomously.")

    print()
    print("  ✅ no inverted legs" if all_ok else
          "  🔴 at least one leg inverted or unreadable")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
