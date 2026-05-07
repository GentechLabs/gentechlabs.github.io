---
name: hermes-github-operations
description: "GitHub operations within Hermes agent sessions: Python-based Git/GH workflows, token auth via subprocess, cross-session repo path handling"
version: 0.1.0
author: DMOB (Gentech Labs)
license: MIT
metadata:
  hermes:
    tags: [GitHub, Hermes, Python, Automation, Agent]
    related_skills: [github-auth, github-repo-management, vault-atomic-operations]
---

# Hermes GitHub Operations

This skill covers GitHub workflows when operating from inside a Hermes agent session. Unlike manual shell work, agent sessions run in isolated Python contexts with their own home directories. This affects credential storage, repo location persistence, and subprocess command patterns.

## Context

- **Agent session isolation**: Each Hermes agent runs in its own home directory (`~/.hermes/profiles/<agent>/home/`). Files created in one session may not be visible in another unless in shared locations.
- **GitHub token storage**: Store tokens in `~/.hermes/.env` (loaded automatically) or use `gh` CLI with `--with-token` via subprocess.
- **Git executable**: Available at `/usr/bin/git` in standard Hermes images.
- **gh CLI**: Available at `/usr/bin/gh` in standard Hermes images.

---

## Quick Setup (One-Time)

```python
import subprocess
import os

# Save token to Hermes env (persists across sessions for this agent)
env_path = os.path.expanduser("~/.hermes/.env")
with open(env_path, 'a') as f:
    f.write(f'\nGITHUB_TOKEN={YOUR_TOKEN}\n')

# Export for current session
os.environ['GITHUB_TOKEN'] = YOUR_TOKEN

# Authenticate gh CLI (creates ~/.config/gh/hosts.yml)
subprocess.run(['gh', 'auth', 'login', '--with-token'], input=YOUR_TOKEN + '\n', text=True)
subprocess.run(['gh', 'auth', 'setup-git'])

# Set git identity
subprocess.run(['git', 'config', '--global', 'user.name', 'Your Name'])
subprocess.run(['git', 'config', '--global', 'user.email', 'you@example.com'])
```

---

## Pattern: Token-Auth GH CLI from Python

When you need to run GH CLI commands from a Python agent script and the token is in an env var or variable:

```python
import subprocess

TOKEN = os.environ.get('GITHUB_TOKEN')  # or pass it explicitly

# gh auth login with token (non-interactive)
result = subprocess.run(
    ['gh', 'auth', 'login', '--with-token'],
    input=TOKEN + '\n',
    capture_output=True, text=True
)
# Check result.returncode, result.stdout, result.stderr
```

**Why not shell `echo "$TOKEN" | gh auth login --with-token` in Python?**  
The `input=` parameter avoids shell quoting issues and works reliably across platforms.

---

## Pattern: Git Operations with Token in Python

Once `gh auth setup-git` has run, git uses the stored credential. For direct token use without gh:

```python
import subprocess

# Set remote with embedded token (per-repo, avoids credential prompts)
subprocess.run([
    'git', 'remote', 'set-url', 'origin',
    f'https://{username}:{TOKEN}@github.com/{owner}/{repo}.git'
])

# Or configure credential helper to use token from env
subprocess.run(['git', 'config', '--global', 'credential.helper', 'store'])
# First git operation will prompt; pipe username=TOKEN, password=TOKEN
```

---

## Finding Repos Across Agent Sessions

**Problem**: A repo cloned in session A (e.g., `~/portfolio`) may not exist at the same path in session B due to different agent home directories.

**Solution**:
1. **Standardize clone location**: Use an absolute path under `/root/` or `/opt/` that's session-independent.
   ```python
   REPO_DIR = '/root/portfolio'  # stable across sessions
   ```
2. **Or store path in vault**: Record the absolute path in the task's vault notes and read it back on next session.
3. **Or discover by search**: Search known locations (cautious — may find multiples).
   ```python
   import glob
   candidates = glob.glob('/root/*/portfolio') + glob.glob('/root/portfolio')
   ```

**Best practice**: For long-lived repos, clone to `/root/<repo-name>` (session-agnostic). Document the location in the agent's memory section or vault.

---

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| `gh auth login --with-token` hangs waiting for stdin | Always provide `input=TOKEN + '\n'` in `subprocess.run`, don't rely on piped shell input |
| Token not persisted to git credentials | Run `gh auth setup-git` immediately after login. Verify with `git config --global credential.helper` (should be `store` or `cache`) |
| Repo path missing in new session | Clone to `/root/` or use vault-stored path; agent homes (`~/.hermes/...`) are ephemeral across sessions |
| `Permission denied (publickey)` after token auth | gh uses HTTPS by default; ensure `gh config get git_protocol` returns `https` or force remote URLs to `https://` |
| `gh: command not found` in some images | Fall back to git-only method with embedded token in remote URL |
| Push rejected due to GitHub Actions auto-commit | If the repo has a GitHub Actions workflow that auto-commits (e.g. portfolio sync), the remote may have new commits after your local changes. Fix: `git pull --rebase origin main` then push. If the rebase causes conflicts on non-critical changes, `git reset --hard origin/main` and re-apply your small fix on top. |
| GitHub Pages not deployed after push | Pages CDN has 25-30s deployment delay after push. Verify with `sleep 25 && curl -s https://<user>.github.io/ | grep '<changed element>'`. Don't assume failure if the live site doesn't reflect changes immediately. |

---

## Verification Checklist

After setup, run in Python to confirm:

```python
import subprocess

# 1. gh auth works
r = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
assert r.returncode == 0 and 'Logged in' in r.stdout

# 2. git identity set
r = subprocess.run(['git', 'config', '--global', 'user.name'], capture_output=True, text=True)
assert r.returncode == 0 and r.stdout.strip()

# 3. Can list a known repo
r = subprocess.run(
    ['git', 'ls-remote', 'https://github.com/ProtoJay4789/ProtoJay4789.github.io'],
    capture_output=True, text=True
)
assert r.returncode == 0
print('Ready to push')
```

---

## When to Use This Skill

Use this skill when:
- Writing Python scripts that interact with GitHub from a Hermes agent
- Needing to re-authenticate after token expiry across sessions
- Managing repo locations that must persist beyond a single agent run
- Automating PR creation, issue updates, or deployments from agent context

**Not needed** for manual one-off `gh` or `git` commands in a shell where you're already logged in.

---

## Related

- `github-auth` — manual auth flows, SSH setup, token generation
- `github-repo-management` — clone, fork, branch workflows
- `vault-atomic-operations` — concurrent-safe vault writes for repo metadata

## Session Notes

- [`session-path-protojay-portfolio.md`](references/session-path-protojay-portfolio.md) — Path isolation issue encountered during portfolio deployment (May 2026), resolution via standardized `/root/` repo locations.
