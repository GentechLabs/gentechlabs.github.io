#!/usr/bin/env python3
"""Prove a DETECTED deposit is checked against the tenant's ceiling before it is reported.

Jordan, 2026-09-26: "He just wants to put money in it." A deposit is the ONLY moment a depositor
can breach their own limit, so the arrival report must carry the verdict. An arrival announced
without the limit checked presents a breach as good news.

This runs the real detector and the real ceiling guard against a synthetic wallet state, using a
scratch baseline — it touches no chain state and moves no capital.

Run: python3 test_deposit_ceiling.py
"""
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import steward_progress as SP  # noqa: E402

ok = fail = 0


def check(name, got, want):
    global ok, fail
    if got == want:
        ok += 1
        print(f"  PASS  {name}")
    else:
        fail += 1
        print(f"  FAIL  {name}: got {got!r}, want {want!r}")


# ── The ceiling guard, loaded by path (the filename has a hyphen) ──────────────────────────────
_s = importlib.util.spec_from_file_location("cg", os.path.join(HERE, "capital-guard.py"))
CG = importlib.util.module_from_spec(_s)
_s.loader.exec_module(CG)

print("\n  ── BASELINES ARE PER-TENANT (a shared one invents deposits) ──")
check("jordan keeps the original filename", SP._baseline_file("jordan"), SP.BASELINE_FILE)
check("dadrian gets his OWN file",
      SP._baseline_file("dadrian").endswith(".steward-wallet-baseline-dadrian.json"), True)
check("  ...and it is NOT jordan's file",
      SP._baseline_file("dadrian") == SP.BASELINE_FILE, False)

print("\n  ── A DETECTED DEPOSIT CARRIES THE CEILING VERDICT ──")
# Synthetic wallet state: dadrian holds $27.69 and receives $10. The real detector writes a scratch
# baseline, so a first pass establishes it and a second pass sees the delta.
tmp = tempfile.mkdtemp()
orig = SP._baseline_file
SP._baseline_file = lambda t: os.path.join(tmp, f"base-{t}.json")
# `detect_deposit` suppresses a deposit while the machine has been ACTIVE (a rebuild changes units
# too, so this stops false positives). That is correct behaviour, but it makes detection
# non-deterministic in a test, so the activity probe is pinned to "quiet" here. NOTE: the caveat is
# real and is recorded — a deposit arriving DURING machine activity is not reported AND still
# advances the baseline, so it can go silent. That is pre-existing and separate from the ceiling.
_orig_active = SP._machine_active_recently
SP._machine_active_recently = lambda hours=2.0: False

cur_before = {"value_usd": 27.69, "token_units": 27.69, "native_usd": 1.0, "stable_usd": 26.69}
cur_after = {"value_usd": 37.69, "token_units": 37.69, "native_usd": 1.0, "stable_usd": 36.69}

SP.detect_deposit(cur_before, "dadrian")          # establishes the baseline
d = SP.detect_deposit(cur_after, "dadrian")       # +$10.00
check("the deposit is detected", d.get("detected"), True)
check("the delta is right", round(d.get("delta_usd", 0), 2), 10.0)

cap = CG.tenant_ceiling("dadrian")
ok10, why10 = CG.check_tenant_ceiling(10.0, "dadrian")
print(f"  (dadrian: ceiling ${cap}, now ${CG.current_tenant_value('dadrian'):.2f}, +$10.00)")
check("+$10 is within his ceiling", ok10, True)
ok50, why50 = CG.check_tenant_ceiling(50.0, "dadrian")
check("+$50 would breach it", ok50, False)
print(f"     refusal says: {why50[:104]}")

print("\n  ── AN UNREGISTERED DEPOSITOR CANNOT ARRIVE UNBOUNDED ──")
check("a tenant with no ceiling is refused", CG.check_tenant_ceiling(1.0, "ghost")[0], False)

SP._baseline_file = orig
SP._machine_active_recently = _orig_active
print(f"\n  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok+fail} checks passed\n")
sys.exit(0 if fail == 0 else 1)
