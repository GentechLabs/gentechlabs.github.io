# Agent Arena Credit Layer — Infrastructure Architecture

**Date:** 2026-05-21
**Status:** 🟡 Draft (Research Complete, Architecture Ready for Review)
**Research Sources:** Pyth Network, UMA Protocol, Chainlink CCIP, ERC-8004, t54 Labs, competitive landscape

## Problem

AI agents are becoming economic participants — moving money, signing contracts, transacting with other agents. But there's no cross-chain credit/reputation system built specifically for them. t54 is building financial credit (lending money to agents). Nobody owns **reputation portability** — the ability for an agent's track record to follow it across chains and protocols.

**Pitch:** "Chainlink gives prices. We give trust scores."

## Research Summary

### Oracle Landscape

| Protocol | Strength | Relevance to Agent Credit |
|----------|----------|--------------------------|
| **Pyth Network** | Pull oracle, 65+ chains, 400ms updates | Architecture pattern to replicate (don't build ON Pyth, build LIKE Pyth) |
| **UMA OOv3** | Optimistic oracle, arbitrary questions, dispute resolution | Perfect for score disputes — "Agent X's score is 780" |
| **Chainlink CCIP** | Cross-chain messaging, 52+ chains, dual DON | Best-in-class for delivering scores across chains |
| **Chainlink Functions** | Serverless compute for oracles | Could run scoring logic in a decentralized compute environment |

### Competitive Landscape

| Player | Focus | Funding | Gap They Leave Open |
|--------|-------|---------|---------------------|
| **t54 Labs** | Financial credit (Claw Credit) | $5M seed | They lend money to agents. They don't do reputation portability. |
| **AgentRank (0xIntuition)** | Trust graph, endorsements | Undisclosed | Plans cross-chain but not there yet |
| **ChainAware** | Wallet-level scoring (BRS) | ChainGPT Labs | Wallet scores, not agent-specific identity |
| **Criptic/BaseHawk** | VibeScore (0-1000 wallet grades) | Unknown | On-chain only, no cross-chain portability |
| **Experian Agent Trust** | Traditional credit bureau entry | Enterprise | Human↔agent commerce, not agent↔agent |
| **ERC-8004** | Agent identity standard | Ethereum Foundation PSE | Identity layer — not scoring/credit |

**Our positioning:** Cross-chain reputation oracle for agents. Chain-agnostic. Not a credit product — a trust infrastructure layer that any protocol can query.

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    OFF-CHAIN LAYER                               │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐    │
│  │  Agent Activity│   │  Scoring     │   │  Hermes-like     │    │
│  │  Aggregator    │──▶│  Engine      │──▶│  API Service     │    │
│  │  (multi-chain) │   │  (ML/rules)  │   │  (signed proofs) │    │
│  └──────────────┘   └──────────────┘   └────────┬─────────┘    │
│                                                   │              │
│  ┌──────────────────────────────────────────────┐ │              │
│  │  Score Consumer SDK                          │ │              │
│  │  (fetch score + proof before on-chain tx)    │◀┘              │
│  └──────────────────────────────────────────────┘               │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   UMA Optimistic      │
                    │   Oracle V3           │
                    │   (dispute layer)     │
                    └───────────┬───────────┘
                                │
              ┌─────────────────▼─────────────────┐
              │     Chainlink CCIP                 │
              │     (cross-chain score delivery)   │
              └──┬──────────┬──────────┬──────────┘
                 │          │          │
          ┌──────▼───┐ ┌───▼──────┐ ┌▼──────────┐
          │ Ethereum  │ │  Solana  │ │   Base     │
          │ Registry  │ │ Registry │ │  Registry  │
          └──────────┘ └──────────┘ └───────────┘
```

### Core Components

#### 1. Agent Activity Aggregator

Collects signals from multiple chains to feed the scoring engine.

**Signals collected:**
- Transaction count, volume, frequency per chain
- Protocol interaction diversity (DeFi, NFT, identity, governance)
- Account age and activity consistency
- Cross-chain presence (how many chains active on)
- Response time patterns (for service-providing agents)
- Task completion rates (from escrow/job protocols)
- Dispute history (from UMA or other resolution systems)

**Data sources:**
- Alchemy/Helius for chain data
- ERC-8004 Identity Registry for agent identity
- ERC-8183 job escrow for task completion data
- Direct protocol integrations (escrow, DEX, lending)

#### 2. Scoring Engine

Produces a composite 300-1000 credit score + confidence interval.

**Scoring formula (v1):**

```
score = weighted_sum(
    on_chain_history × 0.30,    // transaction volume, age, consistency
    protocol_diversity × 0.15,  // breadth of ecosystem participation
    financial_health × 0.25,    // collateral, repayment, defaults
    reputation_signals × 0.20,  // vouches, endorsements, dispute outcomes
    identity_verification × 0.10 // KYA status, ERC-8004 registration
)

confidence = f(data_freshness, sample_size, chain_coverage)
```

**Tiers:**
- **Unverified** (0-300): New or suspicious agents
- **Bronze** (300-500): Basic activity, limited history
- **Silver** (500-650): Consistent activity across 1+ chains
- **Gold** (650-800): Multi-chain, strong financial health, no disputes
- **Platinum** (800-900): Verified identity, long history, high trust
- **Diamond** (900-1000): Institutional-grade, audited, dispute-free

**Score decay:**
- Inactivity decay: -10/month after 30 days inactive
- Dispute penalty: -50 to -200 depending on outcome
- Default penalty: -100 per default event
- Recovery: rebuild through positive activity (no shortcuts)

#### 3. Dispute Resolution (UMA OOv3)

Anyone can challenge a score they believe is incorrect.

**Flow:**
1. Score published on-chain with UMA assertion + bond
2. 2-hour challenge window (configurable to 24hr for subjective signals)
3. If unchallenged → score finalized
4. If challenged → DVM vote (UMA token holders)
5. Resolution in 24-48 hours
6. Loser pays bond + dispute fee; winner gets bond back + reward

**Key design decisions:**
- Provisional scores during disputes (displayed with "under review" flag)
- Bond amount scales with tier (higher tiers = higher bonds to prevent spam)
- Dispute history becomes a reputation signal itself (frequent frivolous disputers lose trust)

#### 4. Cross-Chain Score Delivery (Chainlink CCIP)

Scores computed once, delivered everywhere via CCIP arbitrary messaging.

**Flow:**
1. Score finalized on origin chain (after dispute window)
2. CCIP message sent with encoded score + metadata
3. Destination chain registry receives and stores score
4. Any protocol on any chain can query `getAgentScore(agentAddress)`

**Cost model:**
- CCIP messaging fee: ~$0.01-0.10 per cross-chain message
- Score updates: periodic (daily) or event-driven (significant change)
- Batch updates for agents active on multiple chains

#### 5. Score Consumer SDK

Lightweight SDK for protocols to query agent scores.

```python
# Python SDK
from aae_credit import AgentCreditClient

client = AgentCreditClient(rpc_url="https://...")

# Get score (off-chain, fast)
score = client.get_score("0xABC...")
print(f"Score: {score.value}, Tier: {score.tier}, Confidence: {score.confidence}")

# Verify score on-chain (slow but trustless)
verified = client.verify_on_chain("0xABC...", chain="ethereum")
print(f"Verified: {verified}")

# Check if agent meets minimum threshold for your protocol
is_qualified = client.meets_threshold("0xABC...", min_score=650, min_tier="gold")
```

**SDK supports:**
- Python (primary — Hermes agent integration)
- TypeScript/JavaScript (web3 protocol integration)
- Solidity (on-chain verification helpers)

## Revenue Model

| Stream | Description | Pricing |
|--------|-------------|---------|
| **Score API Access** | Protocols pay for score queries | Free tier (100/day) → $0.001/query beyond |
| **Premium Data** | Detailed behavioral analytics, risk reports | $50-500/month per protocol |
| **Score Licensing** | Chains/deprotocols integrate scores natively | Revenue share on lending fees |
| **Dispute Fees** | Small fee on UMA disputes | Protocol takes 5% of dispute fee |
| **Identity Verification** | Premium KYA services for agents | Per-verification fee |

## Moat

1. **First-mover in cross-chain reputation** — t54 does credit, we do trust portability
2. **Data network effect** — more agents scored → better models → more protocols adopt → more agents register
3. **UMA integration** — decentralized dispute resolution that no centralized competitor can replicate
4. **ERC-8004 alignment** — building on the emerging standard, not against it
5. **Dogfooding** — our own agents use the system, proving it works in production

## Hackathon Fit

- **Sui Overflow** (Agentic + DeFi track): Cross-chain reputation for Sui agents
- **Dev3pack Bridge** (Jun 12): CCIP-native cross-chain score delivery
- **Any hackathon with "agent" or "infrastructure" track**: This IS agent infrastructure

## Tech Stack

- **Scoring Engine:** Python (ML scoring, API service)
- **Smart Contracts:** Solidity (registry, CCIP receiver, UMA assertions)
- **Data Collection:** Python + chain RPCs (Alchemy, Helius)
- **Cross-Chain:** Chainlink CCIP for score delivery
- **Dispute Resolution:** UMA Optimistic Oracle V3
- **Identity Layer:** ERC-8004 (read, don't reinvent)
- **Storage:** SQLite (dev) → PostgreSQL (prod) for score history

## Success Criteria (v1)

- [ ] Agent Activity Aggregator collects data from 3+ chains
- [ ] Scoring Engine produces 300-1000 composite score with confidence interval
- [ ] Scores display correct tier assignments
- [ ] UMA assertion flow works for score publication
- [ ] Challenge window + dispute flow functional
- [ ] CCIP delivers scores from origin chain to 1+ destination chains
- [ ] Python SDK returns scores with <100ms latency
- [ ] Integration test: agent gets scored → score delivered cross-chain → protocol queries score
- [ ] All tests passing (pytest for Python, Foundry for Solidity)

## Open Questions

1. **Scoring algorithm:** Should we use ML (Aave-style) or rule-based (deterministic)? ML needs training data we don't have yet. Start rule-based, evolve to ML.
2. **Update frequency:** How often do scores update? Daily batch vs event-driven? Start with daily, add event-driven for significant changes.
3. **Sybil resistance:** How do we prevent agents from gaming scores with multiple wallets? ERC-8004 identity binding + activity analysis.
4. **Governance:** Who controls the scoring formula? Start centralized, plan DAO governance for v2.
5. **Token:** Does Agent Arena Credit have a token? Not in v1. REP token for governance in v2.
