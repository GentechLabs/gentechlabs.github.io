---
name: github-status-review
description: Review GitHub org/person repos for project status, recent activity, and health. Uses gh CLI to compile status reports across multiple repos.
triggers:
  - "check github for project status"
  - "what's the status of our repos"
  - "review github activity"
  - "github status report"
---

# GitHub Status Review

Compile a status report across multiple GitHub repos for an org or user.

## Steps

### 1. List repos with metadata
```bash
gh repo list OWNER --limit 30 --json name,updatedAt,pushedAt,isFork,isPrivate,description --template '{{range .}}{{.name}} | {{if .isPrivate}}Private{{else}}Public{{end}} | {{if .isFork}}(fork){{end}} | Pushed: {{.pushedAt}} | {{.description}}{{"\n"}}{{end}}'
```

### 2. Check recent commits (per repo)
```bash
gh api repos/OWNER/REPO/commits?per_page=5 --template '{{range .}}{{.sha | slice 0 7}} | {{.commit.author.date}} | {{.commit.message}}{{"\n---\n"}}{{end}}' | head -40
```

**PITFALL:** `slice` fails on `sha` field (it's an int in the API, not a string). Use simpler template:
```bash
gh api repos/OWNER/REPO/commits?per_page=5 --jq '.[] | "\(.sha[0:7]) | \(.commit.author.date) | \(.commit.message | split("\n")[0])"'
```
Or clone with `--depth 1` and use `git log --oneline -10`.

### 3. Get repo details
```bash
gh repo view OWNER/REPO --json languages,description,updatedAt,pushedAt,defaultBranchRef
```

### 4. Check issues/PRs
```bash
gh issue list --repo OWNER/REPO --state all --limit 5
gh pr list --repo OWNER/REPO --state all --limit 5
```

### 5. Check CI/CD
```bash
gh run list --repo OWNER/REPO --limit 5
```

## Classification heuristic
- **🔥 Active**: Pushed within 24 hours
- **🟡 Recent**: Pushed within 7 days
- **🔴 Stale**: Pushed >7 days ago
- **💀 Dormant**: Pushed >30 days ago

## Known issues
- `gh notification` is NOT a valid command — use `gh status` instead
- Go template `slice` fails on non-string types — prefer `--jq` for complex transforms
- Go template doesn't have `split` — use `jq` instead for string manipulation
- `gh api` JSON responses need `--jq` (not Go templates) for string operations like `[0:7]` slicing

## Output format
Organize as table with: Repo | Status | Last Push | Notes (description + key flags)
