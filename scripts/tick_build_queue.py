#!/usr/bin/env python3
"""
Build Queue Tick Script — reads forge-completions.md and updates build_queue.json.

Forge writes completed item IDs to 01-HANDOFFS/forge-completions.md.
This script reads that file, marks items as shipped in build_queue.json,
and writes a fresh for-the-forge.md with the current queue.

Usage:
    python3 scripts/tick_build_queue.py          # dry run (no changes)
    python3 scripts/tick_build_queue.py --apply   # apply changes
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
QUEUE = VAULT / "scripts" / "build_queue.json"
COMPLETIONS = VAULT / "01-HANDOFFS" / "forge-completions.md"
FOR_FORGE = VAULT / "01-HANDOFFS" / "for-the-forge.md"
FROM_FORGE = VAULT / "01-HANDOFFS" / "from-the-forge.md"

DRY_RUN = "--apply" not in sys.argv


def parse_completions(path: Path) -> list[int]:
    """Extract shipped item IDs from forge-completions.md."""
    if not path.exists():
        return []
    text = path.read_text()
    ids = re.findall(r'\*\*#(\d+)\s', text)
    return [int(i) for i in ids]


def load_queue(path: Path) -> dict:
    return json.loads(path.read_text())


def save_queue(path: Path, data: dict):
    path.write_text(json.dumps(data, indent=2) + "\n")


def write_for_forge(queue: dict, shipped: list[int]):
    """Write a fresh for-the-forge.md with the current queue."""
    today = date.today().isoformat()
    active = [i for i in queue["items"] if i["status"] not in ("cancelled", "shipped")]

    lines = [f"## For Forge — {today}\n"]
    lines.append("### Priority items\n")

    # Group by priority
    for p in ("urgent", "high", "medium", "low"):
        items = [i for i in active if i.get("priority") == p]
        if not items:
            continue
        lines.append(f"**{p.upper()}:**\n")
        for i in items:
            lines.append(f"- **#{i['id']}** {i['name']} — {i.get('detail','')[:120]}")
        lines.append("")

    lines.append("### Recently shipped\n")
    for sid in shipped:
        lines.append(f"- **#{sid}** — marked shipped in queue")
    if not shipped:
        lines.append("- None this cycle.")

    lines.append(f"\n### Full queue ({len(active)} active items)")
    lines.append(f"See `scripts/build_queue.json` for details.\n")

    return "\n".join(lines)


def main():
    shipped_ids = parse_completions(COMPLETIONS)
    queue = load_queue(QUEUE)

    if not shipped_ids:
        print("No new completions found in forge-completions.md")
        if not DRY_RUN:
            print("Nothing to do.")
        return

    print(f"Found {len(shipped_ids)} shipped IDs: {shipped_ids}")

    updated = []
    for item in queue["items"]:
        if item["id"] in shipped_ids and item["status"] != "shipped":
            item["status"] = "shipped"
            updated.append(item["id"])
            print(f"  #{item['id']} {item['name']} → shipped")

    if not updated:
        print("No items needed updating (already shipped or not found).")
        return

    # Recalculate summary
    active = [i for i in queue["items"] if i["status"] != "cancelled"]
    queue["summary"]["total"] = len(queue["items"])
    queue["summary"]["shipped"] = sum(1 for i in queue["items"] if i["status"] == "shipped")
    queue["summary"]["in_progress"] = sum(1 for i in queue["items"] if i["status"] == "in_progress")
    queue["summary"]["pending"] = sum(1 for i in queue["items"] if i["status"] == "pending")
    queue["summary"]["needs_jordan"] = sum(1 for i in active if i.get("needs_jordan", False))
    queue["gate_summary"]["human_gated"] = sum(1 for i in active if i.get("human_gated", False))
    queue["gate_summary"]["decision_gated"] = sum(1 for i in active if i.get("gate_type") == "decision")

    queue["version"] += 1
    queue["updated"] = date.today().isoformat()

    if DRY_RUN:
        print(f"\nDRY RUN — would save queue v{queue['version']} and write for-the-forge.md")
        return

    save_queue(QUEUE, queue)
    print(f"\nQueue saved: v{queue['version']}, {queue['summary']['shipped']} shipped")

    # Write fresh for-the-forge.md
    forge_text = write_for_forge(queue, updated)
    FOR_FORGE.write_text(forge_text)
    print(f"Wrote for-the-forge.md ({len(updated)} shipped items)")

    # Clear forge-completions.md (keep header)
    COMPLETIONS.write_text(
        f"# Forge Completions — {date.today().isoformat()}\n\n"
        "> Forge writes completed item IDs here after each work session.\n"
        "> The build queue tick script reads this file and auto-updates the queue.\n\n"
        "---\n\n## Shipped\n\n*None this session.*\n"
    )
    print("Cleared forge-completions.md for next cycle")


if __name__ == "__main__":
    main()
