# Labs Queue — Active Tasks

## 🔴 Priority 1: AgentNFT + Marketplace Contracts
**Status:** In Progress — Core Contracts Done ✅
**Assigned:** Dmob
**Created:** 2026-04-18

### What We're Building
- AgentNFT (ERC-721) — each bot/vault is an NFT with on-chain metadata ✅
- AgentMarketplace — list/buy/sell bots, platform fee (5%), creator royalty (2%) 🔄
- AgentVault — holds gas reserves + trading capital, owned by NFT holder ✅
- Lifecycle states: Created → Active → Paused → Listed → Sold → Closing → Closed ✅

### Spec Documents
- `02-Labs/Agent-Lifecycle-Marketplace.md` — full architecture
- `02-Labs/DeepTutor-DeFi-Integration.md` — product integration
- `02-Labs/Monetization-Brainstorm.md` — pricing model

### Decisions Locked In
- Chain: Avalanche C-Chain (multi-chain later)
- Auth: Wallet-based
- Revenue: Swap fees + $5-10 launch + marketplace 5%
- Free tier: Education + analysis + tracking

### Completed
- [x] AgentNFT contract (ERC-721 + metadata + lifecycle)
- [x] AgentVault contract (gas reserve + token management)
- [x] Foundry tests — 40/40 passing
- [x] Gas optimization (optimizer=200 runs)

### Next Steps
- [ ] Build marketplace contract (list/buy/sell + fees)
- [ ] Security review before any deployment
- [ ] NatSpec documentation on all public functions
- [ ] Deployment scripts for Avalanche testnet

---

## 🟡 Priority 2: ETHGlobal Open Agents
**Status:** In Progress
**Deadline:** May 3
**Plan:** `02-Labs/ETHGlobal-Open-Agents-Plan.md`

---

## 🟢 Priority 3: Retro9000 Grant
**Status:** Planning
**Plan:** `/tmp/retro9000-grant-outline.md`
