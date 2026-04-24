---
name: gentech-agent-orchestration
description: Standard operating procedure for high-scale multi-agent coordination and system maintenance within the GenTech Agency ecosystem.
triggers:
- "coordinate agents"
- "establish workflow"
- "agent communication protocol"
- "systematic brain sync"
---

# GenTech Agent Orchestration Protocol

This skill defines the operational standards for coordinating the Specialist agents (DMOB, YoYo, Desmond) and the lead (Gentech) to maximize reasoning quality and minimize API bottlenecks.

## 1. Communication Hierarchy
A three-tier communication flow is used to prevent noise in the main channel and ensure vetted outputs.
1. **Specialist Layer**: Agents work in their respective domain groups (Labs, AAE, Security).
2. **Coordination Layer (Green Room)**: Specialists coordinate and synthesize results in the Green Room.
3. **Command Layer (HQ)**: One consolidated, vetted answer is delivered to the user in HQ.

## 2. Operational Directives
- **Non-Interrupt Protocol**: If the user messages mid-task, agents must NOT interrupt. Messages are queued and processed only at natural stopping points.
- **The Closing Loop**: Every response must end with a **Direct Answer/Result**. 
- **Approval Sync**: Before the final answer, agents must cross-reference the Obsidian Vault (`/00-System/Inbox`) for pending approvals or constraints.
- **Voice Reporting**: Detailed analysis, long reports, or critical updates must be accompanied by a voice message (ElevenLabs TTS).

## 3. Model Tiering (Anti-429 Strategy)
To avoid rate limiting (Error 429) and optimize cost/reasoning, use a Tri-Tier architecture:
- **Baseline (General/Coordination)**: GLM 5.1 (Global standard for baseline reasoning).
- **Precision (Audit/Logic)**: `gpt-5-coder` or `deepseek-v3.1` (Activated for security audits, complex architecture, or high-reasoning tasks).
- **Routine (Mechanical)**: `gemini-3-flash` (Activated for Morning Briefs, Vault maintenance, and summaries).

## 4. Brain (Vault) Maintenance
- **Morning Intelligence Brief**: Recurring job at 06:30 AM EST synthesizing the last 24h of discourse.
- **Vault Janitor**: Weekly job to scan for stale/outdated notes.
- **Brain Sync**: The command "Update the Brain" triggers a synchronized push of the Obsidian Vault and agent configs to the `hermes-brain-backup` GitHub repo.
- **Atomic Structure**: Move toward Maps of Content (MOCs) and Atomic Notes to keep context windows lean.

## 5. Collaborator Access
- **Specialist Groups**: Open to vetted collaborators (e.g., Vanito, Dadrian).
- **HQ Group**: Restricted (User and agents only).

## Verification
- Check for "Direct Answer" at the end of turn.
- Verify if a long response has a corresponding voice file.
- Ensure the current model matches the task tier (e.g., using a flash model for a summary).
