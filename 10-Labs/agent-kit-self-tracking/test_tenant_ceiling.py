#!/usr/bin/env python3
"""Prove the per-tenant capital ceiling REFUSES correctly, in every direction.

Jordan, 2026-09-26: "his agentic treasury should follow the same RULES mine does. He would prefer
I manage it for him ... He just wants to put money in it."

The rules are shared; the ceiling is personal. Because Jordan is NOT going to be the one watching
a collaborator's balance, this guard must be right without him — so every failure mode is a
REFUSAL, never a warning, and never a silent pass.

Run: python3 test_tenant_ceiling.py
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# `capital-guard.py` has a hyphen, so it cannot be imported by name — load it by path.
import importlib.util  # noqa: E402

_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capital-guard.py")
_spec = importlib.util.spec_from_file_location("capital_guard", _p)
CG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CG)  # noqa: E402

ok = fail = 0


def check(name, got, want):
    global ok, fail
    if got == want:
        ok += 1
        print(f"  PASS  {name}")
    else:
        fail += 1
        print(f"  FAIL  {name}: got {got!r}, want {want!r}")


print("\n  ── DADRIAN: WITHIN, AT, AND OVER HIS CEILING ──")
print(f"  (his registered ceiling: ${CG.tenant_ceiling('dadrian')})")
cur = CG.current_tenant_value("dadrian")
print(f"  (his current value:       ${cur})\n")

cap = CG.tenant_ceiling("dadrian")
check("a small deposit is permitted", CG.check_tenant_ceiling(5.0, "dadrian")[0], True)
check("  ...and a deposit landing exactly ON the ceiling is permitted",
      CG.check_tenant_ceiling(cap - cur, "dadrian")[0], True)
check("one cent over the ceiling is REFUSED",
      CG.check_tenant_ceiling(cap - cur + 0.01, "dadrian")[0], False)
check("a large deposit is REFUSED", CG.check_tenant_ceiling(500.0, "dadrian")[0], False)

print("\n  ── FAIL CLOSED: the three ways this could be fooled ──")
# 1. No ceiling registered. An unset limit must not mean unlimited — that is the whole point.
_orig = CG.tenant_ceiling
CG.tenant_ceiling = lambda t=None: None
check("NO ceiling registered -> REFUSED (not unlimited)",
      CG.check_tenant_ceiling(1.0, "dadrian")[0], False)
CG.tenant_ceiling = _orig

# 2. Balance unreadable. We cannot say whether a deposit fits, so we must not say it does.
_origv = CG.current_tenant_value
CG.current_tenant_value = lambda t=None: None
check("balance UNREADABLE -> REFUSED (an unreadable balance is not zero)",
      CG.check_tenant_ceiling(1.0, "dadrian")[0], False)
CG.current_tenant_value = _origv

# 3. A non-numeric amount. Refuse rather than guess.
check("non-numeric amount -> REFUSED", CG.check_tenant_ceiling("lots", "dadrian")[0], False)

print("\n  ── JORDAN IS NOT CAPPED BY A COLLABORATOR LIMIT ──")
# His ceiling is his total allocation, set by him directly, and reads None. But an amount he DOES
# supply must still not be silently permitted through a collaborator guard with no limit.
check("jordan has no collaborator ceiling registered",
      CG.tenant_ceiling("jordan"), None)
check("  ...so a sized deposit for him is REFUSED rather than passed as unlimited",
      CG.check_tenant_ceiling(10.0, "jordan")[0], False)

print("\n  ── AN UNKNOWN TENANT CANNOT BORROW SOMEONE ELSE'S LIMIT ──")
check("unknown tenant has no ceiling", CG.tenant_ceiling("nobody"), None)
check("  ...so it is REFUSED", CG.check_tenant_ceiling(1.0, "nobody")[0], False)

print(f"\n  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok+fail} checks passed\n")
sys.exit(0 if fail == 0 else 1)
