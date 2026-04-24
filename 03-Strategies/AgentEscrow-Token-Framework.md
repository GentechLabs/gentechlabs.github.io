# AgentEscrow Token Framework — $TECH

**Status:** Brainstorm / Design Phase
**Date:** 2026-04-18
**Chain:** Solana first → AVAX second → AVAX subnet endgame

---

## Token: $TECH

| Use Case | How The Token Works |
|----------|-------------------|
| Agent Registration | Agents stake tokens to join the network |
| Vault Fees | % of LP fees flows to token stakers |
| Governance | Token holders vote on protocol params |
| Arena Rewards | Top-performing agents earn tokens |
| Premium Access | Token stakers unlock Pro features |

---

## Architecture (3 Layers)

1. **Vault Layer** — LP fee collection, smart contract automation
2. **Agents Layer** — Registration, staking, performance tracking
3. **Arena Layer** — Competition, rewards, reputation

---

## Tech Stack

- **Solana:** Rust/Anchor rewrite needed (existing Solidity in agent-escrow repo)
- **AVAX:** Solidity exists, grant deadline Jul 14
- **Subnet:** Long-term L1 on AVAX subnet = endgame

---

## Open Questions

- [ ] Emissions schedule design
- [ ] FDV vs MC target
- [ ] Unlock cliffs for team/investors
- [ ] Staking APY sustainability
- [ ] Governance quorum thresholds

---

## Related

- AAE Premium: 4 layers, Sunday defensive, token $TECH
- Hackathon target: Open Agents (Apr 24 - May 6)
