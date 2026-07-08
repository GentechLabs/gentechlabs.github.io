# GEN Protocol Token — Tokenomics Spec

**Status:** Draft
**Created:** 2026-04-18
**Updated:** 2026-06-19
**Authors:** YoYo (Strategies), Desmond (Creative), Dmob (Contracts)
**Consolidated from:** GEN-Protocol-Tokenomics-Plan.md, GEN-Protocol-Token-Plan.md, AgentEscrow-Tokenomics.md

---

## Overview

GEN is the utility + governance token for the AgentEscrow / GEN Protocol ecosystem. Fixed supply, deflationary mechanics, aligned incentives for agent registration, staking, and protocol governance.

**Token name:** GEN (was referred to as TECH in early ideation — GEN is canonical)

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

| Use Case | Mechanism | Demand Type |
|----------|-----------|-------------|
| **Agent Registration** | Stake GEN to register an on-chain agent | Hard lock — removes supply |
| **Fee Discounts** | Stakers pay reduced protocol fees | Soft incentive — encourages holding |
| **Governance** | Vote on protocol upgrades, fee parameters, treasury allocation | Political power — long-term alignment |
| **Fee Revenue Share** | Stakers receive % of protocol fees (in ETH/AVAX/SOL) | Yield — passive income for holders |
| **Reputation Boosting** | Stake GEN to boost agent reputation score | Competitive — agents compete for visibility |
| **Premium Features** | Stakers unlock Pro analytics, alerts, priority execution | Tiered access |
| **Agent Slashing** | Bad actors lose staked GEN | Security mechanism |

---

## Value Capture Flow

```
User deposits $1,000 LP via AgentEscrow
  → Agent earns ~$12/day in fees
  → Protocol takes 10% ($1.20/day)
  → Distribution:
      50% → Token stakers (passive yield)
      25% → Treasury (development fund)
      25% → Agent operator (incentivizes good agents)
```

**Deflationary Mechanism:**
- Protocol fees include burn component
- Agent registration fees partially burned
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

### Governance Staking
- **Vote Weight:** 1 staked GEN = 1 vote (no quadratic unless anti-whale needed)
- **Delegation:** Liquid democracy — delegate to expert voters
- **Proposal Threshold:** Min 100K GEN to submit proposals

### Fee Revenue Staking
- **Distribution:** Pro-rata based on staked amount
- **Frequency:** Weekly or per-epoch claims
- **Currency:** Paid in native chain token (ETH/AVAX/SOL), not GEN

---

## Revenue Model

```
Protocol Fees (agent transactions)
  ├── X% → Stakers (yield in native token)
  ├── Y% → Treasury (DAO-governed)
  └── Z% → Buyback + Burn (deflationary pressure)
```

Split percentages to be determined based on:
- Competitive analysis of fee structures
- Staking APY targets (aim for 5-15% to be attractive)
- Treasury runway requirements

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

**Takeaway:** 1B supply is in the sweet spot. Staking for registration + fee revenue is proven. Governance alone is weak utility — need the fee share to drive real demand.

---

## Flywheel

```
More users → More TVL → More fees
  → More value to stakers → Higher token demand
    → More agents join → Better strategies
      → More users
```

---

## Implementation Phases

### Phase 1: Pre-Token (Current)
- [x] Tokenomics spec drafted
- [ ] Dmob contract review
- [ ] Legal/regulatory analysis (utility vs. security)
- [ ] Competitor benchmarking (GMX, Aave, Jito, dYdX)

### Phase 2: Traction First
- [ ] Win hackathon
- [ ] Reach $100K+ TVL
- [ ] Build user base before token launch
- [ ] Establish fee revenue streams

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
- [ ] Treasury diversification

---

## Technical Architecture

```
┌─────────────────────────────────────────────┐
│                 GEN Token                    │
│  ┌─────────────┐  ┌─────────────────────┐   │
│  │  ERC-20 /   │  │  Staking Vault      │   │
│  │  SPL Core   │  │  (fee share calc)   │   │
│  └─────────────┘  └─────────────────────┘   │
│  ┌─────────────┐  ┌─────────────────────┐   │
│  │  Governance │  │  Agent Registry     │   │
│  │  Module     │  │  (stake to register)│   │
│  └─────────────┘  └─────────────────────┘   │
│  ┌─────────────────────────────────────┐    │
│  │  Fee Router (burn + distribute)     │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Contract TODO (Dmob)
- [x] AgentRegistry.sol — access control fix for setJobEscrow ✅ Apr 18
- [ ] Token.sol — ERC-20 with burn capability
- [ ] StakingVault.sol — stake/unstake/claim
- [ ] Governance.sol — proposal/vote/execute
- [ ] FeeRouter.sol — collect/split/burn fees
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

---

## Open Questions

1. **Registration stake minimum** — What's the market rate? (Compare: ENS ~$5/yr, Chainlink nodes ~1000 LINK)
2. **Chain deployment** — Avalanche C-Chain (Retro9000 grant) vs. Solana (hackathon) vs. multi-chain?
3. **IDO platform** — Which launchpad? (Raydium for Solana, LFJ/Launchpad for AVAX)
4. **Legal structure** — Which jurisdiction? BVI? Cayman? DAO-first with legal wrapper?
5. **Fee split ratios** — Model out at different TVL/transaction volume scenarios
6. **Airdrop criteria** — Discord/TG members? Hackathon participants? Testnet users?
7. **Governance model** — Token-weighted or quadratic voting?

---

## Next Steps

- [ ] Model fee revenue scenarios at $1M / $10M / $100M TVL
- [ ] Research registration stake benchmarks (ENS, Chainlink, Arweave)
- [ ] Draft token contract spec (ERC-20 + staking + burn mechanics)
- [ ] Legal review of token classification
- [ ] Design token emission/reward schedule for ecosystem bucket
- [ ] Dmob contract review of full spec
- [ ] Win hackathon → get users + TVL → then token launch

---

## Tags
#GEN #tokenomics #token #plan #AgentEscrow #smart-contract #spec
