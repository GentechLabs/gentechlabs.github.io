# AgentEscrow — Tokenomics Spec (Draft)
**Created:** 2026-04-18
**Status:** Ideation — needs Dmob review
**Triggered by:** "Lol aye let's go TECH 😭 damn not my own token"

---

## Token Utility

| Use Case | Mechanism |
|----------|-----------|
| **Agent Registration** | Agents stake tokens to join network |
| **Vault Fee Sharing** | % of LP fees → token stakers |
| **Governance** | Vote on protocol parameters |
| **Arena Rewards** | Top agents earn tokens |
| **Premium Access** | Stakers unlock Pro features |
| **Agent Slashing** | Bad agents lose staked tokens |

## Value Capture Model

```
User deposits $1,000 LP via AgentEscrow
  → Agent earns ~$12/day in fees
  → Protocol takes 10% ($1.20/day)
  → Distribution:
      50% → Token stakers
      25% → Treasury
      25% → Agent operator
```

## Flywheel

```
More users → More TVL → More fees
  → More value to stakers → Higher token demand
    → More agents join → Better strategies
      → More users
```

## Comparable Models

| Protocol | Token | Model | TVL |
|----------|-------|-------|-----|
| GMX | GMX | Stake → earn protocol fees | $500M+ |
| Aave | AAVE | Governance + safety module | $10B+ |
| Jito | JTO | Solana MEV + staking | $1B+ |
| dYdX | DYDX | Trading fee discounts | $300M+ |

## Open Questions

1. **Token name:** TECH (GenTech) ✅
2. **Supply:** Fixed cap or inflationary emissions?
3. **Distribution:** Team %, community %, treasury %, airdrop %?
4. **Launch timing:** Post-MVP? After hackathon wins? After TVL?
5. **Chain:** Solana (SPL token) with product launch?
6. **Vesting:** Team lock-up period? Investor vesting?

## Risks

| Risk | Mitigation |
|------|-----------|
| Regulatory (SEC) | Utility-first, not security. No profit promises. |
| Low TVL = dead token | Don't launch until product has traction |
| Dump after launch | Vesting + lock-ups + real utility |
| Copycats | First-mover + community moat |

## Recommendation

**Don't launch token before TVL.** Token captures existing value, doesn't create imaginary value.

Sequence:
1. Win hackathon (Kite AI Apr 26, Solana Frontier May 11)
2. Get users + TVL
3. Token launch captures real value
4. Airdrop to early users → community

---

## Tags
#AgentEscrow #tokenomics #token #spec
