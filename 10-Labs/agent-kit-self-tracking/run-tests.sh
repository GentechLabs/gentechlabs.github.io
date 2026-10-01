#!/usr/bin/env bash
# run-tests.sh — the canonical test runner for the treasury scripts.
#
# WHY THIS EXISTS (2026-09-28):
#   Ad-hoc `for f in test_*.py` loops graded tests by exit code alone, which conflated three
#   genuinely different outcomes. Three tests in this suite exit **2 = CANNOT JUDGE** by design:
#   they need a live chain read or a funded wallet, and when that is unavailable they refuse to
#   render a verdict rather than invent one. A bare runner counted those as FAILURES, so the suite
#   reported "4 fail" while two of the four were the code working correctly.
#
#   Worse in the other direction: a runner that mapped rc==2 to PASS would let a test that NEVER
#   judges anything stay green forever — the false-value family, wearing a test's clothes.
#
# So there are THREE outcomes, and they are reported separately:
#     PASS (0)            the check ran and the property holds
#     CANNOT JUDGE (2)    the check could not run (no chain read / no funds) — NOT a pass
#     FAIL (1, 124, other) the check ran and the property is VIOLATED, or the test hung/crashed
#
# A CANNOT-JUDGE is never counted as a pass and is always printed. It is not a failure of the code
# under test, but it is also not evidence that anything works — it is an unknown, and an unknown
# must never be silently green. If the cannot-judge count stays high, the suite is not testing
# anything and THAT is the finding.
set -uo pipefail
cd "$(dirname "$0")" || exit 1

PASS=0; FAIL=0; CJ=0
TIMEOUT_SECS="${TEST_TIMEOUT:-240}"
CJ_FILE="$(mktemp)"; FAIL_FILE="$(mktemp)"
# Where a failing test's own transcript goes. A failure must carry its evidence (below).
FAIL_LOG_DIR="${FAIL_LOG_DIR:-/tmp/treasury-test-failures}"
trap 'rm -f "$CJ_FILE" "$FAIL_FILE"' EXIT

for f in test_*.py; do
    [ -e "$f" ] || continue
    out="$(timeout "$TIMEOUT_SECS" python3 "$f" 2>&1)"; rc=$?
    case "$rc" in
        0)  PASS=$((PASS+1)) ;;
        2)  CJ=$((CJ+1))
            # Surface WHY it could not judge — the reason is the useful part.
            # Write record-per-line: the shell word-splits an unquoted string on spaces, which
            # shattered the reason message into one "test" per word.
            reason="$(printf '%s\n' "$out" | grep -iE 'cannot judge|unreadable|untested|no wavax|balance is dust|skip|not funded' | head -1 | sed 's/^[[:space:]]*//')"
            printf '%s\t%s\n' "$f" "${reason:-no reason given}" >> "$CJ_FILE" ;;
        *)  FAIL=$((FAIL+1))
            # A FAILURE MUST CARRY ITS EVIDENCE. This branch recorded `rc=` and threw `$out` away —
            # and `$out` was captured for exactly this purpose. So a red test reported a filename
            # and an exit code, and NOTHING to diagnose from: the only way to learn why was to
            # re-run that test by hand, blind. (The cannot-judge branch above mines its output for
            # a reason; the failure branch mining none is the asymmetry, and it is the bug.)
            # A verdict whose supporting output is discarded cannot be audited, and an auditor who
            # must reproduce the run to see the reason will eventually stop reproducing it.
            # Mine the test's own most informative line AND keep the whole transcript on disk.
            mkdir -p "$FAIL_LOG_DIR"
            printf '%s\n' "$out" > "$FAIL_LOG_DIR/$f.log"
            reason="$(printf '%s\n' "$out" | grep -iE 'FAIL|RESULT|Traceback|Error|assert' \
                      | tail -1 | sed 's/^[[:space:]]*//' | cut -c1-140)"
            printf '%s\t%s\n' "$f" "rc=$rc — ${reason:-no output}  [full: $FAIL_LOG_DIR/$f.log]" >> "$FAIL_FILE" ;;
    esac
done

echo "════════════════════════════════════════════════════════════════"
echo "  pass=$PASS   cannot-judge=$CJ   fail=$FAIL"
echo "════════════════════════════════════════════════════════════════"
if [ -s "$CJ_FILE" ]; then
    echo "  ➖ CANNOT JUDGE (ran, refused to invent a verdict — NOT a pass):"
    while IFS="$(printf '\t')" read -r name why; do
        printf '     %-36s %s\n' "$name" "$why"
    done < "$CJ_FILE"
fi
if [ -s "$FAIL_FILE" ]; then
    echo "  ❌ FAILED (the property is violated, or the test hung/crashed):"
    while IFS="$(printf '\t')" read -r name why; do
        printf '     %-36s %s\n' "$name" "$why"
    done < "$FAIL_FILE"
    exit 1
fi

# A suite where nothing can actually judge anything must not report success.
TOTAL=$((PASS+CJ))
if [ "$TOTAL" -gt 0 ] && [ "$CJ" -ge "$TOTAL" ]; then
    echo "  ❌ EVERY test could not judge — the suite is not testing anything."
    exit 1
fi
exit 0
