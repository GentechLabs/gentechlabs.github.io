---
name: agent-wake-protocol
description: Wake-up sequence for when agents come back online after downtime or session reset. Ensures continuity across sessions.
tags: [workflow, memory, onboarding, continuity]
---

# Agent Wake-Up Protocol

When you come back online (new session, after downtime, or after a reset), follow this sequence BEFORE responding to any messages:

## Step 1: Check Memory
- Read your injected memory block at the top of your context
- Identify: who you are, what your role is, what project you're on

## Step 2: Check Recent Sessions
- Call `session_search()` (no query) to see recent work
- Identify the last task/project discussed

## Step 3: Check Brain Backup (if relevant)
- Quick check of `Gentech-Labs/hermes-brain-backup` for latest commits
- Command: `cd /root/hermes-brain-backup && git log --oneline -5`
- Compare with your memory — anything you're missing?

## Step 4: Proactive Greeting
After gathering context, message Jordan with:
1. What you remember from last session
2. What the current state is (any active tasks, cron jobs, pending items)
3. Ask: "What should we work on?" or "Last thing we talked about was X — want to continue?"

## Example Opening:
> "Hey Jordan, I'm back online. Last session we were [X]. My memory shows [Y]. Any updates, or should we pick up where we left off?"

## Important:
- NEVER pretend you remember if you don't — check first
- If memory is empty/fresh, say so honestly
- Always be proactive — don't wait for Jordan to re-explain everything
- If Jordan sent messages while you were offline, review them first
