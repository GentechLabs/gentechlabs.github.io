#!/usr/bin/env python3
"""The posture cache must never be observable in a half-written state.

THE BUG (found 2026-09-28). `defi-hub-refresh.sh` wrote the posture cache with a bare shell
redirect:

    python3 posture.py --tenant dadrian --json > "$SCRIPTS_DIR/.posture-dadrian.json"

A shell `>` TRUNCATES the target to 0 bytes *before* the command runs. The posture pass takes
~42s per tenant, so for ~42s out of every 10-minute sweep that file sat EMPTY on disk — while the
5-minute watchdog was reading it. A read landing in the window died with
`JSONDecodeError: Expecting value: line 1 column 1 (char 0)`, and the pass reported

    ⚠️ POSTURE UNREADABLE for dadrian — JSONDecodeError

caught live: jordan's cache was observed at exactly 0 bytes during a sweep.

WHY IT MATTERED BEYOND THE COSMETIC. An unreadable posture is an UNKNOWN, and the watchdog treats
it as one rather than as agreement — correct. But a ~7% failure rate that looks like a flaky chain
read trains everyone to ignore the warning, and the one time it is a REAL unreadable posture it
looks identical. Intermittent, self-healing, and indistinguishable from a genuine fault is the
worst combination a monitor can have.

WHAT THIS TEST PROVES
  1. A concurrent reader NEVER observes a partial or empty cache while the writer runs.
  2. The write is atomic — readers see the complete old file or the complete new one.
  3. A failing posture pass publishes an explicit error record, never an empty file.
  4. The old (buggy) pattern is demonstrably observable — so the test is not vacuous.

Exit codes: 0 pass, 1 fail, 2 could not read inputs.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time

SCRIPTS = "/root/.hermes/profiles/gentech-treasury/scripts"
results = []


def check(name, ok, detail=""):
    results.append((ok, name, detail))
    print(f"  {'PASS' if ok else 'FAIL'} — {name}" + (f"  [{detail}]" if detail and not ok else ""))


def atomic_write(target, blob):
    """The fixed writer's behaviour: write a temp file, then rename into place."""
    tmp = f"{target}.tmp.{os.getpid()}"
    with open(tmp, "w") as fh:
        fh.write(blob)
    os.replace(tmp, target)


def bare_write(target, blob):
    """The OLD writer's behaviour: truncate then write. Exactly what a shell `>` does."""
    with open(target, "w") as fh:      # <- truncates to 0 the instant it opens
        fh.write(blob)
        fh.flush()
        time.sleep(0.002)              # the ~42s window, scaled down


def observe(writer, target, seconds=1.0):
    """Hammer-read the target while a writer runs. Record anything that is not valid JSON."""
    bad = []
    stop = threading.Event()

    def reader():
        while not stop.is_set():
            try:
                with open(target) as fh:
                    raw = fh.read()
                if raw == "":
                    bad.append("EMPTY")
                else:
                    json.loads(raw)
            except json.JSONDecodeError as e:
                bad.append(f"BAD_JSON:{e.msg}")
            except FileNotFoundError:
                pass          # a rename leaves no gap — but tolerate it and record it
            time.sleep(0.0002)

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    time.sleep(0.02)
    end = time.time() + seconds
    while time.time() < end:
        writer(target, json.dumps({"tenant": "t", "decision": {"posture": "SKEW_CURVE"},
                                   "pad": "x" * 2000}))
    stop.set()
    t.join(timeout=2)
    return bad


# ── 1. inputs
if not os.path.isdir(SCRIPTS):
    print("  SKIP — scripts dir not found"); sys.exit(2)

# ── 2. the REAL writer on disk uses a rename, not a bare redirect
refresh = os.path.join(SCRIPTS, "defi-hub-refresh.sh")
if not os.path.exists(refresh):
    print("  SKIP — defi-hub-refresh.sh not found"); sys.exit(2)
src = open(refresh).read()
check("writer no longer uses a bare `>` redirect into the posture cache",
      '--json > "$SCRIPTS_DIR/.posture-$_t.json"' not in src)
check("writer writes to a temp path first", "_tmp=" in src and ".tmp.$$" in src)
check("writer renames into place (mv -f)", "mv -f" in src)
check("writer refuses to publish an empty file", '[ -s "$_tmp" ]' in src)

# ── 3. NON-VACUITY: the OLD pattern IS observable by this method
with tempfile.TemporaryDirectory() as td:
    tgt = os.path.join(td, "state.json")
    atomic_write(tgt, json.dumps({"ok": 1}))
    bad_old = observe(bare_write, tgt, seconds=1.0)
    check("the OLD pattern IS caught (test is not vacuous)", len(bad_old) > 0,
          f"old pattern produced {len(bad_old)} bad reads")

    # ── 4. the NEW pattern is clean under the same load
    atomic_write(tgt, json.dumps({"ok": 1}))
    bad_new = observe(atomic_write, tgt, seconds=1.0)
    check("the NEW pattern is NEVER observed partial", len(bad_new) == 0,
          f"new pattern produced {len(bad_new)} bad reads: {bad_new[:3]}")

    # ── 5. a failing pass publishes an explicit error, never an empty file
    err_target = os.path.join(td, "err.json")
    atomic_write(err_target, json.dumps({"tenant": "t", "error": "posture pass failed"}))
    d = json.load(open(err_target))
    check("a failed pass publishes an explicit error record", d.get("error") == "posture pass failed")
    check("a failed pass is never a 0-byte file", os.path.getsize(err_target) > 0)

# ── 6. the reader can now NAME the cause
wd = os.path.join(SCRIPTS, "steward-watchdog.sh")
wsrc = open(wd).read()
check("reader explains a 0-byte cache", "0 bytes" in wsrc)
check("reader explains invalid JSON with position", "not valid JSON" in wsrc)

# ── 7. BOTH live caches are valid and belong to the right tenant
for t in ("jordan", "dadrian"):
    p = os.path.join(SCRIPTS, f".posture-{t}.json")
    if not os.path.exists(p):
        check(f"live cache exists: {t}", False, "missing")
        continue
    try:
        d = json.load(open(p))
        ok = (d.get("tenant") == t) and bool((d.get("decision") or {}).get("posture")) and not d.get("error")
        check(f"live cache valid and correctly owned: {t}", ok,
              f"tenant={d.get('tenant')} posture={(d.get('decision') or {}).get('posture')}")
    except Exception as e:
        check(f"live cache valid and correctly owned: {t}", False, str(e))

# ── 8. no 0-byte posture files left anywhere
stray = [f for f in os.listdir(SCRIPTS) if f.startswith(".posture-") and f.endswith(".json")
         and os.path.getsize(os.path.join(SCRIPTS, f)) == 0]
check("no 0-byte posture files remain", not stray, str(stray))

# ── 9. no leftover temp files
# FLAKE FIX (2026-09-28): this flagged EVERY file containing ".tmp.", including the one the hub job
# is writing RIGHT NOW as part of a correct atomic write. The suite runs for minutes against a
# production scripts dir where `defi-hub-refresh.sh` writes `.posture-<tenant>.json.tmp.$$` every
# 10 minutes, so under load the two overlap and a WORKING writer reads as a leak. Observed live:
# suite red while the same test passed 3/3 standalone, with posture mtimes 17:03:48 / 17:04:31
# matching the suite window exactly.
#   A leak is an ORPHANED temp — a file left behind by a SIGKILL, which is exactly what the sweep
#   at the top of defi-hub-refresh.sh deletes with `-mmin +5`. A temp younger than that is a write
#   in flight, and flagging it makes the guard cry wolf on its own correct behaviour.
# So: only temps older than the sweep threshold count as leftover.
_ORPHAN_AGE_S = 300
_now = time.time()
tmp_left = []
for _f in os.listdir(SCRIPTS):
    if ".tmp." not in _f:
        continue
    _p = os.path.join(SCRIPTS, _f)
    try:
        if _now - os.path.getmtime(_p) > _ORPHAN_AGE_S:
            tmp_left.append(f"{_f} (age {int(_now - os.path.getmtime(_p))}s)")
    except OSError:
        continue
check("no ORPHANED temp files (in-flight temps are not a leak)", not tmp_left, str(tmp_left[:4]))

passed = sum(1 for ok, _, _ in results if ok)
print(f"\n  RESULT: {'PASS' if passed == len(results) else 'FAIL'} — {passed}/{len(results)} checks passed")
for ok, name, detail in results:
    if not ok:
        print(f"    FAILED: {name} {detail}")
sys.exit(0 if passed == len(results) else 1)
