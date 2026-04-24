# Competitive Landscape — Agent Marketplaces & Commerce Platforms

**Date:** 2026-04-18
**Analyst:** YoYo
**Layer:** All 5

---

## Executive Summary

Every existing agent marketplace focuses on either infrastructure (Olas, Fetch.ai) or token distribution (Morpheus) — none address the full commerce lifecycle from discovery through dispute resolution. The critical unaddressed gap is the middle layer: agent intelligence (memory/learning), risk assessment, and enforcement/compliance mechanisms. AAE's 5-layer architecture uniquely covers the complete agent-to-agent commerce stack, with Layers 1-4 being almost entirely uncontested.

---

## Competitor Comparison Table

| Feature | Olas | Fetch.ai | Morpheus | Theoriq | AgentLayer | **AAE** |
|---------|------|----------|----------|---------|------------|---------|
| Agent Discovery | Registry | Directory | Planned | None | Basic | **Full Marketplace** |
| Escrow/Payments | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ Layer 5** |
| Reputation System | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ Layer 5** |
| Agent Memory/Evolution | ⚠️ | ⚠️ | ❌ | ⚠️ | ❌ | **✅ Layer 3** |
| Risk/Sentiment Intel | ❌ | ❌ | ❌ | ⚠️ | ❌ | **✅ Layer 2** |
| DeFi Fee Management | ❌ | ❌ | ⚠️ | ❌ | ❌ | **✅ Layer 1** |
| SLA Enforcement | ⚠️ | ❌ | ❌ | ❌ | ❌ | **✅ Layer 4** |
| Dispute Resolution | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ Layer 4** |
| Slashing/Penalties | ⚠️ | ❌ | ❌ | ❌ | ❌ | **✅ Layer 4** |
| End-User UX | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| Agent-to-Agent Commerce | ❌ | ⚠️ | ❌ | ❌ | ❌ | **✅** |
| Shipped Product | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | **Building** |

---

## Three Underserved Pillars AAE Can Own

### 1. Agent Intelligence (Layer 3 — Brain)
- Nobody has structured agent memory, learning, or evolution
- Current "agents" are stateless functions with optional KV stores
- AAE Layer 3 gives agents institutional memory
- **Hackathon angle:** "Your agent remembers. Competitors' agents forget."

### 2. Commerce Enforcement (Layer 4 — Enforcement)
- Zero competitors have SLA frameworks, dispute resolution, or meaningful slashing
- Olas has basic slashing for agent misbehavior, but no buyer protection
- **Hackathon angle:** "First agent commerce platform with real accountability."

### 3. Risk Intelligence (Layer 2 — Agent Risk Intel)
- Nobody provides sentiment analysis or risk signals for agent interactions
- **Hackathon angle:** "Know before you go — risk intel for every agent interaction."

---

## Competitor Deep Dives

### Autonolas (Olas)
- **One-liner:** Framework for building/deploying autonomous agents with on-chain coordination
- **Commerce model:** Service registry + OLAS staking, revenue shared between stakers and developers
- **Layers covered:** Layer 3 (⚠️ partial memory), Layer 4 (⚠️ basic slashing), Layer 5 (⚠️ registry only)
- **Weaknesses:** Extremely high complexity, no native escrow, no reputation, no dispute resolution, Python-only
- **GitHub:** ~1,300+ stars (valory-olas org)
- **Token:** OLAS — utility/governance for bonding/staking

### Fetch.ai
- **One-liner:** Blockchain platform for agent-based economy with uAgents framework
- **Commerce model:** Almanac contract for agent registration/discovery, ASI-1 token for interactions
- **Layers covered:** Layer 3 (⚠️ KV store memory), Layer 5 (⚠️ directory only)
- **Weaknesses:** Directory only — no transactional layer, no payment rails, no quality signals, ASI Alliance merger causing confusion
- **GitHub:** ~1,800+ stars (fetchai/uAgents)
- **Token:** FET/ASI — utility, staking for registration

### Morpheus
- **One-liner:** Decentralized AI network for local LLMs with MOR incentives
- **Commerce model:** Proof-of-contribution for compute, code, models, capital
- **Layers covered:** Layer 1 (⚠️ capital staking only), Layer 5 (⚠️ SmartAgent vaporware)
- **Weaknesses:** Mostly vaporware, heavy on vision light on product, SmartAgent marketplace is future promise
- **GitHub:** ~2,000+ stars but mostly L1 staking + compute
- **Token:** MOR — proof-of-contribution distribution

### Theoriq
- **One-liner:** Agent protocol for composable/interoperable agents via BaseAgent framework
- **Commerce model:** AgentCollectives for agent composition, developer SDK focus
- **Layers covered:** Layer 2 (⚠️ concept only), Layer 3 (⚠️ partial memory)
- **Weaknesses:** Very early stage, no payment rails, no reputation, no end-user UX
- **GitHub:** ~500+ stars, limited activity
- **Token:** Not yet launched

### AgentLayer
- **One-liner:** Decentralized AI agent network with marketplace
- **Commerce model:** Token-based payments, staking for operators
- **Layers covered:** Layer 5 (⚠️ basic marketplace concept)
- **Weaknesses:** Minimal presence, low GitHub, no differentiation
- **GitHub:** <100 stars
- **Token:** Exists but low liquidity

### Kite AI (Ecosystem Partner)
- **One-liner:** High-performance blockchain for AI agent workloads
- **Role:** L1 infrastructure — AAE is the application layer on top
- **What Kite provides:** Agent identity, on-chain execution, fast finality
- **What Kite doesn't:** Commerce primitives, escrow, reputation, DeFi, agent intelligence

---

## Positioning Recommendations

### Pitch 1: "The Missing Commerce Stack"
> "Every competitor is building infrastructure or networks. We're building the *business layer*. Olas gives you agents. Fetch.ai gives you a directory. Morpheus gives you compute. AAE gives you a complete commerce system — from discovery to payment to dispute resolution — that actually works with real money."

### Pitch 2: "Agents That Remember, Platforms That Enforce"
> "Current agents are stateless and unaccountable. AAE Layer 3 gives agents persistent memory and learning. Layer 4 gives both parties enforcement and dispute resolution. This is the trust layer that makes agent-to-agent commerce viable."

### Pitch 3: "Build on Kite, Commerce with AAE"
> "Kite AI provides the best L1 for agent workloads. AAE provides the application layer nobody else is building — the commerce engine that sits on top. Together: infrastructure + commerce = complete stack."

### Key Differentiators
1. Full stack coverage — 5 layers vs competitors' 0-2 layers
2. Real money rails — escrow + LP fee management (nobody has this)
3. Enforcement — SLAs + disputes + slashing (nobody has this)
4. Agent intelligence — memory + learning + evolution (nobody has this)
5. End-user accessible — not just developer SDKs

---

*Note: GitHub stats and token data should be verified with live web tools before use in final hackathon materials.*

---

*Source: YoYo competitive analysis — web tools partially unavailable, supplemented by training knowledge*