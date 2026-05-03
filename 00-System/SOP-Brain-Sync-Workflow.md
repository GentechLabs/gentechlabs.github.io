# 🧠 Brain Sync Workflow (Obsidian Vault ↔ GitHub)

**Applies to:** GenTech Shared Brain  
**Owner:** DMOB (Labs) + Gentech (HQ)  
**Created:** 2026-05-03  
**Status:** ACTIVE  
**Related:** `01-Agency/brain-backup.md`, `00-System/GenTech-Work-Processes-v2.2.md`

---

## 📋 Overview

The GenTech brain is an **Obsidian markdown vault** (`/root/vaults/gentech/`) automatically backed up to **GitHub** via git commits + manual pushes.

**Two components:**
1. **Obsidian Vault** — primary source of truth, edited in real-time
2. **GitHub Remote** — cold backup + external sync (disaster recovery)

---

## 🗺️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT                          │
│            (/root/vaults/gentech/)                        │
│  • Atomic markdown notes (MOCs + topic notes)             │
│  • Daily edits, in-place updates                          │
│  • Local git repo (commits frequent, pushes sporadic)    │
└────────────────────────┬────────────────────────────────────┘
                         │
                `git add/commit` (frequent)
                         │
            [Local git history builds up]
                         │
                `git push` (manual/cron)
                         │
┌─────────────────────────────────────────────────────────────┐
│                GITHUB REMOTE (agent-escrow)               │
│    git@github.com:ProtoJay4789/agent-escrow.git           │
│  • Mirror of vault state                                   │
│  • Disaster recovery copy                                   │
│  • Historical snapshot on every push                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔁 Sync Workflow

### 1. Local Commit Flow (automatic, always ON)

```
Edit file in Obsidian
         ↓
   Save (Obsidian auto-saves)
         ↓
   `git add <changed files>`
         ↓
   `git commit -m "<descriptive message>"`
```

**Convention:** Commit messages follow
```
<type>(<scope>): <subject>

Types: feat|fix|docs|chore|refactor|audit|emergency
Scope: vault|labs|aae|security|strategies|notes
Example: fix(lp-monitor): resolve NameError crash + add Rule 6
```

**Frequency:** On every meaningful edit (when file closes, every ~10 mins if auto-commit script is running).

### 2. Push to GitHub (manual OR cron)

```
git push origin main
```

**Status:** May fail if:
- Node.js v22 not available (obsidian-headless-sync requires it)
- SSH key not loaded / GitHub auth expired
- Remote has diverged (rebase/resolution needed)
- Network interruption

**Current approach:** Manual `git push` until stable, then cron.

---

## 🚨 Monitoring & Detection

### Detect Unpushed Commits

```bash
# Check how many commits local is ahead of remote
git log --oneline origin/main..main

# Quick count
git rev-list --count origin/main..main
```

**Alert threshold:** > 10 commits behind → escalate to DMOB.

### Check Latest Push Age

```bash
# Get timestamp of last successful push
git log -1 --format='%ci' origin/main

# Compare to now
# > 24 hours old = STALE
```

---

## 🛠️ Maintenance Procedures

### A. Daily Health Check (DMOB)

**When:** Start of Labs session (~9am UTC)  
**Command:**
```bash
cd /root/vaults/gentech
ahead=$(git rev-list --count origin/main..main)
last_push=$(git log -1 --format='%s' origin/main 2>/dev/null || echo "never")

if [ "$ahead" -gt 10 ]; then
  echo "⚠️  VAULT IS $ahead COMMITS AHEAD OF GITHUB — PUSH NEEDED"
  # Send alert to Green Room or Mess Hall
elif [ -z "$last_push" ]; then
  echo "❌ GITHUB CONNECTION FAILING — CAN'T READ REMOTE"
else
  echo "✅ Brain sync healthy (local: +$ahead)"
fi
```

### B. Emergency Push (when behind)

**Step-by-step:**
1. Verify Node.js available for any required sync scripts:
   ```bash
   node --version  # must be v22+
   ```
2. Check remote status:
   ```bash
   git fetch origin --dry-run
   ```
3. If behind, fast-forward only (no merge conflicts expected):
   ```bash
   git push origin main
   ```
4. Verify push succeeded:
   ```bash
   git ls-remote --heads origin main
   ```
5. Report in Green Room:
   > "✅ Brain backup synced — local now at `$(git rev-parse --short HEAD)`"

### C. Recovery (if GitHub repo corrupted)

1. Clone fresh from vault:
   ```bash
   cd ~
   rm -rf agent-escrow-recovery
   git clone git@github.com:ProtoJay4789/agent-escrow.git agent-escrow-recovery
   ```
2. Compare file counts:
   ```bash
   find /root/vaults/gentech -type f | wc -l
   find ~/agent-escrow-recovery -type f | wc -l
   ```
3. If mismatch, pull vault → overwrite remote (force push):
   ```bash
   git -C /root/vaults/gentech push --force origin main
   ```

---

## 📜 Scheduled Cron (future)

Once stable, schedule **daily push at 4am UTC**:

```bash
# crontab -e
0 4 * * * cd /root/vaults/gentech && git add -A && git commit -m "auto: daily brain backup $(date +\%Y-\%m-\%d)" && git push origin main 2>&1 | tee -a /var/log/brain-sync.log
```

**Log monitoring:** `/var/log/brain-sync.log` → alert on failures.

---

## 🧩 Related Scripts & Paths

| Purpose | Path |
|---------|------|
| Vault location | `/root/vaults/gentech/` |
| Vault git config | `/root/vaults/gentech/.git/config` |
| GitHub remote URL | `git@github.com:ProtoJay4789/agent-escrow.git` |
| Obsidian vault config | `/root/vaults/gentech/.obsidian/` |
| Obsidian sync settings | `~/Library/Application Support/obsidian/` (if GUI sync enabled) |
| Sync log (if cron) | `/var/log/brain-sync.log` |

---

## 🚫 Pitfalls & Gotchas

### 1. Permissions Denied (SSH)
**Symptom:** `git@github.com: Permission denied (publickey).`  
**Fix:** Ensure SSH agent has key:
```bash
ssh-add -l  # list loaded keys
ssh-add ~/.ssh/id_ed25519  # or correct key
```
**Key file:** Usually `~/.ssh/id_ed25519` or `~/.ssh/github_rsa`.

### 2. Node.js v22 Requirement
**Symptom:** obsidian-headless-sync or other scripts fail with "Node not found"  
**Fix:**
```bash
# Check
node --version  # must be v22.x

# Install if missing (via nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22
```

### 3. Merge Conflicts on Remote
**Symptom:** `! [rejected] main -> main (fetch first)`  
**Fix:** Rebase local onto remote first:
```bash
git fetch origin
git rebase origin/main
# resolve conflicts if any
git push origin main
```

### 4. Large Files Accidentally Added
**Symptom:** Push rejected due to file > 100MB  
**Fix:** Remove from git history:
```bash
git rm --cached <large-file>
git commit -m "remove large file"
git push origin main
```
**Add to `.gitignore`** to prevent recurrence.

---

## ✅ Checklist (Before Leaving Vault Unattended)

- [ ] No uncommitted changes: `git status` shows clean working tree
- [ ] Local ≤ 10 commits ahead of remote: `git rev-list --count origin/main..main`
- [ ] Last push < 24h old: `git log -1 --format='%ci' origin/main`
- [ ] No `.gitignore` regressions (no large files staged)
- [ ] SSH agent running: `ssh-add -l` shows key

---

## 📊 Metrics & Alerts

| Metric | Target | Alert |
|--------|--------|-------|
| Push lag (commits) | 0–3 | >10 commits behind |
| Push lag (time) | <24h | >48h stale |
| Push success rate | 100% | Any failure |
| Remote divergence | 0 conflicts | Merge conflict detected |

**Alert destinations:** Green Room → DMOB → YoYo (if persistent >48h)

---

## 🔄 Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-05-03 | 1.0 | Initial workflow documented — covers vault→GitHub sync, monitoring, recovery |
