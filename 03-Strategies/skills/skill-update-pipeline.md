# Skill Update Pipeline — Gentech

## Description
Weekly cron job that pulls the latest updates from all git-based skill repos and reports changes.

## Current Cron Job
- **ID:** `5b7f0cc7b6d5`
- **Name:** Sunday Skill Update Check
- **Schedule:** `0 10 * * 0` (Sundays at 10:00 UTC)

## Prompt Refactoring

### Before (Raw code in prompt)
```bash
#!/bin/bash
REPOS=(
  "/root/.hermes/skills/autonomous-ai-agents/hermes-agent-self-evolution"
  "/root/.hermes/skills/autonomous-ai-agents/hermes-council"
  "/root/.hermes/skills/finance/nethermind-defi-skills"
  "/root/.hermes/skills/note-taking/obsidian-skills"
  "/root/.hermes/skills/red-teaming/anthropic-cybersecurity-skills"
  "/root/.hermes/skills/red-teaming/krait"
  "/root/.hermes/skills/red-teaming/trailofbits-skills"
)
```

### After (Clean human-readable prompt)

You are the Gentech DevOps Agent. Run the **weekly skill update check**.

**Task:**
Scan all git-based skill repos under `/root/.hermes/skills/` and update any that have new commits upstream. Report:
- Repos that are up-to-date ✅
- Repos that were updated with commit count 📥  
- Repos that failed with error reason ❌

**Execution:**
1. Iterate through all subdirectories under `/root/.hermes/skills/`
2. For each repo subdirectory that is a git repository:
   - `git fetch origin` to check for updates
   - Compare local vs remote HEAD
   - If behind: `git pull origin` and log changes
   - If error: log the error without crashing
3. Generate a summary table of all repos and their status
4. Deliver the summary to Telegram group -1003893562036 (Entertainment)

**Expected Output Format:**
```
🔄 Skills Update Check — 2026-04-27
================================================

📦 hermes-agent-self-evolution    ✅ Up to date
📦 hermes-council                 📥 3 commits — pulled
📦 nethermind-defi-skills         ❌ Pull failed: error: ...
...

📊 Summary: 2 updated, 1 error, 4 already current
```

> **Note:** Keep silent if all repos are up-to-date. Only deliver if updates occurred or if errors need attention.
