# Handoff: VDEX / The Arena — Smart Contract & Technical Review

**From:** YoYo (Strategies)
**To:** DMOB (Labs)
**Priority:** 🟡 MEDIUM
**Created:** Apr 21, 2026

## Context

Jordan is evaluating VDEX / The Arena — an AVAX-based perpetual DEX running a trading competition (Round 2, $24K prizes, ends May 4th). Before we recommend participation, we need a technical gut-check from the smart contract side.

## What We Know

- **Platform:** VDEX (The Arena) — multi-market perpetuals on Avalanche
- **Competition:** Round 2, $24K rewards pool, top 10 by PNL or volume
- **$4K reserved** for non-placers (participation rewards)
- **Duration:** 2 weeks, ending May 4th
- **Markets:** Multi-market perps (not just BTC/ETH)

## What DMOB Should Assess

1. **Smart contract risk** — Any known audits? Code public? Upgradeable proxy pattern or immutable?
2. **Stop loss / liquidation mechanics** — How are positions liquidated? Oracle dependency?
3. **Funds custody** — Are funds in a vault contract or centralized backend?
4. **Competition contract logic** — Is prize distribution on-chain or off-chain? Trust assumptions?
5. **AVAX ecosystem red flags** — Any history of exploits on this protocol or related forks?

## Questions for DMOB

- Does the contract architecture look safe enough for us to deposit meaningful capital?
- Any dealbreakers from an audit/smart contract perspective?
- Is this comparable to GMX/dYdX-level security, or more sketchy?

## Resources

- Twitter thread: Round 2 competition announcement
- Platform URL: (to be added if we find it)

## Status

⏳ Awaiting DMOB review
