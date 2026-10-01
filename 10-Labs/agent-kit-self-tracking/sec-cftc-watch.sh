#!/bin/bash
# sec-cftc-watch.sh — cron wrapper for the SEC/CFTC rulemaking watch.
#
# Jordan (Sep 16 2026): "stop this cron job... we pretty much know what's going on,
# we got the announcement yesterday. Now we should be tracking what the SEC and the
# CFTC are going to be doing as a result."
#
# With CLARITY dead (cloture failed 49-50, Sep 15 2026), the operative framework for
# the next 12-24 months is agency RULEMAKING: fast, narrow, reversible.
# Silent unless a source publishes something new (watermark dedup inside the script).
#
# ── UPGRADED Sep 18 2026 (Jordan) ────────────────────────────────────────────
#   "upgrade this ... to also look into how the new rules coming in benefit GenTech
#    or could benefit GenTech or what we should do as a result, you know, major
#    decisions we should make. So now the job also becomes the Fed Chair giving his
#    opinion on certain things and keeping a note for the Sunday meetings so we can
#    talk about everything collectively together."
#
# So the run is now TWO passes:
#   1. sec-cftc-watch.py      WHAT PUBLISHED — facts, watermarks, comment clocks.
#   2. regulatory-benefit.py  THE CHAIR'S READ — benefit, action, and the running note
#                             the Sunday council reads collectively.
#
# The second pass answers four questions per item in a fixed order — PERMISSION,
# RESTRICTION, DISCOVERABILITY, DECISION — and is allowed to conclude "this does not
# reach us". That verdict is the whole point: a clipping service can never give it,
# and a watcher that cannot say "irrelevant" trains its reader to skim.
#
# THE TEXT is fact. THE CHAIR is judgment and is labelled as judgment, always, on the
# same page. On-chain-data-is-king applies here too: a source that does not say which
# half it is gets ignored.
#
# The note is APPEND-ONLY and idempotent per (date, item), so Sunday sees the thread
# rather than the last message, and a re-run never doubles a section.
set -uo pipefail
D="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

# A wrapper that silently runs only ONE of its two passes is the exact bug this treasury keeps
# catching: a mechanism reporting success while doing half its job. regulatory-benefit.py was
# written but not enrolled, so pass 2 died on "No such file or directory" while the run still
# exited 0 from the caller's perspective. Check the scripts exist BEFORE claiming to run them.
for _f in sec-cftc-watch.py regulatory-benefit.py; do
  if [ ! -f "$D/$_f" ]; then
    echo "❌ SEC/CFTC WATCH — MISSING PASS SCRIPT: $D/$_f"
    echo "   This is an ENROLLMENT failure, not a market event. Fix sync-treasury-scripts.sh."
    exit 3
  fi
done

# ── ORDER MATTERS, AND IT IS A DELIVERY BUG, NOT A PREFERENCE ────────────────────────────────
# Jordan (2026-09-21): "upgrade this cron job to also include what's relevant for us and what's a
# benefit for us as these rulings come out."
#
# The read already existed (built Sep 18) and already ran — but it ran SECOND, and the combined
# output is ~13.5 KB against Telegram's ~4 KB limit. So the message was TRUNCATED and the Chair's
# read — the entire point of the upgrade — was the part cut off. Generated every weekday since
# Sep 18 and discarded at the message boundary, silently, with the run reporting ok.
#
# That is the treasury's signature failure again: a mechanism reporting success while the useful
# half never arrives. The fix is ordering plus a size discipline, not more content.
#
# The Chair's read goes FIRST because it is the decision surface. The technical pass follows.
# ── ORDER: the facts pass now RUNS first, but is PRINTED second. Both halves of that
# matter, and they are different requirements pulling opposite ways.
#
# PRINTING order stays as it was: the Chair's read is the decision surface, so it goes
# first and a truncation can never delete it.
#
# RUNNING order must be the reverse. Pass 2's coverage check (added 2026-09-24) asks
# "which items pass 1 flagged have no read here?" and reads pass 1's state file to answer.
# If pass 1 had not yet run, pass 2 would judge the PREVIOUS run's flagged list and could
# print "every flagged item has a read" about a run it has never seen — the coverage check
# itself becoming the false-value shape it was written to stop. So: run pass 1 into a
# buffer first, let pass 2 read THIS run's flags, then emit the buffer underneath.
_tmp="$(mktemp)"
trap 'rm -f "$_tmp"' EXIT
python3 "$D/sec-cftc-watch.py" > "$_tmp" 2>&1
rc=$?

echo "━━━ THE CHAIR'S READ — benefit, action, and what it means for us ━━━"
python3 "$D/regulatory-benefit.py"
rc2=$?

echo
echo "━━━ WHAT PUBLISHED (facts + comment clocks) ━━━"
cat "$_tmp"

exit $(( rc != 0 ? rc : rc2 ))
