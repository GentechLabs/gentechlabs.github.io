# Modular Swap Matrix — ARC → Kite → ETHGlobal

**Principle:** Same core AgentEscrow architecture. Only adapters, deployment targets, and demo narratives change.

## 🔒 SHARED CORE (Build Once, Submit Everywhere)

| Component | File | Status |
|-----------|------|--------|
| AgentEscrow.sol | Core escrow logic | ✅ Built (40/44 tests passing) |
| Task lifecycle | create → claim → complete → release | ✅ Built |
| Dispute resolution interface | validateAndRelease() / dispute() | ✅ Built |
| EIP-712 signatures | Gas-efficient approvals | ✅ Built |
| Foundry project structure | `src/`, `test/`, `script/` | ✅ Built |
| Content framework | Video script, pitch, README templates | ✅ Drafted (Desmond) |

---

## 🔄 SWAP SURFACE PER HACKATHON

### ARC Hackathon (Apr 25) — $10K

| Layer | What | Why |
|-------|------|-----|
| **Payment adapter** | Circle x402 protocol + Arc nanopayments | Sub-cent agent commerce |
| **Chain** | Arc network (Circle USDC settlement) | Nanopayment viability |
| **Enforcement** | Basic validator interface (no GenLayer) | Keep it simple for ARC |
| **Demo narrative** | "Sub-cent transactions between agents" | Focus on nanopayments |
| **Content** | ARC video script + pitch (done) | Ready to record |

**What Dmob swaps:**
- Wire x402 payment middleware into escrow flow
- Deploy to Arc testnet (not 0G)
- Simplify dispute resolution to basic validator check

**What Jordan does:**
- Record 2-min demo video using ARC script
- Submit to lablab.ai by Apr 25

---

### Kite AI Global (Apr 26) — TBA

| Layer | What | Why |
|-------|------|-----|
| **Payment adapter** | Standard ETH/USDC (no x402 needed) | Kite doesn't require nanopayments |
| **Chain** | Kite AI testnet | Hackathon requirement |
| **Enforcement** | GenLayer intelligent contracts (subjective consensus) | Best fit for AI dispute resolution |
| **Demo narrative** | "AI judges contract quality, not just conditions" | Focus on GenLayer enforcement |
| **Content** | Kite README + demo outline (done) | Ready to deploy |

**What Dmob swaps:**
- Fix GenLayer test fixtures (conftest.py)
- Swap x402 adapter → GenLayer enforcement layer
- Deploy to Kite testnet
- Write GenLayer dispute resolution integration

**What Jordan does:**
- Record 2-min demo video using Kite outline
- Submit to Kite portal by Apr 26

---

### ETHGlobal Open Agents (May 3) — $50K

| Layer | What | Why |
|-------|------|-----|
| **Storage** | 0G decentralized storage (Merkle trees) | Primary track: $15K |
| **Chain** | 0G testnet (Chain ID: 16602) | 0G integration requirement |
| **Execution** | KeeperHub MCP + check-and-execute | Secondary track: $5K |
| **Enforcement** | Full AgentKeeper + dispute resolution | Multi-layer demo |
| **Demo narrative** | "Agents that coordinate autonomously on-chain" | Focus on 0G + KeeperHub |
| **Content** | ETHGlobal README, pitch, video script (done) | Ready to deploy |

**What Dmob swaps:**
- Add 0G Storage integration (@0glabs/0g-ts-sdk)
- Add KeeperHub MCP integration
- Deploy to 0G testnet (Chain ID: 16602)
- Wire AgentKeeper for autonomous execution

**What Jordan does:**
- Join ETHGlobal Discord, claim 0G tokens, get KeeperHub API key
- Record 3-min demo video using ETHGlobal script
- Submit by May 3, 4 PM UTC

---

## 📊 Quick Comparison Table

| Feature | ARC | Kite AI | ETHGlobal |
|---------|-----|---------|-----------|
| **Chain** | Arc | Kite AI | 0G testnet |
| **Payment** | x402 nanopayments | Standard ETH/USDC | Standard ETH/USDC |
| **Enforcement** | Basic validator | GenLayer AI consensus | KeeperHub MCP |
| **Storage** | On-chain only | On-chain only | 0G Merkle storage |
| **Core contracts** | ✅ Shared | ✅ Shared | ✅ Shared |
| **Demo video** | 2-min (script done) | 2-min (outline done) | 3-min (script done) |
| **Deadline** | Apr 25 | Apr 26 | May 3 |

## 🎯 Build Sequence

```
1. ARC: Wire x402 → deploy Arc → record video → submit Apr 25
2. KITE: Swap x402→GenLayer → fix conftest.py → deploy Kite → record → submit Apr 26
3. ETHGLOBAL: Add 0G Storage + KeeperHub → deploy 0G → record → submit May 3
```

---

#modular #swap-matrix #hackathon #strategy
