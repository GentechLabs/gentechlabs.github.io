---
name: gentech-workflow-management
description: Management of the multi-agent coordination, reporting, and communication protocols for the GenTech Agency.
triggers:
- "workflow update"
- "communication protocol"
- "agent coordination"
- "morning brief"
- "non-interrupt protocol"
---

# GenTech Agency Workflow Management

This skill defines the operational standards for communication and task execution across the GenTech agent collective.

## Core Protocols

### 1. Communication Flow
- **The Chain**: Specialists $\rightarrow$ Green Room (Coordination) $\rightarrow$ HQ (Consolidated Delivery).
- **Closing the Loop**: Every conversation must culminate in a **Direct Answer** or consolidated result.
- **Approval Sync**: Before delivering a final result, agents must cross-reference the Obsidian Vault for pending approvals, constraints, or historical presets.
- **Voice Integration**: Long updates, reports, or complex analyses must be accompanied by a voice message (TTS) for the user's convenience.

### 2. Task Execution (Non-Interrupt Protocol)
- **State Preservation**: If a user sends a message while an agent is mid-task, the agent must **stay on the current task**.
- **Queuing**: New messages are queued and addressed only at a natural stopping point or once the current P0 item is resolved.
- **Notification**: Avoid "Interrupting current task" messages; simply execute and report back once the queue is reached.

### 3. Intelligence & Maintenance
- **Morning Intelligence Brief**: A scheduled 06:30 AM EST summary synthesizing the last 24 hours of discourse across all groups (TL;DR, Decision Log, Pending Actions).
- **Vault Janitor**: A recurring maintenance job to scan the Obsidian vault for stale notes, outdated TODOs, and redundant files, proposing a cleanup list.
- **Brain Optimization**: Shift from monolithic files to Atomic Notes and Maps of Content (MOCs) to optimize LLM context windows.

## Implementation Steps
1. **Sync to Brain**: All workflow changes must be documented in `/root/vaults/gentech/00-System/Workflow_vX.md`.
2. **Audit Cronjobs**: Use `cronjob(action='list')` to ensure intelligence and maintenance jobs are active.
3. **Action Listing**: Maintain a "Pending Actions" list in the vault for user-side task completion (e.g., sign-ups).

## Pitfalls
- **Over-communication**: Avoid posting raw specialist coordination in HQ; use the Green Room.
- **Context Exhaustion**: Avoid reading massive files into context; use MOCs to target specific atomic notes.
