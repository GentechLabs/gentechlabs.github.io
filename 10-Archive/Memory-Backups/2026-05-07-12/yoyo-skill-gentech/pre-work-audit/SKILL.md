---
name: pre-work-audit
title: Pre-Work Audit Protocol
description: Always audit existing state before starting work — check GitHub + Obsidian vault first. Never duplicate work or assume fresh start.
version: 1.0.0
last_updated: 2026-05-05
---

## Trigger Conditions

Before starting ANY work session on any project, load this skill and execute the audit. Applies to all agents (YoYo, DMOB, Desmond, Gentech).

## Protocol

### Step 1: GitHub Audit
```bash
# Check latest commits
git -C /path/to/repo log --oneline -10

# Check current branch + status
git -C /path/to/repo status

# Check for uncommitted work
git -C /path/to/repo diff --stat

# Check for untracked files
git -C /path/to/repo ls-files --others --exclude-standard
```

### Step 2: Obsidian Vault Audit
```bash
# Search for prior work on this project
rg "PROJECT_NAME" /root/vaults/gentech/03-Projects/ --md -l

# Search for handoffs
rg "PROJECT_NAME" /root/vaults/gentech/09-Green Room/ --md -l

# Search for any mentions
rg "PROJECT_NAME" /root/vaults/gentech/ --md -l | head -20
```

### Step 3: Pending Approvals Check
When asked "what needs approval?" or "what's pending?", audit these locations:

```bash
# Check Green Room approvals folder
ls -la /root/vaults/gentech/09-Green\ Room/approvals/

# Check HQ approvals folder
ls -la /root/vaults/gentech/00-HQ/Approvals/

# Check active handoffs for blockers
ls -la /root/vaults/gentech/09-Green\ Room/active-handoffs/

# Read master todo for pending items
cat /root/vaults/gentech/09-Green\ Room/master-todo.md

# Search for "BLOCKER" or "needs approval" across vault
rg -i "blocker|needs approval|waiting for" /root/vaults/gentech/ --md -l | head -10
```

**Key files to check:**
- `09-Green Room/master-todo.md` — master task list with priorities and blockers
- `09-Green Room/active-handoffs/` — current work threads with status
- `00-HQ/Approvals/` — items awaiting Jordan's approval
- `00-HQ/TODO/` — task tracking and sync issues

### Step 4: Synthesis
Before writing any code or creating any files:
1. List what already exists (code, docs, configs)
2. List what's incomplete or stale
3. List what's actually needed (gap analysis)
4. Only then begin work

## No-Idle Workflow Directive

After the audit, if you hit a stopping point (waiting for approval, blocked on a tool/person, external dependency), **immediately queue the next priority task and keep working.** Do not idle.

**Stopping points defined as:**
- Waiting for Jordan's approval
- Waiting on a tool/person unavailable (e.g., George)
- Any external dependency that creates idle time

**Queue order for current sprint:**
1. Primary hackathon deliverables (Solana Frontier → Kite AI)
2. Sidetrack adapters (thin wrappers, low effort)
3. Next priority from master-todo

This applies to ALL agents, not just DMOB.

**Example workflow:**
- If blocked on Solana Frontier (waiting for Anchor toolchain fix) → pivot to Zerion/GoldRush adapters
- If blocked on both → scaffold next priority from master-todo
- If waiting for Jordan's approval → document the blocker and queue next task

## Why This Exists

Repeated instances of:
- Building something that already existed in the vault
- Not knowing about prior handoffs or decisions
- Duplicating work because the agent didn't check first
- Starting from scratch when 80% was already done

## Example

**Bad:** "Let me scaffold a new AgentEscrow project" (without checking)
**Good:** "Let me check the vault and GitHub for existing AgentEscrow work first, then fill gaps"
