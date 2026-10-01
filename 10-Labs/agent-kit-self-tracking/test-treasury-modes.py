#!/usr/bin/env python3
"""test-treasury-modes.py — verify the HOLD mode addition in both directions.

Per the standing rule: a check that can't fail is not a check. So this asserts BOTH:
  - the new behaviour (HOLD is recognised, and is NOT confused with stables)
  - the old behaviour (YIELD_FARM / TRADE / DRY_POWDER unchanged; unknown still falls back)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import treasury_state as ts   # noqa: E402

fails = []


def check(label: str, got, want) -> None:
    ok = got == want
    if not ok:
        fails.append(f"{label}: got {got!r}, want {want!r}")
    print(f"  {'✅' if ok else '❌'} {label:<52} {got!r}")


print("=" * 78)
print("  TREASURY MODE TESTS — new behaviour")
print("=" * 78)
check("HOLD is a recognised mode", "HOLD" in ts.MODES, True)
check("get_mode(HOLD) returns HOLD (not YIELD_FARM)", ts.get_mode({"mode": "HOLD"}), "HOLD")
check("is_holding(HOLD)", ts.is_holding({"mode": "HOLD"}), True)
check("is_dry_powder(HOLD) is FALSE", ts.is_dry_powder({"mode": "HOLD"}), False)
check("is_directional(HOLD)", ts.is_directional({"mode": "HOLD"}), True)
check("can_trade(HOLD) is FALSE", ts.can_trade({"mode": "HOLD"}), False)
check("HOLD has documented semantics", bool(ts.mode_semantics({"mode": "HOLD"})), True)

print()
print("=" * 78)
print("  TREASURY MODE TESTS — existing behaviour must be UNCHANGED")
print("=" * 78)
check("YIELD_FARM still valid", ts.get_mode({"mode": "YIELD_FARM"}), "YIELD_FARM")
check("TRADE still valid", ts.get_mode({"mode": "TRADE"}), "TRADE")
check("DRY_POWDER still valid", ts.get_mode({"mode": "DRY_POWDER"}), "DRY_POWDER")
check("can_trade(TRADE) still TRUE", ts.can_trade({"mode": "TRADE"}), True)
check("is_dry_powder(DRY_POWDER)", ts.is_dry_powder({"mode": "DRY_POWDER"}), True)
check("is_holding(DRY_POWDER) is FALSE", ts.is_holding({"mode": "DRY_POWDER"}), False)
check("is_directional(YIELD_FARM) is FALSE", ts.is_directional({"mode": "YIELD_FARM"}), False)
check("unknown mode still falls back", ts.get_mode({"mode": "GARBAGE"}), "YIELD_FARM")
check("missing mode still falls back", ts.get_mode({}), "YIELD_FARM")

print()
print("=" * 78)
print("  THE GATE — trade signals must not fire outside TRADE")
print("=" * 78)
for m in ("YIELD_FARM", "TRADE", "DRY_POWDER", "HOLD"):
    allowed = ts.gated("trade_signal") if False else None
    try:
        ts.assert_mode("trade_signal", {"mode": m})
        allowed = True
    except ts.ModeGateError:
        allowed = False
    want = (m == "TRADE")
    check(f"trade_signal allowed in {m}", allowed, want)

print()
print("=" * 78)
if fails:
    print(f"  ❌ {len(fails)} FAILURE(S)")
    for f in fails:
        print(f"     - {f}")
    sys.exit(1)
print("  ✅ ALL CHECKS PASSED — HOLD works, nothing existing changed")
print("=" * 78)
