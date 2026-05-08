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

## Detection Flow

When a user asks you to work with GitHub, run this check first:

```bash
# Check what's available
git --version
gh --version 2>/dev/null || echo "gh not installed"

# Check if already authenticated — capture BOTH exit code AND output
gh auth status 2>&1 || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
```

**Decision tree:**
1. If `gh auth status` shows authenticated with NO failures → you're good, use `gh` for everything
2. **⚠️ Pitfall — Mixed state:** If `gh auth status` shows BOTH a failure (e.g., `GITHUB_TOKEN` invalid) AND a stored account, `gh` CLI API calls will fail because it prefers the env var. See **Pitfall: GITHUB_TOKEN env var conflict** below. Fix: use `curl` for API operations, `git push` with recovered credentials.
3. If `gh` is installed but not authenticated → use "gh auth" method below
4. If `gh` is not installed → use "git-only" method below (no sudo needed)

---

## ⚠️ Pitfall: GITHUB_TOKEN Env Var Conflict

**Symptom:** `gh auth status` shows both `X Failed to log in using token (GITHUB_TOKEN)` and `✓ Logged in to github.com account <user>`. `gh repo create`, `gh api`, etc. fail with `HTTP 401: Bad credentials`.

**Root cause:** The `GITHUB_TOKEN` env var is set to an invalid/expired token. The `gh` CLI prefers the env var over stored credentials for API calls, even when `hosts.yml` has a valid token.

**Fix — use curl for API, git for push:**

```bash
# 1. Extract the valid token from hosts.yml (bypasses gh and env var)
TOKEN=$(grep oauth_token ~/.config/gh/hosts.yml | head -1 | awk '{print $2}' | tr -d '"')

# 2. Use curl for API operations (repo create, etc.)
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{"name":"my-repo","description":"...","public":true}'

# 3. Set up git credentials for push
echo "https://$(git config user.name):${TOKEN}@github.com" > ~/.git-credentials
git config --global credential.helper store

# 4. Push works normally after credential setup
git push -u origin main
```

**Permanent fix (optional):** Unset or fix the env var:
```bash
unset GITHUB_TOKEN  # or fix in ~/.hermes/.env
```

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
- Set expiration — for agent stacks, use **"No expiration"** (classic PATs only). Fine-grained tokens max at 1 year. Default 30-day expiry causes frequent token death and user friction.
- Copy the token — it won't be shown again

**Step 2: Configure git to store the token**

```bash
# Set up the credential helper to cache credentials
# "store" saves to ~/.git-credentials in plaintext (simple, persistent)
git config --global credential.helper store

# Store credentials by doing a test operation that triggers auth
# Username: <your-github-username> (must be exact, case-sensitive)
# Password: <paste the personal access token, NOT your GitHub password>
git ls-remote https://github.com/<your-username>/<any-repo>.git

# The credential file format IS:
# https://<username>:<token>@github.com
# (note the colon after username, not just https://<token>@github.com)
# File location: ~/.git-credentials
cat ~/.git-credentials
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

## Token Rotation & Recovery

Stored tokens can expire. When `git push` fails with *"Invalid username or token"* or `gh auth status` shows not logged in despite a `hosts.yml` file, the token is stale.

**Recovery flow:**

```bash
# 1. Check if gh has a token cached (may be expired)
gh auth token 2>/dev/null || echo "No active token"

# 2. Check the raw gh config file (bypasses gh's cache)
cat ~/.config/gh/hosts.yml | grep oauth_token | head -1 | awk '{print $2}' | tr -d '"'

# 3. If token exists in hosts.yml but gh rejects it, rewrite git credentials
#    with the token from the file and retry
TOKEN=$(grep oauth_token ~/.config/gh/hosts.yml | head -1 | awk '{print $2}' | tr -d '"')
echo "https://$(git config user.name):${TOKEN}@github.com" > ~/.git-credentials
git config --global credential.helper store
git push origin main  # retry
```

If the token is missing or still rejected, generate a fresh PAT and re-run the credential setup below.

**Alternative: regenerate via `gh auth login`**

```bash
# Force re-authentication (opens browser on desktop)
gh auth logout --hostname github.com
gh auth login
# Select: GitHub.com → HTTPS → Browser flow
gh auth setup-git  # refresh git credential helper
```

If on headless/SSH, use `--with-token` and paste a new PAT.

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

### Hermes-Specific Recovery: Extracting a Stale Token from hosts.yml

**Problem:** `gh auth token` returns nothing even though `~/.config/gh/hosts.yml` contains a valid OAuth token. This happens when gh's internal cache is corrupted or the session expired but the file wasn't cleared.

**Solution:** Extract the token directly from the YAML file and inject it into git credentials.

```bash
# Extract token and username from gh's hosts.yml (works even if gh is broken)
if [ -f ~/.config/gh/hosts.yml ]; then
  TOKEN=$(grep 'oauth_token:' ~/.config/gh/hosts.yml | head -1 | awk '{print $2}' | tr -d '"')
  USERNAME=$(grep '^  user:' ~/.config/gh/hosts.yml | head -1 | awk '{print $2}')
  
  if [ -n "$TOKEN" ] && [ -n "$USERNAME" ]; then
    echo "https://${USERNAME}:${TOKEN}@github.com" > ~/.git-credentials
    git config --global credential.helper store
    echo "✅ Recovered git credentials from gh hosts.yml"
  else
    echo "⚠️ Could not parse token/username from hosts.yml"
  fi
fi
```

**Why this works:** The `gh` CLI stores the OAuth token in `~/.config/gh/hosts.yml` even when the session is expired. Bypassing the CLI and reading the file directly recovers the token without needing to re-authenticate.

**Verification:** After writing credentials, test with `git ls-remote https://github.com/<username>/<repo>.git` — should succeed without prompting for password.

---

### Recovery Script

Use the bundled helper when credentials fail:

```bash
# Run from skill directory or anywhere
/root/.hermes/profiles/gentech/skills/github/github-auth/scripts/fix-git-credentials.sh
# Or dry-run first to see what it would do:
/root/.hermes/profiles/gentech/skills/github/github-auth/scripts/fix-git-credentials.sh --dry-run
```

The script checks your `~/.git-credentials` format, extracts a fresh token from `~/.config/gh/hosts.yml` if available, and rewrites credentials with correct `username:token` format.
