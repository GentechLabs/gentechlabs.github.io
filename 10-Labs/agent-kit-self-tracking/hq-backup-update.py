#!/usr/bin/env python3
"""
hq-backup-update.py — keep the OFF-BOX baseline (`hq-backup-20260928`) current.

WHY THIS EXISTS
  The vault checkout cannot push `main` while it is forked, so the automatic leg is blocked
  and the off-box copy is a SNAPSHOT that re-ages by the minute: measured tonight, the delta
  behind the backup went 29 -> 32 -> 43 -> 50 commits while we discussed it.

  A BASELINE THAT DECAYS, NOT A SAFETY NET. THE MERGE CLOSES THE GAP; NO SNAPSHOT DOES.
  This script does not fix the fork and must never be used as an argument that the fork can
  wait. It keeps a restore point close to HEAD so that a disk loss costs hours, not a day.

THREE CONSTRAINTS (HQ, 2026-09-28 — the ref is theirs, given with disclosure)
  1. FAST-FORWARD ONLY. Backup ref only. NEVER `main`. If the update is ever not a
     fast-forward, STOP and say so — that state is an ALARM, not an obstacle. Never force.
  2. At most HOURLY, through the fleet gate, SILENT ON SUCCESS. Not a second nag.
  3. NEVER COMPETE WITH A MAIN PUSH. If `main` can land, `main` wins the slot and this
     exits without doing anything. The backup is a fallback, not a competitor.

WHERE `main` APPEARS IN THIS FILE (corrected 2026-09-28)
  Exactly twice, and both are inert by construction — neither can become a push target:
    - the NEVER_TOUCH constant, read by assert_target_safe() before any push; and
    - a read-only `git merge-base --is-ancestor {remote}/main HEAD` query for constraint 3.
  The only push in the file is `HEAD:refs/heads/{BACKUP_REF}`. An earlier version of this
  header claimed `main` appeared "only in the docstring" — that was loose, and the looser
  sentence is what a future editor would have trusted.

WHY "FAST-FORWARD ONLY" IS WRITTEN THIS WAY
  The first draft of this offer said "force-push only the backup ref". That wording was wrong
  and has been withdrawn: a plan that says *force* invites a reader to reach for `--force` on
  the day it is NOT a fast-forward -- which is exactly the day forcing would destroy work.
  `git merge-base --is-ancestor` answers the question directly, and non-zero is a STOP.
  For the same reason there is no `--force-run`: the flag that ignores the INTERVAL is `--now`,
  because a flag named "force" is a word a reader will one day reach for wrongly.

EXIT CODES
  0  did nothing (fine): up to date, too soon, main wins the slot, gate deferred, or pushed
  1  STOPPED: the update would not be a fast-forward, OR the refspec failed its safety
     assertion. Investigate; do NOT force.

Usage:  hq-backup-update.py [--json] [--dry-run] [--now] [--ref REF]
"""

import argparse
import json
import os
import subprocess
import sys
import time

VAULT = "/root/vaults/gentech"
BACKUP_REF = "hq-backup-20260928"
NEVER_TOUCH = "main"                      # constraint 1: non-negotiable
MIN_INTERVAL_S = 3600                     # constraint 2: at most hourly
STATE = "/root/.hermes/state/hq-backup-update.json"


def run(cmd, timeout=280):
    p = subprocess.run(cmd, cwd=VAULT, shell=True, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def resolve_remote():
    """A hardcoded remote name is the bug whichever name it is (HQ, 2026-09-28)."""
    _, remotes = run("git remote")
    names = [r.strip() for r in remotes.splitlines() if r.strip()]
    for preferred in ("vault", "origin"):
        if preferred in names:
            return preferred
    return names[0] if names else "origin"


def assert_target_safe(refspec, ref):
    """Constraint 1, READ not merely declared — AND REACHABLE.

    v1 declared NEVER_TOUCH and referenced it ZERO times: the protection that actually held was
    the hardcoded refspec and the named guard was inert. A guard that looks like the guard is not
    the guard (HQ, 2026-09-28).

    v2 read the real target, but the guard sat DOWNSTREAM of two earlier returns, so it could not
    fire at all from the CLI (HQ, 2026-09-28): the FF query returned STOPPED_NOT_FAST_FORWARD for
    ANY non-ancestor ref BEFORE control reached this function, and `--ref main` is exactly such a
    ref. Proven: `--now --ref main` printed "vault/main is not an ancestor of HEAD" — CORRECT
    BEHAVIOUR, WRONG REASON. Three conditions were unreachable by construction:
      - `name != ref` could never hold: the refspec is BUILT from `ref`.
      - `name not in dest` could never hold: dest is literally "refs/heads/" + name.
      - the never-touch check could not be consulted, because nothing got here.

    v3 (this version) checks the REF ITSELF, which is a CLI input, and main() calls it FIRST —
    before the interval, the fetch and the FF query — so no earlier return can mask it. A guard
    whose firing case requires hand-editing the subject is not a guard; it is a comment.

    BOUNDARY (2026-09-28, stated not scored — HQ's ask): ONE LIVE GUARD AND THREE TRIPWIRES. main()
    builds the refspec as HEAD:refs/heads/{ref}, so `dest` is ALWAYS "refs/heads/" + ref. Therefore:
      - A is REACHABLE from today's CLI (`--ref main`) — the one live guard.
      - B is SHADOWED BY A: ref == NEVER_TOUCH is caught first, so when the dest comparison would
        hold, A has already returned. It cannot be the condition that fires.
      - C and D can never hold at all while that construction stands.
    B, C and D stay as armour against a future refactor that assembles the refspec elsewhere — that
    is a defensible reason to keep them. But "four checks" reads as four protections and it is ONE,
    so the count must not be cited as the strength of the guard. The strength is A being FIRST.
    Returns None when safe, or a reason string when not.
    """
    # A — the REF ITSELF must not be the never-touch ref. Reachable from the CLI by `--ref main`,
    #     which is the case this tool exists to refuse. Checked FIRST because it is the input.
    if ref == NEVER_TOUCH:
        return f"ref {ref!r} is the never-touch ref"
    # B — and not by destination path either (catches a refspec assembled some other way).
    dest = refspec.split(":", 1)[-1]              # refs/heads/<name>
    if dest == f"refs/heads/{NEVER_TOUCH}":
        return f"refspec targets the never-touch ref {NEVER_TOUCH!r}"
    # C — the destination must name EXACTLY this ref. Equality, not membership: `name in dest`
    #     was vacuously true by construction and proved nothing.
    if dest != f"refs/heads/{ref}":
        return f"refspec targets {dest!r}, not refs/heads/{ref!r}"
    # D — and must be a branch refspec at all.
    if not dest.startswith("refs/heads/"):
        return f"refspec destination {dest!r} is not under refs/heads/"
    return None


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(st, f)


def emit(a, out, human=""):
    print(json.dumps(out) if a.json else human)


def main():
    ap = argparse.ArgumentParser(description="Fast-forward the off-box backup ref. Never main, never force.")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--now", action="store_true", help="ignore the hourly interval (never the FF rule)")
    ap.add_argument("--ref", default=BACKUP_REF,
                    help="override the backup ref, for tests. The safety assertion still applies, so "
                         "`--ref main` is REFUSED rather than dangerous.")
    a = ap.parse_args()
    ref = a.ref
    now = time.time()
    st = load_state()

    # ---- constraint 1 FIRST: validate the TARGET before anything can return ahead of it ------
    # v2 called this right before the push, which meant the FF query returned for any
    # non-ancestor ref BEFORE control ever arrived here — so `--ref main` was refused for the
    # WRONG REASON and the guard was unreachable from the CLI (HQ, 2026-09-28). Order is
    # necessary and not sufficient: asserting a call happens before the push proves nothing
    # about reachability. Validating the input FIRST makes the guard reachable by construction.
    refspec = f"HEAD:refs/heads/{ref}"
    problem = assert_target_safe(refspec, ref)
    if problem:
        emit(a, {"status": "STOPPED_UNSAFE_REFSPEC", "refspec": refspec, "why": problem,
                 "action": "DO NOT PUSH — the target is not the backup ref."},
             f"  🛑 backup-update: STOPPED — refusing to push `{refspec}`: {problem}")
        return 1

    # ---- constraint 2: hourly, silent on success -------------------------------------
    if not a.now and st.get("last_ok") and (now - st["last_ok"]) < MIN_INTERVAL_S:
        emit(a, {"status": "TOO_SOON", "next_in_min": round((MIN_INTERVAL_S - (now - st["last_ok"])) / 60, 1)}, "")
        return 0

    remote = resolve_remote()
    rc, _ = run(f"git fetch {remote} --quiet")
    if rc != 0:
        emit(a, {"status": "FETCH_FAILED", "remote": remote},
             f"  ⚠️  backup-update: `git fetch {remote}` failed — nothing attempted")
        return 0

    # ---- constraint 1: is the update a fast-forward? ask the GRAPH, not a push attempt --
    rc_anc, _ = run(f"git merge-base --is-ancestor {remote}/{ref} HEAD")
    if rc_anc != 0:
        st["stopped_at"] = now
        save_state(st)
        emit(a, {"status": "STOPPED_NOT_FAST_FORWARD", "backup": f"{remote}/{ref}",
                 "why": f"{remote}/{ref} is not an ancestor of HEAD",
                 "action": "DO NOT FORCE — investigate. This is an alarm, not an obstacle."},
             f"  🛑 backup-update: STOPPED — updating {remote}/{ref} would NOT be a "
             f"fast-forward.\n     DO NOT FORCE. Investigate the ref before touching it.\n"
             f"     (This is an alarm, not an obstacle.)")
        return 1

    # ---- constraint 3: if main can land, main wins the slot ---------------------------
    rc_main, _ = run(f"git merge-base --is-ancestor {remote}/{NEVER_TOUCH} HEAD")
    if rc_main == 0:
        emit(a, {"status": "MAIN_WINS_SLOT", "why": "main is fast-forwardable — the drain should take it"},
             "")
        return 0

    head = run("git rev-parse --short HEAD")[1].strip()
    behind = run(f"git rev-list --count {remote}/{ref}..HEAD")[1].strip()
    if behind == "0":
        st["last_ok"] = now
        save_state(st)
        emit(a, {"status": "CURRENT", "head": head}, "")
        return 0

    # ---- the refspec was BUILT and VALIDATED at the top of main(), before any early return ----
    # (one validation point, reachable by construction — see the note at the top of main())
    if a.dry_run:
        emit(a, {"status": "WOULD_PUSH", "target": refspec, "commits": behind, "head": head,
                 "target_verified_by": "assert_target_safe"},
             f"  (dry-run) would fast-forward {remote}/{ref} by {behind} commit(s) to {head}\n"
             f"  (target verified by assert_target_safe: {refspec})")
        return 0

    # ---- the push. The pre-push hook applies the fleet gate automatically. -------------
    rc, msg = run(f"git push {remote} {refspec}", timeout=280)
    low = msg.lower()
    if "deferred" in low:
        emit(a, {"status": "DEFERRED_GATE", "detail": msg.strip().splitlines()[-1][:120] if msg.strip() else ""},
             f"  ⏳ backup-update: gate deferred — the gate is a WAIT; the next run will retry")
        return 0
    if rc != 0:
        emit(a, {"status": "PUSH_FAILED", "detail": msg.strip()[-200:]},
             f"  ⚠️  backup-update: push failed — {msg.strip()[-160:]}")
        return 0

    st["last_ok"] = now
    st["stopped_at"] = None
    save_state(st)
    emit(a, {"status": "UPDATED", "target": f"{remote}/{ref}", "commits": behind, "head": head}, "")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.TimeoutExpired:
        print("  ⚠️  backup-update: timed out")
        sys.exit(0)
