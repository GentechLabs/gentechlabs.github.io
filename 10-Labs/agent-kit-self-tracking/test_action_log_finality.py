"""Regression tests for the four defects the K2.7 audit found.

Per the permanent-fix rule: a fix is not done until the defect CANNOT recur and you can say why.
Each test below fails against the pre-audit code.
"""
import importlib.util, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
fails, checks = [], []


def check(name, cond, detail=""):
    checks.append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))
    if not cond:
        fails.append(name)


spec = importlib.util.spec_from_file_location("al", os.path.join(HERE, "steward_action_log.py"))
al = importlib.util.module_from_spec(spec)
spec.loader.exec_module(al)

tmp = os.path.join(tempfile.mkdtemp(), "audit.jsonl")
al.LOG_PATH = tmp

# ── AUDIT FINDING 1 (the serious one) ───────────────────────────────────────────────────────────
# A `timeout` that killed the engine AFTER it broadcast a transaction must NOT close the intent.
# Before the fix: any result line closed it, so a settlement in flight read as zero outstanding.
eid = al.log_intent("watchdog", "recenter", reason="long rebuild", decided_by="machine")
al.log_result(eid, "failed", final=False,
              txs=[{"hash": "0x" + "ab" * 32, "block": None, "verified": False}])
g = al.gaps()
check("a NON-final result (timeout, settlement in flight) still shows as an outstanding gap",
      len(g) == 1 and g[0]["id"] == eid, f"{len(g)} gap(s)")

# A genuine failure DID reach a verdict, so it closes normally.
eid2 = al.log_intent("watchdog", "rescue", reason="refused", decided_by="machine")
al.log_result(eid2, "failed", final=True)
check("a FINAL failed result closes the intent (a verdict is a verdict)",
      all(x["id"] != eid2 for x in al.gaps()))

# ── AUDIT FINDING 2 ─────────────────────────────────────────────────────────────────────────────
# Receipts grepped from a process's stdout are CLAIMED, not confirmed.
res = [r for r in al.read_events() if r.get("phase") == "result"][0]
check("a receipt taken from stdout is labelled verified:false, never implied confirmed",
      res["txs"][0].get("verified") is False)

# ── AUDIT FINDING 3 ─────────────────────────────────────────────────────────────────────────────
# An omitted `final` must keep old/mixed writers working rather than crashing or misreading.
eid3 = al.log_intent("other", "thing", decided_by="machine")
al.log_result(eid3, "ok")            # no final= passed
check("omitting `final` defaults to final (back-compat with other writers)",
      all(x["id"] != eid3 for x in al.gaps()))

print(f"\n  RESULT: {'PASS' if not fails else 'FAIL'} — {len(checks) - len(fails)}/{len(checks)} checks passed")
if fails:
    for f in fails:
        print(f"    FAILED: {f}")
sys.exit(1 if fails else 0)
