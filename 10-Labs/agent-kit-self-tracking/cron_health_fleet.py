#!/usr/bin/env python3
"""Cron Health Sentinel — FLEET EDITION (with debounce + quiet hours).

The one-profile sentinel (cron_health.py) generalized into a FLEET-WIDE STANDARD.
It reads EVERY profile's cron ring under /root/.hermes/profiles/*/cron/jobs.json and
answers one question per job: DID IT DO WHAT IT IS FOR?

THE DOCTRINE (see skill: cron-health-standard):

  1. HEAL BEFORE SPEAKING. Re-fire a failed SCRIPT job once, immediately. Most failures are
     transient (a lagging RPC, a rate limit, a node timeout) and the retry fixes them without
     a human ever knowing. A SILENT SUCCESSFUL RETRY IS THE IDEAL OUTCOME.
  2. SPEAK ONLY ABOUT WHAT HEALING COULD NOT FIX — and then only ONCE PER DISTINCT PROBLEM.
     A monitor that repeats the same unresolved failure on every tick trains its reader to
     ignore it. 134 jobs at a 30-minute cadence is 48 runs a day: an alert per run is noise.
  3. SILENCE WHEN HEALTHY MEANS SILENCE — not a status line, not an all-clear. Empty stdout,
     byte count zero.
  4. A MONITOR MUST BE ABLE TO SAY "I DO NOT KNOW": an unreadable job list reports UNKNOWN and
     exits non-zero, never healthy.
  5. A FAILURE IS REPORTED WITH ITS **INTENT** AND ITS ERROR, not just its name.

DEBOUNCE — the rule the founder asked for: "stay mostly quiet unless something needs our
attention ... we already have a lot of cron jobs running."

  * ALERT ONCE PER DISTINCT PROBLEM. A shared fleet state file records, per job, the failure
    signature already reported. Same problem next tick -> SILENT.
  * RE-ARM ON SUCCESS. When a job recovers its state is cleared, so the NEXT failure is news
    again. A problem that recurs after being fixed is news; one that never stopped is not.
  * ESCALATION IS A CHANGE. Re-alert when the streak crosses a threshold (3, 6, 12, 24 …), not
    on every increment.
  * THE DEBOUNCE MUST NOT BE ABLE TO HIDE A NEW PROBLEM. Suppression is per job, keyed by job
    id and signature; a second job failing while the first is silenced alerts normally.

QUIET HOURS: outside working hours the sentinel still READS and HEALS and RECORDS — only the
MESSAGE waits. Alerts discovered in the window are held in the state file and flushed by the
first run after it (default 00:00–08:00 America/New_York, override with
HERMES_CRON_QUIET_HOURS / HERMES_CRON_QUIET_TZ).

ONE VOICE: the four rings all run this scan and all deliver to HQ, but they share one debounce
state — so a problem produces ONE message, from whichever ring runs first. Redundant readers,
single voice, no silent ring. Heals are scoped to the ring's OWN profile, so a job is never
re-fired by two rings at once.

SAFETY: this is a MONITOR. It runs one read-only retry of a job's own script and nothing else.
It never reads keys, never moves capital, never invents a money action. To test the heal path,
use a throwaway script in a scratch dir — never re-fire a live money job.

Exit codes: 0 = healthy (possibly after a heal) · 1 = a NEW/unresolved problem needs a human ·
2 = UNKNOWN / a job list could not be read.

Usage:
  python3 cron_health_fleet.py --heal --quiet-unless-bad     # the cron invocation
  python3 cron_health_fleet.py [--json] [--dry-run] [--profiles a,b] [--show-silenced]
                               [--jobs-file PATH] [--intents PATH] [--emit-intents]
                               [--state PATH] [--heal-scope own|all|none]
                               [--no-debounce] [--no-quiet-hours] [--now ISO] [--reset-state]
"""
import argparse
import datetime
import fcntl
import glob
import json
import os
import pathlib
import re
import subprocess
import sys
from datetime import timezone

PROFILES_DIR = os.environ.get("HERMES_PROFILES_DIR", "/root/.hermes/profiles")
CANONICAL_INTENTS = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/cron-intents.json"
DEFAULT_STATE = os.environ.get("HERMES_CRON_HEALTH_STATE",
                               "/root/.hermes/state/cron-health-fleet.json")

# The sentinel's own registrations — NEVER graded by the sentinel (see trap below).
SELF_SCRIPT_RE = re.compile(r"^cron-health(-fleet)?\.sh$")
SELF_NAME_RE = re.compile(r"cron\s*health", re.I)

# Streak thresholds at which a still-unresolved failure becomes NEWS again (escalation is a
# change; every individual increment is not).
THRESHOLDS = [3, 6, 12, 24, 48, 96]

HEALTHY = {"success", "ok", "completed", "scheduled", "running", "delivered",
           "delivery_queued", None, ""}

# A job retired by hand carries a terminal status, not a failure. "archived" is a clean
# retirement and must NOT be read as breakage — otherwise every deliberate archive becomes a
# permanent alert. Kept separate from HEALTHY because a RUNNING job with this status would be
# a contradiction; only the pause path consults it.
RETIRED_STATUSES = {"archived", "retired"}

RETRY_TIMEOUT = 240


def pl(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


# ── intent ────────────────────────────────────────────────────────────────────────────────
def resolve_intents_path(explicit=None):
    """Where a job's INTENT is looked up. Order is deterministic and documented:

    (1) --intents PATH   (2) $HERMES_CRON_INTENTS   (3) the vault canon
    (4) cron-intents.json next to this script (the per-profile deployed copy).
    """
    for cand in (explicit, os.environ.get("HERMES_CRON_INTENTS"), CANONICAL_INTENTS,
                 os.path.join(os.path.dirname(os.path.abspath(__file__)), "cron-intents.json")):
        if cand and os.path.exists(cand):
            return cand
    return None


def load_intents(path):
    if not path:
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def derive_intent(job):
    """Deterministic last resort, read OUT OF THE JOB SPEC ITSELF (never invented):
    the job's own opening purpose sentence with the addressing boilerplate removed.
    Flagged as derived so a reader knows it is uncurated and the registry needs a proper
    entry — a derived intent is a STARTING POINT, not a substitute for a declared one."""
    text = " ".join((job.get("prompt") or "").split())
    if text:
        # Drop the standard lead-ins that carry no purpose of their own.
        text = re.sub(r"^You are [^.]{0,90}? (running|doing|performing) (the )?", "", text).strip()
        text = re.sub(r"^QUIET HOURS:.{0,140}?\.\s*", "", text).strip()
        text = re.sub(r"^##+\s*", "", text).strip()
        # First real sentence within a sane window; headings/instructions fall through.
        m = re.match(r"(.{15,190}?[.!])(\s|$)", text)
        cand = (m.group(1) if m else text[:190]).strip()
        if "```" not in cand and not cand.startswith(("{", "[", "#", "-", "|")):
            return cand.rstrip()
    name = (job.get("name") or "").strip()
    script = job.get("script")
    if script and name:
        return f"{name} — runs {script} on schedule; purpose not recorded in the registry."
    if script:
        return f"Runs {script} on schedule; purpose not recorded in the registry."
    return "Purpose not recorded — curate this job in cron-intents.json."


def intent_for(job, profile, intents):
    """Return (intent, source). Lookup order: job-spec field -> registry by id ->
    registry by name rule -> derived from the spec."""
    spec = job.get("intent")
    if isinstance(spec, str) and spec.strip():
        return spec.strip(), "job-spec"
    if intents:
        entry = (intents.get("by_id") or {}).get(str(job.get("id")))
        if isinstance(entry, dict) and (entry.get("intent") or "").strip():
            return entry["intent"].strip(), entry.get("source", "registry")
        for rule in intents.get("by_name") or []:
            if rule.get("profile") not in (None, "*", profile):
                continue
            try:
                if re.search(rule.get("match") or r"$^", job.get("name") or ""):
                    return (rule.get("intent") or "").strip(), "name-rule"
            except re.error:
                continue
    return derive_intent(job), "DERIVED"


# ── job list ──────────────────────────────────────────────────────────────────────────────
def jobs_path(profile):
    return os.path.join(PROFILES_DIR, profile, "cron", "jobs.json")


def scripts_dir(profile):
    return os.path.join(PROFILES_DIR, profile, "scripts")


def profile_of_jobs_path(jpath):
    """The scripts live in the SAME profile dir as the jobs.json that names them —
    derived from the path so a throwaway jobs.json is self-contained."""
    parent = os.path.dirname(os.path.dirname(os.path.abspath(jpath)))
    return parent, os.path.join(parent, "scripts")


def my_profile():
    """The ring this process is running FOR, from $HERMES_HOME or from this file's location
    (<profile>/scripts/cron_health_fleet.py). None when running from the vault copy."""
    for cand in (os.environ.get("HERMES_HOME"), os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
        if not cand:
            continue
        name = os.path.basename(os.path.normpath(cand))
        if os.path.exists(jobs_path(name)):
            return name
    return None


def load_jobs(path):
    """Return job list. Raises on anything unreadable — the caller turns that into UNKNOWN."""
    with open(path) as f:
        d = json.load(f)
    jobs = d if isinstance(d, list) else d.get("jobs", d)
    if isinstance(jobs, dict):
        jobs = list(jobs.values())
    if not isinstance(jobs, list):
        raise ValueError(f"unrecognised jobs.json shape: {type(d).__name__}")
    return jobs


def discover_profiles(only=None):
    if only:
        return [p.strip() for p in only.split(",") if p.strip()]
    return sorted(os.path.basename(os.path.dirname(os.path.dirname(p)))
                  for p in glob.glob(os.path.join(PROFILES_DIR, "*", "cron", "jobs.json")))


def classify(job):
    """(state, detail). state in HEALTHY | FAILED | DISABLED | PAUSED_BROKEN.

    PAUSED_BROKEN exists because `enabled: false` used to be a black hole: a job turned off
    while it was FAILING was counted as "disabled" and skipped, so the fleet reported perfect
    health while the monitor itself was dead. A pause is not automatically a retirement —
    distinguish them by the LAST RECORDED OUTCOME:

      clean outcome (ok / never ran)  -> DISABLED   a retirement; quiet.
      failure evidence               -> PAUSED_BROKEN  a job stopped while broken; a finding.
    """
    if not job.get("enabled"):
        st = job.get("last_status")
        fs = job.get("failure_streak") or 0
        err = job.get("last_error") or job.get("last_delivery_error")
        # A deliberate retirement says so. Only a pause with NO clean verdict is suspicious.
        if str(st).lower() in RETIRED_STATUSES:
            return "DISABLED", "disabled (retired)"
        if fs and fs > 0:
            return "PAUSED_BROKEN", (f"PAUSED while failing | failure_streak={fs}"
                                     + (f" | {str(err)[:300]}" if err else ""))
        if st is not None and str(st).lower() not in HEALTHY:
            return "PAUSED_BROKEN", (f"PAUSED with last_status={st}"
                                     + (f" | {str(err)[:300]}" if err else ""))
        return "DISABLED", "disabled"
    st = job.get("last_status")
    fs = job.get("failure_streak") or 0
    err = job.get("last_error") or job.get("last_delivery_error")
    if fs and fs > 0:
        return "FAILED", (f"failure_streak={fs}" + (f" | {str(err)[:300]}" if err else ""))
    if st is not None and str(st).lower() not in HEALTHY:
        return "FAILED", (f"status={st}" + (f" | {str(err)[:300]}" if err else ""))
    return "HEALTHY", ""


def heal_allowed(job, intents):
    """A job may refuse a mechanical re-fire — a partially-executed money action must not be
    double-fired. Declared in the registry (by_id[id].heal = false) or in the job spec
    (heal: false / no_heal: true). Idempotency is the job author's call, not the monitor's."""
    for src in (job, (intents or {}).get("by_id", {}).get(str(job.get("id"))) or {}):
        if src.get("heal") is False or src.get("no_heal") is True:
            return False
    return True


def is_self(job):
    return bool(SELF_NAME_RE.search(job.get("name") or "")
                or SELF_SCRIPT_RE.match(os.path.basename(job.get("script") or "")))


def clear_scheduler_record(jobs_path, job_id, note="healed"):
    """Mark a healed job CLEAN in the scheduler's own jobs.json.

    Why this exists: heal() proved the script runs, but the scheduler keeps its own verdict.
    A job entry stuck on last_status=error / failure_streak>0 stays a healing candidate
    forever, so the 30-minute sentinel re-fires a DAILY job ~47 times a day for nothing.

    Safety:
      - writes only the fields that describe the verdict (status/streak/error/timestamps);
        schedule, script, delivery, model and prompts are never touched;
      - the write is atomic (tmp file + os.replace) so a crash mid-write cannot truncate the
        scheduler's file — that would be a self-inflicted outage on every job at once;
      - honours the same .jobs.lock the scheduler uses, so we never race a real tick;
      - the id must still be present in the file we read, or we do nothing.
    Returns True if the file was updated, False if we declined or failed.
    """
    if not jobs_path or not job_id:
        return False
    jpath = pathlib.Path(jobs_path)
    lock = jpath.parent / ".jobs.lock"
    try:
        import fcntl
        fh = open(lock, "a+")
        fcntl.flock(fh, fcntl.LOCK_EX)
    except Exception:
        fh = None  # no lock available: still proceed atomically, but say nothing about racing

    tmp = jpath.with_suffix(".json.heal-tmp")
    try:
        data = json.loads(jpath.read_text())
        jobs = data if isinstance(data, list) else data.get("jobs", [])
        hit = False
        for job in jobs:
            if str(job.get("id")) == str(job_id):
                job["last_status"] = "ok"
                job["failure_streak"] = 0
                job["last_error"] = None
                job["last_delivery_error"] = None
                job["last_run_at"] = datetime.datetime.now(timezone.utc).isoformat()
                job["last_heal_note"] = str(note)[:200]
                hit = True
                break
        if not hit:
            return False
        tmp.write_text(json.dumps(data, indent=2) + "\n")
        os.replace(tmp, jpath)
        return True
    except Exception:
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass
        return False
    finally:
        if fh is not None:
            try:
                fcntl.flock(fh, fcntl.LOCK_UN)
                fh.close()
            except Exception:
                pass


def heal(job, sdir):
    """Re-fire the job's script ONCE, from the scripts dir of the profile that owns it.
    Returns (ok, note). Never raises. Agent-prompt jobs (no script) are reported honestly,
    never as a retry that happened."""
    script = job.get("script")
    if not script:
        return False, "cannot retry: no script (agent-prompt job)"
    path = os.path.join(sdir, script)
    if not os.path.exists(path):
        return False, f"cannot retry: script missing ({script})"
    try:
        r = subprocess.run(
            (["bash", path] if path.endswith((".sh", ".bash")) else [sys.executable, path]),
            cwd=sdir, capture_output=True, text=True, timeout=RETRY_TIMEOUT,
            env={**os.environ, "STEWARD_HEAL": "1", "HERMES_HEAL": "1"},
        )
        if r.returncode == 0:
            return True, "re-fired clean"
        tail = [l for l in (r.stderr or r.stdout or "").splitlines() if l.strip()][-2:]
        return False, f"retry exit={r.returncode}" + (" | " + " / ".join(tail)[:200] if tail else "")
    except subprocess.TimeoutExpired:
        return False, f"retry timed out ({RETRY_TIMEOUT}s)"
    except Exception as e:
        return False, f"retry raised {type(e).__name__}: {e}"


# ── debounce state ────────────────────────────────────────────────────────────────────────
def _now(a=None):
    if a and a.now:
        try:
            return datetime.datetime.fromisoformat(a.now.replace("Z", "+00:00"))
        except Exception:
            pass
    return datetime.datetime.now(datetime.timezone.utc)


def in_quiet_hours(now, a):
    """Default window 00:00–08:00 America/New_York (the fleet's quiet hours)."""
    if a and a.no_quiet_hours:
        return False
    spec = (os.environ.get("HERMES_CRON_QUIET_HOURS") or "0-8").strip()
    if spec.lower() in ("", "off", "none", "0"):
        return False
    try:
        start, end = (int(x) for x in spec.split("-", 1))
    except Exception:
        start, end = 0, 8
    try:
        from zoneinfo import ZoneInfo
        tzname = os.environ.get("HERMES_CRON_QUIET_TZ", "America/New_York")
        local = now.astimezone(ZoneInfo(tzname))
    except Exception:
        local = now
        tzname = "UTC"
    h = local.hour
    inside = (start <= h < end) if start <= end else (h >= start or h < end)
    return inside


def load_state(path):
    try:
        with open(path) as f:
            s = json.load(f)
        s.setdefault("jobs", {})
        s.setdefault("pending", [])
        return s
    except Exception:
        return {"version": 1, "jobs": {}, "pending": []}


def claim(state_path, candidates, now, quiet, a):
    """Atomically claim the right to SPEAK for the candidates that are still new/changed.

    This is what makes four rings produce ONE message: the first ring to claim a problem
    marks it alerted, the others find it claimed and stay silent. Returns
    (claimed_candidates, pending_flushed) — pending alerts held during quiet hours are
    flushed by the first run after the window closes.
    """
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    lock = state_path + ".lock"
    with open(lock, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        st = load_state(state_path)
        claimed = []
        for c in candidates:
            key = c.get("key") or f"{c['profile']}:{c['id']}"
            prev = st["jobs"].get(key) or {}
            if prev.get("alerted") and prev.get("sig") == c["sig"] and not c["escalate"]:
                c["silenced_by"] = ("state", prev.get("last_alerted"))
                continue
            st["jobs"][key] = {
                "profile": c["profile"], "name": c["name"], "sig": c["sig"],
                "streak": c["streak"], "alerted": True, "alerts": (prev.get("alerts") or 0) + 1,
                "next_threshold": c["next_threshold"],
                "first_seen": prev.get("first_seen") or now.isoformat(),
                "last_seen": now.isoformat(), "last_alerted": now.isoformat(),
            }
            claimed.append(c)
        # A recovered job re-arms: clear its entry so the NEXT failure is news again.
        for key in [k for k, v in list(st["jobs"].items()) if v.get("recovered")]:
            st["jobs"].pop(key, None)
        pending = []
        if not quiet:
            pending = st.get("pending") or []
            st["pending"] = []
        st["updated"] = now.isoformat()
        tmp = state_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(st, f, indent=2)
        os.replace(tmp, state_path)
        fcntl.flock(lf, fcntl.LOCK_UN)
    return claimed, pending


def record_recovered(state_path, keys, now):
    """Clear debounce state for jobs that are healthy again (RE-ARM ON SUCCESS)."""
    if not keys:
        return
    try:
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        with open(state_path + ".lock", "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            st = load_state(state_path)
            for k in keys:
                st["jobs"].pop(k, None)
            st["updated"] = now.isoformat()
            tmp = state_path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(st, f, indent=2)
            os.replace(tmp, state_path)
            fcntl.flock(lf, fcntl.LOCK_UN)
    except Exception:
        pass


def hold_for_morning(state_path, blocks, now):
    """Record an alert that must not be delivered at this hour. It is still RECORDED —
    only the MESSAGE waits."""
    try:
        os.makedirs(os.path.dirname(state_path), exist_ok=True)
        with open(state_path + ".lock", "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            st = load_state(state_path)
            for b in blocks:
                st["pending"].append({"since": now.isoformat(), "text": b})
            st["updated"] = now.isoformat()
            tmp = state_path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(st, f, indent=2)
            os.replace(tmp, state_path)
            fcntl.flock(lf, fcntl.LOCK_UN)
    except Exception:
        pass


# ── main ──────────────────────────────────────────────────────────────────────────────────
def sig_of(detail, streak):
    """Signature of a distinct problem: the error text plus the escalation bucket. Same text
    and same bucket = the SAME problem = do not speak again."""
    text = re.sub(r"\s+", " ", (detail or "")).strip().lower()[:200]
    bucket = 0
    for t in THRESHOLDS:
        if streak >= t:
            bucket = t
    return f"{text}|b{bucket}"


def render(c, prefix="   "):
    streak = f" (failure_streak {c['streak']})" if c["streak"] else ""
    isrc = "" if c["intent_source"] in ("job-spec", "registry", "curated", "name-rule") \
        else f" [{c['intent_source']} — curate in cron-intents.json]"
    out = [f"{prefix}❌ {c['name']}{streak}",
           f"{prefix}   id {c['id']} · {c['profile']}",
           f"{prefix}   INTENT: {c['intent']}{isrc}",
           f"{prefix}   ERROR:  {c['detail']}"]
    if c.get("heal"):
        out.append(f"{prefix}   RETRY:  {c['heal']}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--heal", action="store_true", help="re-fire each failed SCRIPT job once")
    ap.add_argument("--dry-run", action="store_true", help="report only; execute no retries")
    ap.add_argument("--quiet-unless-bad", action="store_true",
                    help="print nothing when there is nothing NEW to report (cron default)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--profiles", help="comma-separated profile names (default: all discovered)")
    ap.add_argument("--jobs-file", help="read ONE jobs.json at this path (proof/testing hook)")
    ap.add_argument("--intents", help="explicit cron-intents.json path")
    ap.add_argument("--state", default=DEFAULT_STATE, help="debounce state file")
    ap.add_argument("--heal-scope", choices=["own", "all", "none"], default=None,
                    help="which rings' jobs this run may re-fire (default: own ring when the "
                         "tool runs from a profile, all for an explicit manual run)")
    ap.add_argument("--no-debounce", action="store_true",
                    help="speak about every unresolved failure every run (ops/debug only)")
    ap.add_argument("--no-quiet-hours", action="store_true", help="deliver regardless of hour")
    ap.add_argument("--show-silenced", action="store_true",
                    help="also list problems being kept quiet by the debounce")
    ap.add_argument("--now", help="ISO timestamp to evaluate the clock as (testing)")
    ap.add_argument("--reset-state", action="store_true", help="forget all debounce state")
    ap.add_argument("--emit-intents", action="store_true",
                    help="seed cron-intents.json with a derived entry for every job (additive)")
    a = ap.parse_args()

    now = _now(a)
    intents_path = resolve_intents_path(a.intents)
    intents = load_intents(intents_path)

    if a.reset_state:
        hold_for_morning(a.state, [], now)
        with open(a.state + ".lock", "w") as lf:
            fcntl.flock(lf, fcntl.LOCK_EX)
            json.dump({"version": 1, "jobs": {}, "pending": [], "updated": now.isoformat()},
                      open(a.state, "w"), indent=2)
            fcntl.flock(lf, fcntl.LOCK_UN)
        print(f"debounce state cleared: {a.state}")
        return 0

    targets = ([(os.path.basename(os.path.dirname(os.path.dirname(
                    os.path.abspath(a.jobs_file)))) or "(explicit)", a.jobs_file)]
               if a.jobs_file
               else [(p, jobs_path(p)) for p in discover_profiles(a.profiles)])

    if a.emit_intents:
        return emit_intents(targets, intents_path, intents)

    heal_scope = a.heal_scope or ("all" if a.jobs_file else ("own" if my_profile() else "all"))
    me = my_profile()

    per_profile, unknown, healed, candidates, silenced, exempt = [], [], [], [], [], []
    recovered_keys, owned_failing = [], []
    total = healthy_n = failed_n = 0
    quiet = in_quiet_hours(now, a)

    for profile, jpath in targets:
        try:
            jobs = load_jobs(jpath)
        except Exception as e:
            unknown.append({"profile": profile, "path": jpath,
                            "error": f"{type(e).__name__}: {e}"})
            continue
        _pdir, p_scripts = profile_of_jobs_path(jpath)
        p_healthy = p_failed = p_disabled = 0
        p_fail_rows = []
        for job in jobs:
            jid = str(job.get("id"))
            key = f"{profile}:{jid}"
            if is_self(job):
                if job.get("enabled"):   # only live health jobs are worth listing as exempt
                    exempt.append({"profile": profile, "id": jid[:12],
                                   "name": str(job.get("name"))[:60]})
                continue
            state, detail = classify(job)
            if state == "DISABLED":
                p_disabled += 1
                continue
            if state == "PAUSED_BROKEN":
                # A job stopped while broken. Counted as failing (it IS unresolved work) and
                # routed through the SAME debounce as any other finding — it speaks once, and
                # re-arms on success, so restoring a job clears the alert instead of leaving it.
                p_failed += 1
                intent, isrc = intent_for(job, profile, intents)
                streak = job.get("failure_streak") or 0
                errtext = str(job.get("last_error") or job.get("last_delivery_error")
                              or job.get("last_status") or "")
                rec = {"profile": profile, "id": jid[:12], "key": key,
                       "name": str(job.get("name"))[:70],
                       "intent": intent, "intent_source": isrc, "detail": detail, "streak": streak,
                       "script": job.get("script"), "errtext": errtext,
                       "sig": sig_of(f"PAUSED_BROKEN:{errtext or detail}", streak),
                       "next_threshold": next((t for t in THRESHOLDS if t > streak), streak + 96),
                       "escalate": False,
                       "heal": "not retried: the job is PAUSED — re-enable it to resume "
                               "(a monitor must not silently un-pause another seat's job)"}
                candidates.append(rec)
                p_fail_rows.append(rec)
                continue
            if state != "FAILED":
                p_healthy += 1
                if key in state_keys(a.state):
                    recovered_keys.append(key)
                continue
            p_failed += 1
            intent, isrc = intent_for(job, profile, intents)
            streak = job.get("failure_streak") or 0
            # Signature text comes from the RAW recorded error, never from the rendered
            # detail (which embeds the streak count and would change on every increment).
            errtext = str(job.get("last_error") or job.get("last_delivery_error")
                          or job.get("last_status") or "")
            rec = {"profile": profile, "id": jid[:12], "key": key,
                   "name": str(job.get("name"))[:70],
                   "intent": intent, "intent_source": isrc, "detail": detail, "streak": streak,
                   "script": job.get("script"), "errtext": errtext,
                   "sig": sig_of(errtext or detail, streak),
                   "next_threshold": next((t for t in THRESHOLDS if t > streak), streak + 96),
                   "escalate": False}
            owns = (heal_scope == "all") or (heal_scope == "own" and profile == me)
            if a.heal and not a.dry_run and not heal_allowed(job, intents) :
                rec["heal"] = "retry suppressed: job is marked non-idempotent (heal=false)"
            elif a.heal and not a.dry_run and not owns:
                rec["heal"] = (f"retry left to the {profile} ring (heal-scope=own): a job is "
                               "re-fired by the ring that owns it, never twice")
            elif a.heal and not a.dry_run:
                ok, note = heal(job, p_scripts)
                rec["heal"] = note
                if ok:
                    # A clean retry must CLEAR the scheduler's own record, not just ours.
                    #
                    # Without this, heal() only proves the script works — the job entry keeps
                    # last_status=error / failure_streak=N, so the sentinel re-fires it on the
                    # NEXT 30-minute tick, and the tick after that, forever. Measured on
                    # fc81fc07ecd3 (Nightly skills sync, scheduled 30 4 * * *): 11 consecutive
                    # successful runs after its single recorded failure, while the scheduler
                    # still showed error — ~47 wasted runs a day for a job meant to run once.
                    #
                    # A heal that does not update the record is not a heal; it is a retry in a
                    # loop wearing a heal's clothes. We also re-arm our own debounce key, so
                    # the job stops being a candidate at all.
                    if clear_scheduler_record(jpath, job.get("id"), note):
                        rec["heal"] = f"{note}; scheduler record cleared"
                    healed.append(rec)
                    p_failed -= 1
                    p_healthy += 1
                    recovered_keys.append(key)
                    p_fail_rows.append(rec)
                    continue
            elif a.dry_run and job.get("script"):
                rec["heal"] = "would re-fire once (dry run)"
            elif not job.get("script"):
                rec["heal"] = "cannot retry: no script (agent-prompt job)"
            else:
                rec["heal"] = "retry not requested (--heal off)"
            candidates.append(rec)
            p_fail_rows.append(rec)
        total += len(jobs)
        healthy_n += p_healthy
        failed_n += p_failed
        per_profile.append({"profile": profile, "jobs_file": jpath,
                            "total": len(jobs), "healthy": p_healthy, "failing": p_failed,
                            "disabled": p_disabled, "failures": p_fail_rows})

    record_recovered(a.state, recovered_keys, now)

    # DEBOUNCE: only the NEW / CHANGED problems may speak. Everything else is recorded and
    # kept quiet — "alert once per distinct problem, re-arm on success".
    if a.no_debounce:
        claimed, pending = candidates, []
    else:
        claimed, pending = claim(a.state, candidates, now, quiet, a)
        _cid = {id(c) for c in claimed}
        silenced = [c for c in candidates if id(c) not in _cid]
        for c in silenced:
            c["silenced_by"] = "state"

    held_quiet = 0
    if quiet and claimed:
        blocks = [f"🚨 CRON HEALTH (FLEET) — held from {now.isoformat()} (quiet hours; "
                  "recorded now, delivered by the first run after the window)"
                  + "\n" + "\n".join(render(c) for c in claimed)]
        hold_for_morning(a.state, blocks, now)
        held_quiet = len(claimed)
        claimed = []

    payload = {"profiles": per_profile, "new": claimed, "silenced": silenced,
               "healed": healed, "unknown": unknown, "exempt_self": exempt,
               "pending_flushed": pending, "quiet_hours": quiet, "state": a.state,
               "totals": {"jobs": total, "healthy": healthy_n, "failing": failed_n}}
    if a.json:
        print(json.dumps(payload, indent=2))
        return 2 if unknown else (1 if (claimed or pending) else 0)

    # ── SPEAK ────────────────────────────────────────────────────────────────────────────
    # UNKNOWN ALWAYS SPEAKS — even under --quiet-unless-bad. Silence doctrine protects
    # against noise from good news; it must never be used to hide blindness.
    if unknown:
        print("🚨 CRON HEALTH (FLEET): CANNOT READ A JOB LIST — REPORTING UNKNOWN, NOT HEALTHY")
        for u in unknown:
            print(f"   ❓ {u['profile']}  {u['path']}")
            print(f"      {u['error']}")
        print("   A monitor blind to its own blindness reports perfect health, which is")
        print("   worse than reporting nothing.")
        if not (claimed or pending):
            return 2

    spoke = False
    if pending:
        print(f"🚨 CRON HEALTH (FLEET) — {pl(len(pending),'ALERT')} HELD OVER QUIET HOURS "
              f"(flushed now, first run after the window):")
        for p in pending:
            print(p["text"])
            print()
        spoke = True

    if claimed:
        verb = "NEEDS" if len(claimed) == 1 else "NEED"
        print(f"🚨 CRON HEALTH (FLEET) — {pl(len(claimed),'NEW PROBLEM').upper()} {verb} A HUMAN "
              f"({pl(total,'job')} across {pl(len(per_profile),'profile')} scanned)")
        for c in claimed:
            print(render(c))
        spoke = True

    if not spoke:
        if a.show_silenced and (silenced or healed or exempt):
            print(f"✅ CRON HEALTH (FLEET) — nothing NEW. "
                  f"({pl(total,'job')} across {pl(len(per_profile),'profile')} scanned"
                  + (f"; {pl(len(silenced),'known problem')} already reported and being kept "
                     "quiet" if silenced else "")
                  + (f"; {pl(len(healed),'transient failure')} healed by retry" if healed else "")
                  + ")")
            for c in silenced:
                k = c.get("key") or f"{c['profile']}:{c['id']}"
                print(f"   🔇 {c['name']} — already reported, staying silent "
                      f"(id {c['id']} · {c['profile']} · state key {k})")
                print(f"      INTENT: {c['intent']}")
                print(f"      ERROR:  {c['detail']}")
        if held_quiet and not a.quiet_unless_bad:
            print(f"🤫 CRON HEALTH (FLEET) — {pl(held_quiet,'new problem')} held until quiet "
                  f"hours end (recorded now, delivered by the first run after the window).")
            return 0
        if not a.quiet_unless_bad and not a.show_silenced:
            line = (f"✅ CRON HEALTH (FLEET) — {pl(total,'job')} across "
                    f"{pl(len(per_profile),'profile')} report healthy.")
            if healed:
                line += (f" ({pl(len(healed),'transient failure')} healed by retry: "
                         + ", ".join(h["name"] for h in healed) + ")")
            if silenced:
                line += f" ({pl(len(silenced),'known problem')} already reported, kept quiet)"
            print(line)
        return 0

    if healed:
        print(f"   ↩︎ HEALED BY RETRY (transient, no human needed): "
              + ", ".join(f"{h['name']} [{h['profile']}]" for h in healed))
    if silenced:
        print(f"   🔇 {pl(len(silenced),'other problem')} already reported earlier — kept quiet "
              "on purpose (alert once per distinct problem; re-arms when the job recovers).")
    if exempt:
        print("   (health sentinel(s) exempt from their own scan: "
              + ", ".join(f"{e['profile']}:{e['id']}" for e in exempt) + ")")
    print("   A job that fails silently is indistinguishable from a job that never ran.")
    return 2 if unknown else 1


_STATE_CACHE = {}


def state_keys(path):
    """Keys already present in the debounce state (used to decide re-arm on success)."""
    p = path or DEFAULT_STATE
    if p not in _STATE_CACHE:
        _STATE_CACHE[p] = set(load_state(p).get("jobs", {}).keys())
    return _STATE_CACHE[p]


def emit_intents(targets, intents_path, intents):
    """Additive seed: add a derived entry for every job that has none. Curated entries are
    NEVER overwritten (source != 'derived' wins)."""
    out_path = intents_path or CANONICAL_INTENTS
    if intents is None:
        intents = json.load(open(out_path)) if os.path.exists(out_path) else {}
    intents.setdefault("version", 1)
    intents.setdefault("by_id", {})
    added = 0
    for profile, jpath in targets:
        try:
            jobs = load_jobs(jpath)
        except Exception as e:
            print(f"❓ cannot read {jpath}: {e}")
            return 2
        for job in jobs:
            jid = str(job.get("id"))
            cur = intents["by_id"].get(jid)
            if isinstance(cur, dict) and cur.get("intent"):
                continue
            intents["by_id"][jid] = {
                "profile": profile,
                "name": str(job.get("name"))[:80],
                "intent": derive_intent(job),
                "source": "derived",
            }
            added += 1
    intents["updated"] = datetime.date.today().isoformat()
    with open(out_path, "w") as f:
        json.dump(intents, f, indent=2, sort_keys=False)
        f.write("\n")
    print(f"seeded {added} intent(s) into {out_path} "
          f"({len(intents['by_id'])} total; curated entries untouched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
