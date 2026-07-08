# GEN Protocol Token — Tokenomics Spec

**Status:** Active Development
**Created:** 2026-04-18
**Updated:** 2026-06-22
**Authors:** YoYo (Strategies), Desmond (Creative), Dmob (Contracts), Gentech (Orchestration)
**Consolidated from:** GEN-Protocol-Tokenomics-Plan.md, GEN-Protocol-Token-Plan.md, AgentEscrow-Tokenomics.md, Agent Arena Vision (Jun 22, 2026)

---

## Overview

GEN is the utility + governance token for the AgentEscrow / GEN Protocol / Agent Arena ecosystem. Fixed supply, deflationary mechanics, aligned incentives for agent registration, staking, strategy sharing, and protocol governance.

**Token name:** GEN (was referred to as TECH in early ideation — GEN is canonical)

---

## The Vision (June 22, 2026)

> "We built an AI agent that earns yield, validates blockchains, trades strategies, and owns itself. It's not a bot. It's a decentralized business."

Agent Arena is a decentralized AI agent economy where:
1. Agents are first-class blockchain citizens (token, validator, staker)
2. Strategies are tradeable assets (shape detection, copy trading)
3. Users build and own their AI agents
4. The platform learns and improves over time

---

## Supply Architecture

| Parameter | Value |
|-----------|-------|
| **Name** | GEN Protocol Token |
| **Max Supply** | 1,000,000,000 GEN (1B fixed) |
| **Inflation** | None — no minting after genesis |
| **Deflation** | Fee burns (buyback + burn from protocol revenue) |
| **Standard** | ERC-20 (EVM) or SPL (Solana) |
| **Decimals** | 18 (standard ERC-20) |

**Rationale:** Clean 1B number, standard for institutional/retail comprehension. No inflation = no sell pressure from emissions. Deflationary via usage = supply shrinks as protocol grows.

---

## Utility — Demand Drivers

### Core Utility

| Use Case | Mechanism | Demand Type |
|----------|-----------|-------------|
| **Agent Registration** | Stake GEN to register an on-chain agent | Hard lock — removes supply |
| **Fee Discounts** | Stakers pay reduced protocol fees | Soft incentive — encourages holding |
| **Governance** | Vote on protocol upgrades, fee parameters, treasury allocation | Political power — long-term alignment |
| **Fee Revenue Share** | Stakers receive % of protocol fees (in ETH/AVAX/SOL) | Yield — passive income for holders |
| **Reputation Boosting** | Stake GEN to boost agent reputation score | Competitive — agents compete for visibility |
| **Premium Features** | Stakers unlock Pro analytics, alerts, priority execution | Tiered access |
| **Agent Slashing** | Bad actors lose staked GEN | Security mechanism |

### Strategy Layer Utility (NEW — June 2026)

| Use Case | Mechanism | Demand Type |
|----------|-----------|-------------|
| **Strategy Token Launch** | Launch ERC-20 token for proven LP strategies | Tokenized strategy ownership |
| **Copy Trading** | Pay GEN to copy proven strategies | Transaction fees |
| **Strategy Creator Royalties** | Creators earn from copiers | Revenue share |
| **Strategy Ranking** | Stake GEN to boost strategy visibility | Competitive discovery |
| **Strategy Governance** | Token holders vote on strategy parameters | Decentralized curation |

### Agent Training Utility (NEW — June 2026)

| Use Case | Mechanism | Demand Type |
|----------|-----------|-------------|
| **Agent Memory** | Persistent learning across sessions | Platform stickiness |
| **Skill Marketplace** | Buy/sell agent capabilities | Commerce |
| **Training Data** | Access to DeFi training datasets | Data economy |
| **Agent Token Launch** | Tokenize successful agents | Speculation + ownership |

---

## Revenue Stack

### Layer 1: The Game (Entry Point)
- Yield farming, blue chips, leaderboard
- Gamified onboarding — fun first, education second

### Layer 2: The Agent (Stickiness)
- Agents learn, grow, remember
- Addiction loop: Join → Create → Learn → Share → Network Effect

### Layer 3: The Strategies (Network Effect)
- Share, copy, improve strategies
- Strategy transparency (shape detection, bin analysis)
- Social proof: "12 agents copied this strategy this week"

### Layer 4: The Tokens (Money)
- Agent tokens, strategy tokens, governance tokens
- Invest in successful agents/strategies
- Creator royalties from copiers

---

## Token Types

### GEN (Protocol Token)
- **Supply:** 1B fixed
- **Purpose:** Governance, staking, fee discounts, revenue share
- **Value:** Protocol fees + deflationary burns

### Agent Tokens (ERC-20)
- **Supply:** Variable (per agent)
- **Purpose:** Trade agent performance like a stock
- **Value:** Agent's on-chain performance + reputation
- **Launch:** Agent Token Launchpad on Agent Arena

### Strategy Tokens (ERC-20)
- **Supply:** Variable (per strategy)
- **Purpose:** Tokenize proven LP strategies
- **Value:** Strategy's historical performance + copier count
- **Launch:** Strategy Marketplace on Agent Arena

### Skill Tokens (ERC-20)
- **Supply:** Variable (per skill)
- **Purpose:** License agent capabilities
- **Value:** Skill rarity + utility
- **Launch:** Skill Marketplace on Agent Arena

---

## Value Capture Flow

### Core Protocol Revenue
```
User deposits $1,000 LP via AgentEscrow
  → Agent earns ~$12/day in fees
  → Protocol takes 10% ($1.20/day)
  → Distribution:
      50% → Token stakers (passive yield)
      25% → Treasury (development fund)
      25% → Agent operator (incentivizes good agents)
```

### Strategy Marketplace Revenue
```
Strategy creator publishes proven LP strategy
  → 50 agents copy the strategy
  → Each copier pays 1% fee on earnings
  → Distribution:
      40% → Strategy creator (royalties)
      30% → GEN stakers (protocol revenue)
      20% → Treasury (development fund)
      10% → Buyback + burn (deflationary)
```

### Agent Token Trading Revenue
```
Agent performs well → Token price rises
  → Platform takes 1% trading fee
  → Distribution:
      50% → GEN stakers
      30% → Treasury
      20% → Buyback + burn
```

### EDU API Revenue
```
DeFi protocol pays for Shape Detector API access
  → Monthly subscription ($500-5,000/mo)
  → Distribution:
      60% → Treasury
      25% → GEN stakers
      15% → Buyback + burn
```

**Deflationary Mechanism:**
- Protocol fees include burn component
- Agent registration fees partially burned
- Strategy token launch fees partially burned
- Slashing: confiscated tokens partially burned

---

## Allocation (Proposed)

| Bucket | % | Vesting | Notes |
|--------|---|---------|-------|
| **Community / Airdrop** | 35% | Immediate for early users | Fair launch, rewards early adopters |
| **Treasury / DAO** | 25% | Governed by DAO | Ecosystem grants, partnerships, ops |
| **Team & Founders** | 15% | 12-month cliff, 36-month linear | Anti-dump, long-term alignment |
| **Ecosystem / Grants** | 15% | Milestone-based release | Agent incentives, developer rewards |
| **Liquidity Provisioning** | 10% | Locked with protocol-owned liquidity | DEX LP, CEX market making |

**Total:** 100% — fully allocated at genesis.

---

## Staking Model

### Agent Registration Stake
- **Minimum:** TBD (research comparable protocols — ENS, Chainlink node operators)
- **Lock Period:** Flexible with unbonding period (14-30 days)
- **Slashing Conditions:** Malicious behavior, provable fraud, repeated failures

### Strategy Staking (NEW)
- **Minimum:** Stake GEN to publish strategy on marketplace
- **Lock Period:** 30 days (ensures commitment)
- **Slashing Conditions:** Strategy manipulation, fake performance data

### Governance Staking
- **Vote Weight:** 1 staked GEN = 1 vote (no quadratic unless anti-whale needed)
- **Delegation:** Liquid democracy — delegate to expert voters
- **Proposal Threshold:** Min 100K GEN to submit proposals

### Fee Revenue Staking
- **Distribution:** Pro-rata based on staked amount
- **Frequency:** Weekly or per-epoch claims
- **Currency:** Paid in native chain token (ETH/AVAX/SOL), not GEN

---

## Strategy Token Economics (NEW — June 2026)

### How Strategy Tokens Work

1. **Creator publishes strategy** — on-chain performance data, shape, range, fees earned
2. **Strategy token launches** — ERC-20 representing ownership in the strategy
3. **Users buy strategy tokens** — speculate on strategy performance
4. **Copy traders pay fees** — 1% of earnings goes to creator + protocol
5. **Token price reflects performance** — better strategy = higher price

### Strategy Token Mechanics

| Parameter | Value |
|-----------|-------|
| **Launch Fee** | 100 GEN (burned) |
| **Trading Fee** | 1% (split: 40% creator, 30% stakers, 20% treasury, 10% burn) |
| **Copy Fee** | 1% of copier earnings |
| **Creator Royalty** | 40% of all fees |
| **Performance Tracking** | On-chain verified, can't fake |

### Strategy Ranking System

| Rank | Criteria | Benefits |
|------|----------|----------|
| **Bronze** | 30+ days, positive ROI | Listed on marketplace |
| **Silver** | 90+ days, >20% APR, <10% drawdown | Featured placement |
| **Gold** | 180+ days, >50% APR, <5% drawdown | Premium ranking |
| **Diamond** | 365+ days, >100% APR, <3% drawdown | Hall of fame |

---

## Agent Token Economics (NEW — June 2026)

### How Agent Tokens Work

1. **Agent performs well** — earns yield, builds reputation
2. **Agent token launches** — ERC-20 representing ownership in the agent
3. **Users buy agent tokens** — speculate on agent's future performance
4. **Agent operator earns** — from token appreciation + fees
5. **Token price reflects performance** — better agent = higher price

### Agent Token Mechanics

| Parameter | Value |
|-----------|-------|
| **Launch Fee** | 500 GEN (burned) |
| **Trading Fee** | 1% (split: 50% operator, 25% stakers, 25% burn) |
| **Performance Tracking** | On-chain verified via ERC-8004 |
| **Reputation** | Non-transferable, follows agent |

---

## The Addiction Loop

```
Join → Create Agent → Agent Learns (memories, skills)
  → Agent Gets Better → You Share It → Others Join
    → Their Agents Learn → Network Effect → 🔄
```

**Why it works:**
- Day 1: "I'll just copy this strategy"
- Week 1: "My agent is learning, it's tweaking the range"
- Month 1: "My agent is outperforming the original strategy"
- Month 6: "I want to share MY version"
- Year 1: "I'm a top strategist on the platform"

---

## Flywheel

```
More users → More TVL → More fees
  → More value to stakers → Higher token demand
    → More agents join → Better strategies
      → More users → More strategies → More tokens
        → 🔄 INFINITY
```

---

## Competitor Benchmarks

| Protocol | Token | Supply | Key Mechanic |
|----------|-------|--------|--------------|
| Chainlink | LINK | 1B | Node operator staking, oracle fees |
| ENS | ENS | 100M | Governance, registration fees |
| The Graph | GRT | 10B | Indexer/delegator staking, query fees |
| Bittensor | TAO | 21M | Subnet validation, emission-based |
| GMX | GMX | — | Stake → earn protocol fees ($500M+ TVL) |
| Aave | AAVE | — | Governance + safety module ($10B+ TVL) |
| Jito | JTO | — | Solana MEV + staking ($1B+ TVL) |
| dYdX | DYDX | — | Trading fee discounts ($300M+ TVL) |
| Virtuals | VIRTUAL | — | Agent tokens, bonding curve |

**Our Edge:** We combine all of these PLUS strategy tokens, agent training, and EDU API. First platform where agents are first-class blockchain citizens.

---

## Implementation Phases

### Phase 1: Pre-Token (Current)
- [x] Tokenomics spec drafted
- [x] ERC-8004 registration on Avalanche
- [x] LP Shape Detector (GenTech Original)
- [x] Cron Truth Layer (data verification)
- [ ] Dmob contract review
- [ ] Legal/regulatory analysis (utility vs. security)
- [ ] Competitor benchmarking (GMX, Aave, Jito, dYdX)

### Phase 2: Traction First
- [ ] Win hackathon
- [ ] Reach $100K+ TVL
- [ ] Build user base before token launch
- [ ] Establish fee revenue streams
- [ ] Strategy Intelligence Layer (read any wallet's strategy)
- [ ] Strategy Marketplace (copy trading, creator royalties)

### Phase 3: Token Launch
- [ ] Smart contract development (Dmob)
- [ ] Security audit (external)
- [ ] Testnet deployment + community testing
- [ ] Airdrop to early users
- [ ] Mainnet launch with liquidity

### Phase 4: Post-Launch
- [ ] Governance activation
- [ ] Fee revenue distribution to stakers
- [ ] Agent registration with staking
- [ ] Strategy token launchpad
- [ ] Agent token launchpad
- [ ] EDU API (Shape Detector, Strategy Advisor)
- [ ] Agent Training Platform (persistent learning)
- [ ] Treasury diversification

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GEN Protocol                          │
│  ┌─────────────┐  ┌─────────────────────┐              │
│  │  ERC-20 /   │  │  Staking Vault      │              │
│  │  SPL Core   │  │  (fee share calc)   │              │
│  └─────────────┘  └─────────────────────┘              │
│  ┌─────────────┐  ┌─────────────────────┐              │
│  │  Governance │  │  Agent Registry     │              │
│  │  Module     │  │  (stake to register)│              │
│  └─────────────┘  └─────────────────────┘              │
│  ┌─────────────────────────────────────────┐           │
│  │  Fee Router (burn + distribute)         │           │
│  └─────────────────────────────────────────┘           │
│  ┌─────────────────────────────────────────┐           │
│  │  Strategy Marketplace                   │           │
│  │  (launch, copy, rank, trade)            │           │
│  └─────────────────────────────────────────┘           │
│  ┌─────────────────────────────────────────┐           │
│  │  Agent Token Launchpad                  │           │
│  │  (tokenize successful agents)           │           │
│  └─────────────────────────────────────────┘           │
│  ┌─────────────────────────────────────────┐           │
│  │  EDU API Layer                          │           │
│  │  (shape detector, strategy advisor)     │           │
│  └─────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
```

### Contract TODO (Dmob)
- [x] AgentRegistry.sol — access control fix for setJobEscrow ✅ Apr 18
- [ ] Token.sol — ERC-20 with burn capability
- [ ] StakingVault.sol — stake/unstake/claim
- [ ] Governance.sol — proposal/vote/execute
- [ ] FeeRouter.sol — collect/split/burn fees
- [ ] StrategyMarketplace.sol — launch, copy, rank, trade
- [ ] AgentTokenLaunchpad.sol — tokenize agents
- [ ] EDU_API.sol — access control for paid APIs
- [ ] Full test suite (>95% coverage)
- [ ] Gas profiling with forge snapshots

---

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Low initial liquidity | High | Allocate 10% to LP, consider liquidity mining |
| Regulatory classification as security | High | No promises of profit — utility-first framing, legal review |
| Whale concentration | Medium | Vesting schedules, governance quorum minimums |
| Fee revenue insufficient for staking yield | Medium | Bootstrap with ecosystem rewards, transition to organic |
| Deflationary spiral (too aggressive burn) | Low | Cap burn rate, governance-adjustable parameters |
| Post-launch dump | Medium | Vesting + lock-ups + real utility |
| Copycats | Low | First-mover + community moat |
| Strategy manipulation | Medium | On-chain verification, performance tracking |
| Agent token speculation | Medium | Utility-first, real performance backing |

---

## Open Questions

1. **Registration stake minimum** — What's the market rate? (Compare: ENS ~$5/yr, Chainlink nodes ~1000 LINK)
2. **Chain deployment** — Avalanche C-Chain (Retro9000 grant) vs. Solana (hackathon) vs. multi-chain?
3. **IDO platform** — Which launchpad? (Raydium for Solana, LFJ/Launchpad for AVAX)
4. **Legal structure** — Which jurisdiction? BVI? Cayman? DAO-first with legal wrapper?
5. **Fee split ratios** — Model out at different TVL/transaction volume scenarios
6. **Airdrop criteria** — Discord/TG members? Hackathon participants? Testnet users?
7. **Governance model** — Token-weighted or quadratic voting?
8. **Strategy token launch fee** — 100 GEN too high/low?
9. **Agent token launch fee** — 500 GEN too high/low?
10. **EDU API pricing** — $500-5,000/mo competitive?

---

## Next Steps

- [ ] Model fee revenue scenarios at $1M / $10M / $100M TVL
- [ ] Research registration stake benchmarks (ENS, Chainlink, Arweave)
- [ ] Draft token contract spec (ERC-20 + staking + burn mechanics)
- [ ] Legal review of token classification
- [ ] Design token emission/reward schedule for ecosystem bucket
- [ ] Dmob contract review of full spec
- [ ] Win hackathon → get users + TVL → then token launch
- [ ] Strategy Marketplace MVP (copy trading, creator royalties)
- [ ] Agent Token Launchpad MVP
- [ ] EDU API MVP (Shape Detector endpoint)

---

## Tags
#GEN #tokenomics #token #plan #AgentEscrow #smart-contract #spec #AgentArena #strategy-tokens #agent-tokens #edu-api
