#!/usr/bin/env python3
"""Steward — Macro Scheduler Cron Wrapper.

Runs the macro planner in ENFORCEMENT mode (--schedule) on a cadence. When a
high-impact event (CPI/FOMC/NFP) is within the auto-schedule window (<36h),
it writes the real one-shot rebalance + stand-down cron jobs to jobs.json and
records them to .steward-macro-scheduled.json.

Silent-when-nothing: if no event is auto-schedulable, prints nothing (no_agent
cron pattern → no delivery). This is the enforcement layer — the machine now
DOES what it reports instead of just printing a plan.

The planner's --schedule already skips events >36h out. So this wrapper is
safe to run every ~30-60min — it only ever schedules imminent events, and it
overwrites the scheduled-state file with the latest enforced plan.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLANNER = os.path.join(
    "/root/vaults/gentech/10-Labs/agent-kit-self-tracking", "steward_macro.py")

# Only run when the treasury has capital (reuse the capital gate).
GATE = os.path.join(HERE, "capital_gate.py")


def main():
    # Capital gate: flat treasury → stay silent, don't schedule repos (nothing to move).
    try:
        chk = subprocess.run(
            [sys.executable, GATE, "--check"], capture_output=True, text=True, timeout=30)
        if "TRUE" not in (chk.stdout or ""):
            sys.exit(0)  # flat / no capital — silent
    except Exception:
        pass

    # Run the planner in --schedule (enforcement) mode.
    proc = subprocess.run(
        [sys.executable, PLANNER, "--schedule"],
        capture_output=True, text=True, timeout=90)

    out = (proc.stdout or "").strip()
    # SILENCE DOCTRINE: only emit when something was actually SCHEDULED (a
    # reposition was written to jobs.json). A plan with only "⏭ monitor only /
    # outside window" lines is noise — don't deliver it every run. Keep the
    # group hearing about a real enforcement, not about quiet monitoring.
    if "✅ WRITTEN rebalance job" in out:
        print(out)  # enforce happened — deliver the confirmation
    # else: silent (nothing was enforced; the next scheduling window will fire)


if __name__ == "__main__":
    main()
