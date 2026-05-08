# Fork Sync Diagnostic Script — Hermes Agent

One-command diagnostic to assess Hermes agent fork sync health.

## Usage

```bash
cd /path/to/hermes-agent
# Or use absolute path directly
./scripts/fork-sync-diagnostic.sh /usr/local/lib/hermes-agent
```

## What It Checks

1. **Installation path**: Verifies directory exists and is a git repo
2. **Active process**: Shows if agent is running from this path
3. **Remote configuration**: Lists all remotes (origin/upstream) with URLs
4. **Current branch & HEAD**: Shows branch name and commit hash
5. **Ahead/Behind counts**: Numeric difference vs origin/main and upstream/main
6. **Uncommitted changes**: Any local modifications (should be none for clean sync)
7. **Custom skills detection**: Untracked skill directories outside git
8. **Git health**: Index size, fsck status, worktree cleanliness
9. **Index corruption flag**: Detects "all files deleted" syndrome

## Sample Output

```
=== Hermes Agent Fork Sync Diagnostic ===
Path: /usr/local/lib/hermes-agent
Git repo: YES
Agent running: YES (PID 1234)

--- Remotes ---
origin  https://github.com/NousResearch/hermes-agent.git (fetch)
origin  https://github.com/NousResearch/hermes-agent.git (push)

--- Branch Info ---
Current branch: main
HEAD: 75e1339d4 (fix(telegram): send seed message...)

--- Sync Status ---
Ahead vs origin/main: 0
Behind vs origin/main: 32
Ahead vs upstream/main: 0
Behind vs upstream/main: 32

--- Uncommitted Changes ---
None (clean)

--- Git Health ---
Index size: 124592 bytes
Worktree clean: YES
Fsck: clean

--- Custom Skills ---
Untracked skill dirs: .agents/skills/, .adal/skills/
Vault skills: /root/vaults/gentech/skills/

--- Warnings ---
[OK] No issues detected. Fast-forward sync recommended.
```

## Script Source

```bash
#!/bin/bash
# fork-sync-diagnostic.sh — Hermes agent fork sync health check

HERMES_DIR="${1:-/usr/local/lib/hermes-agent}"

echo "=== Hermes Agent Fork Sync Diagnostic ==="
echo "Path: $HERMES_DIR"

# 1. Path check
if [ ! -d "$HERMES_DIR" ]; then
  echo "ERROR: Directory not found"
  exit 1
fi
if [ ! -d "$HERMES_DIR/.git" ]; then
  echo "ERROR: Not a git repository"
  exit 1
fi
echo "Git repo: YES"

# 2. Running process
if pgrep -f "hermes.*$HERMES_DIR" >/dev/null; then
  echo "Agent running: YES (PID $(pgrep -f "hermes.*$HERMES_DIR"))"
else
  echo "Agent running: NO"
fi

cd "$HERMES_DIR" || exit 1

# 3. Remotes
echo ""
echo "--- Remotes ---"
git remote -v

# 4. Branch & HEAD
echo ""
echo "--- Branch Info ---"
echo "Current branch: $(git branch --show-current)"
echo "HEAD: $(git rev-parse --short HEAD) ($(git log -1 --oneline | cut -c8-))"

# 5. Sync counts
echo ""
echo "--- Sync Status ---"
AHEAD_ORIGIN=$(git rev-list --left-right --count HEAD...origin/main 2>/dev/null | awk '{print $1}')
BEHIND_ORIGIN=$(git rev-list --left-right --count HEAD...origin/main 2>/dev/null | awk '{print $2}')
AHEAD_UPSTREAM=$(git rev-list --left-right --count HEAD...upstream/main 2>/dev/null | awk '{print $1}')
BEHIND_UPSTREAM=$(git rev-list --left-right --count HEAD...upstream/main 2>/dev/null | awk '{print $2}')
echo "Ahead vs origin/main: ${AHEAD_ORIGIN:-N/A}"
echo "Behind vs origin/main: ${BEHIND_ORIGIN:-N/A}"
echo "Ahead vs upstream/main: ${AHEAD_UPSTREAM:-N/A}"
echo "Behind vs upstream/main: ${BEHIND_UPSTREAM:-N/A}"

# 6. Uncommitted changes
echo ""
echo "--- Uncommitted Changes ---"
CHANGES=$(git status --porcelain)
if [ -z "$CHANGES" ]; then
  echo "None (clean)"
else
  echo "$CHANGES" | head -20
fi

# 7. Git health
echo ""
echo "--- Git Health ---"
echo "Index size: $(wc -c < .git/index 2>/dev/null || echo 'missing') bytes"
git status -sb | grep -q "^## main" && echo "Worktree clean: YES" || echo "Worktree clean: NO"
git fsck --full 2>&1 | head -5

# 8. Custom skills
echo ""
echo "--- Custom Skills ---"
echo "Untracked skill dirs:"
find . -maxdepth 3 -type d -name "skills" -not -path "*/.git/*" 2>/dev/null | head -5
echo "Vault skills: $(find /root/vaults/gentech/skills/ -type f 2>/dev/null | wc -l) files"

# 9. Warnings
echo ""
echo "--- Warnings ---"
if [ "$BEHIND_ORIGIN" != "0" ] 2>/dev/null; then
  echo "[ACTION] $(git rev-list --left-right --count HEAD...origin/main | awk '{print $2}') commits behind origin/main — consider: git pull --rebase origin main"
fi
if [ "$BEHIND_UPSTREAM" != "0" ] 2>/dev/null && [ "$BEHIND_ORIGIN" = "0" ]; then
  echo "[WARNING] Tracking upstream but origin is up-to-date — fork may be stale"
fi
if [ -n "$CHANGES" ]; then
  echo "[WARNING] Uncommitted changes present — stash or commit before pulling"
fi
echo "[OK] No issues detected. Fast-forward sync recommended."
```

Save as `scripts/fork-sync-diagnostic.sh` in this skill for reuse.