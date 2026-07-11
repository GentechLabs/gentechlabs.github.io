#!/usr/bin/env python3
"""
GenTech V4 — Build Queue Tick
Runs autonomously every 30 min via cron.
1. Check build_queue.json for available tasks
2. Pick next available (Easy first, then priority)
3. Start working, checkpoint, brain note on block
4. Move to next task
"""

import json
import os
import sys
from datetime import datetime, timezone

QUEUE_PATH = "/root/vaults/gentech/scripts/build_queue.json"
BRAIN_DIR = "/root/vaults/gentech/11-Mess Hall/agent-brain"
AGENT = os.environ.get("AGENT", "gentech")

DIFFICULTY = {"easy": 0, "medium": 1, "hard": 2}
PRIORITY = {"urgent": 0, "high": 1, "medium": 2, "low": 3}

def load_queue():
    with open(QUEUE_PATH) as f:
        return json.load(f)

def save_queue(q):
    q["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    with open(QUEUE_PATH, "w") as f:
        json.dump(q, f, indent=2)

def find_next_task(q):
    """Find the next available task for this agent. Easy first."""
    available = [
        i for i in q["items"]
        if i["status"] == "pending" and i.get("assigned_to") in (AGENT, "auto")
    ]
    if not available:
        return None
    available.sort(key=lambda x: (
        DIFFICULTY.get(x.get("difficulty", "medium"), 1),
        PRIORITY.get(x.get("priority", "low"), 99),
        x.get("id", 999)
    ))
    return available[0]

def create_brain_note(task_id, name, what_done, stopping_point, next_steps, state):
    """Create a brain note at a stopping point."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    dir_path = os.path.join(BRAIN_DIR, today)
    os.makedirs(dir_path, exist_ok=True)

    seq = len([f for f in os.listdir(dir_path) if f.endswith(".md")]) + 1
    note = f"""# Brain Note — {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
# Task: #{task_id} {name}

## What was done
{what_done}

## Stopping point
{stopping_point}

## Next steps when resumed
{chr(10).join(f"{j}. {s}" for j, s in enumerate(next_steps, 1))}

## State
{chr(10).join(f"- {k}: {v}" for k, v in state.items())}
"""
    path = os.path.join(dir_path, f"{seq:03d}-task{task_id}-{name[:30].lower().replace(' ', '-')}.md")
    with open(path, "w") as f:
        f.write(note)
    print(f"📝 Brain note saved: {path}")
    return path

def summary(q):
    """Print a summary of queue state."""
    counts = {"pending": 0, "in_progress": 0, "blocked": 0, "completed": 0}
    waiting_jordan = 0
    for i in q["items"]:
        s = i["status"]
        if s in counts:
            counts[s] += 1
        if i.get("assigned_to") == "jordan" and i["status"] in ("pending", "blocked"):
            waiting_jordan += 1

    print(f"\n📋 Build Queue — {len(q['items'])} items")
    print(f"  ✅ Completed: {counts.get('completed', 0)}")
    print(f"  ⏳ In progress: {counts.get('in_progress', 0)}")
    print(f"  ⏸️  Pending: {counts.get('pending', 0)}")
    print(f"  🚫 Blocked: {counts.get('blocked', 0)}")
    print(f"  👑 Awaiting Jordan: {waiting_jordan}")

if __name__ == "__main__":
    q = load_queue()
    summary(q)

    next_task = find_next_task(q)
    if next_task:
        print(f"\n▶️  Next task: #{next_task['id']} [{next_task['difficulty']}] {next_task['name']}")
    else:
        print(f"\n💤 No available tasks for {AGENT}. All assigned or in progress.")

    save_queue(q)