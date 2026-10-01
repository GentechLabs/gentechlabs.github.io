#!/usr/bin/env python3
"""Guard the self-funding gas top-up — the tool that lets the treasury manage itself.

Jordan, 2026-09-27: *"Yes install that. The treasury needs to be able to manage itself."*

WHY THIS TEST EXISTS. `gas_reserve.py --plan` printed a top-up plan for months and NOTHING could
run it. That gap stranded jordan's book for hours. Building the executor took FIVE passes because
every version reported success while the thing it existed to enable was still blocked — the
false-value family this codebase keeps re-learning, written four times in one afternoon:

  1. targeted the FLOOR, so it said "✅ ALREADY ABOVE TARGET" on a wallet that could not run a
     cycle (the floor sizes a cycle from measured gas; the deploy GATE charges 3,500,000 — an
     entirely different, larger number that a floor-only target ignores);
  2. all-or-nothing on WAVAX — if the wallet held SOME but not ALL of the needed WAVAX it skipped
     straight to a swap it could not afford, and called a solvable problem unsolvable;
  3. sized the unwrap through a FLOAT (`int(0.009079999... * 1e18)` rounded UP past the real
     balance) — `execution reverted` on the very first live run;
  4. gated the FINISHING unwrap with a threshold meant for DECIDING WHETHER TO START, so WAVAX
     bought specifically to become gas was left unconverted;
  5. counted only the unwrap's gas (35k) when the swap leg is 165k — so it happily spent 186k gas
     to close a shortfall smaller than its own cost, and LOWERED the wallet.

Each of those is a rule below. A test that only checked "it runs" would have passed all five.

Run: python3 test_gas_topup.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "gas_topup.py")

ok = 0
fail = 0


def check(name, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS  {name}")
    else:
        fail += 1
        print(f"  FAIL  {name}  {detail}")


def run(args=(), tenant="jordan"):
    env = dict(os.environ)
    env["STEWARD_TENANT"] = tenant
    env["STEWARD_WALLET"] = ("0x572ABd6461BED2258615E6b99c585Ab7c5d05037" if tenant == "jordan"
                             else "0x6c69F8FD6C23A5b6b3ccbCB0d638AA6D527812Fe")
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True,
                          env=env, timeout=400, cwd=HERE)


src = open(SCRIPT).read()

print("")
print("  ── 1. IT TARGETS WHAT THE GATE DEMANDS, NOT WHAT THE FLOOR SAYS ─────────")
check("imports the gate's own budget (RECENTER_GAS) rather than guessing",
      "RECENTER_GAS" in src, "the target must be the strictest gate's requirement")
check("self-sufficiency = full recenter + floor left intact",
      "self_sufficient = recenter_avax + floor" in src)
check("says 'self-sufficient' only when the shortfall is genuinely ZERO",
      "if shortfall_native <= 0:" in src,
      "a 0.0027 AVAX shortfall was once reported as 'ALREADY SELF-SUFFICIENT'")

print("")
print("  ── 2. INTEGER WEI, NEVER A FLOAT, FOR ANY AMOUNT IN A TRANSACTION ──────")
check("unwrap takes integer wei", "amount_wei" in src)
check("a whole balance is never routed through a float to size a tx",
      "int(amount_avax * 1e18)" not in src.split("def unwrap")[1].split("def main")[0]
      or "if amount_wei is None" in src,
      "float round-trip reverted the first live run")
check("clamping to the live balance happens in integer space",
      "min(plan_wei, live_wei)" in src and "min(wavax_wei, need_wei)" in src)

print("")
print("  ── 3. USE WHAT THE BOOK HAS FIRST, THEN BUY ONLY THE REMAINDER ─────────")
check("unwraps the WAVAX present before considering a swap",
      "plan_unwrap" in src and "remainder" in src)
check("the swap amount is sized from the ACTUAL remainder, not the whole need",
      # The remainder must be WEI-EXACT. This check used to pin the FLOAT form
      # `unwrap_need - (plan_wei / 1e18)`, which was itself the bug: subtracting two int-truncated
      # wei counts as floats leaves binary dust (~1e-19 AVAX), and any `remainder > 0` then appended
      # a phantom "sell ~$0.0000 of USDC" leg — measured on 5.7% of plans, intermittently.
      # A test that pins the buggy expression will happily re-introduce it, so assert the integer
      # form is present AND the float form is gone.
      "max(0, need_wei - plan_wei)" in src and "unwrap_need - (plan_wei / 1e18)" not in src)
check("a remainder below the swap floor is dropped, not planned as a step",
      "MIN_SWAP_USD" in src and "remainder_wei < max(1, min_swap_wei)" in src)
check("re-reads the balance before the second step instead of assuming",
      "bal_now = w3.eth.get_balance(me) / 1e18" in src)

print("")
print("  ── 4. THE FINISHING STEP IS TESTED ECONOMICALLY, NOT BY A START FLOOR ──")
check("the final unwrap compares its cost to the gas it produces",
      "take_wei > unwrap_cost_wei" in src,
      "a fixed MIN_UNWRAP_AVAX left bought WAVAX unconverted")
check("the swap leg's gas is counted, not just the unwrap's",
      "SWAP_GAS_EST" in src and "swap_gas_cost" in src,
      "counting only the unwrap made a loss-making top-up look profitable")
check("stopping below cost is EXPLAINED, not silent",
      "NOT WORTH IT" in src)

print("")
print("  ── 5. A FAILED BOOTSTRAP IS LOUD (silence == false success) ────────────")
check("a wallet under the bootstrap floor is refused explicitly",
      "CANNOT BOOTSTRAP" in src)
check("it says no asset here can move without gas",
      "no asset in this wallet can be moved without gas" in src)

print("")
print("  ── 6. DRY-RUN BY DEFAULT (house pattern) ───────────────────────────────")
check("requires BOTH --execute and --yes to send",
      'a.execute and a.yes' in src)
check("does not import a signer unless executing",
      'SI.signer() if a.execute else None' in src)

print("")
print("  ── 7. LIVE: THE REAL RUN ON THE REAL WALLET ────────────────────────────")
r = run()
print(f"      exit={r.returncode}")
out = (r.stdout or "") + (r.stderr or "")
check("it ran against the live chain without raising",
      r.returncode in (0, 1, 3) and "Traceback" not in out,
      f"rc={r.returncode} {out[-200:]}")
check("it reports the gate's requirement and the measured floor separately",
      "a FULL recenter costs" in out and "one measured cycle" in out)
check("it does NOT claim success while short of a full cycle",
      not ("✅ SELF-SUFFICIENT" in out and "SHORTFALL" in out),
      "success and shortfall must not coexist in one report")
check("every decision line is present: shortfall or sufficiency",
      ("SHORTFALL" in out or "SELF-SUFFICIENT" in out or "NOT WORTH IT" in out))
# The verdict must be self-consistent: if it announces a shortfall, it must not also say
# there is nothing to do without explaining WHY.
if "NOT WORTH IT" in out:
    check("when it declines, it explains the cost comparison",
          "COST TO CLOSE" in out and "NOT WORTH IT" in out)

print("")
print("  ── 8. IT IS WIRED IN, NOT AN ORPHAN ───────────────────────────────────")
sy = open(os.path.join(HERE, "sync-treasury-scripts.sh")).read()
check("gas_topup.py is in the sync manifest (or it never deploys)", "gas_topup.py" in sy)
gr = open(os.path.join(HERE, "gas_reserve.py")).read()
check("--plan now points at the executor", "gas_topup.py --execute --yes" in gr)
check("the misleading 'restores 600 cycles' claim is gone",
      "restores {RESERVE_TARGET_OPERATIONS} cycles" not in gr,
      "a display line asserting a number nothing computes")

print("")
print("  ── 9. THE SECOND TENANT REFUSES HONESTLY (found by running it) ────────")
# dadrian's wallet holds $0.00001 USDC — all his capital is DEPLOYED in 21 bins. The tool planned
# "sell ~$0.2952 of USDC", a swap it could not fund, and did not know. A plan presented as
# available when the asset is not there is the same false-value family as everything above.
r2 = run(tenant="dadrian")
out2 = (r2.stdout or "") + (r2.stderr or "")
print(f"      dadrian exit={r2.returncode}")
check("it checks the wallet's LIQUID usdc, not the book's total value",
      "liquid, in the WALLET" in src and "USDC  held" in src)
check("dadrian's run does not plan a swap it cannot fund",
      not ("ACTION" in out2 and "sell ~$" in out2 and "CANNOT BUY" not in out2),
      "planned an unexecutable swap")
# FIXTURE-ROT FIX (2026-09-28): these two checks PINNED dadrian's UNDERFUNDED state. Jordan's gas
# top-up made him SELF-SUFFICIENT (0.06654008 >= 0.03663876), so the "cannot buy" branch is no
# longer reached and both checks failed on a treasury that is now HEALTHIER. A test that goes red
# when the system improves is not testing the property — it is pinning a snapshot, the same defect
# as the wall-clock fixture in test_freshness_and_deploy_read.py. Same day, same family.
# The real invariant holds in BOTH states and is now asserted per-state:
#   self-sufficient -> the tool must SAY so (a reachable verdict, not silence)
#   a gap           -> the tool must explain it AND state that nothing was spent
_self_sufficient = "SELF-SUFFICIENT" in out2
# FIXTURE-ROT FIX #2 (2026-09-28): the tool now correctly REFUSES this top-up, because with the
# phantom float-dust swap leg gone (see gas_topup.py) the whole plan collapses to an unwrap-only
# gap that sits BELOW MIN_SWAP_USD — so "GAP TOO SMALL TO JUSTIFY A TRANSACTION" is the right
# verdict, not an unexplained failure. That branch is a STATED refusal, so accept it here.
# The invariant being protected is "never silent": a run must reach a stated verdict. It must NOT
# be weakened into "any output passes" — keep every named verdict and add only this one.
_stated = (_self_sufficient or "CANNOT BUY" in out2 or "DEPLOYED" in out2
           or "no usable asset" in out2
           or "GAP TOO SMALL TO JUSTIFY A TRANSACTION" in out2)
check("it reaches a STATED verdict (self-sufficient, or an explained gap)",
      _stated, out2[-160:])
check("a dry run always states that nothing was spent",
      (("Nothing was spent" in out2) or ("nothing was spent" in out2)
       or _self_sufficient) and "execute" not in (r2.stderr or ""),
      out2[-160:])

print("")
print("  ── 10. A SMALL GAP IS DISTINGUISHED FROM NO ASSETS ────────────────────")
# Both produced the SAME message once: "the wallet holds no usable asset" — printed for a wallet
# holding 0.065 USDC. Two facts, one message, and the message named the wrong one.
check("the two causes are separated by whether liquid assets exist",
      "has_liquid" in src and "gap_too_small" in src and "nothing_liquid" in src)
check("a gap too small is reported as a gap, not as an absence of assets",
      "GAP TOO SMALL TO JUSTIFY A TRANSACTION" in src)

print("")
print(f"  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok + fail} checks passed")
print("")
sys.exit(0 if fail == 0 else 1)
