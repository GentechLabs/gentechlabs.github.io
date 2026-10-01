#!/usr/bin/env python3
"""test_action_log.py — the action log must be an audit, not a diary.

Run:  python3 test_action_log.py
Two properties, and the second is the one that earns the log its place:
  1. Every line is self-describing AND filterable -- an outcome that cannot be found by the same
     query as its intent is a record that hides things.
  2. FAIL-SOFT is absolute: the log must never be the reason a money path fails.
"""
import importlib.util, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
fails = []
checks = []


def check(name, cond, detail=""):
    checks.append(name)
    print(f"  {'PASS' if cond else 'FAIL'} — {name}" + (f"  [{detail}]" if detail else ""))
    if not cond:
        fails.append(name)


spec = importlib.util.spec_from_file_location("al", os.path.join(HERE, "steward_action_log.py"))
al = importlib.util.module_from_spec(spec)
spec.loader.exec_module(al)

tmp = os.path.join(tempfile.mkdtemp(), "action.jsonl")
al.LOG_PATH = tmp

# ── a complete action: intent, then result with its receipt ─────────────────────────────────────
eid = al.log_intent("watchdog", "recenter", reason="efficiency 41% < 75% floor",
                    before={"bins": 45, "usd": 107.88, "shape": "bid-ask"},
                    decided_by="machine", provenance="TREASURY-CONSTITUTION.md Part 3A",
                    chain="avalanche", venue="lfj-v22")
al.log_result(eid, "ok", after={"bins": 40, "usd": 103.66, "shape": "curve"},
              txs=[{"hash": "0xdeadbeef", "block": 96458806, "leg": "bid"}])

# ── an action that started and never finished — the query that matters most ─────────────────────
al.log_intent("watchdog", "rebalance", reason="dies mid-action", decided_by="machine")

ev = al.read_events()

check("every line carries the mandatory fields",
      all(all(k in r for k in al.MANDATORY) for r in ev), f"{len(ev)} events")

res = [r for r in ev if r.get("phase") == "result"]
check("a result line names its own actor and verb",
      res and res[0].get("actor") == "watchdog" and res[0].get("verb") == "recenter")
check("a result line carries its on-chain receipt",
      res and res[0].get("txs") and res[0]["txs"][0]["hash"] == "0xdeadbeef")

# THE ONE THAT CAUGHT A REAL BUG: the decided_by filter must see intents AND their outcomes.
m = al.read_events(decided_by="machine")
check("filtering by decided_by sees intents AND results (not intents only)",
      len(m) == 3, f"{len(m)} of 3")

check("filtering by verb works the same way",
      len(al.read_events(verb="recenter")) == 2, f"{len(al.read_events(verb='recenter'))} of 2")

g = al.gaps()
check("gaps() finds the action that started and never finished",
      len(g) == 1 and g[0]["verb"] == "rebalance", f"{len(g)} gap(s)")

check("a completed action is NOT reported as a gap",
      all(x["verb"] != "recenter" for x in g))

# ── FAIL-SOFT: unwritable path must not raise, and must not lie ─────────────────────────────────
real = al.LOG_PATH
al.LOG_PATH = "/proc/nonexistent/dir/action.jsonl"
raised = False
try:
    r = al.log_intent("x", "test")
except Exception:
    raised = True
    r = None
check("an unwritable log does NOT raise", not raised)
check("an unwritable log returns empty rather than a fake event id", r == "", repr(r))
check("reading a missing log returns [] rather than raising", al.read_events() == [])
al.LOG_PATH = real

check("an invalid decided_by is coerced, not silently trusted",
      (al.log_intent("x", "t", decided_by="nonsense"), al.read_events()[-1]["decided_by"])[1] == "unknown")

print(f"\n  RESULT: {'PASS' if not fails else 'FAIL'} — {len(checks) - len(fails)}/{len(checks)} checks passed")
if fails:
    for f in fails:
        print(f"    FAILED: {f}")
sys.exit(1 if fails else 0)
