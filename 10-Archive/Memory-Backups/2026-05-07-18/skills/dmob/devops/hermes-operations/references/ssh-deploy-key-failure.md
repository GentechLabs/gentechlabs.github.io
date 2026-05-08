# SSH Deploy Key Failure — Diagnostic Flow

## Context
The brain backup repo (`Gentech-Labs/hermes-brain-backup`) uses an SSH deploy key at `/root/.ssh/hermes-brain-backup`. When this key is revoked or removed from GitHub, push fails with `Permission denied (publickey)` but the backup script still exits 0.

## Key Identity
- **File:** `/root/.ssh/hermes-brain-backup` (private), `/root/.ssh/hermes-brain-backup.pub` (public)
- **Type:** ed25519
- **Fingerprint:** `SHA256:RzSh2agGZrCQGkV8YCo1iRh2doshAPxlgX0uHBmkYkk`
- **Label:** `hermes-brain-backup@gentechlabs.io`
- **SSH config** (`~/.ssh/config`): Forces `IdentitiesOnly yes` for github.com

## Diagnostic Sequence (when push fails)

### Step 1: Check if key exists
```bash
ls -la /root/.ssh/hermes-brain-backup*
ssh-keygen -l -f /root/.ssh/hermes-brain-backup
```

### Step 2: Try ssh-agent
```bash
eval $(ssh-agent -s)
ssh-add /root/.ssh/hermes-brain-backup
cd /root/hermes-brain-backup && git push origin main
```

### Step 3: Verbose SSH test (determines if key is accepted)
```bash
ssh -vT -i /root/.ssh/hermes-brain-backup git@github.com 2>&1 | tail -30
```
**Look for:** "Offering public key" → if followed by "Authentications that can continue: publickey" again, key is rejected. GitHub does not recognize this key.

### Step 4: Try HTTPS fallback
```bash
source /root/vaults/gentech/00-HQ/config/github-token.env
cd /root/hermes-brain-backup
git remote set-url origin "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/Gentech-Labs/hermes-brain-backup.git"
git push origin main
git remote set-url origin git@github.com:Gentech-Labs/hermes-brain-backup.git  # restore
```
**Note:** If the GitHub token is expired/invalid, HTTPS also fails. This is a separate issue from the SSH key.

### Step 5: Report to Gentech
The deploy key needs to be re-added at: **https://github.com/Gentech-Labs/hermes-brain-backup/settings/keys**
- Click "Add deploy key"
- Paste the contents of `/root/.ssh/hermes-brain-backup.pub`
- Check "Allow write access"

## Last Known Working
- **May 1, 2026** — last successful push per `backup.log`
- **May 2, 2026** — push started failing (HTTPS error: `could not read Username`)

## Common Causes
1. **Key removed from GitHub** — deploy keys are per-repo, not per-account
2. **Repo recreated** — new repo won't have old deploy keys
3. **GitHub security rotation** — rarely, GitHub revokes keys for policy compliance
4. **Key file permissions** — should be `600` (checked automatically by SSH)

## The backup-brain.py Gotcha
The script (`/root/hermes-brain-backup/scripts/backup-brain.py`) does this:
1. Updates memory snapshot → ✅
2. Updates skills index → ✅
3. Tries `git push` → ⚠️ may fail
4. Reports "✅ Backup complete" regardless of push status

**Always check `/root/hermes-brain-backup/backup.log`** after cron runs to verify push succeeded.
