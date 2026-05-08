---
name: pre-work-audit
description: "Pre-work audit pattern: before starting any task, always check what already exists in GitHub and Obsidian vault first. Prevents duplicate work, ensures building on existing foundations."
tags: [workflow, audit, github, obsidian, best-practice]
trigger: "Before starting any new work task, sprint, or build — always run this audit first. No exceptions."
version: 1.0.0
author: Gentech
---

# Pre-Work Audit Protocol

**Rule:** Before starting ANY work, ALWAYS do a clean audit of what already exists. Check GitHub and Obsidian vault first. No exceptions.

## Why This Matters
- Prevents duplicate work across agents
- Ensures we build on existing foundations, not restart from scratch
- Surfaces blockers, partial builds, and context that would otherwise be lost
- Keeps the team aligned on what's real vs. what's planned

## Audit Steps

### Step 1: GitHub Check
```bash
# Check for existing repos related to the task
gh repo list <org> --limit 20 | grep -i <keyword>

# Check recent commits on relevant repos
gh api repos/{owner}/{repo}/commits --jq '.[0:5] | .[] | "\(.commit.message) (\(.commit.author.date))"'

# Check open issues/PRs
gh issue list --repo <repo> --state open
gh pr list --repo <repo> --state open

# Check if there's existing code to build on
git log --oneline -10
```

### Step 2: Obsidian Vault Check
```bash
# Search vault for relevant docs
grep -r "<keyword>" /root/vaults/gentech/ --include="*.md" -l

# Check project folders
ls /root/vaults/gentech/03-Projects/<project>/
ls /root/vaults/gentech/02-Labs/Hackathons/Active/

# Check for existing architecture docs
find /root/vaults/gentech -name "*architecture*" -o -name "*spec*" -o -name "*plan*" | grep -i <keyword>
```

### Step 3: Cross-Reference
- Compare GitHub state vs. vault docs — are they in sync?
- Identify partial builds that can be completed vs. starting fresh
- Check for blockers, TODOs, or known issues in existing code
- Review any handoffs or status notes from previous sessions

### Step 4: Document Findings
Create a brief audit summary:
```markdown
## Pre-Work Audit — [Task Name]
**Date:** YYYY-MM-DD
**Auditor:** [Agent Name]

### What Exists
- [List found code, docs, configs]

### What's Complete
- [List finished components]

### What's Partial/Incomplete
- [List items that need finishing]

### What's Missing
- [List items that need to be built from scratch]

### Recommendation
- [Build on X / Start fresh / Merge Y and Z]
```

### Step 5: Proceed with Clarity
- Only NOW start the actual work
- Reference existing code/docs in your build
- Update vault with progress as you go
## Step 6: Deploy to All Agents

When creating or updating this skill, ensure it's deployed to ALL agent skill directories:
- `/root/.hermes/profiles/gentech/skills/devops/pre-work-audit/`
- `/root/.hermes/profiles/yoyo/skills/gentech/pre-work-audit/`
- `/root/.hermes/profiles/dmob/skills/` (create path as needed)
- `/root/.hermes/profiles/desmond/skills/` (create path as needed)

**Deployment status tracker:**
| Agent | Status | Last Updated |
|-------|--------|-------------|
| Gentech | ✅ | 2026-05-05 |
| YoYo | ✅ | 2026-05-05 |
| DMOB | ❌ NOT DEPLOYED | — |
| Desmond | ❌ NOT DEPLOYED | — |

## Pitfalls

- **NEVER skip the audit** — even if you think nothing exists. Check anyway.
- **NEVER assume GitHub is up to date** — vault and repo can diverge. Check both.
- **NEVER start from scratch** without confirming nothing exists — the audit might save hours.
- **ALWAYS document what you found** — the next agent benefits from your audit trail.
- **ALWAYS check build environment compatibility** — see `references/solana-anchor-toolchain-compat.md` for known issues with Anchor/Solana version mismatches.
- **DEPLOY to all agents** — a skill only Gentech has doesn't help when DMOB or Desmond starts working.

## Example
Jordan: "Build the AgentEscrow frontend"
Agent: "Before I start, let me check what we have..."
→ Runs pre-work audit
→ Discovers 4 programs already deployed to devnet, architecture docs exist, demo storyboard planned
→ Builds on top of existing work instead of starting from zero
→ Saves 2-3 hours of redundant effort

---

*Created: 2026-05-05 | Per Jordan's directive: always audit before starting work*
