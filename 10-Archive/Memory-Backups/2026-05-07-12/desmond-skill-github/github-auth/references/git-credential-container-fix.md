# Git Credential Store in Containerized Environments

## Error Pattern

```
fatal: could not read Username for 'https://github.com': No such device or address
```

This occurs when:
1. Git is configured with `credential.helper=store`
2. The `$HOME` environment variable points to a **non-existent** or **non-standard** directory
3. Git tries to read `$HOME/.git-credentials` but fails, then has no TTY to prompt
4. The error surfaces even though credentials exist elsewhere (e.g. `/root/.git-credentials`)

## Diagnostic Checklist

```bash
# 1. Check what HOME git sees
echo "HOME=$HOME"
ls -la "$HOME/.git-credentials" 2>/dev/null || echo "❌ No .git-credentials at $HOME"

# 2. Check actual credential location
ls -la /root/.git-credentials 2>/dev/null && echo "✅ Found at /root"

# 3. Test credential fill manually
git credential fill <<EOF
protocol=https
host=github.com
EOF

# 4. Check git's credential helper config
git config --get credential.helper  # should be 'store'
```

## Fixes (in order of preference)

### Fix 1: Set HOME Correctly Before Running Git (one-time per session)

```bash
export HOME=/root
git push origin main
```

### Fix 2: Pre-approve Credentials (best for scripts)

Run once per shell session before git operations:

```bash
git credential approve <<EOF
protocol=https
host=github.com
username=ProtoJay4789
password=${GITHUB_PAT}
EOF

# Now git push will work in this session
git push origin main
```

### Fix 3: Use the `pre-seed-credentials.sh` script (recommended for automation)

```bash
# Source it to pre-approve in current shell
source skills/github/github-auth/scripts/pre-seed-credentials.sh "$GITHUB_PAT"

# Or let it read GITHUB_PAT from env
export GITHUB_PAT="ghp_..."
source skills/github/github-auth/scripts/pre-seed-credentials.sh
```

### Fix 4: Write credentials to the correct HOME location

```bash
# If you want persistent store, ensure HOME points to a writable dir with .git-credentials
mkdir -p "$HOME"
cat > "$HOME/.git-credentials" <<EOF
https://${GITHUB_PAT}@github.com
EOF
chmod 600 "$HOME/.git-credentials"
```

## Why This Happens in Hermes

Hermes agents run with `HOME` set to their profile home directory:
```
Desmond: HOME=/root/.hermes/profiles/desmond/home
YoYo:     HOME=/root/.hermes/profiles/yoyo/home
```

But the **system git credentials** are stored at `/root/.git-credentials` (root's home). When git runs under the agent's HOME, it looks in the wrong place and fails.

The `pre-seed-credentials.sh` script sidesteps the file lookup entirely by injecting credentials directly into git's in-memory credential cache via `git credential approve`.

## Related References
- Skill: `github-auth` — full auth setup methods (HTTPS, SSH, gh CLI)
- Script: `scripts/pre-seed-credentials.sh` — reusable fix
- Vault: `00-HQ/config/defi-lp-config.env` — stores GITHUB_PAT for backup jobs
