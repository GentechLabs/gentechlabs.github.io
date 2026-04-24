---
name: gentech-workflow-protocol
description: Communication and workflow rules for GenTech agents. Captures Jordan's preferences for message style, task handling, Brain updates, and cross-group coordination.
tags: [gentech, workflow, communication, protocol]
---

# GenTech Workflow Protocol

## Communication Style
- **Lean Mode**: Keep messages short and direct. Reference vault notes instead of re-pasting content.
- **Voice Messages**: Use `text_to_speech` for long-form or complex messages. The ElevenLabs key is in memory.
- **No Walls of Text**: One-sentence conclusions over paragraphs. Tables only when comparing options.
- **Lead with the recommendation, then reasoning.**

## Task Handling
- **Stay the Course Protocol**: When Jordan sends a link or message while an agent is mid-task, do NOT interrupt. Complete the current logic-block, reach a natural stopping point, THEN process the new message.
- **Queue, Don't Jump**: Treat incoming messages as a queue of inspirations to process at the next stopping point.
- **Direct Answer Mandate**: Every conversation must end with a definitive answer or conclusion. No open-ended technical threads left dangling.
- **Brain Sync Before Reporting**: Before reporting to HQ, check the Vault/Brain for pending approvals or constraints. Deliver ONE consolidated answer to Jordan.

## "Update the Brain" Protocol
When Jordan says "Update the Brain", execute this three-step atomic operation:
1. **Vault Commit**: Finalize all atomic notes, metadata headers, and wikilinks in the Obsidian vault.
2. **Skills Sync**: Mirror any new/updated skills into the `/skills/` directory.
3. **GitHub Push**: `cd /root/vaults/gentech && git add . && git commit -m "brain sync: [summary]" && git push`

## Brain SOP (Knowledge Management Standard)
1. **Atomic Notes**: One concept per note. No mega-files.
2. **YAML Metadata Headers**: Every strategic note starts with status, priority, owner, last_updated, tags.
3. **Wikilinks**: Use `[[NoteName]]` to connect related concepts. Never leave ideas isolated.
4. **Inbox Folder**: Use `/00-Inbox/` for Green Room/Mess Hall handoffs and items needing Jordan's approval.

## Model Assignment
| Agent | Department | Model |
|-------|-----------|-------|
| YoYo | Strategies | glm-5.1 (Ollama Cloud) |
| Gentech | HQ | glm-5.1 (Ollama Cloud) |
| Desmond | Entertainment | glm-5.1 (Ollama Cloud) |
| DMOB | Labs | qwen3-coder (Ollama Cloud) |

All models must be Ollama Cloud compatible. Specialized routing for heavy tasks is acceptable but defaults to glm-5.1.

## Context Management
If context compression triggers frequently:
- Switch to shorter responses (Lean Mode)
- Reference vault paths instead of re-explaining context
- Consider escalating to a higher-context model (kink-42-thinking, deepseek-v3.1) for complex reasoning sessions

## Cron Job: Omni-Summary Master Brief
Single consolidated morning briefing at 6:30 AM EST (30 11 * * *) delivered to HQ.
Uses `session_search` to pool conversations from ALL groups, then delivers:
- 📌 Yesterday's Wins & Decisions
- ⚠️ Active Blockers & Urgent Needs
- 🎯 Today's Strategic Focus (top 3)
- 🛠️ Vault/System Status

## Collaborators
- Vanito (8774981477): Music/creative, in Entertainment + Strategies + Labs
- Dadrian (6842745592): Logistics/travel, Jordan's cousin, in Strategies + Labs + Entertainment
- NOT in HQ (Jordan + agents only)

## Pitfalls
- Do NOT use FAL image generation via Nous proxy (broken). Use `vision_analyze` or set FAL_KEY directly.
- `web_extract` fails on X/Twitter URLs — always use `browser_navigate` instead.
- ElevenLabs TTS key must be in the live shell environment, not just agent memory, to work.
- Dadrian's Telegram ID has a discrepancy in some files (6842745592 vs 6842745552) — confirm with Jordan.