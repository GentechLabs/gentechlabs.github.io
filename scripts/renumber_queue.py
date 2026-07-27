#!/usr/bin/env python3
"""
Renumber build queue items 1..N so highest ID always equals total count.

Run this after any manual edit to the queue to keep IDs clean.

Usage:
    python3 scripts/renumber_queue.py          # dry run (show changes)
    python3 scripts/renumber_queue.py --apply   # apply changes
"""

import json
import sys
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
QUEUE = VAULT / "scripts" / "build_queue.json"
DRY_RUN = "--apply" not in sys.argv


def renumber_items(queue):
    priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3, 'none': 4}
    active = [i for i in queue["items"] if i["status"] not in ("cancelled", "shipped")]
    inactive = [i for i in queue["items"] if i["status"] in ("cancelled", "shipped")]
    active.sort(key=lambda i: (priority_order.get(i.get('priority', 'medium'), 2), i.get('_orig_id', i['id'])))

    for idx, item in enumerate(active, 1):
        item['_orig_id'] = item['id']
        item['id'] = idx
    for idx, item in enumerate(inactive, len(active) + 1):
        item['_orig_id'] = item['id']
        item['id'] = idx

    queue["items"] = active + inactive
    return queue


def recalc_summary(queue):
    active = [i for i in queue["items"] if i["status"] not in ("cancelled", "shipped")]
    queue["summary"]["total"] = len(queue["items"])
    queue["summary"]["shipped"] = sum(1 for i in queue["items"] if i["status"] == "shipped")
    queue["summary"]["in_progress"] = sum(1 for i in queue["items"] if i["status"] == "in_progress")
    queue["summary"]["pending"] = sum(1 for i in queue["items"] if i["status"] == "pending")
    queue["summary"]["blocked"] = 0
    queue["summary"]["needs_jordan"] = sum(1 for i in active if i.get("needs_jordan", False))
    queue["gate_summary"]["human_gated"] = sum(1 for i in active if i.get("human_gated", False))
    queue["gate_summary"]["decision_gated"] = sum(1 for i in active if i.get("gate_type") == "decision")
    queue["gate_summary"]["autonomous"] = 0
    return queue


def main():
    queue = json.loads(QUEUE.read_text())
    old_ids = {i['id']: i['name'][:50] for i in queue['items']}

    queue = renumber_items(queue)
    queue = recalc_summary(queue)
    queue['version'] += 1
    queue['updated'] = date.today().isoformat()

    print(f"Version: {queue['version']}")
    print(f"Total: {queue['summary']['total']} items")
    print(f"Active: {sum(1 for i in queue['items'] if i['status'] not in ('cancelled','shipped'))}")
    print()
    print("ID changes:")
    for i in queue['items']:
        old = i['_orig_id']
        new = i['id']
        if old != new:
            print(f"  #{old} → #{new}  {i['name'][:55]}")
        else:
            print(f"  #{new} (unchanged)  {i['name'][:55]}")

    if DRY_RUN:
        print(f"\nDRY RUN — would save v{queue['version']}")
        return

    QUEUE.write_text(json.dumps(queue, indent=2) + "\n")
    print(f"\nSaved v{queue['version']} — highest ID is now #{queue['items'][-1]['id']}")


if __name__ == "__main__":
    main()
