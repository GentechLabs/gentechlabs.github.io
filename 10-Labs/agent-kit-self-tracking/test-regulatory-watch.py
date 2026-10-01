#!/usr/bin/env python3
"""test-regulatory-watch.py — pins the three defects found in this watcher on 2026-09-21.

A test that cannot fail is not a test. Each check below is written to FAIL on the old
code and PASS on the new, and the old behaviour is asserted too (see the negative
controls) so a future edit that reintroduces a bug trips it.

Run:  python3 test-regulatory-watch.py
Exit: 0 all pass · 1 a check failed
"""
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FAILED = []


def code_only(path):
    """Source with full-line comments stripped.

    A static assertion like `"f\"{today}:{frag}\"" not in src` fires on the explanatory
    COMMENT that says the bug is fixed, not on the bug. Measured here: this test failed
    on its first run for exactly that reason. Strip comments before asserting on source.
    """
    return "\n".join(
        ln for ln in open(path).read().split("\n") if not ln.lstrip().startswith("#")
    )


def src_prose(text):
    """Source with Python string-literal line breaks rejoined, then whitespace collapsed.

    WHY (found 2026-09-23): several checks assert on a SENTENCE that lives in the source
    as adjacent string literals spanning two lines, e.g.

        "... It is an exemption, "
        "not a rule."

    A literal `"it is an exemption, not a rule" in src` therefore FAILS on source that is
    entirely correct — the phrase is split by `",\n            "`. That is the same
    false-value family this treasury keeps catching, one level up: a check that cannot
    recognise a PASS is exactly as unreadable as one that cannot fail. It was failing
    silently on the shipped file (reproduced against the pre-fix copies) because the
    correct text was RE-WRAPPED when THE TEXT was corrected on 2026-09-22.
    """
    t = re.sub(r'"\s*\n\s*"', "", text)   # rejoin split string literals
    t = re.sub(r"\s+", " ", t)              # collapse all whitespace
    return t


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
    return ok


def check_true(label, got):
    return check(label, bool(got), True)


def check_false(label, got):
    return check(label, bool(got), False)


print("=" * 78)
print("  SEC/CFTC RULEMAKING WATCH — regression tests")
print("=" * 78)

print("\n── DEFECT 1: relevance filter missed the British spelling ──")
w = load(os.path.join(HERE, "sec-cftc-watch.py"), "scw")
# Positive controls: it must still catch what it always caught.
check_true("catches US 'Tokenized NMS Stock'", w.REL_RE.search("Tokenized NMS Stock"))
check_true("catches 'Regulation Crypto Assets'", w.REL_RE.search("Regulation Crypto Assets"))
check_true("catches 'stablecoin'", w.REL_RE.search("stablecoin reserve requirements"))
check_true("catches 'digital asset'", w.REL_RE.search("digital asset custody"))
# The bug: these were FALSE before the fix.
check_true("catches UK 'Tokenised NMS Stock'", w.REL_RE.search("Tokenised NMS Stock"))
check_true("catches 'tokenisation'", w.REL_RE.search("tokenisation of fund units"))
# Negative controls: the filter must still be able to say NO. (Sep 19 note: 'de' + 'fi'
# matched 'definition' — a filter that cannot refuse is not a filter.)
check_false("still DROPS proxy plumbing", w.REL_RE.search("Proxy Solicitation Modernization"))
check_false("still DROPS shareholder proposals", w.REL_RE.search("Shareholder Proposals"))
check_false("no 'definition' false positive", w.REL_RE.search("the definition of a security"))
# And no duplicate patterns (the copy-paste tell).
src = code_only(os.path.join(HERE, "sec-cftc-watch.py"))
check("no duplicated 'digital assets' pattern", src.count(r'r"\bdigital assets?\b"'), 1)

print("\n── DEFECT 7: the filter keyed on ASSETS and could not see VENUES ──")
# THE BUG (found 2026-09-23). The relevance filter matched ASSET vocabulary only, so an
# item was visible only if it NAMED the asset. Three crypto-native exchanges filed SRO
# rule changes that published that morning — Coinbase Derivatives (SR-COIN-2026-002,
# perpetual single-stock futures), Bitnomial (SR-BTNL-2026-001), KalshiEX
# (SR-KALSHIEX-2026-02) — and ALL THREE were dropped silently, because "Coinbase
# Derivatives" carries no crypto vocabulary. Confirmed absent from the watermark file too.
# Positive controls — the three real filings, quoted from their Federal Register titles.
check_true("catches Coinbase Derivatives (perpetual single-stock futures)",
           w.REL_RE.search("Self-Regulatory Organizations; Coinbase Derivatives, LLC; "
                           "Notice of Filing and Immediate Effectiveness of a Proposed Rule "
                           "Change Relating to the Adoption of Coinbase Derivatives, LLC's "
                           "Rules Governing Cash Settled Futures on Individual Equity "
                           "Securities Including Perpetual Single-Stock Futures"))
check_true("catches KalshiEX security futures listing standards",
           w.REL_RE.search("Self-Regulatory Organizations; KalshiEX LLC; Notice of Filing "
                           "and Immediate Effectiveness of a Proposed Rule Change Relating "
                           "to Listing Standards for Security Futures Products"))
check_true("catches Bitnomial security futures listing standards",
           w.REL_RE.search("Self-Regulatory Organizations; Bitnomial Exchange, LLC; Notice "
                           "of a Filing of a Proposed Rule Change Relating to Security "
                           "Futures Product Listing Standards, Customer Margin and Related Rules"))
check_true("catches the CFTC event-contracts proposal",
           w.REL_RE.search("Data Reporting Requirements for Certain Event Contracts"))
check_true("catches a prediction-markets proposal",
           w.REL_RE.search("Prediction Markets; Public Interest Determinations"))
check_true("catches MEMX securities event contracts",
           w.REL_RE.search("Self-Regulatory Organizations; MEMX LLC; Notice of Filing of a "
                           "Proposal To Adopt Rules for the Listing and Trading of "
                           "Securities Event Contracts on the Exchange"))
# Negative controls — the filter must STILL say no, or the patch just floods the feed.
# This is the half that makes the fix a filter rather than a firehose.
check_false("still DROPS a Cboe fee-schedule SRO notice",
            w.REL_RE.search("Self-Regulatory Organizations; Cboe BZX Exchange, Inc.; Notice "
                            "of Filing and Immediate Effectiveness of a Proposed Rule Change "
                            "To Amend Rule 11.15(a) To Clarify the Handling of Orders"))
check_false("still DROPS FINRA housekeeping",
            w.REL_RE.search("Self-Regulatory Organizations; Financial Industry Regulatory "
                            "Authority, Inc.; Notice of Filing and Immediate Effectiveness "
                            "of a Proposed Rule Change To Modify the Clearly Erroneous Policy"))
check_false("still DROPS a mutual-fund trust notice",
            w.REL_RE.search("Northern Lights Fund Trust and Ocean Park Asset Management, LLC"))
# Routine paperwork: the FILTER does match the product name; relevant() is the layer that
# refuses it, and it does so to match comment_deadlines()' own long-standing policy. Assert
# the layer that actually makes the decision, or the check tests the wrong function.
check_false("still DROPS routine information-collection paperwork",
            w.relevant({"title": "Agency Information Collection Activities: Notice of Intent "
                                 "To Extend Collection 3038-0059: Part 41, Relating to "
                                 "Security Futures Products", "abstract": ""}))
check_false("still DROPS a bare paperwork notice",
            w.relevant({"title": "Agency Information Collection Activities: Notice of Intent "
                                 "To Extend", "abstract": ""}))
check_false("no 'derivatives' firehose (interest-rate swap determin)",
            w.REL_RE.search("Clearing Requirement Determination Under Section 2(h) for "
                            "Interest Rate Swaps To Account for CAD and MXN Benchmark Transition"))

print("\n── DEFECT 2: open comment windows were silently truncated at 8 ──")
check_true("deadline loop no longer caps at [:8]", "deadlines[:8]" not in src)
check_true("deadline header states the true total", "open window(s) total" in src)
# Verify the count we actually have today is fully printable.
try:
    ds = w.comment_deadlines()
    print(f"          (live: {len(ds)} open windows, all of which now print)")
    check_true("live window list is non-empty", len(ds) > 0)
except Exception as e:
    print(f"          NETWORK — could not re-read live windows here: {e}")
    print("          (the static check above still proves the cap is gone)")
check_true("truncation is now disclosed for item lists", "showing {a.max} of {len(hot)}" in src)

print("\n── DEFECT 4: a failed comment-window fetch deleted an agency silently ──")
# THE BUG (found 2026-09-22): comment_deadlines() did `except Exception: continue` per
# agency, so a dead SEC comment-date query removed every SEC window — Regulation Crypto
# Assets among them — and printed a shorter, clean list with NO failure line. Measured
# by killing only the SEC query: 6 windows vanished, output said nothing.
check_true("a fetch error is recorded, not swallowed", "failures.append(" in src)
check_true("comment_deadlines returns the failures it saw",
           "out.failures = tuple(failures)" in src)
check_true("caller surfaces an incomplete window list",
           "COMMENT-WINDOW INCOMPLETE" in src)
check_true("no bare 'except: deadlines = []' swallow remains",
           "except Exception:\n        deadlines = []" not in src)
check_true("empty window list distinguishes 'none open' from 'failed to fetch'",
           "none open in the next 60 days" in src)
check_true("'all shown' is not asserted over a partial fetch",
           'if deadline_failures:\n            print(f"   ── {len(deadlines)} window(s) shown'
           in src or "INCOMPLETE, see warning above" in src)
# The end-to-end proof: kill ONLY the SEC comment query and require a failure line.
try:
    import copy as _copy
    _real = w.fetch
    def _broken(url, timeout=40):
        if "comment_date" in url and "securities-and-exchange-commission" in url:
            raise OSError("simulated SEC comment-date outage")
        return _real(url, timeout=timeout)
    w.fetch = _broken
    _dl = w.comment_deadlines()
    check("failures are attached to the returned list", len(list(_dl.failures)), 1)
    check_true("the failed agency is named", "SEC" in _dl.failures[0])
    check_true("CFTC windows still came through", len(_dl) > 0)
    check_true("no SEC window survived the SEC outage",
               all(d["agency"] != "SEC" for d in _dl))
    w.fetch = _real
except Exception as e:
    print(f"          NETWORK — could not exercise the outage path: {e}")

print("\n── DEFECT 5: a nothing-new day suppressed the live deadline ──")
# THE BUG (found 2026-09-22): `if not show and not errors: return 0` returned BEFORE the
# comment-window pass, so the Chair's live carry-forward deadline (Regulation Crypto
# Assets, closes 2026-10-20) was deleted from the delivered message on any quiet day.
# NOTE: this asserts on CODE, not on a comment. The first draft of this check looked for
# the explanatory comment — and `code_only()` strips comments, so it FAILED on the fixed
# file. Same false-positive trap this treasury already has on record (a test firing on the
# prose describing the fix). Proved by running it: it failed here before being corrected.
_anchor = src.find("if not show and not errors:")
check_true("the early-return branch exists", _anchor != -1)
if _anchor != -1:
    _ret = src.find("return 0", _anchor)
    _probe = src.find("_probe = comment_deadlines()", _anchor)
    check_true("the comment clocks are checked BEFORE the silent return",
               _probe != -1 and _ret != -1 and _probe < _ret)
check_true("a quiet day with an open window still reports",
           "NO NEW PUBLICATIONS" in src)
check_true("a quiet day with NO window and NO failure still stays silent",
           "if not _probe and not _pfail:" in src)

print("\n── DEFECT 6: THE TEXT contained a legal mechanism that does not exist ──")
# THE BUG (found 2026-09-22). regulatory-benefit.py's 2026-90 "text" field — the one declared
# to be quotable FACT — read "conditional and self-certified". Verified against the primary
# document (Release No. 34-106402 / File No. 4-927, Federal Register 2026-19388), the SEC press
# release, and the Chairman's statement: "self-certified" occurs 0 times in all three. It IS a
# real term of art (356 FR hits) but belongs to SRO filings effective on filing, not to this
# order. The order's actual mechanism is a 30-days-prior public Notice + 1-business-day email
# to the Commission. A fabricated mechanism in the FACT field is worse than a missing one.
_rb = code_only(os.path.join(HERE, "regulatory-benefit.py"))
check_true("no fabricated 'self-certified' claim remains",
           "self-certified" not in _rb)
check_true("the real 5-year term and end date are stated",
           "2031-09-17" in _rb)
check_true("the real Notice mechanism is stated (30 days prior)",
           "30 days before operating" in _rb)
check_true("the pool smart-contract disclosure is stated",
           "smart contract addresses" in _rb)
check_true("release/file number cited so the claim is checkable",
           "34-106402" in _rb and "4-927" in _rb)
_rb_prose = src_prose(_rb).lower()
check_true("still labelled an exemption, not a rule",
           "it is an exemption, not a rule" in _rb_prose)

print("\n── DEFECT 3: the Sunday note re-appended identical reads ──")
b = load(os.path.join(HERE, "regulatory-benefit.py"), "rb")
# The old key was f"{today}:{frag}" — date-keyed, so a new day re-appended static reads.
b_src = code_only(os.path.join(HERE, "regulatory-benefit.py"))
check_true("dedupe key is no longer date-prefixed", 'f"{today}:{frag}"' not in b_src)
check_true("dedupe now uses a content fingerprint", "read_fingerprint(r)" in b_src)
# A fingerprint must be STABLE across a ticking countdown...
# Guarded: on pre-fix code read_fingerprint does not exist, and a traceback is a worse
# test result than a named FAIL. Verified by running this file against the pre-fix copies.
if not hasattr(b, "read_fingerprint"):
    check_true("read_fingerprint exists", False)
else:
    r = {"text": "comments close 2026-10-20 (29 days out).",
         "chair": {"DECISION": "decide, 29 days out."}}
    r2 = {"text": "comments close 2026-10-20 (28 days out).",
          "chair": {"DECISION": "decide, 28 days out."}}
    check("fingerprint stable as countdown ticks", b.read_fingerprint(r), b.read_fingerprint(r2))
    # ...but must CHANGE when the verdict changes.
    r3 = {"text": r["text"], "chair": {"DECISION": "DIFFERENT VERDICT"}}
    check_true("fingerprint changes on a new verdict",
               b.read_fingerprint(r) != b.read_fingerprint(r3))
    fp_again = "".join(b.read_fingerprint(r).split())
    check_true("fingerprint is a hex digest", re.fullmatch(r"[0-9a-f]{16}", fp_again) is not None)

# End-to-end: append twice into a temp note; the second must add NOTHING.
print("\n── DEFECT 3 (end-to-end): append is idempotent per content ──")
tmpd = tempfile.mkdtemp(prefix="regwatch-test-")
b.NOTE = os.path.join(tmpd, "note.md")
b.STATE = os.path.join(tmpd, "state.json")
first = b.append_note(["2026-90", "9300-26", "2026-17183"])
second = b.append_note(["2026-90", "9300-26", "2026-17183"])
check("first append writes all three", sorted(first), ["2026-17183", "2026-90", "9300-26"])
check("second append writes nothing", second, [])
note = open(b.NOTE).read()
check("no duplicated section headers", note.count("## 2026-"), 0 + 3)  # 3 content sections
check("Carry to Sunday written exactly once", note.count("### Carry to Sunday"), 1)
# Simulate the NEXT DAY (the exact shape of the live bug): same static list, new date.
import datetime as _dt
_real = _dt.datetime


class _Tomorrow(_real):
    @classmethod
    def now(cls, tz=None):
        return _real.now(tz) + _dt.timedelta(days=1)


b.datetime = _Tomorrow
third = b.append_note(["2026-90", "9300-26", "2026-17183"])
check("TOMORROW does not re-append unchanged reads", third, [])
# RESTORE the clock. Leaving the module frozen one day in the future made the freshness
# guard further down see its own fixture as stale, so DEFECT 8 measured this monkeypatch
# instead of the coverage logic.
b.datetime = _real
check("still exactly 3 sections after a day rollover", open(b.NOTE).read().count("## 2026-"), 3)
check("still exactly 1 Carry block after a day rollover",
      open(b.NOTE).read().count("### Carry to Sunday"), 1)

print("\n── DEFECT 8: the Chair read a FIXED board and never said what it had NOT read ──")
# THE BUG (found 2026-09-24). Pass 1 discovers a CHANGING set of relevance-flagged items;
# pass 2 rendered a FIXED three-item board (its own READS dict) and printed it as though it
# were the complete read. Measured on the live board that day: pass 1 flagged FIVE items
# (SEC 2026-19512 Coinbase Derivatives security-futures customer margin; 2026-19407/8/9 the
# three crypto-venue SRO filings; 2026-19215 Nadex's Section 6(g) registration) and pass 2
# said nothing about any of them. It has three reads and no coverage check. An item with no
# read gets NO verdict — and "does not reach us" is only a verdict when it is WRITTEN.
_w_src = code_only(os.path.join(HERE, "sec-cftc-watch.py"))
_rb_src = code_only(os.path.join(HERE, "regulatory-benefit.py"))
check_true("pass 1 records the flagged list for pass 2", "record_hot(st, hot)" in _w_src)
check_true("pass 1 clears the list on a nothing-new run", _w_src.count("record_hot(st, [])") == 2)
check_true("pass 2 has a coverage function", "def uncovered(" in _rb_src)
check_true("pass 2 reads pass 1's state", "WATCH_STATE" in _rb_src)
check_true("the coverage line is actually rendered", "UNCOVERED CHECK" in _rb_src)
# The OTHER half: a read written but never requested reaches nobody, and no debt line
# would ever mention it — the half a READS-keyed coverage check structurally cannot see.
check_true("pass 2 has the orphan check", "def board_integrity(" in _rb_src)
check_true("the orphan line is actually rendered", "NEVER RENDERED" in _rb_src)
# The budget must refuse to grow without limit, and must NAME what it drops rather than
# trimming silently. Silent trimming is how the 2026-09-22 DECISION line was lost.
check_true("the Chair block is rendered under a budget", "CHAIR_BUDGET_BYTES" in _rb_src)
check_true("what does not fit is NAMED, not silently trimmed", "DID NOT FIT" in _rb_src)
# The two negative controls that matter most: a MISSING key and a STALE list must NOT
# collapse to the clean pass. [] would render as "every item has a read" — a false PASS
# is worse than no check, because it is the reassuring answer.
check_true("missing key cannot read as 'all covered'", '"last_hot" not in raw' in _rb_src)
check_true("stale list cannot read as 'all covered'", "max_age_seconds" in _rb_src)
check_true("unreadable state renders as UNVERIFIED, not clean",
           "UNAVAILABLE" in _rb_src and "UNVERIFIED" in _rb_src)
# ── THE FALSE "ALREADY NOTED TODAY" (found 2026-09-28) ───────────────────────────────────
# The closing line printed "(already noted today — idempotent)" whenever `added` was empty —
# but `added` is empty BOTH when every read is already on the note AND when nothing has ever
# been noted. On a quiet day the note had not been touched for three days while the message
# told the reader it was current. Assert the false string is GONE and that the honest
# replacement keys on the note itself, not on the emptiness of `added`.
check_true("the false 'already noted today' string is gone",
           "already noted today" not in _rb_src)
check_true("the append line reports the note's real newest section",
           "newest note section" in _rb_src)
check_true("...and it reads that date from the NOTE, not from `added`",
           'startswith("## ")' in _rb_src)
# The wrapper must RUN the facts pass first (so pass 2 reads THIS run) while still
# PRINTING the Chair first (so truncation cannot delete the decision surface).
_wsrc = open(os.path.join(HERE, "sec-cftc-watch.sh")).read()
# Guarded anchors: on pre-fix source these strings do not exist, and a ValueError
# traceback is a WORSE test result than a named FAIL — verified by running this file
# against the pre-fix copies, where an unguarded index() aborted the suite mid-way.
def _idx(hay, needle):
    try:
        return hay.index(needle)
    except ValueError:
        return None


_bf = _idx(_wsrc, 'python3 "$D/sec-cftc-watch.py" >')
_bc = _idx(_wsrc, 'python3 "$D/regulatory-benefit.py"')
check_true("wrapper buffers pass 1 before pass 2 runs",
           _bf is not None and _bc is not None and _bf < _bc)
# Anchor on the ECHO LINES, not on the explanatory header comment: the phrase
# "THE CHAIR'S READ" appears twice in the wrapper (prose and code), and index() returns
# the prose — so the first version of this check asserted on a comment. A check that
# measures prose instead of behaviour is the same unreadable shape as one that cannot fail.
_echo_chair = _idx(_wsrc, 'echo "━━━ THE CHAIR\'S READ')
_echo_facts = _idx(_wsrc, 'echo "━━━ WHAT PUBLISHED')
check_true("wrapper still EMITS the Chair\'s read first",
           _echo_chair is not None and _echo_facts is not None and _echo_chair < _echo_facts)
# ...but EXECUTES the facts pass first, so the coverage check reads THIS run's flags.
check_true("wrapper RUNS the facts pass before the Chair pass", _bf is not None and _bc is not None and _bf < _bc)
# End-to-end on the real functions, with a synthetic flagged list containing an item that
# has NO read and one that does.
if hasattr(b, "uncovered"):
    _tmp2 = tempfile.mkdtemp(prefix="regwatch-cover-")
    _st = os.path.join(_tmp2, "watch-state.json")
    _now = _dt.datetime.now(_dt.timezone.utc).isoformat()
    json.dump({"last_hot": [
        {"id": "fr:2026-19512", "agency": "SEC", "type": "Notice",
         "date": "2026-09-24", "title": "Coinbase Derivatives customer margin"},
        {"id": "fr:2026-17183", "agency": "SEC", "type": "Proposed Rule",
         "date": "2026-08-21", "title": "Regulation Crypto Assets"},
    ], "last_hot_run": _now}, open(_st, "w"))
    # Pass the board EXPLICITLY: with board=None the function falls back to
    # RENDERED_BOARD, which is empty outside main(), and the conservative answer then is
    # "everything is owed". (Verified: the first version of this fixture asserted
    # ['19512'] and got both items back — correct behaviour, wrong fixture.)
    _d = b.uncovered(state_path=_st, board=["2026-17183"])
    check("finds the item with no read and not the one with a read",
          [i["id"] for i in _d], ["fr:2026-19512"])
    # With board=None the question is Q1 "does a read EXIST?" — and both of these HAVE a
    # read in READS (19512 is the fixture's own id and 17183 is a real read), so nothing is
    # owed. The false-pass route is caught by board_integrity() instead, below.
    check("board=None asks 'does a read exist', and both do",
          [i["id"] for i in b.uncovered(state_path=_st)], [])
    _d2 = b.uncovered(state_path=_st, board=["2026-17183", "2026-19512"])
    check("reports nothing once every flagged item has a read", _d2, [])
    # MISSING KEY -> None (unknown), NOT [] ("all covered").
    _st2 = os.path.join(_tmp2, "empty.json")
    json.dump({"seen": []}, open(_st2, "w"))
    check("missing key is UNKNOWN, not 'all covered'", b.uncovered(state_path=_st2), None)
    # STALE list -> None, so we never judge a run that is not this one.
    _st3 = os.path.join(_tmp2, "stale.json")
    _old = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=1)).isoformat()
    json.dump({"last_hot": [{"id": "fr:2026-1"}], "last_hot_run": _old}, open(_st3, "w"))
    check("stale list is UNKNOWN, not 'all covered'", b.uncovered(state_path=_st3), None)
    # An absent file -> None as well.
    check("unreadable state is UNKNOWN, not 'all covered'",
          b.uncovered(state_path=os.path.join(_tmp2, "nope.json")), None)
    # ── THE TWO FALSE-PASS ROUTES, both closed ────────────────────────────────────────
    # An item counts as covered only if it was ASKED FOR and HAS a read. Either half alone
    # would report a clean pass while nothing about the item was printed. Measured while
    # writing this: keying on the READS dict flipped the line from "5 owed" to a clean pass
    # with 5 items still unrendered.
    _saved_reads = dict(b.READS)
    _saved_board = list(b.REQUESTED_BOARD)
    _one = [{"id": "fr:2026-19512", "agency": "SEC", "type": "Notice",
             "date": "2026-09-24", "title": "CDE customer margin"}]
    # ── THE FIXTURE IS SCOPED, AND THIS FIX IS THE POINT (found 2026-09-28) ───────────
    # These three cases assert on board_integrity()/uncovered(), which both read the
    # module-level READS dict. The original fixture ASSUMED that dict held exactly the two
    # keys it manipulates, so it silently became a test of the SIZE of production READS:
    # the moment reads were added for 2026-19512/19215 (2026-09-24) and 2026-90/9300-26
    # were already there, every other read in the dict was returned as an extra "orphan"
    # and two checks went red — on correct code, for unrelated work. Measured: this suite
    # printed 2 FAILED on the live file, and had been red since 2026-09-24 while nothing
    # gated on it. A test whose verdict depends on how much unrelated data has accumulated
    # is the same false-value shape this treasury keeps catching: a check that cannot
    # recognise a PASS is as unreadable as one that cannot fail.
    # Fix: give the fixture its OWN two-entry READS dict, so the assertion is about the
    # LOGIC (asked-for vs has-a-read) and not about whatever the board happens to contain.
    b.READS.clear()
    b.READS.update({"2026-17183": {"text": "x", "chair": {}},
                    "2026-19512": {"text": "x", "chair": {}}})
    # (a) a read exists but was NEVER REQUESTED -> an ORPHAN, caught by board_integrity.
    # It is NOT a coverage debt (a read exists) but it reaches nobody, and without this
    # check nothing at all would mention it.
    b.REQUESTED_BOARD[:] = ["2026-17183"]
    check("read exists but was never requested -> ORPHAN",
          b.board_integrity(), ["2026-19512"])
    check("...and it is NOT reported as a coverage debt",
          [i["id"] for i in b.uncovered(hot=_one)], [])
    # (b) on the board but has NO read -> still owed (render() would skip it silently).
    b.REQUESTED_BOARD[:] = ["2026-17183", "2026-19512"]
    del b.READS["2026-19512"]
    check("on the board but has NO read -> still owed",
          [i["id"] for i in b.uncovered(hot=_one)], ["fr:2026-19512"])
    check("...and with no read it is NOT an orphan (it is a debt)",
          b.board_integrity(), [])
    # (c) both halves present -> genuinely covered and not an orphan.
    b.READS["2026-19512"] = {"text": "x", "chair": {}}
    b.REQUESTED_BOARD[:] = ["2026-17183", "2026-19512"]
    check("on the board AND has a read -> covered",
          [i["id"] for i in b.uncovered(hot=_one)], [])
    check("...and not an orphan", b.board_integrity(), [])
    # RESTORED EXACTLY. A fixture that leaks into the next check is how the assertion above
    # stayed wrong for four days without anyone being told why.
    b.READS.clear(); b.READS.update(_saved_reads)
    b.REQUESTED_BOARD[:] = _saved_board
    check("fixture restored production READS exactly",
          sorted(b.READS.keys()), sorted(_saved_reads.keys()))
else:
    check_true("pass 2 exposes uncovered()", False)

print("\n" + "=" * 78)
if FAILED:
    print(f"  ❌ {len(FAILED)} CHECK(S) FAILED:")
    for f in FAILED:
        print(f"     - {f}")
    print("=" * 78)
    sys.exit(1)
print("  ✅ ALL CHECKS PASSED")
print("=" * 78)
sys.exit(0)
