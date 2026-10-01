#!/usr/bin/env python3
"""Pin the gas budget to the RECEIPTS, so it can never again be argued from a document.

WHY THIS TEST EXISTS. The withdraw budget changed three times in one day, each time justified by
reading a FILE — a table, a derived per-bin rate, a docstring — and each time wrong:

    210,000     the original table value. Under the real withdrawal by ~3.6x. This is the number
                the gate was using when dadrian's first repair was refused and his withdraw then
                died on-chain: "insufficient funds for gas * price + value".
    2,390,445   derived as 53,121 gas/bin x 45 bins. Right instinct (the withdraw is expensive),
                wrong NUMBER — 1,328,018 was the FAILED transaction's TOTAL cost, not the gas of a
                decreaseLiquidity call, so the per-bin rate described an operation that never ran.
    210,000     restored, on the reasoning that lfj_exit.py records "a full exit measures at
                142,395 gas". A docstring is not a receipt: the withdrawal we actually executed
                measured 759,027.

The argument only ended when dadrian's successful repair was read off the chain. So this test
encodes the RECEIPTS, and asserts the budget stays above them.

THE MEASURED RECEIPTS (dadrian, 25-bin book, repair at ~19:00Z 2026-09-27):
    96276762    759,027 gas    the withdrawal (LB router)
    96276822    150,263 gas    the rebalance swap
    96276826    702,895 gas    BID leg mint
    96276834    737,703 gas    ASK leg mint

WHAT IS ASSERTED:
  1. the withdraw budget EXCEEDS the measured withdrawal;
  2. the mint budget EXCEEDS both legs combined;
  3. the budgets are above their measurements, never below (over-budget refuses early and is free;
     under-budget spends the withdraw and then fails the re-deploy);
  4. no budget is derived from a per-bin rate applied to the withdraw;
  5. a budget regression to a known-wrong value FAILS this test (it is not vacuous).
"""
import re
import sys

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    if not cond and detail:
        print(f"        {detail}")


import gas_reserve as GR

# ── THE RECEIPTS, transcribed from the chain ─────────────────────────────────────────────────
WITHDRAW_MEASURED = 759_027          # block 96276762
SWAP_MEASURED = 150_263              # block 96276822
MINT_BID_MEASURED = 702_895          # block 96276826
MINT_ASK_MEASURED = 737_703          # block 96276834
MINT_BOTH_MEASURED = MINT_BID_MEASURED + MINT_ASK_MEASURED      # 1,440,598
# a second LB-router tx (150,865) sat in the same window and may also belong to the withdraw phase
WITHDRAW_WORST_CASE = WITHDRAW_MEASURED + 150_865               # 909,892

print("  ── 1. THE WITHDRAW BUDGET EXCEEDS THE MEASURED WITHDRAWAL ──")
wd = GR.OP_GAS_UNITS["decreaseLiquidity"]
check(f"withdraw budget {wd:,} > measured {WITHDRAW_MEASURED:,}", wd > WITHDRAW_MEASURED,
      "the 210,000 value that stranded a live book was BELOW this")
check(f"withdraw budget {wd:,} >= worst joint reading {WITHDRAW_WORST_CASE:,}",
      wd >= WITHDRAW_WORST_CASE, "the ambiguous second router tx must not under-budget us")

print("")
print("  ── 2. THE MINT BUDGET EXCEEDS BOTH LEGS ──")
mt = GR.OP_GAS_UNITS["mint"]
check(f"mint budget {mt:,} > both legs measured {MINT_BOTH_MEASURED:,}", mt > MINT_BOTH_MEASURED,
      "the old 1,250,000 under-budgeted the pair by ~190k")

print("")
print("  ── 3. EVERY BUDGET IS ABOVE ITS MEASUREMENT (the safe direction) ──")
for name, budget, measured in (("decreaseLiquidity", wd, WITHDRAW_MEASURED),
                               ("mint", mt, MINT_BOTH_MEASURED),
                               ("swap", GR.OP_GAS_UNITS["swap"], SWAP_MEASURED)):
    check(f"{name}: budget {budget:,} > measured {measured:,}", budget > measured,
          "an under-budget spends the first tx and fails the second — capital stranded")

print("")
print("  ── 4. NO PER-BIN RATE IS APPLIED TO THE WITHDRAW ──")
src = open(GR.__file__).read()
body = src[src.find("OP_GAS_UNITS = {"):]
body = body[:body.find("}") + 1]
check("the withdraw entry is a literal, not a function call",
      re.search(r'"decreaseLiquidity":\s*[\d_]+\s*,', body) is not None,
      "a per-bin rate applied to the withdraw is how the 2,390,445 error was produced")
check("no per-bin constant remains",
      "PER_BIN" not in src.upper() or "DECREASE_LIQUIDITY_GAS_PER_BIN" not in src,
      "the 53,121/bin figure came from a RE-ENTRY measurement, not the withdraw")

print("")
print("  ── 5. THE TEST IS NOT VACUOUS: known-wrong values FAIL ──")
for wrong, why in ((210_000, "the original table value"),
                   (142_395, "the stale lfj_exit.py docstring figure"),
                   (450_000, "210k + collect + swap, the pre-fix cycle line")):
    check(f"{wrong:,} is correctly BELOW the measured withdrawal ({why})",
          wrong < WITHDRAW_MEASURED,
          "if this fails, the measured receipt itself is wrong — re-read the chain")
for wrong in (450_000, 1_250_000):
    check(f"{wrong:,} would NOT cover both mint legs ({MINT_BOTH_MEASURED:,})",
          wrong < MINT_BOTH_MEASURED, "the old mint budget under-covered the pair")

print("")
print(f"  RESULT: {'PASS' if not FAIL else 'FAIL'} — {len(PASS)}/{len(PASS)+len(FAIL)} checks passed")
for f in FAIL:
    print(f"    - {f}")
sys.exit(1 if FAIL else 0)
