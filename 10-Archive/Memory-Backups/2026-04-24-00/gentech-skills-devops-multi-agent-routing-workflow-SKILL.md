---
name: multi-agent-routing-workflow
description: Standardized protocol for routing requests through a multi-agent Telegram organization to ensure "Zero Noise" in HQ and "Max Signal" for the user.
---

# Multi-Agent Routing Workflow

## Trigger
When the user (Jordan) provides a request in the HQ group that requires specialist knowledge (Financials, Dev, Content) or requires a "behind-the-scenes" coordination between agents.

## Routing Map
- **Financials / Tokenomics / LP / Market Research** $\rightarrow$ **YoYo** (Strategies Group)
- **Smart Contracts / Audits / Dev / Security** $\rightarrow$ **DMOB** (Labs Group)
- **Content / Brand / Writing / Socials** $\rightarrow$ **Desmond** (Creative Group)

## The Execution Pipeline

### 1. Intake & Routing (Gentech)
- **Analyze**: Determine if the request is for the Coordinator or a Specialist.
- **Route**: Post a directive in the specialist's group: `"@AgentName, Jordan needs [X]. Context: [Y]. Please handle and report back to HQ."`
- **Close the Loop**: Tell Jordan in HQ: `"I've routed this to [Agent Name] in the [Department] group. I'll update you once they have a result."`

### 2. The "Sausage Making" (Green Room / Mess Hall)
- **Coordination**: Specialists discuss technical implementation, debate assumptions, and brainstorm in the `09-Green Room/` or `11-Mess Hall/`.
- **Inter-Agent Friction**: Encourage disagreement and stress-testing ideas in these spaces to avoid echo chambers.
- **Consolidation**: Once a consensus is reached, the lead specialist or Gentech synthesizes the result into a single, polished response.

### 3. Final Delivery (HQ)
- **The "Clean Signal"**: Deliver ONE consolidated, short answer to Jordan.
- **Checkboxes**: Use a checklist for deliverables so Jordan can "stamp" approvals quickly.
- **Stop-Point Protocol**: Update the `master-todo.md` and `Mess Hall` logs before switching tasks.

## New Protocols (Apr 23, 2026)

### The Direct Answer Rule
- Every internal discussion MUST end with a **concrete conclusion/decision**. No open-ended discourse.
- After the Direct Answer, **check the Brain/Vault** to determine if the result requires Jordan's formal approval.
- If approval is needed, route it to HQ via the `09-Green Room/` or `09-Collaboration/Inbox.md`.

### The Queue System (No Interruptions)
- When Jordan sends a new message while a specialist is mid-task, **DO NOT interrupt**.
- **Queue the input** and process it only after reaching a logical stopping point on the current task.
- This prevents "interrupting current task" noise and maintains workflow momentum.

### Brain Update = GitHub Sync
- "Update the Brain" is a dual-action command:
  1. Update the Obsidian vault (`/root/vaults/gentech/`).
  2. Push to GitHub (`Gentech-Labs/hermes-brain` repo) via backup script.
- Decision confirmed: consolidate all skills/config backups into the Brain GitHub repo (no separate repo).

### Voice Pairing
- Long messages or complex updates MUST be paired with a TTS voice bubble (ElevenLabs).
- Short status updates are text-only.

### Team Roster
- **Vanito** (8774981477): Strategies, Labs, Entertainment (music/DONNA AI collaborator)
- **Dadrian** (6842745592): Strategies, Labs, Entertainment (travel coordination)
- They are in the 3 specialist groups. NOT in HQ (HQ = Jordan + agents only).

### Model Configuration
- **Default:** GLM-5.1 via Ollama Cloud (migration in progress from Gemma 4).
- **Vision:** Must use a **multimodal model** (`qwen3.5`, `open-3.5`, or `kimi-k2.6`) for the `auxiliary.vision` section in config.yaml. GLM-5.1 is text-only — without a multimodal vision model, photos and videos will fail to process.
- **Context compression:** If conversations are long and "compressing" appears, switch to a model with a larger context window (like `deepseek-v3.1` or `qwen3.5`), or use the Brain-First Protocol (store details in Vault, send only the Direct Answer summary in chat).
- **Compatibility:** All agent configs must remain compatible with Ollama Cloud models.
- **Tiered strategy (optional per task):** Orchestration → `kini-42-thinking`, Dev → `qwen3-coder-next`, Content → `gemini-3-flash-preview`, Vision → `qwen3.5` or `open-3.5`.
- Jordan handles model switches in config. Agents can request a swap for specific tasks if it improves quality.
- **Config location:** `~/.hermes/profiles/gentech/config.yaml` under `model:` (main) and `auxiliary.vision:` (vision).

### Smart Routing for Links
- Links (especially from X) trigger "Smart Routing" — the agent in that group must immediately analyze, determine the required action, and execute.
- Work stays in the group where the link was posted UNLESS Jordan explicitly says "Bring this to HQ."
- Cross-departmental work is coordinated in Mess Hall/Green Room FIRST, then one consolidated answer back to the origin group.

### Morning Digest (Cron: b006812998df)
- Runs daily at 6:30 AM EST (11:30 UTC).
- Pools all 4 groups' history from the previous 24 hours.
- Outputs: The Recap, The Board (✅/⏳/🚨), The A-Priori Plan, and Urgent Flags.
- Old briefings (f8d7cf167b8a, 8459e3404aa7) have been removed — this is the single master digest.

### Market Thesis
- The 4-year BTC cycle is DEAD. Markets are now news-driven, not cycle-driven.
- M2/global money supply still valid, but halving-based strategies are obsolete.
- Implications: shift from cycle models to news-sentiment overlays; bug bounties + hackathons are more reliable than cycle-dependent DeFi yield.
- See `03-Strategies/4-Year-Cycle-is-Dead.md` for full thesis.

## Pitfalls & Rules
- **No HQ Noise**: Specialists must NOT respond in HQ unless explicitly asked.
- **No Direct Questions**: Specialists should not ask the user for clarification directly; they route the question back through Gentech.
- **No Interruptions**: Queue Jordan's inputs; finish current task first.
- **Model switches require config.yaml**: The Telegram /model command only changes the chat model. Always edit config.yaml directly for full backend model changes.
- **Pair long texts with TTS voice messages** when ElevenLabs is configured.
- **Consistency over Individualism**: All agents on GLM-5.1 by default; tiered models only for specialized tasks.
