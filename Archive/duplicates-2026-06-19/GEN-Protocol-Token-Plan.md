# GEN Protocol Token — Implementation Plan

**Created:** 2026-04-18
**Status:** Planning
**Parent:** AgentEscrow-Tokenomics.md
**Triggered by:** Jordan confirming tokenomics framework

---

## Token Specification

| Parameter | Value |
|-----------|-------|
| **Name** | GEN Protocol Token |
| **Supply** | 1,000,000,000 (1B fixed) |
| **Inflation** | None — deflationary via fee burns |
| **Standard** | ERC-20 (EVM) or SPL (Solana) |

---

## Utility Matrix

| Use Case | Mechanism | Demand Driver |
|----------|-----------|---------------|
| **Agent Registration** | Stake GEN to register on-chain agent | Sinks supply, gates participation |
| **Fee Discounts** | Stakers pay lower protocol fees | Incentivizes holding/staking |
| **Governance** | Vote on protocol upgrades, fee parameters, treasury allocation | Aligns community incentives |
| **Fee Revenue Share** | % of protocol fees → stakers (GMX model) | Passive yield, value accrual |
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

## Distribution Plan

| Allocation | % | Vesting |
|------------|---|---------|
| Community / Airdrop | 35% | Immediate for early users |
| Treasury | 25% | Governance-controlled |
| Team | 15% | 12-month cliff, 36-month linear vest |
| Ecosystem / Grants | 15% | Milestone-based release |
| Liquidity / Market Making | 10% | Locked with protocol-owned liquidity |

---

## Implementation Phases

### Phase 1: Pre-Token (Current)
- [x] Tokenomics spec drafted
- [ ] Dmob contract review
- [ ] Legal/regulatory analysis (utility vs. security)
- [ ] Competitor benchmarking (GMX, Aave, Jito, dYdX)

### Phase 2: Traction First
- [ ] Win hackathon (Kite AI Apr 26, Solana Frontier May 11)
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

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| SEC regulatory | Utility-first design, no profit promises, legal review |
| Low TVL = dead token | Don't launch until product has traction |
| Post-launch dump | Vesting + lock-ups + real utility |
| Copycats | First-mover + community moat |
| Gas costs (EVM) | L2 deployment (Avalanche C-Chain, Base) |

---

## Open Questions

1. **Chain:** Avalanche C-Chain (Retro9000 grant) vs. Solana (hackathon) vs. multi-chain?
2. **Launch timing:** After hackathon wins or after TVL milestone?
3. **Airdrop criteria:** Discord/TG members? Hackathon participants? Testnet users?
4. **Fee structure:** Flat % or tiered by stake amount?
5. **Governance model:** Token-weighted or quadratic voting?

---

## Comparable Protocols

| Protocol | Token | Model | Key Insight |
|----------|-------|-------|-------------|
| GMX | GMX | Stake → earn protocol fees | Proven fee-share model |
| Aave | AAVE | Governance + safety module | Risk management value |
| Jito | JTO | Solana MEV + staking | Agent-like model (validators) |
| dYdX | DYDX | Trading fee discounts | Tiered utility |
| UNI | UNI | Governance only | Value capture question |

---

## Dmob's Contract TODO

- [x] ~~AgentRegistry.sol — access control fix for setJobEscrow~~ ✅ Apr 18
- [ ] Token.sol — ERC-20 with burn capability
- [ ] StakingVault.sol — stake/unstake/claim
- [ ] Governance.sol — proposal/vote/execute
- [ ] FeeRouter.sol — collect/split/burn fees
- [ ] Full test suite (>95% coverage)
- [ ] Gas profiling with forge snapshots

---

## Tags
#GEN #tokenomics #token #plan #AgentEscrow #smart-contract
