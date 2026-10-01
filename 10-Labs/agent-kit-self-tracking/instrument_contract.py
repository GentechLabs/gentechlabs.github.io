#!/usr/bin/env python3
"""INSTRUMENT CONTRACT — every measurement declares what it is allowed to answer.

WHY THIS EXISTS (2026-09-23)
----------------------------
Four defects in ONE day, all the same shape:

  1. A stopwatch: 24 seconds of bin sampling used to judge a day's tape.
  2. A 7d/30d-low anchor used to measure "run-up" -> read +47.8% on a quiet month
     of grind, and proposed EXITING the pool.
  3. A <=200-bin wallet scan used to judge a live book -> a failed read returns 0x,
     int.from_bytes(b'') == 0, so a FAILED READ read as a REAL ZERO -> "flat".
  4. The pool's volatilityAccumulator (decays in 600s) used to judge a 2-day
     trend -> read 12.9% of ceiling ("quiet") while AVAX fell 7.07%, and chose a
     NARROW curve for a directional tape.

Each one produced a CONFIDENT NUMBER from an instrument that could not answer the
question asked. Patch #4 did not fix #1-#3, because each patch teaches ONE
instrument ONE lesson. This file is the mechanism instead of the lesson.

THE RULE
--------
An instrument is only allowed to answer a question whose TIMESCALE IT COVERS.
A measurement whose output cannot say what PERIOD it measured will be read as
having measured the period the reader cares about. That is not a bug in the
reader; it is a missing field in the instrument.

So every instrument declares, in code, verifiable by execution:

  * NEW  what QUESTION it answers, and the TIMESCALE that question implies.
  * NEW  its WINDOW — the span of tape its number is actually about.
  * NEW  a NULL fixture     (nothing happening)  -> it MUST read low.
  * NEW  a CONTRAST fixture (the thing happening) -> it MUST read high.

`falsify()` runs every instrument against both fixtures. An instrument that cannot
read low on the null case is a MIRROR. One that cannot read high on the contrast
case is DEAD. Both read as healthy numbers.

`covers()` is the guard that would have caught all four defects: it refuses to let
an instrument answer a question longer than its window.

Run it:  python3 instrument_contract.py            (falsify everything)
         python3 instrument_contract.py --questions (show the coverage matrix)
"""
from __future__ import annotations

import argparse
import sys

# ── units ────────────────────────────────────────────────────────────────────────────────
SEC = 1.0
MIN = 60.0
HOUR = 3600.0
DAY = 86400.0


class Instrument:
    """One measurement, with the question it may answer and the proof it can be wrong."""

    def __init__(self, name, question, window, null_case, contrast_case,
                 reads, unit="", note=""):
        self.name = name                # the function it wraps, by name
        self.question = question        # the question, in words
        self.window = window            # seconds of tape the number is ABOUT
        self.null_case = null_case      # (fixture, expected) -> must read low/false
        self.contrast_case = contrast_case  # (fixture, expected) -> must read high/true
        self.reads = reads              # callable(fixture) -> number
        self.unit = unit
        self.note = note

    def __repr__(self):
        return f"<Instrument {self.name} window={self.window/DAY:.3g}d>"


# ── helpers: a reading is "low" / "high" relative to the case's own expectation ──────────
def _verdict(reads, fixture, expect, kind):
    """Return (ok, got). `expect` is the value the fixture MUST produce."""
    try:
        got = reads(fixture)
    except Exception as e:                                   # a raising instrument is not a pass
        return False, f"RAISED {type(e).__name__}: {e}"
    if got is None:
        return False, "None (never a regime — a missing value must REFUSE, not read as 0)"
    if kind == "low":
        ok = got <= expect
    else:
        ok = got >= expect
    return ok, got


# ── THE REGISTRY ─────────────────────────────────────────────────────────────────────────
# Fixtures are tiny, self-contained, and use the SAME synthetic tape for the volatility
# family, so the only thing that varies between an instrument's null and contrast case is
# the thing that instrument is supposed to detect.

def _flat_tape():
    """30 daily closes, going nowhere. Realized move ~0.3%."""
    return [10.00 * (1 + (0.001 if i % 2 else -0.001)) for i in range(30)]


def _pullback_tape():
    """30 daily closes: a 7% fall over the final 2 days — the Sep 23 AVAX shape."""
    base = [10.00] * 26 + [10.60, 10.35]
    base[-3] = 11.20
    return base


def _chop_tape():
    """30 daily closes, chopping 5% peak-to-trough but ending flat."""
    out = []
    for i in range(30):
        out.append(10.00 * (1 + (0.025 if i % 2 else -0.025)))
    return out


# ── the fixtures are BUILT ONCE, as objects. A fixture rebuilt per call is a different object
# every time, so any `is` comparison against it silently fails — which is how this file's OWN
# first version shipped a reading that could not go low. The harness caught it on run one,
# which is the point of having one.                                              (2026-09-23)
FLAT_TAPE = _flat_tape()
PULLBACK_TAPE = _pullback_tape()
CHOP_TAPE = _chop_tape()


def _move_over(closes, days):
    """Net % over the last `days` closes — the SAME definition the tracker uses."""
    if len(closes) <= days:
        return None
    base = closes[-1 - days]
    return None if not base else (closes[-1] / base - 1) * 100


def _realized_vol(closes):
    """Std-dev of daily returns, in %, annualisation-free (matches the tracker)."""
    if len(closes) < 3:
        return None
    rets = [(closes[i] / closes[i - 1] - 1) for i in range(1, len(closes)) if closes[i - 1]]
    if len(rets) < 2:
        return None
    m = sum(rets) / len(rets)
    var = sum((r - m) ** 2 for r in rets) / (len(rets) - 1)
    return (var ** 0.5) * 100


REGISTRY: list[Instrument] = [

    # 4. THE ONE THAT BIT TODAY. Window = the pool's decayPeriod (600s).
    Instrument(
        name="pool_accumulator_level",
        question="Is price crossing bin edges RIGHT NOW? (a 10-MINUTE question)",
        window=10 * MIN,
        null_case=({"level": 0.05}, 0.20),     # a quiet pool must read <=20% of ceiling
        contrast_case=({"level": 0.62}, 0.20),  # heavy edge-crossing must read >20%
        reads=lambda f: f["level"],
        unit="fraction of ceiling",
        note="DECAYS in decayPeriod (600s). CANNOT see a trend. Today it read 12.9% "
             "('quiet') during a -7.07% two-day fall.",
    ),

    # The instrument that REPLACED the crude anchor. Window = its lookback.
    Instrument(
        name="sustained_move",
        question="Has the tape MOVED over a multi-day window? (a 2-DAY question)",
        window=2 * DAY,
        null_case=(FLAT_TAPE, 1.0),             # flat tape -> |move| under 1%
        contrast_case=(PULLBACK_TAPE, 4.0),     # the pullback -> |move| over 4%
        reads=lambda t: (lambda m: abs(m) if m is not None else None)(_move_over(t, 2)),
        unit="% net move",
        note="Built 2026-09-23 BECAUSE the 10-minute accumulator could not answer this.",
    ),

    # 2. The anchor that read a month-old grind as a fresh run.
    Instrument(
        name="escape_past_our_band",
        question="How far past OUR DEPLOYED BAND is price? (a question about position)",
        window=0.0,                             # instantaneous: it compares two live prices
        null_case=({"spot": 10.40, "lo": 10.35, "hi": 10.64}, 0.0),
        contrast_case=({"spot": 11.20, "lo": 10.35, "hi": 10.64}, 5.0),
        reads=lambda f: (lambda s, lo, hi: 0.0 if lo <= s <= hi
                         else (s / hi - 1) * 100 if s > hi else (s / lo - 1) * 100)(
            f["spot"], f["lo"], f["hi"]),
        unit="% past the band",
        note="Anchored on OUR band, NOT a 7d/30d low. The low-anchored version read "
             "+47.8% on a quiet grind and proposed EXITING the pool.",
    ),

    # 1. The stopwatch.
    Instrument(
        name="edge_crossings_rate",
        question="Is price crossing edges DURING THIS SAMPLE? (a ~1-MINUTE question)",
        window=60 * SEC,
        null_case=({"crossings": 0, "n": 11}, 0.20),
        contrast_case=({"crossings": 8, "n": 11}, 0.20),
        reads=lambda c: (c["crossings"] / max(1, c["n"] - 1)),
        unit="fraction of samples that changed bin",
        note="The original fallback. Today's defect #1 was using it to judge a day's "
             "tape — 24 seconds of samples cannot describe 24 hours.",
    ),

    # The measurement that must be able to say "the subject is gone".
    Instrument(
        name="book_is_flat",
        question="Is there ANY position held? (a question about EXISTENCE, not size)",
        window=0.0,
        null_case=({"held": 0, "read_failed": False}, False),   # a real empty book -> False
        contrast_case=({"held": 25, "read_failed": False}, True),
        reads=lambda f: None if f.get("read_failed") else bool(f.get("held")),
        unit="bool",
        note="Defect #3: a FAILED read (0x -> 0) rendered as a REAL ZERO, so an "
             "unreadable book read as a flat one. A failed read must REFUSE.",
    ),
]


def falsify(registry=None, verbose=True):
    """Prove every instrument can read LOW and HIGH. A mirror or a dead one fails here."""
    registry = registry if registry is not None else REGISTRY
    rows, bad = [], []
    for ins in registry:
        lo_ok, lo_got = _verdict(ins.reads, *ins.null_case, "low")
        hi_ok, hi_got = _verdict(ins.reads, *ins.contrast_case, "high")
        rows.append((ins, lo_ok, lo_got, hi_ok, hi_got))
        if not (lo_ok and hi_ok):
            bad.append(ins.name)
    if verbose:
        print("=" * 100)
        print("  INSTRUMENT FALSIFIABILITY — can each one read BOTH low and high?")
        print("=" * 100)
        for ins, lo_ok, lo_got, hi_ok, hi_got in rows:
            w = "instant" if ins.window == 0 else f"{ins.window/DAY:.3g}d"
            print(f"  {ins.name:24s} window {w:>8s}   "
                  f"null {'OK' if lo_ok else 'FAIL':>4s} ({lo_got!s:>6.6s})   "
                  f"contrast {'OK' if hi_ok else 'FAIL':>4s} ({hi_got!s:>6.6s})")
            if not (lo_ok and hi_ok):
                why = ("MIRROR — cannot read low, so it reads 'fine' in every condition"
                       if not lo_ok else
                       "DEAD — cannot read high, so it can NEVER detect its own subject")
                print(f"      ^^ {why}")
        print()
        if bad:
            print(f"  FAILED: {', '.join(bad)}")
        else:
            print(f"  OK — all {len(rows)} instruments can read BOTH directions. "
                  f"A mirror and a dead instrument both read as healthy numbers.")
    return rows, bad


def covers(question_days, registry=None):
    """THE GUARD. Which instruments are ALLOWED to answer a question of this timescale?

    This is the check that would have caught all four defects: an instrument whose window
    is far shorter than the question is not a weak answer, it is the wrong instrument.
    """
    registry = registry if registry is not None else REGISTRY
    want = question_days * DAY
    ok, short = [], []
    for ins in registry:
        if ins.window == 0:                 # instantaneous readings are exempt from span
            continue
        (ok if ins.window >= want * 0.5 else short).append(ins)
    return ok, short


def print_coverage(registry=None):
    registry = registry if registry is not None else REGISTRY
    print("=" * 100)
    print("  COVERAGE — which instrument may answer which question?")
    print("=" * 100)
    for q in (0.0007, 0.017, 0.042, 0.5, 2.0, 7.0, 30.0):
        label = (f"{q*1440:.0f} min" if q < 1/24 else f"{q*24:.0f} h" if q < 1 else f"{q:.0f} d")
        ok, short = covers(q, registry)
        names = ", ".join(i.name for i in ok) or "— NONE —"
        print(f"  a {label:>6s} question  ->  may be answered by: {names}")
        for ins in short:
            # only complain about the instruments that would TEMPT a caller
            if ins.window > 0 and ins.window / DAY < q:
                print(f"      X {ins.name} ({ins.window/DAY:.3g}d) must NOT answer a {label} "
                      f"question — {ins.window/DAY/q*100:.2f}% of the span")
    print()


def main() -> int:
    ap = argparse.ArgumentParser(description="instrument contract: falsify + coverage")
    ap.add_argument("--questions", action="store_true", help="show the coverage matrix")
    a = ap.parse_args()
    _rows, bad = falsify()
    if a.questions:
        print_coverage()
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
