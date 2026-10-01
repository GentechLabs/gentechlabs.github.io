#!/usr/bin/env python3
"""test-fed-council-carry.py — pins the carry-reader defect found 2026-09-23.

THE BUG. `_read_regulatory_carry()` scanned the note for `### Carry to Sunday`, collected
`- ` lines, and `break`-ed at the next heading, then sliced `out[-3:]`. The break ended the
scan at the FIRST block, so the slice could never select anything but the first block. The
comment above it promised "keep only the most recent block — the note appends, so the last
one wins"; the code always produced the FIRST. Measured on the live note (3 Carry blocks):
the reader returned the 2026-09-18 lines, and every later update was unreachable.

That matters because the note is APPEND-ONLY BY DESIGN — the whole point of the carry block
is that the newest standing question reaches the Sunday council. A reader pinned to block #1
turns an accumulating note back into a one-shot document, silently.

A test that cannot fail is not a test: the checks below are written to FAIL on the pre-fix
reader. Verified by running this file against a copy of the pre-fix script.

Run:  python3 test-fed-council-carry.py
Exit: 0 all pass · 1 a check failed
"""
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FAILED = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check(label, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        print(f"          got : {got!r}")
        print(f"          want: {want!r}")
        FAILED.append(label)


def check_true(label, got):
    check(label, bool(got), True)


print("=" * 78)
print("  FED COUNCIL — carry-to-Sunday reader regression tests")
print("=" * 78)

c = load(os.path.join(HERE, "weekly-fed-council.py"), "wfc")

NOTE = """# Regulatory Watch — the Chair's notes for the Sunday council

## 2026-09-18 — 2026-90

**THE TEXT**

something.

### Carry to Sunday
- **SEC 2026-90:** OLD LINE — watch for the pool-address registry.
- **Regulation Crypto Assets (comments close 2026-10-20):** OLD decide line.
- **Passive-software line:** OLD autonomy line.

---

## 2026-09-23 — 2026-19407

**THE TEXT**

something newer.

### Carry to Sunday
- **SEC 2026-90:** NEW LINE — the registry now has real occupants.
- **Regulation Crypto Assets (comments close 2026-10-20):** NEW decide line.
- **Passive-software line:** NEW autonomy line.

### Some other trailing section
- a bullet that must NOT be treated as carry
"""

tmp = tempfile.mkdtemp(prefix="carry-test-")
path = os.path.join(tmp, "regulatory-watch-notes.md")
open(path, "w").write(NOTE)

# 1. The static shape: the old bug was `break` inside the scan plus a trailing slice.
_src = open(os.path.join(HERE, "weekly-fed-council.py")).read()
_csrc = "\n".join(l for l in _src.split("\n") if not l.lstrip().startswith("#"))
check_true("no longer breaks out of the scan at the first block",
           'if s.startswith("#") and not s.startswith("### Carry"):\n                break' not in _csrc)
check_true("selects the LAST block explicitly", "blocks[-1]" in _csrc)

# 2. Behavioural: the newest block must be the one returned.
# The reader must accept a path, or this test cannot exercise it. On the pre-fix code it
# takes no argument and the call raises TypeError — report that as a NAMED failure rather
# than a traceback, because a traceback is a worse test result than a named FAIL and hides
# which check broke. (Verified against the pre-fix copy: named FAIL, exit 1, no traceback.)
try:
    got = c._read_regulatory_carry(path)   # the REAL function, against a fixture
except TypeError as e:
    check_true(f"reader is path-injectable so a test can exercise it ({e})", False)
    got = []
check_true("returns the NEWEST carry block", any("NEW LINE" in g for g in got))
check_fail = [g for g in got if "OLD LINE" in g]
check("never returns the OLD block", check_fail, [])
check_true("returns exactly the 3 newest carry lines", len(got) == 3)
check_true("a trailing '### other section' is not read as carry",
           not any("must NOT be treated as carry" in g for g in got))

# 3. The LIVE note. This is the check that matters most, so it may NOT silently skip:
#    an earlier draft caught its own read error and printed a friendly NOTE, then reported
#    ALL CHECKS PASSED — a test that degrades to vacuous on failure, which is the exact
#    bug class this whole file exists to catch. A failure here now FAILS the suite.
LIVE = "/root/vaults/gentech/Treasury/Strategy-Journal/regulatory-watch-notes.md"
try:
    note_txt = open(LIVE).read()
except Exception as e:
    check_true(f"live note is readable ({LIVE}): {e}", False)
    note_txt = None

if note_txt is not None:
    try:
        live = c._read_regulatory_carry(LIVE)
    except TypeError as e:
        check_true(f"live reader is path-injectable too ({e})", False)
        live = []
    check_true("live note returns carry lines", len(live) > 0)
    n_blocks = note_txt.count("### Carry to Sunday")
    print(f"          (live note carries {n_blocks} block(s))")
    check_true("live note has at least one carry block", n_blocks >= 1)
    if n_blocks > 1:
        parts = note_txt.split("### Carry to Sunday")
        first_block, newest_block = parts[1], parts[-1]
        # The premise: block choice is only testable if the blocks actually differ.
        check_true("live blocks differ, so block choice is meaningful",
                   first_block.strip() != newest_block.strip())
        newest_lines = [l.strip()[2:].replace("**", "").strip()
                        for l in newest_block.splitlines() if l.strip().startswith("- ")]
        check_true("the newest block has lines", len(newest_lines) > 0)
        if newest_lines:
            key = newest_lines[0][:40]
            check_true(f"live reader surfaces the NEWEST block, not the first: {key!r}",
                       any(key in l for l in live))

print("\n" + "=" * 78)
if FAILED:
    print(f"  ❌ {len(FAILED)} CHECK(S) FAILED:")
    for f in FAILED:
        print(f"     - {f}")
    print("=" * 78)
    sys.exit(1)
print("  ✅ ALL CHECKS PASSED")
print("=" * 78)
