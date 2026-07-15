#!/usr/bin/env python3
"""
GenTech V4 — Brain Backup
Saves a compressed snapshot of the agent-brain directory.
Runs as part of nightly maintenance, or standalone.
"""

import os, subprocess, sys
from datetime import datetime, timezone

VAULT_DIR = "/root/vaults/gentech"
BRAIN_DIR = f"{VAULT_DIR}/11-Mess Hall/agent-brain"
BACKUP_DIR = f"{VAULT_DIR}/00-HQ/brain-snapshots"

def run(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() or r.stderr.strip(), r.returncode
    except Exception as e:
        return str(e), -1

def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%d")
    out_path = f"{BACKUP_DIR}/{stamp}.md"

    # Gather brain notes
    notes = []
    if os.path.isdir(BRAIN_DIR):
        for day in sorted(os.listdir(BRAIN_DIR)):
            day_path = os.path.join(BRAIN_DIR, day)
            if not os.path.isdir(day_path):
                continue
            for note in sorted(os.listdir(day_path)):
                if note.endswith(".md"):
                    path = os.path.join(day_path, note)
                    with open(path) as f:
                        content = f.read()
                    notes.append(f"## {day}/{note}\n\n{content}\n\n---\n")

    with open(out_path, "w") as f:
        f.write(f"# Brain Snapshot — {stamp}\n\n")
        f.write(f"**{len(notes)} notes**\n\n---\n\n")
        f.writelines(notes)

    # Sync to git
    run(f"cd {VAULT_DIR} && git add {BACKUP_DIR} && git commit -m 'brain snapshot {stamp}' 2>&1 && git push vault main 2>&1 | tail -2")
    print(f"✅ Brain snapshot saved: {out_path} ({len(notes)} notes)")

if __name__ == "__main__":
    main()
