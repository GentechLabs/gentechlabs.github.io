#!/usr/bin/env python3
"""Falsifiable tests for lfj_shapes.shape_of_mass — the mass-based shape reader.

WHY THIS EXISTS (2026-09-30): the classifier was added the same night the count-based one produced
a live false reading, and it shipped with NO TEST. This suite has already watched three classifiers
fail silently on the exact state they were written to catch, so the tests assert the PROPERTY --
width independence -- not the implementation.

The property: a book's shape is where the MONEY sits, so the answer must not change when the same
shape is built at a different width. That is the single thing the old count-based reader could not
do, and it is what these tests pin.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lfj_shapes as LS

PASS = FAIL = 0
def check(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1; print(f"  PASS  {name}")
    else:
        FAIL += 1; print(f"  FAIL  {name}  got {got!r} want {want!r}")

def bell(n):
    """A bell: money at the CENTRE — a curve."""
    c = (n - 1) / 2.0
    return {i: int((1 - abs(i - c) / c) * 10000) + 1 for i in range(n)}

def u_shape(n):
    """A U: money at the EDGES — a bid-ask."""
    c = (n - 1) / 2.0
    return {i: int(abs(i - c) / c * 10000) + 1 for i in range(n)}

def flat(n):
    return {i: 10000 for i in range(n)}

print("\n  ── WIDTH INDEPENDENCE: the property the count test lacked ──")
# The old reader named a 40-bin bell "bid-ask". The new one must name every width the same.
for n in (18, 25, 30, 40, 45):
    check(f"{n}-bin bell reads curve", LS.shape_of_mass(bell(n)), "curve")
for n in (18, 25, 31, 45):
    check(f"{n}-bin U reads bid-ask", LS.shape_of_mass(u_shape(n)), "bid-ask")

print("\n  ── THE LIVE FAILURE, PINNED ──")
# 40 bins was legal for NEITHER geometry, so the count test returned "" and the cross-reader
# disagreement followed. The mass test must still name it.
check("40-bin bell (the live book) does not return ''", LS.shape_of_mass(bell(40)) != "", True)
check("40 bins is genuinely illegal for the count test",
      LS.shape_of_bins(list(range(40))), "")

print("\n  ── HONESTY: an unnameable book says so, never guesses ──")
check("flat book is not guessed at", LS.shape_of_mass(flat(30)), "")
check("empty book returns nothing", LS.shape_of_mass({}), "")
check("single bin returns nothing", LS.shape_of_mass({5: 100}), "")
check("zero amounts returns nothing", LS.shape_of_mass({1: 0, 2: 0, 3: 0}), "")

print("\n  ── SYMMETRY: mirroring a book must not change its shape ──")
b = bell(30)
check("bell mirrored is still a curve",
      LS.shape_of_mass({-k: v for k, v in b.items()}), "curve")

print(f"\n  RESULT: {'PASS' if FAIL == 0 else 'FAIL'} — {PASS}/{PASS+FAIL} checks passed")
sys.exit(1 if FAIL else 0)
