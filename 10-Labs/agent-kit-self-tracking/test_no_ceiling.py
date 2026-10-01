#!/usr/bin/env python3
"""Prove there is NO amount gate, and that removing it did not remove protection.

Replaces test_tenant_ceiling.py and test_deposit_ceiling.py, which asserted a per-tenant capital
ceiling that Jordan removed on 2026-09-27:

    "we don't need anything blocking anything, okay? We don't need any gates for how much money can
     be in the Agentic Treasury... Any other rules like that are stoppers. We should just go ahead
     and take them out. We want to make this as simple and easy as possible."

A test for a deleted feature is not a passing test, it is a false record. So these do not merely
stop asserting the ceiling — they assert its REMOVAL, and they assert in both directions, because
the thing Jordan did not ask for is for protection to go out with the stopper.

The distinction this file exists to hold:
  * AMOUNT is not a gate. Any sum into an approved destination is permitted.
  * DESTINATION is still a gate. An unknown address is still refused, and a parked venue is still
    refused. That is not a limit on the owner, it is the thing that stops money reaching a place
    nobody approved.

Run: python3 test_no_ceiling.py
"""
import importlib.util
import json
import os
import re
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
CAPITAL_GUARD = os.path.join(HERE, "capital-guard.py")
PROGRESS = os.path.join(HERE, "steward_progress.py")
REGISTRY = os.path.join(HERE, "tenants.json")
RAILS = os.path.join(HERE, "capital-guard-rails.json")

ok = 0
fail = 0


def check(name, cond, detail=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"  PASS  {name}")
    else:
        fail += 1
        print(f"  FAIL  {name} {detail}")


def load_guard():
    """capital-guard.py has a hyphen, so it cannot be imported by name."""
    spec = importlib.util.spec_from_file_location("capital_guard", CAPITAL_GUARD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["capital_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


print("")
print("  ── THE CEILING IS GONE ──────────────────────────────────────────────")

cg = load_guard()
dadrian = json.load(open(REGISTRY))["tenants"]["dadrian"]["wallet"]
cfg = cg.load_rails()

# The amount must never be the reason. Tested at four orders of magnitude, including absurd ones,
# because a cap that only bites above some threshold is exactly what we are trying to prove absent.
for amt in (25, 1_000, 25_000, 1_000_000):
    r = cg.check(cfg, dadrian, chain="avalanche", amount_usd=amt, direction="in", purpose="deposit")
    refused_for_amount = (not r.get("ok")) and "ceiling" in (r.get("reason") or "").lower()
    check(f"${amt:,} into an approved wallet -> no amount gate", not refused_for_amount,
          f"reason={r.get('reason')!r}")

# The function may still exist, but nothing may CALL it. A live caller is the gate.
for path, label in ((CAPITAL_GUARD, "capital-guard.py"), (PROGRESS, "steward_progress.py")):
    src = open(path).read()
    calls = [ln for ln in src.splitlines()
             if "check_tenant_ceiling(" in ln and not ln.strip().startswith(("def ", "#"))]
    check(f"no live caller of the ceiling in {label}", not calls, f"{len(calls)} call(s)")

# And it must not be REPORTED either — a verdict printed is a verdict enforced.
src = open(PROGRESS).read()
check("the deposit report prints no ceiling verdict", "ceiling_ok" not in src)

print("")
print("  ── BUT PROTECTION DID NOT GO OUT WITH IT ────────────────────────────")

r = cg.check(cfg, "0xDEADBEEFdeadbeefDEADBEEFdeadbeefDEADBEEF",
             chain="avalanche", amount_usd=100)
check("an UNKNOWN destination is still refused", r.get("ok") is False and r.get("verdict") == "REFUSED",
      f"got ok={r.get('ok')} verdict={r.get('verdict')}")

# The crash. A KeyError here means check() raises instead of returning a verdict — which a caller
# cannot distinguish from a refusal, and a lenient caller reads as approval.
#
# Checked with an AST, not a grep: the first version of this test grepped the function body and
# FAILED on its own docstring, which quotes the old buggy line. A test that reads prose as code
# reports a defect that is not there — the same false-value family it is meant to catch.
import ast

tree = ast.parse(open(CAPITAL_GUARD).read())
lookup_fn = next((n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "lookup"), None)
check("lookup() exists", lookup_fn is not None)

subscripts = []
if lookup_fn is not None:
    for node in ast.walk(lookup_fn):
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
            subscripts.append(f"{node.value.id}[{ast.unparse(node.slice)}]")
check("lookup() never subscripts a rail field directly (would KeyError on a rail without it)",
      not any(s.startswith("r[") for s in subscripts), f"found {subscripts}")

try:
    cg.lookup(cfg, "0xDEADBEEFdeadbeefDEADBEEFdeadbeefDEADBEEF", "avalanche")
    check("lookup() on an unknown address returns, rather than raising", True)
except Exception as e:                                              # noqa: BLE001
    check("lookup() on an unknown address returns, rather than raising", False,
          f"{type(e).__name__}: {e}")

# A rail with no address is legitimate (venue-level entries are approved by name). It must be
# SKIPPED, not crashed on, and not matched by an empty string.
check("a rail without an address cannot be matched by an empty query",
      cg.lookup(cfg, "", chain="avalanche") is None)

print("")
print("  ── THE RAILS FILE ITSELF ────────────────────────────────────────────")
rails = json.load(open(RAILS))["rails"]
check("every rail still resolves (no rail crashes the lookup)",
      all("address" in r or r.get("name") for r in rails))
has_dadrian = any((r.get("address") or "").lower() == dadrian.lower() for r in rails)
check("dadrian's own wallet is an approved destination (capital can come back)", has_dadrian)

print("")
print(f"  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok + fail} checks passed")
print("")
sys.exit(0 if fail == 0 else 1)
