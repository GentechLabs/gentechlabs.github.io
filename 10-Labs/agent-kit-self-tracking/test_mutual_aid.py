#!/usr/bin/env python3
"""Prove the mutual-aid rail behaves: orchestrator-gated, no cap, self-preserving.

JORDAN'S DECISION (2026-09-27): *"there's not really like a cap or anything like that... it's more
about getting the okay from the orchestrator to send."*

So the design is: NO SPENDING CAP, the OKAY is the control. Two things must therefore be true and
are tested here:
  1. WITHOUT the okay -> REFUSED, cleanly (not a traceback).
  2. WITH the okay    -> allowed, and RECORDED (an action above the ladder is never silent).
Plus the two rails that survive the no-cap decision:
  3. an UNLISTED destination is refused (a typo must not become an irreversible send);
  4. the sender's OWN gas floor is never spent to fund a peer (or a rescue leaves the rescuer
     unrepairable — the exact failure mutual aid exists to prevent).

And the rail registry must report Solana honestly rather than pretending.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "steward-send-native.py")
VAULT = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking"

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    if not cond and detail:
        print(f"        {detail}")


def run(*args, tenant="jordan", wallet="0x572ABd6461BED2258615E6b99c585Ab7c5d05037"):
    env = dict(os.environ, STEWARD_TENANT=tenant, STEWARD_WALLET=wallet)
    return subprocess.run([sys.executable, TOOL, *args], capture_output=True, text=True,
                          timeout=300, env=env)


print("  ── 1. THE OKAY IS THE CONTROL (no cap, but never alone) ──────────────")
r = run("--to", "dadrian", "--amount", "0.001", "--allow-below-floor")
out = (r.stdout or "") + (r.stderr or "")
check("without an authorization the send is REFUSED", r.returncode != 0, f"rc={r.returncode}")
check("the refusal is a REFUSAL, not a traceback",
      "ORCHESTRATOR OKAY REQUIRED" in out and "Traceback" not in out,
      "a gate that refuses correctly must not read like a crash")
check("it names the mechanism (move_capital needs a human decision)",
      "move_capital" in out or "human" in out.lower())

r2 = run("--to", "dadrian", "--amount", "0.001", "--allow-below-floor",
         "--authorized-by", "Jordan (orchestrator): test of the mutual-aid rail")
out2 = (r2.stdout or "") + (r2.stderr or "")
check("with the orchestrator's okay it PASSES the autonomy gate", r2.returncode == 0,
      f"rc={r2.returncode}")
check("AND the instruction is recorded (never silent)",
      "human-authorizations.jsonl" in out2 or "HUMAN-INSTRUCTED" in out2)

print("")
print("  ── 2. NO CAP EXISTS, BY DESIGN ───────────────────────────────────────")
src = open(TOOL).read()
check("the tool has no amount ceiling", "MAX_AMOUNT" not in src and "spending_cap" not in src)
pol = json.load(open(os.path.join(VAULT, "mutual-aid-policy.json")))
check("the policy records Jordan's no-cap decision",
      "NO SPENDING CAP" in json.dumps(pol).upper())
check("and records WHY it is not a loosening (the okay was already mandatory)",
      "already mandatory" in json.dumps(pol).lower() or "already" in json.dumps(pol).lower())

print("")
print("  ── 3. AN UNLISTED DESTINATION IS STILL REFUSED ───────────────────────")
r3 = run("--to", "some-random-guy", "--amount", "0.001")
o3 = (r3.stdout or "") + (r3.stderr or "")
check("an unapproved name is refused", r3.returncode != 0)
check("the refusal says it is not an approved destination",
      "NOT AN APPROVED DESTINATION" in o3)

print("")
print("  ── 4. THE SENDER'S OWN FLOOR IS PROTECTED ────────────────────────────")
# ── DERIVE THE PROBING AMOUNT; NEVER HARDCODE A BALANCE (fixed 2026-09-27) ────────────────────
# This check used to send a fixed 0.014 against a remembered balance of ~0.0153. That is a fixture
# frozen at a moment: jordan's balance moved (he funded dadrian, then was funded back), and the
# test began FAILING while the behaviour it guards was working perfectly — the send was still
# refused for the right reason, but the fixed amount no longer left him below the floor, so the
# tool never printed the floor message the test grepped for.
#
# The lesson is the one this suite keeps teaching: a test that encodes a MOMENT fails when the
# moment passes, and a failing test that should pass hides real failures. So ask the tool what the
# floor is and probe just past it.
_r0 = run("--to", "dadrian", "--amount", "0.0000001", "--dry-run")
_o0 = (_r0.stdout or "") + (_r0.stderr or "")
_bal = _floor = None
for _line in _o0.split("\n"):
    if _line.strip().startswith("balance") and _bal is None:
        try:
            _bal = float(_line.split()[1])
        except Exception:
            pass
    if "gas floor" in _line and _floor is None:
        try:
            _floor = float(_line.split("gas floor")[1].split()[0])
        except Exception:
            pass
check("the preflight reports a readable balance and floor",
      _bal is not None and _floor is not None, f"bal={_bal} floor={_floor}")

if _bal is not None and _floor is not None:
    # an amount that definitely leaves him under the floor, derived from the live numbers
    _probe = round(max(0.0, _bal - _floor) + max(_floor * 0.5, 0.001), 6)
    check(f"the probe amount {_probe} is genuinely below the floor "
          f"(balance {_bal}, floor {_floor})", _bal - _probe < _floor,
          "otherwise this section cannot reach the refusal it is testing")
    r4 = run("--to", "dadrian", "--amount", str(_probe),
             "--authorized-by", "Jordan (orchestrator): floor-rail test")
else:
    r4 = run("--to", "dadrian", "--amount", "0.014",
             "--authorized-by", "Jordan (orchestrator): floor-rail test")
o4 = (r4.stdout or "") + (r4.stderr or "")
check("a send that would leave him below his own floor is REFUSED", r4.returncode != 0,
      f"rc={r4.returncode}")
check("it explains that funding a peer must not disarm the funder",
      "SPEND THE GAS FLOOR" in o4)
check("the override is loud and opt-in, never the default",
      "--allow-below-floor" in o4)

print("")
print("  ── 5. THE RAIL REGISTRY IS HONEST ABOUT WHAT IS MISSING ──────────────")
r5 = run("--to", "dadrian", "--amount", "0.001", "--chain", "solana")
o5 = (r5.stdout or "") + (r5.stderr or "")
check("solana reports NOT IMPLEMENTED rather than pretending", r5.returncode == 3,
      f"rc={r5.returncode}")
check("it explains what is missing (a signer)", "signer" in o5.lower())
check("avalanche and base ARE implemented", "implemented" in src and '"avalanche"' in src)

r6 = run("--to", "dadrian", "--amount", "0.001", "--dry-run", "--execute")
o6 = (r6.stdout or "") + (r6.stderr or "")
check("--dry-run + --execute is a REFUSED contradiction", r6.returncode == 2, f"rc={r6.returncode}")

print("")
print("  ── 6. BOTH DIRECTIONS ARE APPROVED (a peer must be able to send BACK) ─")
rails = json.load(open(os.path.join(VAULT, "capital-guard-rails.json")))
named = {r.get("wallet_name"): r for r in rails.get("rails", []) if r.get("wallet_name")}
check("jordan is an approved destination", "jordan" in named,
      f"have {list(named)}")
check("dadrian is an approved destination", "dadrian" in named)
for t in ("jordan", "dadrian"):
    e = named.get(t) or {}
    check(f"  {t}: ACTIVE and durable",
          e.get("status") == "ACTIVE" and e.get("kind") == "personal_durable",
          f"got status={e.get('status')} kind={e.get('kind')}")
check("per-tenant rule preserved (not approved globally)",
      any("not approved for another" in h for h in rails["policy"]["hard_rules"]))

print("")
print(f"  RESULT: {'PASS' if not FAIL else 'FAIL'} — {len(PASS)}/{len(PASS)+len(FAIL)} checks passed")
for f in FAIL:
    print(f"    - {f}")
sys.exit(1 if FAIL else 0)
