# Sui Overflow 2026 — Agent Infrastructure Port

> **Hackathon:** Sui Overflow 2026
> **Timeline:** May → August 2026 (3 months)
> **Prizes:** $500K+ across tracks
> **Tracks:** The Agentic Web, DeFi & Payments
> **Registration:** https://overflow.sui.io/

## Strategy: Port Existing Work

**Core Insight:** We already have working agent logic in Python/Solidity. Port to Sui's Move language and object-centric model.

### Porting Plan

| Project | Source Chain | Target Track | Effort |
|---------|--------------|--------------|--------|
| Agent Catcher | Somnia (EVM) | The Agentic Web | Medium — Move contracts |
| DeFi Signal Agent | Solana (SVM) | DeFi & Payments | Low — Python stays, add Sui RPC |
| AAE Milestones | EVM | DeFi & Payments | Low — adapt to Sui objects |

### Sui Stack

- **Language:** Move (object-centric, not account-based like Solidity)
- **CLI:** `sui` binary for build/test/deploy
- **RPC:** `fullnode.testnet.sui.io:443`
- **Explorer:** `suiscan.xyz`
- **Security:** MoveBit Analyzer, Skry (LLM static analysis), Move Prover
- **Faucet:** `faucet.testnet.sui.io`

## Timeline

**Week 1 (May 20-26):** Move crash course + Agent Catcher port
**Week 2 (May 27-Jun 2):** DeFi Signal Agent Sui integration
**Week 3-4 (Jun 3-16):** AAE Milestones + integration testing
**Week 5-8 (Jun 17-Aug):** Polish, demo video, submission

## Key Differences: EVM/SVM → Sui Move

1. **Objects, not accounts** — everything is an object with ID
2. **Resources** — on-chain storage with linear type (can't copy/drop)
3. **No `selfdestruct`** — objects live forever unless explicitly deleted
4. **Ability system** `copy`, `drop`, `store`, `key` — controls object behavior
5. **Entry functions** — explicit public entry points
6. **Events** — built-in event emission system

## Next Steps

- [ ] Install Sui CLI + configure testnet
- [ ] Complete Move intro course (2-3 hours)
- [ ] Port Agent Catcher contract to Move
- [ ] Set up Python ↔ Sui RPC integration
- [ ] Register on overflow.sui.io

## Resources

- Sui Move Intro Course: https://github.com/sui-foundation/sui-move-intro-course
- The Move Book: https://move-book.com/
- Sui Docs: https://docs.sui.io/
- MoveBit Analyzer: https://movebit.xyz/analyzer
- Skry (LLM security): https://nowarp.io/blog/skry/

---

**Decision:** Port existing work to Sui Overflow 2026.
**Rationale:** $500K+ prizes, tracks match our stack, 3-month timeline, leverage existing agent logic.
