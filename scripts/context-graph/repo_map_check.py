#!/usr/bin/env python3
"""
repo_map_check.py — Staleness-aware refresh for the repo-context graph.

Borrowed primitive #2 from Graft: before acting on a repo that has a saved map,
run a cheap *structural* freshness check (file content-hashes vs the map's
fingerprint). If anything drifted — uncommitted edits included — fail loudly
(exit 1) so the agent regenerates the map instead of acting on a stale one.

Pure stdlib.

USAGE:
    python3 repo_map_check.py /path/to/repo            # exit 0 = fresh, 1 = drifted
    python3 repo_map_check.py /path/to/repo --rebuild  # auto-regen if drifted
    python3 repo_map_check.py /path/to/repo --out .repo-map

EXIT CODES:
    0  fresh — map matches current filesystem
    1  drifted — map is stale (list the changed files); use --rebuild to regen
    2  no fingerprint/map found — build one first
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from repo_map import build_map, compute_fingerprint, JUNK_DIRS, _is_code_file


def _current_fingerprint(repo_root: str) -> dict:
    """Compute a fresh fingerprint of the repo's code files right now."""
    repo_root = os.path.abspath(repo_root)
    files = {}
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in JUNK_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if _is_code_file(full):
                rel = os.path.relpath(full, repo_root)
                try:
                    with open(full, "r", encoding="utf-8", errors="replace") as f:
                        files[rel] = _hash(f.read())
                except OSError:
                    files[rel] = "unreadable"
    return files


def _hash(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def check(repo_root: str, out: str = ".repo-map") -> tuple[int, list[str], list[str]]:
    """Return (status, added, changed_or_removed) — status 0=fresh,1=drifted,2=missing."""
    repo_root = os.path.abspath(repo_root)
    fp_path = os.path.join(repo_root, out, "fingerprint.json")
    if not os.path.exists(fp_path):
        return 2, [], ["no fingerprint.json — run repo_map.py first"]

    with open(fp_path, "r", encoding="utf-8") as f:
        saved = json.load(f)
    saved_files = saved.get("files", {})

    current = _current_fingerprint(repo_root)

    added = sorted(set(current) - set(saved_files))
    changed = []
    removed = []
    for rel in saved_files:
        if rel not in current:
            removed.append(rel)
        elif current[rel] != saved_files[rel]:
            changed.append(rel)

    drifted = added or changed or removed
    return (1 if drifted else 0), added, changed + removed


def main() -> int:
    ap = argparse.ArgumentParser(description="Check repo-context graph freshness.")
    ap.add_argument("repo", help="Path to the repository")
    ap.add_argument("--rebuild", action="store_true", help="Auto-regenerate the map if drifted")
    ap.add_argument("--out", default=".repo-map", help="Output dir (default: .repo-map)")
    args = ap.parse_args()

    if not os.path.isdir(args.repo):
        print(f"error: not a directory: {args.repo}", file=sys.stderr)
        return 2

    status, added, changed = check(args.repo, args.out)

    if status == 2:
        print(f"[repo_map_check] no map found in {args.repo}/{args.out}")
        print(f"[repo_map_check] run: python3 repo_map.py {args.repo}")
        return 2

    if status == 0:
        print(f"[repo_map_check] FRESH — {len(added)} added, {len(changed)} changed/removed")
        return 0

    # drifted
    print(f"[repo_map_check] DRIFTED — map is stale ({len(added)} added, {len(changed)} changed/removed):")
    for a in added:
        print(f"  + {a}")
    for c in changed:
        print(f"  ~ {c}")

    if args.rebuild:
        print(f"[repo_map_check] --rebuild: regenerating map...")
        import repo_map as rm
        graph = rm.build_map(args.repo)
        out_dir = os.path.join(os.path.abspath(args.repo), args.out)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "repo-map.md"), "w", encoding="utf-8") as f:
            f.write(rm.render_markdown(graph))
        with open(os.path.join(out_dir, "graph.json"), "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2, default=str)
        with open(os.path.join(out_dir, "fingerprint.json"), "w", encoding="utf-8") as f:
            json.dump(rm.compute_fingerprint(graph), f, indent=2)
        print(f"[repo_map_check] rebuilt → {out_dir}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
