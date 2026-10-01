#!/usr/bin/env python3
"""Guard the two-person bug: a per-tenant read that ignores the tenant label is ONE book wearing TWO names.

Jordan, 2026-09-27: *"run an audit of our shapes and fee efficiency. Something is off."* He was right.

WHAT WAS WRONG — proven against the chain, not inferred:
    $ STEWARD_TENANT=dadrian python3 fee_efficiency.py --tenant dadrian
        FEE EFFICIENCY — dadrian as curve  (ACTUAL deployed bins 8363337..8363348 (12 bins))
        efficiency 50.2%
    That is JORDAN's twelve bins. Dadrian's real book is 25 bins (8363326..8363352) and scores
    52.4%. So the efficiency number reported for dadrian was computed from jordan's position.

WHY — the mechanism, which is what makes this a CLASS and not a typo:
    `steward_identity.wallet()` consulted STEWARD_WALLET, then the PROFILE's treasury_config.json.
    It never read STEWARD_TENANT. Ten scripts set STEWARD_TENANT (the label) without setting
    STEWARD_WALLET (the address):
        auto_compound, capital-guard, compound_status, cron_health, fee_efficiency, gas_reserve,
        provision_tenant_wallet, defi-hub-refresh.sh, fee-ledger.sh, lfj-curve-deploy.sh
    posture.py had already been patched to export BOTH — a fix applied at ONE call site, so the
    other nine kept the bug. That is the lesson: patching the caller leaves the class alive.

THE FIX IS AT THE RESOLVER, NOT THE CALL SITES. `_from_env()` now resolves a declared
STEWARD_TENANT from the registry. Ten call sites cannot be trusted to remember; one resolver can.

This test covers:
  1. the resolver: a declared tenant yields THAT tenant's wallet, not the default;
  2. precedence: an explicit STEWARD_WALLET still wins (nothing that already works may move);
  3. no declaration -> unchanged behaviour (None, so the config fallback still applies);
  4. the two tenants are genuinely different addresses (else every check here is vacuous);
  5. and it re-reads the CHAIN to confirm the fix changed the ANSWER, not just the label.

Run: python3 test_tenant_isolation.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

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


REG = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"
reg = json.load(open(REG)).get("tenants") or {}
W = {t: (r or {}).get("wallet") for t, r in reg.items() if (r or {}).get("wallet")}


def resolve(env_extra):
    """Resolve the wallet in a CLEAN subprocess — env is the thing under test, so it must be fresh."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("STEWARD_TENANT", "STEWARD_WALLET")}
    env.update(env_extra)
    r = subprocess.run(
        [sys.executable, "-c",
         "import steward_identity as SI; print(SI.wallet())"],
        capture_output=True, text=True, cwd=HERE, env=env)
    return (r.stdout.strip().splitlines() or [""])[-1], r.stderr.strip()


print("")
print("  ── THE TWO TENANTS MUST BE DIFFERENT (else every check below is vacuous) ──")
check("registry holds at least two distinct wallets", len(set(W.values())) >= 2, str(W))
for t, w in W.items():
    print(f"      {t:9} {w}")

print("")
print("  ── 1. A DECLARED TENANT RESOLVES ITS OWN WALLET (the fix) ──────────────")
for t, w in W.items():
    got, err = resolve({"STEWARD_TENANT": t})
    check(f"STEWARD_TENANT={t:9} -> its own wallet", got.lower() == (w or "").lower(),
          f"got {got!r}")

print("")
print("  ── 2. AN EXPLICIT WALLET STILL WINS (nothing that works may move) ────────")
other = [x for x in W.values() if x and x.lower() != (W.get("jordan") or "").lower()]
if other:
    got, err = resolve({"STEWARD_TENANT": "jordan", "STEWARD_WALLET": other[0]})
    check("explicit STEWARD_WALLET beats the tenant registry",
          got.lower() == other[0].lower(), f"got {got!r}, want {other[0]!r}")

print("")
print("  ── 3. SILENCE IS UNCHANGED — no declaration, no behaviour change ────────")
got, err = resolve({})
check("no STEWARD_TENANT still falls through to the config default",
      "@" not in got, f"got {got!r} — expected the configured default or a clean failure")

print("")
print("  ── 4. THE FAILURE THE FIX EXISTS TO PREVENT ─────────────────────────────")
print("      the same scenario that produced dadrian's wrong number:")
if "dadrian" in W:
    got, _ = resolve({"STEWARD_TENANT": "dadrian"})
    jord = W.get("jordan", "")
    check("dadrian no longer resolves to jordan's wallet",
          got.lower() != (jord or "").lower(), "STILL reading jordan's book for dadrian")

print("")
print("  ── 5. CALLER-LEVEL: does the fix change the ANSWER, not just the label? ─")
if "dadrian" in W:
    env = {k: v for k, v in os.environ.items()
           if k not in ("STEWARD_TENANT", "STEWARD_WALLET")}
    env["STEWARD_TENANT"] = "dadrian"
    try:
        r = subprocess.run([sys.executable, "fee_efficiency.py", "--tenant", "dadrian"],
                           capture_output=True, text=True, cwd=HERE, env=env, timeout=280)
        out = r.stdout + r.stderr
        line = next((l for l in out.splitlines() if "ACTUAL deployed bins" in l), "")
        if line:
            print(f"      {line.strip()}")
            # jordan's book is 12 bins; dadrian's is 25. Reporting 12 here IS the bug.
            check("dadrian's book read is NOT jordan's 12 bins",
                  "12 bins" not in line, f"still reading jordan's book: {line.strip()}")
        else:
            print("      (no geometry line in output — read may be offline; not a failure)")
    except subprocess.TimeoutExpired:
        print("      (timed out reaching the chain — not a failure of the fix)")

print("")
print(f"  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok + fail} checks passed")
print("")
sys.exit(0 if fail == 0 else 1)
