#!/usr/bin/env python3
"""
Master Digest Helper — pattern recognition & staleness checks for daily CEO digest.
Run this to quickly compute handoff ages, coordination board health, and stale items.
"""

from datetime import datetime, timezone
from pathlib import Path
import re

VAULT = Path("/root/vaults/gentech")

def parse_handoff_date(filename):
    """Extract YYYY-MM-DD from handoff filename and return date object."""
    match = re.match(r"(\d{4}-\d{2}-\d{2})", filename.name)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d").date()
    return None

def get_handoff_ages():
    """Return list of active handoffs with age in days."""
    handoffs_dir = VAULT / "09-Green Room" / "active-handoffs"
    if not handoffs_dir.exists():
        return []
    items = []
    for f in sorted(handoffs_dir.glob("*.md")):
        handoff_date = parse_handoff_date(f)
        if handoff_date:
            age = (datetime.now(timezone.utc).date() - handoff_date).days
            items.append({"file": f.name, "age_days": age, "date": handoff_date})
    return items

def check_agent_coordination_board():
    """Read agent coordination board and return status dict."""
    board = VAULT / "11-Mess Hall" / "agent-coordination-board.md"
    if not board.exists():
        return {"error": "board not found"}
    content = board.read_text()
    # Simple check: look for OFFLINE statuses
    offline_agents = []
    for line in content.splitlines():
        if "| OFFLINE" in line:
            # Extract agent name from table row pattern: | Agent | ... | OFFLINE |
            parts = [p.strip() for p in line.split("|")]
            if len(parts) > 3:
                offline_agents.append(parts[1])
    return {"offline_agents": offline_agents, "raw_lines": len(content.splitlines())}

def check_master_todo_staleness():
    """Return (last_updated_date, days_ago) for master-todo.md."""
    todo = VAULT / "09-Green Room" / "master-todo.md"
    if not todo.exists():
        return None
    stat = todo.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).date()
    days_ago = (datetime.now(timezone.utc).date() - mtime).days
    # Also try to parse frontmatter date
    content = todo.read_text()
    date_match = re.search(r"^# Master To-Do — (\d{4}-\d{2}-\d{2})", content, re.MULTILINE)
    if date_match:
        try:
            fmt_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
            if fmt_date != mtime:
                mtime = fmt_date
                days_ago = (datetime.now(timezone.utc).date() - mtime).days
        except ValueError:
            pass
    return {"last_updated": str(mtime), "days_ago": days_ago}

def count_active_hackathons():
    """Count active hackathon files and list them."""
    active_dir = VAULT / "02-Labs" / "Hackathons" / "Active"
    if not active_dir.exists():
        return []
    files = list(active_dir.glob("*.md"))
    # Filter to top-level only (not nested Anchor.toml etc)
    top_level = [f.name for f in files if f.parent == active_dir and f.suffix == ".md"]
    return top_level

def get_recent_mess_hall_files(days=1):
    """List Mess Hall files modified in last N days."""
    mh = VAULT / "11-Mess Hall"
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent = []
    for f in mh.rglob("*.md"):
        if f.stat().st_mtime > cutoff.timestamp():
            recent.append(f.relative_to(VAULT))
    return sorted(recent)

def print_digest_readout():
    print("=" * 60)
    print("MASTER DIGEST HELPER — Org Health Snapshot")
    print("=" * 60)

    print("\n📋 HANDOFF AGES (active-handoffs/):")
    handoffs = get_handoff_ages()
    if handoffs:
        for h in handoffs:
            emoji = "🚨" if h["age_days"] >= 13 else "🟡" if h["age_days"] >= 5 else "🟢"
            print(f"  {emoji} {h['file']} — {h['age_days']} days old")
    else:
        print("  ✅ No active handoffs")

    print("\n👥 AGENT COORDINATION BOARD:")
    board = check_agent_coordination_board()
    if "error" in board:
        print(f"  ❌ {board['error']}")
    else:
        if board["offline_agents"]:
            print(f"  🚨 OFFLINE: {', '.join(board['offline_agents'])}")
        else:
            print("  ✅ All agents ONLINE (or board not showing OFFLINE)")

    print("\n📝 MASTER TODO STALENESS:")
    todo = check_master_todo_staleness()
    if todo:
        emoji = "⚠️" if todo["days_ago"] >= 5 else "🟢"
        print(f"  {emoji} Last updated: {todo['last_updated']} ({todo['days_ago']} days ago)")
    else:
        print("  ❌ master-todo.md not found")

    print("\n🏆 ACTIVE HACKATHONS:")
    active = count_active_hackathons()
    if active:
        for h in active:
            print(f"  🔴 {h}")
    else:
        print("  ⚠️ No active hackathon files found")

    print("\n📅 RECENT MESS HALL (last 24h):")
    recent = get_recent_mess_hall_files(days=1)
    if recent:
        for r in recent[-5:]:  # last 5
            print(f"  • {r}")
    else:
        print("  ⚠️ No Mess Hall activity in last 24h")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    from datetime import timedelta
    print_digest_readout()
