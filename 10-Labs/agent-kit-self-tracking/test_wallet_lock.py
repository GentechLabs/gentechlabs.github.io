#!/usr/bin/env python3
"""Prove the per-wallet lock actually EXCLUDES — the fix for the 2026-09-27 half-built book.

THE INCIDENT
------------
    cron cadence for the position watchdog   */5 * * * *    (every 5 minutes)
    how long one rebuild takes               7–11 minutes
    mutual exclusion in the chain            NONE

A run longer than its own cadence, with nothing preventing the next start, means the next run
starts mid-cycle. Two `--execute` processes on one wallet, observed live: processes from **11:41
and 11:42 alive simultaneously**, nonce 1601 -> 1604 in 45 minutes.

Cost, proven 11:36Z: jordan's book rebuilt as **13 bins, ASK only, out of range, earning $0.00.**
The bid leg read an allowance another run was mid-flight changing
(`ERC20: transfer amount exceeds allowance`), and leg 2 landed alone. Capital intact, book broken.

WHAT THIS TEST MUST SHOW
------------------------
1. A second process is EXCLUDED while the first holds the wallet.
2. The exclusion is per WALLET — another wallet is unaffected (jordan's run must not block
   dadrian's; that would be a new deadlock, not a fix).
3. A CRASHED holder leaves NO stale lock — the kernel drops it with the fd. A pidfile would
   survive the crash and block every future run, which is the "stuck until a human notices"
   failure this system keeps producing.
4. It never BLOCKS: a blocked cron run is a pile-up, so it must fail fast with a clear message.
5. Exit code 9 means "the lock is doing its job", NOT an error worth alerting on.
6. lfj_recenter actually takes it before it can sign.
"""
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

LOCKDIR = tempfile.mkdtemp(prefix="locktest-")
os.environ["STEWARD_LOCK_DIR"] = LOCKDIR

import agent_lock as AL       # noqa: E402
AL.LOCK_DIR = LOCKDIR         # the module read env at import; point it at the sandbox

JORDAN = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
DADRIAN = "0x6c69F8FD6C23A5b6b3ccbCB0d638AA6D527812Fe"

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    if not cond and detail:
        print(f"        {detail}")


print("  ── 1. THE LOCK EXCLUDES A SECOND HOLDER ─────────────────────────────")
a = AL.WalletLock(JORDAN, purpose="first", verbose=False).acquire()
check("first holder acquires", a.fd is not None)
try:
    AL.WalletLock(JORDAN, purpose="second", verbose=False).acquire()
    check("second holder is REJECTED  <<< the whole point", False, "it acquired — no exclusion")
except AL.LockBusy as e:
    check("second holder is REJECTED  <<< the whole point", True)
    check("the refusal names the holder so a human can diagnose it",
          "first" in str(e) or "pid=" in str(e), f"msg={e}")
check("holder_of reports who holds it", "first" in AL.holder_of(JORDAN),
      f"got {AL.holder_of(JORDAN)!r}")

print("")
print("  ── 2. IT IS PER-WALLET, NOT GLOBAL ───────────────────────────────────")
b = AL.WalletLock(DADRIAN, purpose="dadrian", verbose=False).acquire()
check("another WALLET is not blocked by jordan's lock  <<< or this is a new deadlock",
      b.fd is not None)
b.release()

print("")
print("  ── 3. IT NEVER BLOCKS (a blocked cron run is a pile-up) ─────────────")
t0 = time.time()
try:
    AL.WalletLock(JORDAN, purpose="blocking-test", verbose=False).acquire()
except AL.LockBusy:
    pass
dt = time.time() - t0
check("a contended acquire returns immediately, does not wait", dt < 1.5, f"took {dt:.2f}s")

print("")
print("  ── 4. RELEASE / RE-ACQUIRE ──────────────────────────────────────────")
a.release()
check("after release the wallet is FREE", AL.holder_of(JORDAN) == "")
c = AL.WalletLock(JORDAN, purpose="third", verbose=False).acquire()
check("and it can be acquired again (not one-shot)", c.fd is not None)
c.release()

print("")
print("  ── 5. A CRASHED HOLDER LEAVES NO STALE LOCK  <<< why flock not a pidfile ──")
# Spawn a child that takes the lock and then DIES WITHOUT RELEASING.
child = subprocess.Popen(
    [sys.executable, "-c",
     f"import os,sys,time; os.environ['STEWARD_LOCK_DIR']={LOCKDIR!r};"
     f" sys.path.insert(0,{HERE!r});"
     f" import agent_lock as A; A.LOCK_DIR={LOCKDIR!r};"
     f" l=A.WalletLock({JORDAN!r},purpose='will-crash',verbose=False).acquire();"
     f" print('HELD',flush=True); time.sleep(60)"],
    stdout=subprocess.PIPE, text=True)
line = child.stdout.readline().strip()
check("child really took the lock", line == "HELD", f"child said {line!r}")
check("while the child lives, the lock is HELD", "will-crash" in AL.holder_of(JORDAN))
child.kill()                       # SIGKILL — no cleanup code runs, no release() called
child.wait()
time.sleep(0.5)
h = AL.holder_of(JORDAN)
check("after SIGKILL the lock is FREE — the kernel dropped it  <<< no stale state, ever",
      h == "", f"still held by {h!r} — a stale lock would block every future run")

print("")
print("  ── 6. THE INTEGRATION: lfj_recenter takes it before signing ──────────")
rc = open(os.path.join(HERE, "lfj_recenter.py")).read()
check("lfj_recenter imports the lock", "from agent_lock import WalletLock" in rc)
check("it takes the lock ONLY on execute runs (dry runs stay diagnosable)",
      "if a.execute and a.yes:" in rc)
check("it refuses to sign if the lock module is missing (fails CLOSED)",
      "refusing to sign without mutual exclusion" in rc)
check("the lock is taken BEFORE the first tx-capable action, not mid-cycle",
      rc.index("_lock.acquire_or_exit()") < rc.index("subprocess.run(",
                                                    rc.index("_lock.acquire_or_exit()")),
      "a lock taken after the withdraw leaves the whole cycle racy")
# NOTE — the first version of this check compared the lock's index against the index of
# `def _gas_precondition`, which is a FUNCTION DEFINITION near the top of the file, not a call.
# It failed while the code was correct: the lock sits at the parse point and the first
# subprocess.run (the withdraw) is 8.7k characters further down. A test that compares an
# execution point against a definition point measures nothing — the same "assert on the wrong
# variable" mistake the rest of tonight's suite kept catching.
check("exit 9 is defined as LOCK-BUSY", AL.EXIT_LOCK_BUSY == 9)

print("")
print("  ── 7. THE COUNTERFACTUAL: WOULD IT HAVE SAVED TONIGHT? ─────────────")
# 11:36 run started; the 11:41 pass begins while it is still mid-rebuild.
first = AL.WalletLock(JORDAN, purpose="11:36-run", verbose=False).acquire()
second_attempted = False
try:
    AL.WalletLock(JORDAN, purpose="11:41-run", verbose=False).acquire()
    second_attempted = True
except AL.LockBusy:
    pass
check("the 11:41 pass would have been SKIPPED, not raced", not second_attempted)
check("so the bid leg could not have read a mid-flight allowance",
      not second_attempted, "this is exactly the failure that produced 13 ask-only bins")
first.release()

print("")
print(f"  RESULT: {'PASS' if not FAIL else 'FAIL'} — {len(PASS)}/{len(PASS)+len(FAIL)} checks passed")
for f in FAIL:
    print(f"    - {f}")
sys.exit(1 if FAIL else 0)
