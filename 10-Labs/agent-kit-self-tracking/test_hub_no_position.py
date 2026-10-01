#!/usr/bin/env python3
"""
test_hub_no_position.py — lock the "No position" honesty fix.

THE BUG THIS LOCKS (2026-09-28):
    Jordan exited the LFJ pool on purpose. The hub printed "Unknown" — the same label it uses
    when the chain read FAILS. Two different worlds, one word:
        (a) we could not measure the book  -> "Unknown" is correct and honest
        (b) we measured it perfectly and it is FLAT (0 bins held) -> "No position"
    (b) rendering as (a) tells Jordan his dashboard is broken when it is working correctly.

THE RULE: a zero may only be reported as a KNOWN state when the scan that produced it was
COMPLETE. A truncated window or an unresolved bin means absence of a bin is not evidence of
absence of a position, and the page must still say "Unknown".

Reads defi_hub_data.py as SOURCE TEXT and compiles it, deliberately NOT importing it: Python
validates cached bytecode on (mtime, size) only, so a same-second, same-length edit is invisible
to the import system and the test would assert against stale bytecode. (This exact trap produced
a false alarm earlier in the same file.)
"""
import re
import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "defi_hub_data.py"

FAILS = []


def check(name, cond, detail=""):
    if cond:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}  {detail}")
        FAILS.append(name)


def main():
    if not SRC.exists():
        print(f"  ❌ source not found: {SRC}")
        return 1
    text = SRC.read_text(encoding="utf-8")

    # ── 1. the payload must distinguish the two worlds ────────────────────────────────
    check("payload branches on a COMPLETE scan before claiming No position",
          '"No position" if (_scan_complete and not has_pos)' in text)

    # The real invariant: an actual False must be consumed by "Out of Range" BEFORE the flat-book
    # test can see it — otherwise a genuinely out-of-range book would be mislabelled "No position".
    # (My first version of this assertion demanded the wrong order and failed on correct source.)
    # A missing substring must FAIL the check, not raise: an unhandled ValueError aborts the whole
    # suite and reports nothing, which is how a guard silently stops guarding.
    def _at(needle):
        return text.index(needle) if needle in text else -1

    i_in, i_out, i_np = (_at('"In Range" if in_range'),
                         _at('"Out of Range" if in_range is False'),
                         _at('"No position" if (_scan_complete'))
    check("an explicit False is handled BEFORE the flat-book case",
          -1 not in (i_in, i_out, i_np) and i_in < i_out < i_np,
          f"(order was in={i_in} out={i_out} no-position={i_np}; -1 means the branch is MISSING)")

    # ── 2. both names must be bound on EVERY path (the bug I made writing this) ──────
    check("_scan_complete initialised before the try (never unbound)",
          re.search(r"_scan_complete\s*=\s*False\s*\n\s*try:", text) is not None)
    check("has_pos initialised before the try (never unbound)",
          re.search(r"has_pos\s*=\s*False\s*\n\s*_scan_complete\s*=\s*False", text) is not None)

    # ── 3. _scan_complete must use the SAME completeness test as the unreadable line ──
    # The assignment spans two lines (the `and not (d.get("partial_bins") or []))` is on the next),
    # so the regex must allow the newline. My first version required `)` on the same line and
    # failed on correct source.
    m = re.search(r"_scan_complete\s*=\s*\(.*?\)\)", text, re.S)
    check("_scan_complete tests truncated_low", m and "truncated_low" in m.group(0))
    check("_scan_complete tests truncated_high", m and "truncated_high" in m.group(0))
    check("_scan_complete tests partial_bins", m and "partial_bins" in m.group(0))

    # ── 4. the JS must render the words, and must not style it as a failure ──────────
    check("JS renders NO POSITION text", '"NO POSITION"' in text)
    check("JS explains why in a title", "scan completed and found zero bins" in text)
    check("JS keeps UNKNOWN as the fallback (not in/out)",
          '? "OUT OF RANGE" : "UNKNOWN"' in text)

    # ── 5. the pill must not be red for no-position: it stays the neutral 'unk' class ─
    check("pill class for No position stays neutral ('unk'), not 'out'",
          'd.in_range === true ? "in" : d.in_range === false ? "out" : "unk"' in text)

    # ── 6. non-vacuity: the three-way branch must actually exist ────────────────────
    check("all three states present (In Range / Out of Range / No position)",
          all(s in text for s in ('"In Range"', '"Out of Range"', '"No position"')))

    print()
    if FAILS:
        print(f"  {len(FAILS)} FAILED: {', '.join(FAILS)}")
        return 1
    print("  all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
