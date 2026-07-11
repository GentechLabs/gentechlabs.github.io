#!/usr/bin/env python3
"""
Morning To-Do List — Jordan's Action Items + Overnight Report
Script-only mode (no LLM) to avoid quota limits.
V4 update: reads overnight brain notes, build queue, and considerations.
"""

import json
import os
import subprocess
import sys
from datetime import datetime

# Quiet hours: 8 AM - 10 PM ET
def is_quiet_hours():
    now = datetime.utcnow()
    et_hour = (now.hour - 4) % 24
    return et_hour < 8 or et_hour >= 22


def send_telegram_message(message, chat_id="-1003863540828"):
    """Send message via Telegram"""
    try:
        subprocess.run([
            "curl", "-X", "POST",
            "http://localhost:8080/api/telegram/send",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            })
        ], check=True, capture_output=True, timeout=15)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}", file=sys.stderr)


def read_considerations():
    """Read unchecked action items from considerations.md"""
    path = "/root/vaults/gentech/11-Mess Hall/considerations.md"
    if not os.path.exists(path):
        return []
    items = []
    with open(path) as f:
        for line in f:
            s = line.strip()
            if s.startswith("- [ ]"):
                items.append(s[6:].strip())
    return items


def read_build_queue_summary():
    """Read build queue for awaiting-Jordan tasks"""
    path = "/root/vaults/gentech/scripts/build_queue.json"
    if not os.path.exists(path):
        return []
    with open(path) as f:
        q = json.load(f)
    jordan_tasks = []
    for i in q["items"]:
        if i.get("assigned_to") == "jordan" and i["status"] == "pending":
            jordan_tasks.append(i)
    # Sort easy first
    diff_order = {"easy": 0, "medium": 1, "hard": 2}
    jordan_tasks.sort(key=lambda x: (diff_order.get(x.get("difficulty", "medium"), 1), x.get("id", 999)))
    return jordan_tasks


def read_overnight_report():
    """Read the latest overnight maintenance report from agent-brain"""
    brain_dir = "/root/vaults/gentech/11-Mess Hall/agent-brain"
    today = datetime.utcnow().strftime("%Y-%m-%d")
    today_dir = f"{brain_dir}/{today}"
    report_path = f"{today_dir}/000-nightly-maintenance.md"
    if os.path.exists(report_path):
        with open(report_path) as f:
            content = f.read()
        # Extract just the build queue section
        sections = content.split("## ")
        for s in sections:
            if s.startswith("Build Queue"):
                lines = s.split("\n")[:20]
                return "\n".join(lines)
    return None


def read_git_overnight():
    """Check what was committed overnight"""
    try:
        r = subprocess.run(
            "cd /root/vaults/gentech && git log --since='4 hours ago' --oneline --no-decorate 2>&1 | head -10",
            shell=True, capture_output=True, text=True, timeout=10
        )
        output = r.stdout.strip()
        if output:
            return output.split("\n")
        return None
    except:
        return None


def main():
    if is_quiet_hours():
        print("Quiet hours — skipping")
        return

    now = datetime.now()
    date_str = now.strftime("%B %d, %Y")

    # Build message
    msg = f"📋 **Morning Digest — {date_str}**\n\n"

    # Overnight activity
    commits = read_git_overnight()
    if commits:
        msg += "**🌙 Overnight Activity**\n"
        for c in commits[:5]:
            msg += f"  `{c}`\n"
        msg += "\n"

    # Build queue — awaiting Jordan
    jordan_tasks = read_build_queue_summary()
    if jordan_tasks:
        msg += f"**👑 Awaiting Jordan ({len(jordan_tasks)})**\n"
        for t in jordan_tasks:
            diff = t.get("difficulty", "?")
            icon = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(diff, "⚪")
            msg += f"  {icon} #{t['id']} {t['name']}\n"
        msg += "\n"

    # Considerations
    items = read_considerations()
    if items:
        msg += "**📝 Open Items**\n"
        for item in items[:5]:
            msg += f"  • {item}\n"
        msg += "\n"

    # Quick tip
    msg += "💡 Tip: Reply `handoff` for a full status check"

    send_telegram_message(msg)
    print("Morning digest delivered")


if __name__ == "__main__":
    main()