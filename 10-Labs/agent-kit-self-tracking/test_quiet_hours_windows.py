#!/usr/bin/env python3
"""
test_quiet_hours_windows.py — the quiet-hours gate must be correct for ALL window shapes,
not just the one we happen to use today.

WHY THIS EXISTS (2026-09-29)
  `is_quiet_hours()` computed one formula — `hour >= start or hour < end` — for every window.
  That formula is correct ONLY for a window that wraps midnight (22->8). It was guarded by:

      if start < end:
          # e.g. 22->8 spans midnight handled by the OR below
          pass

  ...a `pass`. The branch claimed to handle the non-wrapping case and did nothing. For a
  same-day window (08:00-22:00) the wrapping formula returns True for all 24 hours, so the
  guard would have silenced EVERY run, all day.

  It never fired because the only caller that sets a window (buylist-cron.sh, QUIET_START=22
  QUIET_END=7) wraps. That is exactly what makes it worth a test: the bug is invisible to the
  current caller and live for the next one.

THE PROPERTY, stated independently of the implementation:
  For a window [start, end) the gate is quiet iff the hour lies inside that window, where a
  window with start > end wraps through midnight, and start == end disables the gate.

THE NEGATIVE CONTROL
  Section 4 re-implements the OLD expression and asserts it FAILS the same cases this suite
  passes. Without it, a suite that only tests the wrapping window would have gone green on the
  broken code — so a test that cannot fail is not evidence. (Same discipline as
  test_lfj_exit_reserve.py, which carries the old block as its control.)
"""

import sys
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "quiet_hours.py"
_spec = importlib.util.spec_from_file_location("quiet_hours_under_test", SCRIPT)
qh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qh)

_n = [0]
_fails = []


def check(name, cond, detail=""):
    _n[0] += 1
    if cond:
        print(f"    PASS  {name}")
    else:
        print(f"    FAIL  {name}   {detail}")
        _fails.append(name)


def is_quiet_at(hour, start, end):
    """
    Call the real predicate with the clock stubbed to a fixed hour AND the window supplied.

    NOTE: `is_quiet_hours()` takes no arguments — it reads QUIET_START / QUIET_END from the
    ENVIRONMENT. An earlier version of this test passed start/end as parameters, which the
    function simply ignored, so every assertion was silently reading whatever happened to be
    exported in the calling shell. Set the env for real, and restore it afterwards.
    """
    import os
    orig_hour = qh._get_hour
    prev = {k: os.environ.get(k) for k in ("QUIET_START", "QUIET_END")}
    qh._get_hour = lambda: hour
    os.environ["QUIET_START"] = str(start)
    os.environ["QUIET_END"] = str(end)
    try:
        return bool(qh.is_quiet_hours())
    finally:
        qh._get_hour = orig_hour
        for k, v in prev.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def expected(hour, start, end):
    """The property, computed straight from the definition — NOT from the implementation."""
    if start == end:
        return False                      # zero-width window disables the gate
    if start < end:
        return start <= hour < end        # same-day window
    return hour >= start or hour < end    # wraps midnight


print("=" * 74)
print("  QUIET HOURS — WINDOW SHAPES")
print("=" * 74)

# ── 1. THE WINDOW WE ACTUALLY RUN (wrapping) ────────────────────────────────────
print("\n  ── 1. WRAPPING WINDOW (buylist-cron.sh: 22 -> 7) — the live config ──")
for h in range(24):
    got = is_quiet_at(h, 22, 7)
    want = expected(h, 22, 7)
    check(f"22->7 at {h:02d}:00 is {'quiet' if want else 'active'}", got == want,
          f"got={got} want={want}")
check("22->7 is quiet at 23:00 (late evening)", is_quiet_at(23, 22, 7))
check("22->7 is quiet at 00:00 (past midnight)", is_quiet_at(0, 22, 7))
check("22->7 is ACTIVE at 07:00 (the 7am run must be live)",
      not is_quiet_at(7, 22, 7))
check("22->7 is ACTIVE at 12:00", not is_quiet_at(12, 22, 7))

# ── 2. THE CASE THAT WAS BROKEN (same-day window) ───────────────────────────────
print("\n  ── 2. SAME-DAY WINDOW (08 -> 22) — the case that was a no-op ──")
for h in range(24):
    got = is_quiet_at(h, 8, 22)
    want = expected(h, 8, 22)
    check(f"08->22 at {h:02d}:00 is {'quiet' if want else 'active'}", got == want,
          f"got={got} want={want}")
check("08->22 is QUIET at 12:00 (midday is inside the window)",
      is_quiet_at(12, 8, 22))
check("08->22 is ACTIVE at 03:00 (small hours are outside the window)",
      not is_quiet_at(3, 8, 22))
check("08->22 is ACTIVE at 23:00 (late evening is outside)",
      not is_quiet_at(23, 8, 22))
check("08->22 is QUIET at 21:00 (last hour inside the window)",
      is_quiet_at(21, 8, 22))
check("08->22 is ACTIVE at 22:00 (end is EXCLUSIVE)",
      not is_quiet_at(22, 8, 22))
check("08->22 is QUIET at 08:00 (start is INCLUSIVE)",
      is_quiet_at(8, 8, 22))

# ── 3. EDGE SHAPES ──────────────────────────────────────────────────────────────
print("\n  ── 3. EDGE SHAPES ──")
check("start == end (0,0) is NOT quiet at 3am — zero-width disables the gate",
      not is_quiet_at(3, 0, 0))
check("start == end (12,12) is NOT quiet at midday",
      not is_quiet_at(12, 12, 12))
check("start == end leaves EVERY hour active",
      all(not is_quiet_at(h, 9, 9) for h in range(24)))
check("a one-hour window (0 -> 1) is quiet only at 00:00",
      is_quiet_at(0, 0, 1) and not is_quiet_at(1, 0, 1) and not is_quiet_at(23, 0, 1))
check("a one-hour wrapping window (23 -> 0) is quiet only at 23:00",
      is_quiet_at(23, 23, 0) and not is_quiet_at(0, 23, 0) and not is_quiet_at(22, 23, 0))
check("a 23-hour window (0 -> 23) is quiet at every hour except 23:00",
      all(is_quiet_at(h, 0, 23) for h in range(23)) and not is_quiet_at(23, 0, 23))

# The predicate must never disagree with the definition for ANY legal window.
print("\n  ── 3b. EXHAUSTIVE: every (start, end) pair x every hour ──")
bad = []
for s in range(24):
    for e in range(24):
        for h in range(24):
            if is_quiet_at(h, s, e) != expected(h, s, e):
                bad.append((s, e, h))
check(f"all 13,824 (start,end,hour) combinations agree with the definition "
      f"({len(bad)} disagreements)", not bad, f"e.g. {bad[:4]}")

# ── 4. NEGATIVE CONTROL — prove the OLD code fails these ────────────────────────
print("\n  ── 4. NEGATIVE CONTROL (the old expression must FAIL) ──")


def old_expr(hour, start, end):
    """The exact expression the file used to evaluate, for every window shape."""
    if start < end:
        pass                      # the no-op branch, preserved verbatim
    return hour >= start or hour < end


mismatches = [(h) for h in range(24) if bool(old_expr(h, 8, 22)) != expected(h, 8, 22)]
check("the OLD code WOULD have been wrong on the same-day window "
      f"({len(mismatches)} of 24 hours disagree)", len(mismatches) > 0,
      "the control did not reproduce the bug — the test would be vacuous")
check("the OLD code was right on the wrapping window (why it hid)",
      all(bool(old_expr(h, 22, 7)) == expected(h, 22, 7) for h in range(24)))
check("the OLD code turned a zero-width window permanently ON",
      all(bool(old_expr(h, 8, 8)) for h in range(24)))
check("the NEW code is correct where the OLD one failed",
      all(is_quiet_at(h, 8, 22) == expected(h, 8, 22) for h in range(24)))

# ── RESULT ──────────────────────────────────────────────────────────────────────
print("\n" + "=" * 74)
if _fails:
    print(f"  RESULT: FAIL — {_n[0] - len(_fails)}/{_n[0]} checks passed")
    for f in _fails[:6]:
        print(f"     ✗ {f}")
    print("=" * 74)
    sys.exit(1)
print(f"  RESULT: PASS — {_n[0]}/{_n[0]} checks passed")
print("=" * 74)
sys.exit(0)
