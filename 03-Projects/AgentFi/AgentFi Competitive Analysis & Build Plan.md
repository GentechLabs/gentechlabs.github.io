# AgentFi — Competitive Analysis & Build Plan

**Date:** 2026-04-20
**Status:** Strategic Planning — READY
**Trigger:** Bankr $500M volume claim + Jordan's "let's start AgentFi for real"

---

## ⚠️ Bankr Claim Status: UNVERIFIED

The original claim ("Bankr Uniswap hook, $500M volume") could not be independently verified across 10+ sources (news, GitHub, DeFi Llama, CoinGecko, Farcaster, on-chain). This analysis uses the Bankr model as described in the thread, but treats unverified claims as **narrative**, not fact.

---

## 1. Competitive Landscape: What Exists

### Bankr (as described)
| What they do | What they don't do |
|---|---|
| Token launchpad on Base → Uniswap V4 pool | Multi-DEX routing |
| Free deployment with 1.2% swap fee | Portfolio management |
| Fee split: 57% creator / 36.1% Bankr / 5% protocol / 1.9% ecosystem | Risk management (SL, TP, MEV protection) |
| Agent wallet: cross-chain gas sponsorship | Cross-chain execution |
| LLM gateway for agent reasoning | Social/sentiment awareness |
| Token launch + basic agent trading | Multi-strategy (LP, yield farming, arb) |
| Uniswap hook for embedded intelligence | User-facing dashboard/interface |
| Doppler pricing mechanism | Reputation/scoring system |

### Other Players (confirmed)
| Project | What they do | Gap |
|---|---|---|
| **Eliza OS** | Agent framework, multi-chain | No DeFi execution layer |
| **Virtuals Protocol** | Agent launch + tokenization | No trading execution |
| **Goat Protocol** | Agent tooling for DeFi | No unified platform |
| **AI16Z / DAOS.fun** | Agent-run funds | No retail-facing tooling |
| **Truth Terminal** | Meme agent, wallet autonomy | One-off, not a platform |
| **Kite AI** | Agent payments blockchain | No DeFi trading (yet) |

### The Gap: No one is doing the FULL stack
```
Bankr = Launch + basic execution
Eliza = Framework (no DeFi)
Virtuals = Tokenization (no execution)
Goat = Tooling (no platform)
Kite = Payments (no DeFi)

AgentFi = ALL OF IT
```

---

## 2. What We Already Have (Inventory)

### ✅ Existing Assets

| Asset | Location | Status | Relevance |
|---|---|---|---|
| **Agent Economy Contracts** | `agent-economy-kite` repo | Foundation ✅ | AgentPaymentFlow, daily limits, payment execution |
| **Kite Testnet Integration** | Deployed contracts on Kite AI testnet | Ready | Chain ID 2368, AA SDK, gasless via EIP-3009 |
| **Agent NFT Burn Floor** | Vault: `03-Projects/Kite/` | Engineering-approved | Dynamic floor, auto-burn, reserve pool, soulbound |
| **Agent Lifecycle Marketplace** | Vault: `02-Labs/Agent-Lifecycle-Marketplace.md` | Draft | Bot states (created→active→listed→sold), performance scoring |
| **Sim-to-Real Trading Engine** | Vault: `02-Labs/AAE-Sim-to-Real-Trading.md` | Concept | Free simulation → earn $TECH → real capital deployment |
| **AgentEscrow Contracts** | `agent-escrow` repo (Solidity) | Exists | Solana first, AVAX second, L1 endgame |
| **AAE Architecture** | Vault: `02-Labs/AAE-*` | Designed | 8-layer architecture (Brain→Lifecycle) |
| **LFJ LP Monitor** | Active cron jobs | Running | Range monitoring, pause/resume, LP management |
| **LP Range Monitor Skill** | Skills library | Active | Automated range breach detection |
| **DeFi Fork Evaluation** | Skills library | Active | Framework for evaluating DeFi forks |

### 🟡 Partial Assets

| Asset | Gap |
|---|---|
| **Tokenomics** | $TECH token design exists but incomplete |
| **Frontend** | React scaffold planned but not built |
| **Agent Passport** | Kite Agent Passport explored, not integrated |
| **Multi-chain** | Kite + Solana planned, not deployed |
| **Revenue model** | Conceptual (swap fees, subscriptions), not quantified |

### ❌ Missing

| Need | Why it matters |
|---|---|
| **Live agent trading engine** | The core product — agents that actually trade on-chain |
| **Uniswap V4 hook** | Bankr's claimed moat — embedded intelligence at liquidity layer |
| **Token ($TECH)** | Required for burn floor, staking, governance |
| **Dashboard/UI** | User-facing interface for managing agents |
| **On-chain reputation** | Agent scoring, performance tracking |
| **Hackathon submission** | Need a concrete deadline to ship |

---

## 3. Strategic Positioning: Where We Win

### The Thesis
Bankr is a **launchpad with agent execution**. We build the **full agent lifecycle platform**:

```
Bankr: Launch → Trade → Done
Kite:  Launch → Manage → Earn → Sell → Burn → Repeat
```

### Our Moats (if we build them)
1. **Sim-to-Real funnel** — Nobody else offers free simulation → real capital
2. **Burn floor insurance** — Guaranteed exit for agent NFTs (Bankr doesn't have this)
3. **Lifecycle marketplace** — Buy, sell, upgrade, downgrade agents (Bankr = one-and-done)
4. **Multi-DEX execution** — Not locked to one hook/pool
5. **Reputation scoring** — Agent performance history = trust signal
6. **Revenue sharing** — Stakers earn from platform fees (Bankr splits with creators only)

---

## 4. Build Plan: Phased Approach

### Phase 1: MVP (Weeks 1-4) — "Agent Trading Engine"
**Goal:** Deploy a working agent that can execute trades on-chain

| Task | Owner | Priority |
|---|---|---|
| Deploy AgentPaymentFlow to Kite testnet | Dmob | P0 |
| Build agent trading agent (Eliza/Goat + on-chain execution) | Dmob | P0 |
| Scaffold React dashboard (view agents, positions, P&L) | Dmob | P1 |
| Integrate Kite AA SDK (gasless transactions) | Dmob | P1 |
| Write docs + demo video | Jordan | P2 |
| Submit to Kite AI hackathon (Apr 26 deadline) | Team | P2 |

### Phase 2: Token + Burn Floor (Weeks 4-8) — "Agent Economy"
**Goal:** Deploy $TECH token + Agent NFT burn floor

| Task | Owner | Priority |
|---|---|---|
| Deploy $TECH token (ERC-20) | Jordan (Solidity) | P0 |
| Deploy ReservePool contract | Jordan (Solidity) | P0 |
| Deploy AgentNFT with burn floor | Jordan (Solidity) | P0 |
| Audit (Cyfrin Updraft exercise + CodeHawks) | Jordan | P0 |
| Integrate burn floor with AgentPaymentFlow | Dmob | P1 |
| Deploy to testnet | Team | P1 |

### Phase 3: Marketplace + Sim-to-Real (Weeks 8-12) — "Full Platform"
**Goal:** Launch agent marketplace + simulation engine

| Task | Owner | Priority |
|---|---|---|
| Build agent marketplace (list, buy, sell) | Dmob | P0 |
| Deploy sim-to-real trading engine | Dmob | P0 |
| Agent reputation/scoring system | Team | P1 |
| Multi-DEX routing (Uniswap + LFJ) | Dmob | P1 |
| Launch public beta | Team | P0 |

---

## 5. Revenue Model

| Stream | Mechanism | Estimate |
|---|---|---|
| **Swap fees** | 0.1-0.3% on agent trades | Scales with volume |
| **Launch fees** | $5-10 per agent deployment | High margin |
| **Premium subscriptions** | Advanced features, faster execution | Recurring |
| **Marketplace fees** | 2-5% on agent NFT sales | Network effects |
| **Staking yield** | Protocol fees distributed to $TECH stakers | Token demand |
| **LP autopilot** | Subscription for automated LP management | Recurring |

---

## 6. Immediate Next Steps

1. **Decide hackathon target** — Kite AI (Apr 26) or wait for next one
2. **Assign Phase 1 tasks** — Dmob gets contracts deployed, YoYo researches Uniswap V4 hook architecture
3. **Define MVP scope** — What's the minimum that proves the thesis?
4. **Set timeline** — When do we want Phase 1 complete?
5. **Budget** — Gas costs, testnet tokens, potential audit costs

---

## 7. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Bankr is real and ships fast | High | Focus on lifecycle + burn floor (their gap) |
| Kite AI chain doesn't gain adoption | Medium | Multi-chain from start (Base, AVAX, Solana) |
| Smart contract vulnerability | Critical | Cyfrin Updraft audits + CodeHackets |
| Regulatory uncertainty on agent trading | Medium | Start on testnet, no KYC needed yet |
| Token economics not sustainable | High | Conservative reserve pool + circuit breaker |

---

*This doc is a living strategy. Update as new information arrives.*
