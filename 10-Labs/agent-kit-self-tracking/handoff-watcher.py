#!/usr/bin/env python3
"""
HANDOFF WATCHER — unified. Answers two questions and nothing else:

  1. "Are the DMs being ANSWERED?"      -> missed-ack + stall detection
  2. "Are handoffs being ADDRESSED?"    -> stuck detection (open too long, no return)

Merged from two divergent fleet designs (2026-09-17):
  - HQ's 992-line version  -> the DETECTION engine (missed-ack, stall, return-note
    matching, truth-check). It had no cooldown, no lane scoping, no cap.
  - the 274-line version on gizmo/treasury/pixel -> the NOISE CONTROL
    (HUMAN_LANES, OWN_LANES, STUCK_RENAG_HOURS cooldown, MAX_STUCK_PER_RUN cap).

WHY THE MERGE: both halves were right and each was missing the other's. Detection
without noise control trains a human to ignore the alert that matters; noise
control without detection means nobody ever learns a DM went unanswered.

NOISE RULES (non-negotiable — every section obeys all three):
  * LANE SCOPE  — a seat reports only its own lanes. Without this, four agents
    scan one vault and mail four copies of one fact.
  * HUMAN LANES — transit between two agents is the system working, not news.
  * COOLDOWN    — an item alerts once, then stays quiet for RENAG_HOURS. A NEW
    item alerts immediately; an OLD one reminds daily, never every 15 minutes.

Runs as a no_agent cron script. Prints NOTHING when nothing needs a human.

Usage:
    python3 handoff-watcher.py [vault_path] [--days N] [--vault-name NAME]
                               [--state PATH] [--own-lanes labs,gizmo]
                               [--seat gizmo]
"""
import os
import re
import sys
import json
import time
import subprocess
import datetime

VAULT = "/root/vaults/gentech"
VAULT_NAME = "gentech"
STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "handoff-watcher.state.json")

# Lanes each seat owns. A seat reports only what it can act on; without this,
# four agents scan one vault and mail four copies of the same fact. HQ is the
# coordination seat, so it sees everything ([] = all lanes).
#
# Cron has no script-args field, so the seat is derived from the script's own
# path (/root/.hermes/profiles/<seat>/scripts/...) — no cron change needed.
SEAT_LANES = {
    "gentech": [],                                                    # HQ — all lanes
    "gentech-treasury": ["treasury", "strategies", "gentech-treasury"],
    "gizmo": ["labs", "gizmo"],
    "pixel": ["entertainment", "pixel"],
    "forge": ["forge"],
}


def _seat_from_path():
    parts = os.path.dirname(os.path.abspath(__file__)).split(os.sep)
    if "profiles" in parts:
        i = parts.index("profiles")
        if i + 1 < len(parts):
            return parts[i + 1]
    return "gentech"


KNOWN_GROUPS = {"hq", "forge", "labs", "entertainment", "treasury", "gizmo",
                "gentech", "gentech-treasury", "pixel", "stealth", "jordan",
                "jintech", "strategies"}

# Lanes that belong to a HUMAN. A handoff landing here is news; a handoff moving
# between two agents is transit — the agents' business, not Jordan's.
HUMAN_LANES = {"hq", "jordan", "jintech"}

TO_LANE_RE = re.compile(r"^(.+)-to-(.+)$")

# ---- thresholds -------------------------------------------------------------
# "Are the DMs being answered?" — two escalating signals.
ACK_AFTER_HOURS = 2        # open + no ack back  -> "agent read it but went quiet"
STALL_AFTER_HOURS = 6      # open + no return    -> "agent may have gone silent"
# "Has this been addressed at all?" — the human-worthy one.
STUCK_AFTER_HOURS = 24     # open >1 day, no return -> interrupt a human
STUCK_RENAG_HOURS = 24     # re-nag the same item at most once per day
MAX_STUCK_PER_RUN = 5      # cap the list so one run can't dump the backlog
ACK_LOOKBACK_DAYS = 7
STALL_LOOKBACK_DAYS = 14

# ---- PROACTIVE TIER (added 2026-09-20, Jordan) -------------------------------
# "Can we upgrade this cron job to be more proactive... I'm starting to see DMs
# are going unanswered."
#
# The watcher used to only TELL Jordan. Now, past the stall threshold, it wakes
# the receiving AGENT directly over the a2a mesh — the vault stays the record,
# the DM only breaks the silence (DM to wake, vault to record).
#
# ORDER MATTERS: this ships together with the _hours_open fix above. Auto-waking
# on the old filename-derived age would have DM'd agents about handoffs that
# were minutes old — an alert about a note written at 00:35 with yesterday's
# date reads as 13h stalled the instant it lands. Proactive + wrong age is a
# fleet-wide false alarm generator, so the age fix is load-bearing, not cosmetic.
WAKE_AFTER_HOURS = STALL_AFTER_HOURS   # wake the receiving agent (not Jordan)
WAKE_RENAG_HOURS = 12                  # never re-wake the same handoff more often
WAKE_MAX_PER_RUN = 3                   # a bad sweep must not DM the whole fleet

# Lane receiver name -> a2a peer alias that `hermes peer dm` actually knows.
# Lanes use group names (entertainment, labs, treasury); the mesh uses seat
# names (pixel, gizmo, gentech-treasury). Waking the wrong one is a silent no-op.
LANE_TO_PEER = {
    "pixel": "pixel",
    "entertainment": "pixel",
    "gizmo": "gizmo",
    "labs": "gizmo",
    "treasury": "gentech-treasury",
    "gentech-treasury": "gentech-treasury",
    "forge": "forge",
}

# Sender lane -> the name a human reader knows it by. The nudge header used to
# hardcode "HQ" while the BODY interpolated {sender} — so a nudge about a Pixel
# note was headed "HQ → …" and named pixel two lines below. A message that
# misnames its own author is unverifiable at a glance. Measured 2026-09-28.
SENDER_DISPLAY = {
    "gentech": "HQ",
    "gentech-treasury": "Treasury",
    "gizmo": "Labs",
    "pixel": "Entertainment",
    "forge": "Forge",
}

def sender_display(lane):
    """Display name for a sending lane; falls back to the lane name itself.

    Falling back rather than guessing is deliberate: a wrong label is worse
    than an unfamiliar one, because it reads as a correction."""
    return SENDER_DISPLAY.get((lane or "").strip(), lane)

# Desktop seats power down overnight BY DESIGN — measure their age in AWAKE
# hours so a note landing at 23:00 isn't scored as late. Windows are Jordan's
# actual availability: evening session + occasional morning.
DESKTOP_SEATS = {"forge"}
DESKTOP_TZ = "America/New_York"
DESKTOP_WINDOWS = ((17, 1), (7, 10))

RESOLVED_MARKERS = (
    "status: [x]", "status: resolved", "status: done", "status: closed",
    "## resolved", "- [x]", "status: completed", "status: shipped",
    "shipped & verified", "shipped and verified", "verified shipped",
    # MEASURED, not guessed (2026-09-17). The fleet's dominant resolution word is
    # "answered" (~30 uses across the vault) and the marker list did not contain
    # it -- so every answered handoff still counted as open. Impact: 123 of 250
    # "stuck" items were false positives (49%), and the whole forge-to-labs lane
    # read as congested when 12 of its 13 notes were answered. "filed" likewise
    # means the work landed.
    "status: answered", "answered", "status: filed", "filed",
    # Added 2026-09-17 after finding the emoji strip above. These match the
    # fleet's real completion vocabulary that the ASCII-only scan could not see:
    # "**Status:** ✅ ..." (-> "status: [done]"), and the explicit stand-down
    # phrases used when work is cancelled rather than completed.
    "status: [done]", "[done] acknowledged", "nothing owed", "no further action",
    # Added 2026-09-24 — the watcher did not speak the fleet's own closer vocabulary.
    # The handoff-mesh skill documents the closers as
    # `answered | acked | confirmed | superseded | done-done`, but only "answered"
    # and "filed" were implemented. Measured: `**Status:** done-done` matched NO
    # marker, so a note its owner had already closed read OPEN forever and the
    # watcher re-nudged the agent who closed it. The existing "status: done" cannot
    # catch it: the lookahead `(?![\w-])` sees the "-" in "done-done".
    #
    # STATUS-SCOPED ONLY, never bare. `superseded` and `confirmed` appear in ordinary
    # prose ("v3 being superseded before my note landed"), and _marker_hit falls back
    # to a whole-text scan for notes with NO status line — bare words would have
    # false-closed 4 real open notes. Status-scoped cannot: those notes have no
    # status line, and a note that declares a status is judged only on that line.
    #
    # NOT adding "acked" here: IN_PROGRESS_STATUS already owns it deliberately, so an
    # acked-but-unfinished handoff surfaces instead of vanishing.
    "status: done-done", "status: superseded", "status: confirmed",
)

# Explicit "someone is on it, work has begun" states. These are NOT stuck --
# they are in flight. Kept separate from RESOLVED so an acked-but-never-finished
# item still surfaces under its own signal rather than vanishing entirely.
IN_PROGRESS_STATUS = (
    "status: acked", "status: ack", "ack + work started", "acked, starting",
    "status: in progress", "status: working", "status: picked up",
)

# nightly-maintenance.py archives any *-to-*/ lane note older than this.
ARCHIVE_AFTER_DAYS = 7
WARN_BEFORE_ARCHIVE_DAYS = 2

QUEUE_JSON = os.path.join(VAULT, "scripts", "build_queue.json")
DONE_STATUSES = {"shipped", "done", "cancelled", "dropped"}
WAIT_RE = re.compile(r"waiting on|needs jordan|awaiting jordan|blocked|pending direction|green-?light needed", re.I)
CLAIM_DONE_RE = re.compile(r"\bshipped\b|\bcompleted\b", re.I)

COMPLETION_FILES = {
    "gentech": "gentech-completions.md", "entertainment": "entertainment-completions.md",
    "treasury": "treasury-completions.md", "labs": "labs-completions.md",
    "gizmo": "gizmo-completions.md", "forge": "forge-completions.md",
    "hq": "hq-completions.md",
}


def _bases():
    """Lane roots. Mirror kept for the HQ seat only; others read the real root."""
    out = [os.path.join(VAULT, "01-HANDOFFS")]
    mirror = os.path.join(VAULT, "Gentech", "01-HANDOFFS")
    if os.path.isdir(mirror):
        out.append(mirror)
    return out


INBOX = os.path.join(VAULT, "01-HANDOFFS", "INBOX")


STANDING_DOCS = re.compile(
    r"soul|constitution|charter|protocol\.md$|readme\.md$|index\.md$|"
    r"jordan-queue|deadline-board|routing\.md$|memory-trim",
    re.I,
)


def is_standing_doc(name):
    """True for permanent documents that live in the lanes but are not handoffs.

    SOUL files, protocols, READMEs and standing registries are records, not
    work items. They never get 'answered' and they are never done, so an expiry
    clock on them is a permanent false alarm. Found 2026-09-17: all five
    'expiring' items were FORGE-SOUL.md and soul-and-record.md — standing
    documents that had been counted as neglected handoffs.
    """
    return bool(STANDING_DOCS.search(name))


# Meaning-carrying emoji must be CONVERTED before the non-ASCII strip, because
# is_resolved() deletes every non-ASCII byte. Measured 2026-09-17: "✅" was the
# fleet's dominant completion signal and it was being erased before matching —
# 24 handoffs carried a "**Status:** ✅ ..." line that no marker could ever see,
# and 2 of them were actively showing to Jordan as unanswered.
EMOJI_STATUS = {
    "\u2705": " [done] ",   # ✅
    "\u2714": " [done] ",   # ✔
    "\u2713": " [done] ",   # ✓
    "\U0001F7E2": " [done] ",  # 🟢
    "\U0001F534": " [open] ",  # 🔴
    "\U0001F7E0": " [open] ",  # 🟠
    "\u23F8": " [open] ",   # ⏸
    "\u23F3": " [open] ",   # ⏳
}


def _normalise(text):
    """Lowercase + tokenise status emoji + strip non-ASCII + collapse whitespace.

    Order matters: emoji are replaced FIRST so their meaning survives the strip.
    """
    norm = text.lower()
    for emoji, token in EMOJI_STATUS.items():
        norm = norm.replace(emoji, token)
    norm = re.sub(r"[^\x00-\x7F]+", "", norm)
    norm = re.sub(r"\*\*", "", norm)
    norm = re.sub(r"\s+", " ", norm)
    return norm


_NEG_WINDOW = 14
_NEG_RE = re.compile(r"\b(not|no|never|isn'?t|wasn'?t|hasn'?t|without|un|nor|neither|pending)\W*$")


def _normalise_lines(text):
    """Like _normalise, but PRESERVES newlines so status lines can be isolated.

    _normalise collapses all whitespace (including newlines) into single spaces,
    which merges the whole note into one line — so any line-scoped logic must run
    on this variant instead.
    """
    norm = text.lower()
    for emoji, token in EMOJI_STATUS.items():
        norm = norm.replace(emoji, token)
    norm = re.sub(r"[^\x00-\x7F\n]+", "", norm)
    norm = re.sub(r"\*\*", "", norm)
    norm = re.sub(r"[ \t]+", " ", norm)
    norm = re.sub(r"\n\s*\n+", "\n", norm)
    return norm


def _scan_markers(text):
    """The word-boundary + negation + code-span scan, over one blob of text."""
    for m in RESOLVED_MARKERS:
        probe = text
        if m in probe:
            probe = re.sub(r"`[^`]*`", " ", probe)
        if not re.search(r"(?<![\w-])" + re.escape(m) + r"(?![\w-])", probe):
            continue
        for hit in re.finditer(r"(?<![\w-])" + re.escape(m) + r"(?![\w-])", probe):
            before = probe[max(0, hit.start() - _NEG_WINDOW):hit.start()]
            if _NEG_RE.search(before):
                continue          # e.g. "not answered", "never filed"
            return True
    return False


def _marker_hit(norm):
    """Do any RESOLVED_MARKERS appear, honestly?

    Several defects were measured on 2026-09-18. The first three cause FALSE
    NEGATIVES (a genuinely open note reads resolved — the direction that HIDES
    work); the fix must not create false POSITIVES either.

      1. Plain substring matching. "unanswered" contains "answered", so
         `**Status:** open` plus the prose "unanswered for 22h" resolved.
      2. No negation handling. "this was NOT answered" also resolved.
      3. Markers inside CODE SPANS counted, so a note that DOCUMENTS the closure
         vocabulary or shows a command example resolved itself:
            "use a word the resolver knows: `answered` / `resolved` / `done`"
            "handoff_closure.py close <h> --outcome answered --note <return>"
      4. Markers in PROSE about a DIFFERENT handoff counted:
            "you answered it on 2026-09-16"  (about another note entirely)
         → a note saying "you answered it properly" resolved itself.

    Fix for 1-3: word boundaries, a negation window, and a code-span strip.
    Fix for 4: judge a note on its STATUS LINES. If a note declares a status at
    all, that declaration is what counts — prose describing other handoffs must
    not close it. Notes with NO status line fall back to the legacy whole-text
    scan, so the fleet's prose closers keep working.
    """
    lines = _normalise_lines(norm).split("\n")
    status = [
        ln for ln in lines
        if "status:" in ln
        or ln.strip().startswith("- [x]")
        or ln.strip().startswith("## resolved")
    ]
    if status:
        return _scan_markers("\n".join(status))
    return _scan_markers(_normalise(norm))


def _closure_says_closed(path):
    """Authoritative override: a closure RECORD beats the marker scan.

    The fleet has two closure mechanisms and only one is authoritative:
      * `handoff_closure.py` writes a sha-bound closure record into the RECEIVER's
        lane (`<receiver>-to-<sender>/_closed/<slug>.md`). Sender-verifiable.
      * this watcher scans the SOURCE file for a marker word — a heuristic that
        cannot see a closure record at all.
    So every handoff properly closed by record still read as OPEN here. Real impact:
    an audit reported `github-compliance-fleetwide` as "unanswered at 22h" when the
    authoritative check said CLOSED (answered by forge, 2026-09-16T02:03:16Z).

    Worse, the two mechanisms actively CONFLICT: stamping the source file's Status
    line (what the V4 skill instructs) changes the source hash and REOPENS the
    record — verified: check() goes CLOSED -> "REOPENED: source changed since
    closure". So the marker scan must not be the last word.

    Defer to the record. Fail-open on any error (a broken import must never make a
    resolved handoff look stuck).
    """
    try:
        import importlib.util as _ilu
        tool = os.path.join(VAULT, "10-Labs", "agent-kit-self-tracking", "handoff_closure.py")
        if not os.path.exists(tool):
            return False
        spec = _ilu.spec_from_file_location("_handoff_closure_w", tool)
        mod = _ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        closed, _reason = mod.is_closed(path)
        return closed is True
    except Exception:
        return False


def is_resolved(path):
    """RECORD FIRST, marker second — the order the skill documents and the code did not.

    This function used to be marker-first:

        if _marker_hit(text): return True          # returns before the record is read
        return _closure_says_closed(path)

    which silently defeats the fail-closed reopen that the record exists to provide.
    Measured 2026-09-28 with a probe note: close it (record OK), then edit the source so
    the record goes stale. `handoff_closure.is_closed()` correctly returns
    (False, 'REOPENED: source changed since closure'), and `_closure_says_closed()` returns
    False — but `is_resolved()` still returned True, because the note's own marker matched
    first and the record was never consulted. A genuinely reopened handoff that carried any
    marker word read RESOLVED by the sweep, so the reopen was invisible to the only thing
    that acts on it.

    The `False` direction is the dangerous one, and it is exactly the direction this
    ordering got wrong: a note that still says "ANSWERED" but whose source was edited
    afterwards is genuinely open again, and stale prose was overriding the record.

    Contract (matches handoff-mesh's documented table):
        closed is True   -> resolved      (record exists, hash matches)
        closed is False  -> OPEN          (REOPENED — this WINS over any marker)
        closed is None   -> fall through  (no record/unverifiable -> legacy marker scan)

    The `None` fall-through preserves every legacy resolution: a note whose record is
    absent or unverifiable still resolves by marker exactly as before, so this is a strict
    superset — nothing that resolved before stops resolving.
    """
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return False
    rec = _closure_verdict(path)
    if rec is True:
        return True
    if rec is False:
        # Fail-closed: a REOPENED record outranks any marker on the source.
        return False
    return _marker_hit(text)


def _closure_verdict(path):
    """The closure record's tri-state verdict, or None when there is nothing to consult.

    Returns True (closed) / False (REOPENED — fail-closed) / None (no record, unverifiable,
    or a broken import). `None` is the signal to fall through to the legacy marker scan, so
    an unusable record can never make a resolved handoff look stuck.
    """
    try:
        import importlib.util as _ilu
        tool = os.path.join(VAULT, "10-Labs", "agent-kit-self-tracking", "handoff_closure.py")
        if not os.path.exists(tool):
            return None
        spec = _ilu.spec_from_file_location("_handoff_closure_w", tool)
        if spec is None or spec.loader is None:
            return None
        mod = _ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        closed, _reason = mod.is_closed(path)
        if closed is True:
            return True
        if closed is False:
            return False
        return None
    except Exception:
        return None


# ---- "somebody diagnosed it and nobody acted" --------------------------------
# Jordan (Sep 17): "look for things that are stuck, or things that anybody
# diagnosed... we always want to make sure communications are going through."
#
# Measured before choosing markers: 139 of 258 open to-lane handoffs contain
# diagnosis-flavoured language ("root cause", "diagnosed", "I found"). A scan on
# those words is worthless — it fires on 54% of the vault and is pure noise.
#
# Most of those are DESCRIPTIONS of work already done ("root cause was X, fixed").
# What actually needs a human is a REQUEST that never got answered. So the
# markers below match asks directed at another party, never descriptions:
#   "needs your decision" / "decision needed" / "awaiting your call" /
#   "blocked on you" / "waiting on Jordan" / "green-light needed" / "your call"
# Combined with the existing no-return-note requirement, this stays narrow.
DECISION_RE = re.compile(
    r"needs?\s+(your|a)\s+(decision|call|input|go-?ahead|sign-?off)"
    r"|decision\s+(needed|required|pending|outstanding)"
    r"|awaiting\s+(your|a)\s+(call|decision|response|reply|answer)"
    r"|\byour\s+call\b"
    r"|what\s+i\s+need\s+(from\s+you|is)"
    r"|blocked\s+(on|by)\s+(you|jordan|your\b)"
    r"|waiting\s+on\s+(you|jordan|your\b)"
    r"|green-?light\s+needed",
    re.I,
)


def needs_decision(path):
    """True if the note asks someone for a decision and is not resolved."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except OSError:
        return False
    return bool(DECISION_RE.search(text))


IN_PROGRESS_MARKERS = (
    "status: in progress", "status: in route", "status: in-transit",
    "status: in transit", "status: working", "status: picked up",
    "status: acked", "status: active", "status: in flight", "## in progress",
    "## in route", "## in transit", "- [ ] in progress",
    "status: awaiting review", "status: awaiting review",
    # Bare forms actually seen in the vault (measured 2026-09-17):
    "acked, starting", "ack + work started", "ack'd, ", "started; ",
)


def is_in_progress(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return False
    norm = re.sub(r"[^\x00-\x7F]+", "", text.lower())
    norm = re.sub(r"\*\*", "", norm)
    norm = re.sub(r"\s+", " ", norm)
    return any(m in norm for m in IN_PROGRESS_MARKERS)


def obsidian_link(rel_path):
    from urllib.parse import quote
    return f"obsidian://open?vault={VAULT_NAME}&file={quote(rel_path, safe='')}"


# ---------- discovery --------------------------------------------------------

def find_open():
    """{rel: (group, name, path)} of still-open handoffs across INBOX + to-lanes."""
    open_notes = {}

    def scan_dir(gdir, group):
        if not os.path.isdir(gdir):
            return
        for name in sorted(os.listdir(gdir)):
            if not name.endswith(".md"):
                continue
            path = os.path.join(gdir, name)
            if is_resolved(path):
                continue
            open_notes[os.path.relpath(path, VAULT)] = (group, name, path)

    if os.path.isdir(INBOX):
        for group in sorted(os.listdir(INBOX)):
            if group in KNOWN_GROUPS:
                scan_dir(os.path.join(INBOX, group), group)

    for base in _bases():
        if not os.path.isdir(base):
            continue
        for d in sorted(os.listdir(base)):
            m = TO_LANE_RE.match(d)
            if not m:
                continue
            receiver = m.group(2)
            if receiver in KNOWN_GROUPS:
                scan_dir(os.path.join(base, d), receiver)
    return open_notes


def _hours_from_name(name):
    """Hours since a handoff's YYYY-MM-DD filename date (midday anchored).

    Filename date, NOT mtime — git sync re-touches every mtime, so mtime is
    useless as a "how long has this been open" signal.

    ⚠️ FALLBACK ONLY (2026-09-20). This reads a date the AUTHOR typed, not when
    the handoff actually landed, so a note written at 00:35 UTC and named with
    yesterday's date is scored as ~13h old the moment it arrives. That produced a
    false "12h, no return" on a handoff that was answered in two minutes. Real age
    now comes from _first_seen(); this survives only for uncommitted files with no
    usable timestamp.
    """
    m = re.match(r"^(20\d\d-\d\d-\d\d)", name)
    if not m:
        return None
    try:
        d = datetime.datetime.strptime(m.group(1), "%Y-%m-%d").replace(hour=12)
        return max(0.0, (datetime.datetime.now() - d).total_seconds() / 3600)
    except ValueError:
        return None


# ---------- real age: when did this handoff actually appear? -----------------
# Age must not come from the filename (author-typed, wrong across midnight) and
# must not come from mtime (git sync re-touches every file). The commit that
# ADDED the file is stable through syncs, and anything we have seen before is
# pinned in state so it can never drift later.

FIRST_SEEN = {}          # rel -> epoch seconds, persisted in state

# Proactive-tier switches (set from argv). Default: wake ENABLED — that is the
# point of the tier — but every run is bounded by WAKE_MAX_PER_RUN and the
# per-handoff cooldown, and --no-wake / --dry-run exist for testing and for any
# seat that does not want outbound DMs from its watcher.
NO_WAKE = False
DRY_RUN = False


def _git_added_epoch(path):
    """Epoch of the commit that ADDED this file. None if untracked/no git."""
    try:
        out = subprocess.run(
            ["git", "-C", VAULT, "log", "--diff-filter=A", "--format=%ct", "-1", "--", path],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0 and out.stdout.strip():
            return float(out.stdout.strip().splitlines()[-1])
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return None


def _first_seen(path, rel):
    """Epoch this handoff first appeared, best evidence available, pinned in state."""
    memo = FIRST_SEEN.get(rel)
    if memo:
        return memo
    epoch = _git_added_epoch(path)
    if epoch is None:
        try:
            epoch = os.path.getmtime(path)      # uncommitted: mtime is all we have
        except OSError:
            epoch = time.time()
    FIRST_SEEN[rel] = epoch
    return epoch


def _hours_open(path, name, rel):
    """Hours this handoff has genuinely been open. Replaces the filename guess."""
    epoch = _first_seen(path, rel)
    hours = max(0.0, (time.time() - epoch) / 3600)
    # Guard against a bogus future clock or an ancient commit on a re-used path:
    # if git is confident it is older than the filename date, the filename is
    # simply wrong — trust git. If git says NEWER than the filename, that is a
    # re-added file; trust the earlier of the two so we do not under-report.
    by_name = _hours_from_name(name)
    if by_name is not None and by_name < hours and hours - by_name > 12:
        return by_name
    return hours


def _in_desktop_window(dt):
    for start, end in DESKTOP_WINDOWS:
        if start <= end:
            if start <= dt.hour < end:
                return True
        elif dt.hour >= start or dt.hour < end:
            return True
    return False


def _desktop_awake_hours(since_dt):
    """Availability-window hours elapsed. None on failure (caller keeps wall clock)."""
    try:
        try:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(DESKTOP_TZ)
        except Exception:
            tz = datetime.timezone.utc
        start = since_dt.astimezone(tz) if since_dt.tzinfo else since_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz)
        end = datetime.datetime.now(tz)
    except Exception:
        return None
    if end <= start:
        return 0.0
    total = 0.0
    day = (start - datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    while day <= end:
        for w_start_h, w_end_h in DESKTOP_WINDOWS:
            if w_start_h <= w_end_h:
                spans = [(day + datetime.timedelta(hours=w_start_h),
                          day + datetime.timedelta(hours=w_end_h))]
            else:
                spans = [(day + datetime.timedelta(hours=w_start_h),
                          day + datetime.timedelta(days=1)),
                         (day, day + datetime.timedelta(hours=w_end_h))]
            for w_start, w_end in spans:
                lo, hi = max(w_start, start), min(w_end, end)
                if hi > lo:
                    total += (hi - lo).total_seconds() / 3600
        day += datetime.timedelta(days=1)
    return total


def _dt_from_name(name):
    m = re.match(r"^(20\d\d-\d\d-\d\d)", name)
    if not m:
        return None
    try:
        return datetime.datetime.strptime(m.group(1), "%Y-%m-%d").replace(hour=12)
    except ValueError:
        return None


def _reverse_lane(sender, receiver):
    return f"{receiver}-to-{sender}"


_RE_LINE_RE = re.compile(r"^[ \t|>*\-]*\**\s*re\s*\**\s*:\s*\**\s*(.+)$", re.I | re.M)


def _re_names_handoff(path, handoff_name):
    """True when the note's own `**Re:**` line(s) name THIS handoff by FILENAME.

    WHY THIS EXISTS (pixel, 2026-09-30). In a filed dir the only test that runs is the filename
    substring, so a reply with its OWN title is unfindable: measured on the real pair, the identical
    bytes read True in the live lane and False in `_archive/`, and the ONLY link between the two
    notes was the `**Re:**` path inside the reply's body. The topic-in-body scan is correctly
    disabled in filed dirs, so the one test that could have matched it was switched off in exactly
    the directory the archiver files returns into. Each guard was right; the conjunction made a
    genuinely answered handoff read "no return" forever.

    A `**Re:**` line is neither a filename nor a topic mention: it is a deliberate claim by the
    reply about WHAT IT ANSWERS, and a note that merely mentions a topic does not emit one. That is
    why this fixes the false negative WITHOUT reopening the false positive the `if sub: continue`
    guard exists to prevent -- confirmed both ways in the harness (a filed note mentioning the topic
    stays False; a filed note whose Re: names a different handoff stays False).

    Matches the handoff FILENAME (which carries the `.md`, so it cannot be coincidental) and, as a
    fallback, the extension-less slug on a word boundary -- a longer name that merely contains it
    does not qualify.

    BOUNDARY, STATED PLAINLY (pixel, 2026-09-30 -- this is where the fix ENDS). **The edge is the
    CONVENTION, not the mechanism.** A reply whose `Re:` is PROSE, or which links by CONTENT rather
    than by citing the path, is STILL invisible here: measured on a real pair, the reply said what it
    answered ("re: your Correction 2 answered with the exact command; your Correction 1 is the SAME
    over-count Treasury already retracted") and contained the handoff's basename ZERO times. **That is
    a large, older cohort, because citing the filename is the NEWER convention.**

    DO NOT WIDEN THIS TO A LOOSER BODY MATCH. The obvious relaxation -- match the topic anywhere in
    the body -- is exactly the false positive the `if sub: continue` guard exists to prevent, and it
    would trade a false negative for a false positive at fleet scale.

    **THE REMEDY IS THE RECORD, NOT A WIDER HEURISTIC.** A closure record is a deliberate, hash-bound
    claim that names its subject exactly, and it needs no convention: `is_resolved()` is RECORD-FIRST,
    so a prose-linked reply CLOSED BY RECORD stops nagging regardless of what this function returns.
    Measured 2026-09-30: 17 handoffs carry a closure record and 0 of them fail this heuristic -- the
    gap is unexercised, not absent, and the record is what covers it.
    """
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            body = fh.read()
    except OSError:
        return False
    for m in _RE_LINE_RE.finditer(body):
        line = m.group(1)
        if handoff_name and handoff_name in line:
            return True
        bare = handoff_name[:-3] if handoff_name.endswith(".md") else handoff_name
        if len(bare) >= 12 and re.search(r"(?<![\w-])" + re.escape(bare) + r"(?![\w-])", line):
            return True
    return False


def _has_return_note(outbound_rel, sender, receiver):
    """True if a reply exists in any reverse lane the RECEIVER owns.

    DEFECT FIXED 2026-09-24. This used to check a single lane,
    `f"{receiver}-to-{sender}"`. But a seat is registered under TWO lane names —
    SEAT_LANES["gizmo"] == ["labs", "gizmo"], SEAT_LANES["pixel"] ==
    ["entertainment", "pixel"] — and agents write returns into whichever name they
    use for themselves. Measured: a handoff to `gizmo` answered in
    `labs-to-gentech/2026-09-23-ack-permanent-fix-rule.md` (topic present in the
    filename) counted as NO RETURN, so the item stayed "open 24h, no return" and
    the watcher re-nudged the agent who had already closed it. The mirror case is
    worse: a return written to `gizmo-to-gentech` while the watcher only looked at
    `labs-to-gentech` was invisible to ITS OWN sender's sweep.

    Fix: try every lane name the receiver is known by, plus the receiver verbatim
    (so an unregistered alias still works). Order-independent, and a superset of the
    old behaviour — the original single lane is always included, so nothing that
    resolved before stops resolving.

    DEFECT FIXED 2026-09-28. It then still `os.listdir()`ed the lane only. The fleet
    ARCHIVES answered handoffs into `_archive/`, and closure records file the source
    into `_closed/`, so a return that had been FILED AWAY read as NO RETURN and the
    item nagged forever — the failure this function exists to stop, one directory down.
    Falsified before the fix: the identical note copied verbatim from `_archive/` into
    the live lane flipped the verdict False -> True purely on its location.

    STALE-REPLY GUARD: in the filed dirs a reply must not PREDATE the handoff it
    answers, otherwise a recurring topic (`forge-tasks`, re-sent daily) is "answered"
    by a note from two weeks earlier. The live lane keeps its previous unguarded
    behaviour, so this stays a strict superset of what resolved before.
    """
    stem = os.path.basename(outbound_rel)[:-3]
    handoff_name = os.path.basename(outbound_rel)      # the full filename, WITH .md
    topic = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
    # A daily roundup note (`.../2026-09-28.md`) has a DATE-ONLY "topic", which would
    # match any same-dated note. That is incidental, not an answer: keep such topics
    # to the live lane's pre-existing behaviour and never let them close via a filed
    # directory. (Measured: dropping this guard flipped 2 daily notes to resolved on a
    # same-date filename alone.)
    topic_specific = bool(topic) and bool(re.search(r"[A-Za-z]", topic))
    sent = _dt_from_name(os.path.basename(outbound_rel))
    def _aliases(seat):
        """Every name this seat answers to, its own included."""
        out = [seat]
        for s, lanes in SEAT_LANES.items():
            if seat == s or seat in lanes:
                out.extend(lanes)
                out.append(s)
        return out

    aliases = _aliases(receiver)
    # THE LANE NAME IS TWO-SIDED (pixel, 2026-09-30). A seat carries two names on BOTH halves, and
    # aliasing only the RECEIVER left the SENDER verbatim: a reply written to
    # `entertainment-to-treasury` was invisible to a handoff sent from `gentech-treasury`, even
    # though the reply's own `Re:` named the handoff by filename. Measured on the real pair: the
    # lane `entertainment-to-treasury` EXISTS and was never tried, so the lookup was
    # {receiver aliases} x {sender verbatim} against replies addressed every other way.
    # Cross the two sides; the receiver half is unknown from the handoff alone, and so is the
    # sender half.
    senders = _aliases(sender)
    lane_names = []
    for r_alias in aliases:
        for s_alias in senders:
            ln = f"{r_alias}-to-{s_alias}"
            if ln not in lane_names:
                lane_names.append(ln)
    # NOTE the old `seen` set was hoisted ABOVE this loop, so after the first base every alias was
    # already "seen" and the inner loop did nothing -- the scan silently stopped at ONE base. Lane
    # names are deduped per base instead.
    for base in _bases():
        for lane_name in lane_names:
            lane = os.path.join(base, lane_name)
            if not os.path.isdir(lane):
                continue
            # Live lane, then its filed subdirs (_archive/ = fleet archiver,
            # _closed/ = closure records). Non-recursive listdir missed both, so a
            # FILED return read as NO RETURN and the item nagged forever.
            for sub in ("", "_archive", "_closed"):
                scan = os.path.join(lane, sub) if sub else lane
                if not os.path.isdir(scan):
                    continue
                for name in sorted(os.listdir(scan)):
                    if not name.endswith(".md"):
                        continue
                    # STALE-REPLY GUARD now applies to the LIVE lane too (2026-09-28,
                    # symmetry — HQ flagged that gating it to `sub` left the identical
                    # hazard reachable in the live lane). A note dated BEFORE the handoff
                    # cannot be its answer, wherever it sits. Measured: extending it to
                    # the live lane changes 0 verdicts on today's vault.
                    #
                    # The DATE-ONLY guard stays gated to filed dirs: a daily roundup
                    # (`2026-09-28.md`) legitimately pairs with the same-named note in the
                    # reverse live lane (the pre-existing `stem in name` behaviour), so
                    # hoisting it out un-resolved 1 real daily note. In a FILED dir there
                    # is no such pairing and a same-date match is incidental.
                    if sub and not topic_specific:
                        continue
                    rd = _dt_from_name(name)
                    if sent is not None and rd is not None and rd < sent:
                        continue
                    if topic_specific:
                        if (topic and topic in name) or stem in name:
                            return True
                    elif name == os.path.basename(outbound_rel):
                        # DATE-ONLY topic (a daily roundup): the ONLY legitimate pairing is the
                        # SAME FILENAME in the reverse lane, which is the pre-existing `stem in
                        # name` behaviour this preserves. A SUBSTRING match is not that: with the
                        # sender half now aliased, `2026-09-30` matched
                        # `2026-09-30-multiplex-convergence-checkpoint.md` in a newly-reachable
                        # lane -- a DIFFERENT note sharing only a date. Measured: 2 flips of that
                        # exact shape, both false. Require equality.
                        return True
                    # Body scan is for batch/roundup acks in the LIVE lane. In the
                    # filed dirs the TOPIC scan leaks: a note that merely MENTIONS the
                    # topic (an archive of unrelated reports) would answer a handoff it
                    # never addressed. Caught by the B4 cross-sender guard.
                    #
                    # FILED DIRS ask a different question of the same file: not "does it
                    # mention this topic" but "does it SAY it answers this handoff". A
                    # `**Re:**` line naming the handoff is a deliberate claim; a topic
                    # mention is not -- which is why this closes the false negative
                    # without reopening the false positive above. (pixel, 2026-09-30)
                    if sub:
                        if _re_names_handoff(os.path.join(scan, name), handoff_name):
                            return True
                        continue
                    # Only long topic slugs are matched inside bodies, to avoid FPs.
                    if not topic or len(topic) < 12:
                        continue
                    try:
                        with open(os.path.join(scan, name), encoding="utf-8", errors="ignore") as f:
                            body = f.read()
                    except OSError:
                        continue
                    if stem in body or topic in body:
                        return True
    return False


def _outbound_items(own_lanes):
    """Yield (rel, sender, receiver, name, hours_open) for open outbound handoffs.

    Applies lane scoping: only lanes this seat owns, never human lanes (those are
    surfaced separately as "FOR YOU"), never the inbound-to-self lane.
    """
    seen = set()
    for base in _bases():
        if not os.path.isdir(base):
            continue
        for d in sorted(os.listdir(base)):
            m = TO_LANE_RE.match(d)
            if not m:
                continue
            sender, receiver = m.group(1), m.group(2)
            if sender not in KNOWN_GROUPS or receiver not in KNOWN_GROUPS:
                continue
            if sender == receiver or receiver in ("gentech",) or receiver in HUMAN_LANES:
                continue
            if own_lanes and receiver not in own_lanes and sender not in own_lanes:
                continue
            gdir = os.path.join(base, d)
            if not os.path.isdir(gdir):
                continue
            for name in sorted(os.listdir(gdir)):
                if not name.endswith(".md") or (sender, name) in seen:
                    continue
                # SOUL files, protocols, READMEs and standing registries live in
                # the lanes but are records, not work items. They never get
                # answered, so they would nag forever.
                if is_standing_doc(name):
                    continue
                seen.add((sender, name))
                # Scope guard kept: dated handoffs only, exactly as before. The
                # AGE is what changes — see _hours_open.
                if _hours_from_name(name) is None:
                    continue
                path = os.path.join(gdir, name)
                rel = os.path.relpath(path, VAULT)
                hours = _hours_open(path, name, rel)
                if receiver in DESKTOP_SEATS:
                    d0 = _dt_from_name(name)
                    if d0 is not None:
                        awake = _desktop_awake_hours(d0)
                        if awake is not None:
                            hours = awake
                path = os.path.join(gdir, name)
                if is_resolved(path):
                    continue
                # Explicitly in-flight ("acked", "work started") is NOT stuck.
                # Someone is on it; nagging about it is the noise we're removing.
                if is_in_progress(path):
                    continue
                rel = os.path.relpath(path, VAULT)
                if _has_return_note(rel, sender, receiver):
                    continue
                yield rel, sender, receiver, name, hours


def find_stalled(min_hours=None):
    """Stalled handoffs ANYWHERE in the mesh — open past the threshold, no reply.

    WHY THIS EXISTS (added 2026-09-17): nightly-maintenance.py imports this module
    and calls find_stalled() to protect stalled notes from auto-archiving. The
    function did not exist, so the caller's `except` caught the AttributeError,
    fell back to an empty set, and the sweep archived stalled handoffs anyway —
    while a comment in the archiver promised they were "NEVER auto-archived".
    A protection that silently does nothing is worse than no protection, because
    it is trusted.

    Unlike the display path this is NOT seat-scoped and NOT capped: the archiver
    must see every lane, and a cap here would leave the tail unprotected.
    """
    threshold = STUCK_AFTER_HOURS if min_hours is None else min_hours
    out = {}
    for rel, sender, receiver, name, hours in _outbound_items(own_lanes=None):
        if hours is not None and hours >= threshold:
            out[rel] = {"sender": sender, "receiver": receiver,
                        "name": name, "hours": hours}
    return out


def _seat_owns_group(seat, group, own_lanes):
    """Is this note addressed to a party THIS seat is responsible for?

    WHY THIS EXISTS (2026-09-17): FOR YOU and EXPIRING were never seat-scoped —
    FOR YOU filtered only on HUMAN_LANES and EXPIRING iterated every open note in
    the vault. So all four seats printed the identical list, and Jordan saw the
    same four notes surfaced in every group ("I keep seeing the watcher in
    different groups pulling that up"). A per-seat watcher that shows every
    seat's inbox is not per-seat.

    HQ is the exception: it owns the human lanes (Jordan's queue) and the mesh as
    a whole, so it keeps the broad view. Every other seat sees only its own.
    """
    if seat == "gentech":
        return True
    return group in own_lanes or group == seat


def _queue_status_map():
    try:
        with open(QUEUE_JSON, encoding="utf-8") as f:
            items = json.load(f)
        return {int(it["id"]): (str(it.get("status", "?")).lower(), it.get("name", "")) for it in items}
    except Exception:
        return {}


def _verify_queue_refs(text, rel):
    findings = []
    qmap = _queue_status_map()
    if not qmap:
        return findings
    recent = (_hours_from_name(os.path.basename(rel)) or 999) <= 48
    for line in text.splitlines():
        refs = [int(n) for n in re.findall(r"#(\d{1,3})\b", line) if int(n) in qmap]
        ambiguous = len(refs) > 2
        for n in refs:
            status, name = qmap[n]
            if WAIT_RE.search(line) and status in DONE_STATUSES:
                findings.append(f"queue #{n} '{name[:40]}' is {status.upper()} in the brain but this handoff lists it as open — stale claim")
            elif recent and not ambiguous and CLAIM_DONE_RE.search(line) and status == "pending":
                findings.append(f"claims queue #{n} '{name[:40]}' shipped, but the brain says PENDING — verify")
    seen, out = set(), []
    for f_ in findings:
        if f_ not in seen:
            seen.add(f_)
            out.append(f_)
    return out[:4]


def verify_truth(open_notes):
    findings = []
    for rel in sorted(open_notes):
        try:
            with open(os.path.join(VAULT, rel), encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue
        for msg in _verify_queue_refs(text, rel):
            findings.append((rel, msg))
    return findings


# ---------- state + cooldown -------------------------------------------------

def load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(state):
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except OSError:
        pass


def _cooled(rel, prev_nagged, now, hours):
    """True if this item is still inside its quiet window."""
    last = prev_nagged.get(rel)
    if not last:
        return False
    try:
        return (now - datetime.datetime.fromisoformat(last)).total_seconds() / 3600 < hours
    except (ValueError, TypeError):
        return False


def wake_agent(receiver, sender, name, hours, dry_run=False):
    """DM the receiving AGENT that a handoff is waiting. Returns (ok, detail).

    The DM is a NUDGE, never the record — the vault already holds the handoff, and
    the note says so. Fails soft: an unreachable seat must not break the sweep,
    and a seat with no mesh alias is reported rather than silently skipped.
    """
    peer = LANE_TO_PEER.get(receiver)
    if not peer:
        return False, f"no mesh alias for lane '{receiver}'"
    msg = (
        f"{sender_display(sender)} → {peer}: handoff waiting on you.\n\n"
        f"  {sender} → {receiver} · open {int(hours)}h, no return\n"
        f"  {name}\n\n"
        f"⚠️ AS OF {datetime.datetime.now(datetime.timezone.utc).strftime('%H:%MZ')} — if you have replied since this "
        f"was generated, this nudge is STALE: re-check before acting, and do not treat it as a live finding.\n\n"
        f"The vault is the record — read it at 01-HANDOFFS/{sender}-to-{receiver}/{name}\n"
        f"Reply into your own lane, then archive the inbound note so the watcher can close it.\n"
        f"(Automatic nudge from the handoff watcher; no action needed if you are already on it.)"
    )
    if dry_run:
        return True, f"DRY RUN — would DM {peer}"
    try:
        out = subprocess.run(["hermes", "peer", "dm", peer, msg],
                             capture_output=True, text=True, timeout=60)
        if out.returncode == 0:
            return True, f"DM sent to {peer}"
        return False, f"dm to {peer} exit {out.returncode}: {(out.stderr or '').strip()[:120]}"
    except (OSError, subprocess.SubprocessError) as e:
        return False, f"dm to {peer} failed: {e}"


def main():
    global VAULT, INBOX, VAULT_NAME, STATE_PATH, NO_WAKE, DRY_RUN
    argv = sys.argv[1:]
    days = 2
    own_lanes = None
    seat = _seat_from_path()
    while argv:
        a = argv.pop(0)
        if a == "--days" and argv:
            days = int(argv.pop(0))
        elif a == "--no-wake":
            NO_WAKE = True
        elif a == "--dry-run":
            DRY_RUN = True
            NO_WAKE = False
        elif a == "--vault-name" and argv:
            VAULT_NAME = argv.pop(0)
        elif a == "--state" and argv:
            STATE_PATH = argv.pop(0)
        elif a == "--own-lanes" and argv:
            own_lanes = [x.strip() for x in argv.pop(0).split(",") if x.strip()]
        elif a == "--seat" and argv:
            seat = argv.pop(0)
        elif a.startswith("/") and os.path.isdir(a):
            VAULT = a
        INBOX = os.path.join(VAULT, "01-HANDOFFS", "INBOX")

    # No --own-lanes given (the cron path): fall back to this seat's lanes.
    if own_lanes is None:
        own_lanes = SEAT_LANES.get(seat, [])

    prev = load_state()
    prev_open = set(prev.get("open", []))
    prev_nagged = prev.get("cooldown", {}) or {}
    prev_woken = prev.get("woken", {}) or {}
    # Pin first-seen stamps across runs so a handoff's age can never drift, and
    # seed from history the first time this runs after the 2026-09-20 age fix.
    for _rel, _epoch in (prev.get("first_seen", {}) or {}).items():
        try:
            FIRST_SEEN.setdefault(_rel, float(_epoch))
        except (TypeError, ValueError):
            pass

    cur_open = find_open()
    cur_open_keys = set(cur_open.keys())
    now = datetime.datetime.now()
    lines = []

    # (1) FOR YOU — a NEW handoff actually addressed to a human THIS seat serves.
    # Seat-scoped. HQ surfaces Jordan's human lanes (its job); every other seat
    # surfaces only what is addressed to ITSELF. Previously unscoped, so all four
    # seats printed the same HQ list and the same note appeared in every group.
    if seat == "gentech":
        human_new = [r for r in (cur_open_keys - prev_open)
                     if cur_open[r][0] in HUMAN_LANES]
    else:
        human_new = [r for r in (cur_open_keys - prev_open)
                     if cur_open[r][0] in own_lanes or cur_open[r][0] == seat]
    if human_new:
        lines.append("📨 FOR YOU:")
        for rel in sorted(human_new):
            if is_standing_doc(cur_open[rel][1]):
                continue      # SOUL files / protocols are records, not work items
            lines.append(f"• {cur_open[rel][1]}")
            lines.append(f"    {obsidian_link(rel)}")

    # (2/3/4) OUTBOUND — answer "was the DM answered / was this addressed?"
    # Eligibility and DISPLAY are deliberately separate. An item that is past
    # threshold and out of cooldown is ELIGIBLE: it gets stamped immediately,
    # whether or not it fits in this run's display cap. Stamping only the shown
    # items leaks the backlog out N-at-a-time on every subsequent run — the same
    # nag, just batched, which is indistinguishable from no dedup at all.
    missed, stalled, stuck, decision = [], [], [], []
    eligible = []
    for rel, sender, receiver, name, hours in _outbound_items(own_lanes):
        if _cooled(rel, prev_nagged, now, STUCK_RENAG_HOURS):
            continue
        eligible.append(rel)
        age_d = int(hours // 24)
        # A decision-request outranks the plain age signals: somebody did the
        # work, told us what they found, and is waiting on an answer.
        if needs_decision(os.path.join(VAULT, rel)):
            decision.append((age_d, sender, receiver, name, rel, hours))
        elif hours >= STUCK_AFTER_HOURS:
            stuck.append((age_d, sender, receiver, name, rel, hours))
        elif hours >= STALL_AFTER_HOURS:
            stalled.append((sender, receiver, name, rel, hours))
        elif hours >= ACK_AFTER_HOURS:
            missed.append((sender, receiver, name, rel, hours))

    alerted = eligible

    # (2b) PROACTIVE TIER — wake the receiving AGENT, not only Jordan.
    # Jordan 2026-09-20: "upgrade this cron job to be more proactive... I'm
    # starting to see DMs are going unanswered."
    #
    # Bounded on purpose: only past WAKE_AFTER_HOURS, only once per
    # WAKE_RENAG_HOURS per handoff, and hard-capped at WAKE_MAX_PER_RUN so a bad
    # sweep can never DM the whole fleet. Items already resolved or in-flight
    # never reach here — _outbound_items filtered them upstream.
    woken, wake_failed, wake_lines = [], [], []
    if not NO_WAKE:
        queue = [(a, s, r, n, rel, h) for a, s, r, n, rel, h in stuck]
        queue += [(0, s, r, n, rel, h) for s, r, n, rel, h in stalled]
        for _a, sender, receiver, name, rel, hours in queue:
            if len(woken) + len(wake_failed) >= WAKE_MAX_PER_RUN:
                break
            if hours < WAKE_AFTER_HOURS:
                continue
            if _cooled(rel, prev_woken, now, WAKE_RENAG_HOURS):
                continue
            ok, detail = wake_agent(receiver, sender, name, hours, dry_run=DRY_RUN)
            if ok:
                woken.append(rel)
                wake_lines.append(f"• [{sender}→{receiver}] {int(hours)}h — {name} — {detail}")
            else:
                wake_failed.append(rel)
                wake_lines.append(f"• [{sender}→{receiver}] {int(hours)}h — {name} — NOT woken: {detail}")
        if wake_lines:
            lines.append("")
            lines.append(f"📣 WOKE THE SEAT ({len(woken)} sent) — nudged the agent directly, no human needed:")
            lines.extend(wake_lines)

    # (2) DIAGNOSED / ASKED, NEVER ANSWERED. Narrow by design: measured markers
    #     are requests addressed to another party, not descriptions of work.
    if decision:
        lines.append("")
        lines.append(f"⏸ NEEDS DECISION ({len(decision)}) — diagnosed or asked, no reply:")
        for age_d, sender, receiver, name, rel, hours in decision[:MAX_STUCK_PER_RUN]:
            age = f"{age_d}d" if age_d else f"{int(hours)}h"
            lines.append(f"• [{sender}→{receiver}] {age} — {name}")
            lines.append(f"    {obsidian_link(rel)}")
        if len(decision) > MAX_STUCK_PER_RUN:
            lines.append(f"    …and {len(decision) - MAX_STUCK_PER_RUN} more")

    if missed:
        lines.append("")
        lines.append(f"⏳ NO ACK ({len(missed)}) — sent out, open >{ACK_AFTER_HOURS}h, nobody confirmed pickup:")
        for sender, receiver, name, rel, hours in missed[:MAX_STUCK_PER_RUN]:
            lines.append(f"• [{sender}→{receiver}] {int(hours)}h, no ack — {name}")
            lines.append(f"    {obsidian_link(rel)}")
        if len(missed) > MAX_STUCK_PER_RUN:
            lines.append(f"    …and {len(missed) - MAX_STUCK_PER_RUN} more")

    if stalled:
        lines.append("")
        lines.append(f"🆘 UNANSWERED ({len(stalled)}) — open >{STALL_AFTER_HOURS}h, no reply:")
        for sender, receiver, name, rel, hours in stalled[:MAX_STUCK_PER_RUN]:
            lines.append(f"• [{sender}→{receiver}] {int(hours)}h, no return — {name}")
            lines.append(f"    {obsidian_link(rel)}")
        if len(stalled) > MAX_STUCK_PER_RUN:
            lines.append(f"    …and {len(stalled) - MAX_STUCK_PER_RUN} more")

    if stuck:
        total = len(stuck)
        shown = stuck[:MAX_STUCK_PER_RUN]
        lines.append("")
        lines.append(f"🚩 STUCK ({total}) — open >{STUCK_AFTER_HOURS}h, no reply:")
        for age_d, sender, receiver, name, rel, hours in shown:
            lines.append(f"• [{sender}→{receiver}] {age_d}d — {name}")
            lines.append(f"    {obsidian_link(rel)}")
        if total > len(shown):
            lines.append(f"    …and {total - len(shown)} more (all now in cooldown — they will not repeat tomorrow's list)")

    # (5) TRUTH CHECK — handoff claims vs the vault brain (read-only).
    try:
        truth_all = verify_truth(cur_open)
    except Exception as e:
        print(f"truth-check error (non-fatal): {e}", file=sys.stderr)
        truth_all = []
    prev_truth = set(prev.get("truth_flags", []))
    new_truth = [(r, m) for r, m in truth_all if f"{r}|{m}" not in prev_truth]
    if new_truth:
        # Dedupe by the CLAIM, not the file. Two handoffs can report the same
        # underlying issue — found 2026-09-17: two KeeperHub notes both flagged
        # queue #1 as "shipped but the brain says PENDING", so one problem
        # occupied two lines. Same claim now prints once, with its sources.
        claims = {}
        for rel, msg in new_truth:
            claims.setdefault(msg, []).append(rel)
        lines.append("")
        lines.append(f"🔍 TRUTH CHECK ({len(claims)}) — handoff claims vs vault brain:")
        for msg, rels in sorted(claims.items())[:MAX_STUCK_PER_RUN]:
            lines.append(f"• {msg}")
            for rel in sorted(rels)[:2]:
                lines.append(f"    {rel.split('/')[-1]}")
                lines.append(f"      {obsidian_link(rel)}")
            if len(rels) > 2:
                lines.append(f"    (+{len(rels) - 2} more handoffs making the same claim)")

    # (6) EXPIRING — about to be auto-archived, so it can't vanish silently.
    # Seat-scoped for the same reason as FOR YOU: this used to iterate every open
    # note in the vault, so all four seats warned about HQ's notes (each line
    # literally tagged "[gentech]") and the section read as permanent noise.
    prev_expiring = set(prev.get("expiring", []))
    expiring_all = []
    for rel in sorted(cur_open_keys):
        g, name, path = cur_open[rel]
        if not _seat_owns_group(seat, g, own_lanes):
            continue          # not this seat's note — another seat's watcher reports it
        if is_standing_doc(name):
            continue          # a SOUL file is not a neglected handoff
        try:
            age_days = (datetime.datetime.now().timestamp() - os.path.getmtime(path)) / 86400
        except OSError:
            continue
        if age_days >= (ARCHIVE_AFTER_DAYS - WARN_BEFORE_ARCHIVE_DAYS):
            expiring_all.append((age_days, g, name, rel))
    new_expiring = [e for e in expiring_all if e[3] not in prev_expiring]
    if new_expiring:
        lines.append("")
        lines.append(f"⚠️ EXPIRING (archived in {WARN_BEFORE_ARCHIVE_DAYS}d if untouched):")
        for age_days, g, name, rel in new_expiring[:MAX_STUCK_PER_RUN]:
            lines.append(f"• [{g}] {int(ARCHIVE_AFTER_DAYS - age_days)}d left — {name}")
            lines.append(f"    {obsidian_link(rel)}")

    # Cooldown bookkeeping: keep existing stamps for still-open items, refresh
    # the ones we just alerted on. Closed items drop out.
    merged = {k: v for k, v in prev_nagged.items() if k in cur_open_keys and k not in alerted}
    merged.update({r: now.isoformat() for r in alerted})

    # Wake bookkeeping: same cooling rule, its own key space, so "we alerted
    # Jordan" and "we woke the agent" never suppress each other.
    merged_woken = {k: v for k, v in prev_woken.items() if k in cur_open_keys}
    merged_woken.update({r: now.isoformat() for r in woken})

    save_state({
        "open": sorted(cur_open_keys),
        "truth_flags": sorted(f"{r}|{m}" for r, m in truth_all),
        "cooldown": merged,
        "woken": merged_woken,
        # Pin first-seen only for handoffs still open; closed ones drop out so
        # the file cannot grow forever.
        "first_seen": {k: v for k, v in FIRST_SEEN.items() if k in cur_open_keys},
        "expiring": sorted(e[3] for e in expiring_all),
        "seat": seat,
    })

    if not lines:
        return 0
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
