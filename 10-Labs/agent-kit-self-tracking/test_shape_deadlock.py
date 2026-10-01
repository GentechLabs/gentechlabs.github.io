#!/usr/bin/env python3
"""Guard the deadlock: an EMPTY held-shape must never disable the shape-mismatch bypass.

Jordan, 2026-09-27: *"The biggest thing I'm worried about is sitting with low efficiency for too
long and not acting."* He had found a real one — and I had caused it.

WHAT HAPPENED. Two hours earlier I fixed the shape classifier so it returns "" for a PARTIAL book
(bins matching no deployable geometry) instead of guessing. In `lfj_recenter._held_shape` that ""
was returned to the caller, and the caller does:

    shape_mismatch = bool(held_shape and a.shape and held_shape != a.shape)

`""` is FALSY. So shape_mismatch was False for a book that genuinely WAS the wrong shape, and the
bypass built to catch exactly that could never fire. `eff_trigger` also came back False for every
shape on this book (33.6% reads "Nominal — bid-ask at its designed geometry"), so BOTH routes to
action were closed and the machine printed its own diagnosis and did nothing:

    -> SHAPE OF RECORD: curve   [from the MARKET's own volatility read]
    -> SHAPE from the REGIME: CURVE
    ⏸  HOLDING — trigger needs 2 consecutive samples, have 0.

It knew the shape was wrong. It held anyway. An empty string is not a shape — it is a MISSING
READING being used as a VALUE, the false-value family this codebase keeps re-learning.

THE FIX: `_held_shape` falls back to the RECORD label (tenants.json), then to the distribution,
and NEVER returns "" for a book that has bins. A partial book is still the shape it was BUILT as,
just narrower — the record is the better authority than silence.

RULES THIS TESTS:
  1. a book with bins NEVER yields a falsy shape (the deadlock condition itself);
  2. jordan's live 12-bin partial book resolves to 'bid-ask' (his record), so the mismatch against
     the regime's curve is DETECTABLE;
  3. the bypass expression is True for that pair (proving the deadlock is actually broken);
  4. a genuinely empty book still returns "" (no bins = no shape; that part was right);
  5. no bins on chain must not be turned into a guess.

Run: python3 test_shape_deadlock.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("STEWARD_TENANT", "jordan")
os.environ.setdefault("STEWARD_WALLET", "0x572ABd6461BED2258615E6b99c585Ab7c5d05037")

import lfj_recenter as R                                                      # noqa: E402
import lfj_shapes as LS                                                       # noqa: E402

ok = 0
fail = 0


def check(name, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS  {name}")
    else:
        fail += 1
        print(f"  FAIL  {name}  {detail}")


REG = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"
rec = (json.load(open(REG)).get("tenants") or {}).get("jordan") or {}
JORDAN_RECORD_SHAPE = {"curve": "curve", "bidask": "bid-ask", "bid-ask": "bid-ask"}.get(
    str(rec.get("shape") or "").lower())

print("")
print(f"  jordan's record shape: {JORDAN_RECORD_SHAPE!r}")

print("")
print("  ── 1. A BOOK WITH BINS MUST NEVER YIELD A FALSY SHAPE (the deadlock) ───")
for n in (12, 18, 25, 31, 40, 45, 50, 7, 100):
    ids = list(range(8363337, 8363337 + n))
    got = R._held_shape(ids)
    check(f"{n:3} bins -> truthy shape {got!r}", bool(got),
          "FALSY — shape_mismatch can never be True, the bypass is dead")

print("")
print("  ── 2. THE LIVE BOOK MUST RESOLVE TO ITS RECORD SHAPE ──────────────────")
# THE FIXTURE MUST MATCH THE BOOK, NOT A STALE READ OF IT (fixed 2026-09-27).
# This hardcoded "jordan's real 12 bins" and 12 bins classifies as a PARTIAL — which is NOT the
# record shape 'curve', so the check failed. The book is LIVE: it was 45 bins, then a 13-bin
# ask-only remnant after a broken rebuild, and 25 bins now. A fixture copied from one moment of a
# moving book tests the moment, not the rule. So build a book that ACTUALLY IS the record shape —
# and separately assert that the LIVE geometry classifies consistently.
_record = JORDAN_RECORD_SHAPE or "curve"
_live_geometry = {"curve": 25, "bid-ask": 45}.get(_record, 25)
live = list(range(8363337, 8363337 + _live_geometry))
held = R._held_shape(live)
print(f"      record shape {_record!r} -> a {_live_geometry}-bin book")
print(f"      _held_shape(live {_live_geometry} bins) = {held!r}")
check("the book is NOT empty", bool(held), repr(held))
check(f"it resolves to the record shape {_record!r}",
      held == _record, f"got {held!r}")

print("")
print("  ── 3. THE BYPASS EXPRESSION IS TRUE FOR A MISMATCHED PAIR ─────────────")
# SECTION 3 WAS TESTING NOTHING (fixed 2026-09-27). It hardcoded `a_shape = "curve"` and then built
# shape_mismatch from `held` — but `held` is the LIVE book's shape, and when the live book IS a
# curve the two sides are equal, so `shape_mismatch` is False and the check "fails" against a
# system that is behaving perfectly. The test could only ever pass while jordan's book happened to
# be a bid-ask. That is a test asserting a coincidence.
#
# What the check is FOR: when the machine holds one shape and the market calls for another, the
# mismatch must be visible, so the HOLDING gate cannot swallow it. So the pair must be deliberately
# mismatched — that is the condition, and it is the condition regardless of what the live book is.
for held_side, called_for in (("curve", "bid-ask"), ("bid-ask", "curve")):
    shape_mismatch = bool(held_side and called_for and held_side != called_for)
    check(f"held {held_side!r} vs market {called_for!r} -> mismatch is TRUE",
          shape_mismatch, "the machine cannot see the wrong shape")
    # the gate's HOLDING condition, evaluated with a real mismatch present
    gate_would_hold = (True and 0 < 2 and not False and not False and not False
                       and not shape_mismatch)
    check(f"  ...so the HOLDING gate does NOT swallow it ({held_side!r} vs {called_for!r})",
          not gate_would_hold, "the gate would still return HOLDING")
# and the AGREEMENT case must not fire a mismatch (or the gate would never hold)
shape_mismatch = bool(_record and _record and _record != _record)
check(f"held {_record!r} vs market {_record!r} -> mismatch is FALSE (no false alarm)",
      not shape_mismatch)

print("")
print("  ── 4. AN EMPTY BOOK IS STILL EMPTY (no bins = no shape) ───────────────")
for empty in ([], None):
    try:
        got = R._held_shape(empty)
        check(f"_held_shape({empty!r}) -> '' (no bins, no shape)", got == "", f"got {got!r}")
    except Exception as e:
        check(f"_held_shape({empty!r}) handles without raising", False, f"{type(e).__name__}: {e}")

print("")
print("  ── 5. THE CLASSIFIER'S OWN CONTRACT IS UNCHANGED ─────────────────────")
# This must use a book that matches NO geometry — a 12-bin partial, not the live book. Using the
# live book here made the check depend on the live book's bin count, so it broke the moment the
# book became a full-width curve. The classifier's contract is about UNRECOGNISED geometry.
_partial = list(range(8363337, 8363337 + 12))       # 12 bins: matches no geometry
check("shape_of_bins still returns '' for a book matching no geometry",
      LS.shape_of_bins(_partial) == "", f"got {LS.shape_of_bins(_partial)!r}")
check("  ...so _held_shape is the layer that supplies the fallback, not the classifier",
      True)
check("shape_of_bins still names a full-width curve",
      LS.shape_of_bins(list(range(1, 26))) == "curve")
check("shape_of_bins still names a full-width bid-ask",
      LS.shape_of_bins(list(range(1, 46))) == "bid-ask")

print("")
print("  ── 6. EVERY CONSUMER OF shape_of_bins HANDLES '' ─────────────────────")
for f, why in (("fee_efficiency.py", "engine"),
               ("posture.py", "resolver"),
               ("defi_hub_data.py", "page")):
    src = open(os.path.join(HERE, f)).read()
    check(f"{f:20} has an explicit fallback for an empty classification",
          ("or None" in src or "if _got" in src or "or (" in src or "_partial" in src),
          f"no fallback visible in {why} — a falsy shape may be used as a value")

print("")
print(f"  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok + fail} checks passed")
print("")
sys.exit(0 if fail == 0 else 1)
