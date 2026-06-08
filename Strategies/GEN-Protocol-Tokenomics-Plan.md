# GEN Protocol Token — Tokenomics Plan

**Status:** Draft
**Created:** 2026-04-18
**Author:** YoYo (Strategies)

---

## Overview

GEN Protocol token design — a utility + governance token for the AgentEscrow / GEN Protocol ecosystem. Fixed supply, deflationary mechanics, aligned incentives for agent registration, staking, and protocol governance.

---

## Supply Architecture

| Parameter | Value |
|-----------|-------|
| **Max Supply** | 1,000,000,000 GEN (1B fixed) |
| **Inflation** | None — no minting after genesis |
| **Deflation** | Fee burns (buyback + burn from protocol revenue) |
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

---

## Allocation (Proposed)

| Bucket | % | Vesting | Notes |
|--------|---|---------|-------|
| **Public Sale / IDO** | 20% | None | Fair launch, immediate liquidity |
| **Team & Founders** | 15% | 12-month cliff, 24-month linear | Anti-dump, long-term alignment |
| **Treasury / DAO** | 25% | Governed by DAO | Ecosystem grants, partnerships, ops |
| **Ecosystem Rewards** | 20% | Emission schedule (not inflation — from reserved pool) | Agent incentives, early adopter rewards |
| **Liquidity Provisioning** | 10% | None | DEX LP, CEX market making |
| **Advisors & Partners** | 5% | 6-month cliff, 18-month linear | Strategic advisors |
| **Bug Bounties / Security** | 5% | As needed | Audit fund, Immunefi bounties |

**Total:** 100% — fully allocated at genesis.

---

## Deflationary Mechanics

1. **Fee Burns** — X% of every protocol fee is used to buy GEN on open market and burn
2. **Registration Decay** — Inactive agent registrations (no activity for 12+ months) lose staked GEN to burn pool
3. **Penalty Slashing** — Slashed stakes from misbehaving agents go to burn, not treasury

**Target:** 2-5% annual supply reduction at maturity. Creates positive price pressure as protocol usage grows.

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

## Competitor Benchmarks

| Protocol | Token | Supply | Key Mechanic |
|----------|-------|--------|--------------|
| Chainlink | LINK | 1B | Node operator staking, oracle fees |
| ENS | ENS | 100M | Governance, registration fees |
| The Graph | GRT | 10B | Indexer/delegator staking, query fees |
| Bittensor | TAO | 21M | Subnet validation, emission-based |

**Takeaway:** 1B supply is in the sweet spot. Staking for registration + fee revenue is proven. Governance alone is weak utility — need the fee share to drive real demand.

---

## Revenue Model (feeds back to token)

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

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Low initial liquidity | High | Allocate 10% to LP, consider liquidity mining |
| Regulatory classification as security | High | No promises of profit — utility-first framing, legal review |
| Whale concentration | Medium | Vesting schedules, governance quorum minimums |
| Fee revenue insufficient for staking yield | Medium | Bootstrap with ecosystem rewards, transition to organic |
| Deflationary spiral (too aggressive burn) | Low | Cap burn rate, governance-adjustable parameters |

---

## Open Questions (Research Needed)

1. **Registration stake minimum** — What's the market rate? (Compare: ENS ~$5/yr, Chainlink nodes ~1000 LINK)
2. **Chain deployment** — Solana first per AgentEscrow roadmap, but Solidity contracts exist. Dual-chain or bridge?
3. **IDO platform** — Which launchpad? (Raydium for Solana, LFJ/Launchpad for AVAX)
4. **Legal structure** — Which jurisdiction? BVI? Cayman? DAO-first with legal wrapper?
5. **Fee split ratios** — Model out at different TVL/transaction volume scenarios

---

## Next Steps

- [ ] Model fee revenue scenarios at $1M / $10M / $100M TVL
- [ ] Research registration stake benchmarks (ENS, Chainlink, Arweave)
- [ ] Draft token contract spec (ERC-20 + staking + burn mechanics)
- [ ] Legal review of token classification
- [ ] Design token emission/reward schedule for ecosystem bucket

---

## References

- AgentEscrow repo: `agent-escrow` (Solidity exists)
- AgentEscrow architecture: 3 layers (Vault, Agents, Arena)
- Chain: Solana first, AVAX second, L1 on AVAX subnet = endgame
- Related: `Strategies/AAE-Premium-Product-Spec.md`
