#!/usr/bin/env python3
"""Prove recent_is_rangebound() fires BOTH ways.

The old test ANDed two absolute numbers against a 12-hour tape, so a large-range CHOP could never
be declared rangebound. This locks the corrected test, and it checks the direction that BLOCKS as
well as the one that fires — a boundary never tested in the direction it blocks is not known to work.

Run: python3 test_rangebound.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from volatility_tracker import recent_is_rangebound as RB   # noqa: E402

ok = fail = 0


def check(name, got, want):
    global ok, fail
    if got == want:
        ok += 1
        print(f"  PASS  {name}")
    else:
        fail += 1
        print(f"  FAIL  {name}: got {got!r}, want {want!r}")


def tape(rng, net, n=81, hours=12):
    return {"range_pct": rng, "net_pct": net, "n": n, "hours": hours}


print("\n  ── THE CASE THAT WAS MISSED (jordan, 2026-09-26, 5.44%/0.10%) ──")
# Went up 5.44% and came all the way back. Chop. The old test said NOT rangebound.
check("wide range + flat net = CHOP -> rangebound", RB(tape(5.44, 0.10)), True)
check("  ...and the mirrored chop (net negative)", RB(tape(6.10, -0.20)), True)

print("\n  ── A REAL DRIFT MUST STILL BLOCK (the refusing direction) ──")
# A genuine trend: the net move is what a curve cannot survive.
check("large net (6%) -> NOT rangebound", RB(tape(3.0, 6.0)), False)
check("net just over the limit -> NOT rangebound", RB(tape(1.0, 2.5)), False)
check("  ...scaled to a 5% band, net 6% -> NOT rangebound",
      RB(tape(2.0, 6.0), band_span_pct=5.0), False)

print("\n  ── THE ORIGINAL HAPPY PATH MUST STILL PASS ──")
check("small range + small net -> rangebound", RB(tape(1.2, 0.4)), True)
check("tiny everything -> rangebound", RB(tape(0.3, 0.05)), True)

print("\n  ── THIN DATA MUST REFUSE, NOT ASSUME CALM ──")
check("too few reads -> None (cannot tell)", RB(tape(1.0, 0.1, n=2)), None)
check("empty tape -> None", RB({}), None)

print("\n  ── THE BAND SCALES WITH WHAT WE FARM ──")
check("net 3% is a drift on a 2% band -> NOT rangebound",
      RB(tape(1.0, 3.0), band_span_pct=2.0), False)
check("net 3% but band is 5% wide -> rangebound (it is inside what we farm)",
      RB(tape(4.0, 3.0), band_span_pct=5.0), True)

print(f"\n  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok+fail} checks passed\n")
sys.exit(0 if fail == 0 else 1)
