# 🧠 GenTech Brain SOP: Knowledge Management Standard

## 🎯 Objective
Transform the Obsidian vault from a storage unit into a strategic engine by ensuring all agent contributions are atomic, structured, and interconnected.

## 🛠️ The Three Pillars of the Brain

### 1. Atomic Note-Taking (Zettelkasten)
- **Rule**: One concept per note.
- **Action**: Do not create "Mega-Notes." If a note covers two separate projects or ideas, split it into two atomic notes.
- **Goal**: Reduce "noise" in agent retrieval.

### 2. Structured Metadata (YAML Headers)
Every clinical/strategic note MUST start with the following metadata block:
```yaml
---
status: [active | pending | archived]
priority: [P1 | P2 | P3]
owner: [YoYo | DMOB | Desmond | Gentech]
last_updated: YYYY-MM-DD
tags: [tag1, tag2]
---
```
- **Action**: Update these headers whenever the status or priority shifts.

### 3. The Knowledge Web (Wikilinks)
- **Rule**: Never leave a concept isolated.
- **Action**: Use `[[Wikilinks]]` to connect a note to its parent strategy, related tools, or dependent tasks.
- **Example**: `Bags-Hackathon.md` $\to$ `[[Agentic-Commerce-Pattern]]`

## 📂 Departmental Routing
- **Strategies**: `/03-Strategies/`
- **Projects**: `/03-Projects/`
- **Daily/Mess Hall**: `/08-Daily/`, `/11-Mess Hall/`

## 💾 Persistence & Synchronization
- **Working Memory**: The local Obsidian Vault (`/root/vaults/gentech/`) is the active working environment.
- **Permanent Archive**: The GitHub repository `Gentech-Labs/hermes-brain-backup` serves as the authoritative backup.
- **Sync Trigger**: Whenever "Update the Brain" is invoked, agents must perform a full synchronization of the vault, updated agent behaviors, and new skills to the GitHub backup repo.
- **Verification**: Maintenance cycles must verify that the GitHub archive reflects the current state of the local vault.
