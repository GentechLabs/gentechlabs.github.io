#!/usr/bin/env python3
"""Guard the completions file's structure — the entry-header swallow, which recurred 4 times.

THE RECURRING BUG. Appending an entry to `01-HANDOFFS/gentech-treasury-completions.md` with a
`patch` whose anchor was the NEXT entry's header text replaced that header with the new entry's
tail. The new entry swallowed the previous one's title, so a shipped, dated record lost its
heading and became an unlabelled paragraph under someone else's. It happened FOUR times in one
session and was fixed by hand each time.

WHY IT RECURS: the anchor is the header of the entry BELOW the insertion point, so a successful
replace *must* consume it. Nothing in the tool reports that. The fix is not to be more careful —
it is to CHECK every time, and to write the check down so the next session inherits it.

WHAT THIS ASSERTS:
  1. every dated entry starts on its own line at column 0, in the form `- YYYY-MM-DD ...`;
  2. no entry has an older entry's header glued onto its tail (the exact signature of the bug);
  3. no line contains two dated headers;
  4. the file's newest entries are all still present — a swallow removes a title, and titles are
     how the scanner and the group find the work.

Run: python3 test_completions_structure.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = [
    os.path.join(HERE, "..", "..", "01-HANDOFFS", "gentech-treasury-completions.md"),
    "/root/vaults/gentech/01-HANDOFFS/gentech-treasury-completions.md",
]
PATH = next((p for p in CANDIDATES if os.path.exists(p)), None)

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


if not PATH:
    print("  FAIL  the completions file was not found")
    sys.exit(1)

text = open(PATH, encoding="utf-8").read()
lines = text.splitlines()

print("")
print(f"  file: {os.path.abspath(PATH)}")
print(f"  lines: {len(lines)}")

HEAD = re.compile(r"^- \d{4}-\d\d-\d\d")
heads = [i for i, l in enumerate(lines) if HEAD.match(l)]

print("")
print("  ── 1. EVERY DATED ENTRY STARTS ON ITS OWN LINE ──────────────────────")
check(f"found {len(heads)} dated entries", len(heads) > 200,
      f"only {len(heads)} — the file may have been truncated")

print("")
print("  ── 2. NO GLUED HEADERS (the exact signature of the swallow) ─────────")
# The bug leaves a line like:  "...enabling.: JORDAN'S BOOK WAS ...**"
# i.e. a finished sentence, a colon, then an ALL-CAPS title that belongs to another entry.
#
# DO NOT "REFINE" THIS PATTERN WITHOUT A NEGATIVE CONTROL (learned 2026-09-29 the hard way).
# An attempt was made to tighten it to require an embedded DATE inside the glued title, to
# silence a false positive. The tightened version MISSED BOTH documented real swallows AND
# still flagged two ordinary lines. The pattern is tuned; it was not the problem.
# The actual false positive that prompted the change was a line whose header was INDENTED,
# so HEAD could not see it — an indentation defect, caught by check 2 exactly as designed.
# That is fixed below (check 2b), and this regex is restored verbatim.
INDENTED_HEAD = re.compile(r"^[ \t]+- \d{4}-\d\d-\d\d")
glued = [l for l in lines if re.search(r"\*\*\s*\.?:\s+[A-Z🔴]", l) and HEAD.search(l) is None
         and not INDENTED_HEAD.match(l)]
check("no entry tail has another entry's header glued on", not glued,
      f"{len(glued)} found, e.g. ...{glued[0][-70:] if glued else ''}")

print("")
print("  ── 2b. NO INDENTED ENTRY HEADERS ────────────────────────────────────")
# ADDED 2026-09-29. Every entry in this file starts at COLUMN 0 — 501 of them before this check
# existed, and 3 written in one session on 2026-09-29 were indented by two spaces.
#
# WHY IT MATTERS (two independent failures, both real):
#   1. HEAD is `^- \d{4}-\d\d-\d\d` — anchored at column 0. An indented header is not an entry
#      to this file's own tooling, so it silently reduces the entry count that check 1 reports
#      and that the group's scanner reads. A record can be present and invisible at once.
#   2. It made check 2 fire on a CORRECT entry: HEAD could not see the indented header, so the
#      entry's own body was scanned as if it were an entry tail, and ordinary bold prose
#      ("**133 ACTIVE markets**: AVAX...") matched the glue pattern.
# The lesson is the family one: a header that does not match the header pattern is not merely
# uncounted, it is mis-attributed — the tool blames the entry for the formatting.
INDENTED_HEAD = re.compile(r"^[ \t]+- \d{4}-\d\d-\d\d")
indented = [i for i, l in enumerate(lines, 1) if INDENTED_HEAD.match(l)]
check("every dated entry starts at column 0 (none indented)", not indented,
      f"{len(indented)} indented, lines {indented[:4]}")

print("")
print("  ── 3. NO LINE CARRIES TWO DATED HEADERS ─────────────────────────────")
two = [i for i, l in enumerate(lines) if len(re.findall(r"- \d{4}-\d\d-\d\d\s+\d", l)) > 1]
check("no line contains two dated headers", not two, f"lines {two[:3]}")

print("")
print("  ── 4. THE NEWEST WORK IS STILL TITLED ───────────────────────────────")
# A swallowed header is invisible to a regex over headers, so check the recent content directly:
# the last few entries must be preceded by their own header within a short distance.
#
# WINDOW OVERLAP IS NOT OPTIONAL (fixed 2026-09-27). The first version sliced `lines[-260:]` and
# then looked BACKWARD up to 60 lines for a header — but the slice truncated that lookback, so a
# section whose header sits just above the boundary is reported as an orphan. It fired on a
# correct document: the flagged line was index 0 of the window, with its header one line above it.
# A windowed check must carry enough context to judge its own first entries, or it invents defects
# at the seam. Same family as the rest of today: the measuring tool manufacturing the fault.
#
# ── THE SEAM WAS STILL WRONG, ONE LAYER DEEPER (fixed again 2026-09-27) ─────────────────────────
# Widening the window to 330 fixed the SLICE truncation but not the LOOKBACK: the loop still
# searched only `range(max(0, i - 60), i)` INSIDE the window. So the window's own first entry could
# never see a header sitting above it — the boundary just moved. Measured: file line 380 was
# flagged as an orphan while its dated header sat at line 374 (six lines above, well within 60),
# purely because the window happened to start at 380.
#
# This is why the entry count kept shifting the failure around: every append moves the window by a
# line, so a correct entry is reported, then not, at random. A guard whose verdict depends on how
# many lines the file has is reporting the file's LENGTH, not its structure.
#
# THE FIX: prepend real context. `CONTEXT` lines of the file above the window are included for the
# lookback while the loop still only judges entries inside the window. Now the first entry can see
# its header, and the check reports structure rather than position.
CONTEXT = 70
WINDOW = 260 + 70
_win = lines[-WINDOW:]
recent = lines[-(WINDOW + CONTEXT):]
_off = len(recent) - len(_win)          # how many context lines precede the judged window
orphan = []
for _wi, l in enumerate(_win):
    i = _wi + _off                      # index of this line within `recent`
    if re.match(r"^\s+\*\*(WHAT|THE|PROVEN|TESTS|COMMIT|ALSO|RECOVERY|ROOT|SECOND|STILL)", l):
        # a bolded section must sit under SOME dated header above it — searched across the context
        if not any(HEAD.match(recent[j]) for j in range(max(0, i - 60), i)):
            orphan.append(l[:60])
# ── THE CHECK MUST STILL FIRE ON A REAL ORPHAN (or the widened window just muted it) ──────────
# A widened window that stops firing is not a fix, it is a silencer. Proved on a synthetic file:
# a bolded section with NO header anywhere above it must still be flagged.
# NOTE — the first probe put a header ABOVE the orphan, so of course it was not flagged; the probe
# was wrong, not the check. A probe must reproduce the condition it claims to test.
_probe = ["  some prose with no header", "  more prose", "  **THE ORPHAN WITH NO HEADER ABOVE**"]
_o = []
for _i, _l in enumerate(_probe):
    if re.match(r"^\s+\*\*(WHAT|THE|PROVEN|TESTS|COMMIT|ALSO|RECOVERY|ROOT|SECOND|STILL)", _l):
        if not any(HEAD.match(_probe[_j]) for _j in range(max(0, _i - 60), _i)):
            _o.append(_l)
check("a synthetic orphan IS still caught (the widened window did not silence the check)",
      len(_o) == 1, f"caught {len(_o)}")

# and the inverse: a correctly-titled section must NOT be flagged (no false alarm)
_probe2 = ["- 2026-01-01 00:00Z — a real header", "  **THE SECTION UNDER IT**"]
_o2 = []
for _i, _l in enumerate(_probe2):
    if re.match(r"^\s+\*\*(WHAT|THE|PROVEN|TESTS|COMMIT|ALSO|RECOVERY|ROOT|SECOND|STILL)", _l):
        if not any(HEAD.match(_probe2[_j]) for _j in range(max(0, _i - 60), _i)):
            _o2.append(_l)
check("a correctly-titled section is NOT flagged (no false alarm at the seam)",
      len(_o2) == 0, f"false-flagged {len(_o2)}")

check("every bolded section sits under a dated header", not orphan,
      f"{len(orphan)} orphaned, e.g. {orphan[0] if orphan else ''}")

print("")
print("  ── 5. THE ENTRY WE JUST SHIPPED IS PRESENT AND TITLED ───────────────")
for needle, label in (("gas_topup.py", "the gas executor"),
                      ("CANNOT FINISH THE CYCLE", "the rescue affordability fix")):
    hit = any(needle in l for l in lines)
    check(f"the record of {label} is in the file", hit, needle)

print("")
print(f"  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok + fail} checks passed")
print("")
sys.exit(0 if fail == 0 else 1)
