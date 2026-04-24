---
name: gentech-brain-management
description: Standard operating procedure for managing the GenTech Obsidian vault as a strategic long-term memory for AI agents.
---

# GenTech Brain Management

## 🎯 Objective
Maintain the Obsidian vault as a high-fidelity external memory that allows agents to bypass context window limits and maintain strategic continuity across sessions.

## 🛠️ Core Standards

### 1. Atomic Note-Taking (Zettelkasten)
- **One Concept, One Note**: Avoid "Mega-Notes." Split broad topics into individual, focused notes.
- **Reasoning**: Reduces noise during `search_files` and `read_file` operations, ensuring the model receives only the most relevant data.

### 2. Structured Metadata (YAML)
Every strategic or project note MUST begin with a YAML frontmatter block:
```yaml
---
status: [active | pending | archived]
priority: [P1 | P2 | P3]
owner: [YoYo | DMOB | Desmond | Gentech]
last_updated: YYYY-MM-DD
tags: [tag1, tag2]
---
```
- **Maintenance**: Update the `status` and `priority` during shift wrap-ups or project pivots.

### 3. The Knowledge Web (Wikilinks)
- **Interconnectivity**: Use `[[Note Name]]` syntax to link related concepts.
- **Pattern**: Link a specific implementation (e.g., `Bags-Hackathon.md`) back to its parent strategy (e.g., `[[Agentic-Commerce-Pattern]]`).

## 📂 Vault Architecture
- **SOP Location**: `/root/vaults/gentech/00-System/Brain-SOP.md`
- **Departmental Folders**:
    - Strategies: `03-Strategies/`
    - Projects: `03-Projects/`
    - Coordination: `11-Mess Hall/`
    - Daily Logs: `08-Daily/`

## 🔄 Agent Workflow
1. **Consult before acting**: Check the vault for existing templates, presets, or historical decisions before proposing a new path.
2. **Commit after deciding**: Once a decision is finalized in a conversation, update the corresponding atomic note and YAML status.
3. **Clean up**: Use the nightly sweep cron to archive stale notes based on `last_updated` and `status`.

## 📬 Inbox Protocol
- The `00-Inbox/` folder is for cross-agent handoffs and items requiring Jordan's approval.
- Green Room discussions that reach a conclusion must produce a note in `00-Inbox/` with a clear action item and owner.
- Jordan reviews Inbox items and moves them to the appropriate department folder.

## 🔄 "Update the Brain" = Full Sync
When Jordan says "Update the Brain," this triggers a three-step atomic operation:
1. **Vault Commit**: Finalize all atomic notes, metadata headers, and wikilinks in the Obsidian vault.
2. **Skills Sync**: Mirror any newly developed skills or procedural updates into the `/skills/` directory.
3. **GitHub Push**: Execute `git add .` → `git commit` → `git push` to the private Gentech-Labs brain repo.

Git repo must be initialized at `/root/vaults/gentech/` if not already done. Use `.gitignore` for `.env` files and raw API keys.

## 🎙️ Voice Message Protocol
- For any message longer than ~3 paragraphs, include a `text_to_speech` voice summary alongside the text.
- Requires `ELEVENLABS_API_KEY` set in the agent's `.env` file (not just memory).
- If TTS fails with "key not set" error, the key needs to be added to the shell environment AND the `.env` file of the relevant agent profile.

## 🛑 "Stay the Course" Protocol
- When Jordan sends a link or inspiration mid-task, **queue it, don't interrupt**.
- Finish the current logic-block or tool-sequence, reach a natural stopping point, THEN process the new message.
- Never drop an active task to chase a new link.

## 📊 "Direct Answer" Mandate
- Every Green Room or Strategies discussion must end with a **direct, definitive answer or recommendation** — no open-ended technical threads.
- Before reporting back to HQ, check the Brain/Inbox for pending approvals or project constraints.
- This ensures the team arrives at a conclusion, not just more questions.
