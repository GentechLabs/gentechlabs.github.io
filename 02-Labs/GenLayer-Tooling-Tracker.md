# GenLayer Tooling Tracker
**Last Updated:** 2026-04-25  
**Owner:** DMOB — Head of Labs

---

## Deploy & Deploy Tracking

| Tool | Status | Link | Notes |
|------|--------|------|-------|
| **Shipyard** | ✅ Active | https://gen-shipyard.vercel.app | No-CLI, web-based GenLayer deploy. AI demoed integration (Antigravity agent). Same builder as genscope (@gaymused). |
| **GenLayer CLI** | 🟡 In Use | `genlayer-cli` | Standard Foundry-based workflow. anchor-solana-escrow repo uses. |
| **GenLayer SDK** | 🟡 In Use | `/root/vaults/gentech/02-Labs/GenLayer-SDK/` | Local docs + templates. |

---

## DevOps & CI/CD

| Tool | Status | Link | Notes |
|------|--------|------|-------|
| **Foundry** | ✅ Active | `forge`, `cast`, `anvil`, `chisel` | Standard for GenLayer EVM development. |
| **Anchor (Solana)** | ✅ Active | `anchor` v1.0 | Used for agent-escrow-solana — built against Ed25519 precompiles. |

---

## AI Agent Integration

| Agent | Status | Integration Point | Notes |
|-------|--------|-------------------|-------|
| **Antigravity** (AI coding agent) | 🚀 Demoed | Shipyard contract → frontend | Built EVMValidator in <10s end-to-end. Shows agent-native GenLayer dev experience. |
| **Hermes Agents** | 🟡 Planning | x402/agent-payment routing | Consider agent钱包 integration for chain-agnostic payments. |

---

## Hackathon Tools

| Tool | Status | Link | Notes |
|------|--------|------|-------|
| **Kite AI Hackathon** | 🎯 Priority | May 11, 2026 | Priority GenTech participation. Shipyard could accelerate our submissions. |
| **Novel Track** | 🎯 Priority | Shipyard-friendly | Emphasize UI/UX and rapid iteration — Shipyard aligns. |

---

## Tracking Notes

- ✅ Shipyard entry added 2026-04-24 by @encrypt_wizard
- 📝 AI agent integration detail added here 2026-04-25 — Antigravity demo shows agent-native GenLayer dev path.
- 🚀 Priority: Shipyard + Kite AI Hackathon submission path.

---

## Roadmap

- [ ] Add Shipyard as default deploy option in GenLayer SDK docs
- [ ] Test Antigravity → Shipyard → frontend integration path
- [ ] Document agent wallet payments (x402) integration for Shipyard deployments

|#GenLayer #tooling #deployment #hackathon #agent-integration #Shipyard |
