#!/bin/bash
# lfj-curve-deploy.sh — deploy a CURVE (two-sided, range-bound) position on LFJ.
#
# ⚠ NO WALLET LOCK OF ITS OWN — CORRECT ONLY WHILE THE CALL GRAPH HOLDS (measured 2026-09-27)
# -------------------------------------------------------------------------------------------
# This script calls `gas_reserve.py` and `lfj_bid_deploy.py`, and NEITHER of them nor this
# script takes the wallet lock. Today that is safe for one reason only:
#
#     the ONLY caller is lfj_recenter.py (line ~885), which holds
#     agent_lock.WalletLock for EXECUTE runs (lfj_recenter.py:739)
#
# So the mutual exclusion around the wallet is INHERITED, not enforced here. Verified: no cron
# invokes this script directly, and `WalletLock` is absent from gas_reserve.py, lfj_exit.py,
# lfj_bid_deploy.py and steward_execute.py.
#
# THE TRAP: the moment anything calls this script (or those two) DIRECTLY from cron, the
# recenter-vs-recenter race reopens with nothing to catch it. That race is real and costly —
# the watchdog is `*/5 * * * *` while a rebuild takes 7–11 minutes, and it produced nonce drift
# (1601→1604 in 45 min) and a 13-bin ASK-only book earning $0.00 at 11:36Z.
#
# IF YOU ADD A DIRECT CALLER: acquire `WalletLock(<wallet>, purpose=...)` at this script's top
# (see lfj_recenter.py:739 for the pattern), or call this path only from inside the lock.
#
# WHY THIS IS TWO DEPLOYS AND NOT ONE (2026-09-20)
# ------------------------------------------------
# Jordan: "If we get stable switch to curve."
#
# A true two-sided Liquidity Book position - both tokens spread across both sides of spot -
# requires the router to compute a COMPOSITION FACTOR to reconcile the two tokens in shared
# bins. That path REVERTS with CompositionFactorFlawed. We hit it earlier and it is why the
# book went single-sided in the first place. It is not a bug to out-think; it is a path that
# does not need walking.
#
# But a curve does not require it. A curve is, economically:
#
#       BID  (USDC below spot)  buying the dip on the way down
#     + ASK  (WAVAX above spot) selling the rally on the way up
#
# Those are TWO SINGLE-SIDED positions. Each has one token, so there is NO composition to
# compute and each uses the exact code path already proven live today. Visually and
# economically it is a curve: liquidity both sides of spot, earning on chop in either
# direction. The only cost is two transactions instead of one - ~$0.003 extra in gas.
#
# USAGE
#   bash lfj-curve-deploy.sh [--execute] [--bid-ratio 0.5] [--ask-ratio 0.7]
#
#   --bid-ratio   fraction of USDC to place in the dip ladder   (default 0.5)
#   --ask-ratio   fraction of WAVAX to place in the sell ladder (default 0.3)
#
# ASK RATIO 0.7 -> 0.3 (Jordan, 2026-09-20). At 0.7 the curve's ask leg deployed SEVENTY PERCENT
# of our WAVAX into sell-side bins, so a range-bound call would quietly liquidate most of the
# position into any rally. Jordan caught this: "if we get stable switch to curve" is a FEE
# instruction, not an instruction to sell the upside. At 0.3 the curve still earns on both sides
# of spot but keeps 70% of the WAVAX RAW and fully exposed. The shape does the range-bound job;
# the stack still rides the breakout.
#
# WHY NOT 100% BOTH SIDES: a curve is a range-bound structure. Holding back a slice of each
# leg keeps dry powder to re-center with when price wanders out of the range, so the loop can
# maintain the curve rather than needing new capital.

set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

EXEC=""
# ── YIELD-FARM LOGIC: NO IDLE FUNDS (Jordan, 2026-09-21) ──────────────────────────────────────
# Jordan: "I want the whole balance to be on the left and the right... we need this to be yield
# farm logic where we don't want funds to sit idle. We want funds to be balanced, either 50/50,
# 60/40, or 70/30."
#
# BOTH legs now deploy their FULL side. A re-center must MOVE capital, not shrink it. Idle capital
# is the named failure mode (risk-envelope.json: "Capital leaving a perp must not idle in a
# wallet. Idle capital is the failure mode this exists to prevent.").
#
# BID_RATIO 1.0 -- the bid leg is USDC below spot = pure BUYING POWER. There is no upside to
# preserve on this side, so holding any of it back was never a position, it was capital earning
# nothing. The old 0.5 reserve existed to fund future re-centers at ~$0.003 each; it cost far more
# in forgone fees than the gas it protected.
BID_RATIO="1.0"
# ASK_RATIO 0.3 -> 1.0 (Jordan, 2026-09-21). The old 0.3 kept 70% of the WAVAX RAW "so the stack
# rides a breakout". That reasoning was sound as far as it went -- but it left ~$71 of a $113 book
# earning ZERO while $41 worked. Jordan's ruling: the whole balance goes to work.
#
# THE TRADE-OFF IS REAL AND IS ACCEPTED, NOT HIDDEN. Measured geometry at spot $11.11, binStep
# 0.1%: the 45-bin ceiling means the widest possible ask tops out at $11.62, so the stack converts
# to USDC on a ~4.6% pop. No width both earns and holds -- earning requires sitting near spot, and
# near spot converts on a small move. Cushion by target price:
#     $11.35 (2.2%) =  21 bins | $11.61 (4.5%) =  44 bins | $12.00 (8.0%) =  77 bins  (over cap)
# If riding a breakout matters more than the fees on a given day, pass --ask-ratio explicitly.
ASK_RATIO="1.0"
# ── SHAPE → WIDTH (Jordan, 2026-09-22) ────────────────────────────────────────────────────────
# "remember a curve shape should be closer to 25 bins. 45 for the bid ask."
# The geometry is NOT defined here any more. It lives in lfj_shapes.py so the deploy path, the
# efficiency metric and the re-center planner cannot disagree about it -- they all used to regex
# this file's source text, where a second assignment line would have made them silently report the
# wrong shape's width. This script now ASKS for the shape it means.
# DEFAULT IS CURVE (Jordan, 2026-09-22): "the one that I've set up in the vault or in the
# brain, I think should just be our default for the yield farm" -- the reference implementation
# is the 25-bin curve. It was "bidask" here, which is why a caller that omitted --shape
# silently got the opposite shape from the house default.
SHAPE="${SHAPE:-curve}"
# ── THE GAS FLOOR IS CHECKED BEFORE LEG 1, NOT INSIDE A LEG (Jordan, 2026-09-25) ──────────────
# This wrapper fires TWO legs. Each leg now holds back the reserve on its own side, and each leg
# also refuses when the WALLET is at or below the floor — but a leg refusing AFTER leg 1 landed is
# the half-built state this whole script exists to avoid ("a directional position wearing a
# curve's name"). So the floor is checked ONCE, up front, before anything is built:
# the same gas_reserve.py the legs call, the same live gas price, one implementation.
# --rescue is the ONLY way past it, and it travels to both legs so the decision is made once and
# is visible in the log.
RESCUE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --execute) EXEC="--execute --yes"; shift ;;
    --bid-ratio) BID_RATIO="$2"; shift 2 ;;
    --ask-ratio) ASK_RATIO="$2"; shift 2 ;;
    --shape) SHAPE="$2"; shift 2 ;;
    --rescue) RESCUE="--rescue"; shift ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

echo "================================================================================"
echo "  LFJ CURVE DEPLOY — bid + ask as two single-sided legs"
echo "  (the two-sided single-tx path reverts with CompositionFactorFlawed)"
echo "================================================================================"

# ---- LEG 1: the BID (USDC below spot) -------------------------------------------
echo
echo "  ── LEG 1/2 : BID (USDC below spot) ──"

# ─────────────────────────────────────────────────────────────────────────────────────────────
# BIN WIDTH RULE  (Jordan, 2026-09-21: "why are we in 101 bins, we should be keeping this tighter")
#
# There was NO width rule before this. 101 bins was simply what the arguments said: 56 bid + 45 ask,
# about 10.5% wide at binStep 10bps. A width that exists because nobody chose it is not a strategy.
#
# THE RULE: BID-ASK MAXIMUM IS 45 BINS (Jordan, 2026-09-21).
#   BID  near 2  far 23  -> 22 bins
#   ASK  near 1  far 23  -> 23 bins
#   total 45 bins  <= the 45 ceiling
#
# ⚠️ THIS BLOCK SAID "38 bins" WHILE lfj_recenter.py SAID "45" -- and the recenter DISPLAYED 45
# while CALLING this script, so a re-center would have silently SHRUNK a 45-bin position to 38.
# Three files held three different bin counts. The fix is not another number written in a comment:
# it is the COMPUTED GUARD BELOW, which derives the total from the arguments actually passed and
# refuses to deploy over the ceiling. A rule stated in prose drifts; a rule computed from the
# command cannot. (Same defect class as the hardcoded "45 / 45 max" guard that printed max even
# when the args said 60.)
#
# WHY TIGHTER IS BETTER HERE: the same capital spread over fewer bins earns MORE PER BIN whenever
# price is crossing. $57.98 over 101 bins is ~$0.57/bin; over 45 bins it is ~$1.29/bin.
# A wide band earns a little almost always; a tight band earns a lot while it is in range.
#
# WHY WE CAN AFFORD THE EXTRA RE-CENTERS: gas is ~$0.003 per re-center (Jordan: "I would never
# worry about the rebalance or re-center cost because that's so cheap, it's almost free"). Paying
# pennies of gas to raise fee density is the correct trade at this book size.
#
# THE TRADE-OFF, STATED: tighter goes out of range sooner. That is the cost, and it is accepted.
# ─────────────────────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────────────────────
# GEOMETRY: resolved from lfj_shapes.py for THIS shape (curve ~25 bins, bidask 45). Jordan's
# 45-bin rule is a CEILING and the table enforces it, so a shape whose width exceeds it is a
# hard refusal rather than a silent overrun.
_SW="$(python3 "$DIR/lfj_shapes.py" --shape "$SHAPE" --emit json 2>/dev/null)"
if [ -z "$_SW" ]; then
  echo "  ❌ REFUSING: could not resolve geometry for shape '$SHAPE' from lfj_shapes.py."
  exit 2
fi
eval "$(python3 - "$_SW" <<'PY'
import json, sys
d = json.loads(sys.argv[1])
print(f"BID_NEAR={d['bid_near']}; BID_FAR={d['bid_far']}; ASK_NEAR={d['ask_near']}; ASK_FAR={d['ask_far']}; MAX_BINS={d['ceiling']}")
PY
)"
BID_N=$(( BID_FAR - BID_NEAR + 1 ))
ASK_N=$(( ASK_FAR - ASK_NEAR + 1 ))
TOTAL_N=$(( BID_N + ASK_N ))
if (( TOTAL_N > MAX_BINS )); then
  echo "  ❌ REFUSING: BID $BID_N + ASK $ASK_N = $TOTAL_N bins exceeds the $MAX_BINS ceiling."
  exit 2
fi
echo "  shape=$SHAPE  bins: BID $BID_N + ASK $ASK_N = $TOTAL_N  (ceiling $MAX_BINS)"

# ── THE GAS FLOOR — A FLOOR THE NO-IDLE RULE MUST RESPECT (Jordan, 2026-09-25) ────────────────
# "Deploy the whole balance" means "deploy the whole balance MINUS the reserve". The reserve is
# computed by gas_reserve.py from the LIVE gas price and the LIVE AVAX price, and it is what pays
# for the next swap or re-deploy — so no deploy path may spend it. ONE tenant per check: the
# tenant comes from --tenant / STEWARD_TENANT / steward_identity, never from OR-ing every tenant.
if [ -z "$RESCUE" ]; then
  _FLOOR_OUT="$(python3 "$DIR/gas_reserve.py" --deploy-check 2>&1)"
  _FLOOR_RC=$?
  echo "$_FLOOR_OUT" | sed 's/^/  /'
  if [ "$_FLOOR_RC" -ne 0 ]; then
    echo "  ❌ REFUSING BEFORE LEG 1/2 — the gas floor gates this deploy (deploy-check exit $_FLOOR_RC)."
    echo "     Refusing to BEGIN is free; a book half-built because leg 2 could not pay its gas is"
    echo "     'a directional position wearing a curve's name' — the state this script exists to avoid."
    echo "     Restore the reserve (python3 gas_reserve.py --plan), or force a genuine re-entry of a"
    echo "     stranded book with: bash lfj-curve-deploy.sh --shape $SHAPE --rescue --execute"
    exit 7
  fi
else
  echo "  ⚠️  --rescue: the gas floor does NOT gate this two-leg deploy (stated loudly, never silently)."
fi
# ── --kind WAS NEVER PASSED (fixed 2026-09-23) ─────────────────────────────────────────
# Without this the tool took its default ("bidask") on EVERY deploy, so the distribution was
# fixed at centre-heavy no matter which shape the caller asked for. The shape was in the
# WIDTH but never in the WEIGHTS — half the geometry silently constant.
_KIND="$SHAPE"; [ "$_KIND" = "bid-ask" ] && _KIND="bidask"; [ "$_KIND" = "curve" ] || _KIND="bidask"
python3 "$DIR/lfj_bid_deploy.py" --kind "$_KIND" --side bid --ratio "$BID_RATIO" --near "$BID_NEAR" --far "$BID_FAR" $EXEC $RESCUE
BID_RC=$?
echo "  leg 1 exit=$BID_RC"

# ---- LEG 2: the ASK (WAVAX above spot) ------------------------------------------
echo
echo "  ── LEG 2/2 : ASK (WAVAX above spot) ──"
python3 "$DIR/lfj_bid_deploy.py" --kind "$_KIND" --side ask --ratio "$ASK_RATIO" --near "$ASK_NEAR" --far "$ASK_FAR" $EXEC $RESCUE
ASK_RC=$?
echo "  leg 2 exit=$ASK_RC"

echo
echo "================================================================================"
if [[ $BID_RC -eq 0 && $ASK_RC -eq 0 ]]; then
  # ── THE BANNER WAS HARDCODED (fixed 2026-09-23) ──────────────────────────────────────────
  # This said "✅ CURVE LIVE — liquidity both sides of spot" for EVERY successful deploy,
  # including --shape bid-ask. Jordan asked "I'm currently in a curve, did conditions change?"
  # while on chain holding 45 bins with a 3-bin gap at spot — a BID-ASK. The machine had told
  # him "CURVE" in the one line he reads, and he believed it. The script already knows the shape
  # (line 151 prints shape=$SHAPE); the success line just ignored it.
  # A completion banner that names the wrong shape is worse than no banner: it is a confident
  # wrong answer about the position the operator is holding.
  _SHAPE_UP="$(echo "$SHAPE" | tr '[:lower:]' '[:upper:]')"
  echo "  ✅ $_SHAPE_UP LIVE — deployed as BID $BID_N + ASK $ASK_N = $TOTAL_N bins"
  if [[ "$SHAPE" == "bid-ask" || "$SHAPE" == "bidask" ]]; then
    echo "     Two single-sided legs with a gap at spot — this is a BID-ASK, not a curve."
  else
    echo "     One contiguous band spanning spot — a curve."
  fi
  echo "     Honest caveat either way: it is TWO positions, not one. Deployed as two single-sided"
  echo "     legs, it re-centers as two legs, and either leg can drift out of range independently."
  echo "     The watchdog must therefore maintain BOTH, not one."
  RC=0
else
  echo "  ⚠️ PARTIAL — bid=$BID_RC ask=$ASK_RC. A half-built curve is a directional"
  echo "     position wearing a curve's name. Check which leg landed before trusting it."
  RC=1
fi
echo "================================================================================"
exit $RC
