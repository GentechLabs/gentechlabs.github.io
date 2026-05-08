---
name: vault-atomic-operations
description: Atomic concurrent-safe read/write operations for shared Obsidian vault access. File-locking patterns, append-only logging, search utilities, and integration workflows for multi-agent environments where the vault is the single source of truth.
version: 0.1.0
author: DMOB (Gentech Labs)
license: MIT
metadata:
  hermes:
    tags: [vault, obsidian, concurrency, file-locking, shared-brain, atomic]
    related_skills: [vault-audit, vault-intelligence-recon, hermes-operations]
---

# Vault Atomic Operations

When multiple agents (Hermes instances, cron jobs, human operators) need to read/write the same Obsidian vault concurrently, race conditions can corrupt context, lose decisions, or create merge conflicts. This skill provides a **file-locking + append-only** pattern that makes the vault a safe shared brain.

## Problem

Without coordination:
- Two agents append to the same `.md` file simultaneously → lost writes or corrupted delimiter structure
- Simultaneous reads during a partial write → torn reads
- No provenance tracking → unclear who wrote what and when

## Solution

`vault_writer.py` implements:
- **File-based locks** (`fcntl.flock`) per group/file namespace
- **Atomic append** with `---` delimiter and `## {timestamp} — {author}` headers
- **Idempotent writes** — same timestamp won't duplicate (detected in content)
- **Tail reads** — fetch last N entries without scanning entire file
- **Fast substring search** across vault with context lines

All operations are **single-process safe** and work across any language that can call Python scripts.

---

## Quick Start

```bash
# Install (already in Labs scripts)
ls /root/vaults/gentech/02-Labs/scripts/vault_writer.py

# Append a decision/ finding
./vault_writer.py write 02-Labs/decisions.md \
  --content "Use Checks-Effects-Interactions for all external calls" \
  --author DMOB --group Labs

# Read full file with metadata
./vault_writer.py read 02-Labs/decisions.md

# Read last 3 entries only
./vault_writer.py read 02-Labs/decisions.md --tail 3

# Search for "reentrancy" across Labs files
./vault_writer.py search "reentrancy" --group Labs --limit 20
```

Output is JSON: `{"status":"ok","path":"...","timestamp":"...","bytes_written":123}`

---

## Conventions

| Element | Pattern | Rationale |
|---------|---------|-----------|
| Lock namespace | `{group}-{filename}` (no extension) | E.g., `Labs-decisions` — prevents cross-group collisions |
| Timestamp format | ISO 8601 with timezone (`2026-05-03T18:35:59.677604+00:00`) | Lexicographically sortable, unambiguous |
| Entry delimiter | `---\n` (three dashes on their own line) | Clear boundary for tail/parsing; avoids regex ambiguity |
| Author field | `## {timestamp} — {author}` | Visible provenance in rendered markdown |
| Write mode | `append` (default), `overwrite` (rare) | Prevent accidental overwrites; overwrite requires explicit opt-in |
| Frontmatter | Optional YAML block at file top (`---\nkey: val\n---`) | Machine-readable metadata for integrations |

---

## Integration Pattern

### Agent lifecycle hook

```python
# Before starting work
read_result = vault_writer.read("02-Labs/brain.md", tail=5)
context = read_result["content"]  # feed into LLM system prompt

# ... perform task ...

# After completion
vault_writer.write("02-Labs/brain.md",
  content=f"Found: {finding}",
  author=agent_name,
  group="Labs")
```

### Hermes agent skill

Load `vault-atomic-operations` in any Hermes session:
```
/skill vault-atomic-operations
```
Then use terminal tool to call `vault_writer.py` directly.

### Cron job logging

```bash
# Log scanner results without stepping on other scanner instances
0 9 * * * /root/vaults/gentech/02-Labs/scripts/vault_writer.py write \
  02-Labs/scans/daily-$DATE.md \
  --content "$(cat scan-report.json)" \
  --author "opportunity-scanner" --group "Labs"
```

---

## Pitfalls

### 1. Lock timeout too short
If multiple agents contend heavily (e.g., many scanners running in parallel), default 30s timeout may be tight. **Increase via `--timeout`** or batch writes less frequently.

### 2. Tail parsing depends on delimiter consistency
Never edit entry delimiters manually. If delimiter structure gets corrupted, regenerate file from latest backup then resume append-only.

### 3. No built-in merge/conflict resolution
This is **last-write-wins at append granularity**. If two agents write different content within the same timestamp window, both entries appear sequentially. Do not use `overwrite` mode concurrently — it will clobber.

### 4. Timezone drift
Ensure all systems run NTP. ISO timestamps include timezone, but skewed clocks produce non-chronological order in tail reads.

### 5. Large files
Tail reads are cheap; full reads of multi-MB vault files become slow. Split by topic (e.g., `decisions-2026-Q2.md` vs `decisions-archive.md`) and rotate quarterly.

### 6. Stale vault clones (gentech-vault problem)
Old clones (`/root/gentech/gentech-vault`, `/root/vault`) can drift and silently accumulate commits. They're not part of the backup chain and should be removed. **Detection:** check remote URLs and last modified dates:

```bash
# Find vault-like dirs
find /root -maxdepth 2 -type d -name "*vault*" | grep -v vaults/gentech

# Inspect remotes of any git repos found
for d in /root/gentech/gentech-vault /root/vault; do
  if [ -d "$d/.git" ]; then
    echo "=== $d ==="
    git -C "$d" remote -v
  fi
done
```

**Cleanup:** If a clone hasn't been modified since the last major sweep (e.g., pre-2026-05-03) and points at an obsolete remote, archive (tar → `10-Archive/brain-prune-2026-05-03/`) then delete. Update any lingering SOUL references from `/root/vault` → `/root/vaults/gentech`.

### 7. Headless sync unnecessary when git backup exists
If you already have a git-based backup repo (like `hermes-brain-backup`), **do not add obsidian-headless-sync** — it introduces another sync layer with no benefit. Use atomic writes + rsync + git push. See [Architecture: Gentech brain backup](references/brain-backup-architecture.md).

---

## Extension: Git-Native Writes

If your backup repo is git-tracked and you want automatic commits on each write, wrap `vault_writer.py`:

```bash
#!/bin/bash
# vault_git_writer.sh
set -e
VAULT="/root/vaults/gentech"
WRITER="02-Labs/scripts/vault_writer.py"

# 1. Atomic write
python3 "$VAULT/$WRITER" write "$1" --content "$2" --author "$3" --group "$4"

# 2. Commit if repo dirty
cd "$VAULT"
if ! git diff --quiet; then
  git add -A
  git commit -m "vault: $1 updated by $3 $(date -u +%Y-%m-%dT%H:%M:%SZ)"
fi
```

Enable only if you want full git history per entry (creates many small commits).

---

## Vault Folder Consolidation

When merging top-level vault folders (e.g., `03-Projects` → `02-Labs`), follow this pattern:

### Pre-flight Check
```bash
# List source subfolders
ls -1d 03-Projects/*/

# Check for name conflicts in destination
for d in $(ls -1d 03-Projects/*/); do
  name=$(basename "$d")
  [ -d "02-Labs/$name" ] && echo "CONFLICT: $name" || echo "OK: $name"
done
```

### Merge Execution
```bash
# Clean moves (no conflict)
for d in AAE BirdeyeBIP DeFi; do
  mv "03-Projects/$d" "02-Labs/" && echo "✓ Moved $d"
done

# Conflict resolution (e.g., Hackathons) — merge contents, not directories
mv 03-Projects/Hackathons/*.md 02-Labs/Hackathons/

# Move loose files
mv 03-Projects/*.md 02-Labs/

# Cleanup empty source
find 03-Projects -empty -type d -delete
rmdir 03-Projects
```

### Post-merge: Update References
After folder consolidation, search the entire vault for stale path references:
```bash
grep -rn "03-Projects" --include="*.md" --include="*.json" --include="*.html" .
```
Update all references to the new paths. This includes:
- Portfolio `projects.json` vault_path fields
- Inline JavaScript in HTML files (use `sed` — the `patch` tool fails on escaped quotes in JS strings)
- Obsidian wikilinks and embeds
- Cron script paths

**Pitfall:** `sed` works better than the `patch` tool for updating paths embedded in JavaScript strings inside HTML files. The `patch` tool can't match escaped quote patterns like `\"vault_path\"`.

## Related

- `vault-audit` — scans vault for structural integrity and sensitive data exposure
- `vault-intelligence-recon` — discovers credentials, contacts, and operational intel
- `hermes-operations` — Hermes Agent vault connectivity patterns

---

## References

### Script source
`02-Labs/scripts/vault_writer.py` — single-file, zero-dependency (only stdlib). Drop into any Python 3.8+ environment.

### Lock semantics
Uses `fcntl.flock(fd, LOCK_EX | LOCK_NB)` — advisory, mandatory on same filesystem. Blocks other `vault_writer` instances until released. Does NOT prevent manual edits outside the writer; those bypass locks (intentional — humans can force-write during emergencies).

### Idempotency
Duplicate detection: if the exact `## {timestamp} — {author}` block already exists in the file, append is skipped. Relies on unique timestamps (second precision) + author name collision avoidance.

### Performance
- Lock acquisition: ~0.1s uncontended, retry loop with 0.1s backoff
- Single-append: ~0.01s after lock held
- Tail read (N=10 on 1000-entry file): ~0.02s
- Full read of 10k-line file: ~0.15s

Safe for dozens of concurrent agents. Beyond ~50 simultaneous writers, consider sharding by topic file to reduce lock contention.
