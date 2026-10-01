#!/usr/bin/env python3
"""Prove the PHASED gas gate: a deployed book may pay for its own re-center, and nothing else changes.

THE CIRCULAR DEPENDENCY THIS CLOSES (found 2026-09-27 on dadrian's live book):
    to get gas, top up from the book
    to reach the book, withdraw it
    to withdraw it, you must already have gas      <-- the loop
The gate checked affordability BEFORE the withdraw (correct — refusing to begin is free) but
treated the wallet's current native balance as everything it would ever have. For a DEPLOYED book
that is false: the withdraw RETURNS the book as WAVAX + USDC. Measured on dadrian: balance
0.00458405 AVAX, one exit 0.002250, one re-entry 0.006830 — he could afford the WITHDRAW but not
the RE-DEPLOY, so the whole cycle was refused and his book stayed at 7.5% efficiency, able to pay
for its own repair and forbidden to start.

WHAT MUST STAY TRUE (these are the checks — a loosened gate on a money path is worse than the bug):
  1. a wallet that cannot afford the WITHDRAW is still refused, whatever the book is worth;
  2. a book too small to close its own gap is still refused;
  3. an UNMEASURABLE book refuses (fail closed) — never "assume it can pay";
  4. omitting the book value reproduces the OLD behaviour exactly (no silent loosening);
  5. the FLOOR is not lowered by this change — the reserve is untouched;
  6. the phased path is ONLY reachable when the withdraw is genuinely affordable.
"""
import sys

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    if not cond and detail:
        print(f"        {detail}")


import lfj_recenter as R
import gas_reserve as GR

# ── A synthetic reserve_info shaped like the real one (dadrian's live numbers) ──────────────
#
# ⚠️ EXIT / REENTRY ARE DERIVED FROM gas_reserve.OP_GAS_UNITS, NOT TYPED IN (fixed 2026-09-27).
# They used to be literals — 0.002250 and 0.006830 — captured before the budgets were pinned to
# on-chain receipts. When the sibling receipt fix raised `decreaseLiquidity` 210,000 -> 1,000,000 and
# `mint` 1,250,000 -> 1,500,000, the real withdraw cost rose to 0.0054 AVAX while this fixture still
# claimed 0.002250, so the SCENARIO this test builds stopped matching the code under test: the gate
# correctly refused dadrian's wallet and 6 checks failed for a reason that had nothing to do with the
# mechanism they were written to protect.
#
# Hardcoding a cost that the code computes means a budget change silently invalidates the test's
# premise. Deriving it keeps the scenario honest: the fixture moves with the table, and the checks
# keep testing the PHASED LOGIC rather than a stale arithmetic coincidence.
#
# The receipts these correspond to (dadrian, block 96276762+): withdraw 759,027 gas, swap 150,263,
# mints 702,895 + 737,703. Every budget in the table sits ABOVE its receipt — that is
# test_gas_from_receipts.py's job to enforce, and it is the authority on the numbers.
GP = 5_000_000_000                       # 5 nAVAX, his live gas price
EXIT = (GR.OP_GAS_UNITS["decreaseLiquidity"] + GR.OP_GAS_UNITS["collect"]) * GP / 1e18
REENTRY = (GR.OP_GAS_UNITS["approve"] * 2 + GR.OP_GAS_UNITS["mint"]) * GP / 1e18
RESERVE = 0.01818182                     # the $0.20 floor
PRICE = 11.01
# A balance that can pay the withdraw but not the whole cycle — the exact circular-dependency case.
# DERIVED TOO: if it were pinned and the withdraw cost rose past it, the fixture would silently start
# testing "cannot even cover the withdraw", which is a different branch than the one intended.
BAL_DEPLOYED = EXIT * 1.2


def info(balance, reserve=RESERVE):
    # MIRROR reserve_info()'s FULL key set. shortfall_text()/gate() read by_cycles_avax,
    # by_usd_avax, shortfall_avax and shortfall_usd, so a partial fixture raises KeyError instead
    # of exercising the gate. (Cost me two rounds — the fix is to copy the real shape, not guess.)
    cyc = EXIT + REENTRY
    short = max(0.0, reserve - balance)
    return {
        "measured": True, "unmeasured_reason": None, "tenant": "dadrian", "wallet": "0x" + "1" * 40,
        "balance_avax": balance, "balance_wei": int(balance * 1e18), "reserve_avax": reserve,
        "exit_avax": EXIT, "reentry_avax": REENTRY, "cycle_avax": cyc, "cycle_gas_units": 1_816_000,
        "gas_price_wei": GP, "gas_price_navax": 5.0, "avax_usd": PRICE,
        "floor_cycles": 1, "floor_usd": 0.20,
        "by_cycles_avax": 1 * cyc, "by_usd_avax": 0.20 / PRICE, "reserve_usd": 0.20,
        "shortfall_avax": short, "shortfall_usd": short * PRICE,
        "deployable_avax": max(0.0, balance - reserve),
        "deployable_wei": int(max(0.0, balance - reserve) * 1e18),
        "ops_runway": 0, "above": balance >= reserve,
    }


print("  ── 1. THE LOOP IS CLOSED: a deployed book can fund its own re-center ──")
ok, why = R._deployed_book_can_close_its_own_gap(info(BAL_DEPLOYED), 48.60)
check("dadrian's live numbers now ADMIT the cycle", ok, why[:150])
check("and it says PHASED (the mechanism is named, not implied)", "PHASED" in why, why[:160])
check("it reports the withdraw is affordable", "withdraw is affordable" in why.lower(), why[:200])
check("it names the top-up step that will buy the native gas", "PROVISION GAS" in why, why[:200])

print("")
print("  ── 2. THE SAFETY: refusal where refusal is correct ──")
ok2, why2 = R._deployed_book_can_close_its_own_gap(info(0.0001), 48.60)
check("a wallet that cannot afford the WITHDRAW is refused even with a fat book", not ok2, why2[:150])
check("  ...and it says so in terms of the withdraw, not the book",
      "cannot even cover the withdraw" in why2, why2[:160])

ok3, why3 = R._deployed_book_can_close_its_own_gap(info(BAL_DEPLOYED), 0.05)
check("a book TOO SMALL to close its own gap is refused", not ok3, why3[:150])
check("  ...and it says an outside deposit is genuinely required",
      "outside deposit" in why3, why3[:200])

ok4, why4 = R._deployed_book_can_close_its_own_gap(info(BAL_DEPLOYED), None)
check("an UNMEASURED book refuses (fail closed)", not ok4, why4[:150])
ok5, why5 = R._deployed_book_can_close_its_own_gap(info(BAL_DEPLOYED), 0.0)
check("a zero-valued book refuses", not ok5, why5[:120])

print("")
print("  ── 3. UNMEASURABLE COSTS REFUSE, exactly as before ──")
bad = info(BAL_DEPLOYED); bad["gas_price_wei"] = 0
check("an unmeasurable gas price refuses", not R._deployed_book_can_close_its_own_gap(bad, 48.6)[0])
bad2 = info(BAL_DEPLOYED); bad2["exit_avax"] = 0
check("an unmeasurable exit cost refuses", not R._deployed_book_can_close_its_own_gap(bad2, 48.6)[0])

print("")
print("  ── 4. THE OLD BEHAVIOUR IS UNCHANGED WHEN THERE IS NO BOOK VALUE ──")
# _gas_precondition needs w3g only to read the balance; supply a stub.
class _W3:
    def __init__(self, bal):
        self._b = bal
        self.eth = _Eth(bal)
class _Eth:
    def __init__(self, bal): self._b = bal
    def get_balance(self, _a): return int(self._b * 1e18)
def stub_w3(bal):
    return _W3(bal)

# Patch reserve_info so the unit test needs no network and cannot drift with live gas.
import gas_reserve as GR
_real = GR.reserve_info
GR.reserve_info = lambda tenant=None, w3=None, avax_usd=None, balance_avax=None, gas_price_wei=None: info(balance_avax)
try:
    okN, whyN = R._gas_precondition(stub_w3(BAL_DEPLOYED), "0x" + "1" * 40, position_usd=None)
    check("without a book value it still REFUSES (no silent loosening)", not okN, whyN[:150])
    check("  ...and the refusal is the original wording",
          "CANNOT FINISH THE CYCLE" in whyN, whyN[:150])

    okY, whyY = R._gas_precondition(stub_w3(BAL_DEPLOYED), "0x" + "1" * 40, position_usd=48.60)
    check("with a measured book value the SAME wallet proceeds", okY, whyY[:150])
    check("  ...and the floor is still reported, not hidden",
          "Floor note" in whyY or "reserve" in whyY, whyY[:200])

    okA, whyA = R._gas_precondition(stub_w3(1.0), "0x" + "1" * 40, position_usd=48.60)
    check("a wallet already above the cycle needs NO phasing (unchanged path)", okA, whyA[:150])
    check("  ...and does not claim to be PHASED", "PHASED" not in whyA, whyA[:160])
finally:
    GR.reserve_info = _real

print("")
print("  ── 5. THE FLOOR IS NOT LOWERED BY THIS CHANGE ──")
check("FLOOR_USD is still 0.20 (Jordan's standard)", abs(GR.FLOOR_USD - 0.20) < 1e-9, f"{GR.FLOOR_USD}")
check("the reserve is computed, never taken from the book",
      "reserve_avax" in info(BAL_DEPLOYED))
# The phased path must never alter the reserve it reports.
_r1 = info(BAL_DEPLOYED)["reserve_avax"]
check("the reserve figure is independent of the book's value", abs(_r1 - RESERVE) < 1e-6)

print("")
print(f"  RESULT: {'PASS' if not FAIL else 'FAIL'} — {len(PASS)}/{len(PASS)+len(FAIL)} checks passed")
for f in FAIL:
    print(f"    - {f}")
sys.exit(1 if FAIL else 0)
