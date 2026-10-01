#!/usr/bin/env python3
"""Prove the protection layer reads a CURRENT calendar — and STILL fires on a real event.

Jordan, 2026-09-27: *"do what's best for the current situation."* Before acting on the shape, the
shape's own inputs have to be trustworthy. They were not.

THE BUG, measured:
    /var/www/gentechlabs/DeFi/economic-calendar.json  lastUpdated 2026-09-11
    its events still read  time:"TODAY"  ->  "high-impact TODAY: PPI (MoM), PPI (YoY)"
    the file was 245 HOURS (10 days) old when posture read it.

`macro_imminent` was derived purely from the STRINGS inside the file, with NO freshness check. So
PROTECTION fired on every single run, short-circuited to FARM_BIDASK, and **the market and regime
never got a vote on the shape**. Jordan's book read as a bid-ask the market wanted to be a curve
because the only layer wanting bid-ask was reading a ten-day-old file.

TWO RULES THIS TESTS — and the second one matters as much as the first:
  1. a calendar we cannot confirm as CURRENT must ABSTAIN (not assert an event from a stale file);
  2. a genuinely CURRENT calendar with a high-impact event TODAY must STILL FORCE BID-ASK.

Rule 2 is the whole point of the protection layer. A fix that silences the alarm is not a fix — it
is the same defect wearing the opposite mask. Verified on the live system: today is Sunday
2026-09-27, the nearest FOMC was 10 days ago, and the tracker finds nothing in the window — so the
honest current state is "quiet", and it now SAYS quiet rather than asserting a phantom event.

Run: python3 test_calendar_freshness.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

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


def protection_from(cal_obj, age_hours):
    """Run posture's protection layer against a calendar written `age_hours` ago."""
    tmp = tempfile.mkdtemp(prefix="caltest-")
    p = os.path.join(tmp, "economic-calendar.json")
    with open(p, "w") as f:
        json.dump(cal_obj, f)
    old = time.time() - age_hours * 3600
    os.utime(p, (old, old))
    env = dict(os.environ)
    env["STEWARD_CALENDAR_PATHS"] = p
    code = f'''
import os, sys, json
sys.path.insert(0, {HERE!r})
import posture
L = posture.gather("jordan")["protection"]
print("RESULT" + json.dumps(L))
'''
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       cwd=HERE, env=env, timeout=280)
    shutil.rmtree(tmp, ignore_errors=True)
    for line in (r.stdout or "").splitlines():
        if line.startswith("RESULT"):
            try:
                return json.loads(line[6:])
            except Exception:
                return None
    print("      (no result; stderr tail: " + (r.stderr or "")[-200:].replace("\n", " ") + ")")
    return None


TODAY_EVENT = {"name": "CPI (MoM)", "time": "TODAY", "impact": "high", "emoji": "🟠"}
QUIET = {"name": "Weekly Claims", "time": "in 4 days", "impact": "low", "emoji": "⚪"}

print("")
print("  ── 1. A STALE CALENDAR MUST ABSTAIN (this was the live bug) ──────────")
stale = {"lastUpdated": "2026-09-11T12:54:26Z", "date": "Friday, September 11, 2026",
         "events": [TODAY_EVENT]}
for age in (245, 48, 37):
    L = protection_from(stale, age)
    if L is None:
        check(f"{age}h old -> protection unreadable", False, "layer produced no result")
        continue
    check(f"{age}h old -> UNREADABLE, not a phantom 'TODAY' event",
          L.get("readable") is False, f"readable={L.get('readable')} macro_imminent={L.get('macro_imminent')}")
    check(f"  ...and it names the age so the cause is visible",
          str(L.get("stale_hours") or "") != "", f"stale_hours={L.get('stale_hours')}")

print("")
print("  ── 2. A CURRENT CALENDAR WITH A REAL HIGH-IMPACT EVENT MUST STILL FIRE ─")
fresh = {"lastUpdated": "2026-09-27T02:00:00Z", "date": "Sunday, September 27, 2026",
         "events": [TODAY_EVENT]}
L = protection_from(fresh, 1.0)
if L is None:
    check("fresh + high-impact TODAY -> macro_imminent", False, "layer produced no result")
else:
    check("fresh + high-impact TODAY -> macro_imminent TRUE",
          L.get("macro_imminent") is True, f"got {L.get('macro_imminent')}")
    check("  ...and it is READABLE (not abstaining)",
          L.get("readable") is True, f"readable={L.get('readable')}")

print("")
print("  ── 3. A CURRENT CALENDAR WITH NOTHING TODAY MUST BE QUIET, NOT STALE ───")
quiet = {"lastUpdated": "2026-09-27T02:00:00Z", "date": "Sunday, September 27, 2026",
         "events": [QUIET]}
L = protection_from(quiet, 1.0)
if L is None:
    check("fresh + nothing today -> quiet", False, "layer produced no result")
else:
    check("fresh + nothing today -> readable and NOT imminent",
          L.get("readable") is True and L.get("macro_imminent") is False,
          f"readable={L.get('readable')} imminent={L.get('macro_imminent')}")

print("")
print("  ── 4. THE TRACKER MUST WRITE ON A QUIET DAY (the origin of the bug) ───")
# The early `return  # empty = SILENT` skipped the writer entirely, which is how the file froze.
src = open(os.path.join(HERE, "fed-event-tracker.py")).read()
check("the tracker no longer returns without writing",
      "return  # empty = SILENT\n" not in src.replace("\n\n", "\n\n"),
      "early return still present — the file will freeze again")
check("it has ONE shared writer used by both paths",
      src.count("_write_calendar(") >= 3, f"_write_calendar call/def count = {src.count('_write_calendar(')}")
check("a failed write is LOUD, not swallowed",
      "could not refresh the economic calendar" in src, "write failure is still silent")

print("")
print("  ── 5. THE LIVE CALENDAR RIGHT NOW ─────────────────────────────────────")
live = "/var/www/gentechlabs/DeFi/economic-calendar.json"
if os.path.exists(live):
    d = json.load(open(live))
    age_h = (time.time() - os.path.getmtime(live)) / 3600.0
    n = len(d.get("events") or [])
    print(f"      lastUpdated={d.get('lastUpdated')}  mtime age={age_h:.2f}h  events={n}")
    check("the live calendar is now CURRENT (<36h)", age_h < 36, f"age={age_h:.1f}h")
else:
    print("      (live calendar missing)")

print("")
print(f"  RESULT: {'PASS' if fail == 0 else 'FAIL'} — {ok}/{ok + fail} checks passed")
print("")
sys.exit(0 if fail == 0 else 1)
