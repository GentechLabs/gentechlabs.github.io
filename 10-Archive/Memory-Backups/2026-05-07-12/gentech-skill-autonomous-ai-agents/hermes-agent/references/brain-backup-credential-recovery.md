# Brain Backup Git Credential Recovery — Reference

## Quick Diagnosis

```bash
# From each brain backup repo
cd /root/hermes-brain-backup   # or /root/repos/hermes-brain
git status --porcelain         # check for uncommitted changes
git log --oneline -5
git rev-list --left-right --count HEAD...origin/main   # shows ahead/behind
```

**Signs of credential failure:**
- `git push` → `fatal: could not read Username for 'https://github.com': No such device or address`
- `git push` → `remote: Invalid username or token`
- `~/.git-credentials` contains `***` (redacted placeholder)
- Backup cron logs show commits but no push confirmation

## Recovery: HTTPS Credentials (Profile-Specific Store)

```bash
# 1. Find a working GITHUB_PAT in vault .env files
VAULT_ENV="/root/vaults/gentech/.env"
GITHUB_PAT=$(grep 'GITHUB_PAT' "$VAULT_ENV" | head -1 | cut -d'=' -f2)

# 2. Write to the profile-specific credentials file
# Gentech HOME is /root/.hermes/profiles/gentech/home
PROFILE_HOME="/root/.hermes/profiles/gentech/home"
CRED_FILE="${PROFILE_HOME}/.git-credentials"

echo "https://ProtoJay4789:${GITHUB_PAT}@github.com" > "$CRED_FILE"
chmod 600 "$CRED_FILE"

# 3. Verify credential helper
git config credential.helper   # should output 'store'
git credential fill <<EOF
protocol=https
host=github.com
EOF
# Expected output includes: username=ProtoJay4789\npassword=<token>

# 4. Ensure remote is HTTPS
git remote set-url origin https://github.com/Gentech-Labs/hermes-brain-backup.git

# 5. Push
git push origin main --verbose
```

## Recovery: SSH Deploy Key (Service Account Pattern)

```bash
# 1. Generate SSH key (if not exists)
ssh-keygen -t ed25519 -C "hermes-brain-backup@gentechlabs.io" \
  -f /root/.ssh/hermes-brain-backup -N ""

chmod 600 /root/.ssh/hermes-brain-backup
chmod 644 /root/.ssh/hermes-brain-backup.pub

# 2. Configure SSH to always use this key for github.com
cat >> /root/.ssh/config <<'EOF'
Host github.com
  IdentityFile /root/.ssh/hermes-brain-backup
  IdentitiesOnly yes
EOF
chmod 600 /root/.ssh/config

# 3. Add public key as Deploy Key in GitHub:
#    Repo → Settings → Deploy keys → Add deploy key
#    Title: "Hermes Brain Backup Server"
#    Key: (paste contents of /root/.ssh/hermes-brain-backup.pub)
#    ✅ Allow write access

# 4. Switch remote to SSH
git remote set-url origin git@github.com:Gentech-Labs/hermes-brain-backup.git

# 5. Test connection
ssh -i /root/.ssh/hermes-brain-backup -o BatchMode=yes \
  -o ConnectTimeout=5 git@github.com
# Expected: "successfully authenticated" or "Warning: Permanently added 'github.com' to known_hosts"

# 6. Push
git push origin main
```

## Multi-Repo Coordination

Both brain backup repos need independent credential recovery:

```bash
for REPO in /root/hermes-brain-backup /root/repos/hermes-brain; do
  echo "=== Fixing $REPO ==="
  cd "$REPO"
  
  # Ensure HTTPS remote and working .git-credentials
  git remote set-url origin https://github.com/Gentech-Labs/$(basename "$REPO").git
  
  # Copy Gentech credentials (same for both repos)
  cp /root/.hermes/profiles/gentech/home/.git-credentials .
  git config credential.helper store
  
  # Push
  git push origin main && echo "✅ $REPO synced" || echo "❌ $REPO failed"
done
```

## Verification

```bash
# Check sync status across all brain repos
for REPO in /root/hermes-brain-backup /root/repos/hermes-brain; do
  echo "=== $(basename "$REPO") ==="
  cd "$REPO"
  git rev-list --left-right --count HEAD...origin/main
  # Output should be: "0       0" (fully synced)
done

# Verify backup cron is working
hermes cron list --profile gentech | grep -i brain
# Check last_run_at is recent
```

## Common Pitfalls

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `credential fill` returns nothing | Wrong HOME for `.git-credentials` | Place file at `$PROFILE_HOME/.git-credentials`, not `~/.git-credentials` |
| `git push` asks for username | `.git-credentials` not formatted correctly | Use `https://user:token@github.com` single line format |
| SSH `Permission denied (publickey)` | Deploy key not added to GitHub repo | Add `.pub` key as Deploy Key in repo settings with Write access |
| HTTPS push → `Password authentication not supported` | Using OAuth token as password | GitHub requires PAT or SSH; `gh` OAuth tokens won't work for Git |
| Push succeeds but GitHub doesn't update | Pushing to wrong remote URL | Verify `git remote -v` shows correct repo |
| Backup keeps falling behind | Cron job not running or failing | Check `hermes cron list --profile gentech` and gateway logs |

## Source of Truth

- Vault `.env` files contain working `GITHUB_PAT` used by Hermes for GitHub integration
- Profile-specific gitconfig at `/root/.hermes/profiles/<profile>/home/.gitconfig` sets `credential.helper=store`
- Gentech uses `/root/.hermes/profiles/gentech/home/` as HOME for all Gentech Hermes operations
