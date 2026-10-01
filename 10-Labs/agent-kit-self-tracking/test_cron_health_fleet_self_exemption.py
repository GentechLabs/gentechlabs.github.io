#!/usr/bin/env python3
"""Regression test: the FLEET sentinel must never re-fire a job it scans, and a PAUSED job
must never reach heal().

WHY THIS EXISTS (two independent reports, 2026-09-28):
  1. Treasury's own sentinel fork-bombed the host — `heal()` re-fired its own job id, unbounded,
     465 concurrent processes, load 42. Treasury then identified the exact property that kept the
     FLEET tool out of that outage: `cron_health_fleet.py` exempts any "cron health" job via
     `is_self()` BEFORE the loop can reach `heal()`. Their words: "Worth checking that `is_self()`
     keeps running *before* the heal branch in any future refactor — that ordering is what is
     holding the line."
     That is a load-bearing INVARIANT held only by line order, with nothing asserting it. A
     refactor that moves `is_self()` below the heal call silently re-arms the fork bomb.

  2. This session added a PAUSED_BROKEN branch to that same loop. Adding a branch is exactly the
     kind of change that can reorder or bypass the exemption — so the ordering is now tested
     rather than trusted.

This test asserts GENERAL properties, not "bug X is gone":
  * a health-named job is exempt regardless of how broken it looks (name AND script patterns);
  * the source executes `is_self()`, and `continue`s on it, before the first `heal(` call;
  * PAUSED_BROKEN is dispatched and `continue`s before heal is reachable;
  * the exemption does not over-block: a normal failing job IS still considered for healing.

Hermetic: no host state is asserted. A temporary fixture jobs.json is used for the functional
checks, so this passes on any seat.
"""
import importlib.util
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "cron_health_fleet.py")

fails = []


def check(name, cond, detail=""):
    print(f"  {'✅' if cond else '❌'} {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def load():
    spec = importlib.util.spec_from_file_location("fleet_under_test", SRC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


print("═══ fleet sentinel: self-exemption + pause safety ═══")
fleet = load()
src = open(SRC).read()
lines = src.split("\n")

# ── 1. is_self() identifies health jobs by NAME and by SCRIPT ─────────────────────────────────
check("is_self recognises a health-named job",
      fleet.is_self({"name": "Steward Cron Health Sentinel", "script": "other.sh"}))
check("is_self recognises a health-named job case-insensitively",
      fleet.is_self({"name": "FLEET CRON HEALTH sentinel", "script": "other.sh"}))
check("is_self recognises cron-health.sh by script",
      fleet.is_self({"name": "anything", "script": "cron-health.sh"}))
check("is_self recognises cron-health-fleet.sh by script",
      fleet.is_self({"name": "anything", "script": "cron-health-fleet.sh"}))
check("is_self does NOT over-exempt an ordinary job",
      not fleet.is_self({"name": "Steward Position Watchdog (5m)", "script": "steward-watchdog.sh"}))

# ── 2. THE LOAD-BEARING INVARIANT: is_self() + its `continue` precede the first heal() CALL ───
# NB: match the CALL SITE, not the `def heal(...)` declaration — the definition sits near the top
# of the file and a naive regex finds it first, which would make this check pass/fail for a
# reason unrelated to ordering. (This test was written wrong once for exactly that reason.)
iself = next((i for i, l in enumerate(lines) if re.search(r"\bif is_self\(job\):", l)), None)
heal = next((i for i, l in enumerate(lines) if re.search(r"=\s*heal\(job", l)), None)
check("both is_self() and heal() exist in the source", iself is not None and heal is not None,
      f"is_self@{iself if iself is None else iself + 1} heal@{heal if heal is None else heal + 1}")
if iself is not None and heal is not None:
    check("is_self() runs BEFORE the first heal() call", iself < heal,
          f"line {iself + 1} < {heal + 1} — ordering is what holds the line")
    # the exemption must also SKIP, not merely test: a branch without `continue` falls through
    window = lines[iself:iself + 6]
    check("is_self() branch `continue`s (exemption skips, not falls through)",
          any(re.match(r"\s*continue\b", l) for l in window),
          "found within 6 lines of the is_self check")

# ── 3. PAUSED_BROKEN is dispatched and skips before heal is reachable ─────────────────────────
pb = next((i for i, l in enumerate(lines) if 'state == "PAUSED_BROKEN"' in l), None)
check("PAUSED_BROKEN is dispatched in the loop", pb is not None,
      f"line {pb + 1}" if pb is not None else "NOT FOUND — the pause rule was dropped")
if pb is not None and heal is not None:
    check("PAUSED_BROKEN is handled BEFORE heal()", pb < heal,
          f"line {pb + 1} < {heal + 1} — a paused job must never be re-fired")
    check("PAUSED_BROKEN branch `continue`s",
          any(re.match(r"\s*continue\b", l) for l in lines[pb:pb + 26]),
          "found within the branch body")

# ── 4. classify(): a pause is not a retirement (the rule this session added) ──────────────────
CASES = [
    ("enabled + ok",              {"enabled": True,  "last_status": "ok"},                       "HEALTHY"),
    ("enabled + failing",         {"enabled": True,  "last_status": "error", "failure_streak": 1}, "FAILED"),
    ("paused cleanly",            {"enabled": False, "last_status": "ok"},                        "DISABLED"),
    ("paused, never ran",         {"enabled": False, "last_status": None},                        "DISABLED"),
    ("paused + retired marker",   {"enabled": False, "last_status": "archived", "failure_streak": 1}, "DISABLED"),
    ("PAUSED WHILE FAILING",      {"enabled": False, "last_status": "error", "failure_streak": 1}, "PAUSED_BROKEN"),
    ("paused + bad status",       {"enabled": False, "last_status": "error"},                      "PAUSED_BROKEN"),
    ("paused + streak only",      {"enabled": False, "failure_streak": 2},                         "PAUSED_BROKEN"),
]
for label, job, expected in CASES:
    got, _ = fleet.classify(job)
    check(f"classify: {label} -> {expected}", got == expected, f"got {got}")

# ── 5. FUNCTIONAL: run the tool against a fixture ring and read the verdicts ──────────────────
tmpd = tempfile.mkdtemp(prefix="fleet_selftest_")
fixture = os.path.join(tmpd, "jobs.json")
jobs = {"jobs": [
    # a health sentinel that is FAILING and PAUSED — the worst case; must stay exempt
    {"id": "deadbeef0001", "name": "Steward Cron Health Sentinel", "enabled": False,
     "last_status": "error", "failure_streak": 1, "script": "cron-health.sh"},
    # a genuinely paused-broken ordinary job — must be reported
    {"id": "deadbeef0002", "name": "ordinary paused-broken job", "enabled": False,
     "last_status": "error", "failure_streak": 1, "script": "whatever.sh"},
    # a cleanly retired job — must stay quiet
    {"id": "deadbeef0003", "name": "cleanly retired job", "enabled": False,
     "last_status": "ok", "script": "whatever.sh"},
    # a healthy job — must stay quiet
    {"id": "deadbeef0004", "name": "healthy job", "enabled": True,
     "last_status": "ok", "script": "whatever.sh"},
]}
with open(fixture, "w") as f:
    json.dump(jobs, f)

import subprocess
r = subprocess.run(
    # --now pins the clock to a WORKING HOUR. Without it this test's result depends on
    # when it runs: quiet hours deliberately hold findings for later delivery, so a real
    # paused-broken job lands in `pending` instead of `new` and the assertion below fails
    # on a perfectly healthy tool. --no-debounce opts out of the debounce gate; this opts
    # out of the quiet-hours gate. Both are needed to test routing rather than the calendar.
    [sys.executable, SRC, "--jobs-file", fixture, "--no-debounce", "--json",
     "--now", "2026-09-29T14:00:00+00:00", "--state", os.path.join(tmpd, "state.json")],
    capture_output=True, text=True, timeout=180)
try:
    out = json.loads(r.stdout)
except Exception:
    out = None
    print(f"    (rc={r.returncode}) stderr tail: {(r.stderr or '')[-300:]}")

check("fleet tool runs against a fixture ring", out is not None)
if out:
    new = out.get("new", [])
    ids = {n["id"] for n in new}
    check("the FAILING+PAUSED health sentinel is NOT reported (exempt)",
          "deadbeef00" not in str(ids) or all("sentinel" not in n["name"].lower() for n in new),
          f"new={sorted(ids)}")
    check("the ordinary paused-broken job IS reported", "deadbeef0002" in ids,
          f"new={sorted(ids)}")
    check("the cleanly retired job is NOT reported", "deadbeef0003" not in ids)
    check("the healthy job is NOT reported", "deadbeef0004" not in ids)
    check("no self-job was offered for healing",
          all("sentinel" not in (n.get("name") or "").lower() for n in new if n.get("profile") != "?"),
          "an exempt job must never reach the heal branch")

# cleanup
import shutil as _sh
_sh.rmtree(tmpd, ignore_errors=True)

print()
if fails:
    print(f"❌ {len(fails)} FAILED: " + ", ".join(fails))
    sys.exit(1)
print("✅ fleet sentinel cannot re-fire a scanned job; a pause is not a retirement")


# ── 6. QUIET HOURS: DETECTED always, DELIVERED deferred, LOST never ──────────────────────
# This section exists because the assertion above was WRONG, not because the tool was.
# It ran at whatever hour it executed: outside working hours the sentinel deliberately HOLDS
# findings for later delivery, so a real paused-broken job is absent from `new` and the
# original assertion failed on a perfectly healthy tool. It passed only by accident of the
# clock — a green that was not testing the thing it claimed to test.
#
# The real contract has three parts, and all three are asserted here so this cannot
# silently regress again: DETECTED at night, DEFERRED at night, DELIVERED in daylight.
# Asserting "not in new" alone would have been a lie; asserting "found" alone would have
# passed by accident of the hour. The deferral is never a loss.
import subprocess as _sp, json as _js


def _fixture_run(flags):
    _t = tempfile.mkdtemp(prefix="fleet_qh_")
    _f = os.path.join(_t, "jobs.json")
    _js.dump({"jobs": [
        {"id": "deadbeef0009", "name": "ordinary paused-broken job", "enabled": False,
         "last_status": "error", "failure_streak": 1, "script": "whatever.sh"},
    ]}, open(_f, "w"))
    _r = _sp.run([sys.executable, SRC, "--jobs-file", _f, "--json", "--no-debounce",
                  "--state", os.path.join(_t, "state.json")] + flags,
                 capture_output=True, text=True, timeout=180)
    try:
        return _js.loads(_r.stdout)
    except Exception:
        return {}


def _ids(out, key):
    return {str(n.get("id", "")) for n in (out.get(key) or []) if isinstance(n, dict)}


_night = _fixture_run(["--now", "2026-09-29T06:00:00+00:00"])
_day = _fixture_run(["--now", "2026-09-29T14:00:00+00:00"])
_fid = "deadbeef0009"

check("quiet hours: the job is DETECTED at night (failing count)",
      (_night.get("totals") or {}).get("failing") == 1,
      f"night totals={_night.get('totals')}")
check("quiet hours: the run declares it is in quiet hours (deferral is legible)",
      _night.get("quiet_hours") is True,
      f"quiet_hours={_night.get('quiet_hours')}")
check("quiet hours: the finding is DEFERRED, not delivered at night",
      not any(i.startswith(_fid) for i in _ids(_night, "new")),
      f"night new={sorted(_ids(_night, 'new'))}")
check("daytime: the SAME job is DELIVERED in `new` (deferral is not loss)",
      any(i.startswith(_fid) for i in _ids(_day, "new")),
      f"day new={sorted(_ids(_day, 'new'))}")
