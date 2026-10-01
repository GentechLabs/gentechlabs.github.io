#!/usr/bin/env python3
"""constitution_trace.py — RULE -> SCRIPT -> CRON -> DELIVERY, and it CHECKS ITSELF.

WHY THIS EXISTS (Part 8, 2026-09-30). Jordan: *"I don't know if we ever properly wired everything
together."* The answer is a table, not an opinion: one row per rule, columns for the component that
implements it, the job that runs it, and where the result is delivered. A BLANK CELL IS THE FINDING.

WHY IT CHECKS ITSELF (Part 13). A rule written for a human can leave a gap because the human fills it
without noticing; an agent fills it with whatever default it finds first. So this is not a document
that describes the wiring -- it VERIFIES it. If a script is missing, a job is gone, or a delivery
target is unset, this FAILS. A traceability table that cannot fail is a human document in an agent's
body, which is the exact defect it is meant to detect.

Run:  python3 constitution_trace.py            # verify all links, exit 1 if any are broken
      python3 constitution_trace.py --gaps     # show only the unwired rules
"""
import json, os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILE_CRON = "/root/.hermes/profiles/gentech-treasury/cron/jobs.json"

# rule id -> (constitution part, implementing component, cron job substring or None, delivery)
# delivery: "telegram" | "local" | "(none)"  — None means the row is UNWIRED and is a finding.
TRACE = [
 ("R-SHAPE-CLASSIFY", "Part 2",   "lfj_shapes.py",        None,                  "local"),
 ("R-SHAPE-DEPLOY",   "Part 2",   "lfj_bid_deploy.py",    None,                  "local"),
 ("R-CURVE-DEPLOY",   "Part 2",   "lfj-curve-deploy.sh",  None,                  "local"),
 ("R-SHAPE-HOLD",     "Part 2",   "lfj_recenter.py",      "Position Watchdog",   "telegram"),
 ("R-ACT-ALONE",      "Part 3",   "lfj_recenter.py",      "Position Watchdog",   "telegram"),
 ("R-SCANNER-CADENCE","Part 3A",  "fee_efficiency.py",    "Position Watchdog",   "telegram"),
 ("R-EFF-FLOOR-75",   "Part 3A",  "fee_efficiency.py",    "Position Watchdog",   "telegram"),
 ("R-EFF-FLOOR-COPY", "Part 3A",  "lp-monitor-v2.py",     None,                  "local"),
 ("R-DIP-EXEMPTION",  "Part 3A",  "fee_efficiency.py",    "Position Watchdog",   "telegram"),
 ("R-SELL-STRENGTH",  "Part 3B",  None,                   None,                  None),
 ("R-PULLBACK-70-30", "Part 3B",  None,                   None,                  None),
 ("R-EUPHORIA-EXIT",  "Part 3C",  None,                   None,                  None),
 ("R-HOLD-GATE",      "Part 4",   "steward_hold.py",      None,                  "local"),
 ("R-HOLD-TRIGGER",   "Part 4",   "hold_trigger.py",      None,                  "local"),
 ("R-BUYLIST",        "Part 4",   "steward-buylist.py",   "Steward Watch List",  "telegram"),
 ("R-COQ-DIP-BUY",    "Part 4",   "coq_accumulator.py",   "COQ Accumulator",     "telegram"),
 ("R-HONESTY-HUB",    "Part 5",   "defi_hub_data.py",     "hub refresh",         "web"),
 ("R-CRON-HEALTH",    "Part 8",   "cron_health.py",       "Cron Health Sentinel","telegram"),
 ("R-CRON-FLEET",     "Part 8",   "cron_health_fleet.py", "Fleet Cron Health",   "telegram"),
 ("R-BIN-FOUNDATION", "Part 10",  "lfj_shapes.py",        None,                  "local"),
 ("R-WIDTH-ADVISOR",  "Part 10",  "width_advisor.py",     None,                  "local"),
 ("R-ESCALATE",       "Part 9",   None,                   None,                  None),
 ("R-GAS-RESERVE",    "Part 5",   "gas_reserve.py",       None,                  "local"),
 ("R-EXIT-RAILS",     "Part 4",   "lfj_exit.py",          None,                  "local"),
]

def jobs():
    try:
        j = json.load(open(PROFILE_CRON))
        return j if isinstance(j, list) else j.get("jobs", [])
    except Exception:
        return None

def _referenced_anywhere(fname, all_jobs):
    """Is this file actually EXECUTED or IMPORTED by anything? A script that nothing runs is wired
    in appearance only -- the least visible kind of unwired rule, and the one a name-based audit
    always misses."""
    for x in (all_jobs or []):
        if fname in str(x.get("script") or "") or fname in str(x.get("name") or ""):
            return True
    stem = fname[:-3] if fname.endswith(".py") else fname
    for cand in ("*.py", "*.sh"):
        for f in glob.glob(os.path.join(HERE, cand)):
            if os.path.basename(f) == fname:
                continue
            try:
                body = open(f, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            if f"{stem}" in body and ("import " in body or "./" + fname in body):
                return True
    return False


def main():
    gaps_only = "--gaps" in sys.argv
    all_jobs = jobs()
    unwired, broken, jedge = [], [], []
    for rid, part, script, cron, deliver in TRACE:
        unwired_row = script is None
        problems = []
        if script and not os.path.exists(os.path.join(HERE, script)):
            problems.append(f"script '{script}' MISSING")
        if cron and all_jobs is not None:
            if not any(cron.lower() in str(x.get("name", "")).lower() for x in all_jobs):
                problems.append(f"cron '{cron}' NOT FOUND")
        if cron is None and not unwired_row and deliver not in (None, "local", "web"):
            problems.append("cron-less rule claims a delivery")
        if script and not problems and not _referenced_anywhere(script, all_jobs):
            problems.append(f"'{script}' is referenced by NO job and imported by nothing (dead)")
        if unwired_row:
            unwired.append((rid, part))
        elif problems:
            broken.append((rid, part, problems))
        else:
            jedge.append((rid, part))

    W = 20
    print("\n  ══ CONSTITUTION TRACE — rule → script → cron → delivery ══\n")
    for rid, part, script, cron, deliver in TRACE:
        if unwired_row := (script is None):
            mark = "🔴 UNWIRED"
        elif any(p.startswith("script") or p.startswith("cron") for p in
                 next((b[2] for b in broken if b[0] == rid), [])):
            mark = "⚠️  BROKEN"
        else:
            mark = "✅ WIRED "
        if gaps_only and mark == "✅ WIRED ":
            continue
        print(f"  {mark} {rid:<{W}} {part:<9} {(script or '—'):<22} {(cron or '—'):<22} {deliver or '—'}")

    print(f"\n  ── {len(jedge)} wired · {len(unwired)} UNWIRED · {len(broken)} BROKEN ──")
    if unwired:
        print("\n  BLANKS ARE THE FINDINGS — these rules exist in prose and nowhere executable:")
        for rid, part in unwired:
            print(f"    {rid:<{W}} ({part})")
    if broken:
        print("\n  BROKEN LINKS — declared wiring that does not exist:")
        for rid, part, probs in broken:
            print(f"    {rid:<{W}} {', '.join(probs)}")
    if all_jobs is None:
        print("\n  ⚠️  could not read the cron job list — job links UNVERIFIED, not passed")
    print()
    return 1 if (unwired or broken) else 0

if __name__ == "__main__":
    sys.exit(main())
