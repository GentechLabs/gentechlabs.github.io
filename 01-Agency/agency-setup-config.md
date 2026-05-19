# GenTech Agency Setup & Configuration Registry

## Infrastructure
- Vault: `/root/vaults/gentech/`
- Backup: Synced to `Gentech-Labs/hermes-brain` (Private)
- Cron: 30+ jobs managing briefings, health checks, and vault maintenance.

## Agent Configuration
- **Gentech (HQ)**: Orchestrator, Routing, Voice-pairing for long messages.
- **YoYo (Strategies)**: Investment analyst, DeFi research, LP monitoring.
- **DMOB (Labs)**: Smart contract dev, security auditor, a-priori build lead.
- **Desmond (Creative)**: Content pipeline, brand identity, narrative wrapper.

## Core Operational Workflow
1. **Routing Flow**: Jordan (HQ) $\rightarrow$ Gentech $\rightarrow$ Specialist Group.
2. **Coordination**: Discussion in Mess Hall $\rightarrow$ One consolidated **Direct Answer** to HQ.
3. **Queue System**: Specialists complete current tasks to a logical stopping point before processing new "queued" inputs from Jordan.
4. **Brain-First**: All decisions must be codified in the Obsidian vault immediately.
5. **Approval Loop**: Results are cross-referenced with the Brain for approval/update markers.
6. **Reporting**: Master Morning Digest generated daily at 6:30 AM EST.

## Model Configuration (Apr 23, 2026)
- **HQ Model:** `kimi-k2.6` (Ollama Cloud) — Multimodal + thinking + swarm orchestration + vision built-in.
- **Labs Model:** `qwen3-coder-next` (Ollama Cloud) — Coding-focused for smart contract dev.
- **Vision Model:** `kimi-k2.6` (handles vision natively, no separate model needed).
- **Current State:** All agents and crons on `gemma4:31b` (switching tonight).
- **Compatibility:** All agent configs must remain compatible with Ollama Cloud models.
- **ALL 30 cron jobs** currently use `gemma4:31b` — must be updated when model changes.
- **Vision auxiliary** in config.yaml is set to `provider: auto, model: ''` — needs explicit multimodal model.
- **Tiered Model Strategy (Optional):** Specialist tasks can invoke a specific model for best quality:
  - Orchestration/HQ: `kini-42-thinking` (multi-agent reasoning)
  - Dev/Labs: `open-3-coder-next` (smart contract precision)
  - Content/Speed: `gemini-3-flash-preview` (high-volume content extraction)
- **Protocol:** Jordan handles the model switch in config. Agents can request a model swap for a specific task if it improves output quality.

## Skill Management
- All specialized procedural knowledge is saved to `~/.hermes/profiles/gentech/skills/`.
- Backup of skills is consolidated within the Brain GitHub repository.
