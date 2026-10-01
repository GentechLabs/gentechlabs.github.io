#!/usr/bin/env python3
"""
transition_map.py — SCENARIOS AS STATES, MOVES AS TRANSITIONS.

Jordan, 2026-09-24:
    "For a long time, we've talked about how to predict different scenarios and what to do in
     different scenarios. But we never talk about going from bullish to bearish or bearish to
     bullish or transitioning different scenarios."

    "Like on a controller, let's say Street Fighter... it'll show all different directions --
     left, right, up, down, then you got the corners. What if we introduce something called
     TRANSITIONS, and we have certain transitions that go well together. For instance you
     transition from a 70/30 bid-ask to a 60/40 curve, and then as the curve starts to perform
     well, then you go to 50/50. I think our ideas work better as transitions."

WHY THIS EXISTS
---------------
Every rule built so far is a CLASSIFIER: read the market, name the scenario, jump the book to
whatever that scenario implies. There is no notion of WHERE YOU ARE or WHAT YOU CAN BECOME FROM
HERE. That is the structural cause of the churn and of the blind spots:

  * A classifier has no neighbours, so it can leap 45-bin bid-ask -> 25-bin curve in one action.
  * A classifier has no dwell, so one noisy reading can move a funded book.
  * A classifier has no "why", because it never had a "from".

A TRANSITION has all three: a `from`, a `to`, a guard that licenses the crossing, and a dwell that
stops a single sample from thrashing the book. **You step to a neighbour; you never teleport.**

And this is not new doctrine — it is Jordan's own, finally written as one thing:
    "Don't switch, ADD."                        -> a transition, not a switch
    "Ladder DOWN, get paid while waiting."      -> a transition with an order
    "60/40 if still pulling back, 50/50 if flat" -> two rungs of the same ladder
    "Withdraw, hold the asset, wait for stability" -> a transition into EXIT
    "Volatile -> bid-ask; stable -> curve"      -> a transition between shapes

THE LADDER (Jordan's example, made concrete):
    70/30 bid-ask  ->  60/40 curve  ->  50/50 curve
    Each step needs the previous one to be WORKING. You do not go from a heavy volatile book
    straight to neutral; you earn your way there, one rung at a time.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ── THE STATES ──────────────────────────────────────────────────────────────────────────────
# A state is a POSITION THE BOOK CAN HOLD: shape + bin count + ratio. Not a mood, not a label --
# something you can actually deploy and verify on chain.
#   ratio = the ASK / WAVAX share. 0.70 = 70% of value in the ask leg (heavy, bullish).
STATES = {
    "VOLATILE_HEAVY": dict(shape="bid-ask", bins=45, ratio=0.70, lean="bullish",
                           why="riding a confirmed up-move: most of the book sells into strength"),
    "VOLATILE_BALANCED": dict(shape="bid-ask", bins=45, ratio=0.50, lean="neutral",
                              why="two-way volatility with no direction: the wide U earns both edges"),
    "VOLATILE_DRY": dict(shape="bid-ask", bins=45, ratio=0.30, lean="bearish",
                         why="breaking down: USDC-heavy, dry powder for the dip"),
    "COOLING_HEAVY": dict(shape="curve", bins=25, ratio=0.60, lean="mildly bullish",
                          why="volatility falling but still leaning up: a bell, still a little heavy"),
    "RANGE_NEUTRAL": dict(shape="curve", bins=25, ratio=0.50, lean="neutral",
                          why="rangebound: the bell peaks at spot, so the centre collects"),
    "RANGE_DRY": dict(shape="curve", bins=25, ratio=0.40, lean="mildly bearish",
                      why="drifting lower inside a range: keep the bell, keep more USDC"),
    "EXIT_STABLE": dict(shape=None, bins=0, ratio=None, lean="flat",
                        why="no band holds this move: flat USDC, wait for stability, re-enter later"),
}

# ── THE TRANSITIONS ─────────────────────────────────────────────────────────────────────────
# Each entry: (from, to) -> guard + the REASON the guard exists. A transition with no guard is a
# classifier wearing a costume, so every edge here must be licensed.
TRANSITIONS = {
    # --- the bullish ladder up ---
    ("RANGE_NEUTRAL", "COOLING_HEAVY"): dict(
        guard="recent tape trending up, not just chopping (net > +1% over the window)",
        why="a range that starts leaning up wants more of the book working the ask side"),
    ("COOLING_HEAVY", "VOLATILE_HEAVY"): dict(
        guard="volatility expanding AND direction confirmed up (not one candle)",
        why="only a CONFIRMED move deserves a 45-bin wide, ask-heavy book"),
    ("VOLATILE_HEAVY", "COOLING_HEAVY"): dict(
        guard="move has stalled: recent tape rangebound after the run",
        why="a finished move no longer needs a wide U; the bell earns more in chop"),

    # --- the cooling ladder down ---
    ("COOLING_HEAVY", "RANGE_NEUTRAL"): dict(
        guard="tape flat: no direction in either direction",
        why="neutral tape -> neutral book; a lean is only worth carrying while it is true"),
    ("RANGE_NEUTRAL", "RANGE_DRY"): dict(
        guard="drifting lower but inside the band (no confirmed break)",
        why="Jordan's rule: 60/40 while still pulling back, 50/50 when flat -- the same rung, one down"),
    ("RANGE_DRY", "VOLATILE_DRY"): dict(
        guard="break DOWN confirmed (speed, not depth) -- sigma/hr, not a percentage",
        why="a confirmed break needs the wide U with the money on the USDC side"),

    # --- the exit and the return ---
    ("VOLATILE_DRY", "EXIT_STABLE"): dict(
        guard="no approved band holds the move: speed exceeds what 45 bins can absorb",
        why="Jordan: 'why not exit the pool and convert to the stable coin and wait it out?'"),
    ("VOLATILE_HEAVY", "EXIT_STABLE"): dict(
        guard="the run is so big that further gains are hard (+5/+10/+20%)",
        why="bullish mode: withdraw, hold the asset, wait for stability"),
    ("EXIT_STABLE", "RANGE_NEUTRAL"): dict(
        guard="2-day move < 4% AND recent tape rangebound (stability actually returned)",
        why="re-enter as a CURVE: a bell is the right first step out of cash, never a wide U"),

    # --- two-way volatility, no direction ---
    ("RANGE_NEUTRAL", "VOLATILE_BALANCED"): dict(
        guard="volatility expanding with NO confirmed direction",
        why="a wide U earns both edges when the price swings without going anywhere"),
    ("VOLATILE_BALANCED", "RANGE_NEUTRAL"): dict(
        guard="tape rangebound again",
        why="the U's design point is the edges; when price sits centre it earns nothing"),
    ("VOLATILE_HEAVY", "VOLATILE_BALANCED"): dict(
        guard="the up-move failed: momentum reversed, direction no longer confirmed",
        why="strip the lean before stripping the width -- the shape is still right"),
    ("VOLATILE_BALANCED", "VOLATILE_HEAVY"): dict(
        guard="direction confirmed up",
        why="add the lean only when there is a direction to lean into"),
    ("VOLATILE_DRY", "VOLATILE_BALANCED"): dict(
        guard="the down-move failed: direction no longer confirmed",
        why="mirror of the line above"),
    ("VOLATILE_BALANCED", "VOLATILE_DRY"): dict(
        guard="direction confirmed down",
        why="mirror of the line above"),
    ("RANGE_DRY", "RANGE_NEUTRAL"): dict(
        guard="the pullback ended (tape flat again)",
        why="stop carrying a lean that is no longer true"),
}

# ── ADJACENCY: who is a NEIGHBOUR of whom ───────────────────────────────────────────────────
# This is the controller. You may only step to a state you are ADJACENT to. A move that is not an
# edge above is not forbidden -- it is DECOMPOSED into steps, so the book walks the ladder instead
# of teleporting. This is what stops 45-bin bid-ask -> 25-bin curve in one action.
ADJACENT = {}
for (a, b) in TRANSITIONS:
    ADJACENT.setdefault(a, set()).add(b)


def neighbours(state):
    return sorted(ADJACENT.get(state, set()))


def ladder(src, dst, _seen=None):
    """The shortest legal walk from src to dst. Returns [src, ..., dst] or None.

    THIS IS THE POINT OF THE WHOLE MODULE. 'Go from a 70/30 bid-ask to a 50/50 curve' is not one
    action -- it is a sequence, and every rung has its own guard. A plan that cannot be walked is
    not a plan; it is a wish.
    """
    if src == dst:
        return [src]
    if src not in STATES or dst not in STATES:
        return None
    _seen = _seen or {src}
    best = None
    for nxt in neighbours(src):
        if nxt in _seen:
            continue
        path = ladder(nxt, dst, _seen | {nxt})
        if path and (best is None or len(path) < len(best)):
            best = path
    return [src] + best if best else None


def describe(state):
    s = STATES.get(state)
    if not s:
        return f"{state}: UNKNOWN STATE"
    sh = s["shape"] or "flat (no position)"
    r = f"{s['ratio']:.0%} ask/WAVAX" if s["ratio"] is not None else "-"
    return f"{state:<18} {sh:<9} {s['bins']:>3} bins  {r:<16} {s['lean']:<15} {s['why']}"


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--state":
        print(describe(sys.argv[2]))
        return
    print("=" * 110)
    print("  TRANSITION MAP — scenarios are STATES, moves are TRANSITIONS")
    print("=" * 110)
    print()
    for name in STATES:
        print("  " + describe(name))
    print()
    print("=" * 110)
    print("  THE LADDERS (a jump that is not an edge is walked, not teleported)")
    print("=" * 110)
    for src, dst in [("VOLATILE_HEAVY", "RANGE_NEUTRAL"),
                     ("VOLATILE_HEAVY", "EXIT_STABLE"),
                     ("EXIT_STABLE", "RANGE_NEUTRAL"),
                     ("RANGE_NEUTRAL", "VOLATILE_HEAVY"),
                     ("RANGE_NEUTRAL", "RANGE_DRY")]:
        path = ladder(src, dst)
        print(f"\n  {src}  ->  {dst}")
        if not path:
            print("     ❌ NO LEGAL WALK — this transition is not reachable. That is a gap in the map.")
            continue
        for i, step in enumerate(path):
            mark = "   " if i == 0 else f" {i}."
            print(f"   {mark} {step}")
            if i > 0:
                g = TRANSITIONS.get((path[i - 1], step))
                if g:
                    print(f"        needs: {g['guard']}")
        print(f"     = {len(path) - 1} step(s), each with its own licence")


if __name__ == "__main__":
    main()
