#!/usr/bin/env python3
"""test_leg_orientation.py — lock the leg-orientation detector against its own FALSE ALARMS.

WHY THIS EXISTS. On 2026-09-26 this detector produced a false "INVERTED" on a correct book THREE
times in one day. Every cut was shipped against the live hub only, so the only way to see a
regression was for Jordan to open his own page and be told his healthy position was built upside
down. That is not a test, it is a user finding our bugs for us.

The three cuts, and what each one lied about:
  1. bell-only  -> flagged EVERY correct bid-ask (jordan's healthy 45-bin book, both legs).
  2. shape-aware but split by spot side -> flagged a CROSSED book (dadrian, ask leg).
  3. run-based + refuses to judge a crossed book -> the cases below.

Every case below is a REAL book measured on chain today, or the arithmetic consequence of one.
Run it after ANY change to _leg_orientation. A check that cannot fail is not a check, so the
false-alarm cases are asserted just as hard as the true-positive one.

    python3 test_leg_orientation.py        # exit 0 = pass
"""
import sys

sys.path.insert(0, "/root/vaults/gentech/10-Labs/agent-kit-self-tracking")
from defi_hub_data import _leg_orientation


def book(bins, act_id, kind="bid_ask"):
    """bins: list of (bin_id, usd). Mirrors the shape dicts the hub builds."""
    return ([{"bin": b, "usd": u, "price": 10.0 + b * 0.01} for b, u in bins], act_id, kind)


def usd_book(act_id, kind="bid_ask", bid_near=0.36, bid_far=5.45, ask_near=0.22, ask_far=6.53,
             n_bid=15, n_ask=30, gap=1):
    """A clean two-run book: bid run strictly below spot, ask run strictly above it.

    DEFAULTS ARE THE CORRECT BID-ASK GEOMETRY and are taken from jordan's real 45-bin book
    (2026-09-26 12:45Z): each leg is SMALLEST nearest spot and LARGEST at its far edge, so the
    two legs together form the U the page draws with spot at the trough. Getting this backwards
    in the fixtures is how the first version of this test "failed" a detector that was correct —
    assert on real measured numbers, not on an assumed direction.
    """
    bins = []
    for i in range(n_bid):                       # nearest-first, growing away from spot
        w = bid_near + (bid_far - bid_near) * (i / max(n_bid - 1, 1))
        bins.append((act_id - 1 - i, round(w, 4)))
    top = act_id + gap
    for i in range(n_ask):
        w = ask_near + (ask_far - ask_near) * (i / max(n_ask - 1, 1))
        bins.append((top + i, round(w, 4)))
    return book(bins, act_id, kind)


FAILURES = []
CHECKS = [0]


def check(desc, got, want):
    CHECKS[0] += 1
    ok = (got == want)
    if not ok:
        FAILURES.append(f"{desc}: got {got!r}, want {want!r}")
    print(f"  {'PASS' if ok else 'FAIL'}  {desc}")
    print(f"        verdict={got!r}")


print("  ── TRUE POSITIVES (a real fault must still be caught) ──────────────────────────")
# A bid leg for a U must be heaviest FARTHEST from spot; heaviest NEAREST spot is the defect.
b, a, k = usd_book(1000, bid_near=5.45, bid_far=0.36)          # bid heavier nearest spot = WRONG
r = _leg_orientation(b, a, k)
check("inverted bid leg is CAUGHT", r["verdict"], "INVERTED: bid")

# An ask leg for a U must be heaviest at its FAR edge; heaviest nearest spot is the defect.
b, a, k = usd_book(1000, ask_near=6.53, ask_far=0.22)          # ask heavier nearest spot = WRONG
r = _leg_orientation(b, a, k)
check("inverted ask leg is CAUGHT", r["verdict"], "INVERTED: ask")

print("\n  ── FALSE ALARM #1: bell-only version flagged EVERY correct bid-ask ─────────────")
# The real jordan book (12:45Z), two runs, both correctly U-shaped for a bid-ask.
b, a, k = usd_book(1000)
r = _leg_orientation(b, a, k)
check("correct bid-ask is NOT flagged (was alarm #1)", r["verdict"], "OK")

print("\n  ── FALSE ALARM #2: spot-side split flagged a CROSSED book ─────────────────────")
# The real dadrian book (12:45Z): 8 bid bins CROSSED above spot then merged into one run with
# the ask leg -> 38 contiguous bins spanning spot. Geometry is unreadable, NOT inverted.
merged = sorted([(8363347 + i, round(4.0 - i * 0.5, 4)) for i in range(8)] +
                [(8363357 + i, round(0.22 + i * 0.2, 4)) for i in range(30)])
b, a, k = book(merged, 8363347)
r = _leg_orientation(b, a, k)
check("crossed book is NOT flagged (was alarm #2), verdict is None",
      r["verdict"], None)
check("crossed book reports judgeable=False so the page shows a note, not silence",
      r["judgeable"], False)

print("\n  ── HONESTY (a read we cannot make must not become a verdict) ──────────────────")
b, a, k = book([(1000, 5.0), (1001, 0.0)], 999)               # all-zero leg
r = _leg_orientation(b, a, k)
ok = r["verdict"] != "OK"
CHECKS[0] += 1
if not ok:
    FAILURES.append("all-zero leg: reported OK")
print(f"  {'PASS' if ok else 'FAIL'}  an all-zero leg never reads as healthy")
print(f"        verdict={r['verdict']!r}")

b, a, k = book([], 5000)
r = _leg_orientation(b, a, k)
check("empty book -> None", r["verdict"], None)

b, a, k = book([(1000, 5.0), (1001, 4.0)], 999)               # single run, no gap
r = _leg_orientation(b, a, k)
ok = r["judgeable"] is False or r["verdict"] is None or r["ask"] is None
CHECKS[0] += 1
if not ok:
    FAILURES.append("single run: invented a second leg")
print(f"  {'PASS' if ok else 'FAIL'}  a single run never invents a second leg")

print("\n  ── SHAPE-AWARE (the same geometry judges differently by design) ───────────────")
# A CURVE is a bell: heaviest nearest spot is CORRECT for a curve.
b, a, k = usd_book(1000, kind="curve", bid_near=4.0, bid_far=0.36, ask_near=6.53, ask_far=0.22)
r = _leg_orientation(b, a, k)
check("a bell-shaped CURVE is OK when heaviest nearest spot", r["verdict"], "OK")

b, a, k = usd_book(1000, kind="bid_ask")
r = _leg_orientation(b, a, k)
check("the SAME book as a bid-ask is OK when heaviest at the far edge", r["verdict"], "OK")

print()
print(f"  {CHECKS[0] - len(FAILURES)}/{CHECKS[0]} checks passed")
if FAILURES:
    print("\n  FAILURES:")
    for f in FAILURES:
        print(f"    - {f}")
    print("\n  RESULT: FAIL")
    sys.exit(1)
print("  RESULT: PASS")
