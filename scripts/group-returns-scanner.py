#!/usr/bin/env python3
"""GenTech — Group Returns Scanner (return loop, V4 full mesh).

V4 is a full mesh: ANY group can hand off to ANY other group for approval,
context, or handoff — not just back to Gentech. This scanner reads EVERY
<from>-to-<to>/ folder in 01-HANDOFFS/ (peer handoffs included) plus every
<group>-completions.md, extracts shipped item IDs + notes, and emits JSON so
the Nightly Build Session + Morning Digest consume them.

  Return folder:   01-HANDOFFS/<from>-to-<to>/     (dated .md files)
  Completion file: 01-HANDOFFS/<group>-completions.md  (item IDs shipped)

Groups: labs, entertainment, finance (Treasury), hq, forge, gizmo. Forge keeps
its legacy forge-completions.md + from-the-forge.md (already consumed by
tick_build_queue).

Output: JSON to stdout. Exit 0 always (no_agent-friendly).
"""
import json, os, re, sys
from pathlib import Path

VAULT = Path("/root/vaults/gentech")
HANDOFFS = VAULT / "01-HANDOFFS"

# Every group agent + the return surface it should write to.
GROUPS = ["labs", "entertainment", "finance", "hq", "forge", "gizmo"]

# Folder name pattern for a peer handoff: <from>-to-<to>/
MESH_RE = re.compile(r"^([a-z]+)-to-([a-z]+)$")


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


def scan_folder(folder: Path, label: str) -> dict:
    """Scan one <from>-to-<to>/ folder for dated return notes."""
    result = {"label": label, "shipped_ids": [], "notes": [], "return_files": []}
    if not folder.exists():
        return result
    for fn in sorted(folder.glob("*.md")):
        text = fn.read_text(encoding="utf-8")
        result["return_files"].append(fn.name)
        result["shipped_ids"].extend(parse_completion_ids(text))
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


def scan_group(g: str) -> dict:
    """Scan a group's completions file + its <g>-to-gentech/ return folder."""
    comp_file = HANDOFFS / f"{g}-completions.md"
    result = {
        "group": g,
        "shipped_ids": [],
        "notes": [],
        "return_files": [],
    }
    if comp_file.exists():
        text = comp_file.read_text(encoding="utf-8")
        result["shipped_ids"] = parse_completion_ids(text)
    folder = HANDOFFS / f"{g}-to-gentech"
    sub = scan_folder(folder, f"{g}-to-gentech")
    result["shipped_ids"].extend(sub["shipped_ids"])
    result["notes"].extend(sub["notes"])
    result["return_files"].extend(sub["return_files"])
    # dedupe
    seen = set()
    dedup = []
    for i in result["shipped_ids"]:
        if i not in seen:
            seen.add(i)
            dedup.append(i)
    result["shipped_ids"] = dedup
    return result


def scan_mesh() -> list[dict]:
    """Scan every peer <from>-to-<to>/ folder (excluding -to-gentech, handled
    in scan_group) so peer handoffs are consumed too."""
    mesh = []
    if not HANDOFFS.exists():
        return mesh
    for folder in sorted(HANDOFFS.iterdir()):
        if not folder.is_dir():
            continue
        m = MESH_RE.match(folder.name)
        if not m:
            continue
        frm, to = m.group(1), m.group(2)
        if to == "gentech":
            continue  # handled by scan_group
        sub = scan_folder(folder, folder.name)
        if sub["return_files"] or sub["shipped_ids"]:
            sub["from"] = frm
            sub["to"] = to
            mesh.append(sub)
    return mesh


def main():
    created = ensure_return_folders()
    reports = [scan_group(g) for g in GROUPS]
    mesh = scan_mesh()

    all_shipped = []
    for r in reports:
        all_shipped.extend(r["shipped_ids"])
    for m in mesh:
        all_shipped.extend(m["shipped_ids"])

    out = {
        "scanned_at": __import__("datetime").datetime.now().isoformat(),
        "folders_created": created,
        "total_shipped_ids": len(set(all_shipped)),
        "groups": reports,
        "mesh_handoffs": mesh,
        "completions_file": str(HANDOFFS / "gentech-completions.md"),
    }
    json.dump(out, sys.stdout, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
