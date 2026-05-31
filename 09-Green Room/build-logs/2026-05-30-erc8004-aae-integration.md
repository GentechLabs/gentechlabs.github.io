# ERC-8004 x AAE Integration Brief

**Date:** May 30, 2026
**Status:** Build Log — Green Room
**Author:** Jordan / ProtoJay4789

---

## 1. BNBAgent SDK Overview

BNBAgent is a **Python SDK** providing four core modules for autonomous agent commerce:

| Module | Standard | Purpose |
|--------|----------|---------|
| **Identity** | ERC-8004 | On-chain agent identity registration and verification |
| **Commerce** | ERC-8183 / APEX | Agent-to-agent and agent-to-human commerce protocols |
| **Payments** | x402 / MPP | Micro-payment channels, pay-per-use billing |
| **Memory** | Greenfield | Decentralized memory storage for agent state persistence |

**Partners:** Google Cloud, AWS, Binance Pay

The SDK targets developers building autonomous agents that need verified identity, transactable commerce, payment rails, and persistent memory — all composable via standard ERC interfaces.

---

## 2. Three ERC-8004 Registries → AAE Layer Mapping

| ERC-8004 Registry | AAE Layer | Integration Role |
|-------------------|-----------|------------------|
| **Identity Registry** | Identity Layer | Agent self-sovereign identity — register, resolve, verify agent wallets on-chain. Provides the root of trust for all downstream AAE operations. |
| **Reputation Registry** | Credit Layer | Agent reputation scores, transaction history, and creditworthiness. Powers risk assessment, credit limits, and trust propagation across agent networks. |
| **Validation Registry** | Safety Layer | Proof-of-computation, task completion attestation, and dispute resolution hooks. Feeds the AAE safety layer with verifiable execution evidence. |

This mapping gives AAE a **chain-native trust stack**: identity anchors everything, reputation calibrates risk, and validation enforces safety guarantees.

---

## 3. Implementation Phases (4 Phases, 12 Weeks)

### Phase 1 — Identity Foundation (Weeks 1–3)
- Deploy ERC-8004 Identity Registry on testnet
- Integrate with AAE Identity Layer API
- Build agent registration flow (register → resolve → verify)
- Unit tests for identity CRUD operations

### Phase 2 — Reputation & Credit (Weeks 4–6)
- Wire Reputation Registry to AAE Credit Layer
- Implement reputation score ingestion pipeline
- Build credit scoring model using on-chain reputation data
- Design dispute resolution hooks via Validation Registry

### Phase 3 — Payments & Commerce (Weeks 7–9)
- Integrate x402/MPP payment rails with Commerce module
- Connect to 0xGasless Agent SDK for gasless tx relay
- Implement micropayment channels for agent-to-agent billing
- End-to-end commerce flow testing (identity → reputation → pay → validate)

### Phase 4 — Memory & Production (Weeks 10–12)
- Greenfield memory integration for agent state persistence
- Cross-chain sync validation
- Security audit and adversarial testing
- Staging deployment and partner integration testing (Google/AWS/Binance Pay)

---

## 4. Stack Interaction Diagram

```
┌─────────────────────────────────────────────────┐
│                    AAE Stack                     │
├─────────────┬─────────────┬─────────────────────┤
│  Identity   │   Credit    │      Safety         │
│   Layer     │   Layer     │      Layer          │
└──────┬──────┴──────┬──────┴──────────┬──────────┘
       │             │                 │
       ▼             ▼                 ▼
┌─────────────────────────────────────────────────┐
│              ERC-8004 Registries                │
│  Identity Registry │ Reputation │ Validation    │
└──────────┬─────────┴─────┬──────┴───────┬───────┘
           │               │              │
     ┌─────▼─────┐   ┌────▼────┐   ┌─────▼──────┐
     │  x402/MPP │   │Chainlink│   │Cross-Chain  │
     │  Payments │   │  Oracle │   │   Bridge    │
     │           │   │(rep.    │   │(identity    │
     │  Pay-per- │   │ scores) │   │  sync)     │
     │  use agent│   │         │   │             │
     │  billing  │   │         │   │             │
     └───────────┘   └─────────┘   └─────────────┘
```

**Key flows:**
- **ERC-8004 x x402:** Identity verification gates payment channel creation; reputation scores influence payment terms
- **ERC-8004 x Chainlink:** Chainlink oracles feed external reputation signals into the Reputation Registry; price feeds for micropayment settlement
- **ERC-8004 x Cross-Chain:** Cross-chain bridges synchronize agent identity and reputation across L1/L2 boundaries; latency is a known risk (see §5)

---

## 5. Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **ERC-8004 spec still in draft** | High | Pin to specific draft version; build adapter layer for spec changes; monitor ERC-8004 GitHub for breaking changes |
| **Cross-chain sync latency** | Medium | Implement eventual consistency model; use optimistic reads with staleness TTL; prioritize single-chain deployment first |
| **Reputation gaming** | Medium | Combine on-chain reputation with off-chain signals (Chainlink); implement decay functions; require minimum transaction history before credit extension |
| **SDK partner dependency** | Low | Abstract BNBAgent interfaces behind our own adapter; avoid tight coupling to any single SDK module |
| **x402 adoption uncertainty** | Medium | Build payment abstraction that supports x402 and fallback to traditional settlement |

---

## 6. Key Recommendation

### Use 0xGasless Agent SDK as the Fastest Integration Path

**Rationale:**
- **Already bundles ERC-8004 + x402** — no need to wire these together manually
- **We have an API key** — immediate access, no onboarding friction
- **Gasless relay** — removes UX barrier of agent wallet gas management
- **Battle-tested** — production-grade, used by multiple agent frameworks

**Recommended approach:**
1. Start with 0xGasless Agent SDK as the integration substrate
2. Layer our AAE Identity/Credit/Safety APIs on top of its ERC-8004 primitives
3. Use BNBAgent modules for Commerce and Memory only (avoid duplicating identity/payment work)
4. This cuts Phase 1 and Phase 3 timelines by ~40%

**Decision:** Fast-track 0xGasless integration as the primary path. BNBAgent SDK remains a secondary reference and partner integration target.

---

*Filed to vault: 2026-05-30-erc8004-aae-integration.md*
