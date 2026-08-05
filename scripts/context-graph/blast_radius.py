#!/usr/bin/env python3
"""
blast_radius.py — Blast-radius-on-edit resolver for the repo-context graph.

Borrowed primitive #3 from Graft: when about to edit a shared symbol/file,
resolve its callers/imports/dependents (via the graph) and print the blast
radius BEFORE the change — the same nudge Graft gives, so we don't break a
sibling subsystem silently.

Reads graph.json produced by repo_map.py. Pure stdlib.

USAGE:
    python3 blast_radius.py /path/to/repo <file-or-module>   # who depends on it
    python3 blast_radius.py /path/to/repo src/ai/agent.js
    python3 blast_radius.py /path/to/repo agent_server       # by module stem

EXIT CODES:
    0  OK — printed dependents
    2  not found in graph (run repo_map.py first, or the file isn't mapped)
"""
from __future__ import annotations

import argparse
import json
import os
import sys


def _load_graph(repo_root: str, out: str = ".repo-map") -> dict:
    path = os.path.join(os.path.abspath(repo_root), out, "graph.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"no graph at {path} — run repo_map.py first")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve(graph: dict, target: str) -> tuple[list[str], list[str]]:
    """Return (direct_dependents, transitive_closure) for the target path/module."""
    files = graph["files"]
    used_by = graph.get("used_by", {})

    def _module_keys(path: str) -> list[str]:
        """Convert a file path to the dotted module keys it may be referenced as."""
        keys = []
        rel = path.replace(os.sep, "/").lstrip("/")
        if rel.endswith((".py", ".js", ".ts", ".mjs", ".cjs", ".jsx", ".tsx")):
            base = rel[:-3] if rel.endswith(".py") else rel[:-3]
            keys.append(base.replace("/", "."))
            keys.append(base)  # also the path form
            # bare basename stem (JS relative imports resolve to bare names, e.g. 'app')
            stem = os.path.basename(base)
            if stem != base:
                keys.append(stem)
        return keys

    # Normalize target: exact path, path-suffix, or bare module stem
    target_key = target.replace(os.sep, "/")
    matches = [k for k in files if k == target_key or k.endswith("/" + target_key)]
    if not matches:
        stem = os.path.splitext(os.path.basename(target_key))[0]
        matches = [k for k in files if os.path.splitext(os.path.basename(k))[0] == stem]

    if not matches:
        return [], []

    # Collect all lookup keys for the matched files (paths + module names)
    lookup_keys = set()
    for k in matches:
        lookup_keys.add(k)
        lookup_keys.update(_module_keys(k))

    direct = set()
    for key in lookup_keys:
        direct.update(used_by.get(key, []))
        # also invert depends_on of every file for this key
        for rel, rec in files.items():
            if key in rec.get("depends_on", []):
                direct.add(rel)
    direct.discard(*matches)

    # transitive closure over direct dependents
    transitive = set(direct)
    changed = True
    while changed:
        changed = False
        for rel in list(transitive):
            for key in _module_keys(rel):
                for dep in used_by.get(key, []):
                    if dep not in transitive:
                        transitive.add(dep)
                        changed = True

    return sorted(direct), sorted(transitive)


def main() -> int:
    ap = argparse.ArgumentParser(description="Blast-radius resolver for a repo graph.")
    ap.add_argument("repo", help="Path to the repository")
    ap.add_argument("target", help="File path or module stem to resolve dependents for")
    ap.add_argument("--out", default=".repo-map", help="Graph dir (default: .repo-map)")
    ap.add_argument("--transitive", action="store_true", help="Also show transitive closure")
    args = ap.parse_args()

    try:
        graph = _load_graph(args.repo, args.out)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    direct, transitive = resolve(graph, args.target)
    if not direct:
        print(f"[blast_radius] no dependents found for '{args.target}'")
        print(f"[blast_radius] (check the path/stem, or that it's a mapped source file)")
        return 2

    print(f"[blast_radius] {len(direct)} direct dependents of '{args.target}':")
    for d in direct:
        print(f"  ← {d}")
    if args.transitive:
        print(f"\n[blast_radius] {len(transitive)} in transitive closure:")
        for d in transitive:
            print(f"  ↯ {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
