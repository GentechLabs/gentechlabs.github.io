---
name: multi-repo-audit
description: "Audit all local repos: discover, test, metrics, context, report."
version: 1.0.0
author: Desmond
metadata:
  hermes:
    tags: [audit, codebase, repos, testing, pygount, foundry, github]
    related_skills: [codebase-inspection, github-repo-management, github-auth]
prerequisites:
  commands: [git, pygount, forge, gh]
---

# Multi-Repo Codebase Audit

Audit all local repositories for health, test coverage, metrics, and documentation state. Produces a structured report suitable for team review.

## When to Use

- User says "audit the codebase", "review all repos", "what do we have"
- Inheriting a new project with multiple repos
- Pre-hackathon health check across repositories
- Onboarding to a team's codebase
- Periodic codebase health assessment

## Prerequisites

```bash
# Install tools if missing
# pygount — watch for rich package conflict on Debian/Ubuntu
pip install --break-system-packages --ignore-installed rich pygount 2>/dev/null || pip install pygount
# Foundry (Solidity projects)
curl -L https://foundry.paradigm.xyz | bash && source ~/.bashrc && foundryup
# gh CLI
apt install gh || brew install gh
```

## Audit Workflow (5 Phases)

### Phase 1: Discover Repos

Find all git repos on the machine:

```bash
# Find all .git directories (max depth 4)
find /root -maxdepth 4 -name ".git" -type d 2>/dev/null

# Or scan specific directories
for dir in /root/gentech/*/ /root/projects/*/; do
  [ -d "$dir/.git" ] && echo "$dir"
done
```

### Phase 2: Environment Check

```bash
# Dev tools
git --version
gh --version 2>/dev/null || echo "gh not installed"
forge --version 2>/dev/null || echo "forge not installed"
node --version 2>/dev/null
python3 --version 2>/dev/null
pygount --version 2>/dev/null || echo "pygount not installed"

# GitHub auth
gh auth status 2>&1 || echo "NOT AUTHENTICATED"
cat ~/.git-credentials 2>/dev/null | head -1 | sed 's/ghp_[a-zA-Z0-9]*/ghp_***REDACTED***/g'
git config --global user.name
git config --global user.email
```

### Phase 3: Per-Repo Metrics

For each discovered repo:

```bash
cd $REPO_DIR

# Basic info
git log --oneline -1          # Latest commit
git remote -v | head -2       # Remote URL
git branch -a | head -5       # Branches
find . -not -path './.git/*' -type f | wc -l  # File count

# Code metrics (pygount)
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,cache,dist,build,.next" \
  . 2>/dev/null

# Test status (Solidity)
forge test --summary 2>/dev/null | tail -10

# Test status (Python)
python -m pytest --tb=no -q 2>/dev/null | tail -5

# Test status (Node)
npm test 2>/dev/null | tail -5
```

### Phase 4: Context Gathering

Read architecture docs, brain vault, strategy files:

```bash
# Brain vault memories
cat /root/repos/hermes-brain/memories/MEMORY.md
cat /root/repos/hermes-brain/memories/USER.md

# Architecture docs
find $VAULT_DIR -name "*architecture*" -o -name "*spec*" | head -10

# Hackathon status
cat $VAULT_DIR/01-Agency/active-hackathons.md
cat $VAULT_DIR/09-Green Room/master-todo.md
```

### Phase 5: Audit Report

Write structured report to vault:

```bash
cat > $VAULT_DIR/01-Agency/Approvals/CODEBASE-AUDIT-$(date +%Y-%m-%d).md << 'EOF'
# 📋 Codebase Audit — [DATE]

## Environment
| Tool | Status |
|------|--------|

## Repo Summary
| Repo | LOC | Files | Tests | Status |
|------|-----|-------|-------|--------|

## Test Results
```
TOTAL: X/Y passing ✅/❌
```

## Key Findings
### ✅ What's Solid
### ⚠️ Gaps Identified

## Recommendations
### Immediate
### Short Term
### Strategic

## Repo Map
```
[tree structure]
```
EOF
```

## Solidity Test Detection

For Foundry projects, detect test files:

```bash
# Count test files
find . -name "*.t.sol" | wc -l

# Run tests with summary
forge test --summary 2>&1 | tail -15

# Check for failing tests
forge test 2>&1 | grep -E "FAIL|PASS" | grep FAIL
```

## Python Test Detection

```bash
# pytest
python -m pytest --co -q 2>/dev/null | tail -3  # count tests
python -m pytest --tb=no -q 2>/dev/null | tail -5  # run tests

# unittest
python -m unittest discover -s tests 2>/dev/null | tail -5
```

## Pitfalls

1. **pygount hangs without --folders-to-skip** — always exclude .git, node_modules, venv
2. **pygount install fails on Debian/Ubuntu** — system `rich` package conflicts. Use `pip install --break-system-packages --ignore-installed rich pygount` to force reinstall
3. **forge not installed** — install foundry first: `curl -L https://foundry.paradigm.xyz | bash && foundryup`. May need approval on first run
4. **GitHub auth** — check `gh auth status` before any push/pull operations. If not authenticated, flag as BLOCKER in report
5. **Large repos (10K+ files)** — use `--suffix` to target specific languages instead of scanning everything
6. **Empty repos** — flag them in the report; they need populating or deletion
7. **Repo overlap** — when repos share >50% code, note it as a consolidation opportunity
8. **Git identity not set** — check `git config --global user.name` and `user.email`. Missing identity causes ugly commit logs
