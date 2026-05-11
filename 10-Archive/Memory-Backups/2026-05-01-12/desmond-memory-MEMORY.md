Inter-agent communication workflow (Jordan, Apr 2026): Green Room (09-Green Room/) = during active work (coordinate before speaking in groups). Mess Hall (11-Mess Hall/) = outside of work (status updates, general check-ins). All agents must sync with each other before posting in any group.
§
Approval workflow: When agents need Jordan's approval, create a note in 00-HQ/Approvals/ using the template (checkbox format). Green Room for debate → Approval note → Jordan checks off items. Template and README already exist in vault.
§
Stopping point protocol (Jordan, Apr 2026): When hitting a stopping point, ask Jordan what's next or check to-do list. If no reply in 10-20 min, audit work in vault, review code, or start extended discussions in Mess Hall. Don't sit idle.
§
Cron jobs for skills update (Jordan, Apr 2026): Two weekly jobs — Sunday 9 AM (dd5a156365f8) and 4 PM (ae7bb8a0d703). Script: ~/.hermes/scripts/skills-update-check.py. Output: 00-HQ/Approvals/.
§
AgentEscrow Solana Frontier (Colosseum) — deadline May 11. 4 Anchor programs scaffolded: AgentRegistry (World ID + Swig), JobEscrow (8-state, PDA vaults), Reputation (Metaplex soulbound NFTs), DisputeResolver. Devnet: 4kX9b9hytCTrC6qikjVpnWYrvDK7NG97qCUDUTk9fMmn. Repo: github.com/ProtoJay4789/agent-escrow. Creative deliverables saved to Colosseum-Frontier/ folder.
§
Jordan's wallet: [REDACTED_WALLET] (Avalanche C-Chain). Used for LFJ AVAX/USDC LP position monitoring. Config saved to 00-HQ/config/defi-lp-config.env. Added to d5-master-cron.py for on-chain position tracking.
§
hermes-kanban (Apr 2026): `kanban` CLI at /usr/local/bin/kanban. DB: /root/.hermes/kanban.db. Venv: /root/.venvs/kanban/. Board "Gentech HQ" seeded. Sync: `kanban sync --vault-dir /root/vaults/gentech`. Two bugs fixed: demo scoping, --archived filter.
§
User prefers humorous acknowledgment of inter-agent coordination mishaps (e.g., duplicate messages). Avoid over-apologizing; instead, use lighthearted self-awareness (e.g., 'Great minds think alike—or at least share the same cron job!').