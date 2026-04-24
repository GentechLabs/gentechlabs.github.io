---
name: gentech-workflow-management
description: Management of the specialized multi-agent communication and reporting workflow for GenTech agency.
---

# GenTech Workflow Management

## Overview
This skill defines the operational norms and communication protocols for the GenTech multi-agent team to ensure high signal-to-noise ratio and consistent delivery to the user.

## Communication Protocols

### 1. The "Direct Answer" Rule
When agents collaborate in the Green Room or Mess Hall, the interaction must not end with a summary of the discussion. 
- **Action**: Every sequence of agent-to-agent coordination MUST terminate with a consolidated, clear, and actionable "Direct Answer" delivered to the user in HQ.
- **Goal**: Eliminate the need for the user to piece together the final decision from a thread of agent discussions.

### 2. The "No-Interrupt" Policy
To maintain deep-work focus and avoid fragmented task states:
- **Behavior**: When the user sends new messages, links, or tools while an agent is in the middle of a task, the agent should acknowledge and queue the message but **NOT** switch contexts immediately.
- **Execution**: Complete the current task to a logical stopping point, then pivot to the queued messages.

### 3. Reporting & The Master Digest
- **Morning Brief**: A single "Master Digest" delivered daily at 6:30 AM EST.
- **Content**: Aggregates key decisions, blockers, and pending tasks from all department groups (Gentech, YoYo, DMOB, Desmond) from the previous 24 hours.

## Vault & Memory Management

### 1. The Brain (Obsidian) as Truth
- All high-level workflows, decision logs, and agent behaviors must be documented in the Obsidian vault.
- Updates to workflows should be reflected in `00-Working-Memory.md` or equivalent master docs.

### 2. Vault Maintenance
- Periodic "Vault Surgeon" audits are required to identify outdated notes, stale requirements, or redundant documentation.
- Proposed deletions or updates must be flagged for user approval.

## Model Configuration
- **Default (All Agents)**: GLM-5.1 via Ollama Cloud (switched from gemma4:31b due to 429 rate limits).
- **Specialist Override**: If a task requires a specialized model (e.g. coding, reasoning), agents may invoke a task-specific model for that job only, then return to baseline.
- **Potential Specialist Models**: qwen-coder (DMOB coding), deepseek-v3.1 (YoYo reasoning).
- **Config Location**: Each agent's model is set in their profile's `config.yaml` (`default:` field).

## Collaborators
- **Vanito** (8774981477) — Music production. In GenTech Entertainment + GenTech Strategies (NOT HQ).
- **Dadrian** (6842745552) — Strategies/Entertainment. In GenTech Entertainment + GenTech Strategies (NOT HQ).
- **Rule**: HQ is Jordan + AI agents only. Collaborators are in the department groups.

## "Update the Brain" = Double Action
When Jordan says "Update the Brain":
1. **Update Obsidian**: Commit changes to the vault.
2. **Sync GitHub**: Push those changes to the master Brain repo (once root Git is initialized).

## Inbox System
- **Location**: `/root/vaults/gentech/09-Collaboration/Inbox.md`
- **Purpose**: Pending approvals, handoffs, and items Jordan needs to review.
- **Rule**: Green Room/Mess Hall outputs that require Jordan's sign-off go here.

## Environment Notes
- **Hermes .env**: `/root/.hermes/.env` (top-level, NOT profile-level).
- **Tilde (`~`) does NOT expand** in terminal() calls — always use `/root/.hermes/` explicit paths.
- **Duplicate keys in .env**: Can cause conflicts. Clean duplicates immediately when found.
- **ELEVENLABS_API_KEY**: Must be in `.env` AND the environment must refresh before TTS works.

## Core Market Thesis
- **"The 4-year BTC cycle is dead."** News, tariffs, SEC rulings, ETF flows, and geopolitical events now drive markets — not technical indicators alone.
- **Implication for GenTech:** AgentEscrow's real value is *real-time risk response* (auto-withdraw on thesis-breaking news). YoYo's role shifts from cycle analysis to news alpha + sentiment detection.
- **Hackathon narrative:** "The cycle is dead. Agents that react to news in real-time are the new edge."
- **Status:** 🟢 Core thesis — integrate into all pitches.

## Accessibility
- **Voice Integration**: Long or complex updates should be accompanied by a TTS (Text-to-Speech) voice bubble to support the user's mobile/on-the-go consumption.
- **TTS Troubleshooting**: If TTS fails after adding a key to `.env`, the running process may need a restart to pick up the new environment variable.
