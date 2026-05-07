# Git Skill Update Patterns

When auditing skill git repos, expect these common states and apply the corresponding fix.

## Pattern: Skill Has `.git` but `origin/main` Doesn't Exist

**Symptom:**
```bash
git -C /root/skills/base rev-parse origin/main
# fatal: ambiguous argument 'origin/main': unknown revision or path not in the working tree.
```

**Cause:** The remote's default branch is `master`, not `main`. Some upstream repos still use `master`.

**Fix:**
```bash
# Probe for the correct branch
for branch in main master dev develop; do
  if git -C "$dir" rev-parse "origin/$branch" &>/dev/null; then
    echo "Remote branch: $branch"
    latest=$(git -C "$dir" rev-parse "origin/$branch")
    break
  fi
done
```

**Action:** Update the audit script to check `main`, `master`, `dev`, and `develop` in order.

---

## Pattern: Skill Has No `.git` But Shows as "local" Source

**Symptom:** `hermes skills list` shows `Source: local`, directory lacks `.git`.

**Cause:** Skill was installed from a filesystem path (not a git clone), or the `.git` directory was deleted post-install.

**Fix:**
1. Check if there's an upstream repo you can re-clone:
   ```bash
   # Look for origin URL in skill metadata
   cat /root/skills/<skill>/SKILL.md | grep -i 'github\|source\|repo'
   ```
2. If found, backup current skill and re-clone:
   ```bash
   mv /root/skills/<skill> /root/skills/<skill>.bak
   git clone <upstream-url> /root/skills/<skill>
   ```
3. If no upstream exists, **init git now** to establish provenance:
   ```bash
   cd /root/skills/<skill>
   git init
   git add -A
   git commit -m "Initial: import skill to version control"
   git remote add origin git@github.com:gentech/skills-<skill>.git
   # Push to establish remote (requires repo creation first)
   ```

**Action:** For DMOB/Labs custom skills, immediately `git init` and push to a Gentech skill remote.

---

## Pattern: Multiple Remotes (origin vs upstream)

**Symptom:** `git remote -v` shows both `origin` (your fork) and `upstream` (original).

**Cause:** Skill was forked to customize, but upstream has since moved forward.

**Fix:**
```bash
# Fetch both
git fetch origin
git fetch upstream

# Compare local against upstream/main (canonical source)
git log --oneline HEAD..upstream/main

# If you want to sync your fork:
git checkout main
git merge upstream/main   # or git rebase upstream/main
git push origin main
```

**Action:** Prefer tracking `origin/main` for Gentech fork; periodically sync `upstream/main → origin/main → local`.

---

## Pattern: Hermes Agent Itself Installed via Git but `hermes update` Says "Already Latest"

**Symptom:** Git shows newer commits on remote but `hermes update` does nothing.

**Cause:** The `hermes` binary is installed in `/usr/local/bin/` from a Python venv; the git repo at `/usr/local/lib/hermes-agent/` is not auto-updated by `hermes update`. The CLI update checks PyPI, not git.

**Fix:**
```bash
# If you want latest git HEAD (bleeding edge):
cd /usr/local/lib/hermes-agent
git fetch origin
git checkout main          # or specific tag
git pull origin main
# Reinstall into venv
pip install -e . --force-reinstall --no-deps
```

**Action:** Use `hermes update` for stable releases; manual git pull for dev installs.

---

## Pattern: `hermes skills update` Reports "No updates" but Git Shows Ahead

**Symptom:** Skill's git repo is ahead of remote (local commits not pushed) and `hermes skills update` does nothing.

**Cause:** `hermes skills update` pulls from the remote but does not push local commits. If local has unpushed work, it's considered "modified" not "out of date".

**Fix:**
```bash
# Check push vs pull divergence
git -C /root/skills/<skill> status
# If ahead:
git -C /root/skills/<skill> log --oneline origin/main..HEAD
# Push to remote if you own it:
git -C /root/skills/<skill> push origin main
# Or reset to remote if local work should be discarded:
git -C /root/skills/<skill> reset --hard origin/main
```

**Action:** For DMOB-owned skill repos, push local commits at least daily. For third-party skills, keep local in sync (no local commits).

---

## Pattern: Awesome-List Fetch Blocked by Rate Limit

**Symptom:** `requests.get('https://raw.githubusercontent.com/...')` returns 403 or hangs.

**Cause:** GitHub enforces rate limits on unauthenticated requests (~60/hr).

**Fix:**
```bash
# Use a GitHub token if available
export GITHUB_TOKEN="ghp_..."
curl -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3.raw" \
  https://raw.githubusercontent.com/0xNyk/awesome-hermes-agent/main/README.md

# Cache aggressively (once per day)
CACHE="/root/skills/.awesome_hermes_cache.md"
if [ $(find "$CACHE" -mmin +1440 2>/dev/null) ]; then
  # refresh
  curl -s -o "$CACHE" <url>
fi
```

**Action:** Set up a GitHub personal access token (no scopes needed for public repos) and store in `~/.hermes/.env` as `GITHUB_TOKEN`. Update `skill-audit-operations` to use it.

---

## Pattern: Vault Lockfile Prevents Git Status

**Symptom:** `git status` in vault fails with "fatal: ... lockfile exists".

**Cause:** Another process (Obsidian sync, backup, or agent) holds a git index or working tree lock.

**Fix:**
```bash
# Remove stale lock (ONLY if no other git process is running)
rm -f /root/vaults/gentech/.git/index.lock
rm -f /root/vaults/gentech/.git/HEAD.lock
# Verify
git -C /root/vaults/gentech status
```

**Action:** `skill-audit-operations` uses `git fetch --quiet` (read-only) only; never `git pull` or `git merge`. If lock detected, skip vault audit and flag warning.

---

## Pattern: Skill Directory Exists but SKILL.md Missing

**Symptom:** `find /root/skills -name SKILL.md` returns nothing for a skill name.

**Cause:** The skill directory was created but the SKILL.md frontmatter was never written (incomplete install).

**Fix:**
```bash
# Generate minimal SKILL.md stub
cat > /root/skills/<category>/<skill>/SKILL.md <<EOF
---
name: $skill
description: TBD — imported from <source>
version: 0.0.0
author: Unknown
license: MIT
---
# $skill
TODO: complete skill documentation
EOF
```

**Action:** Audit script should flag any skill directory without SKILL.md as `BROKEN`.

---

## Safe Update Sequence

For any out-of-date skill:

1. **Backup current version:**
   ```bash
   cp -r /root/skills/<cat>/<skill> /root/skills/<cat>/<skill>.bak-$(date +%Y%m%d)
   ```
2. **Pull latest:**
   ```bash
   git -C /root/skills/<cat>/<skill> pull --ff-only
   ```
3. **Verify SKILL.md present and valid frontmatter:**
   ```bash
   grep '^---' /root/skills/<cat>/<skill>/SKILL.md | head -2
   ```
4. **Reload skill in running Hermes (if interactive):**
   ```bash
   # In Hermes session: /reload-mcp or /reset (for built-ins use hermes restart)
   ```
5. **If breakage:** restore from `.bak` and file an issue in the skill repo.

---

## Version Pinning (For Stability)

If a skill update breaks workflows, pin the version:

```bash
# Freeze at current commit
git -C /root/skills/<cat>/<skill> checkout -b pinned-$(date +%Y%m%d)
# Mark as pinned in skill metadata (edit SKILL.md):
#   pinned: true
#   pinned_commit: abc123
```

Never auto-update pinned skills. Audit script should report them as `PINNED`.
