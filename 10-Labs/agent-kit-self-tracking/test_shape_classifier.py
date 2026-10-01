#!/usr/bin/env python3
"""Prove the shape classifier names every DEPLOYABLE geometry, and refuses to guess otherwise.

Jordan, 2026-09-27, from a screenshot of his own page:
    green:  "✓ This shape is CORRECT — spot at the trough (a V) is where a bid-ask is BUILT to sit"
    amber:  "⚠ ... but the live book is bid-ask — they DISAGREE"

Two boxes, one book, opposite messages. The cause was THREE READERS GIVING THREE ANSWERS:
  * lfj_shapes.shape_of_bins  (the canonical one, used by fee_efficiency/lfj_recenter/posture) -> curve
  * the hub's own inline rule (a second implementation)                                         -> bid-ask
  * the efficiency number on the page, scored with the canonical one                             -> curve math
So the page printed a bid-ask label next to a curve-scored 66.4%, and warned about a disagreement
that was partly arithmetic.

ROOT CAUSE, and this file is the guard for it: `shape_of_bins` used `min()` over a table holding only
the two DEFAULT widths (curve 25, bid-ask 45). But `adaptive_geometry` TIGHTENS on rangebound+earning
— bid-ask 45 -> 31, curve 25 -> 18. A 31-bin bid-ask is 6 from 25 and 14 from 45, so `min()` called it
a CURVE. `min()` cannot return "I don't know", so a book matching nothing was still named after the
nearest thing.

TWO RULES THIS TESTS:
  1. every width the system can DEPLOY must be named correctly by its own classifier;
  2. a book matching NO deployable geometry (a partial book — a leg sold off) must return "" so the
     caller falls back to the record label, rather than being handed a coin-flip.

Note the difference from the tolerance cases: 18 and 31 are within 2 bins of a deployable width
(curve 18 is exact; 31 is exact for the tightened bid-ask), so they ARE named. 35 and 40 sit between
design points and are NOT.

Run: python3 test_shape_classifier.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lfj_shapes as LS                                                     # noqa: E402

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


print("")
print("  ── EVERY DEPLOYABLE WIDTH IS NAMED CORRECTLY ───────────────────────")

# The bug: only the two defaults were known. Assert we now cover what adaptive_geometry emits.
deployable = {s: sorted(LS._deployable_widths(s)) for s in ("curve", "bidask")}
print(f"      deployable widths: {deployable}")

for shape in ("curve", "bidask"):
    want = "bid-ask" if shape == "bidask" else "curve"
    for n in deployable[shape]:
        ids = list(range(8363337, 8363337 + n))
        got = LS.shape_of_bins(ids)
        check(f"{shape:6} deployed at {n:2} bins -> '{got}'", got == want, f"got {got!r}, want {want!r}")

print("")
print("  ── THE TWO HEADLINE WIDTHS STILL WORK (no regression) ──────────────")
for shape, n, want in (("curve", 25, "curve"), ("bidask", 45, "bid-ask")):
    got = LS.shape_of_bins(list(range(1, n + 1)))
    check(f"{n} bins -> '{want}'", got == want, f"got {got!r}")

print("")
print("  ── ONE BIN OF DRIFT EITHER WAY IS STILL TOLERATED ───────────────────")
for n, want in ((24, "curve"), (26, "curve"), (44, "bid-ask"), (46, "bid-ask"),
                (17, "curve"), (30, "bid-ask")):
    got = LS.shape_of_bins(list(range(1, n + 1)))
    check(f"{n} bins -> '{want}' (within 2 of a deployable width)", got == want, f"got {got!r}")

print("")
print("  ── A BOOK MATCHING NOTHING MUST SAY SO, NOT GUESS ───────────────────")
# These sit between design points. Naming either would be a coin-flip.
for n in (12, 35, 40, 22, 50):
    got = LS.shape_of_bins(list(range(1, n + 1)))
    check(f"{n} bins -> '' (matches no deployable geometry)", got == "",
          f"got {got!r} — a guess is not neutral: this codebase has already rebuilt a healthy "
          f"book and scored a bell with U-shape math off a wrong label")

print("")
print("  ── THE LIVE BOOK: THE CLASSIFIER MUST MATCH ITS OWN GEOMETRY CONTRACT ──")
# ── This assertion used to read: "live N-bin partial book -> '' (not a guessed class)" ──────────
# It hard-coded the answer that was true for ONE book on ONE day. On 2026-09-27 the book was
# re-deployed to its full 45-bin bid-ask (15+30, the legal geometry), the classifier correctly
# returned 'bid-ask', and the test reported a FAILURE — because its assumption had gone stale, not
# the code. A test whose expectation is a snapshot of live state tests the state, not the rule.
# The durable rule is: a book whose bin count IS a deployable width classifies to that shape, and a
# book whose count is NOT any deployable width returns "" rather than guessing. Assert THAT.
import json                                                              # noqa: E402
p = "/var/www/gentechlabs/DeFi/defi-data-jordan.json"
if os.path.exists(p):
    d = json.load(open(p))
    ids = [b["bin"] for b in (d.get("shape") or [])]
    if ids:
        got = LS.shape_of_bins(ids)
        n = len(ids)
        legal = {w for sh in ("curve", "bid-ask") for w in LS._deployable_widths(sh)}
        print(f"      live book: {n} bins, contiguous={n == max(ids) - min(ids) + 1}, "
              f"legal width={n in legal}")
        if n in legal:
            check(f"live {n}-bin book IS a deployable width -> classifies to a real shape",
                  got in ("curve", "bid-ask"), f"got {got!r} for a legal width")
            check(f"  ...and the shape matches the geometry {n} belongs to",
                  all(n not in LS._deployable_widths(o)
                      for o in ("curve", "bid-ask") if o != got),
                  f"{n} is a {got} width but also matched another shape")
        else:
            check(f"live {n}-bin book is NOT a deployable width -> '' (no guess)",
                  got == "", f"got {got!r}; {n} is not a legal geometry")
        # and the hub must therefore agree with the engine, because it now ASKS the engine
        check("the hub calls the canonical classifier, not a second rule",
              "shape_of_bins" in open(os.path.join(
                  "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/defi_hub_data.py")).read())
else:
    print("      (live payload not present — skipped)")

print("")
print(f"  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok + fail} checks passed")
print("")
sys.exit(0 if fail == 0 else 1)
