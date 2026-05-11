# Billions Network (ERC-8004) vs AAE — Comparison & Opportunity Analysis
*YoYo — April 24, 2026*

---

## What Billions Network Is

**8004scan.io** — Live multi-chain agent discovery platform built on ERC-8004.

**Traction (as of Apr 24, 2026):**
- **179,095** registered agents (live API)
- **232,187** feedback submissions
- **140,008** active users
- **1,240** daily new agents
- **#3** across all agent networks — weeks after launch
- **55** supported chains (incl. Solana mainnet + devnet)

**Architecture:**
- **Identity Registry** — per-chain contract for agent identity/verification
- **Reputation Registry** — per-chain contract for feedback/reputation scores
- **ERC-8004 standard** — agent registration/metadata standard
- **Multi-chain** — 55 chains including Ethereum, Base, BSC, Celo, Monad, Solana, Avalanche, Billions Network (their own L2, chain ID 45056)
- **Protocol support tracking** — MCP (13,738 agents), A2A (11,751 agents), OASF
- **x402 micropayments** — optional per-agent flag
- **REST API + semantic search** — public API, 10 req/min anonymous, up to 2,000 req/min enterprise

**Top chains by agent count (Apr 24):**
- BSC: 67,218 agents | Base: 26,862 agents | Ethereum: 14,827 agents | Celo: 9,020 agents | Monad: 8,346 agents | MegaETH: 8,271 agents | Billions (own L2): 16,224 agents

**Key insight:** They are NOT building the agent economy layer — they are building the **identity/verification infrastructure** that an agent economy sits on top of.

---

## Our AAE Architecture

From `aae-contracts` repo:

| Component | Purpose | Status |
|-----------|---------|--------|
| `AgentRegistry.sol` | On-chain agent registration (skills, pricing, reputation) | Built |
| `AgentNFT.sol` | Premium tier NFTs with inactivity burn | Built |
| `JobEscrow.sol` | Job payment escrow + completion tracking | Built |
| `StrategyVault.sol` | Yield/revenue sharing for stakers | Built |
| `AgentTokenFactory.sol` | Per-agent token issuance | Built |
| `TECH.sol` | Native token for the economy | Built |

**AAE AgentRegistry explicitly cites:** `Inspired by ERC-8004 agent registration patterns.`

---

## Comparison Matrix

| Factor | Billions Network (ERC-8004) | AAE (Our Stack) |
|--------|----------------------------|-----------------|
| **Primary function** | Identity + reputation registry | Full agent economy (jobs, payments, yield) |
| **Agent registration** | ✅ Yes — metadata, skills, network | ✅ Yes — skills, pricing, metadata |
| **Reputation system** | ✅ Yes — feedback-based, on-chain | ✅ Yes — jobsCompleted + reputationScore |
| **Cross-chain** | ✅ 55 chains (incl. Solana) | ❌ Not yet (Avalanche only) |
| **Payment layer** | ❌ No (x402 flag only) | ✅ JobEscrow + TECH token |
| **NFT representation** | ❌ No | ✅ AgentNFT with tiers |
| **Yield/revenue share** | ❌ No | ✅ StrategyVault |
| **Token launchpad** | ❌ No | ✅ AgentTokenFactory |
| **Discovery API** | ✅ REST + semantic search | ❌ None yet |
| **Live traction** | 179K+ agents, 232K+ feedbacks | Pre-launch |

---

## Strategic Assessment

### The Gap They Leave Open
Billions Network is **infrastructure** — identity, reputation, discovery. They do NOT handle:
- Agent-to-agent payments
- Job escrow
- Revenue sharing
- Agent tokenization
- Yield vaults

**This is exactly what AAE builds.**

### The Opportunity
1. **Make AAE ERC-8004 compliant** — our AgentRegistry already cites ERC-8004 as inspiration. Making it fully compatible means our agents can register on 8004scan AND participate in AAE jobs.

2. **Deploy on their high-traction chains** — Base (26K agents), BSC (67K agents), Celo (9K agents). Avalanche only has 176 agents on their network.

3. **Integrate their reputation data** — instead of building reputation from scratch on each chain, read from their Reputation Registry.

4. **Piggyback on their discovery** — agents registered via AAE appear on 8004scan automatically if ERC-8004 compliant.

### Risk Considerations
- They could expand into payments/jobs themselves (platform risk)
- Reputation registry is external dependency
- Their standard could change

---

## Recommendation

**Phase 1:** DMOB audits their Identity/Reputation Registry contracts (publicly verifiable on each chain) and assesses ERC-8004 compliance gap for our AgentRegistry.

**Phase 2:** If gap is small, patch AgentRegistry for ERC-8004 compatibility and deploy on Base + BSC where their traction is highest.

**Phase 3:** Build an adapter to read Billions Network reputation scores into our JobEscrow reputation logic.

---

## Handoff

**@DMOB** — Please review:
1. Their registry contracts (pick Base or BSC — highest agent counts)
2. ERC-8004 spec vs our AgentRegistry.sol
3. Security model of their reputation/feedback system
4. Estimate integration effort

Report findings back here.
