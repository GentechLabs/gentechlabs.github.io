---
title: "Spring Cleaning — Storage Bloat Analysis"
date: 2026-05-02
status: analysis-complete | cleanup-deferred
category: operations/infrastructure
---

# Spring Cleaning — May 02, 2026

##Context
Initiated due to severe storage bloat (~152 GB used). Goal: identify, archive, and remove unnecessary files to free space and resolve "wait problem" (storage constraints slowing operations).

> **Deferred** to prioritize hackathon deadlines (Solana Frontier due May 11, Kite AI due May 17).

## Actions Taken

### Storage Analysis
- Ran `du -h --max-depth=1 /root` and recursive scans
- Mapped storage consumption across system

### Bloat Sources Identified

| Category | Size | Location |
|---|---|---|
| Hermes Backup Duplication | ~56 GB | `/root/vaults/gentech/10-Archive/Hermes-Backups/20260427-215249/profiles/dmob/home/.hermes/profiles/...` (recursive `.hermes` nesting) |
| VideoAgent Tools | ~75 GB | `/root/repos/VideoAgent/tools/` (seed-vc/examples 22.5 GB, DiffSinger/data 7.3 GB) |
| Build Artifacts | TBD | Rust `target/`, Python `__pycache__`, Node `node_modules`, Solana install (~3.1 GB) |
| Git Repositories | ~142 MB+ | Large `.git/objects/pack` directories (e.g., VideoAgent) |

## Key Findings

- **Root cause**: Recursive Hermes backup loops suggest backup process bug
- **Disk pressure**: Root partition at 82% usage (157G/193G) — systemic risk
- **Impact**: Contributed to later systemic corruption (bytecode, database) affecting all agents

## Cleanup Targets (Pending)

1. Remove recursive Hermes backup loops
2. Archive/delete large VideoAgent tool datasets not immediately needed
3. Clean build artifacts across projects
4. Prune stale git objects and caches

## Next Steps

- Execute cleanup **after** May 11/17 hackathon crunch
- Investigate and fix backup process bug to prevent re-accumulation
- Monitor disk health post-cleanup