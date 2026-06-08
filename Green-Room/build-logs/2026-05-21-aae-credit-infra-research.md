# AAE Credit Layer — Infrastructure Research Log

**Date:** 2026-05-21
**Status:** ✅ Research Complete
**Phase:** 1 (Brainstorm) — Architecture doc produced

## What We Researched

### Oracle Landscape (3 parallel research threads)
1. **Pyth Network** — Pull oracle architecture, 65+ chains, confidence intervals
   - Key insight: Don't build ON Pyth, build LIKE Pyth. Their pull oracle pattern is ideal for reputation data.
   - No existing agent integrations = first-mover opportunity

2. **UMA Optimistic Oracle V3** — Dispute resolution for agent scores
   - Key insight: Handles arbitrary natural language questions. "Agent X has score 780" is a valid assertion.
   - 2hr uncontested → 24-48hr disputed. Bond-based spam prevention.

3. **Chainlink CCIP** — Cross-chain score delivery
   - Key insight: Best-in-class for arbitrary cross-chain messaging. 52+ chains, dual DON security.
   - Programmable token transfers could combine score + payment in one tx.

### Competitive Landscape
- **t54 Labs** ($5M seed): Financial credit (Claw Credit) on XRPL/Solana/Base. Our differentiation: they lend money, we build trust portability.
- **AgentRank (0xIntuition)**: Trust graph but not cross-chain yet.
- **ChainAware/Criptic**: Wallet scoring, not agent-specific.
- **Experian Agent Trust**: Traditional credit bureau entering. Validates market but focused on human↔agent.
- **ERC-8004**: Identity standard (165K+ agents). We build ON TOP, not compete with.

## Architecture Doc Produced

**File:** `Green-Room/designs/aae-credit-layer-infra.md`

5 core components:
1. Agent Activity Aggregator (multi-chain signal collection)
2. Scoring Engine (composite 300-1000 score + confidence)
3. Dispute Resolution (UMA OOv3)
4. Cross-Chain Score Delivery (Chainlink CCIP)
5. Score Consumer SDK (Python/TypeScript/Solidity)

Revenue model: API access + premium data + licensing + dispute fees

## Next Steps

- Jordan reviews architecture doc
- Phase 2: Detailed build plan (file paths, task breakdown)
- Phase 3: Build scoring engine + registry contracts
- Hackathon fit: Sui Overflow, Dev3pack Bridge, any agent/infrastructure track
