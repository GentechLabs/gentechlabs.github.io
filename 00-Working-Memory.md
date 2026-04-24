# GenTech Multi-Agent Workflow v1.1
Last Updated: 2026-04-23

## 1. Communication Protocol
- **Internal Sync**: Agents discuss in 'Green Room' or 'Mess Hall' first to vet technical/creative details.
- **The 'Direct Answer' Rule**: Every multi-agent conversation MUST end with a consolidated "Direct Answer" sent to Jordan in HQ.
- **The 'No Interrupt' Policy**: Agents stay on current tasks until a stopping point is reached before processing new messages/links from Jordan.

## 2. The Brain (Obsidian Vault)
- **Source of Truth**: The vault is the primary reference for agent behaviors and project state.
- **Approval Sync**: Direct Answers are synced to the Brain for Jordan's final approval.
- **Maintenance**: A dedicated 'Vault Surgeon' cron job periodically reviews and prunes outdated notes.

## 3. Reporting & Briefings
- **Master Digest**: A single consolidated summary of all 4 groups delivered daily at 6:30 AM EST.
- **Voice Integration**: Long messages are accompanied by TTS voice bubbles for accessibility.

## 4. Model Configuration
- **Default (All Agents)**: GLM-5.1 via Ollama Cloud (switched from gemma4:31b due to 429 rate limits).
- **Specialist Override**: If a task requires a specialized model (e.g. coding, reasoning), agents may invoke a task-specific model for that job only, then return to baseline.

## 5. Agent Roles
- **Gentech**: Lead/Orchestrator.
- **YoYo**: Investor/Financial Intelligence.
- **DMOB**: Dev/Security/Auditor.
- **Desmond**: Creative/Content/Brand.

## 6. Collaborators
- **Vanito** (8774981477) — Music production, Entertainment group. In GenTech Entertainment + GenTech Strategies (NOT HQ).
- **Dadrian** (6842745552) — Strategies/Entertainment groups. In GenTech Entertainment + GenTech Strategies (NOT HQ).
