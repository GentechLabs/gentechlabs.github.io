# Hermes Skill Storage Architecture

## Overview

Hermes Agent skills are not stored in a single location. They exist across multiple layers depending on origin, installation method, and profile configuration.

## Layer Map

### 1. Core Bundled Skills
**Path:** `/usr/local/lib/hermes-agent/skills/` (or wherever the Python package installs)  
**Source:** Part of the Hermes Agent core repository  
**Update mechanism:** `hermes update` (core version bump)  
**Characteristics:** Read-only, version-locked with agent, includes all 40+ built-in skills

### 2. Bundled Skill Repository
**Path:** `/root/skills/` (organized by category)  
**Source:** Community skill hub / bundled manifest  
**Update mechanism:** Git-based (`git fetch && git merge` inside each skill dir OR `hermes skills update`)  
**Characteristics:**
- 79 skill modules as of 2026-05-03
- Contains `base/`, `solana/`, `github/`, `devops/`, `research/`, `software-development/`, etc.
- Each skill directory may be a standalone git repo (some have `.git`, some don't)
- `/root/skills/.bundled_manifest` maps skill names → commit hashes

### 3. Profile-Specific Installed Skills
**Path:** `~/.hermes/profiles/<profile>/skills/` (per-profile)  
**Source:** `hermes skills install <repo>` or manual copy  
**Update mechanism:** `hermes skills update` (hub-based) or manual file replacement  
**Characteristics:**
- Profile isolation: each profile has independent skill set
- DMOB's profile is NOT at `~/.hermes/profiles/dmob/` in this environment (it's `/root/.hermes/profiles/dmob/home/.hermes/profiles/dmob/` — nested due to sandboxing)
- Skills here may be symlinks or copies of `/root/skills/` entries

### 4. Vault-Coupled Skills
**Path:** `/root/vaults/gentech/` (mirrored via Obsidian sync)  
**Source:** Skill SKILL.md files scattered across vault (e.g., `02-Labs/`, `10-Archive/Memory-Backups/`)  
**Update mechanism:** Manual edit + `git commit`; Obsidian sync pushes to other clients  
**Characteristics:**
- Skills appear in vault as part of documentation/notes
- Memory backups (`10-Archive/Memory-Backups/`) contain **full skill package copies** (entire skill install directories with artifacts)
- Use `ob sync` to propagate changes between vault and other Hermes instances

---

## Discovery Commands

```bash
# List all installed skills (Hermes's view)
hermes skills list

# Find all SKILL.md on system (raw file scan)
find /root -name SKILL.md -not -path '*/node_modules/*' 2>/dev/null

# List git-tracked skill source repos
find /root/skills -name '.git' -type d -exec dirname {} \; | while read d; do
  echo "Git skill: $d"
  git -C "$d" remote -v
done

# Check bundled manifest (skill IDs + hashes)
cat /root/skills/.bundled_manifest

# Profile skill directory (where Hermes actually loads from)
HERMES_HOME=$(hermes config path 2>/dev/null | head -1)
echo "HERMES_HOME=$HERMES_HOME"
ls -la "$HERMES_HOME/skills/" 2>/dev/null || echo "No per-profile skill dir"
```

---

## Common Pitfalls

### Pitfall: `hermes skills list` shows 98 skills but `/root/skills/` has only 79
**Explanation:** Built-in skills count toward the total but are not under `/root/skills/`. The 19-skill gap is the built-in set.

### Pitfall: Skill shows as "local" source type in `hermes skills list`
**Explanation:** "local" means installed from filesystem path (not from a skill hub). It may still be git-tracked under `/root/skills/` but Hermes doesn't track the remote URL — only the local install source.

### Pitfall: Profile skill directory is nested under `/home/` inside the profile
**Cause:** Hermes profile home directory is set to `~/.hermes/profiles/dmob/home/` and inside that home, skills install to `~/.hermes/profiles/dmob/home/.hermes/profiles/dmob/skills/`. The double `profiles/dmob` is expected in sandboxed environments.
**Fix:** Always use `hermes skills list` to get the authoritative view; don't assume path conventions.

### Pitfall: Skill updates via `hermes skills update` do nothing
**Cause:** The skill was installed from a local path or a git repo without a tracked remote. `hermes skills update` only works for hub-installed skills.
**Fix:** Manually `git -C /root/skills/<category>/<skill> pull` or use `skill-audit-operations` to detect and update individually.

---

## AAE Design Principle

For Gentech Labs, prefer **version-controlled skills** (git-tracked) over local-only installs. Store DMOB-built skills in `/root/skills/labs/` or vault `02-Labs/Skills/` with a dedicated git remote. This ensures auditability, rollback, and multi-agent consistency.
