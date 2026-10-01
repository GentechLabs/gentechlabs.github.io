#!/usr/bin/env python3
"""test_lfj_exit_reserve.py — the reserve check must never PASS on a stale read.

The defect (2026-09-28): `lfj_exit.py` read the native balance ONCE, immediately after the
receipt, then judged `delta <= gas_bound` as "GAS ONLY ✅". A node answering with pre-transaction
state returns the balance unchanged, so `delta` came back **0** — and 0 passes the very check that
exists to catch the reserve being drained. Measured live: it printed `spent 0.00000000` while the
real cost was 0.03181886 AVAX (754,001 gas at 42.2 gwei).

A successful tx with gasUsed > 0 cannot leave the balance unchanged. So a ZERO delta is a STALE
READ, never a pass.

HOW THIS TESTS THE REAL CODE: it extracts the reserve-check block from the live `lfj_exit.py` and
EXECUTES it against a fake node, rather than re-implementing the logic in the test. A replica would
only prove the replica. The old, buggy block is carried here as OLD_BLOCK so the same harness can
demonstrate it FAILING the new assertion — that is the negative control.
"""
import contextlib
import io
import os
import re
import sys
import textwrap
import time

# Keep the poll short so the guard can be exercised cheaply. Production default is 30s.
os.environ["STEWARD_RESERVE_POLL_S"] = "2"

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "lfj_exit.py")

START = "# The reserve can only have been touched by GAS"
END = "# 5. VERIFY"

# The exact pre-fix block, kept as the negative control.
OLD_BLOCK = textwrap.dedent('''\
    # The reserve can only have been touched by GAS. Report the delta so "the exit cannot withdraw
    # the reserve" is a MEASURED statement on this tx, not a claim about the code.
    try:
        _native_after = w3.eth.get_balance(ME)
        _gas_bound = int(r["gasUsed"]) * int(tx.get("gasPrice") or 0)
        _delta = _native_before - _native_after
        print(f"      reserve check: native AVAX {_native_before/1e18:.8f} -> "
              f"{_native_after/1e18:.8f} (spent {_delta/1e18:.8f}, gas bound "
              f"{_gas_bound/1e18:.8f}) — {'GAS ONLY ✅ the reserve was not withdrawn' if _delta <= _gas_bound else '⚠️ MORE THAN GAS LEFT THE WALLET — investigate before trusting the floor doctrine'}")
    except Exception as _e:
        print(f"      reserve check: UNMEASURED ({type(_e).__name__}) — the withdraw's native delta "
              f"was not verified on this run")
''')

results = []


def check(name, ok, detail=""):
    results.append((bool(ok), name, detail))


def extract_block(text):
    """Pull the real reserve-check block out of a source text.

    NOTE: back up to the START of each marker line. `str.index` lands on the `#`, so slicing there
    leaves the first line unindented while the rest keep their 4 spaces — the common prefix is then
    0, `dedent` does nothing, and the extracted block dies with IndentationError.
    """
    i = text.index(START)
    i = text.rfind("\n", 0, i) + 1
    j = text.index(END, i)
    j = text.rfind("\n", i, j) + 1
    return textwrap.dedent(text[i:j]).rstrip() + "\n"


class _Eth:
    def __init__(self, seq):
        self.seq, self.i = seq, 0

    def get_balance(self, _me):
        v = self.seq[min(self.i, len(self.seq) - 1)]
        self.i += 1
        return v


class _W3:
    def __init__(self, seq):
        self.eth = _Eth(seq)


BEFORE = 71_061_630_000_000_000          # 0.07106163 AVAX, the live balance at the exit
GAS_USED = 754_001
GAS_PRICE = 42_200_000_000               # 42.2 gwei, what the tx actually paid
BOUND = GAS_USED * GAS_PRICE             # 0.03181886 AVAX
AFTER_REAL = BEFORE - BOUND              # what the chain actually showed


def run_block(block, seq):
    ns = {
        "w3": _W3(seq),
        "ME": "0xME",
        "_native_before": BEFORE,
        "r": {"gasUsed": GAS_USED},
        "tx": {"gasPrice": GAS_PRICE},
        "time": time,
        "os": os,
        "print": print,
    }
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(block, "<reserve-block>", "exec"), ns)
    return buf.getvalue()


# ── 1. the live source must actually contain the fix ─────────────────────────────────────────────
src = open(SRC).read()
block = extract_block(src)
check("the reserve block was extracted from the LIVE source", "reserve check" in block)
check("the block POLLS (does not read once)", "_deadline" in block and "while time.time()" in block)
check("a zero delta is handled explicitly", "_delta == 0" in block)
check("the old single-read form is GONE",
      "_native_after = w3.eth.get_balance(ME)\n        _gas_bound" not in block)

# ── 2. FROZEN node (the stale read) — the case that must NOT pass ────────────────────────────────
frozen = [BEFORE] * 40
out_new = run_block(block, frozen)
check("FROZEN + fixed: reports UNMEASURED", "UNMEASURED" in out_new, out_new.strip()[:70])
check("FROZEN + fixed: does NOT claim 'GAS ONLY'", "GAS ONLY" not in out_new)
check("FROZEN + fixed: does NOT claim the reserve was intact",
      "was not withdrawn" not in out_new or "do not read this line" in out_new)

# ── 3. NEGATIVE CONTROL — the old block must FAIL the same assertion ─────────────────────────────
out_old = run_block(OLD_BLOCK, frozen)
check("NEGATIVE CONTROL: frozen + OLD block DOES print 'GAS ONLY' (bug reproduced)",
      "GAS ONLY" in out_old, out_old.strip()[:70])
check("NEGATIVE CONTROL: so the assertion above is falsifiable",
      ("GAS ONLY" in out_old) and ("GAS ONLY" not in out_new))

# ── 4. a real, moved balance must still PASS ─────────────────────────────────────────────────────
seq_moved = [BEFORE, BEFORE, AFTER_REAL] + [AFTER_REAL] * 30
out_ok = run_block(block, seq_moved)
check("MOVED within bound: reports GAS ONLY", "GAS ONLY" in out_ok, out_ok.strip()[:90])

# ── 5. and a genuine reserve drain must still be CAUGHT ──────────────────────────────────────────
drained = BEFORE - (BOUND * 4)
seq_bad = [BEFORE, BEFORE, drained] + [drained] * 30
out_bad = run_block(block, seq_bad)
check("MOVED beyond bound: reports MORE THAN GAS LEFT", "MORE THAN GAS LEFT" in out_bad,
      out_bad.strip()[:90])

passed = sum(1 for ok, _, _ in results if ok)
print()
print(f"  RESULT: {'PASS' if passed == len(results) else 'FAIL'} — {passed}/{len(results)} checks passed")
for ok, name, detail in results:
    if not ok:
        print(f"    FAILED: {name}  {detail}")
sys.exit(0 if passed == len(results) else 1)
