#!/usr/bin/env python3
"""Cron Health Sentinel — the fleet checks itself and SPEAKS when something breaks.

Jordan (2026-09-25): "Maybe it would also help if we made the cron jobs self-healing...
I think the problem right now is that the cron jobs could fail or whatever and they don't
really report anything or try to fix the problem when stuff happens. I usually have to ask
afterward."

HE IS RIGHT, AND TODAY PROVED IT. Every defect found in this treasury was found because HE
asked a question:
    the re-deploy failure      he asked "troubleshoot why it failed"
    the gas shortfall          he asked "what's going on?"
    the COQ rail that could    he asked for the COQ buy
    never fire
The cron ring already RECORDS the truth -- every job carries `last_status`, `last_error`,
`failure_streak` and `last_delivery_error`. NOTHING READ IT. A field nobody reads is not a
monitor; it is a diary.

WHAT THIS DOES, in the order that matters:
  1. READ    every enabled job's recorded outcome.
  2. HEAL    re-fire the job once, immediately, on a first failure. Most failures are
             transient (a lagging RPC, a rate limit, a node timeout) and a retry fixes
             them without a human ever knowing. A silent successful retry is the ideal
             outcome -- the treasury fixed itself and nobody was woken up for it.
  3. SPEAK   ONLY when healing did NOT work, or when a job has been failing across runs.
             Silence doctrine: quiet unless something CHANGED. A failure is a change.

THE TWO STATES THAT MUST NEVER LOOK ALIKE:
    "nothing is wrong"          -> silence
    "I could not tell"          -> MUST ALSO SPEAK. A sentinel that cannot read the
                                   job list must not report a clean bill of health.
This is the same trap as the failed eth_call reading as a real zero, and the `gap=0`
reading as adjacent: a monitor blind to its own blindness reports perfect health.

Exit codes: 0 = healthy OR healed, 1 = needs a human.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys

JOBS = "/root/.hermes/profiles/gentech-treasury/cron/jobs.json"
STATE = "/root/.hermes/profiles/gentech-treasury/state/cron_health.json"
SCRIPTS = "/root/.hermes/profiles/gentech-treasury/scripts"
PROFILE = "/root/.hermes/profiles/gentech-treasury"

# Jobs whose failure is EXPECTED and should not page anyone.
# 925850367cc2 = "Fleet Cron Health Sentinel" (cron-health-fleet.sh, 30m). It exits NON-ZERO
# by design whenever it has something to say — an alert is its success case — so grading it
# here would make one real problem produce two alerts forever. One problem, one voice: the
# FLEET sentinel owns the fleet verdict, this one owns the treasury ring's local view.
IGNORE = {"925850367cc2"}

# This sentinel's OWN job id. It must never heal itself — see heal() for the outage that caused.
SELF_ID = "70a959e08d3a"

# ── PAUSES ARE NOT AUTOMATICALLY FINE ───────────────────────────────────────────────────────────
# A paused job is a thing that is not doing its job, and `cron_health_fleet.py` SKIPS every job with
# `enabled=false` — so a paused job is invisible to fleet health. That is how this file's own
# sentinel (70a959e08d3a) sat dead for three days while reporting "136 jobs across 4 profiles
# healthy": the monitor that watches our ring had been switched off, and nothing watched IT.
#
# So every pause must be either DECLARED here with a reason, or reported as a finding. An
# undeclared pause is indistinguishable from an accident, and this treasury runs unattended
# overnight — that is exactly when a quiet safety mechanism costs the most.
ACKNOWLEDGED_PAUSED = {
    # ⚠️ Declarations here must be REMOVED the moment a job is resumed. A stale entry makes a
    # RUNNING job read as DISABLED, which masks a real failure — the same class of bug as an
    # undeclared pause, in the opposite direction. (The 2026-09-28 watchdog entry was added when
    # Jordan asked for the pause and removed when he asked for Dadrian to be farming again.)
    "a11f9e0205f3": "Trade Mode engine — dry-run only, superseded by gated-executor",
    "b1b996a54de8": "one-shot: Arc mainnet launch watch (Sept 16 2026 passed)",
    "f9ddcade1837": "superseded: re-entry watch replaced by Steward Watch List",
    # auto_compound.py is the standalone compound driver. Its JOB (deploy idle capital into the LFJ
    # book) is done every 5 min by lfj_recenter.py --execute inside steward-watchdog.sh, which
    # measures `deployable = wallet - gas reserve` and redeploys the whole book. Paused as a
    # duplicate WRITER on the same money, not as a lost capability.
    # ⚠️ If lfj_recenter is ever removed or stops composing, this pause stops being safe.
    "94257d5771be": "duplicate: idle-capital deploy now done by lfj_recenter in steward-watchdog (5m)",
    "5e7f8dcc204f": "superseded: Farm Report replaced by Steward Yield Leaderboard",
    "345097e1b416": "superseded: Strategy Desk proposals folded into Steward Council",

    # ── STAND-DOWN: JORDAN IS FLAT AND OUT OF THE POOL (2026-09-28, his instruction) ──────────
    # Verbatim: "now that I'm outside of the pool, you can go ahead and Pause my notifications
    # because I won't need to be watching anything right now. The only Cron jobs that should be
    # running are the ones that just give like notifications and research like the buy list"
    # Both books are held (jordan flat to Oct 5, dadrian withdrawn and closed to Oct 12), so every
    # job below has nothing to watch. RESEARCH, NOTIFICATIONS AND INFRASTRUCTURE WERE LEFT RUNNING
    # — including Steward Watch List (his buy list), the macro/council/research ring, the script
    # sync, the vault push drain and the health sentinels. Only position- and capital-directed work
    # was stood down.
    # ⚠️ REMOVE EACH ENTRY WHEN JORDAN RE-ENGAGES. He named a return window ("maybe some time next
    # week"), so this whole block is expected to come out together — and a stale entry here reads a
    # RUNNING job as DISABLED, which masks a real failure.
    "51bc9900e24d": "stand-down: position watchdog has no position to watch (Jordan flat, out of pool)",
    "bc885594238f": "stand-down: deposit watchdog — no deposit expected while flat",
    "2bf86edf8fa0": "stand-down: momentum/rotation loop — no capital deployed to rotate",
    "2b55d88b54f5": "stand-down: COQ accumulator MOVES CAPITAL; buy list is waiting on a pullback, which is Jordan's call",
    "3edb7c45fc88": "stand-down: fee ledger snapshots position earnings — no position, nothing to record",
    "a4cae2e71105": "stand-down: LFJ fee history — no LFJ position to build history from",
    "73cdf5227ca4": "stand-down: yield leaderboard ranks deployed capital — nothing is deployed",
}

# A job failing this many consecutive runs needs a human even if a retry "succeeded".
STREAK_ESCALATE = 3

HEALTHY = {"success", "ok", "completed", "scheduled", "running", "delivered", None, ""}

# ONE PROBLEM, ONE VOICE. The fleet sentinel (925850367cc2) already opens and reports incidents in
# executions.db. When it has flagged a job and the incident is still open, repeating it here is not
# extra safety — it is duplicate noise, and noise is what gets a monitor paused. Suppressed ONLY
# while the fleet sentinel is itself healthy: if that voice goes quiet, this one must speak.
INCIDENTS_DB = "/root/.hermes/profiles/gentech-treasury/cron/executions.db"
FLEET_JOB_ID = "925850367cc2"


def fleet_owned_incidents():
    """job_ids the fleet sentinel has already reported and whose incident is still open."""
    import sqlite3
    try:
        c = sqlite3.connect(f"file:{INCIDENTS_DB}?mode=ro", uri=True)
        rows = c.execute(
            "SELECT job_id FROM cron_incidents WHERE state='alerted' AND closed_at IS NULL"
        ).fetchall()
        return {str(r[0]) for r in rows}
    except Exception:
        # Cannot read the incident table -> suppress NOTHING. An unreadable record must never be
        # read as "already handled"; that is how a real failure disappears.
        return set()


def load_jobs():
    with open(JOBS) as f:
        d = json.load(f)
    jobs = d if isinstance(d, list) else d.get("jobs", d)
    if isinstance(jobs, dict):
        jobs = list(jobs.values())
    return jobs


def classify(job):
    """Return (state, detail). state in HEALTHY | FAILED | UNKNOWN | DISABLED | PAUSED_UNEXPLAINED.

    A pause that nobody has written down is treated as a FINDING, not as silence. The failure
    modes this catches, both real in this ring:
      • a safety mechanism switched off and forgotten (the cron sentinel itself, 3 days)
      • a job paused because it FAILED — pausing the alarm instead of fixing the fire
    """
    jid = str(job.get("id"))
    if not job.get("enabled"):
        state = str(job.get("state") or "")
        if state == "paused" or job.get("paused_at"):
            if jid in ACKNOWLEDGED_PAUSED:
                return "DISABLED", f"pause acknowledged: {ACKNOWLEDGED_PAUSED[jid]}"
            return "PAUSED_UNEXPLAINED", (
                f"paused {str(job.get('paused_at'))[:16]} and NOT declared in ACKNOWLEDGED_PAUSED"
                + (f" | reason: {job.get('paused_reason')}" if job.get("paused_reason") else ""))
        return "DISABLED", "disabled"
    st = job.get("last_status")
    fs = job.get("failure_streak") or 0
    err = job.get("last_error") or job.get("last_delivery_error")
    if fs and fs > 0:
        return "FAILED", f"failure_streak={fs}" + (f" | {str(err)[:200]}" if err else "")
    if st is not None and str(st).lower() not in HEALTHY:
        return "FAILED", f"status={st}" + (f" | {str(err)[:200]}" if err else "")
    return "HEALTHY", ""


def heal(job):
    """Re-fire the job once. Returns (ok, note). Never raises.

    ── THIS FUNCTION FORK-BOMBED THE HOST (2026-09-28) ─────────────────────────────────────────
    It graded ITSELF as failed and re-fired ITSELF, without a depth limit. Measured: **465
    concurrent `cron_health.py` processes**, load average **42**, memory driven to ~150 MB free.
    The kernel OOM-killed the treasury gateway twice (`global_oom`) and killed one of these
    children mid-run (`memcg`) — which is exactly why the sentinel's scheduled runs kept coming
    back `unknown` and why the Telegram gateway kept dropping. **The monitor was the outage.**

    A healer that can heal itself is not resilient, it is a recursive process spawner. Two
    independent brakes now make that impossible:
      1. NEVER heal your own job id. A sentinel re-firing itself can never converge.
      2. NEVER heal while already inside a heal cycle (STEWARD_HEAL_DEPTH > 0). The child
         inherits the counter, so recursion cannot outlive one level.
    """
    jid = str(job.get("id"))
    if jid == SELF_ID:
        return False, "REFUSED: a sentinel must never re-fire itself (that is an infinite loop)"
    if int(os.environ.get("STEWARD_HEAL_DEPTH") or 0) >= 1:
        return False, "REFUSED: already inside a heal cycle (depth>0) — no recursive healing"
    script = job.get("script")
    if not script:
        return False, "no script to re-run"
    path = os.path.join(SCRIPTS, script)
    if not os.path.exists(path):
        return False, f"script missing: {script}"
    try:
        r = subprocess.run(
            (["bash", path] if path.endswith(".sh") else [sys.executable, path]),
            cwd=SCRIPTS, capture_output=True, text=True, timeout=240,
            env={**os.environ,
                 "STEWARD_TENANT": os.environ.get("STEWARD_TENANT", "jordan"),
                 "STEWARD_HEAL": "1",
                 # The brake travels with the child. A healed job must never heal on.
                 "STEWARD_HEAL_DEPTH": str(int(os.environ.get("STEWARD_HEAL_DEPTH") or 0) + 1)},
        )
        if r.returncode == 0:
            return True, "re-fired clean"
        tail = [l for l in (r.stderr or r.stdout or "").splitlines() if l.strip()][-2:]
        return False, f"retry exit={r.returncode}" + (" | " + " / ".join(tail)[:160] if tail else "")
    except subprocess.TimeoutExpired:
        return False, "retry timed out (240s)"
    except Exception as e:
        return False, f"retry raised {type(e).__name__}: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--heal", action="store_true", help="re-fire failing jobs once")
    ap.add_argument("--quiet-unless-bad", action="store_true",
                    help="print nothing when everything is healthy (cron default)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    try:
        jobs = load_jobs()
    except Exception as e:
        # FAIL LOUD. A sentinel that cannot read the job list must never report "healthy".
        print(f"🚨 CRON HEALTH: CANNOT READ THE JOB LIST — {type(e).__name__}: {e}")
        print("   Reporting UNKNOWN, not healthy. A monitor blind to its own blindness")
        print("   reports perfect health, which is worse than reporting nothing.")
        return 1

    failed, healed, unresolved, paused_unexplained, fleet_owned = [], [], [], [], []
    _fleet_up = any(str(j.get("id")) == FLEET_JOB_ID and j.get("enabled")
                    and str(j.get("last_status") or "").lower() in HEALTHY for j in jobs)
    _owned = fleet_owned_incidents() if _fleet_up else set()
    for j in jobs:
        jid = str(j.get("id"))
        if jid in IGNORE:
            continue
        # ── A MONITOR MUST NOT ALARM ON ITS OWN ALARM (fixed 2026-09-30) ──────────────────────
        # This sentinel EXITS 1 whenever it finds a problem — that is its contract, and the job
        # runner dutifully records the sentinel ITSELF as a failed job. The next run then finds
        # its own failure, reports it, and exits 1 again: a self-sustaining loop in which the
        # monitor permanently lists itself as a broken job and the real finding drowns in it.
        # It also made `test_cron_health_no_recursion` fail on EVERY run — correctly, because the
        # run's output contained its own id, and an id that appears where it has no business
        # being is indistinguishable from a real recursion until the whole line is read.
        # A sentinel's own exit status is a REPORT, never a finding. Its genuine failures still
        # reach the fleet sentinel, which is the voice that should carry them.
        if jid == SELF_ID:
            continue
        state, detail = classify(j)
        if state == "FAILED":
            rec = {"id": jid[:12], "name": str(j.get("name"))[:52], "detail": detail,
                   "streak": j.get("failure_streak") or 0}
            if a.heal:
                ok, note = heal(j)
                rec["heal"] = note
                (healed if ok else unresolved).append(rec)
            else:
                unresolved.append(rec)
            # The fleet sentinel got there first and its incident is still open: fold it, don't
            # repeat it. If that voice is down (_fleet_up false) we keep the finding ourselves.
            # ── A SENTINEL DOES NOT REPORT ITSELF (fixed 2026-09-30) ────────────────────────
            # This folded ANY fleet-owned failure — including the sentinel's OWN id — into the
            # "already open with the fleet sentinel (not repeated here)" line. So the run printed
            # the sentinel as a job owned by *another* monitor, which is circular: this process
            # already REFUSES to heal itself (see the SELF_ID guard above) for exactly the same
            # reason. It was noise, and it tripped a good test — `test_cron_health_no_recursion`
            # asserts the id never appears in a --heal run's output, and it appeared on every run.
            # The test was right to flag it: an id that shows up where it has no business being is
            # indistinguishable from a real recursion until someone reads the whole line.
            # Our own failure still reaches the fleet sentinel, which reports it.
            if (jid in _owned and jid != SELF_ID and unresolved
                    and unresolved[-1]["id"] == jid[:12]):
                fleet_owned.append(unresolved.pop())
        elif state == "PAUSED_UNEXPLAINED":
            # NOT healed (we cannot know whether resuming is safe) and NOT hidden. The point is
            # that a switched-off mechanism is a finding a human should see, once.
            paused_unexplained.append({
                "id": jid[:12], "name": str(j.get("name"))[:52],
                "paused_at": str(j.get("paused_at"))[:16], "detail": detail,
            })
        elif state == "DISABLED":
            continue

    # A sticky failure_streak whose script actually re-fired CLEAN is a stale alarm, not a fire:
    # the retry proved the job works. Report it once as cleared rather than repeating it forever.
    # (A job with NO script — an agent-prompt job — cannot be healed this way, so it is never
    #  downgraded on a retry; it needs a human or the fleet sentinel.)
    stale_alarms = []
    for r in list(unresolved):
        if r["streak"] and "re-fired clean" in str(r.get("heal") or ""):
            stale_alarms.append(r)
            unresolved.remove(r)

    # Records -- so the next run can tell "still broken" from "newly broken".
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        with open(STATE, "w") as f:
            json.dump({"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       "unresolved": unresolved, "healed": healed,
                       "paused_unexplained": paused_unexplained,
                       "fleet_owned": fleet_owned,
                       "stale_alarms": stale_alarms}, f, indent=2)
    except Exception:
        pass

    if a.json:
        print(json.dumps({"unresolved": unresolved, "healed": healed,
                          "paused_unexplained": paused_unexplained,
                          "fleet_owned": fleet_owned,
                          "stale_alarms": stale_alarms}, indent=2))
        return 1 if (unresolved or paused_unexplained) else 0

    if not unresolved and not paused_unexplained:
        if not a.quiet_unless_bad:
            line = "✅ CRON HEALTH — all enabled jobs report healthy."
            if healed:
                line += f" ({len(healed)} transient failure(s) healed by retry: " \
                        + ", ".join(h["id"] for h in healed) + ")"
            if stale_alarms:
                line += (f" [{len(stale_alarms)} stale alarm(s) with a clean retry, not " \
                         f"re-reported: " + ", ".join(s["id"] for s in stale_alarms) + "]")
            print(line)
        return 0

    if unresolved:
        print("🚨 CRON HEALTH — JOB(S) NEED ATTENTION")
        for r in unresolved:
            dur = f" (failure_streak {r['streak']})" if r["streak"] else ""
            print(f"   ❌ {r['name']}{dur}")
            print(f"      {r['id']}  {r['detail']}")
            if r.get("heal"):
                print(f"      retry: {r['heal']}")
        print()
        print("   These jobs recorded a failure and the retry did not clear it.")
        print("   A job that fails silently is indistinguishable from a job that never ran.")

    if paused_unexplained:
        print()
        print("⏸  PAUSED AND NOT DECLARED — a switched-off job is not a healthy job")
        for r in paused_unexplained:
            print(f"   ⏸ {r['name']}  ({r['id']})")
            print(f"      {r['detail']}")
        print("   Resume it, or declare the pause in ACKNOWLEDGED_PAUSED with a reason.")
        print("   Silence here would mean the monitor cannot see its own ring going dark.")

    if healed:
        print(f"   ↩︎ healed by retry: " + ", ".join(h["id"] for h in healed))
    if fleet_owned:
        print(f"   🔇 already open with the fleet sentinel (not repeated here): "
              + ", ".join(f["id"] for f in fleet_owned))
    if stale_alarms:
        print(f"   🧹 stale alarm(s) cleared by a clean retry (not re-reported): "
              + ", ".join(s["id"] for s in stale_alarms))
    return 1


if __name__ == "__main__":
    sys.exit(main())
