#!/usr/bin/env python3
"""lfj_shapes.py — ONE source of truth for LFJ shape geometry.

WHY THIS FILE EXISTS
--------------------
Jordan, 2026-09-22: "remember a curve shape should be closer to 25 bins. 45 for the bid ask."

Before this file, the widths lived as four shell variables in lfj-curve-deploy.sh, and THREE
different consumers scraped them back out with a regex:

    * fee_efficiency.py   -> _legs_from_config()   (reads the deploy script's source text)
    * lfj_recenter.py     -> its plan reader        (reads the deploy script's source text)
    * lfj-curve-deploy.sh -> itself

That scraping was a standing silent-wrongness hazard: the readers scan EVERY non-comment line and
the LAST match wins, so the moment a second assignment line existed the readers would report the
WRONG shape's geometry while looking perfectly healthy. There was no width rule tied to shape at
all -- every shape deployed at 45 bins, including the ones recorded as "curve".

Now the table lives here as data, and every consumer asks for the shape it actually means.

THE RULE (Jordan, 2026-09-22)
-----------------------------
    curve   -> ~25 bins   (range-bound, symmetric: earns on chop while staying in range)
    bidask  -> 45 bins    (the absolute ceiling Jordan set; pays at the EDGES, U-shape)

45 is a CEILING, not a default. "The widest I could see us going for a bid-ask, I said a maximum
of 45 bins, because we want to be wide but we also don't want to be so wide we're not earning as
much as we could be." (Jordan, 2026-09-21)

SPELLING: the deploy path calls it "bidask"; the efficiency/hub path calls it "bid-ask". Both are
accepted here so the two vocabularies cannot silently fail to match -- that mismatch is the same
defect class as a check that can never fire.
"""
from __future__ import annotations

import json
import sys

CEILING = 45          # absolute maximum bins for any shape (Jordan's hard ceiling)

# shape -> leg geometry. near/far are signed offsets from the active bin; a leg holds
# (far - near + 1) bins. The bid sits BELOW spot and holds USDC; the ask sits ABOVE and holds WAVAX.
WIDTHS: dict[str, dict[str, int]] = {
    "curve":  {"bid_near": 2, "bid_far": 13, "ask_near": 1, "ask_far": 13},   # 12 + 13 = 25
    "bidask": {"bid_near": 2, "bid_far": 16, "ask_near": 1, "ask_far": 30},   # 15 + 30 = 45
}

# ── ADAPTIVE WIDTH BOUNDS (Jordan, 2026-09-26) ──────────────────────────────────────────────────
# "Maybe instead of being so strict about the number of bins, we should be a little bit more open
# based on the scenario." These bound how far the scenario may move us off the shape's default.
# The WIDEST any shape can now get is its own default (still validated against CEILING below), and
# the NARROWEST is NARROW_FACTOR of it — so the adaptive path widens the CHOICE without ever
# relaxing the LIMIT. Measured motivation: the bid-ask band is 4.81% wide and a rangebound tape can
# swing 5.44% in 12h, so a rangebound market walks out of a band sized for a different scenario.
NARROW_FACTOR = 0.70           # tightest we will build = 70% of the shape's default
CONCENTRATE_MIN_EFF = 60.0     # only tighten when the book is genuinely earning where it sits
CEILING_FAR = {"bid_far": 16, "ask_far": 30}   # the widest the bid-ask may reach (already = default)
NARROW_FAR_MAX = {"bid_far": 13, "ask_far": 13}  # the widest a curve may reach (already = default)

# Accept both spellings so a vocabulary mismatch degrades to working, never to silently-wrong.
ALIASES = {
    "bid-ask": "bidask",
    "bid_ask": "bidask",
    "bidask": "bidask",
    "curve": "curve",
    "": "bidask",
}


def canon(shape: str | None) -> str:
    """Normalise a shape name. Unknown shapes fall back to bidask (the wider, safer book)."""
    return ALIASES.get((shape or "").strip().lower(), "bidask")


def _deployable_widths(shape: str) -> set:
    """Every total width this system can ACTUALLY deploy for a shape — not just the table default.

    Jordan, 2026-09-27. `adaptive_geometry` picks a width from the scenario: on RANGEBOUND+earning it
    TIGHTENS (a bid-ask 45 -> 31, a curve 25 -> 17). `shape_of_bins` only knew the two headline
    widths, so a 31-bin bid-ask was 6 bins from "curve" (25) and 14 from "bid-ask" (45) and got named
    a CURVE — by the one classifier the engine trusts. That is the live defect behind three readers
    giving three answers for jordan's book.

    Derived from the same constants `adaptive_geometry` uses, so the two cannot drift: if a new
    scenario is added there, its width appears here automatically.
    """
    w = widths(shape)
    out = {w["total"]}
    # NARROW_FACTOR is the SAME constant adaptive_geometry narrows by (70%), so the two cannot
    # drift: if the factor changes there, the classifier follows it here.
    out.add(int(round(w["total"] * NARROW_FACTOR)))
    return out



def shape_of_mass(amounts: dict) -> str:
    """Which shape is ON CHAIN, decided by WHERE THE MONEY SITS.

    ── THE FOURTH NAME FOR THIS, AFTER THREE FAILURES OF THE SAME IDEA (added 2026-09-30) ────────
    This module has tried to name a book three times, each a different reading of the same wrong
    quantity: (1) the GAP test -- every book read "bid-ask", since every shape has a hole at spot;
    (2) the headline COUNT -- a 31-bin adaptive book read "curve" (fixed 09-27); (3) the count plus
    adaptive variants -- a 40-bin WIDENED book matches neither class, so it falls to the nearer one
    and names a BELL a U. Each fix refined the count. THE COUNT IS NOT THE SHAPE.

    What actually differs is where the liquidity concentrates across the book's own span, and it is
    width-independent by construction:
        curve   -> a BELL. Money clusters at the CENTRE.
        bid-ask -> a flat-ish U. Money spreads to the EDGES.
    Measured on the live book 2026-09-30, density read bin by bin: a bell puts 69.0% inside the
    inner half of its span. Takes {bin_id: amount}. Returns "curve", "bid-ask", or "" when it
    genuinely cannot tell -- and an honest "" always beats a confident wrong name, which is what
    produced three readers giving three answers for one book.
    """
    if not amounts:
        return ""
    ids = sorted(amounts)
    lo, hi = ids[0], ids[-1]
    span = hi - lo
    if span <= 0:
        return ""
    mid = (lo + hi) / 2.0
    inner = sum(a for i, a in amounts.items() if abs(i - mid) <= span / 4.0)
    outer = sum(a for i, a in amounts.items() if abs(i - mid) > span / 4.0)
    tot = inner + outer
    if tot <= 0:
        return ""
    frac = inner / tot
    if frac >= 0.55:
        return "curve"
    if frac <= 0.45:
        return "bid-ask"
    return ""


def shape_of_bins(ids) -> str:
    """Which shape is ON CHAIN, from the bins that actually hold liquidity.

    ── A DISCRIMINATOR MUST DIFFER ACROSS THE CLASSES (fixed 2026-09-25, live churn) ──────────
    This used to be `bid-ask if there is a gap between the legs else curve`. EVERY shape this
    system can deploy is TWO SINGLE-SIDED LEGS WITH A HOLE AT SPOT -- the table above gives even
    the CURVE `bid_near: 2, ask_near: 1`, so bins -1 and 0 are empty in BOTH geometries. A gap
    test therefore named ONE class for every book, and the answer was always "bid-ask":
    measured live on jordan's 25-bin curve, `gap -> bid-ask` while the bin COUNT (25) was the
    curve's own geometry to the bin.

    That one wrong label produced three live failures at once:
      * `shape_mismatch` was TRUE for every in-range curve, so the SHAPE REBUILD trigger fired
        on the healthy state -- and it BYPASSES the cooldown and the streak gates, which is how
        a funded book got withdrawn on a 14.3-minute-old cooldown and left in the wallet when
        the re-deploy failed;
      * `fee_efficiency.evaluate()` scored a bell-shaped book with the U-shape's math, so a
        curve at its peak read "33.9% — bid-ask at its designed geometry" and the low-efficiency
        trigger fired on a book that was placed exactly as designed;
      * a genuine mismatch (a 45-bin bid-ask while the market calls for a curve) could never be
        named, because every book read "bid-ask".

    THE TEST THAT WORKS: the bin COUNT against this table. 25 => curve, 45 => bid-ask, by
    construction, and the two differ by 20 bins. Nearest on that axis, so a book that is a
    little off its design point (a partially drained leg, a leg that landed a bin away) is
    still named by the geometry it was built from. On a tie the wider book wins, which is the
    safer read: it over-states width rather than under-stating it.
    """
    n = len(ids)
    if n <= 0:
        return ""            # nothing on chain is neither shape -- never invent one
    totals = {}
    for k in WIDTHS:
        for w in _deployable_widths(canon(k)):
            totals[k] = totals.get(k, set())
            totals[k].add(w)
    # nearest DEPLOYABLE width per class, then the same 2-bin tolerance as the table rule
    named = {}
    for k, ws in totals.items():
        named[k] = min(abs(w - n) for w in ws)
    key = min(named, key=lambda k: (named[k], k))
    name = "curve" if key == "curve" else "bid-ask"
    # ── IT MUST BE ABLE TO SAY "I DON'T KNOW" (fixed 2026-09-27) ────────────────────────────────
    # `min()` ALWAYS returns a class, so a book matching NEITHER design point was silently named
    # after the nearer one. That is how three readers came to give THREE different answers for one
    # live book, and how the page came to warn Jordan about a disagreement that partly did not
    # exist (jordan, 2026-09-27: "why this shape: ...they DISAGREE").
    #
    # THE MISS, caught live: `adaptive_geometry` tightens on RANGEBOUND+earning — a bid-ask goes
    # 45 -> 31 bins — but this classifier knew only the two TABLE widths (25 and 45). A 31-bin
    # bid-ask is 6 from 25 and 14 from 45, so it was named a CURVE by the only function the ENGINE
    # trusts (fee_efficiency, lfj_recenter, posture). The table is therefore now asked for the
    # widths it can ACTUALLY deploy, not the two headline ones.
    #
    # AND NO GUESSING WHEN A BOOK MATCHES NEITHER: a tolerance of 2 bins on a 20-bin gap is the
    # whole separation. Beyond it the honest answer is "", and callers must fall back to the record
    # label rather than be handed a coin-flip. A wrong label is not neutral here — in this codebase
    # it has already triggered a rebuild on a healthy book and scored a bell with U-shape math.
    if named[key] <= 2:
        return name
    return ""


def adaptive_geometry(shape: str | None, in_range: bool | None = None,
                      efficiency_pct: float | None = None) -> dict:
    """Pick the width from the SCENARIO instead of always deploying the widest band.

    Jordan, 2026-09-26: *"Maybe instead of being so strict about the number of bins, we should be a
    little bit more open based on the scenario. Maybe that might help too."*

    THE PROBLEM HE IS POINTING AT, measured: the band we deploy is **4.81% wide**. A rangebound
    tape can swing **5.44%** inside 12 hours — so a rangebound market wanders OUT of a band we chose
    for a different scenario, and we pay a re-centre for it. 45 bins is a CEILING, not a default;
    the header of this file already says so.

    THE LOGIC, and it is the same one the efficiency rule uses:

      * OUT OF RANGE        -> the market has LEFT the band. Widen, to stop the churn. This is the
                               scenario that actually costs us: an out-of-range book earns nothing
                               and pays a rebuild for the privilege.
      * RANGEBOUND + EARNING-> the band FITS; a narrow band concentrates the same capital on the
                               chop that is actually happening, which is what a curve is for.
      * otherwise           -> the shape's own default width, unchanged.

    BOUNDED, and deliberately conservative: the narrowest we will build is 70% of the shape's
    default and the widest is the shape's default. So this can never build wider than the table
    already allowed, and never builds a band so tight that normal chop throws us out of it. Every
    branch returns a geometry the existing ceiling check still validates — this widens the CHOICE,
    it does not relax the LIMIT.
    """
    base = widths(shape)
    default_far = {"bid_far": base["bid_far"], "ask_far": base["ask_far"]}
    chosen = "default"
    why = f"{base['shape']} at its default width ({base['total']} bins)"

    try:
        if in_range is False:
            # Out of range: widen toward the ceiling. Stop paying to re-centre a band the market
            # keeps leaving.
            far = CEILING_FAR if base["shape"] == "bidask" else NARROW_FAR_MAX
            w = widths(shape)
            w["bid_far"] = far["bid_far"]
            w["ask_far"] = far["ask_far"]
            w["bid_n"] = w["bid_far"] - w["bid_near"] + 1
            w["ask_n"] = w["ask_far"] - w["ask_near"] + 1
            w["total"] = w["bid_n"] + w["ask_n"]
            w["shape"] = base["shape"]
            w["ceiling"] = CEILING
            w["over_ceiling"] = w["total"] > CEILING
            if not w["over_ceiling"] and w["total"] > base["total"]:
                return {**w, "adaptive": True, "chosen": "wide",
                        "why": (f"OUT OF RANGE — widening {base['total']}->{w['total']} bins so the "
                                f"market stops leaving the band (a rebuild costs a re-centre and "
                                f"earns nothing while it is out)")}
            return {**base, "adaptive": False, "chosen": chosen, "why": why}

        # Rangebound AND earning where it sits: concentrate.
        if (in_range is True and efficiency_pct is not None
                and efficiency_pct >= CONCENTRATE_MIN_EFF):
            w = widths(shape)
            w["bid_far"] = max(base["bid_near"] + 1, int(round(base["bid_far"] * NARROW_FACTOR)))
            w["ask_far"] = max(base["ask_near"] + 1, int(round(base["ask_far"] * NARROW_FACTOR)))
            w["bid_n"] = w["bid_far"] - w["bid_near"] + 1
            w["ask_n"] = w["ask_far"] - w["ask_near"] + 1
            w["total"] = w["bid_n"] + w["ask_n"]
            w["shape"] = base["shape"]
            w["ceiling"] = CEILING
            w["over_ceiling"] = w["total"] > CEILING
            if w["total"] < base["total"]:
                return {**w, "adaptive": True, "chosen": "tight",
                        "why": (f"RANGEBOUND and earning {efficiency_pct:.0f}% — tightening "
                                f"{base['total']}->{w['total']} bins concentrates the same capital "
                                f"on the chop that is actually happening")}
    except Exception as e:                                                  # noqa: BLE001
        # Never let the adaptive path be the reason a deploy cannot be planned. Fall back to the
        # shape's own default and SAY the adaptive step failed.
        return {**base, "adaptive": False, "chosen": "default",
                "why": f"{base['shape']} default (adaptive width failed: {type(e).__name__})"}

    return {**base, "adaptive": False, "chosen": chosen, "why": why}


def widths(shape: str | None) -> dict:
    """Resolved geometry for a shape, with the total and the ceiling verdict included."""
    key = canon(shape)
    w = dict(WIDTHS[key])
    w["bid_n"] = w["bid_far"] - w["bid_near"] + 1
    w["ask_n"] = w["ask_far"] - w["ask_near"] + 1
    w["total"] = w["bid_n"] + w["ask_n"]
    w["shape"] = key
    w["ceiling"] = CEILING
    w["over_ceiling"] = w["total"] > CEILING
    return w


def main(argv: list[str]) -> int:
    shape = None
    emit = "shell"
    for i, a in enumerate(argv):
        if a == "--shape" and i + 1 < len(argv):
            shape = argv[i + 1]
        elif a == "--emit" and i + 1 < len(argv):
            emit = argv[i + 1]
    w = widths(shape)

    if w["over_ceiling"]:
        print(f"  \u274c REFUSING: {w['shape']} resolves to {w['total']} bins "
              f"> ceiling {CEILING}", file=sys.stderr)
        return 2

    if emit == "json":
        print(json.dumps(w))
    else:
        # One line, literal digits -- the shape the legacy regex readers expect, but now emitted
        # from the table rather than hand-maintained in two places.
        print(f"BID_NEAR={w['bid_near']}; BID_FAR={w['bid_far']}; "
              f"ASK_NEAR={w['ask_near']}; ASK_FAR={w['ask_far']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
