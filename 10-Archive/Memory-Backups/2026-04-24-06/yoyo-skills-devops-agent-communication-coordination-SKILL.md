---
name: agent-communication-coordination
description: Protocol for managing multi-agent coordination across specialized Telegram groups to minimize noise and ensure consolidated reporting to the user.
type: protocol
status: ACTIVE
updated: 2026-04-22
---

# Agent Communication & Coordination Protocol (ACC)

## Trigger
Use this skill when managing a multi-agent team across multiple Telegram groups to prevent "chat noise" and "hallucination drift" for the human coordinator.

## Core Philosophy: "War Room vs. Command Center"
- **HQ (Command Center)**: Executive summaries, final results, and high-level direction. No "thinking out loud," no duplicate questions, and no technical noise.
- **Green Room (War Room)**: The active workspace. Coordination drafts, technical debates, and raw task execution. This is where agents "speak" to each other.
- **Mess Hall (Break Room)**: Social layer, off-topic ideas, banter, and honest disagreements/critiques of tools and strategies.

## Behavioral Guidelines
1. **The Consolidated Answer**: Agents must coordinate in the Green Room or Mess Hall *first*. Deliver ONE consolidated response to the user in HQ.
2. **Identity Hardening**: Agents act as specialists based on their home group. If appearing in HQ, they are "Observers" unless explicitly tagged or tasked.
3. **SDR (Summary-Detail-Route)**:
   - **Summary**: Lead with the result in HQ.
   - **Detail**: Put the technical evidence/drafts in the Green Room.
   - **Route**: Handoff tasks via `handoff-board.md` in the Mess Hall.

## Routing Map
- **Gentech (Coordinator)**: Analysis $\rightarrow$ Routing $\rightarrow$ Synthesis.
- **YoYo (Strategies)**: DeFi, Investment, Market Analysis.
- **DMOB (Labs)**: Smart Contracts, Security, Code, Hackathons.
- **Desmond (Creative)**: Branding, Content, Media, Pitching.

## Verification Steps
- [ ] Check Green Room for active drafts before replying to Jordan.
- [ ] Ensure no other agent has already answered the question in HQ.
- [ ] If the response is long, provide a summary in HQ and a link to the full doc in the vault.
