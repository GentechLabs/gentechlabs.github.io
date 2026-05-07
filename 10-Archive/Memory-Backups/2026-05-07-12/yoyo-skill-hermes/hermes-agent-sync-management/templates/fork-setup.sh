# Fork Setup Template — Hermes Agent Development Fork

## When to Use

- Setting up a new Gentech development fork of Hermes agent
- Fixing broken remote configuration (missing upstream, wrong origin)
- Creating a proper upstream-tracking fork from scratch
- Onboarding new developer machines

## Prerequisites

- Git installed
- GitHub account with fork of `NousResearch/hermes-agent` to `Gentech-Labs/hermes-agent`
- SSH key or HTTPS credentials configured

## Setup Steps

### Option A: Fresh Clone from Fork (Recommended)

```bash
# Clone YOUR fork (origin = Gentech-Labs)
git clone git@github.com:Gentech-Labs/hermes-agent.git /path/to/hermes-agent
cd /path/to/hermes-agent

# Add upstream remote (NousResearch)
git remote add upstream https://github.com/NousResearch/hermes-agent.git

# Verify
git remote -v
# Should output:
# origin    git@github.com:Gentech-Labs/hermes-agent.git (fetch)
# origin    git@github.com:Gentech-Labs/hermes-agent.git (push)
# upstream  https://github.com/NousResearch/hermes-agent.git (fetch)
# upstream  https://github.com/NousResearch/hermes-agent.git (push)

# Sync to latest upstream main
git fetch upstream
git checkout main
git reset --hard upstream/main
git push origin main --force-with-lease
```

### Option B: Convert Existing Clone to Fork

If you cloned upstream directly but want to switch to fork:

```bash
cd /path/to/hermes-agent

# Change origin to your fork
git remote set-url origin git@github.com:Gentech-Labs/hermes-agent.git

# Add upstream if not present
git remote add upstream https://github.com/NousResearch/hermes-agent.git

# Verify
git remote -v
```

### Option C: Fix Broken Remotes (No upstream, wrong origin)

```bash
cd /path/to/hermes-agent

# Remove broken remote
git remote remove origin

# Re-add correct fork
git remote add origin https://github.com/Gentech-Labs/hermes-agent.git

# Add upstream
git remote add upstream https://github.com/NousResearch/hermes-agent.git

# Clean reset to upstream
git fetch upstream
git reset --hard upstream/main
```

## Standard Workflow After Setup

### Daily Sync (no local changes)

```bash
git fetch upstream
git rebase upstream/main   # OR: git merge upstream/main
# If conflicts: resolve, then git rebase --continue
```

### With Local Custom Commits

```bash
git fetch upstream
git rebase upstream/main   # Reapply your commits on top
# Test agent, then:
git push origin main --force-with-lease  # Update fork
```

### Create Feature Branch (for Gentech-specific work)

```bash
git checkout -b gentech-feature-name
# Make changes, commit
git push origin gentech-feature-name
# Open PR: gentech-feature-name → main (Gentech fork)
# Later: rebase onto upstream/main before merging
```

## Common Pitfalls

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `fatal: 'upstream' does not appear to be a git repository` | Upstream not configured | `git remote add upstream https://github.com/NousResearch/hermes-agent.git` |
| `origin points to NousResearch` | Forked wrong remote | `git remote set-url origin git@github.com:Gentech-Labs/hermes-agent.git` |
| `permission denied (publickey)` | SSH key not added to GitHub | Add key at GitHub Settings → SSH and GPG keys |
| Merge conflicts after `git pull` | Local commits diverge from upstream | Use `git pull --rebase` instead of merge |
| `Everything up-to-date` but behind | Fetching wrong remote | Check `git branch -vv` to see which remote branch tracks upstream |

## Verification

After setup, run diagnostic script:

```bash
/path/to/hermes-agent/scripts/fork-sync-diagnostic.sh /path/to/hermes-agent
```

Expected: 0 ahead, 0 behind, clean worktree, both remotes present.

## Nix / System Install Note

If Hermes installed via Nix or system package manager, git repo may be at `/usr/local/lib/hermes-agent`. In that case:

```bash
# Check if writable
touch /usr/local/lib/hermes-agent/test-write && rm /usr/local/lib/hermes-agent/test-write
# If permission denied, reinstall to user directory:
mkdir -p ~/hermes
git clone git@github.com:Gentech-Labs/hermes-agent.git ~/hermes
ln -s ~/hermes/hermes /usr/local/bin/  # Optional symlink
```

## Maintenance Reminder

Update `AUTHOR_MAP` and `CONTRIBUTING.md` if adding team members to fork. Keep fork in sync with upstream at least weekly to minimize drift.

---

**Template last updated**: 2026-05-02  
**Valid for**: Hermes Agent v0.12.0+