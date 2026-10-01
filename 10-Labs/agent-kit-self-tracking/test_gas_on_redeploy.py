#!/usr/bin/env python3
"""Prove the redeploy PROVISIONS GAS — Jordan's 20c rule, enforced on the money path.

JORDAN, 2026-09-27: *"once you like redeploy, just go ahead and make sure you keep 20 cents worth of
Avax for gas. So that way, even though we're low right now, we're below our cap, we can fix it on
the next redeployment."*

THE GAP THIS CLOSES: the recenter PRESERVED native AVAX but never CREATED it. Its composition step
sizes the deploy against `deployable = wallet MINUS reserve`, so it could hold a reserve back but
had no way to RESTORE one. A wallet already under the floor could never recover through a redeploy
— it would rebuild the book and stay exactly as under-funded as before.

What is tested here:
  1. the step EXISTS and is invoked with --execute;
  2. it sits AFTER the withdraw and BEFORE the swap/deploy — the only window where the freed WAVAX
     is still unspent, so unwrapping there provisions the most gas;
  3. it is ADVISORY: a provisioning failure must not abort a rebuild (thin gas is bad, a stranded
     book is worse);
  4. FLOOR_USD is 0.20 and the dollar term is a true floor (max, never a substitute).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking"
SRC = open(os.path.join(VAULT, "lfj_recenter.py")).read()
GR = open(os.path.join(VAULT, "gas_reserve.py")).read()

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    if not cond and detail:
        print(f"        {detail}")


print("  ── 1. THE STEP EXISTS ON THE MONEY PATH ────────────────────────────")
check("the recenter invokes gas_topup.py", "gas_topup.py" in SRC)
check("and it does so with --execute (not a plan that does nothing)",
      re.search(r"gas_topup\.py\"\),\s*\n?\s*\"--execute\"", SRC) is not None
      or '"--execute", "--yes"]' in SRC)
check("the step is labelled so it is visible in the log", "[4a]" in SRC)

print("")
print("  ── 2. ORDERING: after WITHDRAW, before the SWAP/DEPLOY ──────────────")
# Anchor on the real PRINT statements, not bare substrings.
#
# ⚠️ These anchors used to be plain `SRC.find("[4a] PROVISION GAS")`. That matches ANY occurrence of
# the text — including a COMMENT or DOCSTRING that merely mentions the stage, which appears earlier in
# the file than the stage itself. A docstring added 2026-09-27 that referenced "[4a] PROVISION GAS"
# therefore made this check FAIL while the actual execution order was untouched: the test was
# measuring "where does this text first appear", not "in what order do the steps run".
#
# A guard that a comment can break is a guard that reports on prose, not behaviour — and the obvious
# "fix" for a developer under time pressure is to delete the comment. Anchor on the print statement
# that actually emits the stage label, so only real code can satisfy it.
def _stage_index(label, *, literal=True):
    """Index of the `print(...)` statement that emits `label`. -1 if absent."""
    pat = (r'print\(\s*"[^"]*' + re.escape(label)) if literal \
        else (r'print\(\s*f"[^"]*' + re.escape(label))
    m = re.search(pat, SRC)
    return m.start() if m else -1


i_withdraw = _stage_index("[4] WITHDRAW")
i_provision = _stage_index("[4a] PROVISION GAS")
i_swap = _stage_index("[4b] REBALANCE", literal=False)
i_deploy = _stage_index("[5] RE-DEPLOY", literal=False)
check("all four stages are present", -1 not in (i_withdraw, i_provision, i_swap, i_deploy),
      f"withdraw={i_withdraw} provision={i_provision} swap={i_swap} deploy={i_deploy}")
check("the anchors are PRINT statements, not comments or docstrings",
      all(SRC[i:i + 6] == "print(" for i in
          (i_withdraw, i_provision, i_swap, i_deploy) if i >= 0))
check("PROVISION comes AFTER the withdraw (the capital must have been freed first)",
      i_withdraw < i_provision, f"{i_withdraw} vs {i_provision}")
check("PROVISION comes BEFORE the swap (which would otherwise consume the WAVAX)",
      i_provision < i_swap, f"{i_provision} vs {i_swap}")
check("PROVISION comes BEFORE the redeploy (so the deploy is sized against a restored floor)",
      i_provision < i_deploy, f"{i_provision} vs {i_deploy}")

print("")
print("  ── 3. IT IS ADVISORY — A REBUILD MUST NOT DIE OVER GAS ─────────────")
blk = SRC[i_provision:i_swap]
check("a provisioning failure is reported, not raised", "ℹ️" in blk)
check("and it explicitly says the book is rebuilt regardless",
      "rebuilt" in blk.lower() or "continuing" in blk.lower())
check("it does NOT return/abort on failure",
      not re.search(r"gt\.returncode\s*!=\s*0[^\n]*\n[^\n]*return", blk),
      "an advisory step must not abort the money path")
check("the capture is guarded (a crash in the child must not kill the parent)",
      "capture_output=True" in blk)

print("")
print("  ── 4. THE 20c FLOOR IS REAL AND CANNOT LOWER THE RESERVE ───────────")
check("FLOOR_USD is 0.20 (restored from the drifted 0.10)",
      re.search(r"^FLOOR_USD = 0\.20", GR, re.M) is not None,
      "expected FLOOR_USD = 0.20")
check("the floor is a MAX, so the dollar term can only raise it",
      re.search(r"max\(", GR) is not None and "FLOOR_USD" in GR)
check("the docstring records Jordan's words for the raise",
      "20 cents worth of AVAX" in GR)
check("and records that 20c was a RESTORATION, not a new rule",
      "GO BACK TO" in GR)

print("")
print("  ── 5. NO DEADLOCK: the child must not take the wallet lock ──────────")
topup = open(os.path.join(VAULT, "gas_topup.py")).read()
check("gas_topup does NOT acquire the wallet lock (the parent already holds it)",
      "agent_lock" not in topup and "acquire_or_exit" not in topup,
      "a nested flock on the same fd would deadlock the recenter")
check("but the PARENT does hold the lock while this runs",
      "acquire_or_exit" in SRC)

print("")
print(f"  RESULT: {'PASS' if not FAIL else 'FAIL'} — {len(PASS)}/{len(PASS)+len(FAIL)} checks passed")
for f in FAIL:
    print(f"    - {f}")
sys.exit(1 if FAIL else 0)
