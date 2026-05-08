---
name: hermes-brain-backup
description: Set up private GitHub backup of the Hermes agent brain — skills, config, memories, and agent profiles.
---

# Hermes Brain Backup

Backs up the agent "brain" to a private GitHub repo. Protects against vault corruption, server loss, or accidental deletion.

**Repo:** `Gentech-Labs/hermes-brain` (private)

## What Gets Backed Up
- **Skills** — All custom skills from `~/.hermes/skills/` (the real IP, ~92MB)
- **Config** — Root `config.yaml` + per-profile `config.yaml`
- **Memories** — `~/.hermes/memories/USER.md` + `MEMORY.md`
- **Agent Profiles** — `SOUL.md` + `cron/jobs.json` per agent (yoyo, dmob, desmond)

## What Gets Excluded
- `.env`, `auth.json`, `auth.lock`, `gateway.pid`, `gateway_state.json`, `processes.json`, `.skills_prompt_snapshot.json`
- `state.db*`, `*.lock`, `*.pid`
- `venv/`, `node_modules/`, `__pycache__/`, `cache/`, `logs/`, `sessions/`, `sandboxes/`, `checkpoints/`
- Embedded git repos (they have their own repos)
- `skills/.hub/` (index cache, regenerable)
- Cron job **output** files (only `jobs.json` is backed up)

## Setup Steps

1. **Create private repo:**
   ```bash
   gh repo create Gentech-Labs/hermes-brain --private
   ```

2. **Initialize git directly in ~/.hermes/:**
   ```bash
   cd /root/.hermes
   git init
   git branch -m main
   git remote add origin https://github.com/Gentech-Labs/hermes-brain.git
   ```

3. **Create `.gitignore`** using whitelist approach — ignore everything by default, then unignore specific paths:
   ```
   *
   !.gitignore
   !config.yaml
   !memories/
   !memories/**
   !skills/
   !skills/**
   !profiles/
   !profiles/*/
   !profiles/*/SOUL.md
   !profiles/*/config.yaml
   !profiles/*/cron/
   !profiles/*/cron/jobs.json
   ```

4. **Exclude embedded git repos** (discovered during first backup):
   ```
   skills/autonomous-ai-agents/hermes-agent-self-evolution/
   skills/autonomous-ai-agents/hermes-council/
   skills/finance/nethermind-defi-skills/
   skills/note-taking/obsidian-skills/
   skills/red-teaming/anthropic-cybersecurity-skills/
   skills/red-teaming/krait/
   skills/red-teaming/trailofbits-skills/
   skills/.hub/
   ```

5. **Verify before committing:**
   ```bash
   git add -n .     # dry-run — check what's included
   git add -A && git status --short | wc -l  # should be ~450 files
   git ls-files | xargs du -ch | tail -1     # should be ~8MB
   ```

6. **Commit and push:**
   ```bash
   git add -A && git commit -m "Initial backup: skills, config, memories, agent profiles"
   git push -u origin main
   ```

## Pitfalls
- **Embedded git repos:** Several skills directories are themselves git repos (hermes-council, nethermind-defi-skills, etc.). Git warns about these. Exclude them explicitly in .gitignore — they have their own remotes.
- **Whitelist approach required:** A blacklist .gitignore (excluding specific things) is fragile — you'll always miss something. Whitelist (`*` then `!pattern`) is safer.
- **config.yaml API keys:** Verify with `grep -i "key\|token\|secret" config.yaml`. At time of writing, the `api_key` fields are empty — secrets live in `.env` files (excluded from backup).
- **Cron output vs config:** `profiles/*/cron/output/` accumulates fast. Only back up `jobs.json`, not output files.
- **Profile home dirs are huge:** `~/.hermes/profiles/yoyo/home/` is ~389MB (contains repos). The `.gitignore` whitelist avoids these entirely.
- **Git identity:** First commit uses auto-generated committer from hostname. Amend with `git commit --amend --reset-author` if desired.

## Restore Procedure
```bash
cd /root/.hermes
git clone https://github.com/Gentech-Labs/hermes-brain.git .tmp-brain
cp .tmp-brain/.gitignore .gitignore
cp .tmp-brain/config.yaml config.yaml
cp -r .tmp-brain/memories/* memories/
cp -r .tmp-brain/skills/* skills/
cp -r .tmp-brain/profiles/* profiles/
rm -rf .tmp-brain
```
