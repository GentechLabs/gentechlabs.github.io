#!/usr/bin/env python3
"""Regression test for the mid-rebalance publish guard in defi_hub_data.py.

WHY THIS EXISTS
---------------
The hub published dadrian at $2.77 / 0 bins while his $45.54 book was being re-centered (measured
2026-09-28: gate 12:18:54 -> hub sampled 12:22:40 -> recenter 12:24:38 -> complete 12:29:34). A
re-center withdraws liquidity BY DESIGN, so a reading taken mid-move is not a smaller book — it is
no reading at all, and it was on a PUBLIC page.

VERIFYING IT THE FIRST TIME MEANT WRITING A FAKE $120.00 INTO THE LIVE PAGE and waiting for the
guard to hold it. That worked, but it is exactly the wrong way to test a publish guard: had the
guard failed, the fake number would have gone live, and it relied on a LATER run to clean up.

So this test never touches production files. It drives the same decision function against a
temporary directory and asserts BOTH directions:
  * mid-move + collapse  -> REFUSE (keep the last good value)
  * mid-move + healthy   -> PUBLISH (the guard must not block a real reading)
  * no mid-move + collapse -> PUBLISH (a genuine loss is reported, never hidden)
  * stale recenter state -> PUBLISH (a move hours ago is not a move now)

Run:  python3 test_mid_rebalance_guard.py
Exit: 0 = all hold, 1 = a property is violated.
"""
import importlib.util
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, "/root/.hermes/profiles/gentech-treasury/scripts")
SRC = "/root/.hermes/profiles/gentech-treasury/scripts/defi_hub_data.py"

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    if not cond and detail:
        print(f"        {detail}")


def load(tmp):
    """Import defi_hub_data with HERE pointed at a scratch dir."""
    spec = importlib.util.spec_from_file_location("dhd_test", SRC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.HERE = tmp                  # redirect state lookups away from production
    return m


def write_recenter(tmp, tenant, age_s):
    with open(os.path.join(tmp, f".steward-recenter-state-{tenant}.json"), "w") as f:
        json.dump({"ts": time.time() - age_s, "last_action_ts": time.time() - age_s}, f)


print("═══ mid-rebalance guard ═══")

# ── 1. A FRESH recenter stamp means the machine is moving this book ───────────────────────────
with tempfile.TemporaryDirectory() as tmp:
    m = load(tmp)
    write_recenter(tmp, "dadrian", age_s=5)
    check("fresh recenter stamp -> mid-move DETECTED", m._mid_move("dadrian") is True)

# ── 2. An OLD stamp is not a move ─────────────────────────────────────────────────────────────
with tempfile.TemporaryDirectory() as tmp:
    m = load(tmp)
    write_recenter(tmp, "dadrian", age_s=3600)
    check("1h-old recenter stamp -> NOT a mid-move", m._mid_move("dadrian") is False)

# ── 3. No state file at all must never claim a move ───────────────────────────────────────────
with tempfile.TemporaryDirectory() as tmp:
    m = load(tmp)
    check("no recenter state -> NOT a mid-move (unreadable is not evidence)",
          m._mid_move("dadrian") is False)


# ── 4. THE DECISION ITSELF, both directions ───────────────────────────────────────────────────
def would_hold(m, tenant, new, old, mid):
    """Call the REAL guard. `new`/`old` here are capital_usd values; the guard also inspects the
    chain-scan fields, so a payload is built from them."""
    m._mid_move = lambda t, _mm=mid: _mm
    data = {"tenant": tenant, "capital_usd": new,
            "shape_total_usd": new, "bins": 25 if new else 0}
    prior = {} if old is None else {"capital_usd": old, "shape_total_usd": old, "bins": 25}
    return m._mid_move_reason(data, prior) is not None


with tempfile.TemporaryDirectory() as tmp:
    m = load(tmp)

    check("mid-move + collapse to <50% -> REFUSE",
          would_hold(m, "dadrian", new=2.77, old=45.54, mid=True) is True)
    check("mid-move + HEALTHY read -> PUBLISH (guard must not block a real number)",
          would_hold(m, "dadrian", new=45.44, old=45.54, mid=True) is False)
    check("NO mid-move + collapse -> PUBLISH (a genuine loss is reported, never hidden)",
          would_hold(m, "dadrian", new=2.77, old=45.54, mid=False) is False)
    check("mid-move + growth -> PUBLISH",
          would_hold(m, "dadrian", new=90.0, old=45.0, mid=True) is False)
    check("mid-move + no prior value -> PUBLISH (cannot judge, so do not block)",
          would_hold(m, "dadrian", new=2.77, old=None, mid=True) is False)
    check("mid-move + prior 0 -> PUBLISH (no baseline to collapse from)",
          would_hold(m, "dadrian", new=2.77, old=0.0, mid=True) is False)
    check("exactly 50% -> PUBLISH (boundary is strict, not <=)",
          would_hold(m, "dadrian", new=50.0, old=100.0, mid=True) is False)

# ── 5. The guard must key off the RIGHT tenant ────────────────────────────────────────────────
with tempfile.TemporaryDirectory() as tmp:
    m = load(tmp)
    write_recenter(tmp, "jordan", age_s=5)
    check("jordan mid-move does NOT hold dadrian (tenant keys are separate)",
          m._mid_move("dadrian") is False and m._mid_move("jordan") is True)


# ── 7. THE FIELD THAT ACTUALLY COLLAPSES (this is the bug the first test missed) ──────────────
# The original guard compared capital_usd (LEDGER, stable during a recenter) against itself, so it
# could never fire on a REAL mid-recenter. The chain-scanned fields collapse. This case is the
# actual measured payload from dadrian's public page, and it MUST hold.
with tempfile.TemporaryDirectory() as tmp:
    m = load(tmp)
    m._mid_move = lambda t, _mm=True: _mm
    real_mid = {"tenant": "dadrian", "capital_usd": 45.37, "shape_total_usd": 0.0, "bins": 0}
    prior = {"capital_usd": 45.37, "shape_total_usd": 45.25, "bins": 25}
    why = m._mid_move_reason(real_mid, prior)
    check("REAL mid-recenter (ledger stable, chain scan 0 bins) -> REFUSE", why is not None,
          "this is the measured payload that went public — comparing capital_usd alone misses it")

    # ...and the same incoherent payload with NO mid-move must also refuse: a payload claiming
    # $45.37 AND 0 bins contradicts itself regardless of whether we can explain it.
    m._mid_move = lambda t, _mm=False: _mm
    why2 = m._mid_move_reason(real_mid, prior)
    check("same incoherent payload with NO mid-move -> still REFUSE (self-contradiction)",
          why2 is not None, "a hold is better than publishing a payload that contradicts itself")
    check("...and it says the disagreement is UNEXPLAINED",
          why2 is not None and "UNEXPLAINED" in why2, f"got {why2!r}")

    # a CONSISTENT healthy read still publishes
    healthy = {"tenant": "dadrian", "capital_usd": 45.4, "shape_total_usd": 45.3, "bins": 25}
    check("healthy read -> PUBLISH", m._mid_move_reason(healthy, prior) is None)


print()
if FAIL:
    print(f"  ❌ {len(FAIL)} FAILED: {', '.join(FAIL)}")
    sys.exit(1)
print(f"  ✅ all {len(PASS)} mid-rebalance guard properties hold")
sys.exit(0)
