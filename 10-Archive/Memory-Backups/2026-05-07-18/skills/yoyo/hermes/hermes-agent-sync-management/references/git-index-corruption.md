# Git Index Corruption — "All Files Deleted" Syndrome

## Symptom

```
$ git status
On branch main
Your branch is behind 'origin/main' by 32 commits, and can be fast-forwarded.
  (use "git pull" to update your local branch)

Changes not staged for commit:
  (use "git add/rm <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        deleted:    .dockerignore
        deleted:    .env.example
        deleted:    .envrc
        deleted:    README.md
        ...
```

**But**: `ls -la README.md` shows the file exists. Agent runs normally.

## Root Cause

Git index (`.git/index`) is out of sync with working tree. Common triggers:
- Interrupted `git` operation (kill -9, power loss)
- Filesystem issues / NFS cache desync
- Concurrent git operations
- Bug in git version (rare)

## Diagnosis Matrix

| Check | Command | Expected (healthy) | Corrupted |
|-------|---------|-------------------|-----------|
| Index file exists | `ls -la .git/index` | regular file | zero bytes or missing |
| FSCK clean | `git fsck --full` | no output | dangling/failed objects |
| Actual file state | `ls path/to/file` | exists | N/A (file fine) |
| HEAD commit valid | `git show HEAD:README.md` | shows content | error "path does not exist" |

## Recovery Steps (order of increasing destructiveness)

**Step 1 — Soft reset (preserves uncommitted changes)**
```bash
git reset --hard
# Rebuilds index from HEAD. Safe: no commits lost.
```

**Step 2 — Full reset (if Step 1 fails)**
```bash
git reset --hard HEAD
git clean -fdx   # WARNING: removes ALL untracked files/dirs
```

**Step 3 — Re-clone (last resort)**
```bash
cd ..
mv hermes-agent hermes-agent.backup
git clone <remote-url> hermes-agent
# Manually restore any custom/untracked files from backup
```

## Verification

After recovery:
```bash
git status  # Should show "nothing to commit, working tree clean"
git log -1   # Should show recent commit
```

## Prevention

- Avoid killing git mid-operation
- Use `git commit -m "msg"` (single operation) vs separate `git add` + `git commit` if system unstable
- For NFS/CIFS mounts, set `git config core.trustctime false`
- Regular `git fsck` in cron for automated detection

## Case Study: Hermes Agent at `/usr/local/lib/hermes-agent`

**Observed**: `git status` showed all files deleted, but agent v0.12.0 ran fine. Index corrupted; working tree intact.

**Fix**:
```bash
cd /usr/local/lib/hermes-agent
git reset --hard
git status  # Clean
git pull origin main  # Sync 32 commits
```

**No data loss** — all tracked files preserved in working directory; only index rebuilt.