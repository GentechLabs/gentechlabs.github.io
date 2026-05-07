---
name: hermes-agent-sync-management
description: Diagnose and manage Hermes agent fork sync status, upstream tracking, and development fork lifecycle
triggers:
  - keywords: ["hermes fork sync", "agent sync status", "fork behind", "check hermes updates", "sync hermes fork"]
  - context: "hermes-agent installation requires sync diagnosis or fork management"
---

# Hermes Agent Sync & Fork Management

Systematic methodology for verifying Hermes agent installation sync status, diagnosing fork health, and managing upstream relationships.

## When to Use

- Checking if local installation is up-to-date with upstream
- Diagnosing sync issues or merge conflicts
- Verifying fork existence and tracking configuration
- Recovery from git index corruption
- Planning custom skill development in a fork

## Procedure

### 1. Locate Active Installation

Hermes agent may be installed in multiple locations. Check common paths:

```bash
# Check standard install locations
ls -la /usr/local/lib/hermes-agent/ 2>/dev/null  # Common system install
ls -la /root/hermes-agent/ 2>/dev/null          # Expected dev fork location
ls -la ~/hermes-agent/ 2>/dev/null              # User install

# Use find if locations unknown (timeout ~10s)
find / -maxdepth 4 -name "hermes-agent" -type d 2>/dev/null
```

Look for `.git` directory presence to confirm git repository.

### 2. Check Git Health & Remotes

```bash
cd <hermes-agent-dir>

# Show configured remotes
git remote -v

# Show current branch and HEAD
git branch --show-current
git rev-parse HEAD

# Check git config for fork tracking
git config --list | grep -E "remote|branch"
```

**Expected output**: Should show `origin` pointing to a GitHub repo. Two common patterns:

1. **System install / vanilla upstream**: `origin` points directly to `NousResearch/hermes-agent`. No separate `upstream` remote. Typical for `/usr/local/lib/hermes-agent`.
2. **Development fork**: `origin` points to your fork (e.g., `Gentech-Labs/hermes-agent`); separate `upstream` remote points to `NousResearch/hermes-agent`.

**Detection**: `git remote -v`. Only `origin` with NousResearch URL = Pattern 1 (system install). Both `origin` + `upstream` = Pattern 2 (dev fork).

**Pitfall**: If `upstream` remote missing but `origin` points to `Gentech-Labs/`, the fork remote may be misconfigured. If `origin` points to `NousResearch/`, missing `upstream` is expected for system installs.

### 3. Compare Local vs Upstream

```bash
# Fetch upstream (if configured)
git fetch upstream 2>/dev/null || echo "No upstream remote"

# Count commits ahead/behind
git rev-list --left-right --count HEAD...origin/main
# Format: <ahead> <behind>

# List specific commits
git log --oneline HEAD..origin/main      # Commits upstream has (we're behind)
git log --oneline origin/main..HEAD      # Commits local has (we're ahead)

# Quick ahead/behind check
git status  # Shows "behind N commits" or "ahead M commits"
```

### 4. Detect Index/Worktree Corruption

**Symptom**: `git status` shows hundreds of files as deleted (`D filename`) but files exist on disk and agent runs.

**Diagnosis**:
```bash
# Check if files exist despite git saying deleted
ls -la path/to/file.py  # Should exist

# Check fsck
git fsck --full
```

**Recovery** (non-destructive first):
```bash
# Option A: Reset index from HEAD (preserves uncommitted work)
git reset --hard

# Option B: Full reset if needed
git reset --hard HEAD
git clean -fdx  # CAREFUL: removes all untracked files
```

**Why this happens**: Index (`.git/index`) got out of sync with working tree — common after interrupted operations, filesystem issues, or NFS/cifs mounts.

### 5. Check for Custom Skills

Custom Gentech skills may exist outside the main repo tree:

```bash
# Check common custom skill locations
find . -path "*skills/gentech*" -o -path "*skills/dmob*" 2>/dev/null
ls -la ~/.hermes/skills/ 2>/dev/null
ls -la .agents/skills/ 2>/dev/null  # Agent-created skills
ls -la .adal/skills/ 2>/dev/null    # Another custom location

# In the vault
find /root/vaults/gentech/skills/ -type f -name "*.md" 2>/dev/null
```

Custom skills in untracked directories won't be affected by `git pull`.

### 6. Fork Existence Verification

Before assuming a fork exists:

```bash
# Check via GitHub API (no auth needed for public repos)
curl -s "https://api.github.com/repos/Gentech-Labs/hermes-agent" | head -20
# Returns 404 if no fork exists

# Check git remote URL format
git remote get-url origin
# Nous upstream: https://github.com/NousResearch/hermes-agent.git
# Gentech fork:  https://github.com/Gentech-Labs/hermes-agent.git
```

**If fork doesn't exist**: Either track upstream directly or create fork first.

### 7. Breaking Change Detection

Upstream sync may introduce breaking changes:

```bash
# Review incoming commits for BREAKING CHANGE markers
git log HEAD..origin/main --oneline | head -20

# Check release notes in repo
cat RELEASE_v*.md | grep -i "BREAKING" | head -5

# Compare major version
grep "version:" pyproject.toml | head -1
```

Flag any commits with `BREAKING CHANGE:` in commit message or major version bump (v0.x → v1.x).

### 8. Merge Conflict Prevention

Fast-forward syncs have no conflicts. Non-fast-forward requires rebase or merge:

```bash
# If not fast-forwardable
git merge-base HEAD origin/main  # Find common ancestor
git diff HEAD...origin/main       # Show divergence

# Recommended: rebase to keep linear history
git pull --rebase origin main

# Or fetch + manual merge
git fetch origin
git merge origin/main
```

**Tip**: Local-only commits (ahead) should be rebased onto upstream after pull.

## Decision Matrix

| State | Action |
|-------|--------|
| 0 ahead, 0 behind | Nothing to do |
| N behind, 0 ahead | `git pull --rebase origin main` (fast-forward) |
| 0 behind, M ahead | Local work exists. Consider: keep fork, or `git push` to fork |
| Behind + ahead | Non-linear. `git pull --rebase origin main`, resolve conflicts |
| Index corruption | `git reset --hard` first, then sync |
| No fork configured | Track upstream directly or fork on GitHub first |

## Automation Cheat Sheet

```bash
# One-liner sync (clean working tree)
cd /usr/local/lib/hermes-agent && git fetch origin && git reset --hard origin/main

# One-liner with health check
cd /path/to/hermes-agent && \
  echo "=== Remotes ===" && git remote -v && \
  echo "=== Status ===" && git status -sb && \
  echo "=== Ahead/Behind ===" && git rev-list --left-right --count HEAD...origin/main
```

## Related Skills

- `hermes-agent-health-check` — broader agent health (process, logs, env)
- `git` operations — standard git workflows
- `vault-first-research` — if documenting findings in vault

## Support Files

- `scripts/fork-sync-diagnostic.sh` — one-command diagnostic script (run from any Hermes install)
- `templates/fork-setup.sh` — step-by-step fork setup commands
- `references/git-index-corruption.md` — syndrome diagnosis, recovery, and prevention

## Pitfalls

1. **Untracked custom skills**: `git pull` only affects tracked files. Custom skills in `.agents/skills/`, `.adal/skills/`, or vault remain untouched.

2. **Index corruption after system crash**: Git may think all files are deleted. Fix with `git reset --hard` before attempting sync.

3. **Wrong remote configured**: Double-check `git remote -v`. `origin` should point to your fork (Gentech) or upstream (Nous). Use `git remote set-url origin <url>` to fix.

4. **Non-fast-forward updates**: If local has commits not on upstream, `git pull` will create merge commit or require rebase. Use `git pull --rebase` for linear history.

5. **Path confusion**: Active agent may run from `/usr/local/lib/` while development fork expected at `/root/`. Check process list: `ps aux | grep hermes` to see actual binary path.

6. **Permission issues**: System installs may be read-only. Use `sudo` if needed, or better: run from user-owned directory.

7. **Branch mismatch**: Always operate on `main` branch unless feature branch explicitly intended. Use `git checkout main` first.