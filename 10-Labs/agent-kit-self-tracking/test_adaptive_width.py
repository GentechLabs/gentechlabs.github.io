#!/usr/bin/env python3
"""Prove adaptive_geometry() widens the CHOICE without relaxing the LIMIT.

Jordan, 2026-09-26: "Maybe instead of being so strict about the number of bins, we should be a
little bit more open based on the scenario."

The safety property under test is that this can NEVER build a band the old table would have
refused, and can never build one so tight that ordinary chop throws us out. Both directions are
checked, plus the ceiling.

Run: python3 test_adaptive_width.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lfj_shapes import CEILING, widths, adaptive_geometry as AG   # noqa: E402

ok = fail = 0


def check(name, got, want):
    global ok, fail
    if got == want:
        ok += 1
        print(f"  PASS  {name}")
    else:
        fail += 1
        print(f"  FAIL  {name}: got {got!r}, want {want!r}")


print("\n  ── THE LIMIT IS NEVER RELAXED ──")
for sh in ("curve", "bidask", "bid-ask"):
    base = widths(sh)
    for ir, eff in ((None, None), (False, None), (True, 90.0), (True, 10.0)):
        w = AG(sh, in_range=ir, efficiency_pct=eff)
        label = f"{sh}/{ir}/{eff}"
        check(f"{label}: total <= CEILING", w["total"] <= CEILING, True)
        check(f"{label}: never wider than the shape default",
              w["total"] <= base["total"], True)
        check(f"{label}: never narrower than 70% of default",
              w["total"] >= int(base["total"] * 0.70) - 1, True)

print("\n  ── THE SCENARIOS ──")
check("no info -> the shape's default (unchanged behaviour)",
      AG("curve")["total"], 25)
check("rangebound + EARNING -> tighten the curve",
      AG("curve", in_range=True, efficiency_pct=72.0)["chosen"], "tight")
check("rangebound + earning -> 17 bins",
      AG("curve", in_range=True, efficiency_pct=72.0)["total"], 17)
check("rangebound but NOT earning -> leave it alone",
      AG("curve", in_range=True, efficiency_pct=30.0)["total"], 25)
check("bid-ask earning -> tightens off its 45 default",
      AG("bid-ask", in_range=True, efficiency_pct=72.0)["total"], 31)

print("\n  ── OUT OF RANGE: the widening lever, and its true limit ──")
# The bid-ask default IS the ceiling, so there is no headroom to widen into. The function must say
# so by simply returning the default rather than inventing an illegal width.
w = AG("bid-ask", in_range=False)
check("bid-ask out of range -> stays at its default (no headroom, 45 IS the ceiling)",
      w["total"], 45)
check("  ...and reports adaptive=False rather than pretending it widened",
      w["adaptive"], False)

print("\n  ── A FAILURE IN THE ADAPTIVE STEP MUST NOT BLOCK A DEPLOY ──")
# The function must fall back to the default rather than raise, because it sits in the path that
# can withdraw capital. Force a failure by passing a shape that canon() rejects.
w = AG(None)
check("unknown shape -> still returns a usable geometry", w["total"] > 0, True)
check("  ...and says the default was used", w["chosen"], "default")

print(f"\n  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok+fail} checks passed\n")
sys.exit(0 if fail == 0 else 1)
