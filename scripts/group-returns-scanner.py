#!/usr/bin/env python3
"""GenTech — Group Returns Scanner (return loop, all groups).

Every group agent gets a symmetric return path so work flows BACK to Gentech
overnight, not just one direction. Standard return contract per group:

  Return folder:  01-HANDOFFS/<group>-to-gentech/     (dated .md files)
  Completion file: 01-HANDOFFS/<group>-completions.md  (item IDs shipped)

Groups: labs, entertainment, finance (Treasury), hq. Forge keeps its legacy
forge-completions.md + from-the-forge.md (already consumed by tick_build_queue).

This scanner reads EVERY return path, extracts shipped item IDs + completion
notes, and emits JSON so the Nightly Build Session + Morning Digest consume
them. It also creates the standard return folders if missing so the group
agents have a known place to write.

Output: JSON to stdout. Exit 0 always (no_agent-friendly).
"""
import json, os, re, sys
from pathlib import Path

VAULT = Path("/root/vaults/gentech")
HANDOFFS = VAULT / "01-HANDOFFS"

# Every group agent + the return surface it should write to.
GROUPS = ["labs", "entertainment", "finance", "hq", "forge"]


def ensure_return_folders():
    """Create standard return folders so group agents have a known place."""
    created = []
    for g in GROUPS:
        folder = HANDOFFS / f"{g}-to-gentech"
        comp = HANDOFFS / f"{g}-completions.md"
        if not folder.exists():
            folder.mkdir(parents=True, exist_ok=True)
            created.append(str(folder.relative_to(VAULT)))
        if not comp.exists():
            comp.write_text(
                f"# {g.title()} Completions — {__import__('datetime').date.today().isoformat()}\n\n"
                f"> {g.title()} writes shipped item IDs here after each session.\n"
                f"> The overnight scanner reads this file and updates the queue.\n\n"
                "---\n\n## Shipped\n\n*None this session.*\n"
            )
            created.append(str(comp.relative_to(VAULT)))
    return created


def parse_completion_ids(text: str) -> list[int]:
    """Extract #<id> tokens from a completion file / return note."""
    return [int(x) for x in re.findall(r"#(\d+)", text)]


def scan_group(g: str) -> dict:
    folder = HANDOFFS / f"{g}-to-gentech"
    comp_file = HANDOFFS / f"{g}-completions.md"
    result = {
        "group": g,
        "shipped_ids": [],
        "notes": [],
        "return_files": [],
    }

    # 1. completion file (authoritative shipped IDs)
    if comp_file.exists():
        text = comp_file.read_text(encoding="utf-8")
        result["shipped_ids"] = parse_completion_ids(text)

    # 2. dated return notes in the folder
    if folder.exists():
        for fn in sorted(folder.glob("*.md")):
            text = fn.read_text(encoding="utf-8")
            result["return_files"].append(fn.name)
            ids = parse_completion_ids(text)
            result["shipped_ids"].extend(ids)
            # grab the first "## Shipped" / "## Completed" note line
            for line in text.splitlines():
                s = line.strip()
                if re.match(r"^(## |### )?(Shipped|Completed|Done|✅)", s) and s not in (
                    "## Shipped", "## Completed"):
                    result["notes"].append(s[:160])

    # dedupe ids, preserve order
    seen = set()
    dedup = []
    for i in result["shipped_ids"]:
        if i not in seen:
            seen.add(i)
            dedup.append(i)
    result["shipped_ids"] = dedup
    return result


def main():
    created = ensure_return_folders()
    reports = [scan_group(g) for g in GROUPS]

    all_shipped = []
    for r in reports:
        all_shipped.extend(r["shipped_ids"])

    out = {
        "scanned_at": __import__("datetime").datetime.now().isoformat(),
        "folders_created": created,
        "total_shipped_ids": len(set(all_shipped)),
        "groups": reports,
        "completions_file": str(HANDOFFS / "gentech-completions.md"),
    }
    json.dump(out, sys.stdout, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
