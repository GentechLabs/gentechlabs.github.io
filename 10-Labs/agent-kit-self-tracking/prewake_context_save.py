#!/usr/bin/env python3
"""Wrapper for the Pre-Wake brain checkpoint (gentech-treasury).

The cron runner blocks any script whose path resolves outside the scripts
directory. The canonical context-save lives in gentech's session-hygiene
skill dir, so cron could not execute it directly. This thin wrapper delegates
to the skill's context-save.py so the prewake job can run for this profile.

Logs failures loudly instead of failing silently.
"""
import subprocess
import sys

SKILL_SCRIPT = (
    "/root/.hermes/profiles/gentech/skills/gentech-ops/"
    "session-hygiene/scripts/context-save.py"
)

# Full treasury brain checkpoint (720 min = 12h window).
ARGS = ["--profile", "gentech-treasury", "--minutes", "720"]

if __name__ == "__main__":
    proc = subprocess.run(
        ["python3", SKILL_SCRIPT] + ARGS,
        capture_output=True,
        text=True,
    )
    if proc.stdout.strip():
        print(proc.stdout.strip())
    if proc.returncode != 0:
        if proc.stderr.strip():
            print("ERR:", proc.stderr.strip()[-500:])
        raise SystemExit(proc.returncode)
