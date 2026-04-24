# AgentEscrow Project — Overview

**Status:** 🟢 Active — scaffolded, core contract drafted
**Repo:** https://github.com/ProtoJay4789/agent-escrow
**Started:** April 16, 2026
**Related:** [[Kite-AI-Hackathon-2026]] [[x402-Research]] [[Retro9000 Grant]]

## What It Is
AI-validated escrow with x402 payments. Agents pay for services, AI validators check quality, smart contract releases funds. Trustless, autonomous, on-chain.

## Current State
- ✅ GitHub repo created and pushed
- ✅ Core AgentEscrow.sol contract (USDC + EIP-712)
- ✅ Foundry config for Avalanche deployment
- ✅ README with architecture and roadmap
- 🔜 Foundry dependency install (OpenZeppelin)
- 🔜 Contract tests (Dmob territory)
- 🔜 x402 payment integration
- 🔜 Agent identity (ERC-8004)

## Team Assignments
- **YoYo:** Research, strategy, project coordination
- **Dmob:** Contract hardening, testing, deployment
- **Desmond:** Documentation, demo video, pitch narrative
- **Gentech:** Integration with Retro9000 grant, positioning
- **Vanito:** Collaborator — TBD on role

## Key Resources
- x402 Research: `/root/Documents/Obsidian Vault/05-Learning/x402-Research.md`
- Dexter SDK v3.0: `@dexterai/x402`
- Circle Arc Escrow: Reference implementation
- ERC-8004: Agent Registration standard
- ERC-8183: Agent Jobs standard

## Strategic Position
- **Modular hackathon system:** Best tool per layer, no vendor lock-in. Each hackathon gets a different modular combo — we adapt to the sponsor's stack.
- **L5 + L4 (Escrow/Enforcement):** GenLayer Python — native AI dispute resolution, fastest demo path
- **L3 + L2 (Brain/Risk):** Beam Cloud — stateful bots, fast inference (pending SDK recon)
- **L1 (Fee/LP):** AVAX Solidity — chain ownership, x402, ERC-8004 (endgame)
- **Hackathon approach:** Build L4+L5 on GenLayer, wire L3+L2 to Beam, frame L1 as roadmap
- Monitor what competitors submit
- Core primitive for the agentic economy

---

#project:agent-escrow #status:active
