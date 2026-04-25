# Gentech Agent Workflow v2.1
Date: 2026-04-23 (Updated)

## 1. Communication Protocol
- **Specialists -> Green Room -> HQ**: Specialists coordinate in Green Room, then provide one consolidated answer in HQ.
- **Direct Answer Rule**: Every conversation must end with a clear, consolidated result/direct answer.
- **Approval Sync**: Before the final answer, agents must check the Obsidian Vault for pending approvals or constraints.
- **Non-Interrupt Protocol**: If the user sends a message mid-task, agents stay on current task and queue the new message for the next stopping point.

## 2. Core Model Architecture (Performance Layer)
- **Global Baseline**: All agents default to **GLM 5.1** to mitigate 429 rate limits and standardize reasoning.
- **Specialized Overrides**: For high-criticality tasks, specific models will be activated to ensure maximum quality:
    - **Security/Smart Contract Audits**: High-reasoning models (e.g., DeepSeek v3.1 or GPT-5-Coder).
    - **Creative/Multimedia**: Specialized creative models for audio/video.
    - **Routine/Maintenance**: Lightweight models (e.g., Gemini Flash) for Morning Briefs and Vault Janitor.

## 3. Reporting & Intelligence
- **Morning Intelligence Brief**: Runs 06:30 AM EST. Synthesizes last 24h of discourse across all 4 groups into a TL;DR, Decision Log, and Pending Actions list.
- **Voice Updates**: Long updates/reports must be accompanied by an ElevenLabs voice message.
- **Stopping Point Protocol**: When blocked, proactively prompt Jordan with next to-do item — "Hey Jordan, I could be working on this next while we figure this out." Never idle silently.

## 4. Brain (Vault) Management
- **Structure**: Moving toward MOCs (Maps of Content) and Atomic Notes.
- **Maintenance**: Weekly 'Vault Janitor' cron job to identify and propose deletion of stale/outdated notes.
- **Inbox System**: All formal hand-offs and approval requests are placed in `/00-System/Inbox`.
- **Departmentalization**: Each agent group has a dedicated folder in the vault.

## 5. Execution State
- Focus on Trade Off platform and Solana Hackathons (Frontier, Bags App, Hermes Creative).
- Use $TECH token as a sink for fee discounts.
