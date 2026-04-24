# claude-obsidian — Potential Vault Tool

**Repo:** https://github.com/AgriciDaniel/claude-obsidian
**Stars:** 1.5k | **Forks:** 171 | **Last commit:** Apr 13, 2026
**Status:** Review pending — may integrate with our Obsidian vault

## What It Does
Claude + Obsidian knowledge companion based on Karpathy's LLM Wiki pattern.
- Drop sources → auto-extract entities, concepts, cross-references
- Query vault → citations to your wiki, not training data
- Auto-lint → orphans, dead links, stale claims, missing cross-references
- Session memory → hot cache persists between conversations
- Autonomous research → 3-round web research with gap-filling
- Multi-agent support (Claude, Gemini, Codex, Cursor, Windsurf)
- 10 skills, zero manual filing

## Commands
- `/wiki` — query the vault
- `/save` — save current context
- `/autoresearch` — autonomous research

## Setup
```bash
git clone https://github.com/AgriciDaniel/claude-obsidian
cd claude-obsidian
bash bin/setup-vault.sh
```
Or as Claude Code plugin:
```bash
claude plugin marketplace add AgriciDaniel/claude-obsidian
claude plugin install claude-obsidian
```

## Why Relevant
Tightens the second brain — structured vault maintenance, cross-referencing, session continuity, contradiction flagging. Could reduce the vault cron cleanup workload.
