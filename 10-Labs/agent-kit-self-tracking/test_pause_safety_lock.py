#!/usr/bin/env python3
"""Prove pause_safety takes the wallet lock on an EXECUTE run — and does not block a dry run.

THE GAP THIS CLOSES. The wallet lock is genuine mutual exclusion, but it covered exactly one file:
`lfj_recenter.py`. Gentech audited it and reported that `lfj-curve-deploy.sh` is "reachable solely
from inside recenter, so it inherits the lock" — true for the deploy scripts, and it is a property
of the current CALL GRAPH rather than an enforced invariant. Checking that claim instead of
accepting it found the hole: `pause_safety.py` calls `lfj_exit.py` DIRECTLY and took no lock at all.
A pause-safety flatten running while the 5-minute watchdog was mid-recenter would race the same
wallet — same nonce, same allowance, same balances — which is the half-built-book failure the lock
exists to prevent.

TWO BUGS IN THE FIRST DRAFT OF THE FIX, both caught by checking rather than assuming:
  1. the comment claimed `acquire_or_exit()` WAITS for an in-flight holder. It does not — it is
     fail-closed (exit 9). The comment now says what the code does.
  2. `tenants()` yields (name, wallet) TUPLES; the draft read it as dicts of dicts, so `_w` was
     always None and the loop silently locked NOTHING. The guard would have been decorative —
     present in the diff, absent in effect. That is the exact failure mode this suite keeps
     catching, so it is now pinned by a test.

HOW THIS IS TESTED SAFELY. It never lets the real exit path run: `exit_to_stable` and `resume` are
replaced with a recorder, so the assertions are about WHICH PATH main() reached, not about money.
A test that could flatten two live books if it failed would be worse than no test.

ASSERTIONS:
  1. with an EXECUTE run and a HELD lock -> SystemExit(9), and exit_to_stable NEVER called;
  2. with an EXECUTE run and a FREE lock -> exit_to_stable IS called (the guard does not block
     legitimate work);
  3. a DRY run takes no lock and still reaches its path;
  4. the guard locks EVERY tenant, not just the first;
  5. mutual exclusion is real: a second holder is refused;
  6. the source reads tenants() as tuples (pins bug 2 above).
"""
import io
import os
import sys
import contextlib

PASS, FAIL, SKIPPED = [], [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    if not cond and detail:
        print(f"        {detail}")


def skip(section):
    SKIPPED.append(section)
    print(f"  ⏭  SKIPPED ({section}) — wallet busy with a live run; that is the lock working")


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import pause_safety as PS
import agent_lock as _AL
from agent_lock import LockBusy

TENANTS = PS.tenants()
FIRST_NAME, FIRST_WALLET = TENANTS[0]

CALLS = []
_ACQUIRED = []


def _recorder(*a, **k):
    CALLS.append((a, k))
    return None


# ── TRACK WHAT pause_safety LOCKS, SO THE TEST CAN CLEAN UP AFTER ITSELF ──────────────────────
# pause_safety acquires in main() and never releases in-process — the real run exits and the OS
# drops the flock. A test harness that calls main() repeatedly would therefore hit its own residue
# and fail for a reason unrelated to the behaviour under test. (That is exactly what the first
# version of this test did.) Track the instances and release them between sections.
import agent_lock as _AL
_RealWalletLock = _AL.WalletLock
WalletLock = _RealWalletLock      # used directly by the guard-proof sections


class _TrackedLock(_RealWalletLock):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        _ACQUIRED.append(self)


_AL.WalletLock = _TrackedLock
PS.WalletLock = _TrackedLock


def _release_all():
    while _ACQUIRED:
        lk = _ACQUIRED.pop()
        try:
            lk.release()
        except Exception:
            pass


def run_main(argv, patch_exit=True):
    """Call PS.main() with argv, recording whether the exit path was reached."""
    CALLS.clear()
    _release_all()
    real_exit, real_resume = PS.exit_to_stable, PS.resume
    if patch_exit:
        PS.exit_to_stable = _recorder
        PS.resume = _recorder
    old = sys.argv
    sys.argv = ["pause_safety.py"] + argv
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            PS.main()
        return "returned"
    except SystemExit as e:
        return e.code
    finally:
        sys.argv = old
        PS.exit_to_stable, PS.resume = real_exit, real_resume
        _release_all()


def _wallet_free(w):
    try:
        probe = WalletLock(w, purpose="test-probe")
        probe.acquire()
        probe.release()
        return True
    except LockBusy:
        return False


def _hold(wallet, purpose):
    """Acquire a lock for a section, or return None if a LIVE run already holds it.

    A section that grabs a lock without this crashes with LockBusy when the 5-minute watchdog
    happens to be mid-recenter. That is not a defect — a live repair holding the wallet IS the
    lock working — but a test that dies on it reports a failure that is not one.
    """
    try:
        lk = WalletLock(wallet, purpose=purpose)
        lk.acquire()
        return lk
    except LockBusy:
        return None


# ── A WALLET MAY BE BUSY WITH A REAL REPAIR ─────────────────────────────────────────────────────
# An up-front probe is a HINT, never a guarantee: the watchdog can grab the wallet at any moment
# between this sample and any section below. BUSY is therefore used only to skip the obvious cases
# early; every section re-checks at the moment it actually needs the wallet, and SKIPS loudly
# instead of failing. Skips are counted in the result line so a green result cannot hide one.
BUSY = not _wallet_free(FIRST_WALLET)
if BUSY:
    print(f"  ⚠️  {FIRST_NAME}'s wallet is BUSY with a live run — sections needing a free wallet are")
    print(f"     SKIPPED and named in the result line. This is not a failure; it is the lock working.")

print("  ── 1. A HELD LOCK STOPS AN EXECUTE RUN, AND NOTHING IS FLATTENED ──")
if BUSY:
    skip("1")
else:
    holder = _hold(FIRST_WALLET, "test-holder")
    if holder is None:
        skip("1 (wallet went busy before the section acquired — re-checked, not assumed)")
    else:
        try:
            code = run_main(["--exit", "--execute", "--yes"])
            check("a held lock makes the execute run exit 9 (fail-closed)",
                  code == 9, f"got {code!r}")
            check("and the exit path was NEVER reached (no book touched)",
                  len(CALLS) == 0, f"exit_to_stable was called {len(CALLS)}x")
        finally:
            holder.release()

print("")
print("  ── 2. A FREE LOCK LETS A LEGITIMATE RUN THROUGH ──")
if BUSY:
    skip("2")
else:
    code = run_main(["--exit", "--execute", "--yes"])
    if code == 9:
        # `exit_to_stable` is only reachable with the lock FREE, so exit 9 here can mean exactly
        # one thing: the wallet was busy at the moment of acquire. That is the lock WORKING — the
        # same behaviour section 1 asserts by construction, on this same wallet.
        #
        # The previous version ALSO required the wallet to still read busy on a re-sample:
        #     if code == 9 and not _wallet_free(FIRST_WALLET)
        # which is itself a race. If the watchdog holds the lock across the run and releases it
        # before the re-probe, the second condition is False, control falls to the else branch,
        # CALLS is 0, and the test FAILS on correct behaviour. Re-sampling a condition to decide
        # whether to trust a result is the same stale-input error, one layer deeper — the run's
        # OWN exit code already carries the evidence.
        skip("2 (wallet went busy mid-section — exit 9 IS the lock working)")
    else:
        check("with the lock free, the execute run reaches its exit path",
              len(CALLS) == 1, f"exit_to_stable called {len(CALLS)}x, code={code!r}")

print("")
print("  ── 3. A DRY RUN TAKES NO LOCK AND IS NOT BLOCKED ──")
if BUSY:
    skip("3")
else:
    holder2 = _hold(FIRST_WALLET, "test-holder-2")
    if holder2 is None:
        skip("3 (wallet went busy before the section acquired — re-checked, not assumed)")
    else:
        try:
            code = run_main(["--exit"])          # NOT execute — a dry run
            check("a dry run is not blocked by a held lock",
                  code == "returned", f"got {code!r}")
            check("and it still reaches its path", len(CALLS) == 1, f"called {len(CALLS)}x")
        finally:
            holder2.release()

print("")
print("  ── 4. THE GUARD COVERS EVERY TENANT (not just the first) ──")
check(f"the registry names {len(TENANTS)} tenant(s) with wallets", len(TENANTS) >= 1)
second = _hold(TENANTS[1][1], "test-holder-second") if len(TENANTS) >= 2 else None
if second is not None:
    try:
        code = run_main(["--exit", "--execute", "--yes"])
        check("a lock held on ANY tenant stops the run", code == 9, f"got {code!r}")
    finally:
        second.release()
else:
    skip("4")

print("")
print("  ── 5. MUTUAL EXCLUSION IS REAL ──")
if BUSY:
    skip("5")
else:
    lk = _hold(FIRST_WALLET, "test-a")
    if lk is None:
        skip("5 (wallet went busy before the section acquired — re-checked, not assumed)")
    else:
        try:
            try:
                WalletLock(FIRST_WALLET, purpose="test-b").acquire()
                check("a second holder is refused", False, "the second holder got in")
            except LockBusy:
                check("a second holder is refused", True)
        finally:
            lk.release()

print("")
print("  ── 6. THE SOURCE READS tenants() AS TUPLES (pins the decorative-guard bug) ──")
src = open(os.path.join(HERE, "pause_safety.py")).read()
tail = src[src.find("def main("):]
check("it unpacks (name, wallet) tuples",
      "for _name, _wallet in tenants()" in tail,
      "reading tenants() as dicts makes the loop a no-op — a guard present in the diff and "
      "absent in effect")
check("it calls acquire_or_exit()", "acquire_or_exit()" in tail)
check("the lock is only taken on an EXECUTE run",
      "if a.execute and a.yes:" in tail)
check("and the comment matches the code (no 'waits' claim)",
      "we do not wait" in tail)

print("")
_extra = f" — {len(SKIPPED)} section(s) SKIPPED (wallet busy): {', '.join(SKIPPED)}" if SKIPPED else ""
print(f"  RESULT: {'PASS' if not FAIL else 'FAIL'} — {len(PASS)}/{len(PASS)+len(FAIL)} checks passed{_extra}")
for f in FAIL:
    print(f"    - {f}")
# A SKIPPED RUN IS NOT A GREEN RUN: exit 2 so a caller can tell "verified" from "not verified".
sys.exit(1 if FAIL else (2 if SKIPPED else 0))
