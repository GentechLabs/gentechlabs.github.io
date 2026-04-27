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

---

## 🟡 Priority 4: Swarms Solana Adapter
**Status:** v0.1.0 Pushed ✅ — In Polish
**Repo:** `agent-escrow-solana/swarms-solana-adapter/`
**File:** `02-Labs/Swarms-Solana-Adapter.md`
**Source:** Jordan directive in HQ thread 22473

### Completed (v0.1.0)
- [x] `pyproject.toml` — pip package scaffold, MIT license, Python 3.10+
- [x] `client.py` — async Anchor client (315 LOC), 7 instructions wrapped
- [x] `accounts.py` — PDA derivations (config, escrow, vault)
- [x] `swarms_shim.py` — `SwarmsEscrowAdapter` + `EscrowResult` (140 LOC)
- [x] `idl.json` — bundled Anchor IDL (program `DKx16ix...`)
- [x] CLI example (`example_worker.py`)

### Gaps to Close
- [ ] `Dmob`: Fix `tx_signature` TODO in shim (always None)
- [ ] `Dmob`: Re-add Swarms `@tool` decorators (deleted in refactor)
- [ ] `Dmob`: Clarify `anchorpy` dep vs "no runtime dep" in README
- [ ] `Dmob`: `pytest` suite against devnet or mocked RPC
- [ ] `Dmob`: Env-overridable `PROGRAM_ID` (currently hardcoded)
- [ ] `Desmond`: Draft Swarms marketplace listing pitch
- [ ] `YoYo`: x402 middleware spec (intercept Swarms billing → AAE escrow)

### Blockers for v0.2.0
- Devnet program deployment (currently has placeholder ID)
- Live end-to-end test with funded wallet

### Next Steps
1. `Dmob`: Close polish gaps above (1–2 days)
2. `Desmond`: Marketplace fee research + listing pitch
3. `YoYo`: x402 bridge design doc

