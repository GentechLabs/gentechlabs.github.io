# Repo-Context Graph Toolkit

Borrowed 3 primitives from [NanoNets/Graft](https://github.com/NanoNets/Graft) (MIT) into
our own self-orientation design. **We do not adopt Graft as a dependency** — we port the
structural core to pure-stdlib Python under our control. *Eat the meat, spit out the bones.*

The problem it solves: before most builds we cold-start orientation — grep, open files,
re-follow imports — burning tool calls and tokens to rediscover a codebase we mapped
hours ago. This toolkit builds the codebase map **once**, commits it to the repo (or vault),
and lets the agent re-orient at session start instead of re-exploring.

## The 3 primitives

| # | Tool | Mechanism |
|---|------|-----------|
| 1 | `repo_map.py` | **Persistent repo map** — build a compact per-subsystem markdown graph (what it does + crux lines + depends_on/used_by) once; agents stop re-exploring from zero. |
| 2 | `repo_map_check.py` | **Staleness-aware refresh** — cheap structural check (content-hashes vs fingerprint); fails loudly (exit 1) on drift so you never act on a stale map. `--rebuild` auto-regens. |
| 3 | `blast_radius.py` | **Blast-radius on edit** — resolve callers/imports/dependents of a file/module before editing it, so you don't silently break a sibling subsystem. |

## Usage

```bash
# 1. Build the map (writes .repo-map/{repo-map.md, graph.json, fingerprint.json} into the repo)
python3 repo_map.py /path/to/repo

# 2. Before acting on a repo you've mapped, check freshness (exit 1 = drifted → rebuild)
python3 repo_map_check.py /path/to/repo            # exit 0 fresh / 1 drifted
python3 repo_map_check.py /path/to/repo --rebuild  # auto-regen if drifted

# 3. Before editing a shared symbol/file, see who depends on it
python3 blast_radius.py /path/to/repo src/ai/agent.js --transitive
python3 blast_radius.py /path/to/repo utils         # by module stem

# Tests
python3 test_context_graph.py    # 3/3 pass (Python + JS coverage)
```

## How to wire into a session

1. Once per repo you work in repeatedly: run `repo_map.py` and commit `.repo-map/` (it's a
   lightweight artifact) into the repo or vault.
2. At session start for that repo: `repo_map_check.py <repo> --rebuild` (fresh → 0 and you're
   oriented; drifted → rebuilds the map cheaply).
3. Read `.repo-map/repo-map.md` into context instead of grepping the tree.
4. Before any multi-file edit: `blast_radius.py <repo> <target>` and check the dependents.

## Design notes

- **Pure stdlib** — no deps, `$0`, runs offline. The tree-sitter tier in Graft is heavier;
  we use a lighter structural pass (headers + crux regex + import resolution) that covers
  the 80% case for py/js/ts/sol/rs/go/sh.
- **Repo-location rules** — maps resolve imports only to *sibling* modules inside the same
  repo, so third-party imports never pollute the graph.
- **True negatives** — a repo of standalone action scripts (e.g. gold-402, where each script
  reads `services.json` directly with no cross-imports) legitimately reports "no dependents".
  That's correct, not a bug.
- **Security-minded** — all three tools are read-only over the filesystem; no network, no
  subprocess-to-user-input, no writes outside the repo's `.repo-map/` dir.

## Source of the borrowed idea

- Spec: `09-Green Room/specs/graft-context-graph-borrow.md`
- Build-queue item #35
- Graft benchmark (162-run controlled): 46% fewer tool calls, 42% fewer tokens, 60% less time.
