#!/usr/bin/env python3
"""
GenTech V4 — Nightly Maintenance (Midnight ET)
Runs at 4:00 UTC (midnight ET), no_agent mode.

1. Stash pending changes → git pull → git push
2. Run brain backup script
3. Check build queue → save overnight report
4. Clean up stale agent-brain notes older than 14 days
5. Print report to stdout (captured by cron delivery)
"""

import json, os, subprocess, sys, shutil
from datetime import datetime, timezone, timedelta

VAULT_DIR = "/root/vaults/gentech"
BRAIN_DIR = f"{VAULT_DIR}/11-Mess Hall/agent-brain"
QUEUE_PATH = f"{VAULT_DIR}/scripts/build_queue.json"
REMOTE = "vault"
BRANCH = "main"

now = datetime.now(timezone.utc)
date_str = now.strftime("%Y-%m-%d")

def run(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip() or r.stderr.strip()
        return out, r.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1
    except Exception as e:
        return str(e), -1

def main():
    report = []
    report.append(f"# Nightly Maintenance — {now.strftime('%Y-%m-%d %H:%M UTC')}\n")

    # ── 1. Git sync ──────────────────────────────────────
    report.append("## Git Sync\n")

    # Stash any local changes first
    stash_out, stash_rc = run(f"cd {VAULT_DIR} && git stash push -m 'nightly-stash-{date_str}' 2>&1 | tail -3")
    had_stash = "Saved working directory" in stash_out

    # Pull with explicit remote/branch
    pull_out, pull_rc = run(f"cd {VAULT_DIR} && git pull --rebase {REMOTE} {BRANCH} 2>&1 | tail -5")
    report.append(f"**Pull:** {pull_out}\n")

    # Pop stash if we stashed
    if had_stash:
        pop_out, pop_rc = run(f"cd {VAULT_DIR} && git stash pop 2>&1 | tail -3")
        report.append(f"**Stash restored:** {pop_out}\n")

    # Add, commit, push any new changes
    status_out, _ = run(f"cd {VAULT_DIR} && git status --short")
    changed = [l for l in status_out.split('\n') if l.strip()]
    if changed:
        add_out, _ = run(f"cd {VAULT_DIR} && git add -A 2>&1 | tail -2")
        commit_out, commit_rc = run(
            f"cd {VAULT_DIR} && git commit -m 'nightly sync {date_str}' 2>&1 | tail -3"
        )
        push_out, push_rc = run(f"cd {VAULT_DIR} && git push {REMOTE} {BRANCH} 2>&1 | tail -3")
        report.append(f"**Changed files:** {len(changed)}\n**Push:** {push_out}\n")
    else:
        report.append("**Clean** — no changes to commit.\n")

    # ── 2. Brain backup ─────────────────────────────────
    report.append("## Brain Backup\n")
    backup_script = f"{VAULT_DIR}/scripts/backup-brain.py"
    if os.path.exists(backup_script):
        bk_out, bk_rc = run(f"python3 {backup_script} 2>&1 | tail -5")
        report.append(f"**Backup:** {bk_out}\n" if bk_rc == 0 else f"**Backup FAILED:** {bk_out}\n")
    else:
        report.append("**Backup:** no backup-brain.py found (skipped)\n")

    # ── 3. Build queue overview ──────────────────────────
    report.append("## Build Queue Overnight\n")
    if os.path.exists(QUEUE_PATH):
        try:
            with open(QUEUE_PATH) as f:
                q = json.load(f)

            pending_gentech = [
                i for i in q["items"]
                if i["status"] == "pending" and i.get("assigned_to") == "gentech"
            ]
            pending_jordan = [
                i for i in q["items"]
                if i["status"] == "pending" and i.get("assigned_to") == "jordan"
            ]
            in_progress = [i for i in q["items"] if i["status"] == "in_progress"]
            total = len(q["items"])

            report.append(f"- **Total items:** {total}\n")
            report.append(f"- **⏳ In progress:** {len(in_progress)}\n")
            report.append(f"- **⏸️  Pending (gentech):** {len(pending_gentech)}\n")
            report.append(f"- **👑 Pending (Jordan):** {len(pending_jordan)}\n")

            if in_progress:
                report.append("\n**Active:**\n")
                for i in in_progress:
                    report.append(f"  - #{i['id']} {i['name']} → {i.get('assigned_to','?')}\n")

            if pending_gentech:
                report.append("\n**Ready for gentech:**\n")
                for i in sorted(pending_gentech, key=lambda x: x.get("id", 999)):
                    report.append(f"  - #{i['id']} [{i.get('difficulty','?')}] {i['name']}\n")

        except Exception as e:
            report.append(f"**ERROR reading queue:** {e}\n")
    else:
        report.append("No build_queue.json found.\n")

    # ── 4. Clean old brain notes (＞14 days) ─────────────
    report.append("\n## Brain Note Cleanup\n")
    cutoff = now - timedelta(days=14)
    removed = 0
    if os.path.isdir(BRAIN_DIR):
        for day_dir in os.listdir(BRAIN_DIR):
            day_path = os.path.join(BRAIN_DIR, day_dir)
            if not os.path.isdir(day_path):
                continue
            try:
                day_date = datetime.strptime(day_dir, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if day_date < cutoff:
                    shutil.rmtree(day_path)
                    removed += 1
            except ValueError:
                continue
    report.append(f"**Cleaned:** {removed} old brain note directories\n" if removed else "**Clean:** no old notes to remove\n")

    # ── 5. Print report ──────────────────────────────────
    sys.stdout.writelines(report)

    # Save to agent-brain for morning digest to pick up
    today_dir = f"{BRAIN_DIR}/{date_str}"
    os.makedirs(today_dir, exist_ok=True)
    report_path = f"{today_dir}/000-nightly-maintenance.md"
    with open(report_path, "w") as f:
        f.writelines(report)

if __name__ == "__main__":
    main()
