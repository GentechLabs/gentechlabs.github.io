#!/usr/bin/env python3
"""Per-wallet mutual exclusion for anything that signs a transaction.

WHY THIS EXISTS — and it is the biggest defect found on 2026-09-27
------------------------------------------------------------------
Measured, live:

    the cron schedule for the position watchdog   */5 * * * *   (every 5 minutes)
    how long one rebuild actually takes           7–11 minutes
    mutual exclusion anywhere in the chain        NONE
        (grep -nE "flock|lockfile|\.lock" steward-watchdog.sh lfj_recenter.py
         lfj-curve-deploy.sh  ->  no matches)

A run LONGER THAN ITS OWN CADENCE, with nothing stopping the next one from starting, means the
next one DOES start — while the first is still mid-cycle. Two `lfj_recenter --execute` processes
on ONE wallet.

Observed directly: processes from **11:41 and 11:42 alive at the same time**, plus the 11:36 run
still working. The wallet's nonce moved 1601 -> 1604 = three writes in 45 minutes, with the
attempts racing each other.

WHAT THE RACE ACTUALLY BREAKS
-----------------------------
The rebuild is a SEQUENCE, not a transaction:
    withdraw -> rebalance/swap -> approve -> deploy leg 1 -> deploy leg 2
Every step changes the wallet's balances, its allowance, and its nonce. Two sequences interleaved
on one wallet observe each other's partial state:

  * a leg sizes itself from a balance another process has already spent;
  * an approval is read before the other process's approve has been mined;
  * two transactions are built against the SAME nonce, so one is dropped or replaced.

Proven cost, 2026-09-27 11:36Z: jordan's book came out **13 bins, ASK ONLY, out of range,
earning $0.00**. The bid leg died on `ERC20: transfer amount exceeds allowance` — the allowance
read was taken while another run was mid-flight. Capital was intact; the book was broken.

THE BUG CLASS
-------------
This is the same family as everything else on this system: **a mechanism that reports success
while the thing it exists to protect is broken.** Here, each process believed it was the only
one running. Nothing in the chain ever asked. A cron expression is a REQUEST to start, not a
promise that the previous run finished.

WHY `flock` AND NOT A PIDFILE
-----------------------------
A pidfile survives a crash and leaves a stale lock that blocks every future run — the exact
"stuck until a human notices" failure this system keeps producing. `flock` is held by the OPEN
FILE DESCRIPTOR: the kernel drops it when the process dies, killed, crashed, or otherwise. There
is no stale state to clean up, ever.

The lock is keyed on the WALLET, not on the script. Two different scripts signing for the same
wallet must exclude each other, because the wallet is the thing being raced.

Usage:
    with WalletLock(wallet, purpose="recenter"):   # raises LockBusy if held
        ...sign...
Or as a guard that exits:
    lock = WalletLock(wallet, purpose="recenter")
    lock.acquire_or_exit()                          # prints why, sys.exit(9)

Exit code 9 = ANOTHER RUN HOLDS THIS WALLET. It is not a failure of the work; it is the lock
doing its job, and callers must not treat it as an error worth alerting on.
"""
import errno
import fcntl
import os
import sys
import time

LOCK_DIR = os.environ.get("STEWARD_LOCK_DIR") or "/tmp"
EXIT_LOCK_BUSY = 9


class LockBusy(Exception):
    """Another process is already signing for this wallet."""

    def __init__(self, msg, holder=""):
        super().__init__(msg)
        self.holder = holder


def lock_path(wallet):
    """One lock file per wallet — case-insensitive, because an address is not case-sensitive."""
    w = (wallet or "unknown").lower().replace("0x", "")
    return os.path.join(LOCK_DIR, f"steward-wallet-{w}.lock")


class WalletLock:
    """Hold an exclusive lock for one wallet for the lifetime of the block."""

    def __init__(self, wallet, purpose="tx", verbose=True):
        self.wallet = wallet
        self.purpose = purpose
        self.verbose = verbose
        self.path = lock_path(wallet)
        self.fd = None

    # ── acquire ──────────────────────────────────────────────────────────────────────────────
    def acquire(self):
        """Take the lock, or raise LockBusy. NEVER blocks — a blocked cron run is a pile-up."""
        os.makedirs(LOCK_DIR, exist_ok=True)
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            if e.errno in (errno.EACCES, errno.EAGAIN):
                holder = ""
                try:
                    with open(self.path) as f:
                        holder = f.read().strip()
                except Exception:
                    pass
                os.close(fd)
                raise LockBusy(
                    f"another run holds {self.wallet} ({holder or 'holder unknown'})", holder)
            os.close(fd)
            raise
        # Record WHO holds it, for diagnosis only. The lock itself is the fd, never this text.
        try:
            os.ftruncate(fd, 0)
            os.write(fd, f"pid={os.getpid()} purpose={self.purpose} "
                         f"since={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n".encode())
        except Exception:
            pass
        self.fd = fd
        if self.verbose:
            print(f"  🔒 LOCK ACQUIRED — {self.wallet} held by pid {os.getpid()} ({self.purpose})")
        return self

    def acquire_or_exit(self):
        """Acquire, or explain and exit 9. Used by scripts that mutate a live wallet."""
        try:
            return self.acquire()
        except LockBusy as e:
            print(f"\n  ⏸ ANOTHER RUN IS ALREADY WORKING THIS WALLET — not starting a second one.",
                  file=sys.stderr)
            print(f"     {e}", file=sys.stderr)
            print(f"     This is the LOCK, not an error: two runs on one wallet race the same"
                  f" nonce,\n     allowance and balances, and that is how a book ends up"
                  f" half-built (13 bins,\n     ask-only, earning nothing — measured 2026-09-27).",
                  file=sys.stderr)
            print(f"     The other run finishes on its own; this pass is deliberately skipped.",
                  file=sys.stderr)
            sys.exit(EXIT_LOCK_BUSY)

    # ── release ──────────────────────────────────────────────────────────────────────────────
    def release(self):
        if self.fd is not None:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
            except Exception:
                pass
            try:
                os.close(self.fd)
            except Exception:
                pass
            self.fd = None
            if self.verbose:
                print(f"  🔓 LOCK RELEASED — {self.wallet}")

    def __enter__(self):
        return self.acquire()

    def __exit__(self, *exc):
        self.release()
        return False


def holder_of(wallet):
    """Who currently holds this wallet's lock, or '' if free. For diagnostics and tests."""
    p = lock_path(wallet)
    if not os.path.exists(p):
        return ""
    fd = os.open(p, os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return ""          # we got it, so nobody holds it
    except OSError:
        try:
            with open(p) as f:
                return f.read().strip()
        except Exception:
            return "holder unknown"
    finally:
        os.close(fd)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="per-wallet lock status")
    ap.add_argument("wallet")
    a = ap.parse_args()
    h = holder_of(a.wallet)
    print(f"  {a.wallet}: {'HELD — ' + h if h else 'FREE'}")
    sys.exit(0)
