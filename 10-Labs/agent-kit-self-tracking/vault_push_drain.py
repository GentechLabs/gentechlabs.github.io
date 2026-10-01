#!/usr/bin/env python3
"""
vault_push_drain.py — the vault must never sit unpushed. (Jordan, 2026-09-23)

THE GAP THIS CLOSES:
  Every `git push` in the vault repo passes the fleet gate (`github-write-gate.py`, 20/hr).
  When the budget is spent the gate DEFERS — it prints "deferred ... retry next tick" and
  exits NON-ZERO — and the push simply fails. Nothing in the fleet retried it. The only
  vault-related cron is the 15-minute script sync (vault -> profile), which is not a push.
  So a deferred push sat local until some later commit happened to push it. If the box died
  first, the vault — which IS the fleet's memory — died with it.

WHY A DRAIN AND NOT A BIGGER BUDGET:
  The 20/hr ceiling is deliberate: the account was flagged for burst write volume and this
  repo's pushes were once treated as "free", which is exactly the kind of assumption that
  got it flagged. The gate is right. What was missing is a RETRY, so a deferred push is
  merely delayed instead of forgotten. This retries; it never argues with the budget.

DESIGN:
  - `git fetch` first: git protocol, never counted against API quota, so the comparison is
    against the REAL remote rather than a stale local ref. (A stale `origin/main` is what
    produced a false "11 commits stuck" reading on the day this was written — the fix for
    that misdiagnosis is to always fetch before counting.)
  - 0 to push        -> silent, exit 0. The common case, every 20 minutes.
  - push granted     -> clears the stuck clock. Speaks ONLY if the work had been stuck long
                        enough to matter, so a normal drain is invisible.
  - push deferred    -> records when it first got stuck and exits quietly. Retries next tick.
  - stuck > STUCK_ALERT_MIN -> speaks once. A push that cannot land for hours is material:
                        the fleet's memory is not being backed up.
  Silence doctrine: quiet unless something CHANGED or is genuinely blocked.

CLI: python3 vault_push_drain.py [--json] [--speak-test]
Exit: always 0 (a deferred push is a wait, not an error).
"""
import argparse
import json
import os
import subprocess
import sys
import time

VAULT = "/root/vaults/gentech"
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".vault-push-drain.json")
STUCK_ALERT_MIN = 180       # 3 hours unable to push = material, speak once
FORK_ALERT_HOURS = 24      # a diverged branch cannot be retried into working; speak, then daily.
                           # HQ decision 2026-09-28: a PERMANENT condition gets one loud notice and
                           # a daily line while it is unchanged — not a 20-minute nag. It re-alarms
                           # on a change of CLASS (merge landed / new condition), never on growth:
                           # the pending count climbs with every commit and that is not news.


def resolve_remote() -> str:
    """The vault's remote name is NOT guaranteed to be 'origin'.

    2026-09-28: the remote was renamed `origin` -> `vault` (the transport protocol documents
    `git push vault main`). This script hardcoded `origin/main`, so from that moment `git fetch
    origin` failed, the unpushed count was unreadable, and the drain exited 0 every 20 minutes
    while backing NOTHING up — a green light on a dead leg. Resolve the name; never assume it.
    """
    rc, out = run("git remote")
    names = [n.strip() for n in out.split() if n.strip()]
    if not names:
        return ""
    for preferred in ("vault", "origin"):
        if preferred in names:
            return preferred
    return names[0]


def run(cmd, timeout=180):
    try:
        p = subprocess.run(cmd, cwd=VAULT, shell=True, capture_output=True,
                           text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    except Exception as e:
        return 1, f"{type(e).__name__}: {e}"


def load_state() -> dict:
    """State is JSON, so coerce to the types we actually do arithmetic on."""
    d: dict = {"stuck_since": 0, "spoke_at": 0, "last_drain": 0}
    try:
        with open(STATE) as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            d["stuck_since"] = int(raw.get("stuck_since") or 0)
            d["spoke_at"] = int(raw.get("spoke_at") or 0)
            d["last_drain"] = int(raw.get("last_drain") or 0)
    except Exception:
        pass
    return d


def save_state(s):
    tmp = STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(s, f, indent=2)
    os.replace(tmp, STATE)


def main():
    ap = argparse.ArgumentParser(description="Drain unpushed vault commits through the gate.")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--speak-test", action="store_true")
    a = ap.parse_args()

    st = load_state()
    now = int(time.time())

    # 1) fetch first — a stale <remote>/main makes "unpushed" a lie in either direction
    remote = resolve_remote()
    if not remote:
        out = {"status": "UNKNOWN", "why": "the vault repo has no remote configured"}
        print(json.dumps(out) if a.json else "  \u26a0\ufe0f  vault-push-drain: no git remote configured")
        return 0
    remote_branch = f"{remote}/main"
    run(f"git fetch {remote} --quiet", timeout=120)

    rc, ahead = run(f"git rev-list --count {remote_branch}..HEAD")
    try:
        pending = int(ahead.strip() or "0")
    except Exception:
        pending = -1

    if pending < 0:
        out = {"status": "UNKNOWN", "why": "could not count unpushed commits"}
        print(json.dumps(out) if a.json else "  \u26a0\ufe0f  vault-push-drain: cannot read the unpushed count")
        return 0

    if pending == 0:
        if st.get("stuck_since"):
            st["stuck_since"] = 0
            st["spoke_at"] = 0
            save_state(st)
        if a.json:
            print(json.dumps({"status": "CLEAN", "pending": 0}))
        elif a.speak_test:
            print("  \u2705 vault-push-drain: nothing to push")
        return 0

    # 2) IS THIS A FORK? That is a property of the GRAPH, not of a push attempt.
    #    Found 2026-09-28, an hour after the first fix: `forked` was inferred from the PUSH
    #    REJECTION. When the gate defers, git is never invoked, so no rejection is ever observed
    #    and a permanently-diverged branch was reported as DEFERRED — "retry next tick", forever.
    #    A permanent condition reported as a wait, one level below where it had just been fixed.
    #    Two costs, not one: the mislabel, AND a doomed push that still spends a gate slot.
    #    Ask the graph. It cannot be deferred.
    rc_fork, _ = run(f"git merge-base --is-ancestor {remote_branch} HEAD")
    graph_forked = rc_fork != 0        # non-zero == remote_branch is NOT an ancestor == cannot fast-forward

    # 3) try to land it — unless the graph already says it cannot land
    if graph_forked:
        rc, msg = 0, f"{remote_branch} is not an ancestor of HEAD (diverged)"
        deferred = False
        forked = True
    else:
        rc, msg = run(f"git push {remote} main", timeout=280)
        low = msg.lower()
        deferred = "deferred" in low
        # Still possible here: the branch diverged BETWEEN our fetch and our push (a peer
        # pushed first). Keep the rejection test as a second line of defence, not the first.
        forked = ("non-fast-forward" in low or "fetch first" in low
                  or "behind its remote counterpart" in low)

    if rc == 0 and not deferred and not forked:
        was_stuck = st.get("stuck_since")
        stuck_min = (now - was_stuck) / 60.0 if was_stuck else 0
        st["stuck_since"] = None
        st["spoke_at"] = None
        st["last_drain"] = now
        save_state(st)
        # a normal drain is invisible; only speak if this work had been stranded a while
        if was_stuck and stuck_min >= STUCK_ALERT_MIN:
            print(f"\U0001F4E4 vault-push-drain: {pending} commit(s) were stranded {stuck_min:.0f} min "
                  f"\u2014 pushed now. The brain is backed up again.")
        elif a.json:
            print(json.dumps({"status": "PUSHED", "pending": pending, "stuck_min": stuck_min}))
        elif a.speak_test:
            print(f"  \u2705 vault-push-drain: pushed {pending}")
        return 0

    # 3) did not land — remember when it started, retry next tick
    if not st.get("stuck_since"):
        st["stuck_since"] = now
    stuck_min = (now - int(st["stuck_since"])) / 60.0
    spoke = st.get("spoke_at") or 0

    do_speak = stuck_min >= STUCK_ALERT_MIN and (now - spoke) > 6 * 3600
    if do_speak:
        st["spoke_at"] = now
    save_state(st)

    if forked:
        # Speak at once and say the true thing: this needs a MERGE, not patience.
        if (now - spoke) > FORK_ALERT_HOURS * 3600:
            st["spoke_at"] = now
            save_state(st)
            print(f"\U0001F534 vault-push-drain: local main and {remote_branch} have FORKED "
                  f"\u2014 {pending} commit(s) cannot land by retrying. This needs a merge, not a wait.")
            print(f"   git said: {msg.strip().splitlines()[-1][:140] if msg.strip() else 'no message'}")
        elif a.json:
            print(json.dumps({"status": "FORKED", "pending": pending, "stuck_min": stuck_min}))
        elif a.speak_test:
            print(f"  \U0001F534 vault-push-drain: FORKED ({pending} pending, stuck {stuck_min:.0f} min)")
        return 0

    if do_speak:
        print(f"\u26a0\ufe0f  vault-push-drain: {pending} commit(s) UNABLE TO PUSH for {stuck_min/60:.1f}h "
              f"\u2014 the gate keeps deferring. The vault is not being backed up.")
        print(f"   gate said: {msg.strip().splitlines()[-1][:140] if msg.strip() else 'no message'}")
    elif a.json:
        print(json.dumps({"status": "DEFERRED", "pending": pending, "stuck_min": stuck_min}))
    elif a.speak_test:
        print(f"  \u23f8  vault-push-drain: deferred ({pending} pending, stuck {stuck_min:.0f} min)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
