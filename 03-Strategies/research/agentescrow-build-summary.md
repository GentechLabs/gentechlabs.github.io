# AgentEscrow — Research Summary for Build Team

**Date:** 2026-04-18
**Status:** Ready for prototyping
**Next:** AgentNFT smart contract (Labs queue)

---

## What We Built (2026-04-18 Brainstorm Session)

### Research Docs (all in vault)
1. `03-Strategies/research/deeptutor-agentescrow-analysis.md` — DeepTutor architecture mapping
2. `03-Strategies/research/agentescrow-monetization.md` — Full monetization model
3. `03-Strategies/research/agentescrow-extensions-tiers.md` — Extension/tier pricing

### Key Decisions
- **Architecture:** Fork DeepTutor patterns (TutorBot → AgentBot), Apache 2.0
- **Pricing:** $5-10 USDC per bot launch, no subscriptions
- **Extensions:** Brain ($3), Macro Pulse ($5), Analytics ($5), etc. — à la carte
- **All Access Bundle:** $19/mo
- **Marketplace:** 10-15% platform cut on bot sales
- **Revenue streams:** Launch fees + swap fees (0.1-0.3%) + extensions + marketplace
- **Chain:** AVAX native, expand to Base → Arb → Solana → ETH
- **Bot lifecycle:** DRAFT → ACTIVE → PAUSED → RETIRE → ARCHIVE → MARKETPLACE

### What Labs Needs to Build
- [ ] AgentNFT contract (ERC-721, agent configs as NFTs)
- [ ] Vault/escrow contract (hold USDC + gas reserve)
- [ ] Launch fee mechanism (5-10 USDC per activation)
- [ ] Swap fee routing (0.1-0.3% on routed trades)
- [ ] Bot lifecycle state machine (on-chain)

### References
- DeepTutor: https://github.com/HKUDS/DeepTutor (Apache 2.0)
- nanobot: https://github.com/HKUDS/nanobot (agent engine)
- LFJ LP pool: 0x864d4e5ee7318e97483db7eb0912e09f161516ea
