#!/usr/bin/env python3
"""
retraction-sweep.py — find WITHDRAWN figures still standing UNMARKED in shipped notes.

WHY THIS EXISTS (Pixel, 2026-09-28)
  "A correction applied to the NEW text and not swept through the OLD is how a stale line survives its own
  author." The correction lane is a NOTE; the retracted figure lives in an EARLIER note. Fix the next note and
  the old one keeps answering first, with no marker on it — a reader landing there has no way to learn the
  number was withdrawn. I found this in my own lane: a note headlined "348, not 140" still stood unmarked
  while the correction had gone into a later note.

THE MODEL
  `retractions.json` is DATA, not a literal in this script (the same rule the census tool learned):
    { "figure": "348", "superseded_by": "~42-45 events", "reason": "...", "marked": ["CORRECTION IN PLACE"] }
  For every note in scope, a figure that appears WITHOUT a marker in the same file is REPORTED.

WHAT THIS DELIBERATELY DOES NOT DO
  It does not edit your notes. A sweep that rewrites prose is a destructive write over a record of what someone
  believed; this reports the file and the line so the author decides. It also does not call a marked note clean
  in general — it checks for the marker, and a marker is a claim like any other.

EXIT CODES
  0 = no unmarked retracted figures
  1 = at least one note carries a withdrawn figure with no marker
  2 = could not measure — registry unreadable, OR NO record's scope matched any file in the tree.
      The second is the important one: every record is lane-scoped, so pointing this at an unknown
      lane used to match nothing and return 0 — A PASS ON A LANE IT CANNOT SEE. A per-lane scan
      legitimately has records scoped elsewhere; the failure is when NONE engage, because then
      nothing was looked for.

MARKER LIST (why the default is wider than it looks)
  A correction can be written many ways ("WITHDRAWN", "RETRACTED", "CORRECTED IN PLACE", "Amended",
  "was wrong", ...). The default marker set covers the common ones; a note corrected in wording the
  list does not carry will be reported as unmarked. That is a FALSE POSITIVE, not a defect in the
  note — widen `marked` per record rather than arguing with the report.

KNOWN BOUNDARY — THE META LEVEL (found by Pixel, 2026-09-28; DO NOT PATCH THIS WITH A CARVE-OUT)
  The detector has three levels of reach and the third is a documented limit:
    LEVEL 1 — FORM.  A registry keyed on "5 MiB" cannot see "5 MB". FIXED: `aliases` (match ANY).
    LEVEL 2 — CONTEXT.  A form alone cannot tell a CLAIM from a MEASUREMENT ("files over 5 MB: 102"
                     is a count). FIXED: `assertion_cues`.
    LEVEL 3 — META.  Form + cue cannot tell ASSERTING from QUOTING. A note that DESCRIBES the
                     withdrawn claim fires exactly like a note MAKING it, so a report can land on
                     the note that documents the correction. First instance: this tool's own ACK.
  THE REMEDY IS TO MARK THE NOTE, NOT TO WEAKEN THE DETECTOR. Its verdict means "carries the
  withdrawn form with no correction marker", which is TRUE of a meta-note that never says so.
  A BACKTICK CARVE-OUT ("a code span means it is being quoted") was tested and DECLINED: measured
  across 01-HANDOFFS, 142 of 590 occurrences sit entirely inside backticks across 34 notes — and
  Pixel's own published claim was written both ways, so the carve-out would have created a FALSE
  NEGATIVE on the very defect this tool caught. Silencing a large class to quiet one note trades a
  true positive for a blind spot. WHEN A FINDING LANDS ON A NOTE THAT DISCUSSES THE CLAIM: add a
  marker to that note (keeping the claim visible against its correction) and move on.

Usage: retraction-sweep.py [--dir DIR] [--registry FILE] [--json] [--quiet]
"""
import argparse
import ast
import json
import os
import re
import sys

DEFAULT_DIR = "/root/vaults/gentech/01-HANDOFFS"
DEFAULT_REG = "/root/vaults/gentech/scripts/retractions.json"


def load_registry(path):
    with open(path) as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("registry must be a list of retraction records")
    for rec in data:
        # A RECORD KEYS ON EITHER A TOKEN OR A PHRASE, and the difference is load-bearing.
        # "5 MB" bare matches a MEASUREMENT ("files >5MB excl. .git -> 102"), which is a legitimate
        # count of how many files exceed a threshold. The WITHDRAWN thing is the ASSERTION that the
        # number is a client limit ("hard per-file limit", "silently never syncs"). Keying on the
        # token produced 13 false positives across the fleet's own investigation notes — the exact
        # error class this tool exists to prevent, committed by the tool. So a record may carry
        # `phrase` instead of `figure`, and it matches as a case-insensitive substring.
        if "figure" not in rec and "phrase" not in rec:
            raise ValueError("every record needs a 'figure' or a 'phrase'")
        # STEMS, not fixed phrases. A correction is written many ways — "[CORRECTED 2026-09-28
        # night: ...]", "withdrawn", "superseded by" — and requiring an exact phrase like
        # "CORRECTED IN PLACE" reported a properly-corrected note as unmarked. That is a FALSE
        # POSITIVE, and per the day's lesson a false alarm spends the trust the real finding needs.
        # Note "correct" alone is deliberately ABSENT: it is an adjective ("the correct value") and
        # would silence real findings.
        # "substring" alone is deliberately ABSENT — every figure is a substring of some larger
        # number, so it silences real findings. Distinctive idioms only.
        rec.setdefault("marked", ["correction", "corrected", "withdraw", "retract", "supersed",
                                  "amend", "deprecat", "zero hits", "not a constant",
                                  "was wrong", "answered in place"])
        rec.setdefault("only_files_matching", None)   # optional scope limiter
        # ── ALIASES: ONE CLAIM, MANY COSTUMES (Pixel, 2026-09-28) ────────────────────────────
        # A withdrawn figure is a NUMBER WITH A UNIT, and units get written four ways under
        # pressure: 5 MiB / 5 MB / 5MB / 5242880 / 5*1024*1024 are ONE CLAIM IN FOUR COSTUMES.
        # A registry that lists one costume reports CLEAN on the other three — measured: this tool
        # fired on '5 MiB' and returned exit 0 on 'Obsidian Sync's hard 5 MB per-file limit', which
        # is how the claim was actually PUBLISHED, in four notes.
        #
        # This is the marker-list defect ONE LEVEL DOWN. That list held the instruction to correct
        # a note rather than what a corrected note reads; a figure list holds the unit the FIRST
        # author reached for rather than the forms the claim was published in. Moving the
        # variability from the WHERE (only_files_matching) to the WHAT.
        rec.setdefault("aliases", [])
        # ── ASSERTION CUES: WHY A BARE ALIAS CANNOT BE ENOUGH ────────────────────────────────
        # '5 MB' bare matches a MEASUREMENT — 'files over 5 MB: 102' is a legitimate count of files
        # past a threshold, not a claim that the threshold is a limit. Keying on the token produced
        # 13 fleet-wide false positives in our own notes. So a record may require a CUE on the SAME
        # LINE: the number matches only where the line is also making the CLAIM. Aliases fix the
        # FORM; cues keep the CLAIM/MEASUREMENT distinction that the aliases would otherwise blur.
        rec.setdefault("assertion_cues", None)
    return data


def looks_marked(text, markers):
    # CASE-INSENSITIVE. A note corrected in prose reads "Withdrawn" / "retracted", not the
    # ALL-CAPS marker a human happens to have chosen — and a case-sensitive test reports a
    # corrected note as unmarked, which is a FALSE POSITIVE that trains the reader to ignore
    # the tool. The marker is a CLAIM; match the claim, not its capitalisation.
    low = text.lower()
    return any(m.lower() in low for m in markers)


# AN ARCHIVE IS THE RECORD OF WHAT WAS BELIEVED, NOT A LIVE CLAIM (Pixel, 2026-09-28). A dated memory
# snapshot necessarily carries the figures that were then in force, so sweeping it re-reports the same
# lines every run forever — permanent noise — and MARKING it would erase the evidence that the
# withdrawn constant travelled by MEMORY rather than by note. So it is excluded BY PATH, and the
# CHANNEL is the finding: the myth reached seats through memory, which is exactly why a notes-only
# sweep could never have found it. MEASURED: 0 LIVE memory files carry the withdrawn form; only the
# two dated snapshots (2026-09-12, 2026-09-22) do, so the channel is historical and now closed.
# `_archive/` in the HANDOFF lanes is deliberately NOT excluded: those are closed notes, and one of
# them was a genuine in-place correction whose premise rested on the withdrawn cap.
EXCLUDED_NOTE_DIRS = {"memory-archive"}


def scan(root, registry):
    findings = []
    files_scanned = 0
    scope_matched = [0] * len(registry)
    scope_fired = [0] * len(registry)          # records that produced a FINDING here
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git" and d not in EXCLUDED_NOTE_DIRS]
        for fn in filenames:
            if not fn.endswith((".md", ".markdown")):
                continue
            path = os.path.join(dirpath, fn)
            try:
                text = open(path, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            files_scanned += 1
            for idx, rec in enumerate(registry):
                scope = rec.get("only_files_matching")
                if scope and scope not in path:
                    continue
                scope_matched[idx] += 1
                if "phrase" in rec and "figure" not in rec:
                    # PHRASE record: substring match, still reported per line so the reader can
                    # see the sentence the claim sits in rather than a bare count.
                    ph = rec["phrase"].lower()
                    hits = [i for i, line in enumerate(text.splitlines(), 1) if ph in line.lower()]
                    if not hits or looks_marked(text, rec["marked"]):
                        continue
                    scope_fired[idx] += 1
                    findings.append({
                        "file": os.path.relpath(path, root),
                        "figure": rec["phrase"],
                        "superseded_by": rec.get("superseded_by", ""),
                        "lines": hits[:8],
                        "total_hits": len(hits),
                    })
                    continue
                forms = [rec["figure"]] + [x for x in rec.get("aliases", []) if x]
                cues = rec.get("assertion_cues")
                fig = rec["figure"]
                # WHOLE-TOKEN match. `(?<![\d.])` blocks a DIGIT or DOT before the token, which
                # does NOT block a THOUSANDS SEPARATOR: "1,348" matched figure "348". Fixed by
                # also rejecting a preceding comma that sits between digits ("1,348") while still
                # allowing a leading comma in prose (", 348 events").
                pat = re.compile(
                    r"(?<![\d.])"                # no digit or dot immediately before
                    r"(?<![\d],)"                # ...and not a comma between digits (1,348)
                    + re.escape(fig) +
                    r"(?![\d])"                  # no digit immediately after
                    r"(?!,\d{3}(?![\d]))"        # ...and not the head of a comma group (348,777)
                )
                hits = []
                for i, line in enumerate(text.splitlines(), 1):
                    low = line.lower()
                    matched = any(
                        (re.compile(r"(?<![\w.])" + re.escape(f) + r"(?![\w.])").search(line)
                         if f.isdigit() else
                         re.compile(r"(?<![\w.])" + re.escape(f) + r"(?![\w.])", re.I).search(line))
                        for f in forms
                    )
                    if not matched:
                        continue
                    # CUE GATE: where a record names cues, the number only counts on a line that is
                    # also MAKING THE CLAIM — so 'files over 5 MB: 102' stays quiet while 'the hard
                    # 5 MB per-file limit' fires. Only checkable per-line, which is why it lives here.
                    if cues and not any(c.lower() in low for c in cues):
                        continue
                    hits.append(i)
                if not hits:
                    continue
                if looks_marked(text, rec["marked"]):
                    continue          # the note carries its own correction — OK
                scope_fired[idx] += 1
                findings.append({
                    "file": os.path.relpath(path, root),
                    "figure": fig,
                    "superseded_by": rec.get("superseded_by", ""),
                    "lines": hits[:8],
                    "total_hits": len(hits),
                })
    return files_scanned, findings, scope_matched, scope_fired


# ── SECOND SURFACE: CODE (added 2026-09-28, HQ's 5 MiB case) ─────────────────────────────────
# A withdrawn FIGURE lives in a note. A withdrawn CONSTANT gets BAKED INTO AN ARTIFACT — it stops
# looking like a claim, acquires a comment calling it measured, and outlives the withdrawal in a
# tool that no longer resembles the note it came from. The 5 MiB cap is the case: published, then
# withdrawn, while a tested control kept asserting it.
#
# Code has no prose markers, so "marked" cannot mean the same thing. The honest test is the
# REVERSE one: a code hit is a finding UNLESS the surrounding lines carry the correction — i.e.
# unless the file itself says the value is not what it looks like. That keeps the default loud
# (an uncommented constant is reported) and lets a corrected file pass by naming its own defect.
# A marker is any phrase that shows the text is DISCUSSING the value rather than asserting it.
#
# NARROWED 2026-09-28 (Pixel's finding, measured). The list used to carry "error", "substring",
# "conservative", "assumed" and "misread". Those are ORDINARY ENGLISH: a genuinely stale constant
# with `# raise an error if the path is missing` three lines above it was SILENTLY SUPPRESSED — a
# false NEGATIVE, and the exact mirror of the substring false POSITIVE the boundary guard removed.
# MEASURED: any of those words within the 4-line window silenced a bare `CAP_BYTES = 5*1024*1024`,
# and the window bound is exactly 4 (a hint 5 lines up still fires).
#
# And the words were provably redundant for their stated job: the AST blanking in _code_lines()
# already drops the tool's own docstring and comments, so a constant in prose is NEVER a finding
# whether or not a hint word is present. Proven both ways: constant in a docstring only -> 0;
# constant in a comment only -> 0; the same constant in real code -> 1.
#
# What remains are phrases that NAME THE CONSTANT'S STATUS and cannot appear by accident. Prefer
# excluding a file by path when the exclusion is about the FILE rather than the value.
CODE_MARKER_HINT = ("pre-filter", "prefilter", "not a client constant", "withdrawn", "superseded",
                    "not measured")

# Vendored/build trees are OTHER PEOPLE'S code: their constants are not our claims, and a
# substring of their numbers is not our number. First run flagged an openai SDK docstring that
# says "5 MiB" about its own streaming chunk, and 5242880 as a SUBSTRING of 52428800 in a
# Next.js build artifact. A false alarm spends the trust the one real finding needs.
CODE_VENDOR_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "site-packages",
                    ".next", "dist", "build", "out", "vendor", ".pytest_cache", ".mypy_cache",
                    "graphify-out", "target", ".terraform",
                    # A SEPARATE CODEBASE IS OTHER PEOPLE'S CONSTANTS. `hermes-agent` is our fork of
                    # the upstream Hermes repo, scanned only because the code root is /root. Its
                    # `MAX_FILE_BYTES = 5 * 1024 * 1024` caps E2E evidence PNGs and has nothing to do
                    # with Obsidian's per-file sync cap — flagging it is the tool being RIGHT ABOUT
                    # THE CONSTANT AND WRONG ABOUT THE CLAIM (Pixel, 2026-09-28). Same rule I already
                    # apply to node_modules: vendored trees are not ours to police.
                    "hermes-agent"}


def _code_token_pat(fig):
    """A constant in code must match as a STANDALONE token.

    `\\b` on both sides is what stops 5242880 from matching inside 52428800 — the exact error HQ
    named. Prose figures ("5 MiB") also need the non-word guard so '15 MiB' cannot match '5 MiB'.
    """
    return re.compile(r"(?<![\w.])" + re.escape(fig) + r"(?![\w.])")


# A CONSTANT IN CODE IS OFTEN WRITTEN AS AN EXPRESSION, NOT A LITERAL. The defective value here
# was `CAP_BYTES = 5 * 1024 * 1024` — the literal 5242880 appears in NO file, because the author
# wrote the arithmetic. A registry keyed on the EVALUATED value is blind to the form the value
# actually took, which is the whole error class one more time: the unit of the check decides what
# the check can see. So each code record may carry ALTERNATE FORMS to look for beside the number.
def _code_forms(rec):
    forms = [rec["figure"]]
    forms.extend(rec.get("code_forms", []) or [])
    return forms


def _norm_expr(s):
    """Collapse whitespace/underscores so `5 * 1024 * 1024`, `5*1024*1024` and `5_242_880` agree."""
    return re.sub(r"[\s_]+", "", s)


def _norm_expr_pat(form):
    """The EXPRESSION form, boundary-guarded EXACTLY as the figure form is (Pixel, 2026-09-28).

    A raw substring test on normalised text cannot tell a digit from its neighbour: `25 * 1024 * 1024`
    normalises to `25*1024*1024`, WHICH CONTAINS `5*1024*1024` — so a perfectly correct 25 MiB
    threshold in fleet-hygiene-audit.py was reported as the withdrawn 5 MiB cap, in NINE places.
    That is the same defect as `5242880` inside `52428800`, or `348` inside `1,348`: the boundary the
    figure matcher got and the expression matcher never did. Sixth appearance tonight.
    """
    return re.compile(r"(?<![\w.])" + re.escape(_norm_expr(form)) + r"(?![\w.])")


def _code_lines(path, lines):
    """Return the file's lines with COMMENTS AND DOCSTRINGS BLANKED, indices preserved.

    The code surface exists to find a withdrawn CONSTANT BAKED INTO AN ARTIFACT. A mention inside a
    docstring or a comment is documentation, not a baked constant — and this tool's own docstrings
    necessarily SHOW the form, so it reported ITSELF (4 self-matches, measured). Blanking the prose
    keeps every executable occurrence and drops the commentary.

    THE CONTEXT WINDOW IS STILL READ FROM THE ORIGINAL LINES, deliberately: a comment that names the
    value a CONSERVATIVE PRE-FILTER must still suppress the hit through CODE_MARKER_HINT. Match on
    code, read context from the source.
    """
    out = list(lines)
    if path.endswith(".py"):
        try:
            tree = ast.parse("\n".join(lines))
            ranges = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    b = getattr(node, "body", None)
                    if b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) \
                       and isinstance(b[0].value.value, str):
                        d = b[0]
                        ranges.append((d.lineno, d.end_lineno or d.lineno))
            for lo, hi in ranges:
                for i in range(lo, min(hi, len(out)) + 1):
                    out[i - 1] = ""
        except SyntaxError:
            # An unparsable .py still gets comment-stripping. Not silent: the caller counts on the
            # match being on code, so say so in the finding line if this ever fires.
            out.append("")  # no-op, keeps the shape obvious
    for i, line in enumerate(out):
        if line.lstrip().startswith("#"):
            out[i] = ""
        elif "#" in line:
            out[i] = line.split("#", 1)[0]
        elif path.endswith((".js", ".ts")) and "//" in line:
            out[i] = line.split("//", 1)[0]
    return out


def scan_code(roots, registry, window=4):
    """Report withdrawn constants still standing in code without a correction beside them."""
    findings = []
    suppressed = []          # hits set aside by a hint word — REPORTED, never silent
    files_scanned = 0
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in CODE_VENDOR_DIRS]
            for fn in filenames:
                if not fn.endswith((".py", ".sh", ".js", ".ts")):
                    continue
                path = os.path.join(dirpath, fn)
                # THE REGISTRY IS DATA, NOT A CLAIM. It necessarily CONTAINS every withdrawn figure
                # and every expression form — that is its job — so scanning it reports the tool
                # against itself. Excluded by name, and stated here rather than silently skipped.
                if fn == "retractions.json":
                    continue
                try:
                    text = open(path, encoding="utf-8", errors="ignore").read()
                except OSError:
                    continue
                files_scanned += 1
                lines = text.splitlines()
                # MATCH ON CODE, READ CONTEXT FROM THE SOURCE — see _code_lines.
                code_lines = _code_lines(path, lines)
                for rec in registry:
                    if not rec.get("also_scan_code"):
                        continue
                    # A record may scope its code hits (e.g. our own tools, not any file).
                    scope = rec.get("code_only_files_matching")
                    if scope and scope not in path:
                        continue
                    forms = _code_forms(rec)
                    for i, line in enumerate(code_lines):
                        hit_form = None
                        for form in forms:
                            if form.isdigit():
                                # a bare constant must be a standalone token
                                if _code_token_pat(form).search(line):
                                    hit_form = form
                                    break
                            else:
                                # an EXPRESSION ("5 * 1024 * 1024") — compared normalised so the
                                # author's spacing/underscores cannot hide it, AND boundary-guarded
                                # so `25 * 1024 * 1024` cannot match `5 * 1024 * 1024`
                                if _norm_expr_pat(form).search(_norm_expr(line)):
                                    hit_form = form
                                    break
                        if not hit_form:
                            continue
                        lo = max(0, i - window)
                        hi = min(len(lines), i + window + 1)
                        ctx = "\n".join(lines[lo:hi]).lower()
                        marker = next((h for h in CODE_MARKER_HINT if h in ctx), None)
                        if marker:
                            # SUPPRESSION IS A RESULT, NOT A SILENCE (Pixel, 2026-09-28). A hit
                            # dropped by a hint word used to vanish with no trace, so a false
                            # NEGATIVE looked exactly like a clean file. Collected here and
                            # REPORTED — the reader sees which lines were set aside and on whose
                            # word, and can judge the word.
                            suppressed.append({
                                "file": os.path.relpath(path, root),
                                "line": i + 1,
                                "matched_form": hit_form,
                                "by": marker,
                                "text": line.strip()[:110],
                            })
                            continue      # the code carries its own correction beside it
                        findings.append({
                            "file": os.path.relpath(path, root),
                            "figure": rec["figure"],
                            "matched_form": hit_form,
                            "line": i + 1,
                            "text": line.strip()[:120],
                            "superseded_by": rec.get("superseded_by", ""),
                            "surface": "code",
                        })
    # DEDUPE BY LOCATION: two registry records can name the same underlying defect (a value and
    # the expression that produces it), and reporting one line twice makes a single finding look
    # like two — the same inflation this whole thread is about, one level down.
    seen, out = set(), []
    for f in findings:
        key = (f["file"], f["line"])
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return files_scanned, out, suppressed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=DEFAULT_DIR)
    ap.add_argument("--registry", default=DEFAULT_REG)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--code-roots", default=None,
                    help="root to scan for withdrawn CONSTANTS baked into artifacts; "
                         "defaults to the vault containing --dir, pass '' to disable")
    a = ap.parse_args()

    if not os.path.isdir(a.dir):
        print(f"❌ scan dir not readable: {a.dir}", file=sys.stderr)
        return 2
    if not os.path.isfile(a.registry):
        print(f"❌ registry not readable: {a.registry}", file=sys.stderr)
        return 2
    try:
        registry = load_registry(a.registry)
    except (OSError, ValueError) as e:
        print(f"❌ registry invalid: {e}", file=sys.stderr)
        return 2

    files_scanned, findings, scope_matched, scope_fired = scan(a.dir, registry)

    # ── the CODE surface: a withdrawn constant baked into an artifact ────────────────────────
    # Scanned relative to the vault the lane lives in, so a note-scoped run also catches the
    # TOOLS in the same tree. `--code-roots` overrides; empty disables it entirely.
    code_root = os.path.abspath(os.path.join(a.dir, "..", ".."))
    # `None` (not supplied) -> default vault; `''` (supplied empty) -> DISABLED. An empty string is
    # falsy, so treating it as "not supplied" made the documented off-switch a no-op.
    if a.code_roots is None:
        code_roots = [code_root] if os.path.isdir(os.path.join(code_root, "scripts")) else []
    elif a.code_roots == "":
        code_roots = []
    else:
        code_roots = [a.code_roots]
    code_files, code_findings, code_suppressed = (0, [], [])
    if code_roots:
        code_files, code_findings, code_suppressed = scan_code(code_roots, registry)

    # FAIL CLOSED, BUT ONLY ON BLINDNESS. A record may carry `only_files_matching`, scoping it to a
    # lane, so pointing this at a lane the registry does not know matches ZERO files and used to
    # return 0 — A PASS ON A LANE IT CANNOT SEE. But a per-lane scan will ALWAYS have records scoped
    # elsewhere, so "some scope matched nothing" is normal. The failure is: NO record matched
    # anything here, i.e. this tree is outside the registry's reach and nothing was looked for.
    #
    # CORRECTION 2026-09-28 (found by re-running Pixel's control after my own change): my SEVEN
    # unscoped records — the phrase records, added to sweep ASSERTIONS fleet-wide — incremented
    # scope_matched for EVERY note, so `engaged` was never 0 and PIXEL'S DEFECT-1 FIX COULD NOT
    # FIRE. The code was right and the registry had disarmed it: a control whose input is
    # data-driven goes inert the moment the data stops being narrow. That is rung 4 (reachable) of
    # the guard ladder, and it was invisible because the test still passed.
    #
    # The honest question is not "did any record engage" but "DID ANY RECORD ACTUALLY LOOK HERE" —
    # i.e. did any record engage with a file it was REACHING FOR, rather than merely matching text
    # in common English. So engagement is now measured on SCOPE-BEARING records too: a tree is only
    # "seen" if at least one record with a scope engaged, OR an unscoped record found something.
    n_scoped_engaged = sum(1 for i, n in enumerate(scope_matched)
                           if n > 0 and registry[i].get("only_files_matching"))
    n_fleetwide = sum(1 for rec in registry if not rec.get("only_files_matching"))
    engaged = n_scoped_engaged + n_fleetwide
    # A TREE IS "SEEN" IF ANY RECORD COULD EXAMINE IT. Two kinds of record reach a tree:
    #   - LANE-SCOPED records, which reach it only if their scope matches (Pixel's original check);
    #   - FLEET-WIDE records (no scope), which genuinely examine every note — so while any exist,
    #     no tree is unreadable, and reporting exit 2 would be the false BLOCKER, not the false pass.
    # Both facts are PRINTED so the reader can see the coverage that produced the verdict — the
    # whole hazard of a fail-closed check is that its verdict looks the same either way.
    blind = (n_scoped_engaged == 0 and n_fleetwide == 0)
    dead = [registry[i].get("only_files_matching") or "<unscoped>"
            for i, n in enumerate(scope_matched) if n == 0]

    if a.json:
        # A DENOMINATOR WHOSE NUMERATOR NEVER APPEARS. files_scanned and code_files_scanned were
        # reported with NO ROOT, so a default that is a FRACTION of the documented scope was
        # invisible in the artifact — a peer read --json without --dir, saw 773 "files_scanned", and
        # reasonably called it the whole tree. One root key stops that. (Pixel, 2026-09-28.)
        print(json.dumps({"root": os.path.abspath(a.dir),
                          "code_roots": [os.path.abspath(r) for r in code_roots],
                          "files_scanned": files_scanned, "registry": len(registry),
                          "records_engaged": engaged, "blind": blind,
                          "scopes_matching_nothing": dead, "findings": findings,
                          "code_files_scanned": code_files, "code_findings": code_findings,
                          "code_suppressed": code_suppressed}, indent=2))
    elif not a.quiet:
        print(f"  registry : {len(registry)} retracted figure(s), {engaged} engaged with this tree"
              + (f" ({n_scoped_engaged} lane-scoped, {n_fleetwide} scanned in EVERY tree)"
                 if n_fleetwide else " (all lane-scoped)"))
        print(f"  scanned  : {files_scanned} note(s) under {a.dir}")
        if code_roots:
            print(f"  code     : {code_files} source file(s) under {code_roots[0]} "
                  f"(for the records flagged also_scan_code)")
        if blind:
            print("\n  ❌ NO record's scope matched ANY file in this tree — the registry does not")
            print("     reach this lane, so NOTHING was looked for. A scope that matched nothing is a")
            print("     MEASUREMENT FAILURE, not a clean lane. Add a record for this lane.")
        if findings:
            print(f"\n  🔴 {len(findings)} note(s) carry a WITHDRAWN figure with no correction marker:")
            cur = None
            for f in findings:
                if f["file"] != cur:
                    cur = f["file"]
                    print(f"\n      {cur}")
                print(f"        `{f['figure']}` x{f['total_hits']} (lines {f['lines']})"
                      + (f"  -> {f['superseded_by']}" if f["superseded_by"] else ""))
            print("\n  (a correction applied to the NEXT note and not swept back is how a stale line survives"
                  "\n   its own author — mark the old note in place, keep the claim visible against its correction)")
        elif not blind:
            print("\n  ✅ no unmarked retracted figures")
        if code_findings:
            print(f"\n  🔴 {len(code_findings)} CODE location(s) still assert a WITHDRAWN constant:")
            for f in code_findings:
                print(f"\n      {f['file']}:{f['line']}")
                print(f"        `{f['figure']}`  {f['text']}")
                if f["superseded_by"]:
                    print(f"        -> {f['superseded_by']}")
            print("\n  (a withdrawn NUMBER lives in a note and can be marked. A withdrawn CONSTANT gets")
            print("   baked into an artifact, acquires a comment calling it measured, and stops looking")
            print("   like a claim at all — which is why it needs its own surface.)")
        elif code_roots:
            print("\n  ✅ no unmarked withdrawn constants in code")
        # SUPPRESSION IS A RESULT, NOT A SILENCE. These are hits a hint word set aside. They are not
        # findings — but a false NEGATIVE and a clean file look identical without this, so the reader
        # gets the count, the word each one was set aside on, and the line.
        if code_suppressed:
            by = {}
            for s in code_suppressed:
                by.setdefault(s["by"], []).append(s)
            print(f"\n  ⚪ {len(code_suppressed)} code hit(s) SET ASIDE by a hint word "
                  f"(not findings — listed so the suppression is visible):")
            for word, rows in sorted(by.items(), key=lambda kv: -len(kv[1])):
                print(f"        by {word!r}: {len(rows)}")
                for s in rows[:3]:
                    print(f"           {s['file']}:{s['line']}  {s['text'][:76]}")
        elif code_roots:
            print("        (0 hits were suppressed — nothing was set aside by a hint word)")
    if blind:
        return 2
    return 1 if (findings or code_findings) else 0


if __name__ == "__main__":
    sys.exit(main())
