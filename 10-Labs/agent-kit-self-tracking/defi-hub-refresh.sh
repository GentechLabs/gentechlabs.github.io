#!/bin/sh
# defi-hub-refresh.sh — keep the DeFi hub following the chain, on a schedule. (Jordan, 2026-09-23)
#
# THE GAP THIS CLOSES:
#   Jordan watches the hub and said he now allows "a little bit of grace because it's moving
#   as I'm looking at it and I have to wait 10 minutes for it to update." Checking: the hub
#   was on NO cron at all. It regenerated only when a human ran it. The data file was 26
#   minutes old at the time of the check, and could be hours old in principle.
#   So the grace he was granting was not 10 minutes -- it was unbounded. A display that only
#   refreshes when someone remembers is the same defect as every other one found that day:
#   the screen reporting a state nobody re-read.
#
# The watchdog and leaderboard run every 15 minutes; neither regenerates the hub. This does,
# so the page follows the chain at the same cadence as the machinery that moves it.
#
# SILENT ON SUCCESS (stdout is delivered verbatim): refreshing a page is not news.
# NON-ZERO ON FAILURE so the cron raises an error alert -- a hub that stops refreshing is
# a silent staleness, which is exactly what this exists to prevent.
set -u
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── PICK AN INTERPRETER THAT CAN ACTUALLY READ THE CHAIN (2026-09-30) ─────────────────────────
# `python3` on PATH resolves to the interpreter HERMES BUNDLES for its own tools
# (/root/.hermes/tools/python-3.14.7+…/bin/python3). On 2026-09-30 a Hermes update replaced that
# interpreter with a build that has NO web3 — and every chain read in the hub data build runs
# IN-PROCESS under this interpreter. Result: `data["error"] = "ModuleNotFoundError: No module
# named 'web3'"` was written into the PUBLIC payload for both tenants, and the page rendered a raw
# Python traceback line to any visitor for 21 consecutive refresh runs.
# So we now ASK the interpreter to prove it can import web3, and take the first that can. Verified
# working candidates in order: PATH python3 (only if it passes), /usr/bin/python3 (3.12, has it),
# the Hermes agent venv (has it). Falls back to bare python3 so the failure mode is unchanged.
PY_BIN=""
for _c in python3 /usr/bin/python3 /usr/local/lib/hermes-agent/venv/bin/python3; do
    if command -v "$_c" >/dev/null 2>&1 && "$_c" -c "import web3" >/dev/null 2>&1; then
        PY_BIN="$_c"; break
    fi
done
[ -n "$PY_BIN" ] || PY_BIN="python3"

# ── THE ENVELOPE WAS 88–97% CONSUMED ON A GOOD RUN (fixed 2026-09-28) ──────────────────────────
# This was `timeout 280`. Measured durations of SUCCESSFUL runs of this job: 246s, 252s, 252s,
# 261s, 265s, 266s, 272s — against a 280s cap. The job only ever passed by finishing first, with no
# margin at all, so a normal variance (or the memory pressure of 2026-09-28, when it took 281s and
# was killed) turned straight into a user-visible stale page. It failed with a bare rc=124 and no
# useful output, because the graceful degradation INSIDE defi_hub_data.py (`COLLECT_TIMEOUT`) sat at
# a hardcoded 300s — ABOVE this envelope — so it could never run. Two guards, and the outer one
# always won.
#
# Widened to 600s: long enough that the inner 240s collector timeout is reachable and can degrade one
# tenant instead of the whole page. Precedent that this is safe — the execution ring already shows a
# sibling treasury job completing at 668s, so nothing is enforcing 280s. Cadence is 10 minutes, so a
# 600s ceiling still cannot overlap the next tick.
OUT="$(timeout 600 "$PY_BIN" "$SCRIPTS_DIR/defi_hub_data.py" 2>&1)"
RC=$?

# ── RECORD THE PRICE WE JUST PUBLISHED (Jordan, 2026-09-23) ─────────────────────
# `recent_tape()` needs to know whether the market is STILL moving, and the hub did not keep any
# history: it rewrites one JSON in place and never commits it (verified: zero commits touch it).
# So the tape is recorded here, at the page's own cadence. This is what lets the machine tell a
# FINISHED move from a live one -- the difference between a curve and a wide bid-ask mid-band.
"$PY_BIN" - "$SCRIPTS_DIR" <<'PYEOF' 2>/dev/null || true
import json, sys, time, os
sd = sys.argv[1]
src = "/var/www/gentechlabs/DeFi/defi-data-jordan.json"
tp = os.path.join(sd, ".price-tape.json")
try:
    p = json.load(open(src)).get("price_usd")
    if not p:
        raise ValueError("no price")
    tape = []
    try:
        tape = json.load(open(tp))
        if not isinstance(tape, list):
            tape = []
    except Exception:
        tape = []
    tape.append({"t": int(time.time()), "p": float(p)})
    json.dump(tape[-4000:], open(tp, "w"))
except Exception:
    pass
PYEOF

if [ $RC -ne 0 ]; then
    echo "⚠️ defi-hub-refresh: hub regeneration FAILED (rc=$RC) — the page is going stale"
    echo "$OUT" | tail -6
    exit 1
fi

# ── THE FRONT DOOR (added 2026-09-28) ──────────────────────────────────────────────────────────
# `gentechlabs.net/DeFi/` returned HTTP 403 — no index file existed, so the entry point to the whole
# surface was a permissions error and the hubs were reachable only by exact filename. Rebuilt right
# after the hubs, in the SAME job, so it can never show a stale list of books: it reads the registry
# and each tenant's payload at the moment the hubs were just written.
#
# Not fatal on failure: a missing index is a worse front door, not a broken hub. The hub pages are
# already published by this point, so report it and continue.
IDX_OUT="$(timeout 300 "$PY_BIN" "$SCRIPTS_DIR/defi_hub_index.py" 2>&1)"
IDX_RC=$?
if [ "$IDX_RC" -ne 0 ]; then
    echo "⚠️  defi-hub-refresh: the FRONT DOOR failed to build (rc=$IDX_RC) — /DeFi/ may 403"
    echo "$IDX_OUT" | tail -5
else
    echo "$IDX_OUT" | tail -3
fi

# ── OWNERSHIP OF THE PUBLISHED FILES (moved here 2026-09-28) ────────────────────────────────────
# These files are written by root but SERVED by nginx as www-data. Nothing else set their ownership:
# this was living in the yield-leaderboard wrapper, which is exactly the kind of load-bearing line
# that gets lost when a duplicated step is consolidated — and losing it means the page 403s while
# every script still reports success.
#
# The refresh now owns the hub end to end (generate -> publish -> permissions), which is the job
# whose entire purpose this is. Verified: neither this script nor defi_hub_data.py set perms before,
# so removing it from the leaderboard without moving it here would have broken the public page.
chown www-data:www-data /var/www/gentechlabs/DeFi/*.html /var/www/gentechlabs/DeFi/*.json 2>/dev/null || true
chmod 644 /var/www/gentechlabs/DeFi/*.html /var/www/gentechlabs/DeFi/*.json 2>/dev/null || true

# ── POSTURE — COMPUTED HERE, READ BY THE WATCHDOG (2026-09-26) ──────────────────────────────────
# The Watchdog runs EVERY 5 MINUTES and has to finish inside that budget, but a full posture pass
# costs ~42s per tenant — too slow to put inline (it would double every watchdog pass and risk the
# next tick overlapping).
#
# So the expensive read happens here, on the 10-minute hub cadence that already does the per-tenant
# sweep, and the watchdog just READS the cached decision. Two properties matter:
#   * the watchdog stays fast and still sees ALL SIX LAYERS, which is the point — today's churn was
#     invisible exactly because no single place recorded what every layer read;
#   * the cache carries its own TIMESTAMP, and the watchdog refuses a stale one rather than
#     treating an old healthy posture as a current one (a stale "fine" is the false-value family).
for _t in jordan dadrian; do
    [ -f "/var/www/gentechlabs/DeFi/defi-data-$_t.json" ] || continue
    # ── ATOMIC WRITE (fixed 2026-09-28) ────────────────────────────────────────────────────────
    # This used a bare `> "$SCRIPTS_DIR/.posture-$_t.json"`. A shell redirect TRUNCATES the target
    # to 0 bytes BEFORE the command runs — so for the whole ~42s posture pass the cache sat EMPTY
    # on disk, while the 5-minute watchdog was reading it. Every read landing in that window died
    # with `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` and the pass reported
    #   "⚠️ POSTURE UNREADABLE for dadrian — JSONDecodeError".
    # Measured: jordan's cache was caught at exactly 0 bytes mid-sweep. The failure was
    # intermittent because the window is ~42s in every 10 minutes (~7% of reads) — the worst kind
    # of bug, one that looks like a flaky chain read and is actually our own file handling.
    #
    # Write to a temp file, then `mv` it into place. Rename within one filesystem is atomic, so a
    # reader sees either the complete OLD cache or the complete NEW one — never a partial file.
    # (`defi_hub_data.py` already does exactly this for the pages; this is the same fix, one site
    # over, which is why it was missed.)
    # ── SWEEP STALE TEMPS FIRST (2026-09-28) ──────────────────────────────────────────────────
    # The atomic write below is correct, but its cleanup only runs on a NORMAL exit. When this is
    # SIGKILLed — a cron worker reaped, an OOM, a gateway restart — the temp file is orphaned
    # forever. Measured: `.posture-dadrian.json.tmp.2405506` survived exactly that way.
    # A leak that only happens on abnormal termination is never cleaned by the path that writes it,
    # so the sweep has to live at the START of the next run, not in a trap.
    find "$SCRIPTS_DIR" -maxdepth 1 -name '.posture-*.json.tmp.*' -mmin +5 -delete 2>/dev/null
    _tmp="$SCRIPTS_DIR/.posture-$_t.json.tmp.$$"
    if STEWARD_TENANT="$_t" timeout 150 "$PY_BIN" "$SCRIPTS_DIR/posture.py" \
         --tenant "$_t" --json > "$_tmp" 2>/dev/null && [ -s "$_tmp" ]; then
        mv -f "$_tmp" "$SCRIPTS_DIR/.posture-$_t.json"
    else
        # `[ -s ]` matters: a command can exit 0 and still emit NOTHING, and an empty file is
        # indistinguishable from a failed read. Never publish one as a posture.
        rm -f "$_tmp"
        _err="$SCRIPTS_DIR/.posture-$_t.json.tmp.$$"
        printf '{"tenant":"%s","error":"posture pass failed"}\n' "$_t" > "$_err"
        mv -f "$_err" "$SCRIPTS_DIR/.posture-$_t.json"
    fi
done

# ── REFRESH THE SHARED STATE OF RECORD (added 2026-09-28) ─────────────────────────────────────
# THE GAP: `treasury-state.json` is read by EVERY Steward cron before it speaks or acts, and
# NOTHING on a schedule refreshed it. It was written only when a human ran it, or by the WEEKLY
# council — so its capital block drifted for days. `test_steward_consistency.py` caught exactly
# that: state said deployed $193.91 (a 00:37 snapshot) while the pages said $43.99, Δ+$149.92
# against a ±$3.88 tolerance. The guard was right; the record was stale. A consistency check that
# only ever passes on Sunday is not a check, it is a weekly coincidence.
#
# Wired HERE because this job already holds the fresh chain read at the hub's cadence, so the two
# can no longer disagree: whichever tick moves the pages also moves the record they are checked
# against. Measured 63s, against a 600s envelope that this job uses ~250-270s of.
#
# NON-FATAL BY DESIGN for the page, FATAL for the job: refresh_state_capital.py exits 1 when it
# cannot get a trustworthy read, and its message matches the sweep below on purpose. A stale state
# of record is a real failure — every cron trusts it — so this alerts rather than passing quietly.
if [ -f "$SCRIPTS_DIR/refresh_state_capital.py" ]; then
    _rsc="$(timeout 180 "$PY_BIN" "$SCRIPTS_DIR/refresh_state_capital.py" 2>&1)"
    _rsc_rc=$?
    if [ "$_rsc_rc" -ne 0 ]; then
        echo "⚠️ defi-hub-refresh: state of record refresh failed (rc=$_rsc_rc)"
        echo "$_rsc" | tail -4
    fi
fi

# a partial sweep is also a failure: some tenant's page would silently keep old data
if echo "$OUT" | grep -qiE "traceback|error|unreadable|failed"; then
    echo "⚠️ defi-hub-refresh: regeneration reported a problem — a page may be stale"
    echo "$OUT" | tail -8
    exit 1
fi

exit 0
