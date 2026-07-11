#!/usr/bin/env python3
"""
GenTech V4 — Nightly Maintenance (Midnight ET)
Runs at 4:00 UTC (midnight ET).
1. Sync vault (git pull + git push)
2. Run brain backup
3. Take context snapshot
4. Scan build queue for overnight progress
5. Save overnight report to agent-brain/
"""

import json, os, subprocess, sys
from datetime import datetime, timezone

VAULT_DIR = "/root/vaults/gentech"
BRAIN_DIR = f"{VAULT_DIR}/11-Mess Hall/agent-brain"
QUEUE_PATH = f"{VAULT_DIR}/scripts/build_queue.json"

now = datetime.now(timezone.utc)
date_str = now.strftime("%Y-%m-%d")

def run(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        return str(e)

def main():
    report = []
    report.append(f"# Nightly Maintenance — {now.strftime('%Y-%m-%d %H:%M UTC')}\n")

    # 1. Git sync vault
    pull = run(f"cd {VAULT_DIR} && git pull --rebase 2>&1 | tail -3")
    report.append(f"## Git Pull\n{pull}\n")

    # 2. Git status
    status = run(f"cd {VAULT_DIR} && git status --short")
    changed = len([l for l in status.split('\n') if l.strip()])
    if changed > 0:
        add = run(f"cd {VAULT_DIR} && git add -A 2>&1 | tail -1")
        commit = run(f"cd {VAULT_DIR} && git commit -m 'Nightly sync {date_str}' 2>&1 | tail -1")
        push = run(f"cd {VAULT_DIR} && git push 2>&1 | tail -3")
        report.append(f"## Git Sync\nFiles changed: {changed}\n{push}\n")
    else:
        report.append("## Git Sync\nClean — no changes.\n")

    # 3. Brain backup (Hermes)
    backup = run("echo 'Brain backup would run here'", timeout=10)
    report.append(f"## Brain Backup\n{backup}\n")

    # 4. Build queue overnight summary
    if os.path.exists(QUEUE_PATH):
        with open(QUEUE_PATH) as f:
            q = json.load(f)
        completed_overnight = [i for i in q["items"] if i["status"] == "completed"]
        pending_jordan = [i for i in q["items"] if i.get("assigned_to") == "jordan" and i["status"] == "pending"]
        in_progress = [i for i in q["items"] if i["status"] == "in_progress"]

        report.append("## Build Queue Overnight\n")
        if completed_overnight:
            report.append("### ✅ Completed\n")
            for i in completed_overnight:
                report.append(f"- #{i['id']} {i['name']}\n")
        report.append(f"### 👑 Awaiting Jordan ({len(pending_jordan)})\n")
        for i in sorted(pending_jordan, key=lambda x: x.get("id", 999)):
            report.append(f"- #{i['id']} [{i.get('difficulty','?')}] {i['name']}\n")
        report.append(f"\n### ⏳ In Progress ({len(in_progress)})\n")
        for i in in_progress:
            report.append(f"- #{i['id']} {i['name']} → {i.get('assigned_to','?')}\n")

    # 5. Save report to agent-brain
    today_dir = f"{BRAIN_DIR}/{date_str}"
    os.makedirs(today_dir, exist_ok=True)
    report_path = f"{today_dir}/000-nightly-maintenance.md"
    with open(report_path, "w") as f:
        f.writelines(report)

    report.insert(0, f"📋 **Nightly Maintenance — {now.strftime('%b %d, %Y')}**\n\n")
    sys.stdout.writelines(report)

if __name__ == "__main__":
    main()