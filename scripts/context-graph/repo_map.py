#!/usr/bin/env python3
"""
repo_map.py — Persistent Repo-Context Graph (borrowed from Graft, ported to our own design).

Builds a compact, persistent markdown map of a codebase once, so an agent
re-orients at session start instead of cold-start re-exploring (grep → open →
re-follow imports every run). Each subsystem gets: what it does (from docstrings
+ top-of-file comments), the 3-5 crux lines (key logic), its depends_on (imports
of sibling modules) and used_by (reverse edges).

Pure stdlib. No external deps.

USAGE:
    python3 repo_map.py /path/to/repo            # build repo-map.md + .repo-map.json
    python3 repo_map.py /path/to/repo --json     # print JSON map instead of writing files

Writes (into the repo root):
    .repo-map/repo-map.md          # the human/agent-readable map
    .repo-map/graph.json           # machine-readable graph (for blast_radius.py)
    .repo-map/fingerprint.json     # content-hash snapshot (for repo_map_check.py)

Mechanism (the meat):
    1. Walk the repo, skip junk dirs (.git, node_modules, __pycache__, dist, build,
       .venv, vendor).
    2. For each source file (py/js/ts/mjs/cjs/sol/rs/go), record:
       - header = leading comment block / module docstring  (the "what")
       - crux  = lines that look like core logic: top-level defs/class names +
                 high-signal lines (regex match, return, throw, event emit)
       - imports of *sibling* modules (relative/aliased) → depends_on
    3. Compute the graph: used_by = reverse of depends_on.
    4. Emit the markdown map + machine graph + content-hash fingerprint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Junk directories / files to skip when walking.
# ---------------------------------------------------------------------------
JUNK_DIRS = {
    ".git", "node_modules", "__pycache__", "dist", "build", ".venv", "venv",
    "vendor", ".next", ".cache", ".pytest_cache", ".repo-map", ".terraform",
    ".idea", ".vscode", "target", ".tox", ".mypy_cache",
}
JUNK_FILES = {".DS_Store", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}

# Extensions we can extract structure from.
CODE_EXTS = {".py", ".js", ".ts", ".mjs", ".cjs", ".jsx", ".tsx", ".sol", ".rs", ".go", ".sh"}

# A file is "crux-worthy" if it's larger than this (bytes) — big files get the
# full crux treatment; small files just get their header.
SMALL_FILE_BYTES = 6000

# Lines in a file that hint at real logic worth surfacing as crux.
_CRUX_RE = re.compile(
    r"^\s*(def |async def |class |func |fn |export (async )?function|function |"
    r"return |throw |raise |emit\(|publish\(|await |contract |struct )",
)
# High-value signal inside a function body: regexes, security checks, hard paths.
_SIGNAL_RE = re.compile(
    r"(re\.(match|search|compile|fullmatch)|secrets\.|uuid\.|"
    r"hashlib\.|urllib|requests\.|https?://|verify|signature|payTo|402|x402|"
    r"private|secret|api_key|deadline|nonce)",
)

# Import statement matchers (sibling module detection happens after).
_PY_IMPORT = re.compile(
    r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.M
)
_JS_IMPORT = re.compile(
    r"^\s*(?:import\s+.*?from\s+['\"]([^'\"]+)['\"]|"
    r"require\(['\"]([^'\"]+)['\"]\))", re.M
)


def _is_code_file(path: str) -> bool:
    return path.endswith(tuple(CODE_EXTS)) and os.path.basename(path) not in JUNK_FILES


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def _header_of(src: str) -> str:
    """Return the leading docstring/comment block of a source file (the 'what')."""
    stripped = src.lstrip("\ufeff \t\n")
    lines = stripped.splitlines()
    if not lines:
        return ""
    out = []
    # Python docstring
    if lines[0].startswith(('"""', "'''")):
        quote = lines[0][:3]
        for ln in lines[1:]:
            if ln.strip().endswith(quote) or ln.strip() == quote:
                break
            out.append(ln.strip().lstrip("*"))
        return " ".join(x for x in out if x)[:400]
    # Comment header block (# or // or /* ...)
    for ln in lines[:30]:
        s = ln.strip()
        if s.startswith(("#", "//", "*", "/*")):
            t = s.lstrip("#/* \t")
            if t and not t.startswith(("@", "!")):
                out.append(t)
        elif s and not out:
            continue
        elif s:
            break
    return " ".join(x for x in out if x)[:400]


def _crux_lines(src: str) -> list[str]:
    """Extract the 3-5 'crux' lines that carry the file's core logic."""
    hits = []
    for ln in src.splitlines():
        s = ln.strip()
        if not s:
            continue
        if _CRUX_RE.match(s):
            hits.append(s[:140])
        elif _SIGNAL_RE.search(s) and len(hits) < 60:
            hits.append(s[:140])
    # de-dup preserving order
    seen, uniq = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h)
            uniq.append(h)
    return uniq[:5]


def _sibling_imports(src: str, file_dir: str, repo_root: str) -> list[str]:
    """Find imports that resolve to sibling modules inside the same repo."""
    root_abs = os.path.abspath(repo_root)
    dir_abs = os.path.abspath(file_dir)
    deps = []
    for m in _PY_IMPORT.finditer(src):
        full = m.group(1) or m.group(2) or ""
        # Walk the dotted path from longest to shortest; first one that exists
        # inside the repo wins (resolves `injective_functions.bank` to that submodule).
        resolved = _resolve_py_module(full, dir_abs, root_abs)
        if resolved:
            deps.append(resolved)
    for m in _JS_IMPORT.finditer(src):
        spec = (m.group(1) or m.group(2) or "").strip()
        if spec.startswith(("/node_modules", "http")) or not spec:
            continue
        # Resolve relative import: strip leading ./ ../, take first path segment
        norm = spec.lstrip("./")
        base = norm.split("/")[0]
        # Drop file extension for consistency with sibling module keys
        extless = base.split(".")[0] if "." in base else base
        if extless and extless != "." and extless != "..":
            # verify it resolves within the repo before claiming a dependency
            base_dir = dir_abs if spec.startswith(".") else root_abs
            cand = os.path.join(base_dir, base)
            cand_js = os.path.join(base_dir, extless + ".js")
            cand_ts = os.path.join(base_dir, extless + ".ts")
            if os.path.exists(cand) or os.path.exists(cand_js) or os.path.exists(cand_ts):
                deps.append(extless)
    return sorted(set(deps))


def _resolve_py_module(full: str, dir_abs: str, root_abs: str) -> str | None:
    """Resolve a dotted python import to a sibling module path (or None)."""
    if not full or full.startswith("_"):
        return None
    parts = full.split(".")
    # Try longest-first: injective_functions.bank.exchange → ...bank.exchange → bank
    for i in range(len(parts), 0, -1):
        mod = ".".join(parts[:i])
        # candidates: module file, package dir, package __init__
        candidates = [
            os.path.join(dir_abs, *parts[:i]) if i == 1 else None,
            os.path.join(root_abs, *parts[:i]) if i == 1 else None,
        ]
        # dotted path → nested dirs under root
        nested = os.path.join(root_abs, *parts[:i])
        file_cand = os.path.join(root_abs, *parts[:i - 1], parts[i - 1] + ".py")
        if os.path.isfile(file_cand) or os.path.isdir(nested) or os.path.isfile(os.path.join(nested, "__init__.py")):
            return mod
        # also relative to file_dir (same-dir import like `from .bank import x`)
        rel_nested = os.path.join(dir_abs, *parts[:i])
        if os.path.isfile(os.path.join(dir_abs, *parts[:i - 1], parts[i - 1] + ".py")) or os.path.isdir(rel_nested):
            return mod
    return None



def _subsystem_key(rel_path: str, repo_root: str) -> str:
    """Map a file to a subsystem: top-level dir if present, else file stem."""
    parts = rel_path.split(os.sep)
    if len(parts) >= 2:
        return parts[0]
    return os.path.splitext(parts[-1])[0]


def build_map(repo_root: str) -> dict:
    """Scan repo_root and return the graph dict."""
    repo_root = os.path.abspath(repo_root)
    files = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        # prune junk in-place
        dirnames[:] = [d for d in dirnames if d not in JUNK_DIRS and not d.endswith(".egg-info")]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if _is_code_file(full):
                files.append(full)

    # Per-file records
    subsystems = defaultdict(list)
    file_records = {}
    for full in sorted(files):
        try:
            with open(full, "r", encoding="utf-8", errors="replace") as f:
                src = f.read()
        except OSError:
            continue
        rel = os.path.relpath(full, repo_root)
        size = os.path.getsize(full)
        header = _header_of(src)
        crux = _crux_lines(src) if size > SMALL_FILE_BYTES else []
        deps = _sibling_imports(src, os.path.dirname(full), repo_root)
        record = {
            "path": rel,
            "size": size,
            "sha": _sha256(src),
            "header": header,
            "crux": crux,
            "depends_on": deps,
        }
        file_records[rel] = record
        subsystems[_subsystem_key(rel, repo_root)].append(rel)

    # used_by: reverse edges
    used_by = defaultdict(list)
    for rel, rec in file_records.items():
        for d in rec["depends_on"]:
            used_by[d].append(rel)

    graph = {
        "repo": os.path.basename(repo_root),
        "root": repo_root,
        "files": file_records,
        "subsystems": {k: sorted(v) for k, v in subsystems.items()},
        "used_by": {k: sorted(set(v)) for k, v in used_by.items()},
    }
    return graph


def render_markdown(graph: dict) -> str:
    """Render the machine graph into a compact agent-readable markdown map."""
    lines = []
    lines.append(f"# Repo Context Map — {graph['repo']}\n")
    lines.append(
        f"> Persistent codebase map. Regenerate when the code drifts (see "
        f"repo_map_check.py). Format: per-subsystem summary + crux + "
        f"depends_on/used_by links.\n"
    )
    for sub, rels in graph["subsystems"].items():
        lines.append(f"\n## {sub}\n")
        for rel in rels:
            rec = graph["files"][rel]
            lines.append(f"### `{rel}`")
            if rec["header"]:
                lines.append(f"- **What:** {rec['header']}")
            if rec["depends_on"]:
                lines.append(f"- **depends_on:** {', '.join('`'+d+'`' for d in rec['depends_on'])}")
            ub = graph["used_by"].get(os.path.splitext(rel)[0].split(os.sep)[-1]) or \
                 graph["used_by"].get(rel)
            if rec["crux"]:
                lines.append("- **Crux:**")
                for c in rec["crux"]:
                    lines.append(f"  - `{c}`")
            lines.append("")
    return "\n".join(lines)


def compute_fingerprint(graph: dict) -> dict:
    """Snapshot of every file's content hash — used for staleness check."""
    return {
        "repo": graph["repo"],
        "root": graph["root"],
        "files": {rel: rec["sha"] for rel, rec in graph["files"].items()},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a persistent repo-context graph.")
    ap.add_argument("repo", help="Path to the repository to map")
    ap.add_argument("--json", action="store_true", help="Print the graph as JSON to stdout (no files written)")
    ap.add_argument("--out", default=".repo-map", help="Output dir (default: .repo-map inside repo)")
    args = ap.parse_args()

    if not os.path.isdir(args.repo):
        print(f"error: not a directory: {args.repo}", file=sys.stderr)
        return 2

    graph = build_map(args.repo)

    if args.json:
        print(json.dumps(graph, indent=2, default=str))
        return 0

    out_dir = os.path.join(os.path.abspath(args.repo), args.out)
    os.makedirs(out_dir, exist_ok=True)
    md = render_markdown(graph)
    fp = compute_fingerprint(graph)
    with open(os.path.join(out_dir, "repo-map.md"), "w", encoding="utf-8") as f:
        f.write(md)
    with open(os.path.join(out_dir, "graph.json"), "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2, default=str)
    with open(os.path.join(out_dir, "fingerprint.json"), "w", encoding="utf-8") as f:
        json.dump(fp, f, indent=2)

    n_files = len(graph["files"])
    n_subs = len(graph["subsystems"])
    print(f"[repo_map] mapped {n_files} files across {n_subs} subsystems → {out_dir}")
    print(f"[repo_map] wrote repo-map.md, graph.json, fingerprint.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
