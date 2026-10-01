#!/bin/bash
# steward-watchdog.sh — TENANT-AWARE, SILENCE-COMPLIANT position watchdog.
#
# ── WHY THIS WAS REBUILT (2026-09-22) ────────────────────────────────────────────────────────
#
# 1. IT ONLY KNEW ONE PERSON. The venue probe below hardcoded Jordan's wallet, and the re-center
#    ran for that wallet alone. So when Dadrian entered the same pool, NOTHING watched him: his
#    position drifted 27 bins out of range and sat earning zero while this job happily reported
#    on someone else. A fleet watchdog that names one wallet is not a watchdog — it is a personal
#    assistant with a group chat.
#
# 2. IT SPOKE EVERY TEN MINUTES. It exec'd lfj_recenter.py and delivered its stdout verbatim.
#    lfj_recenter ALWAYS prints a full report, so the comment "silent when healthy" was simply
#    false: the job posted ~144 messages a day whether or not anything had happened. That is not
#    monitoring, it is noise — and noise is how a real alert gets scrolled past.
#
# ── THE RULE THIS NOW FOLLOWS (silence doctrine Sep 3; quiet overnight Sep 22) ───────────────
#    Quiet unless something CHANGED. Alert ONCE. Suppress until it RESOLVES. Re-arm on success.
#    Speak only for: an action taken, a material condition, or an error. Never for "still fine".
#
#    THE WATCHER ALWAYS RUNS. Only the MESSAGE is gated. (Jordan, 2026-09-26: "when I wanted
#    things to be quiet in the chat, I still want the watcher to run... I just didn't want
#    [notifications] popping up left and right.") Nothing below skips a sample, a re-center or a
#    safety check — every branch here decides only whether to POST, never whether to LOOK.
#
#    Overnight (04:00-10:59 UTC) the bar is higher, and it was previously described here as
#    "only ACTIONS and ERRORS speak" — which the code did NOT do, and the mismatch is what let
#    the noise through. The real rule, corrected 2026-09-23 and made true on 2026-09-26:
#      ERROR or MATERIAL  -> speaks ALWAYS, overnight included. A broken book at 3am is news.
#      ADVISORY / ACTION  -> daylight only. True, but not worth waking anyone for.
#    MATERIAL means the book is BROKEN or the money is NOT WORKING (IDLE CAPITAL, OUT OF RANGE,
#    DRIFTED, REBALANCE NOW, flat book). ADVISORY is a standing quality note about a book that IS
#    working (LOW FEE EFFICIENCY, THIN MARGIN, LOW FOR N MIN). Everything carries a ⚠️, so a
#    blanket ⚠️ test cannot tell them apart — it made every advisory MATERIAL and the overnight
#    gate therefore gated nothing.
#
# Each tenant runs in its OWN process with its OWN environment, so one tenant's numbers can
# never be reported as another's.
set -uo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── ACTION LOG (2026-09-30) ─────────────────────────────────────────────────────────────────────
# Wired at the CALLER, not inside lfj_recenter.py. Two reasons, both deliberate:
#   1. lfj_recenter.py is 2230 lines of live money path; the caller is where the DECISION is made,
#      so this is where `decided_by` is actually known.
#   2. It is fail-soft by construction -- if the log is unwritable the trade still happens. Proven:
#      the helper returns 0 on an unwritable path.
# WHY IT EXISTS: on 2026-09-30 this watchdog rebuilt the book at 4am and moved money with no record
# of having done it. The engine could not say what it did. Reconstructed from the chain, tx by tx.
_slog_intent() {   # _slog_intent <verb> <reason>  -> prints the event id (may be empty)
    # `timeout 5` is deliberate: AUDIT FINDING (kimi-k2.7-code, 2026-09-30) -- a synchronous python
    # spawn sits BETWEEN the decision and the trade. If the log call hangs, it delays the very money
    # path it exists to describe. A log that can stall a trade is worse than no log.
    timeout 5 python3 "$SCRIPTS_DIR/steward_action_log.py" log-intent \
        --actor watchdog --verb "$1" --decided-by machine --reason "$2" \
        --provenance "TREASURY-CONSTITUTION.md Part 3A" \
        --chain avalanche --venue lfj-v22 2>/dev/null || echo ""
}

_slog_result() {   # _slog_result <id> <verb> <reason> <rc> <output>
    [ -z "$1" ] && return 0
    # AUDIT FINDING: `[ "$4" -ne 0 ]` with an empty/non-numeric $4 throws to stderr instead of
    # deciding. Compare against the literal "0" instead -- anything not exactly 0 is a failure.
    _st="ok"; [ "$4" = "0" ] || _st="failed"
    _final=1
    # 124 = `timeout` killed it. It reached NO VERDICT, so the intent must stay open in gaps():
    # a transaction may still be settling, and treating that as closed is the false negative the
    # audit found. Explicit, never inferred.
    [ "$4" = "124" ] && _final=0
    # Pull the on-chain receipts straight out of the run's own output -- never a paraphrase.
    # They are CLAIMED receipts (grep'd from stdout), and the log marks them verified:false.
    _txs=""
    for _h in $(printf '%s' "$5" | grep -oE '0x[a-fA-F0-9]{64}' | sort -u | head -8); do
        _txs="$_txs --tx $_h"
    done
    timeout 5 python3 "$SCRIPTS_DIR/steward_action_log.py" log-result \
        --id "$1" --status "$_st" --final "$_final" $_txs 2>/dev/null || true
}

cd "$SCRIPTS_DIR" || exit 0
STATE="$SCRIPTS_DIR/.watchdog-silence.json"
# ── THE RESCUE CIRCUIT BREAKER (2026-09-27) ──────────────────────────────────────────────────────
# Overridable for the same reason REGISTRY is: a breaker that can only point at the live file cannot
# be tested, and an untested trip is not a trip.
BREAKER="${BREAKER:-$SCRIPTS_DIR/.watchdog-breaker.json}"
# Overridable so the monitor can be TESTED against a corrupt/empty registry. A path that can
# only ever point at the live file is untestable, and an untested failure branch is not a branch
# (fixed 2026-09-23 — the first attempt to prove #7 ran the real tenants instead).
REGISTRY="${REGISTRY:-/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json}"

HOUR_UTC="$(date -u +%H)"
OVERNIGHT=0
if [ "$HOUR_UTC" -ge 4 ] && [ "$HOUR_UTC" -le 10 ]; then OVERNIGHT=1; fi

# ── who are we watching? the REGISTRY, not a hardcoded address ────────────────
# ── A REGISTRY WE CANNOT READ IS NOT AN EMPTY REGISTRY (fixed 2026-09-23, Sr audit) ──────
# This used to `raise SystemExit` inside `2>/dev/null`, so a corrupt or missing tenants.json
# produced ZERO rows — and zero rows meant "nobody active, say nothing". Every tenant silently
# unmonitored, no error, and it looks exactly like a legitimately empty registry. A monitor that
# cannot report its own blindness is not a monitor. Distinguish the two cases explicitly.
REG_OUT="$(python3 - "$REGISTRY" <<'PY'
import json, sys
try:
    reg = json.load(open(sys.argv[1]))
except Exception as e:
    print(f"REGISTRY_UNREADABLE\t{type(e).__name__}: {e}")
    raise SystemExit(0)
for n, t in (reg.get("tenants") or {}).items():
    if t.get("status") == "ACTIVE" and t.get("wallet"):
        print(f"{n}\t{t['wallet']}")
PY
)"

if printf '%s' "$REG_OUT" | grep -q '^REGISTRY_UNREADABLE'; then
    echo "⚠️  OUT OF RANGE — the tenant registry cannot be read; EVERY tenant is unmonitored."
    echo "    $(printf '%s' "$REG_OUT" | grep '^REGISTRY_UNREADABLE' | cut -f2-)"
    echo "    ($REGISTRY)"
    exit 1        # non-zero: this is an error, not a quiet no-op
fi

mapfile -t ROWS <<< "$REG_OUT"

[ "${#ROWS[@]}" -eq 0 ] && exit 0        # a VALID, empty registry — nobody active, say nothing

for row in "${ROWS[@]}"; do
    TENANT="${row%%$'\t'*}"
    WALLET="${row##*$'\t'}"
    [ -z "$TENANT" ] && continue

    # ── THE POSTURE VOTE (2026-09-26) ─────────────────────────────────────────────────────────
    # posture.py reads ALL SIX LAYERS for this tenant and emits ONE posture, naming the layer that
    # set it. It is ADVISORY — it does not yet drive the deploy, because changing what the machine
    # DOES to a live book is a deliberate step, not a side effect of adding a monitor.
    #
    # It is here for two reasons:
    #   1. THE LOG now records all six layers, not just the ones lfj_recenter happens to print.
    #      Today's churn was invisible precisely because no single place said what every layer read.
    #   2. A DISAGREEMENT between the posture and what the book actually holds is a MATERIAL
    #      condition. That is the shape bug of 2026-09-26: the layers called one way, the book sat
    #      the other, and nothing said so. Now something does.
    # A layer that cannot be read ABSTAINS (posture.py refuses to vote on a missing value), and an
    # unreadable posture must never read as agreement — so a failure here sets POSTURE_ERR.
    #
    # READ FROM CACHE, NOT COMPUTED. A full posture pass costs ~42s per tenant, which is too much
    # to add inline to a 5-minute job for two tenants. defi-hub-refresh.sh computes it on the
    # 10-minute cadence and writes .posture-<tenant>.json; this only parses it. The cache is
    # REJECTED when missing, unparseable, or older than POSTURE_MAX_AGE — a stale "fine" is the
    # same false-value family as everything else in this file.
    POSTURE_ERR=0; POSTURE=""; POSTURE_LINE=""
    POSTURE_MAX_AGE=2400          # 40 min: comfortably past the 10-min writer, so a missed cycle
                                  # is tolerated, but a dead writer cannot masquerade as healthy
    POSTURE_LINE="$(python3 - "$SCRIPTS_DIR/.posture-$TENANT.json" "$POSTURE_MAX_AGE" \
                        "$TENANT" 2>/dev/null <<'PY'
import json, os, sys, time
p, max_age, tenant = sys.argv[1], float(sys.argv[2]), sys.argv[3]
try:
    if not os.path.exists(p):
        print("POSTURE-UNREADABLE no cache at %s" % p); raise SystemExit
    age = time.time() - os.path.getmtime(p)
    if age > max_age:
        print("POSTURE-UNREADABLE cache is %.0f min old (max %.0f)"
              % (age / 60.0, max_age / 60.0)); raise SystemExit
    # ── SAY WHAT IS ACTUALLY WRONG (fixed 2026-09-28) ──────────────────────────────────────────
    # This used to surface only `type(e).__name__`, so a truncated cache printed
    #   "POSTURE UNREADABLE for dadrian — JSONDecodeError"
    # — naming the exception and nothing about the CAUSE. It cost a hunt to find that the cause was
    # our OWN writer: defi-hub-refresh.sh used a bare `>` redirect, which truncates the file to 0
    # bytes BEFORE python runs, so the cache sat empty for the whole ~42s posture pass while the
    # 5-minute watchdog was reading it. The reader now distinguishes EMPTY from CORRUPT from
    # MISSING, so the next person gets the diagnosis instead of a mystery.
    _sz = os.path.getsize(p)
    if _sz == 0:
        print("POSTURE-UNREADABLE cache is 0 bytes — the writer truncated it and has not "
              "finished (non-atomic write). Writer now renames into place; this read hit the "
              "old window."); raise SystemExit
    try:
        d = json.load(open(p))
    except json.JSONDecodeError as je:
        print("POSTURE-UNREADABLE cache is not valid JSON (%d bytes): %s at line %d col %d"
              % (_sz, je.msg, je.lineno, je.colno)); raise SystemExit
    if d.get("error"):
        print("POSTURE-UNREADABLE %s" % d["error"]); raise SystemExit
    dec = d.get("decision") or {}
    if d.get("tenant") != tenant:
        print("POSTURE-UNREADABLE cache is for %r, not %r" % (d.get("tenant"), tenant))
        raise SystemExit
    post, by = dec.get("posture"), dec.get("set_by")
    if not post:
        print("POSTURE-UNREADABLE no posture in the cached decision"); raise SystemExit
    ab = dec.get("abstained") or []
    line = "POSTURE %s (set by %s, %.0f min old)" % (post, by, age / 60.0)
    if ab:
        line += " | ABSTAINED: %s" % ",".join(ab)
    print(line)
except SystemExit:
    pass
except Exception as e:
    print("POSTURE-UNREADABLE %s" % type(e).__name__)
PY
)"
    case "$POSTURE_LINE" in
        POSTURE-UNREADABLE*) POSTURE_ERR=1 ;;
        POSTURE\ *)          POSTURE="${POSTURE_LINE#POSTURE }" ;;
        *)                   POSTURE_ERR=1 ;;
    esac
    if [ "$POSTURE_ERR" -eq 1 ]; then
        echo "⚠️  POSTURE UNREADABLE for $TENANT — ${POSTURE_LINE#POSTURE-UNREADABLE }"
        echo "    An unreadable posture is NOT agreement: it is an unknown, and an unknown layer"
        echo "    must never be read as a healthy one."
    else
        echo "    $POSTURE_LINE"
    fi


    # ── TILT comes from the REGIME, not a hardcoded number (Jordan, 2026-09-22) ──────
    # "we'll add a scenario for when we move up". The up-scenario is only real if the
    # down-scenario is its mirror: rally = AVAX-heavy (ride it), downtrend = USDC-heavy
    # (dry powder for the dip). steward_rebalance.REGIME_TILT is the one place that
    # mapping lives, and lfj_recenter is the one place the ratio is consumed.
    RATIO="$(python3 - <<'PY' 2>/dev/null
import sys
sys.path.insert(0, "/root/.hermes/profiles/gentech-treasury/scripts")
try:
    from steward_rebalance import read_regime, tilt_for
    r = read_regime() or {}
    print(f"{tilt_for(r.get('regime'))}")
except Exception:
    # ── AN UNREADABLE REGIME MUST BE VISIBLE (fixed 2026-09-23, Sr audit) ────────────────
    # This printed a bare 0.45 and called it "neutral: never silently inherit a directional
    # tilt" — but 0.45 IS a tilt (it is HIGH_VOLATILITY's value in the tilt map), so the
    # comment described the opposite of what the code did. A reader could not tell a healthy
    # high-volatility read from a total failure to read the regime at all: they produce the
    # SAME number. Say UNREADABLE and let the caller mark it, so the fallback is auditable.
    print("UNREADABLE")
PY
)"
    # 0.45 remains the fail-to-neutral VALUE (never inherit a directional lean), but an
    # unreadable regime is now flagged so it cannot masquerade as a normal reading.
    REGIME_ERR=0
    case "$RATIO" in
        UNREADABLE)               REGIME_ERR=1; RATIO="0.45" ;;
        ''|*[!0-9.]*)             REGIME_ERR=1; RATIO="0.45" ;;
    esac
    if [ "$REGIME_ERR" -eq 1 ]; then
        echo "⚠️  REGIME UNREADABLE — falling back to the neutral 0.45 tilt for $TENANT."
        echo "    A missing regime is not a directional signal; it is an unknown."
    fi

    # ── OUTER TIMEOUT MUST OUTLAST THE INNER ONES (fixed 2026-09-23, Sr audit) ──────────────
    # This was `timeout 300`, but lfj_recenter.py allows 420s for the swap AND 420s for the
    # withdraw AND 420s for the deploy — so a normal-slow pass was SIGTERM'd mid-flight. If the
    # kill lands after WITHDRAW succeeded and before RE-DEPLOY finished, the capital is OUT of the
    # pool and nothing re-enters it (see the gate fix below). The churn fix makes long passes
    # rarer; this makes them survivable.
    # ── IS THIS A CHASE, OR A CASCADE? (Jordan, 2026-09-23) ──────────────────────
    # Jordan's rule: "if we're breaking down and it's going faster than we had hoped -- why not
    # exit the pool and convert to the stable coin and wait it out? And once we get a little bit
    # more stable, come back with a curve."
    # SPEED, not depth, decides. His own fall measured -8.83%/day = 0.3 sigma/hour: a GRIND, which
    # a bid-ask eats, and the guard says FARM. A -5%/hour move is 4.6 sigma/hour and no approved
    # band (25 or 45 bins -- 45 is his ceiling) can hold it.
    # This GATES the chase, because re-centering INTO a cascade is the one action guaranteed to
    # lose: you pay the swap and the gas to place a band the price is about to leave again.
    # It does NOT auto-exit the capital -- that is a bigger action than a cron should take on a
    # new, uncalibrated instrument. It suppresses the chase and SPEAKS the proposal instead.
    # A guard that cannot yet measure (no samples) returns UNKNOWN and gates nothing: safe rollout.
    CASCADE=0
    CG="$(STEWARD_TENANT="$TENANT" timeout 260 python3 "$SCRIPTS_DIR/cascade_guard.py" \
            --tenant "$TENANT" 2>&1)"
    if echo "$CG" | grep -qE "VERDICT[[:space:]]+CASCADE"; then
        CASCADE=1
        MATERIAL=1
        echo "$CG" | grep -E "price|speed|band|VERDICT" | sed 's/^/    /'
        echo "  🌀 CASCADE -- NOT chasing. No approved band holds a 3-sigma hour."
        echo "     Proposed: withdraw -> all USDC -> wait -> re-enter as a CURVE when the 2-day move < 4%."
    fi

    # ── A RESCUE IS NEVER SILENT (2026-09-27) ─────────────────────────────────────────────────
    # `RESCUED` MUST be initialised BEFORE the branch, not inside it: this script runs `set -u`, and
    # on the CASCADE path the retry block is never reached — so an unbound $RESCUED here would abort
    # the whole pass. (Caught by checking the else-branch, not by reading the if-branch.)
    RESCUED=0
    # A SECOND FLAG, because "I did not rescue" has TWO MEANINGS (caught before shipping):
    #   - the breaker SKIPPED the attempt (condition still present, breaker open), and
    #   - there was nothing to rescue at all (condition resolved).
    # With one flag, the SKIP path would fall into the RE-ARM branch below, clear the counter it
    # had just tripped, and attempt again next pass — an attempt/attempt/skip cycle that looks
    # like a working breaker and caps nothing. Same family as every other bug fixed today: a
    # FALSE VALUE read as "no condition" when it actually meant "condition unchanged".
    BREAKER_TRIPPED=0

    if [ "$CASCADE" -eq 0 ]; then
    _LREASON="watchdog: book needs a rebuild (ratio $RATIO)"
    _LID="$(_slog_intent recenter "$_LREASON")"
    OUT="$(STEWARD_TENANT="$TENANT" STEWARD_WALLET="$WALLET" \
           timeout 1000 python3 "$SCRIPTS_DIR/lfj_recenter.py" --ratio "$RATIO" --execute --yes 2>&1)"
    RC=$?
    _slog_result "$_LID" recenter "$_LREASON" "$RC" "$OUT"

    # ── THE RESCUE RETRY (Jordan, 2026-09-27) ─────────────────────────────────────────────────
    # Jordan: "I would like it to be able to make these decisions."
    #
    # lfj_recenter has a --rescue flag whose stated purpose is EXACTLY this case — its own header:
    # "IT CANNOT BLOCK A RESCUE ... A genuine emergency — a book stranded out of the pool with the
    # capital idle — is worse than a thin gas balance, and the reserve exists precisely to pay for
    # repairing that." The flag existed and NOTHING reached for it (zero occurrences in this file),
    # so on 2026-09-27 the machine refused a live book that was earning nothing, over ~$0.007 it was
    # never going to spend, and asked a human to top up a wallet that did not need it.
    #
    # THREE CONDITIONS, ALL REQUIRED. This is the difference between a rescue and an override:
    #   1. the refusal was the GAS FLOOR specifically (not a cascade, an unreadable chain, a bad
    #      ratio, a simulation failure — those are all still hard refusals);
    #   2. the book is genuinely STRANDED or IDLE — out of range, flat, or earning nothing. A book
    #      that is in range and collecting is NOT rescued: there "hold and top up" is correct, and
    #      rescuing would spend the repair reserve on a book that did not need repairing;
    #   3. the action is a re-center/re-entry (which is what --rescue is documented to cover).
    # Anything else falls through with the original refusal intact, so the flag cannot become a
    # general-purpose bypass of the floor.
    if echo "$OUT" | grep -qE "REFUSING TO START|REFUSING TO RE-ENTER" \
       && echo "$OUT" | grep -qiE "spend the gas floor|gas floor|CANNOT SHOW THE CYCLE" \
       && echo "$OUT" | grep -qiE "OUT OF RANGE|flat book|earning nothing|nothing in the book is earning"; then
        # ── THE CIRCUIT BREAKER (2026-09-27) ─────────────────────────────────────────────────
        # Measured: this block attempted a rescue EVERY 10 MINUTES FOR OVER TWO HOURS — 23 runs
        # between 04:49 and 07:12 UTC — on a book it could never repair, re-deriving a conclusion
        # it already had. There was no cap of any kind.
        #
        # The key is the CONDITION (WHY it refused), never the incident. A key that is unique by
        # construction can never match its predecessor — the same defect the alert signature had.
        if echo "$OUT" | grep -qiE "CANNOT FINISH THE CYCLE|CANNOT SHOW THE CYCLE CAN BE FINISHED"; then
            BKEY="CANNOT_FINISH"
        elif echo "$OUT" | grep -qiE "UNREADABLE|RPC"; then
            BKEY="UNREADABLE"
        else
            BKEY="FLOOR"
        fi
        BVERDICT="$(python3 "$SCRIPTS_DIR/watchdog_breaker.py" --state "$BREAKER" \
                      --tenant "$TENANT" --key "$BKEY" check 2>/dev/null)"
        if [ "${BVERDICT%% *}" = "SKIP" ]; then
            RESCUED=0; BREAKER_TRIPPED=1
            echo "  ⏸ RESCUE SKIPPED — circuit breaker OPEN (${BVERDICT#SKIP })."
            echo "    This refusal has already been attempted the maximum number of times and it"
            echo "    cannot succeed until the wallet is funded. Not retrying: a rescue that cannot"
            echo "    work is not progress, it is RPC and gas estimation burned every 10 minutes."
            echo "    The breaker RE-ARMS ITSELF the moment a pass refuses to refuse."
            # A tripped breaker is NOT left silent. Suppressing the retry must not look like
            # "everything is fine" — the book is still stranded and a human still needs to know.
            # It reports once (the SPEAK/SIG dedupe upstream handles the repeats).
            MATERIAL=1
            OUT="$OUT

⏸ CIRCUIT BREAKER OPEN — the rescue was NOT retried this pass.
   The book is still in the state above and a wallet top-up is what clears it.
   Not retrying is deliberate: the attempt cannot succeed until then."
        else
        echo "  ↻ GAS FLOOR blocked a book that is genuinely STRANDED — retrying with --rescue."
        echo "    (the reserve exists to pay for repairing exactly this; holding would leave the"
        echo "     capital idle and earning nothing, which is the worse state)"
        _LREASON="watchdog: GAS FLOOR blocked a STRANDED book -- retrying with --rescue"
        _LID="$(_slog_intent rescue "$_LREASON")"
        OUT="$(STEWARD_TENANT="$TENANT" STEWARD_WALLET="$WALLET" \
               timeout 1000 python3 "$SCRIPTS_DIR/lfj_recenter.py" --ratio "$RATIO" --rescue \
               --execute --yes 2>&1)"
        RC=$?
        _slog_result "$_LID" rescue "$_LREASON" "$RC" "$OUT"
        RESCUED=1
        # Record the REFUSAL, not the attempt. Only a rescue that reached a verdict counts.
        if echo "$OUT" | grep -qiE "REFUSING TO START|CANNOT FINISH THE CYCLE"; then
            ATT="$(python3 "$SCRIPTS_DIR/watchdog_breaker.py" --state "$BREAKER" \
                     --tenant "$TENANT" --key "$BKEY" refused 2>/dev/null)"
            echo "  ⏱ ${ATT:-attempt recorded} — the breaker trips after ${BREAKER_MAX_ATTEMPTS:-2}."
        fi
        fi
    fi
    else
        OUT="CASCADE -- chase suppressed by cascade_guard (see above)"; RC=0
    fi

    # ── RE-ARM THE BREAKER (2026-09-27) ───────────────────────────────────────────────────────
    # A breaker you must reset by hand is a breaker that stays tripped. Any pass that did NOT
    # reach a refusal means the condition is gone — the wallet was topped up, the book recovered,
    # the chain came back. So the entry is cleared and the breaker is live again on the very next
    # pass. No human action, no reset command, nothing to remember.
    if [ "$RESCUED" -eq 0 ] && [ "$BREAKER_TRIPPED" -eq 0 ]; then
        REARM="$(python3 "$SCRIPTS_DIR/watchdog_breaker.py" --state "$BREAKER" \
                   --tenant "$TENANT" clear 2>/dev/null)"
        case "$REARM" in
            *"after"*) echo "  ✔ CIRCUIT BREAKER RE-ARMED — $REARM." ;;
        esac
    fi

    # ── classify what happened ────────────────────────────────────────────────
    ACTIONED=0; ERROR=0; MATERIAL=0; ADVISORY=0
    [ $RC -ne 0 ] && ERROR=1
    echo "$OUT" | grep -qE "SUCCESS  block=|CURVE LIVE|SENT [0-9a-f]{16}" && ACTIONED=1
    # ── MATERIAL vs ADVISORY (split 2026-09-26 — Jordan: "I don't know what's going on... as far
    #    as notifications popping up left and right, I just didn't want that to happen") ───────
    # The old test was `... |REBALANCE NOW|⚠️" && MATERIAL=1` — a BLANKET ⚠️. Every advisory in the
    # tree carries a ⚠️, so LOW FEE EFFICIENCY, THIN MARGIN, SHORT and PARTIAL were all promoted to
    # MATERIAL and therefore all bypassed the overnight gate. Measured overnight 06:00-10:37: the
    # watchdog SPOKE on 20 of 26 runs. A rule that reads "quiet overnight unless material" and
    # treats everything as material is quiet never.
    # MATERIAL = the book is BROKEN or the money is NOT WORKING. These never wait, even at 3am.
    echo "$OUT" | grep -qE "IDLE CAPITAL|DRIFTED|OUT OF RANGE|REBALANCE NOW|flat book" && MATERIAL=1
    # ── AN OPERATOR HOLD IS NOT "IDLE CAPITAL" (2026-09-28) ──────────────────────────────────────
    # `lfj_recenter` prints "⚠️ IDLE CAPITAL" on every flat pass, including a DELIBERATE flat book,
    # and the line above promotes that to MATERIAL — which bypasses the overnight gate. So a hold
    # would have woken Jordan every 5 minutes all night to tell him about a decision HE made.
    # A held book is by definition not broken and the money is not idle by accident; it is parked
    # on purpose. Demote it, and let the hold itself (which he set) be the record.
    if echo "$OUT" | grep -qE "OPERATOR HOLD — NOT RE-ENTERING"; then
        MATERIAL=0
        ADVISORY=0
    fi
    # ADVISORY = true, but a standing quality note about a book that IS working. Worth saying
    # once, in daylight. Never a reason to wake anyone.
    echo "$OUT" | grep -qE "⚠️" && ADVISORY=1
    # ── A RESCUE IS NEVER SILENT (2026-09-27) ─────────────────────────────────────────────────
    # Spending the repair reserve on purpose is a decision a human must be able to see, even when
    # it WORKED. It is reported as MATERIAL so it never waits for morning: the whole reason the
    # reserve exists is a book that was earning nothing, and "we fixed it quietly" would leave
    # nobody able to tell a rescue from a wallet quietly draining its floor.
    if [ "$RESCUED" -eq 1 ]; then
        MATERIAL=1
        # ── DID THE RESCUE ACTUALLY SPEND ANYTHING? (fixed 2026-09-27) ────────────────────────
        # This block used to assert "The repair reserve WAS SPENT to put the capital back to
        # work" whenever --rescue had been INVOKED — without checking whether the rescue did
        # anything at all. The first live pass after the affordability fix proved that wrong: the
        # run invoked --rescue, the gate correctly REFUSED before the withdraw (affordability is
        # physics), and this block still printed "the reserve was spent" and reported RESCUE USED
        # as MATERIAL. Nonce and balance were unchanged — not one wei moved.
        # It is a false receipt, the same family as everything else fixed today: a confident
        # statement about a state that did not occur. It matters here more than usual, because
        # "topped up soon? good" and "top up soon, you are below the floor" are opposite actions,
        # and a human reading this log cannot tell them apart. A rescue that was ATTEMPTED and
        # REFUSED is a different fact from a rescue that SPENT, and both must be stated.
        if echo "$OUT" | grep -qiE "REFUSING TO START|CANNOT FINISH THE CYCLE"; then
            ACTIONED=0; MATERIAL=1; ERROR=1
            echo "  ⚑ RESCUE ATTEMPTED — the gas floor was overridden, but NOTHING WAS SPENT."
            echo "    The gate refused before the withdraw (affordability is not overridable by"
            echo "    --rescue), so the position is UNCHANGED and the reserve is INTACT."
            echo "    Below the floor still — top up so the next repair can proceed."
        else
            ACTIONED=1
            echo "  ⚑ RESCUE USED — the gas floor was overridden because the book was stranded."
            echo "    The repair reserve was spent to put the capital back to work. Top up soon so the"
            echo "    NEXT repair is still affordable; if rescues recur, the floor or the float is wrong."
        fi
    fi
    echo "$OUT" | grep -qiE "traceback|unreadable|refus" && ERROR=1

    # ── THE POSTURE/BOOK COMPARISON WAS REMOVED, ON PURPOSE (2026-09-26) ──────────────────────
    # I first shipped a check here comparing the posture's shape against the shape lfj_recenter
    # built. It produced a FALSE MATERIAL ALARM ON EVERY QUIET PASS, and I caught it in the
    # assembled run rather than in a unit test. Two independent reasons it cannot work as written:
    #   1. On a pass where nothing is deployed, the deploy line ("BID-ASK LIVE …") is never printed,
    #      so the grep found nothing and reported a disagreement that did not exist.
    #   2. The two sides answer DIFFERENT QUESTIONS. The posture resolves shape with PROTECTION
    #      first (a macro event forces bid-ask), while lfj_recenter derives shape from the market
    #      read ALONE. So during a macro day they differ BY DESIGN — and a check that fires on
    #      correct behaviour is not a guard, it is noise. This file's own doctrine: "noise is how
    #      the one real alert gets scrolled past."
    # A false alarm is worse than no alarm, so the check is gone rather than left in and muted.
    # The posture is still LOGGED for every tenant above, which is the honest half and the half
    # that makes today's churn visible. A real comparison needs the posture to actually DRIVE the
    # shape choice (so both sides read one source) — that is the "make it an actor" step, and it is
    # a deliberate decision, not a monitor.
    # An unreadable posture has NOT cleared anything: it is an unknown, so it must be able to speak.
    [ "$POSTURE_ERR" -eq 1 ] && ERROR=1

    # ── should we speak? ──────────────────────────────────────────────────────
    # FIXED 2026-09-23 — THE OVERNIGHT GATE WAS ON THE WRONG CATEGORY.
    # Jordan's rule (2026-09-22): "quiet overnight" means NO GROUP MESSAGES IN THE SMALL HOURS
    # **UNLESS MATERIAL**. The old test spoke for a routine ACTION at 3am and stayed SILENT for
    # a MATERIAL condition — exactly backwards:
    #     elif [ $MATERIAL -eq 1 ] && [ $OVERNIGHT -eq 0 ]; then   # material waits for morning
    #     if   [ $ERROR -eq 1 ] || [ $ACTIONED -eq 1 ]; then       # a routine re-center does not
    # A re-center that worked is the LEAST urgent thing that can happen; a book that is FLAT
    # or OUT OF RANGE is the MOST. So: errors and material conditions never wait, and a routine
    # action is what waits for morning.
    SPEAK=0
    if [ $ERROR -eq 1 ] || [ $MATERIAL -eq 1 ]; then
        SPEAK=1                                  # never wait: an error or a material condition
    elif [ $ADVISORY -eq 1 ] && [ $OVERNIGHT -eq 0 ]; then
        SPEAK=1                                  # a standing advisory is daylight news only
    elif [ $ACTIONED -eq 1 ] && [ $OVERNIGHT -eq 0 ]; then
        SPEAK=1                                  # routine action — worth saying, but not at 3am
    fi

    # ── dedupe: alert ONCE, suppress until it resolves ────────────────────────
    # ── EVERY ERROR CLASS NEEDS A SIGNATURE (fixed 2026-09-23, Sr audit) ─────────────────
    # SIG came from a five-token allowlist. An error whose line matched none of them (e.g.
    # "legs UNREADABLE", a traceback) produced an EMPTY SIG, so the `[ -n "$SIG" ]` dedupe test
    # below failed and the same error re-spoke on EVERY pass forever — and the empty string
    # written to state re-armed it each time. Noise is how the one real alert gets scrolled past,
    # which is this script's own stated doctrine. Error-class tokens are now included, and any
    # error with no signature at all still gets one, so it can dedupe like everything else.
    # ── AND THE SIGNATURE ITSELF MUST NOT BE VOLATILE (fixed 2026-09-26) ──────────────────
    # `SENT [0-9a-f]{16}` captured the ACTUAL TX HASH, so the same standing condition produced a
    # DIFFERENT signature on every run that actioned anything: "IDLE CAPITAL|SENT b956db87cb601b94"
    # then "IDLE CAPITAL|SENT d6279a69fb466c12". The dedupe compares signatures for EQUALITY, so a
    # signature that is unique by construction can never match its predecessor and can never
    # suppress anything — a dedupe that cannot dedupe, reported as working. Measured overnight
    # 06:00-10:37: dadrian's book was IDLE from 06:02 to 08:24 and the watchdog spoke on 20 of 26
    # runs, once per pass, on one unchanging condition. Hashes and counts are MASKED to stable
    # tokens; the signature must describe the CONDITION, never the incident.
    SIG="$(printf '%s' "$OUT" | grep -oE "DRIFTED [0-9]+ bins|IDLE CAPITAL|OUT OF RANGE|REBALANCE NOW|UNREADABLE|REGISTRY_UNREADABLE|Traceback \(most recent|❌ [A-Z ]+|⚠️ +[A-Z][A-Z ]+" | sed -E 's/[0-9]+/N/g' | sort -u | tr '\n' '|')"
    if [ -z "$SIG" ] && [ "$ERROR" -eq 1 ]; then
        SIG="ERROR-UNCLASSIFIED"        # unnamed, but still dedupes instead of repeating
    fi
    PREV="$(python3 - "$STATE" "$TENANT" <<'PY' 2>/dev/null
import json, sys
try: print(json.load(open(sys.argv[1])).get(sys.argv[2], ""))
except Exception: print("")
PY
)"
    if [ "$SPEAK" -eq 1 ] && [ -n "$SIG" ] && [ "$SIG" = "$PREV" ]; then
        SPEAK=0                                  # same condition as last time — already said it
    fi

    # record the signature; empty means healthy, which RE-ARMS the alert
    python3 - "$STATE" "$TENANT" "$SIG" <<'PY' 2>/dev/null
import json, sys
p = sys.argv[1]
try: d = json.load(open(p))
except Exception: d = {}
if sys.argv[3]: d[sys.argv[2]] = sys.argv[3]
else: d.pop(sys.argv[2], None)
json.dump(d, open(p, "w"))
PY

    if [ "$SPEAK" -eq 1 ]; then
        echo "═══ $TENANT ═══"
        echo "$OUT" | grep -vE "^[[:space:]]*$"
        echo
    fi
done

exit 0
