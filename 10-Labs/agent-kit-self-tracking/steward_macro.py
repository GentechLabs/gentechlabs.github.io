#!/usr/bin/env python3
"""
Steward — Macro-Event Auto-Execution Planner
=============================================
Turns the "news-driven rebalance" loop (Jordan, Aug 11 2026) into a reusable
pattern. Instead of hand-crafting two one-shot jobs per CPI/FOMC/NFP/PCE, this
module:

  1. Reads the upcoming economic calendar (via fed-event-tracker) for
     HIGH-impact events.
  2. For each imminent event (< ~36h away), decides the SHAPE the position
     should be in around release time:
        - BID_ASK in the ~24h window BEFORE a high-volatility macro event
        - CURVE after the event settles (post-event chop)
  3. Emits a TIMED PLAN: exactly when to reposition, and to what shape.
  4. --schedule mode: actually creates the one-shot cron jobs (rebalance +
     stand-down) so the loop runs itself.

The formula (Jordan's exact intent):
  check LP position -> what it is -> what it's doing -> where we want it ->
  withdraw -> redeploy -> verify.

Reuses: regime classifier, steward_execute.py (withdraw-redeploy --shape),
fed-event-tracker (calendar). All decisions are DETERMINISTIC from live data.

Modes:
  --dry-run (default): read calendar, print the timed plan. No cron, no funds.
  --schedule: create the one-shot rebalance + stand-down cron jobs.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone, timedelta

# ── Config ────────────────────────────────────────────────────────────────
FED_TRACKER = "/root/.hermes/profiles/gentech-treasury/scripts/fed-event-tracker.py"
EXECUTE_SCRIPT = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/steward_execute.py"
WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
GROUP_DELIVER = "telegram:-1002916759037"

# Timing knobs (Jordan's playbook)
PRE_EVENT_HOURS = 0.75        # reposition ~45min before release (T-0.75h)
PRE_WINDOW_HOURS = 36         # only auto-schedule events within this many hours
STAND_DOWN_DELAY_H = 24       # revert to CURVE ~24h after release
MACRO_SHAPE = "bid-ask"       # shape to hold during the macro window
POST_SHAPE = "curve"          # shape after it settles

# High-impact events that warrant repositioning (from fed-event-tracker)
HIGH_IMPACT_KEYWORDS = ("CPI", "FOMC", "NFP", "Non-Farm", "PCE", "FED", "Fed",
                        "Interest Rate", "GDP")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_calendar(text: str):
    """Extract (label, datetime_et) for imminent high-impact events from the
    fed-event-tracker text output. Dedupes calendar-list + impact-analysis lines.
    Returns a list of dicts.
    Handles the tracker's current formats:
      - "├─ 🔴 in 2 days: CPI (MoM)"
      - "🔴 TOMORROW: CPI (MoM)"
      - "🟠  NEXT: PPI"
    """
    import re as _re
    events = []
    seen = set()
    for line in text.splitlines():
        line = line.strip()
        m = _re.search(
            r"(?:in\s+(\d+)\s+days?|TOMORROW|TODAY|NEXT)\s*:\s*([A-Za-z][A-Za-z0-9 ()._/-]*)",
            line)
        if not m:
            continue
        day_offset = int(m.group(1)) if m.group(1) else (1 if ("TOMORROW" in m.group(0)) else 0)
        label = m.group(2).strip().strip("`")
        if not any(k.lower() in label.lower() for k in HIGH_IMPACT_KEYWORDS):
            continue
        base_key = label.lower().split("(")[0].strip()
        if base_key in seen:
            continue
        seen.add(base_key)
        events.append({"label": label, "day_offset": day_offset})
    return events


def et_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=-4)))


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Steward — macro-event auto-execution planner")
    ap.add_argument("--schedule", action="store_true",
                    help="create the one-shot rebalance + stand-down cron jobs")
    ap.add_argument("--dry-run", action="store_true", default=True)
    args = ap.parse_args()

    # 1. Read the calendar
    if not os.path.exists(FED_TRACKER):
        print("❌ fed-event-tracker.py not found"); return 1
    proc = subprocess.run([sys.executable, FED_TRACKER], capture_output=True, text=True, timeout=60)
    text = proc.stdout or ""
    events = parse_calendar(text)

    now = et_now()
    print("=" * 58)
    print("🛡️  STEWARD — MACRO-EVENT AUTO-EXECUTION PLAN")
    print("=" * 58)
    print(f"  Now (ET):   {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Events:     {len(events)} high-impact in view")

    if not events:
        print("  ➖ No imminent high-impact macro event. Holding current shape.")
        print("  (nothing to schedule — loop is quiet until a trigger appears)")
        return 0

    for ev in events:
        release_dt = now.replace(hour=8, minute=30, second=0, microsecond=0) + timedelta(days=ev["day_offset"])
        hours_to = (release_dt - now).total_seconds() / 3600
        rebal_dt = release_dt - timedelta(hours=PRE_EVENT_HOURS)
        stand_dt = release_dt + timedelta(hours=STAND_DOWN_DELAY_H)

        print(f"\n  🔴 {ev['label']}  →  release {release_dt.strftime('%Y-%m-%d %H:%M')} ET")
        print(f"     T-{hours_to:.1f}h out")
        print(f"     → BID_ASK at {rebal_dt.strftime('%H:%M')} ET (T-{PRE_EVENT_HOURS}h)")
        print(f"     → CURVE   at {stand_dt.strftime('%Y-%m-%d %H:%M')} ET (T+{STAND_DOWN_DELAY_H}h)")

        if hours_to > PRE_WINDOW_HOURS:
            print("     ⏭  outside auto-schedule window (>36h) — monitor only")
            continue

        if not args.schedule:
            print("     (--schedule to auto-create the rebalance + stand-down jobs)")
            continue

        # ── SCHEDULE: create the two one-shot jobs ──
        _schedule(rebal_dt, MACRO_SHAPE, ev["label"], stand_dt)
        print("     ✅ Scheduled both jobs")

    return 0


# ── Enforcement: one-shot cron jobs are written directly to jobs.json ──
JOBS_PATH = "/root/.hermes/profiles/gentech-treasury/cron/jobs.json"
# The execute script + flags that PERFORM the reposition (withdraw-redeploy)
# --execute --yes signs + sends; NOT used in dry-run scheduling.
EXEC_MODEL = "deepseek-v4-flash:0731"
EXEC_PROVIDER = "ollama-cloud"
# State file recording what we've scheduled (the VERIFIER reads this)
SCHEDULED_STATE = "/root/.hermes/profiles/gentech-treasury/scripts/.steward-macro-scheduled.json"


def _job_template(name, run_at_iso, prompt):
    """A one-shot cron job dict matching the scheduler's schema."""
    return {
        "id": uuid.uuid4().hex[:12],
        "name": name,
        "prompt": prompt,
        "skills": [],
        "skill": None,
        "model": EXEC_MODEL,
        "provider": EXEC_PROVIDER,
        "provider_snapshot": None,
        "model_snapshot": None,
        "base_url": None,
        "script": None,
        "no_agent": False,
        "monitor_script": None,
        "monitor_url": None,
        "monitor_state": None,
        "context_from": None,
        "schedule": {
            "kind": "once",
            "run_at": run_at_iso,
            "display": f"once at {run_at_iso[:16].replace('T', ' ')}",
        },
        "schedule_display": run_at_iso[:16].replace("T", " "),
        "repeat": {"times": 1, "completed": 0},
        "enabled": True,
        "state": "scheduled",
        "paused_at": None,
        "paused_reason": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "next_run_at": run_at_iso,
        "last_run_at": None,
        "last_status": None,
        "last_error": None,
        "last_delivery_error": None,
        "failure_streak": 0,
        "deliver": GROUP_DELIVER,
        "origin": {
            "platform": "telegram",
            "chat_id": "-1002916759037",
            "chat_name": "Gentech Treasury",
            "thread_id": None,
            "user_id": "7105876857",
            "scope_id": None,
        },
        "enabled_toolsets": ["terminal", "file"],
        "workdir": None,
    }


def _load_jobs():
    try:
        with open(JOBS_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"jobs": [], "updated_at": None}


def _save_jobs(jobs):
    jobs["updated_at"] = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(JOBS_PATH), exist_ok=True)
    with open(JOBS_PATH, "w") as f:
        json.dump(jobs, f, indent=4, ensure_ascii=False)


def _record_scheduled(event_label, rebal_dt, stand_dt, rebal_id, stand_id):
    """Persist what we scheduled so a verifier can confirm it's enforced."""
    data = {
        "label": event_label,
        "scheduled_at": datetime.now(timezone.utc).isoformat(),
        "rebalance": {"id": rebal_id, "run_at": rebal_dt.isoformat(), "shape": "bid-ask"},
        "stand_down": {"id": stand_id, "run_at": stand_dt.isoformat(), "shape": "curve"},
    }
    os.makedirs(os.path.dirname(SCHEDULED_STATE), exist_ok=True)
    with open(SCHEDULED_STATE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _schedule(rebal_dt, shape, label, stand_dt):
    """ACTUALLY create the two one-shot cron jobs in jobs.json.

    This closes the enforcement gap (Jordan Sep 8 2026): previously this was a
    [plan] marker that only PRINTED the schedule — nothing was ever written, so
    the machine talked about repositioning but never did it. Now it writes real
    one-shot rebalance + stand-down jobs to jobs.json AND records them to a
    state file (the verification layer confirms the scheduled action exists).
    """
    # Build the prompt for the rebalance job — self-contained, performs the
    # withdraw-redeploy to the macro shape, then verifies on-chain.
    rebal_prompt = (
        f"MACRO REPOSITION ({label}) — run the Steward's news-driven rebalance.\n\n"
        "The macro event releases today. Reposition the LFJ AVAX/USDC pool to "
        "BID_ASK (concentrated edges) to catch the volatility, then VERIFY. "
        "Execute exactly this (dry-run first, then --execute --yes):\n\n"
        f"  python3 /root/vaults/gentech/10-Labs/agent-kit-self-tracking/steward_execute.py "
        f"--mode withdraw-redeploy --shape bid-ask --execute --yes\n\n"
        "VERIFY (mandatory): after execution, read the position on-chain and confirm "
        "it's BID_ASK / 2-sided, IN range, not flat. If addLiquidity reverted, retry "
        "up to 3x with settled re-reads. Report the verification result — 'done' means "
        "funds confirmed in the repositioned LP, never a plausible summary.\n"
        "Deliver a concise mobile-safe result to the treasury group."
    )
    # Stand-down prompt — revert to CURVE after the event settles.
    stand_prompt = (
        f"MACRO STAND-DOWN ({label}) — the high-volatility window has passed. "
        "Revert the LFJ AVAX/USDC pool from BID_ASK back to CURVE (default chop shape). "
        "Execute exactly this (dry-run first, then --execute --yes):\n\n"
        f"  python3 /root/vaults/gentech/10-Labs/agent-kit-self-tracking/steward_execute.py "
        f"--mode withdraw-redeploy --shape curve --execute --yes\n\n"
        "VERIFY (mandatory): confirm on-chain the position is CURVE / 15 bins, IN range. "
        "Retry up to 3x on revert with settled re-reads. Report verification result. "
        "Deliver a concise mobile-safe result to the treasury group."
    )

    rebal_job = _job_template(
        f"Macro Reposition — {label} (Bid-Ask)", rebal_dt.isoformat(), rebal_prompt)
    stand_job = _job_template(
        f"Macro Stand-Down — {label} (Curve)", stand_dt.isoformat(), stand_prompt)

    jobs = _load_jobs()
    jobs["jobs"].append(rebal_job)
    jobs["jobs"].append(stand_job)
    _save_jobs(jobs)

    _record_scheduled(label, rebal_dt, stand_dt, rebal_job["id"], stand_job["id"])

    print(f"     ✅ WRITTEN rebalance job {rebal_job['id']} @ {rebal_dt.isoformat()} → {shape}")
    print(f"     ✅ WRITTEN stand-down job {stand_job['id']} @ {stand_dt.isoformat()} → curve")
    print(f"     ✅ Recorded to {SCHEDULED_STATE} (verifier input)")


if __name__ == "__main__":
    sys.exit(main())
