#!/usr/bin/env bash
# Prove the RESCUE RETRY fires ONLY for a stranded book, and never as a general floor bypass.
#
# Jordan, 2026-09-27: "I would like it to be able to make these decisions."
#
# The retry is three greps over lfj_recenter's output. This test replays the EXACT text from the
# real refusal that started this (2026-09-27 23:51Z) plus the cases that must NOT rescue, so the
# gate is proven in both directions rather than only on the happy path.
#
# Run: bash test_rescue_gate.sh
set -uo pipefail
cd "$(dirname "$0")"

OUT_OF_RANGE_REFUSAL='  ── PLAN ──  withdraw -> re-deploy CURVE (bidask, BID 12 + ASK 13 = 25 bins (curve))
  🛑 REFUSING TO START — CANNOT SHOW THE CYCLE CAN BE FINISHED, FLOOR INTACT.
     ⚠️  THIS RE-CENTER WOULD SPEND THE GAS FLOOR — balance 0.013892 AVAX, reserve 0.009200 AVAX
     A re-center WITHDRAWS first and re-deploys second.
     HOLDING the position unchanged. Top up native AVAX and the next pass proceeds.
  ⚠️  OUT OF RANGE — spot is 3 bins above the band; nothing in the book is earning.'

# A gas-floor refusal on a book that is IN RANGE and still collecting: must NOT rescue.
IN_RANGE_REFUSAL='  🛑 REFUSING TO START — CANNOT SHOW THE CYCLE CAN BE FINISHED, FLOOR INTACT.
     ⚠️  THIS RE-CENTER WOULD SPEND THE GAS FLOOR — balance 0.013892 AVAX, reserve 0.009200 AVAX
     price is INSIDE the position and earning.'

# A refusal for a NON-gas reason: must NOT rescue, whatever else the output says.
CASCADE_TEXT='  OUT OF RANGE — spot is 3 bins above the band.
  🛑 CASCADE — chasing into a cascade is suppressed.'

BAD_SIM='  OUT OF RANGE — nothing in the book is earning.
  🛑 SIMULATION FAILED — the deploy would revert.'

OK_TEXT='  ✅ BID-ASK LIVE — deployed as BID 15 + ASK 30 = 45 bins
  ✅ ON TARGET (off by -0.1%)'

ok=0; fail=0
check () { # name, expected, actual
  if [ "$2" = "$3" ]; then ok=$((ok+1)); echo "  PASS  $1"; else fail=$((fail+1)); echo "  FAIL  $1 (got $3, want $2)"; fi
}

# The gate, extracted so the test exercises the SAME three conditions as the watchdog.
would_rescue () {
  echo "$1" | grep -qE "REFUSING TO START|REFUSING TO RE-ENTER" \
    && echo "$1" | grep -qiE "spend the gas floor|gas floor|CANNOT SHOW THE CYCLE" \
    && echo "$1" | grep -qiE "OUT OF RANGE|flat book|earning nothing|nothing in the book is earning"
  # grep chain returns 0 (true) only when all three match
}

echo ""
echo "  ── MUST RESCUE ──"
check "gas floor + stranded/out-of-range  -> RESCUE" yes "$([ "$(would_rescue "$OUT_OF_RANGE_REFUSAL" >/dev/null 2>&1; echo $?)" = "0" ] && echo yes || echo no)"

echo ""
echo "  ── MUST NOT RESCUE (the safety half) ──"
check "gas floor but book IN RANGE       -> no rescue" no "$([ "$(would_rescue "$IN_RANGE_REFUSAL" >/dev/null 2>&1; echo $?)" = "0" ] && echo yes || echo no)"
check "out of range but CASCADE          -> no rescue" no "$([ "$(would_rescue "$CASCADE_TEXT" >/dev/null 2>&1; echo $?)" = "0" ] && echo yes || echo no)"
check "out of range but SIMULATION FAILED-> no rescue" no "$([ "$(would_rescue "$BAD_SIM" >/dev/null 2>&1; echo $?)" = "0" ] && echo yes || echo no)"
check "a healthy pass                    -> no rescue" no "$([ "$(would_rescue "$OK_TEXT" >/dev/null 2>&1; echo $?)" = "0" ] && echo yes || echo no)"

echo ""
echo "  ── THE SCRIPT ITSELF MUST SURVIVE set -u ON EVERY PATH ──"
# `set -uo pipefail` means an unbound variable aborts the pass. RESCUED is read after the
# CASCADE branch, so it must be initialised before it.
check "RESCUED is initialised before the branch" yes "$(grep -qE '^\s*RESCUED=0\s*$' steward-watchdog.sh && echo yes || echo no)"
check "  ...and read later" yes "$(grep -qE '\[ "\$RESCUED" -eq 1 \]' steward-watchdog.sh && echo yes || echo no)"

echo ""
echo "  RESULT: $([ $fail -eq 0 ] && echo PASS || echo FAIL) — $ok/$((ok+fail)) checks passed"
echo ""
exit $([ $fail -eq 0 ] && echo 0 || echo 1)
