#!/usr/bin/env python3
"""regulatory-benefit.py — the Chair's read: how a rule helps or hurts GenTech, and what to DO.

Jordan (2026-09-18): "upgrade this ... job to also look into how the new rules coming in benefit
GenTech or could benefit GenTech or what we should do as a result, you know, major decisions we
should make. So now the job also becomes the Fed Chair giving his opinion on certain things and
keeping a note for the Sunday meetings so we can talk about everything collectively together."

So the watcher stops being a clipping service. But an opinion is not a fact, and this treasury lives
by one rule now: NAME THE SOURCE. So every read below is split in two:

  THE TEXT      what the document actually says. Quotable. Verifiable. Never softened.
  THE CHAIR     judgment. Labelled as judgment. Written in the voice we already carry, and allowed
                to conclude "this does not matter to us" — which is the most useful verdict available
                and the one a clipping service can never give.

Four questions per item, in a fixed order, because the order is the discipline:
  1 PERMISSION      does it expand what we may do?
  2 RESTRICTION     does it contract what we may do?
  3 DISCOVERABILITY does it change who can find us, or who we can find?
  4 DECISION        does it force a choice we have not made?

Writes a running note the Sunday council reads. Never edits a position.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone

VAULT = "/root/vaults/gentech"
NOTE = os.path.join(VAULT, "Treasury/Strategy-Journal/regulatory-watch-notes.md")
STATE = "/root/.hermes/scripts/.regulatory-benefit-state.json"

# Pass 1's state file. Pass 2 reads it to find items the facts pass flagged that have NO
# read here — see uncovered() for why this link had to exist.
WATCH_STATE = "/root/.hermes/scripts/.sec-cftc-watch-state.json"

# ── what we actually are, so "benefit" means something concrete ──────────────
OUR_SHAPE = """
GenTech's regulated-touching surfaces, as they exist today:
  • an x402 services gateway selling 14 machine-payable endpoints (payTo 0x7ebff188…), published on
    Base (eip155:8453) and Solana
  • a treasury that provides concentrated liquidity on Avalanche (LFJ Joe v2.2 / Blackhole CL) and
    intends to extend to Solana and possibly Base
  • an agent that moves capital across rails and holds positions in tokens, some of which regulators
    may characterise as securities
  • NO registered entity, NO broker-dealer, NO FCM/IB/DCM relationship, and no current intent to
    acquire one
"""

# ── the four questions, applied as a fixed rubric ────────────────────────────
RUBRIC = [
    ("PERMISSION", "does it expand what we may do?"),
    ("RESTRICTION", "does it contract what we may do?"),
    ("DISCOVERABILITY", "who can find us — or whom can we find?"),
    ("DECISION", "does it force a choice we have not made?"),
]

# The one deadline we own. Declared once and computed, never retyped — the number was
# previously written into the prose as "32 days out" and was still saying 32 on a day it
# was 29. A countdown that is copied is a countdown that is wrong.
CLOSE_2026_17183 = "2026-10-20"

# ── THE DELIVERED-MESSAGE BUDGET ──────────────────────────────────────────────────────
# Telegram truncates at ~4,096 bytes and the injected script output is already ~10.5 KB
# (measured 2026-09-24: 10,512 bytes of context on the 2026-09-23 run), so the Chair block
# must not be allowed to grow without limit. Measured on 2026-09-22 the delivered read
# reached 4,961 bytes and the part cut off was the DECISION line for 2026-17183 —
# Regulation Crypto Assets, the ONE live deadline this treasury owns. This is the same
# failure the wrapper documents (the Chair's read generated every weekday and discarded at
# the message boundary), re-introduced by CONTENT GROWTH instead of by ORDERING.
#
# Adding the two reads owed on 2026-09-24 took this block from ~4.9 KB to 8.8 KB — over
# budget on its own. So the block is now rendered under a hard ceiling, and anything that
# does not fit is NAMED in the message rather than silently dropped. Trimming silently is
# the bug; trimming openly is a size discipline.
# WHICH BOUNDARY THIS IS, STATED SO THE NUMBER IS NOT SUPERSTITION. This block is INJECTED
# CONTEXT — the model's input — because the job runs with a script and no_agent=false; the
# DELIVERED message is the model's own reply, and the ~4 KB Telegram discipline applies
# THERE, by the agent composing it. So the ceiling here is not 4,096: it is a real guard
# against UNBOUNDED growth, set with room for the whole current board so that no live read
# is lost from the input.
#
# Current board, measured 2026-09-24: 2026-17183 874B, 2026-90 2061B, 9300-26 1219B,
# 2026-19512 2765B, 2026-19215 1886B — 8,809B total. 12,000 fits all five with headroom
# and still refuses to grow forever. When it does refuse, it NAMES what it dropped instead
# of trimming silently — that is the property that matters, because silent trimming is
# exactly how the 2026-09-22 DECISION line for Regulation Crypto Assets was lost.
CHAIR_BUDGET_BYTES = 12000


def _days_to(iso: str) -> int:
    """Days from today (UTC) to an ISO date. Recomputed every run, by construction."""
    from datetime import date
    return (date.fromisoformat(iso) - datetime.now(timezone.utc).date()).days


# Volatile numbers must not enter the fingerprint. The read legitimately says
# "29 days out" and that becomes "28 days out" tomorrow — hashing it raw would make
# every day a "new" read and re-append daily, which is the duplication bug wearing a
# different hat. Normalise countdowns to a placeholder; a changed VERDICT still changes
# the fingerprint, a ticking clock does not.
_VOLATILE = (
    (re.compile(r"\(\d+ days? out\)"), "(N days out)"),
    (re.compile(r"\b\d+ (?:days?|weeks?) out\b"), "N days out"),
)


def read_fingerprint(r: dict) -> str:
    """Stable content hash of one read: THE TEXT + THE CHAIR, countdowns normalised."""
    body = r["text"] + "|" + "|".join(f"{k}:{r['chair'].get(k,'')}" for k, _ in RUBRIC)
    for rx, repl in _VOLATILE:
        body = rx.sub(repl, body)
    return hashlib.sha1(body.encode()).hexdigest()[:16]


# ── hand-written reads for the items currently on the board ──────────────────
# Each entry is (id_fragment, THE TEXT, THE CHAIR). Kept here rather than generated, because a
# generated opinion about a legal document is a guess wearing a suit.
READS = {
    "2026-90": {
        # CORRECTED 2026-09-22. This field is THE TEXT — declared to be quotable, verifiable
        # fact. It previously read "effective immediately, 5-year term, conditional and
        # SELF-CERTIFIED". "Self-certified" appears NOWHERE in the order (Release No. 34-106402,
        # File No. 4-927), nowhere in the SEC press release, and nowhere in Chairman Atkins'
        # statement — 0 hits in all three, checked against the primary text. It is a real term of
        # art (356 Federal Register hits) but it belongs to SRO rule filings effective ON FILING,
        # which is NOT this instrument. A fabricated legal mechanism in the fact field is worse
        # than a missing one, because it is the half a reader will quote. Replaced with the
        # mechanism the order actually states.
        "text": (
            "SEC exemptive order (Release No. 34-106402, File No. 4-927) + request for comment. "
            "Temporary and conditional, not self-certifying: the exemptions run from 2026-09-17 "
            "to 2031-09-17 (five years). Permits PERMISSIONED trading of TOKENIZED NMS STOCK on a "
            "Tokenized Securities Venue, and grants dealers relief for providing liquidity in "
            "tokenized NMS stock. Conditions include: a TSV must publish a Notice on its public "
            "website at least 30 days before operating and email the Commission within one "
            "business day; it must disclose its AMM pool smart contract addresses and publish "
            "transaction data in machine-readable form within ten minutes. It is an exemption, "
            "not a rule."
        ),
        "chair": {
            "PERMISSION": (
                "Real but narrow. It legitimises AMM liquidity provision in tokenised EQUITIES. We do "
                "not LP equities and have no plan to, so the permission does not reach us today."
            ),
            "RESTRICTION": (
                "None on our current activity. The conditions bind whoever uses the exemption, and "
                "we are not among them."
            ),
            "DISCOVERABILITY": (
                "THIS is the part that matters, and the corrected TEXT makes it STRONGER, not "
                "weaker. The order does not merely condition relief on publishing pool addresses: "
                "it requires a TSV to publish a standing Notice on its own website, to email the "
                "Commission within one business day, to disclose the smart contract addresses of "
                "its AMM pools, and to publish transaction data in machine-readable form within ten "
                "minutes. A requirement to publish, notify and keep current is structurally a "
                "REGISTRY — and a registry is a place to be listed. Every gap we have hit this week "
                "(CDP Bazaar 12-of-14 invisible, ClawCredit's partner registry, LFJ's three decoy "
                "pools) was a discoverability failure. A mandated public venue registry for "
                "tokenised assets is the most interesting thing in this document and it is not what "
                "the headline says."
            ),
            "DECISION": (
                "None today. Watch for the published pool address list, and treat it as a template: "
                "if regulators make venue registries the norm, being IN the registry is worth more "
                "than being good in it."
            ),
        },
    },
    "9300-26": {
        "text": (
            "CFTC staff no-action position for providers of PASSIVE SOFTWARE facilitating trading "
            "with registered FCMs, IBs and DCMs. Lowest tier of relief — staff-level, withdrawable. "
            "The release mentions crypto, digital asset, virtual currency and bitcoin ZERO times."
        ),
        "chair": {
            "PERMISSION": (
                "As written: nothing for us. It relieves software sitting between a user and a "
                "REGISTERED intermediary, and we have no such relationship."
            ),
            "RESTRICTION": (
                "None. A no-action position relieves; it does not bind third parties."
            ),
            "DISCOVERABILITY": (
                "Indirectly, and this is the honest read: the CFTC has now drawn a staff-level line "
                "around what counts as PASSIVE software — software that does not exercise discretion. "
                "An agent that decides where capital goes is not passive software. That distinction "
                "was implicit; it is now on paper, and it describes us from the wrong side."
            ),
            "DECISION": (
                "Worth one deliberate note for the council: as we add autonomy, we move FURTHER from "
                "the 'passive software' safe harbour, not closer to it. That is not a reason to stop "
                "building — it is a reason to be able to describe, precisely, what our agent decides "
                "and what it merely routes. Keep that description current."
            ),
        },
    },
    # ── 2026-19512 — written 2026-09-24 to close a coverage debt. This item was FLAGGED
    # relevant by pass 1 and had NO read here, so it printed with no verdict at all. The
    # fact field below is quoted from the primary text (FR Doc 2026-19512, 91 FR 60670,
    # Release No. 34-106443 / File No. SR-COIN-2026-001), not from the title.
    "2026-19512": {
        "text": (
            "SEC Notice of Filing of a Proposed Rule Change (NOT a rule, NOT effective): Coinbase "
            "Derivatives, LLC, Release No. 34-106443 / File No. SR-COIN-2026-001, published "
            "2026-09-24, 91 FR 60670. Filed 2026-09-18 under Exchange Act Section 19(b)(2); the "
            "Commission published it to solicit comments, but CDE itself 'has not solicited, and "
            "does not intend to solicit, comments' and the notice states NO comment-close date. "
            "Substance: proposed CDE Rulebook Chapter 12, customer margin for security futures. "
            "Rule 1215(b) sets initial/maintenance margin subject to SEC Rule 242.403 and CFTC "
            "Reg. 41.45 (not less than 15% of contract market value). Rule 1215(c) limits "
            "acceptable margin assets to cash, margin securities, exempted securities and other "
            "assets permitted under Regulation T / CFTC 41.46 / SEC 242.404. Rule 1215(e) requires "
            "a net-capital deduction for an undermargined account and liquidation where there is a "
            "liquidating deficit. CDE is already a registered DCM with the CFTC and registered with "
            "the SEC as a national securities exchange for security futures on 2026-09-01 via Form "
            "1-N (acknowledged 2026-09-08, Release No. 106295). Commission action due within 45 "
            "days of publication, extendable to 90."
        ),
        "chair": {
            "PERMISSION": (
                "None for us. Nothing here expands what GenTech may do; it governs the margin "
                "regime of a registered exchange's clearing members."
            ),
            "RESTRICTION": (
                "None on us, and this is now VERIFIABLE rather than assumed: the primary text "
                "contains the words 'crypto', 'digital asset', 'virtual currency', 'bitcoin' and "
                "'tokeniz' ZERO times, and the acceptable-margin list (Rule 1215(c)) is cash, "
                "margin securities, exempted securities and Regulation T assets. Self-custodied "
                "on-chain LP positions appear nowhere in it. We are not a Participant Firm, a "
                "Clearing Firm or a securities futures intermediary, so Rule 1215's obligations "
                "have no addressee in us."
            ),
            "DISCOVERABILITY": (
                "Real, and the same signal as 2026-19407. A crypto-native exchange is building the "
                "FULL listed-product perimeter - registration, listing standards, and now the "
                "customer margin regime - and getting a margin rule that is 'substantially "
                "identical to CME Rule 930.B.2.c'. That is the tell worth recording: the crypto "
                "venue is adopting the INCUMBENT's rulebook verbatim rather than arguing for a new "
                "one. It is also the second consecutive Coinbase Derivatives filing on the same "
                "file number family (SR-COIN-2026-001 today, SR-COIN-2026-002 on 2026-09-23), "
                "which is a venue assembling a rulebook chapter by chapter. If venue registries "
                "become the norm, this is who will be in them."
            ),
            "DECISION": (
                "None. NO treasury action, zero position impact. Recorded rather than silently "
                "dropped because it was flagged and previously read as nothing."
            ),
        },
    },
    # ── 2026-19215 — written 2026-09-24 to close a coverage debt (same reason).
    "2026-19215": {
        "text": (
            "SEC Notice: Acknowledgement of Receipt of Notice of Registration as a National "
            "Securities Exchange Pursuant to Section 6(g) of the Securities Exchange Act of 1934, "
            "by North American Derivatives Exchange, Inc. ('Nadex'), Release No. 34-106396 / File "
            "No. 10-255, published 2026-09-21, 91 FR 59823. Nadex filed Form 1-N on 2026-09-14; "
            "under Section 6(g)(2)(B) the registration becomes effective CONTEMPORANEOUSLY with "
            "submission of the notice, and the Commission is acknowledging receipt rather than "
            "granting anything. This is an acknowledgement notice, not a rule, not a proposal, "
            "and it carries no comment window."
        ),
        "chair": {
            "PERMISSION": (
                "None for us. It records a status change for one exchange, not a permission we "
                "can use."
            ),
            "RESTRICTION": (
                "None. Section 6(g) registration binds Nadex; we are not an exchange and the "
                "route is only open to a CFTC-designated contract market."
            ),
            "DISCOVERABILITY": (
                "This is the one that completes the pattern, and it corrects our own carry note. "
                "The Section 6(g) route is NARROW ON PURPOSE: an exchange that lists or trades "
                "SECURITY FUTURES PRODUCTS may register as a national securities exchange SOLELY "
                "for the purpose of trading them, provided it is a CFTC-designated contract "
                "market. So the occupants assembling around the SEC's 2026-90 tokenised-equity "
                "registry are arriving through a specific door - security futures on "
                "CFTC-designated venues - not through general crypto venue registration. Nadex, "
                "Coinbase Derivatives, Bitnomial, Kalshi: all four are DCMs with a security-futures "
                "angle. Worth being precise about, because 'crypto exchanges are registering as "
                "national securities exchanges' is now the wrong description of what we are "
                "watching, and a wrong description in a carry note is how a thread quietly goes off "
                "course."
            ),
            "DECISION": (
                "None. NO treasury action. The correction above is the deliverable."
            ),
        },
    },
    "2026-17183": {
        "text": (
            "SEC proposed rule, Regulation Crypto Assets, published 2026-08-21. Comment window CLOSES "
            "2026-10-20. This is the live one."
        ),
        "chair": {
            "PERMISSION": "Unknown in detail — the proposal is long and we have not read it end to end. Said plainly.",
            "RESTRICTION": (
                "Potential: it addresses which crypto assets are securities and what obligations "
                "attach. Our treasury holds tokens that could be characterised either way."
            ),
            "DISCOVERABILITY": "Not directly.",
            "DECISION": (
                "This is the one item on the board with a real deadline that we control: comments "
                f"close {CLOSE_2026_17183} ({_days_to(CLOSE_2026_17183)} days out). Two honest options — (a) read it properly and decide "
                f"whether GenTech has a comment worth filing, or (b) record a deliberate decision NOT "
                f"to, and stop carrying it as open. What we should not do is let the date pass and "
                f"pretend we decided. Bring to Sunday."
            ),
        },
    },
}


def uncovered(hot=None, state_path=None, board=None, max_age_seconds=3600):
    """Items pass 1 flagged that this pass has NO read for, newest first.

    WHY THIS EXISTS (defect found 2026-09-24, at the source of the job's whole point).
    The two passes never spoke. Pass 1 discovers a CHANGING set of relevance-flagged
    documents; pass 2 renders a FIXED board, named in its own READS dict, and printed it
    as if that were the whole read. Measured on the live 2026-09-24 board: pass 1 flagged
    five items (SEC 2026-19512 Coinbase Derivatives security-futures customer margin;
    2026-19407 / 19408 / 19409 the three crypto-venue SRO filings; 2026-19215 Nadex's
    Section 6(g) registration acknowledgement) and pass 2 said nothing at all about any of
    them, because it has exactly three reads and no coverage check.

    That is this treasury's signature failure one level up from the bug class it keeps
    catching: a mechanism reporting success while doing PART of its job, with output that
    looks short, confident and complete. And it is the worst place for it, because the
    question this pass exists to answer is 'how does this benefit or bind GenTech' — an
    item with no read gets NO verdict, and an ABSENCE was being rendered as silence rather
    than as an absence.

    A missing read is NOT the allowed verdict 'this does not reach us'. The allowed verdict
    is a WRITTEN judgment with a reason. Until there is one, the item is OWED a read, and
    that debt is what this function makes visible.
    """
    # THE AUTHORITY IS THE RENDERED BOARD, NOT THE READS DICT. A read that exists in
    # READS but is not passed to render() reaches the reader not at all — so keying
    # coverage on READS would report an item as covered while nothing about it was
    # printed, which is the same false pass this function exists to stop, one level in.
    # Measured while writing this: adding a read without adding it to the board flipped
    # the coverage line from "5 owed" to a clean pass with 5 items still unprinted.
    # TWO DIFFERENT QUESTIONS, and conflating them produces a false report either way:
    #   Q1 (here)      does a READ EXIST for this item?  -> the debt. An absent read is
    #                  an absence, not the verdict "does not reach us".
    #   Q2 (render)    did that read REACH the message? -> the budget. Reported by the
    #                  trim block, which NAMES what did not fit.
    # Keying Q1 on the printed list made a read that merely did not fit look like an
    # unwritten one — a false debt report. Keying Q1 on READS alone let a read be written
    # and never requested. So Q1 uses READS, and board_integrity() below catches the
    # written-but-never-requested case, which is the one READS alone cannot see.
    if board is None:
        board = None  # None -> fall back to READS (Q1: does a read EXIST?)
    if hot is None:
        # ABSENT, UNREADABLE and STALE are all UNKNOWN — none of them is "all covered".
        # A missing key must NOT collapse to an empty list: [] would render as the PASS
        # line "every item has a read", which is this job's signature false-value shape
        # wearing the coverage check's clothes. Measured risk: pass 1 writes last_hot only
        # after this patch ships, so the first run after deploy has no key at all — without
        # this guard that run would have printed a clean, confident, UNVERIFIED pass.
        try:
            with open(state_path or WATCH_STATE) as f:
                raw = json.load(f)
        except Exception:
            return None
        if "last_hot" not in raw:
            return None
        try:
            age = (datetime.now(timezone.utc)
                   - datetime.fromisoformat(raw.get("last_hot_run", ""))).total_seconds()
        except Exception:
            return None
        if age > max_age_seconds:
            return None  # stale list: we would be judging a run that is not this one
        hot = raw.get("last_hot") or []
    out = []
    for i in hot or []:
        iid = i.get("id") or ""
        if board is not None:
            covered = any(k in iid for k in board)
        else:
            covered = any(k in iid for k in READS)
        if not covered:
            out.append(i)
    return out


def board_integrity(board=None, reads=None):
    """Reads that EXIST but were never requested — a read written and never shown.

    The other half of the coverage question, and the half a READS-keyed check cannot see:
    render() only prints fragments it is ASKED for, so a read sitting in READS while
    missing from main()'s board reaches nobody and no debt line would ever mention it.
    Returns the orphaned fragments, or None if it cannot tell.
    """
    reads = READS if reads is None else reads
    if board is None:
        board = REQUESTED_BOARD
        if not board:
            return None  # nothing requested yet: cannot distinguish orphan from not-yet
    return [f for f in reads if f not in board]


# What render() was ASKED for this run. Set by main(). DELIBERATELY the requested list,
# NOT the printed list: a read that was requested and then trimmed for budget is covered
# (it exists, and the trim block names it), whereas a read never requested is an ORPHAN.
# Storing the printed list here would make a budget trim look like an orphaned read.
REQUESTED_BOARD = []


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:
        return {"noted": []}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f, indent=2)
    os.replace(tmp, STATE)


def render(items, budget=None):
    """Produce the Chair's read block for the given id fragments.

    ORDER IS THE DECISION SURFACE, NOT A PREFERENCE. Measured 2026-09-22: the rendered
    block reached 4,961 bytes against Telegram's ~4,096-byte limit, and the part silently
    cut off was the DECISION line for 2026-17183 — Regulation Crypto Assets, the ONE live
    deadline this treasury owns and the item the note says to bring to Sunday. That is the
    exact truncation failure the wrapper already documents, re-introduced by content growth
    rather than by ordering. Two defensive moves, both kept: the item carrying the only
    live deadline is rendered FIRST (so a truncation can never delete it), and the text is
    kept inside the budget. Ordering makes truncation survivable; brevity makes it rare.
    """
    lines = []
    dropped = []
    for frag in items:
        r = READS.get(frag)
        if not r:
            continue
        block = [f"\n**{frag} — THE TEXT**", f"  {r['text']}", f"\n**{frag} — THE CHAIR**"]
        for key, _q in RUBRIC:
            v = r["chair"].get(key)
            if v:
                block.append(f"  {key}: {v}")
        if budget and len("\n".join(lines + block).encode()) > budget:
            dropped.append(frag)
            continue
        lines.extend(block)
    if dropped:
        lines.append("")
        lines.append(f"  ⚠️ {len(dropped)} read(s) DID NOT FIT this message and are NOT shown:")
        lines.append(f"     {', '.join(dropped)}")
        lines.append(f"     They are in the running note: {NOTE}")
        lines.append("     Nothing was dropped from the note — only from this message.")
    return "\n".join(lines), [f for f in items if READS.get(f) and f not in dropped]


def append_note(items):
    """Append a dated section to the running Sunday note. Idempotent per (date, item)."""
    st = load_state()
    os.makedirs(os.path.dirname(NOTE), exist_ok=True)
    if not os.path.exists(NOTE):
        with open(NOTE, "w") as f:
            f.write("# Regulatory Watch — the Chair's notes for the Sunday council\n\n"
                    "Fed-Chair voice. **THE TEXT is fact; THE CHAIR is judgment and is labelled so.**\n"
                    "This file accumulates so Sunday has the whole thread rather than the last message.\n\n"
                    f"## What we are, for the purpose of judging benefit\n{OUR_SHAPE}\n")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    added = []
    with open(NOTE, "a") as f:
        for frag in items:
            r = READS.get(frag)
            if not r:
                continue
            # Key on CONTENT, not on (date, frag). THE BUG THIS FIXES, measured on the
            # live note: the old key was f"{today}:{frag}", and main() passes a HARDCODED
            # list, so every new run-day re-appended the same three static reads. On
            # 2026-09-21 the 2026-90 / 9300-26 / 2026-17183 sections were appended a
            # SECOND time, byte-identical to 2026-09-18 (verified by section diff). The
            # note doubled in length and gained zero information — the same false-value
            # shape as a watcher that prints stale items. Content-addressing means a
            # genuinely UPDATED read still appends (a new day count, a changed verdict),
            # while an unchanged one is silently recognised as already on the page.
            key = f"{frag}:{read_fingerprint(r)}"
            if key in st["noted"]:
                continue
            f.write(f"\n---\n\n## {today} — {frag}\n\n**THE TEXT**\n\n{r['text']}\n\n**THE CHAIR**\n\n")
            for k, q in RUBRIC:
                v = r["chair"].get(k)
                if v:
                    f.write(f"- **{k}** ({q}) — {v}\n")
            st["noted"].append(key)
            added.append(frag)

        # the standing question for the room — written ONCE per day, and only on a day
        # that actually appended something. WHY: this write used to sit outside the
        # `added` check, so a run that appended nothing still stamped a fresh Carry
        # block. Measured on the live file: the same three reads were appended verbatim
        # on 2026-09-18 AND 2026-09-21 (byte-identical THE TEXT + THE CHAIR, verified by
        # comparing the sections), doubling the note without adding one new fact. A note
        # that repeats itself is the same failure as a watcher that prints stale items:
        # it trains the reader to skim. Idempotency now means per ITEM, not per day.
        if added:
            f.write(f"\n### Carry to Sunday\n"
                f"- **SEC 2026-90:** watch for the published pool-address registry; being IN a "
                f"registry beats being good outside one.\n"
                f"- **Regulation Crypto Assets (comments close 2026-10-20):** decide to comment or "
                f"decide not to — do not let the date pass undecided.\n"
                f"- **Passive-software line:** as we add autonomy we move away from that safe harbour. "
                f"Keep an accurate written description of what the agent decides vs merely routes.\n")
    save_state(st)
    return added


def main():
    print("=" * 100)
    print("  THE CHAIR'S READ — benefit and action, not just what published")
    print("=" * 100)
    print("\n  THE TEXT is what the document says. THE CHAIR is judgment, labelled as judgment.")
    print("  A verdict of 'this does not reach us' is a real verdict and is allowed here.\n")
    # The two items below were owed a read (flagged by pass 1, no verdict here). Adding
    # them is the closing of that debt; the coverage line is what proves it closed.
    board = ["2026-17183", "2026-90", "9300-26", "2026-19512", "2026-19215"]
    # REQUESTED_BOARD is the REQUESTED list (see its definition): render() reports what it
    # actually printed so the trim is stated, but coverage and orphan checks compare against
    # what was asked for, not against what survived the budget.
    REQUESTED_BOARD[:] = board
    body, printed = render(board, budget=CHAIR_BUDGET_BYTES)
    print(body)

    # ── THE COVERAGE LINE. Without it a short list reads as a complete one. ───────────
    debt = uncovered()
    if debt is None:
        print("\n  UNCOVERED CHECK: UNAVAILABLE — pass 1's flagged list is missing, unreadable,")
        print("  or stale, so we CANNOT say whether anything flagged has no read. This read is")
        print("  therefore UNVERIFIED, not clean. (Pass 1 runs first in the wrapper so this")
        print("  should be rare — if you see it, the facts pass did not write its state.)")
    elif debt:
        print(f"\n  ⚠️ FLAGGED WITH NO CHAIR READ YET ({len(debt)}) — these have NO verdict,")
        print("     which is not the same as the verdict 'does not reach us':")
        for i in debt:
            print(f"     [{i.get('agency')} · {i.get('type')}] {i.get('date')} "
                  f"{i.get('id','').replace('fr:','')}")
            print(f"       {(i.get('title') or '')[:120]}")
        print("     OWED: a written PERMISSION/RESTRICTION/DISCOVERABILITY/DECISION read.")
    else:
        print("\n  UNCOVERED CHECK: every item pass 1 flagged this run has a read on this board.")
    # The other half: a read that EXISTS but was never requested reaches nobody.
    orphan = board_integrity()
    if orphan:
        print(f"\n  ⚠️ READ EXISTS BUT WAS NEVER RENDERED ({len(orphan)}): {', '.join(orphan)}")
        print("     Written in this file but absent from the board main() renders, so it")
        print("     would reach nobody and no debt line would mention it.")

    added = append_note(board)
    print(f"\n  running note : {NOTE}")
    # ── THIS LINE USED TO LIE, AND IT LIED ON EVERY QUIET DAY (found 2026-09-28) ─────
    # It printed "(already noted today — idempotent)" whenever `added` was empty. But
    # `added` is empty for TWO different reasons, and only one of them is idempotency:
    #   (a) every read on the board is ALREADY on the note  -> idempotent, nothing to do
    #   (b) NO read on the board has ever been noted        -> nothing was appended at all
    # Case (b) is the normal quiet day, and it read as (a). Measured on the live file
    # 2026-09-28: the message said "already noted today" while the note's newest section
    # was headed 2026-09-25 — three days earlier — and the benefit state held ZERO keys
    # starting "2026-09-28". A reader (and the Sunday council, which consumes this note)
    # is told the note is current when it has not been touched. That is a false statement
    # in the one field whose whole job is to say whether the record moved, and it is the
    # same family as the watcher that reported success while doing half its job.
    # Fix: distinguish the two cases by asking the note and the state, not by the
    # emptiness of `added`. Report the newest section date actually on the page.
    _newest = None
    try:
        with open(NOTE) as _f:
            for _ln in _f:
                if _ln.startswith("## "):
                    _newest = _ln[3:].strip()
    except Exception:
        _newest = None
    if added:
        print(f"  appended now : {added}")
    else:
        print(f"  appended now : nothing (no read on the board changed since it was last "
              f"written)")
        print(f"  newest note section : {_newest or 'UNREADABLE — could not read the note'}")
    print("\n" + "=" * 100)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
