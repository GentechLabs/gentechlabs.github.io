---
name: github-auth
description: "GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Authentication, Git, gh-cli, SSH, Setup]
    related_skills: [github-pr-workflow, github-code-review, github-issues, github-repo-management]
---

# GitHub Authentication Setup

This skill sets up authentication so the agent can work with GitHub repositories, PRs, issues, and CI. It covers two paths:

- **`git` (always available)** — uses HTTPS personal access tokens or SSH keys
- **`gh` CLI (if installed)** — richer GitHub API access with a simpler auth flow

## Phase 0: Diagnostic Audit (Run Before Any Setup)

When asked to work with GitHub repositories, first diagnose the current state. This prevents choosing the wrong auth method and uncovers mixed remote configurations.

### Full System Audit

```bash
# 0.1 Check SSH infrastructure
echo "=== SSH KEYS ==="
ls -la ~/.ssh/id_* 2>/dev/null || echo "❌ No SSH keys found"
ssh-add -L 2>/dev/null || echo "⚠️  SSH agent not running or no keys loaded"
if [ -f ~/.ssh/known_hosts ]; then
  echo "✓ known_hosts present ($(wc -l < ~/.ssh/known_hosts) entries)"
fi

# 0.2 Check git remote auth types across relevant repos
echo -e "\n=== GIT REMOTE AUDIT ==="
repos=(
  "/root/vaults/gentech"
  "/root/vaults/gentech/02-Labs/tech-payment-router"
  "/root/vaults/gentech/03-Projects/BirdeyeBIP"
  "/root/vaults/gentech/03-Projects/hermes-kanban"
)
for repo in "${repos[@]}"; do
  if [ -d "$repo/.git" ]; then
    url=$(git -C "$repo" config --get remote.origin.url 2>/dev/null || echo "NO_REMOTE")
    name=$(basename "$repo")
    if [[ $url == git@* ]]; then
      echo "  $name: SSH → $url"
    elif [[ $url == https://* ]]; then
      echo "  $name: HTTPS → $url"
    else
      echo "  $name: $url"
    fi
  fi
done

# 0.3 Test actual SSH access (will fail if keys missing)
echo -e "\n=== SSH ACCESS TEST ==="
git -C /root/vaults/gentech ls-remote --heads origin 2>&1 | head -1

# 0.4 Check gh CLI auth status
echo -e "\n=== GH CLI STATUS ==="
if command -v gh &>/dev/null; then
  gh auth status || echo "❌ gh not authenticated"
else
  echo "❌ gh CLI not installed"
fi

# 0.5 Check for loaded PAT in environment vs .env
echo -e "\n=== TOKEN AVAILABILITY ==="
if [ -n "$GITHUB_TOKEN" ] || [ -n "$GITHUB_PAT" ]; then
  echo "✓ Token found in shell environment"
else
  echo "⚠️  No token in shell env"
  if [ -f /root/vaults/gentech/.env ]; then
    if grep -qE '^GITHUB_(TOKEN|PAT)=' /root/vaults/gentech/.env; then
      echo "  Token found in vault .env (not loaded into shell)"
    fi
  fi
fi

# 0.6 Check git user identity
echo -e "\n=== GIT IDENTITY ==="
git config --global user.name 2>/dev/null || echo "❌ No global user.name"
git config --global user.email 2>/dev/null || echo "❌ No global user.email"
```

### Interpreting Results

| Finding | Meaning | Recommended Path |
|---------|---------|-----------------|
| SSH keys exist + SSH remotes configured | Ready to use SSH | No action needed |
| No SSH keys + SSH remotes configured | SSH broken | Either generate keys OR convert remotes to HTTPS |
| HTTPS remotes + PAT in .env (unloaded) | Token available but inactive | Load `.env` or use `gh auth login` |
| HTTPS remotes + no token | No auth configured | Set up PAT or gh CLI |
| Mixed SSH and HTTPS remotes | Inconsistent state | Standardize to one method (prefer SSH for Gentech) |
| `gh auth status` shows authenticated | gh CLI ready | Use `gh` for all GitHub operations |

### Decision Matrix

**If you have SSH keys and SSH remotes:** → Use SSH (no token expiry, clean)

**If you have no SSH keys and repos use HTTPS:** → Load existing PAT from `.env` or run `gh auth login` with token

**If repos have no remote at all:** → Use `github-repo-management` skill to add origin before any push

**If multi-account (different GitHub users across repos):**
  - SSH: Add the same public key to all relevant GitHub accounts
  - HTTPS: Use credential helper with per-host credentials or embed token per-repo

### Quick Fix: Convert HTTPS → SSH (if SSH keys are available)

```bash
git remote set-url origin git@github.com:$(git remote get-url origin | sed 's|https://github.com/||;s|.git$||').git
```

### Quick Fix: Load PAT from .env into shell

```bash
# Source the vault .env (careful: exposes secrets to shell history; use only in secure session)
export $(grep -v '^#' /root/vaults/gentech/.env | xargs -d '\n' | grep -E 'GITHUB_(TOKEN|PAT)')
# Or use gh token-based login
echo "$GITHUB_PAT" | gh auth login --with-token
```

---

## Phase 0: Diagnostic Audit (Run Before Any Setup)

**Quick one-liner:** Use the bundled audit script to get a full picture in seconds.

```bash
# From anywhere, run the skill's audit helper
# (installed at ~/.hermes/profiles/yoyo/skills/github/github-auth/scripts/gh-audit.sh)
~/skill_scripts/github-auth/gh-audit.sh

# Or call via skill invoker if available
skill_run github-audit
```

The script checks:
- SSH key presence and agent loading
- Git remote auth types (SSH vs HTTPS) per-repo
- Actual SSH access success/failure
- `gh` CLI authentication status
- Token availability (shell env vs .env file)
- Git user identity configuration
- Repo status (missing remotes, uncommitted work)

**When to run:** At the start of any GitHub-related task — cloning, pushing, creating PRs, or deploying.

---

## Full System Audit (Manual Method)

If the script is unavailable, run these commands manually:

```bash

---

## Method 1: Git-Only Authentication (No gh, No sudo)

This works on any machine with `git` installed. No root access needed.

### Option A: HTTPS with Personal Access Token (Recommended)

This is the most portable method — works everywhere, no SSH config needed.

**Step 1: Create a personal access token**

Tell the user to go to: **https://github.com/settings/tokens**

- Click "Generate new token (classic)"
- Give it a name like "hermes-agent"
- Select scopes:
  - `repo` (full repository access — read, write, push, PRs)
  - `workflow` (trigger and manage GitHub Actions)
  - `read:org` (if working with organization repos)
- Set expiration (90 days is a good default)
- Copy the token — it won't be shown again

**Step 2: Configure git to store the token**

```bash
# Set up the credential helper to cache credentials
# "store" saves to ~/.git-credentials in plaintext (simple, persistent)
git config --global credential.helper store

# Now do a test operation that triggers auth — git will prompt for credentials
# Username: <their-github-username>
# Password: <paste the personal access token, NOT their GitHub password>
git ls-remote https://github.com/<their-username>/<any-repo>.git
```

After entering credentials once, they're saved and reused for all future operations.

**Alternative: cache helper (credentials expire from memory)**

```bash
# Cache in memory for 8 hours (28800 seconds) instead of saving to disk
git config --global credential.helper 'cache --timeout=28800'
```

**Alternative: set the token directly in the remote URL (per-repo)**

```bash
# Embed token in the remote URL (avoids credential prompts entirely)
git remote set-url origin https://<username>:<token>@github.com/<owner>/<repo>.git
```

**Step 3: Configure git identity**

```bash
# Required for commits — set name and email
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

**Step 4: Verify**

```bash
# Test push access (this should work without any prompts now)
git ls-remote https://github.com/<their-username>/<any-repo>.git

# Verify identity
git config --global user.name
git config --global user.email
```

### Option B: SSH Key Authentication

Good for users who prefer SSH or already have keys set up.

**Step 1: Check for existing SSH keys**

```bash
ls -la ~/.ssh/id_*.pub 2>/dev/null || echo "No SSH keys found"
```

**Step 2: Generate a key if needed**

```bash
# Generate an ed25519 key (modern, secure, fast)
ssh-keygen -t ed25519 -C "their-email@example.com" -f ~/.ssh/id_ed25519 -N ""

# Display the public key for them to add to GitHub
cat ~/.ssh/id_ed25519.pub
```

Tell the user to add the public key at: **https://github.com/settings/keys**
- Click "New SSH key"
- Paste the public key content
- Give it a title like "hermes-agent-<machine-name>"

**Step 3: Test the connection**

```bash
ssh -T git@github.com
# Expected: "Hi <username>! You've successfully authenticated..."
```

**Step 4: Configure git to use SSH for GitHub**

```bash
# Rewrite HTTPS GitHub URLs to SSH automatically
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

**Step 5: Configure git identity**

```bash
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

---

## Method 2: gh CLI Authentication

If `gh` is installed, it handles both API access and git credentials in one step.

### Interactive Browser Login (Desktop)

```bash
gh auth login
# Select: GitHub.com
# Select: HTTPS
# Authenticate via browser
```

### Token-Based Login (Headless / SSH Servers)

```bash
echo "<THEIR_TOKEN>" | gh auth login --with-token

# Set up git credentials through gh
gh auth setup-git
```

### Verify

```bash
gh auth status
```

---

## Using the GitHub API Without gh

When `gh` is not available, you can still access the full GitHub API using `curl` with a personal access token. This is how the other GitHub skills implement their fallbacks.

### Setting the Token for API Calls

```bash
# Option 1: Export as env var (preferred — keeps it out of commands)
export GITHUB_TOKEN="<token>"

# Then use in curl calls:
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

### Extracting the Token from Git Credentials

If git credentials are already configured (via credential.helper store), the token can be extracted:

```bash
# Read from git credential store
grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|'
```

### Helper: Detect Auth Method

Use this pattern at the start of any GitHub workflow:

```bash
# Try gh first, fall back to git + curl
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  echo "AUTH_METHOD=gh"
elif [ -n "$GITHUB_TOKEN" ]; then
  echo "AUTH_METHOD=curl"
elif [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
  export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
  echo "AUTH_METHOD=curl"
elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
  export GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
  echo "AUTH_METHOD=curl"
else
  echo "AUTH_METHOD=none"
  echo "Need to set up authentication first"
fi
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `git push` asks for password | GitHub disabled password auth. Use a personal access token as the password, or switch to SSH |
| `remote: Permission to X denied` | Token may lack `repo` scope — regenerate with correct scopes |
| `fatal: Authentication failed` | Cached credentials may be stale — run `git credential reject` then re-authenticate |
| `ssh: connect to host github.com port 22: Connection refused` | Try SSH over HTTPS port: add `Host github.com` with `Port 443` and `Hostname ssh.github.com` to `~/.ssh/config` |
| Credentials not persisting | Check `git config --global credential.helper` — must be `store` or `cache` |
| Multiple GitHub accounts | Use SSH with different keys per host alias in `~/.ssh/config`, or per-repo credential URLs |
| `gh: command not found` + no sudo | Use git-only Method 1 above — no installation needed |
