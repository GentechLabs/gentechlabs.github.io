User: ProtoJay4789 (GitHub), Gentech (Gentech-Labs org). Goal: Leave Amazon by Q4 2026 via hackathons → Code4rena → remote role OR $3-5k/mo auditing. 2 hrs/day study at Amazon. Philippines trip Sep-Oct for remote lifestyle test. Collabs: Vanito (8774981477, music), Dadrian (6842745552, strategies) — Entertainment+Strategies only, NOT HQ. "Update the Brain" = update Obsidian + sync GitHub.
§
Model map (Apr 2026, all on Ollama Cloud): Gentech=kimi-k2.6 (swarm orchestration, multimodal), DMOB=qwen3-coder-next (coding), YoYo=glm-5.1 (reasoning, cost-efficient), Desmond=glm-5.1 + qwen3.5:35b for vision. Config files at `/root/.hermes/profiles/{name}/config.yaml`. Vision in main config at `/root/.hermes/config.yaml`.
§
.env at `/root/.hermes/.env` (top-level, NOT profile-level). In terminal(), `~` does NOT expand — always use `/root/.hermes/` explicit paths. Vault: `/root/vaults/gentech/`.
§
x402 ecosystem: Agentic Market ($49.8M vol, Base). GenLayer: 76 repos, SDKs genlayer-py + genlayer-js. Apolo shipped x402+escrow+GenLayer+BNB — BNB-only competitor to AgentEscrow. Cron `582e20252034` tracks x402 bi-weekly. GenLayer Builder Program = HIGH PRIORITY.
§
Multi-agent workflow v1.1: Orchestration via Green Room/Mess Hall, final results synced to Obsidian 'Inbox' for approval. Master Digest delivered daily at 6:30 AM EST.
§
Market Thesis: The 4-year BTC cycle is dead; markets are now news-driven. AgentEscrow's value prop is real-time risk response to news events.
§
Model stack: glm-5.1 baseline (Apr 24). ALL configs permanently switched. Specialist overrides ready: Gentech→kimi-k2.6, DMOB→qwen3-coder-next, Vision→qwen3.5:35b. Cron e00b46103b08 also updated.
§
Kimi K2.6 saved to vault at `06-Content/AI-Model-Notes/Kimi-K2.6.md`. No Obsidian CLI or git repo in vault — files are written directly. "Update the Brain" = write to vault folders.
§
ElevenAgents SDK v1.0 (Apr 23): useConversationClientTool = dynamic tool registration from React components. Key for ElevenHacks #6. Research note in vault: 02-Labs/ElevenHacks-SDK-v1-Research.md. Google Cloud Rapid Agent Hackathon closes Jun 11 — added to trackers.